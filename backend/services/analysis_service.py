import json
import re
import asyncio
import google.generativeai as genai

from backend.config import get_settings
from backend.models.schemas import CompetitorAnalysis, CompetitorPages
from backend.utils.chunker import merge_page_contents

from backend.metrics import (
    gemini_request_duration,
    gemini_requests_total,
    gemini_tokens_used,
    gemini_errors_total,
    gemini_momentum_score,
)
settings = get_settings()

genai.configure(api_key=settings.gemini_api_key)


SYSTEM_PROMPT = """You are a competitive intelligence analyst at a VC-backed B2B SaaS startup.
Your job is to extract strategic signals from competitor web content — not describe what companies do.

You think like a product strategist and a founder who needs to ACT on information.

Rules you never break:
- NEVER describe what a company does generically
- ALWAYS identify what signals their content reveals about strategy and trajectory
- ALWAYS return valid JSON — nothing else, no markdown, no explanation outside the JSON
- If a signal is not detectable from the content, write "Not detected" — never hallucinate
- momentum_score must be an integer 1–10, nothing else"""

USER_PROMPT_TEMPLATE = """You are analyzing web content scraped from {company_name}.

Pages available: {page_types}

Return ONLY a valid JSON object with exactly these fields:

{{
  "core_offering": "One sentence — what specific problem they solve and for whom",
  "icp": "Ideal customer profile based on messaging evidence — industry, company size, role",
  "messaging_tone": "Pick exactly one: enterprise | startup | technical | visionary | hybrid",
  "pricing_signals": "Any pricing tier names, price points, model (per seat/usage/flat), or recent changes detected. Write Not detected if pricing page was unavailable.",
  "hiring_signals": "Which job functions dominate their open roles? What does this reveal about their growth direction?",
  "recent_launches": ["list", "of", "detectable", "new", "features", "or", "product", "announcements"],
  "strategic_keywords": ["top", "8", "recurring", "strategic", "terms", "from", "their", "content"],
  "growth_signals": ["evidence", "of", "expansion", "funding", "new", "markets", "or", "aggressive", "push"],
  "risk_flags": ["anything", "unusual", "pivot", "signals", "inconsistent", "messaging", "decline", "signs"],
  "momentum_score": 7,
  "analyst_note": "One hard-hitting observation a founder should act on immediately — be specific and direct"
}}

MOMENTUM SCORE CALIBRATION — you MUST use this rubric strictly:

Score 9–10: Company shows ALL of these — major product launches in last 6 months, aggressive hiring across multiple functions, pricing expansion (new tiers or enterprise push), strong AI investment signals, expanding into new markets or verticals. Example: a startup doubling headcount + launching enterprise tier + publishing weekly product updates.

Score 7–8: Company shows MOST of these — recent product updates visible, moderate hiring signal, clear growth narrative in messaging, some AI integration, pricing suggests growth stage.

Score 5–6: Company shows SOME of these — product is mature, messaging is stable not aggressive, hiring is selective not broad, no major launches detected, maintaining rather than expanding.

Score 3–4: Company shows FEW growth signals — messaging is defensive or legacy-focused, pricing is static, no recent launches detectable, content is thin or outdated, hiring signals absent.

Score 1–2: Company shows DECLINE or STAGNATION signals — anti-growth messaging (deliberate slow), very thin web presence, no detectable hiring, no product updates, legacy positioning with no forward narrative.

CRITICAL SCORING RULES:
- A large established company (like TCS, HubSpot) is NOT automatically high momentum — size ≠ momentum
- A small startup with thin content should score LOW (3–4) not middle (7)
- Do NOT default to 7. If you are uncertain, score LOWER not higher
- A company actively pushing AI, new products, and enterprise = 8–9
- A company with static content and no detectable changes = 3–4
- You MUST justify your score implicitly through the signals you detect

Content to analyze:
{content}"""



class AnalysisService:

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=settings.default_model,
            system_instruction=SYSTEM_PROMPT
        )
        # Delay between competitor calls to respect per-minute quota
        self.inter_call_delay = 4


    async def analyze_competitor(
        self, competitor_pages: CompetitorPages
    ) -> CompetitorAnalysis:
        """
        Takes scraped pages for one competitor.
        Returns structured CompetitorAnalysis from Gemini.
        """
        print(f"  [analysis] Analyzing {competitor_pages.name}...")

        pages_as_dicts = [
            {
                "url": p.url,
                "page_type": p.page_type,
                "content": p.content
            }
            for p in competitor_pages.pages
            if p.fetch_success and p.content
        ]

        if not pages_as_dicts:
            return self._empty_analysis(
                competitor_pages.name,
                competitor_pages.domain,
                "No pages were successfully fetched"
            )

        merged_content = merge_page_contents(pages_as_dicts)
        page_types = [p["page_type"] for p in pages_as_dicts]

        prompt = USER_PROMPT_TEMPLATE.format(
            company_name=competitor_pages.name,
            page_types=", ".join(page_types),
            content=merged_content
        )

        # Pause before each call to avoid per-minute quota bursting
        await asyncio.sleep(self.inter_call_delay)

        raw_json = await self._call_gemini_with_metrics(prompt, call_type="analysis")

        if not raw_json:
            return self._empty_analysis(
                competitor_pages.name,
                competitor_pages.domain,
                "Gemini API call failed after retries"
            )

        return self._parse_response(
            raw_json,
            competitor_pages.name,
            competitor_pages.domain,
            page_types
        )


    async def _call_gemini_with_metrics(
        self,
        prompt: str,
        call_type: str = "analysis"
    ) -> str:
        """
        Wraps every Gemini call with timing, success/error counters,
        and token estimation.
        """
        import time
        model_name = settings.default_model

        # Rough token estimation: 1 token ≈ 4 characters
        estimated_tokens = len(prompt) // 4
        gemini_tokens_used.labels(call_type=call_type).inc(estimated_tokens)

        for attempt in range(1, 4):
            start = time.time()
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel(model_name)

                response = model.generate_content(prompt)
                duration = time.time() - start

                # Record success metrics
                gemini_request_duration.labels(
                    call_type=call_type, model=model_name
                ).observe(duration)
                gemini_requests_total.labels(
                    call_type=call_type, status="success"
                ).inc()

                return response.text

            except Exception as e:
                duration = time.time() - start
                error_str = str(e)

                # Classify the error type for the metric label
                if "429" in error_str or "quota" in error_str.lower():
                    error_type = "rate_limit"
                    gemini_requests_total.labels(
                        call_type=call_type, status="retry"
                    ).inc()
                elif "timeout" in error_str.lower():
                    error_type = "timeout"
                elif "parse" in error_str.lower():
                    error_type = "parse_error"
                else:
                    error_type = "unknown"

                gemini_errors_total.labels(error_type=error_type).inc()
                gemini_request_duration.labels(
                    call_type=call_type, model=model_name
                ).observe(duration)

                if attempt == 3:
                    gemini_requests_total.labels(
                        call_type=call_type, status="error"
                    ).inc()
                    raise

                # Parse retry delay from 429 response
                retry_delay = self._parse_retry_delay(error_str)
                print(
                    f"  [analysis] Gemini attempt {attempt} failed "
                    f"(waiting {retry_delay}s): {error_str[:80]}"
                )
                await asyncio.sleep(retry_delay)

    def _parse_retry_delay(self, error_str: str) -> float:
        """
        Extract retry delay from Gemini 429 error message.
        Falls back to 60s if not parseable.
        """
        # Pattern: retry_delay { seconds: 59 }
        match = re.search(r'retry_delay\s*\{\s*seconds:\s*(\d+)', error_str)
        if match:
            return float(match.group(1)) + 2  # Add 2s buffer
        # Pattern: "Please retry in 2.52s"
        match = re.search(r'retry in ([\d.]+)s', error_str)
        if match:
            return float(match.group(1)) + 2
        return 60.0  # Safe default

    

    def _parse_response(
        self,
        raw_text: str,
        name: str,
        domain: str,
        page_types: list[str]
    ) -> CompetitorAnalysis:
        try:
            cleaned = re.sub(r"```(?:json)?\s*", "", raw_text).strip()
            cleaned = cleaned.rstrip("```").strip()
            cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', cleaned)
            cleaned = re.sub(r'(?<!\\)\n(?=[^"]*"(?:[^"]*"[^"]*")*[^"]*$)', ' ', cleaned)

            data = json.loads(cleaned)
            data["momentum_score"] = int(data.get("momentum_score", 5))

            # ✅ OBSERVE #1 — happy path, primary parser succeeded
            gemini_momentum_score.observe(data["momentum_score"])

            return CompetitorAnalysis(
                name=name,
                domain=domain,
                pages_analyzed=page_types,
                analysis_success=True,
                **data
            )

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            print(f"  [analysis] JSON parse failed for {name}: {e}")
            print(f"  [analysis] Raw response: {raw_text[:300]}")

            try:
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    fallback_cleaned = json_match.group(0)
                    fallback_cleaned = re.sub(r'[\x00-\x1f\x7f](?<!["\n\t])', '', fallback_cleaned)
                    data = json.loads(fallback_cleaned)
                    data["momentum_score"] = int(data.get("momentum_score", 5))

                    # ✅ OBSERVE #2 — fallback parser recovered the JSON
                    gemini_momentum_score.observe(data["momentum_score"])

                    print(f"  [analysis] Recovered via fallback parser for {name}")
                    return CompetitorAnalysis(
                        name=name,
                        domain=domain,
                        pages_analyzed=page_types,
                        analysis_success=True,
                        **data
                    )
            except Exception as e2:
                print(f"  [analysis] Fallback parser also failed: {e2}")

            return self._empty_analysis(name, domain, f"Parse error: {e}")
    

    def _empty_analysis(
        self, name: str, domain: str, reason: str
    ) -> CompetitorAnalysis:
        return CompetitorAnalysis(
            name=name,
            domain=domain,
            core_offering="Analysis failed",
            icp="Not available",
            messaging_tone="hybrid",
            pricing_signals="Not detected",
            hiring_signals="Not detected",
            recent_launches=[],
            strategic_keywords=[],
            growth_signals=[],
            risk_flags=[f"Analysis failed: {reason}"],
            momentum_score=0,
            analyst_note=f"Could not analyze {name}: {reason}",
            pages_analyzed=[],
            analysis_success=False,
            error=reason
        )