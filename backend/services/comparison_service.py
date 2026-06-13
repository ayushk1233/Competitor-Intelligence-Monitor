import json
import re
import time
from datetime import datetime

from backend.config import get_settings
from backend.models.schemas import ComparisonResult, CompetitorAnalysis, IntelligenceReport
from backend.services.llm_service import COMPARISON_MODEL, call_openrouter

settings = get_settings()


SYSTEM_PROMPT = """You are writing a competitive intelligence briefing for a startup founder.
You have analyzed multiple competitors and must now synthesize cross-competitor insights.

You think like a VC analyst doing due diligence — you look for:
- Who is moving fastest and why
- Who is shifting markets (SMB → enterprise or vice versa)
- Where the white space is that nobody owns
- Who poses the greatest threat to a new entrant

Rules:
- ALWAYS return valid JSON — nothing else
- Be direct and specific — no corporate hedging
- Base every claim on the competitor summaries provided
- Never hallucinate signals that aren't in the data"""

COMPARISON_PROMPT_TEMPLATE = """You are writing a detailed competitive intelligence briefing for a startup founder and their strategy team.

Competitor count: {count}
Competitors analyzed: {names}

Here are the full intelligence summaries for each competitor:

{summaries}

Return ONLY a valid JSON object with exactly these fields:

{{
  "market_leader": "Competitor name only — the single company that leads this market",
  "market_leader_reason": "2-3 sentences explaining why this company is the market leader: what signals prove it, what advantages they hold, what makes them hard to displace",
  "fastest_mover": "Competitor name only — the single company showing the most momentum",
  "fastest_mover_reason": "2-3 sentences with specific evidence: which product areas, which hiring patterns, which content signals suggest aggressive forward momentum",
  "pivot_detected": "Competitor name + 2-3 sentences describing the strategic shift: what they were doing before vs now, and what this signals about their new direction. Write null if none detected.",
  "smb_to_enterprise_shift": ["list of competitor names showing this pattern — empty list if none"],
  "ai_emphasis_ranking": ["ranked list of all competitors from most to least AI-focused based on content signals"],
  "messaging_gaps": "3-4 sentences describing specific positioning territory that NONE of these competitors own. Name the underserved customer segment, the unaddressed pain point, and why this is a real opportunity rather than a gap they ignored intentionally.",
  "messaging_gap": {
    "title": "Short opportunity title (e.g. 'Citizen Developer & SMB Automation Gap')",
    "description": "Detailed explanation of the whitespace opportunity — specific, actionable, evidence-based",
    "target_persona": "Who is underserved (e.g. 'SMB operators, business analysts, operations teams')",
    "business_value": "Why this matters commercially (e.g. 'Expands TAM and reduces dependency on engineering resources')",
    "confidence": "Low | Medium | High"
  },
  "threat_ranking": ["ranked from most to least dangerous to a new market entrant — include all competitors"],
  "threat_ranking_reasons": ["for each competitor in threat_ranking, a 1-sentence explanation of why they are ranked at that position"],
  "executive_briefing": "Write 6-8 sentences as a sharp intelligence briefing a CEO would forward to their product, sales, and strategy teams. Structure it as: (1) who leads and why, (2) who is moving fastest and what that means for the market, (3) what nobody is doing that represents opportunity, (4) what the team should prioritize in the next 90 days based on these signals. Use specific company names, specific signals from the data, and be direct about risk. No hedging, no vague language."
}}"""




class ComparisonService:

    def __init__(self):
        pass

    

    async def generate_report(
        self,
        analyses: list[CompetitorAnalysis],
        start_time: float
    ) -> IntelligenceReport:
        print("  [comparison] Running cross-competitor synthesis...")

        comparison = await self._run_comparison(analyses)

        duration = round(time.time() - start_time, 2)
        total_pages = sum(len(a.pages_analyzed) for a in analyses)

        print(f"  [comparison] Report complete. {total_pages} pages analyzed in {duration}s")

        return IntelligenceReport(
            competitors=analyses,
            comparison=comparison,
            generated_at=datetime.utcnow(),
            total_pages_fetched=total_pages,
            run_duration_seconds=duration
        )

    
    async def _run_comparison(
        self, analyses: list[CompetitorAnalysis]
    ) -> ComparisonResult:
        summaries_dict = {}
        for a in analyses:
            summaries_dict[a.name] = {
                "core_offering": a.core_offering,
                "icp": a.icp,
                "messaging_tone": a.messaging_tone,
                "pricing_signals": a.pricing_signals,
                "hiring_signals": a.hiring_signals,
                "recent_launches": a.recent_launches,
                "strategic_keywords": a.strategic_keywords,
                "growth_signals": a.growth_signals,
                "risk_flags": a.risk_flags,
                "momentum_score": a.momentum_score,
                "analyst_note": a.analyst_note
            }

        prompt = COMPARISON_PROMPT_TEMPLATE.format(
            count=len(analyses),
            names=", ".join(a.name for a in analyses),
            summaries=json.dumps(summaries_dict, indent=2)
        )

        raw_json = await call_openrouter(
            prompt,
            system_prompt=SYSTEM_PROMPT,
            model=COMPARISON_MODEL,
            call_type="comparison",
            max_tokens=2048,
        )

        if not raw_json:
            return self._empty_comparison(analyses)

        return self._parse_response(raw_json, analyses)

   

    def _parse_response(
        self, raw_text: str, analyses: list[CompetitorAnalysis]
    ) -> ComparisonResult:
        try:
            cleaned = re.sub(r"```(?:json)?\s*", "", raw_text).strip()
            cleaned = cleaned.rstrip("```").strip()

            data = json.loads(cleaned)

            if data.get("pivot_detected") == "null":
                data["pivot_detected"] = None

            return ComparisonResult(**data)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"  [comparison] JSON parse failed: {e}")
            print(f"  [comparison] Raw response: {raw_text[:300]}")
            return self._empty_comparison(analyses)

    

    def _empty_comparison(
        self, analyses: list[CompetitorAnalysis]
    ) -> ComparisonResult:
        names = [a.name for a in analyses]
        return ComparisonResult(
            market_leader=f"{names[0]} (comparison analysis failed)",
            fastest_mover="Not determined",
            pivot_detected=None,
            smb_to_enterprise_shift=[],
            ai_emphasis_ranking=names,
            messaging_gaps="Comparison analysis failed — run again",
            threat_ranking=names,
            executive_briefing="Comparison analysis failed. Individual competitor analyses above may still be useful."
        )