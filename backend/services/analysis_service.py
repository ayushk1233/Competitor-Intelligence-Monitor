import json
import re

from backend.config import get_settings
from backend.metrics import (
    llm_momentum_score,
)
from backend.models.schemas import CompetitorAnalysis, CompetitorPages
from backend.reasoning.orchestrator import run_intelligence_pipeline
from backend.retrieval.context_builder import build_ranked_context
from backend.retrieval.signal_compressor import compress_signals
from backend.retrieval.signal_extractor import extract_signals
from backend.services.llm_service import call_openrouter
from backend.utils.json_utils import safe_json_loads

settings = get_settings()

EVALUATION_MODE = True
MAX_CONTEXT_CHARS = 12000 if EVALUATION_MODE else 30000


VALIDATION_SYSTEM_PROMPT = """You are a company identification specialist.
Your job is to identify what company this is and what it does based on web content.
Be precise and specific. If you are unsure, set validation_warning to true.

CRITICAL RULES:
- Do NOT classify software/platform companies as "IT Services". This is a common mistake.
- A company that sells a SaaS product is NOT "IT Services".
- A company that sells a competitive intelligence platform is NOT "Lead Generation" or "IT Services".
- A company that sells developer tools, marketing platforms, or any software product is a SOFTWARE company.
- "IT Services" means outsourcing, managed services, consulting, system integration — NOT software products.
- If the company sells a PRODUCT (SaaS, platform, tool, app), its category should reflect what that product does, not "IT Services".
"""

VALIDATION_USER_PROMPT_TEMPLATE = """Identify the company from the following web content.

Answer these questions:
1. What company is this? (company_name)
2. What does this company actually do? (company_description — one sentence)
3. What category does it belong to? (category — be specific. Examples: "Competitive Intelligence", "CRM", "Marketing Automation", "Developer Tools", "Cloud Infrastructure", "Data Analytics", "Financial Services", "Security", "Design Tools", "Analytics Platform", "No-Code Platform", "Collaboration Software". Do NOT use "IT Services" for software product companies.)
4. What product type is this? (product_type — e.g., "SaaS platform", "Dev tool", "Consulting", "Marketplace", "Open source project", "Agency services", "Mobile app")
5. Who are the primary customers? (primary_use_case — e.g., "Enterprise sales teams", "Software developers", "IT operations", "Small business owners", "Marketing teams", "Product managers")
6. Is your confidence LOW? (validation_warning — true if you are uncertain about the company identity, false if confident)

VALIDATION WARNING TRIGGERS — set validation_warning = true if ANY apply:
- The company appears to be a consulting firm, agency, or services company (not a product company)
- You cannot clearly determine what product they sell
- The content is ambiguous or contradictory about what the company does
- The company seems to be an IT services/outsourcing firm rather than a software product company

COMMON MISTAKES TO AVOID:
- Owler is NOT lead generation or IT services — it is a COMPETITIVE INTELLIGENCE platform. Its category should be "Competitive Intelligence" or "Market Intelligence".
- Crayon is NOT IT services — it is a COMPETITIVE INTELLIGENCE platform. Its category should be "Competitive Intelligence" or "Market Intelligence".
- Klue is NOT lead generation — it is a COMPETITIVE INTELLIGENCE platform. Its category should be "Competitive Intelligence".
- If a company's homepage says "competitive intelligence", "competitor tracking", or "market intelligence", categorize it as "Competitive Intelligence", not "IT Services" or "Lead Generation".

Return ONLY valid JSON:
{
  "company_name": "exact company name",
  "company_description": "what they do in one sentence",
  "category": "most specific category (never 'IT Services' for software products)",
  "product_type": "most specific product type",
  "primary_use_case": "who their customers are",
  "validation_warning": false
}

Content:
{content}"""

SYSTEM_PROMPT = """You are a competitive intelligence analyst at a VC-backed B2B SaaS startup.
Your job is to extract strategic signals from competitor web content — not describe what companies do.

You think like a product strategist and a founder who needs to ACT on information.

Rules you never break:
- NEVER describe what a company does generically
- ALWAYS identify what signals their content reveals about strategy and trajectory
- ALWAYS return valid JSON — nothing else, no markdown, no explanation outside the JSON
- If a signal is not detectable from the content, write "No public evidence found" — never hallucinate
- momentum_score must be an integer 1–10, nothing else"""

USER_PROMPT_TEMPLATE = """You are analyzing web content scraped from {company_name}.

Pages available: {page_types}

Return ONLY a valid JSON object with exactly these fields:

{{
  "core_offering": "One sentence — what specific problem they solve and for whom",
  "icp": "Ideal customer profile based on messaging evidence — industry, company size, role",
  "messaging_tone": "Pick exactly one: enterprise | startup | technical | visionary | hybrid",
  "pricing_signals": "Any pricing tier names, price points, model (per seat/usage/flat), or recent changes detected. Write 'No public evidence found' if pricing page was unavailable.",
  "hiring_signals": "Which job functions dominate their open roles? What does this reveal about their growth direction?",
  "recent_launches": ["list", "of", "detectable", "new", "features", "or", "product", "announcements"],
  "strategic_keywords": ["top", "8", "recurring", "strategic", "terms", "from", "their", "content"],
  "growth_signals": ["evidence", "of", "expansion", "funding", "new", "markets", "or", "aggressive", "push"],
  "risk_flags": ["anything", "unusual", "pivot", "signals", "inconsistent", "messaging", "decline", "signs"],
  "momentum_score": 7,
  "analyst_note": "One hard-hitting observation a founder should act on immediately — be specific and direct"
}}

Tone calibration examples:

enterprise:
formal, compliance-heavy,
process-oriented, Fortune-500 language

startup:
fast-moving, agile,
lightweight productivity-focused messaging

technical:
developer-first, APIs,
infrastructure, engineering-centric language

Examples of technical tone companies:
- Stripe
- Vercel
- Supabase
- Cloudflare

These companies emphasize:
- APIs
- developers
- infrastructure
- engineering workflows
- platform extensibility

This should classify as technical
even if enterprise customers are mentioned.

visionary:
future-focused,
AI-transformation language

AI developer tooling companies
focused on coding workflows,
engineering productivity,
or developer infrastructure
should usually classify as technical,
not visionary.

hybrid:
mix of enterprise + startup messaging

MOMENTUM SCORE CALIBRATION — you MUST use this rubric strictly:

Score 9–10: Company shows ALL of these — major product launches in last 6 months, aggressive hiring across multiple functions, pricing expansion (new tiers or enterprise push), strong AI investment signals, expanding into new markets or verticals. Example: a startup doubling headcount + launching enterprise tier + publishing weekly product updates.

Score 7–8: Company shows MOST of these — recent product updates visible, moderate hiring signal, clear growth narrative in messaging, some AI integration, pricing suggests growth stage.

Score 5–6: Company shows SOME of these — product is mature, messaging is stable not aggressive, hiring is selective not broad, no major launches detected, maintaining rather than expanding.

Score 3–4: Company shows FEW growth signals — messaging is defensive or legacy-focused, pricing is static, no recent launches detectable, content is thin or outdated, hiring signals absent.

Score 1–2: Company shows DECLINE or STAGNATION signals — anti-growth messaging (deliberate slow), very thin web presence, no detectable hiring, no product updates, legacy positioning with no forward narrative.

IMPORTANT NEGATIVE EXAMPLES:

A large established company with:
- stable branding
- mature enterprise positioning
- slow product iteration
- conservative messaging
- low startup energy

should NOT receive scores above 6.

Examples:
- IBM should usually fall between 4-6
Enterprise incumbents should rarely exceed 6
unless there is clear evidence of:
- startup-speed execution
- rapid market repositioning
- unusually aggressive innovation cycles

- Basecamp should usually fall between 2-4

unless there is strong evidence of:
- aggressive AI repositioning
- rapid hiring expansion
- major product launches
- startup-like execution speed

Large company does NOT mean high momentum.

A company with strong branding,
clear positioning,
or loyal users
should NOT automatically receive high momentum.

Momentum measures:
- strategic acceleration
- expansion velocity
- execution intensity
- market movement

NOT:
- popularity
- reputation
- product quality
- brand recognition

When uncertain, prefer LOWER momentum scores.
Do not overestimate momentum.

CRITICAL SCORING RULES:
- A large established company (like TCS, HubSpot) is NOT automatically high momentum — size ≠ momentum
- A small startup with thin content should score LOW (3–4) not middle (7)
- Do NOT default to 7. If you are uncertain, score LOWER not higher
- A company actively pushing AI, new products, and enterprise = 8–9
- A company with static content and no detectable changes = 3–4
- You MUST justify your score implicitly through the signals you detect

Content to analyze:
{content}"""


def ensure_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned.lower() in [
            "not detected",
            "no public evidence found",
            "insufficient information available",
            "none",
            "n/a",
            ""
        ]:
            return []
        return [cleaned]
    return []

def ensure_string(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join([str(v) for v in value])
    if isinstance(value, dict):
        return str(value)
    return str(value)


class AnalysisService:

    def __init__(self):
        # Delay between competitor calls to respect per-minute quota
        self.inter_call_delay = 4


    async def validate_company(
        self, competitor_pages: CompetitorPages
    ) -> dict:
        """
        Stage 1: Company Validation.
        Identifies what company this is before doing full intelligence extraction.
        Returns validation dict with company_name, category, validation_warning, etc.
        """
        print(f"  [validation] Validating {competitor_pages.name}...")

        # Use homepage and about page content for validation
        validation_pages = []
        for p in competitor_pages.pages:
            if p.page_type in ("homepage", "about") and p.fetch_success and p.content:
                validation_pages.append(f"[{p.page_type.upper()}]\n{p.content[:3000]}")

        if not validation_pages:
            # Use any available page
            for p in competitor_pages.pages:
                if p.fetch_success and p.content:
                    validation_pages.append(f"[{p.page_type.upper()}]\n{p.content[:3000]}")
                    break

        if not validation_pages:
            return {
                "company_name": competitor_pages.name,
                "company_description": "No content available",
                "category": "Unknown",
                "product_type": "Unknown",
                "primary_use_case": "Unknown",
                "validation_warning": True,
            }

        content = "\n\n".join(validation_pages)

        try:
            response = await call_openrouter(
                prompt=VALIDATION_USER_PROMPT_TEMPLATE.format(content=content),
                system_prompt=VALIDATION_SYSTEM_PROMPT
            )

            if not response:
                print(f"  [validation] Empty response for {competitor_pages.name}")
                return {"validation_warning": True}

            data = safe_json_loads(response)
            if not isinstance(data, dict):
                return {"validation_warning": True}

            validation = {
                "company_name": ensure_string(data.get("company_name", competitor_pages.name)),
                "company_description": ensure_string(data.get("company_description", "")),
                "category": ensure_string(data.get("category", "")),
                "product_type": ensure_string(data.get("product_type", "")),
                "primary_use_case": ensure_string(data.get("primary_use_case", "")),
                "validation_warning": bool(data.get("validation_warning", False)),
            }

            print(f"  [validation] Result: {validation.get('company_name')} "
                  f"(warning={validation.get('validation_warning')})")

            return validation

        except Exception as e:
            print(f"  [validation] Failed for {competitor_pages.name}: {e}")
            return {"validation_warning": True}


    async def analyze_competitor(
        self, competitor_pages: CompetitorPages
    ) -> CompetitorAnalysis:
        """
        Takes scraped pages for one competitor.
        Pipeline: Validate → Build Context → Extract Signals → Multi-agent Orchestration → Parse
        Returns structured CompetitorAnalysis from OpenRouter LLM.
        """
        print(f"  [analysis] Analyzing {competitor_pages.name}...")

        # Stage 1: Company Validation
        validation = await self.validate_company(competitor_pages)

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

        merged_chunks = build_ranked_context(pages_as_dicts)
        merged_content_str = "\n\n".join(merged_chunks)

        raw_signals = extract_signals(
            merged_content_str
        )

        compressed_signals = compress_signals(
            raw_signals
        )

        print("\n=== SIGNALS ===")
        import pprint
        pprint.pprint(compressed_signals)

        print(
            "[analysis] Extracted signal types:",
            list(compressed_signals.keys())
        )

        print(
            f"  [analysis] Built ranked "
            f"context: "
            f"{len(merged_content_str)} chars"
        )

        if len(merged_content_str) > MAX_CONTEXT_CHARS:
            print(f"  [analysis] Truncating context from {len(merged_content_str)} to {MAX_CONTEXT_CHARS} chars")
            merged_content_str = merged_content_str[:MAX_CONTEXT_CHARS]

        page_types = [p["page_type"] for p in pages_as_dicts]

        signal_summary = ""

        for (
            signal_type,
            evidence_list
        ) in compressed_signals.items():

            signal_summary += (
                f"\n[{signal_type.upper()}]\n"
            )

            for evidence in evidence_list:

                signal_summary += (
                    f"- {evidence}\n"
                )

        signal_summary_chunk = f"STRUCTURED STRATEGIC SIGNALS:\n{signal_summary}"
        
        # Prepend the structured signals to the chunks list
        final_chunks_for_pipeline = [signal_summary_chunk] + merged_chunks

        print(
            "[analysis] Running multi-agent orchestration..."
        )

        agent_result = await run_intelligence_pipeline(
            final_chunks_for_pipeline,
            compressed_signals,
            validation
        )

        print(
            "[analysis] Multi-agent synthesis complete"
        )

        final_analysis = agent_result["final"]

        if not final_analysis:
            return self._empty_analysis(
                competitor_pages.name,
                competitor_pages.domain,
                "LLM API call failed after retries"
            )

        agent_outputs = {
            "momentum": agent_result["momentum"],
            "tone": agent_result["tone"],
            "icp": agent_result["icp"],
            "final": agent_result["final"]
        }

        return self._parse_response(
            final_analysis,
            competitor_pages.name,
            competitor_pages.domain,
            page_types,
            agent_outputs,
            validation
        )


    def _parse_response(
        self,
        raw_text: str,
        name: str,
        domain: str,
        page_types: list[str],
        agent_outputs: dict = None,
        validation: dict = None
    ) -> CompetitorAnalysis:
        if agent_outputs is None:
            agent_outputs = {}
        if validation is None:
            validation = {}
        try:
            data = safe_json_loads(raw_text)
            data["momentum_score"] = int(data.get("momentum_score", 5))

            # ✅ OBSERVE #1 — happy path, primary parser succeeded
            llm_momentum_score.observe(data["momentum_score"])

            list_fields = [
                "recent_launches",
                "strategic_keywords",
                "growth_signals",
                "risk_flags",
                "icp_keywords",
                "icp_evidence",
                "tone_evidence",
                "momentum_evidence",
                "core_offering_evidence",
                "pricing_evidence",
                "hiring_evidence",
                "keywords_evidence",
                "momentum_negative_factors",
            ]
            for field in list_fields:
                data[field] = ensure_list(data.get(field))

            string_fields = [
                "core_offering",
                "icp",
                "messaging_tone",
                "pricing_signals",
                "hiring_signals",
                "analyst_note",
                "core_offering_source",
                "pricing_source",
                "hiring_source",
                "momentum_reasoning",
            ]
            for field in string_fields:
                if field in data:
                    data[field] = ensure_string(data[field])

            int_fields = [
                "core_offering_confidence",
                "pricing_confidence",
                "hiring_confidence",
                "keywords_confidence",
            ]
            for field in int_fields:
                if field in data:
                    try:
                        data[field] = int(data[field])
                    except (ValueError, TypeError):
                        data[field] = 0

            # Build confidence_scores dict from individual fields
            confidence_scores = {}
            for key in ["core_offering", "icp", "tone", "pricing", "hiring", "keywords"]:
                confidence_key = f"{key}_confidence"
                if key == "icp":
                    confidence_val = data.get("icp_confidence", data.get("confidence_scores", {}).get("icp", 0))
                elif key == "tone":
                    confidence_val = data.get("tone_confidence", data.get("confidence_scores", {}).get("tone", 0))
                else:
                    confidence_val = data.get(confidence_key, data.get("confidence_scores", {}).get(key, 0))
                try:
                    confidence_scores[key] = int(confidence_val)
                except (ValueError, TypeError):
                    confidence_scores[key] = 0

            data["confidence_scores"] = confidence_scores
            data["validation"] = validation

            return CompetitorAnalysis(
                name=name,
                domain=domain,
                pages_analyzed=page_types,
                analysis_success=True,
                agent_outputs=agent_outputs,
                **data
            )

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            print(f"  [analysis] JSON parse failed for {name}: {e}")
            print(f"  [analysis] Raw response: {raw_text[:300]}")

            try:
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    fallback_cleaned = json_match.group(0)
                    fallback_cleaned = re.sub(r'[\x00-\x1f\x7f](?!["\\n\\t])', '', fallback_cleaned)
                    data = json.loads(fallback_cleaned)
                    data["momentum_score"] = int(data.get("momentum_score", 5))

                    # ✅ OBSERVE #2 — fallback parser recovered the JSON
                    llm_momentum_score.observe(data["momentum_score"])

                    list_fields = [
                        "recent_launches",
                        "strategic_keywords",
                        "growth_signals",
                        "risk_flags",
                        "icp_keywords",
                        "icp_evidence",
                        "tone_evidence",
                        "momentum_evidence",
                        "core_offering_evidence",
                        "pricing_evidence",
                        "hiring_evidence",
                        "keywords_evidence",
                        "momentum_negative_factors",
                    ]
                    for field in list_fields:
                        data[field] = ensure_list(data.get(field))

                    string_fields = [
                        "core_offering",
                        "icp",
                        "messaging_tone",
                        "pricing_signals",
                        "hiring_signals",
                        "analyst_note",
                        "core_offering_source",
                        "pricing_source",
                        "hiring_source",
                        "momentum_reasoning",
                    ]
                    for field in string_fields:
                        if field in data:
                            data[field] = ensure_string(data[field])

                    int_fields = [
                        "core_offering_confidence",
                        "pricing_confidence",
                        "hiring_confidence",
                        "keywords_confidence",
                    ]
                    for field in int_fields:
                        if field in data:
                            try:
                                data[field] = int(data[field])
                            except (ValueError, TypeError):
                                data[field] = 0

                    confidence_scores = {}
                    for key in ["core_offering", "icp", "tone", "pricing", "hiring", "keywords"]:
                        confidence_key = f"{key}_confidence"
                        if key == "icp":
                            confidence_val = data.get("icp_confidence", data.get("confidence_scores", {}).get("icp", 0))
                        elif key == "tone":
                            confidence_val = data.get("tone_confidence", data.get("confidence_scores", {}).get("tone", 0))
                        else:
                            confidence_val = data.get(confidence_key, data.get("confidence_scores", {}).get(key, 0))
                        try:
                            confidence_scores[key] = int(confidence_val)
                        except (ValueError, TypeError):
                            confidence_scores[key] = 0

                    data["confidence_scores"] = confidence_scores
                    data["validation"] = validation

                    print(f"  [analysis] Recovered via fallback parser for {name}")
                    return CompetitorAnalysis(
                        name=name,
                        domain=domain,
                        pages_analyzed=page_types,
                        analysis_success=True,
                        agent_outputs=agent_outputs,
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
            icp="Insufficient information available",
            messaging_tone="hybrid",
            pricing_signals="No public evidence found",
            hiring_signals="No public evidence found",
            recent_launches=[],
            strategic_keywords=[],
            growth_signals=[],
            risk_flags=[f"Analysis failed: {reason}"],
            momentum_score=0,
            analyst_note=f"Could not analyze {name}: {reason}",
            pages_analyzed=[],
            analysis_success=False,
            error=reason,
            validation={"validation_warning": True, "reason": reason},
        )
