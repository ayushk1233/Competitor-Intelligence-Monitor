import streamlit as st
import asyncio
import sys
import os
import json
from datetime import datetime

# Make backend importable from frontend folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.main import run_intelligence_pipeline
from backend.models.schemas import IntelligenceReport, CompetitorAnalysis

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Competitor Intelligence Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styling ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A5F;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .competitor-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2E86AB;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        color: #1a1a1a !important;
    }
    .signal-box {
        background: #EFF6FF !important;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.9rem;
        color: #1E3A5F !important;
    }
    .risk-box {
        background: #FFF7ED !important;
        border-left: 3px solid #F59E0B;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.9rem;
        color: #92400E !important;
    }
    .analyst-note {
        background: #F0FDF4 !important;
        border-left: 4px solid #10B981;
        border-radius: 6px;
        padding: 1rem;
        font-style: italic;
        color: #065F46 !important;
        margin-top: 0.8rem;
    }
    .briefing-box {
        background: #1E3A5F;
        color: white !important;
        border-radius: 10px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
        font-size: 1rem;
        line-height: 1.7;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1E3A5F;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.4rem;
        margin: 1.5rem 0 1rem 0;
    }
    .metric-card {
        background: white !important;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        color: #1a1a1a !important;
    }
    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 2px;
    }
    .stProgress > div > div {
        background-color: #2E86AB;
    }

    /* Force dark text inside all custom HTML blocks regardless of Streamlit theme */
    div[data-testid="stMarkdownContainer"] .signal-box,
    div[data-testid="stMarkdownContainer"] .signal-box * {
        color: #1E3A5F !important;
    }
    div[data-testid="stMarkdownContainer"] .risk-box,
    div[data-testid="stMarkdownContainer"] .risk-box * {
        color: #92400E !important;
    }
    div[data-testid="stMarkdownContainer"] .analyst-note,
    div[data-testid="stMarkdownContainer"] .analyst-note * {
        color: #065F46 !important;
    }
    div[data-testid="stMarkdownContainer"] .metric-card,
    div[data-testid="stMarkdownContainer"] .metric-card * {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Tone badge colors ─────────────────────────────────────────────────────────

TONE_COLORS = {
    "enterprise":  {"bg": "#1E3A5F", "text": "white"},
    "startup":     {"bg": "#F59E0B", "text": "white"},
    "technical":   {"bg": "#0D9488", "text": "white"},
    "visionary":   {"bg": "#7C3AED", "text": "white"},
    "hybrid":      {"bg": "#6B7280", "text": "white"},
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def tone_badge(tone: str) -> str:
    tone_lower = tone.lower()
    color = TONE_COLORS.get(tone_lower, TONE_COLORS["hybrid"])
    return (
        f'<span style="background:{color["bg"]};color:{color["text"]};'
        f'padding:3px 12px;border-radius:12px;font-size:0.78rem;'
        f'font-weight:600;">{tone.upper()}</span>'
    )

def momentum_color(score: int) -> str:
    if score >= 8:
        return "#10B981"
    elif score >= 5:
        return "#F59E0B"
    else:
        return "#EF4444"

def keyword_tags(keywords: list[str]) -> str:
    tags = ""
    for kw in keywords:
        tags += (
            f'<span style="background:#EFF6FF;color:#1D4ED8;'
            f'padding:3px 10px;border-radius:12px;font-size:0.78rem;'
            f'margin:2px;display:inline-block;">{kw}</span>'
        )
    return tags

def render_list(items: list[str], style: str = "signal") -> None:
    if not items:
        st.caption("None detected")
        return
    css_class = "risk-box" if style == "risk" else "signal-box"
    for item in items:
        st.markdown(f'<div class="{css_class}">▸ {item}</div>', unsafe_allow_html=True)

def generate_markdown_report(report: IntelligenceReport) -> str:
    """Generate a clean markdown export of the full report."""
    lines = []
    lines.append(f"# Competitor Intelligence Report")
    lines.append(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Pages analyzed: {report.total_pages_fetched} | "
                 f"Duration: {report.run_duration_seconds}s\n")
    lines.append("---\n")

    # Executive briefing
    lines.append("## Executive Briefing")
    lines.append(f"\n> {report.comparison.executive_briefing}\n")

    # Comparison
    lines.append("## Strategic Comparison")
    lines.append(f"- **Market Leader:** {report.comparison.market_leader}")
    lines.append(f"- **Fastest Mover:** {report.comparison.fastest_mover}")
    lines.append(f"- **Pivot Detected:** {report.comparison.pivot_detected or 'None'}")
    lines.append(f"- **Messaging Gaps (Opportunity):** {report.comparison.messaging_gaps}")
    lines.append(f"- **Threat Ranking:** {' > '.join(report.comparison.threat_ranking)}")
    lines.append(f"- **AI Emphasis Ranking:** {' > '.join(report.comparison.ai_emphasis_ranking)}\n")
    lines.append("---\n")

    # Per-competitor
    for c in report.competitors:
        lines.append(f"## {c.name}")
        lines.append(f"**Domain:** {c.domain}  ")
        lines.append(f"**Tone:** {c.messaging_tone.upper()}  ")
        lines.append(f"**Momentum:** {c.momentum_score}/10\n")
        lines.append(f"**Core Offering:** {c.core_offering}")
        lines.append(f"**ICP:** {c.icp}")
        lines.append(f"**Pricing Signals:** {c.pricing_signals}\n")
        lines.append(f"**Hiring Signals:** {c.hiring_signals}\n")

        if c.recent_launches:
            lines.append("**Recent Launches:**")
            for item in c.recent_launches:
                lines.append(f"- {item}")

        if c.growth_signals:
            lines.append("\n**Growth Signals:**")
            for item in c.growth_signals:
                lines.append(f"- {item}")

        if c.risk_flags:
            lines.append("\n**Risk Flags:**")
            for item in c.risk_flags:
                lines.append(f"- {item}")

        if c.strategic_keywords:
            lines.append(f"\n**Keywords:** {', '.join(c.strategic_keywords)}")

        lines.append(f"\n**Analyst Note:** {c.analyst_note}\n")
        lines.append("---\n")

    return "\n".join(lines)

# ── Main app ──────────────────────────────────────────────────────────────────

def main():

    # Header
    st.markdown('<div class="main-title">🔍 Competitor Intelligence Monitor</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Strategic signals, not summaries. '
        'Powered by Gemini — built for founders.</div>',
        unsafe_allow_html=True
    )

    # ── Input section ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Add Competitors</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        raw_input = st.text_area(
            label="Enter competitor names or URLs",
            placeholder=(
                "HubSpot\nZoho CRM\nFreshsales\n\n"
                "One per line. Names or full URLs both work."
            ),
            height=140,
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        include_blog = st.checkbox("Include Blog", value=True)
        include_careers = st.checkbox("Include Careers", value=True)
        st.markdown("<br>", unsafe_allow_html=True)
        run_button = st.button(
            "⚡ Run Intelligence",
            type="primary",
            use_container_width=True
        )

    # ── Parse and validate input ──────────────────────────────────────────
    competitors = []
    if raw_input:
        competitors = [
            line.strip()
            for line in raw_input.strip().splitlines()
            if line.strip()
        ]

    if run_button:
        if len(competitors) < 2:
            st.error("Please enter at least 2 competitors.")
            return
        if len(competitors) > 5:
            st.error("Maximum 5 competitors per run.")
            return

        # ── Progress UI ───────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="section-header">Running Intelligence Pipeline</div>',
                    unsafe_allow_html=True)

        stage_labels = {
            "scraping":  "🌐 Stage 1 of 3 — Scraping competitor websites...",
            "analyzing": "🧠 Stage 2 of 3 — Gemini analyzing each competitor...",
            "comparing": "⚡ Stage 3 of 3 — Running cross-competitor synthesis...",
        }

        status_text = st.empty()
        progress_bar = st.progress(0)
        stage_info = st.empty()

        # Track progress across pipeline stages
        progress_state = {"stage": "", "current": 0, "total": 1}

        def progress_callback(stage: str, current: int, total: int):
            progress_state["stage"] = stage
            progress_state["current"] = current
            progress_state["total"] = total

            stage_weights = {"scraping": 0.0, "analyzing": 0.35, "comparing": 0.85}
            stage_span =    {"scraping": 0.35,"analyzing": 0.50, "comparing": 0.15}

            base = stage_weights.get(stage, 0)
            span = stage_span.get(stage, 0.1)
            ratio = current / total if total > 0 else 0
            overall = base + span * ratio

            progress_bar.progress(min(overall, 1.0))
            status_text.markdown(f"**{stage_labels.get(stage, stage)}**")
            if total > 1:
                stage_info.caption(f"{current} of {total} complete")

        # ── Run the pipeline ──────────────────────────────────────────────
        try:
            with st.spinner(""):
                report: IntelligenceReport = asyncio.run(
                    run_intelligence_pipeline(
                        competitors=competitors,
                        include_blog=include_blog,
                        include_careers=include_careers,
                        progress_callback=progress_callback
                    )
                )

            progress_bar.progress(1.0)
            status_text.success(
                f"✅ Intelligence report complete — "
                f"{report.total_pages_fetched} pages analyzed "
                f"in {report.run_duration_seconds}s"
            )
            stage_info.empty()

            # Store in session state so it persists on re-render
            st.session_state["report"] = report

        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.info(
                "Tips: Check your GEMINI_API_KEY in .env. "
                "Make sure you have internet access."
            )
            return

    # ── Render report if available ────────────────────────────────────────
    if "report" in st.session_state:
        render_report(st.session_state["report"])


def render_report(report: IntelligenceReport):
    st.markdown("---")

    # ── Run metadata ──────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Competitors", len(report.competitors))
    with m2:
        st.metric("Pages Analyzed", report.total_pages_fetched)
    with m3:
        st.metric("Run Time", f"{report.run_duration_seconds}s")
    with m4:
        avg_momentum = round(
            sum(c.momentum_score for c in report.competitors) / len(report.competitors), 1
        )
        st.metric("Avg Momentum", f"{avg_momentum}/10")

    # ── Executive briefing ────────────────────────────────────────────────
    st.markdown('<div class="section-header">Executive Briefing</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="briefing-box">📋 {report.comparison.executive_briefing}</div>',
        unsafe_allow_html=True
    )

    # ── Strategic comparison ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Strategic Comparison</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏆 Market Leader**")
        st.info(report.comparison.market_leader)
        st.markdown("**🚀 Fastest Mover**")
        st.success(report.comparison.fastest_mover)
        if report.comparison.pivot_detected:
            st.markdown("**🔄 Pivot Detected**")
            st.warning(report.comparison.pivot_detected)

    with c2:
        st.markdown("**💡 Messaging Gap (Opportunity)**")
        st.info(report.comparison.messaging_gaps)
        st.markdown("**⚠️ Threat Ranking**")
        for i, name in enumerate(report.comparison.threat_ranking, 1):
            st.markdown(f"**{i}.** {name}")

    st.markdown("**🤖 AI Emphasis Ranking**")
    ai_cols = st.columns(len(report.comparison.ai_emphasis_ranking))
    for i, (col, name) in enumerate(
        zip(ai_cols, report.comparison.ai_emphasis_ranking), 1
    ):
        with col:
            st.markdown(
                f'<div class="metric-card"><b>#{i}</b><br>{name}</div>',
                unsafe_allow_html=True
            )

    # ── Per-competitor cards ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Competitor Intelligence Cards</div>',
                unsafe_allow_html=True)

    for competitor in report.competitors:
        render_competitor_card(competitor)

    # ── Export ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Export Report</div>',
                unsafe_allow_html=True)

    markdown_report = generate_markdown_report(report)
    filename = (
        f"intel_report_"
        f"{report.generated_at.strftime('%Y%m%d_%H%M')}.md"
    )

    st.download_button(
        label="⬇️ Download as Markdown",
        data=markdown_report,
        file_name=filename,
        mime="text/markdown",
        use_container_width=False
    )


def render_competitor_card(c: CompetitorAnalysis):
    score_color = momentum_color(c.momentum_score)

    with st.expander(
        f"**{c.name}** — {c.domain}   |   "
        f"Momentum: {c.momentum_score}/10   |   "
        f"Tone: {c.messaging_tone.upper()}",
        expanded=True
    ):
        # Top row: tone badge + momentum bar
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(tone_badge(c.messaging_tone), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Domain:** {c.domain}")
            st.markdown(f"**Pages analyzed:** {', '.join(c.pages_analyzed)}")

        with col2:
            st.markdown(f"**Momentum Score: {c.momentum_score}/10**")
            st.progress(c.momentum_score / 10)
            st.markdown(
                f'<div style="color:{score_color};font-size:0.8rem;">'
                f'{"🔥 High momentum" if c.momentum_score >= 8 else "⚡ Active" if c.momentum_score >= 5 else "😴 Low momentum"}'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Core intel
        r1, r2 = st.columns(2)

        with r1:
            st.markdown("**🎯 Core Offering**")
            st.markdown(f'<div class="signal-box">{c.core_offering}</div>',
                        unsafe_allow_html=True)

            st.markdown("**👤 Ideal Customer Profile**")
            st.markdown(f'<div class="signal-box">{c.icp}</div>',
                        unsafe_allow_html=True)

            st.markdown("**💰 Pricing Signals**")
            st.markdown(f'<div class="signal-box">{c.pricing_signals}</div>',
                        unsafe_allow_html=True)

        with r2:
            st.markdown("**👥 Hiring Signals**")
            st.markdown(f'<div class="signal-box">{c.hiring_signals}</div>',
                        unsafe_allow_html=True)

            st.markdown("**🚀 Recent Launches**")
            render_list(c.recent_launches)

            st.markdown("**📈 Growth Signals**")
            render_list(c.growth_signals)

        # Risk flags
        if c.risk_flags:
            st.markdown("**⚠️ Risk Flags**")
            render_list(c.risk_flags, style="risk")

        # Keywords
        if c.strategic_keywords:
            st.markdown("**🔑 Strategic Keywords**")
            st.markdown(keyword_tags(c.strategic_keywords), unsafe_allow_html=True)

        # Analyst note — most important
        st.markdown(
            f'<div class="analyst-note">💡 <b>Analyst Note:</b> {c.analyst_note}</div>',
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()