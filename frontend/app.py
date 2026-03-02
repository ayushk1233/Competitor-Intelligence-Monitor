import streamlit as st
import requests
import time
import sys
import os

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Competitor Intelligence Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── API base URL — points to FastAPI running in Docker ────────────────────────
API_BASE = "http://localhost:8000"

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
    .history-card {
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2E86AB;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #1a1a1a !important;
    }
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

def keyword_tags(keywords: list) -> str:
    tags = ""
    for kw in keywords:
        tags += (
            f'<span style="background:#EFF6FF;color:#1D4ED8;'
            f'padding:3px 10px;border-radius:12px;font-size:0.78rem;'
            f'margin:2px;display:inline-block;">{kw}</span>'
        )
    return tags

def render_list(items: list, style: str = "signal") -> None:
    if not items:
        st.caption("None detected")
        return
    css_class = "risk-box" if style == "risk" else "signal-box"
    for item in items:
        st.markdown(
            f'<div class="{css_class}">▸ {item}</div>',
            unsafe_allow_html=True
        )

def check_api_health() -> bool:
    """Check if the FastAPI backend is reachable."""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=3)
        return response.status_code == 200
    except Exception:
        return False

def generate_markdown_report(report: dict) -> str:
    """Generate markdown export from report dict."""
    lines = []
    lines.append("# Competitor Intelligence Report")
    lines.append(f"Generated: {report.get('generated_at', 'N/A')}")
    lines.append(
        f"Pages analyzed: {report.get('total_pages_fetched', 0)} | "
        f"Duration: {report.get('run_duration_seconds', 0)}s\n"
    )
    lines.append("---\n")

    comparison = report.get("comparison", {})
    lines.append("## Executive Briefing")
    lines.append(f"\n> {comparison.get('executive_briefing', 'N/A')}\n")

    lines.append("## Strategic Comparison")
    lines.append(f"- **Market Leader:** {comparison.get('market_leader', 'N/A')}")
    lines.append(f"- **Fastest Mover:** {comparison.get('fastest_mover', 'N/A')}")
    lines.append(f"- **Pivot Detected:** {comparison.get('pivot_detected') or 'None'}")
    lines.append(f"- **Messaging Gap:** {comparison.get('messaging_gaps', 'N/A')}")
    threat = comparison.get('threat_ranking', [])
    lines.append(f"- **Threat Ranking:** {' > '.join(threat)}\n")
    lines.append("---\n")

    for c in report.get("competitors", []):
        lines.append(f"## {c.get('name', 'Unknown')}")
        lines.append(f"**Domain:** {c.get('domain', '')}  ")
        lines.append(f"**Tone:** {c.get('messaging_tone', '').upper()}  ")
        lines.append(f"**Momentum:** {c.get('momentum_score', 0)}/10\n")
        lines.append(f"**Core Offering:** {c.get('core_offering', '')}")
        lines.append(f"**ICP:** {c.get('icp', '')}")
        lines.append(f"**Pricing Signals:** {c.get('pricing_signals', '')}\n")
        lines.append(f"**Analyst Note:** {c.get('analyst_note', '')}\n")
        lines.append("---\n")

    return "\n".join(lines)

# ── API calls ─────────────────────────────────────────────────────────────────

def start_analysis(competitors: list, options: dict) -> dict | None:
    """POST /api/analyze — returns run_id instantly."""
    try:
        response = requests.post(
            f"{API_BASE}/api/analyze",
            json={"competitors": competitors, "options": options},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Could not reach API: {e}")
        return None

def poll_status(run_id: str) -> dict | None:
    """GET /api/status/{run_id} — returns current status."""
    try:
        response = requests.get(f"{API_BASE}/api/status/{run_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def fetch_report(run_id: str) -> dict | None:
    """GET /api/report/{run_id} — returns completed report."""
    try:
        response = requests.get(f"{API_BASE}/api/report/{run_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def fetch_recent_runs() -> list:
    """GET /api/runs — returns recent run history."""
    try:
        response = requests.get(f"{API_BASE}/api/runs", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def fetch_competitor_history(name: str) -> list:
    """GET /api/history/{name} — returns momentum history."""
    try:
        response = requests.get(
            f"{API_BASE}/api/history/{name}", timeout=5
        )
        if response.status_code == 200:
            return response.json().get("history", [])
        return []
    except Exception:
        return []

# ── Main app ──────────────────────────────────────────────────────────────────

def main():

    st.markdown(
        '<div class="main-title">🔍 Competitor Intelligence Monitor</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Strategic signals, not summaries. '
        'Powered by Gemini — built for founders.</div>',
        unsafe_allow_html=True
    )

    if not check_api_health():
        st.error(
            "⚠️ Cannot reach the backend API at localhost:8000. "
            "Make sure Docker is running: `docker compose up`"
        )
        st.stop()
    else:
        st.success("✅ Backend API connected — all systems operational")

    tab1, tab2 = st.tabs(["⚡ Run Intelligence", "📊 Run History"])

    with tab1:
        run_intelligence_tab()

    with tab2:
        history_tab()

    # ── Render report ONCE below tabs — only when loaded from History ──────
    # run_intelligence_tab() handles its own report rendering inline.
    # This block only fires when a report was loaded from the History tab
    # (flagged by the "loaded_from_history" key in session state).
    if (
        "report" in st.session_state
        and st.session_state.get("loaded_from_history", False)
    ):
        st.markdown("---")
        st.markdown(
            '<div class="section-header">📊 Loaded Report</div>',
            unsafe_allow_html=True
        )
        run_id = st.session_state.get("run_id", "unknown")
        render_report(st.session_state["report"], report_key=run_id)


def run_intelligence_tab():

    st.markdown(
        '<div class="section-header">Add Competitors</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        raw_input = st.text_area(
            label="Competitors",
            placeholder=(
                "Linear\nNotion\nBasecamp\n\n"
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

    # ── Parse competitors ─────────────────────────────────────────────────
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

        # ── Start analysis — returns run_id instantly ─────────────────────
        st.markdown("---")
        st.markdown(
            '<div class="section-header">Running Intelligence Pipeline</div>',
            unsafe_allow_html=True
        )

        with st.spinner("Sending request to API..."):
            result = start_analysis(
                competitors,
                {
                    "include_careers": include_careers,
                    "include_blog": include_blog,
                    "max_pages_per_competitor": 4
                }
            )

        if not result:
            return

        run_id = result["run_id"]
        st.info(f"📋 Run ID: `{run_id}` — Pipeline started in background")

        # ── Poll for status until completed ───────────────────────────────
        status_text = st.empty()
        progress_bar = st.progress(0)
        stage_info = st.empty()

        stage_labels = {
            "queued":    "⏳ Queued — waiting for worker...",
            "scraping":  "🌐 Stage 1 of 3 — Scraping competitor websites...",
            "analyzing": "🧠 Stage 2 of 3 — Gemini analyzing each competitor...",
            "comparing": "⚡ Stage 3 of 3 — Running cross-competitor synthesis...",
            "completed": "✅ Complete!",
            "failed":    "❌ Pipeline failed",
        }

        final_status = None

        while True:
            status = poll_status(run_id)

            if not status:
                st.error("Lost connection to API while polling.")
                break

            current = status["status"]
            progress = status.get("progress_percent", 0)

            status_text.markdown(
                f"**{stage_labels.get(current, current)}**"
            )
            progress_bar.progress(progress / 100)

            if current == "completed":
                final_status = "completed"
                stage_info.empty()
                break

            elif current == "failed":
                st.error(
                    f"Pipeline failed: {status.get('error', 'Unknown error')}"
                )
                final_status = "failed"
                break

            # Wait 3 seconds before polling again
            time.sleep(3)

        # ── Fetch and display report ──────────────────────────────────────
        if final_status == "completed":
            progress_bar.progress(1.0)
            status_text.success(
                f"✅ Intelligence report complete — "
                f"{status.get('pages_fetched', 0)} pages analyzed "
                f"in {status.get('duration_seconds', 0)}s"
            )

            with st.spinner("Loading report..."):
                report = fetch_report(run_id)

            if report:
                st.session_state["report"] = report
                st.session_state["run_id"] = run_id
                # This came from a fresh run, NOT from history
                st.session_state["loaded_from_history"] = False

    # ── Render inline for fresh runs only ────────────────────────────────
    if (
        "report" in st.session_state
        and not st.session_state.get("loaded_from_history", False)
    ):
        render_report(
            st.session_state["report"],
            report_key=st.session_state.get("run_id", "fresh")
        )

   


def history_tab():
    """Shows recent runs and competitor momentum history."""

    st.markdown(
        '<div class="section-header">Recent Analysis Runs</div>',
        unsafe_allow_html=True
    )

    # Refresh button so user can update the list without reloading
    if st.button("🔄 Refresh", key="refresh_runs"):
        st.rerun()

    runs = fetch_recent_runs()

    if not runs:
        st.info(
            "No runs yet. Go to Run Intelligence and analyze some competitors."
        )
        return

    for run in runs:
        status_emoji = {
            "completed": "✅",
            "failed":    "❌",
            "scraping":  "🌐",
            "analyzing": "🧠",
            "comparing": "⚡",
            "queued":    "⏳",
        }.get(run["status"], "⏳")

        competitors_str = ", ".join(run["competitors"])
        duration = (
            f"{run['duration_seconds']}s"
            if run["duration_seconds"] else "—"
        )

        st.markdown(
            f'<div class="history-card">'
            f'{status_emoji} <b>{competitors_str}</b> &nbsp;|&nbsp; '
            f'Status: {run["status"]} &nbsp;|&nbsp; '
            f'Pages: {run["pages_fetched"] or 0} &nbsp;|&nbsp; '
            f'Duration: {duration} &nbsp;|&nbsp; '
            f'<span style="color:#6B7280;font-size:0.85rem;">'
            f'{run["created_at"][:19] if run["created_at"] else ""}'
            f'</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        if run["status"] == "completed":
            if st.button("📊 Load Report", key=f"load_{run['run_id']}"):
                with st.spinner("Loading report..."):
                    report = fetch_report(run["run_id"])
                if report:
                    st.session_state["report"] = report
                    st.session_state["run_id"] = run["run_id"]
                    # Flag that this came from history
                    # so main() knows to render it below the tabs
                    st.session_state["loaded_from_history"] = True
                    st.rerun()

    # ── Competitor momentum history ───────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="section-header">Competitor Momentum History</div>',
        unsafe_allow_html=True
    )

    competitor_input = st.text_input(
        "Enter competitor name to see history",
        placeholder="e.g. Linear"
    )

    if competitor_input:
        history = fetch_competitor_history(competitor_input)

        if not history:
            st.info(
                f"No history found for '{competitor_input}'. "
                "Run an analysis first."
            )
        else:
            st.markdown(
                f"**{competitor_input}** — {len(history)} run(s) on record"
            )
            for entry in history:
                score = entry["momentum_score"]
                color = momentum_color(score)
                st.markdown(
                    f'<div class="history-card">'
                    f'📅 {entry["date"]} &nbsp;|&nbsp; '
                    f'Momentum: <span style="color:{color};font-weight:700;">'
                    f'{score}/10</span> &nbsp;|&nbsp; '
                    f'Tone: {entry["tone"].upper()}'
                    f'</div>',
                    unsafe_allow_html=True
                )


# ── Report rendering (same as before) ────────────────────────────────────────

def render_report(report: dict ,report_key: str = "default"):
    st.markdown("---")

    competitors = report.get("competitors", [])
    comparison = report.get("comparison", {})

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Competitors", len(competitors))
    with m2:
        st.metric("Pages Analyzed", report.get("total_pages_fetched", 0))
    with m3:
        st.metric("Run Time", f"{report.get('run_duration_seconds', 0)}s")
    with m4:
        scores = [c.get("momentum_score", 0) for c in competitors]
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        st.metric("Avg Momentum", f"{avg}/10")

    # Executive briefing
    st.markdown(
        '<div class="section-header">Executive Briefing</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="briefing-box">'
        f'📋 {comparison.get("executive_briefing", "N/A")}'
        f'</div>',
        unsafe_allow_html=True
    )

    # Strategic comparison
    st.markdown(
        '<div class="section-header">Strategic Comparison</div>',
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏆 Market Leader**")
        st.info(comparison.get("market_leader", "N/A"))
        st.markdown("**🚀 Fastest Mover**")
        st.success(comparison.get("fastest_mover", "N/A"))
        if comparison.get("pivot_detected"):
            st.markdown("**🔄 Pivot Detected**")
            st.warning(comparison["pivot_detected"])

    with c2:
        st.markdown("**💡 Messaging Gap (Opportunity)**")
        st.info(comparison.get("messaging_gaps", "N/A"))
        st.markdown("**⚠️ Threat Ranking**")
        for i, name in enumerate(comparison.get("threat_ranking", []), 1):
            st.markdown(f"**{i}.** {name}")

    ai_ranking = comparison.get("ai_emphasis_ranking", [])
    if ai_ranking:
        st.markdown("**🤖 AI Emphasis Ranking**")
        ai_cols = st.columns(len(ai_ranking))
        for i, (col, name) in enumerate(zip(ai_cols, ai_ranking), 1):
            with col:
                st.markdown(
                    f'<div class="metric-card"><b>#{i}</b><br>{name}</div>',
                    unsafe_allow_html=True
                )

    # Competitor cards
    st.markdown(
        '<div class="section-header">Competitor Intelligence Cards</div>',
        unsafe_allow_html=True
    )
    for competitor in competitors:
        render_competitor_card(competitor)

    # Export
    st.markdown(
        '<div class="section-header">Export Report</div>',
        unsafe_allow_html=True
    )
    markdown_report = generate_markdown_report(report)
    st.download_button(
        label="⬇️ Download as Markdown",
        data=markdown_report,
        file_name=f"intel_report_{report_key}.md",
        mime="text/markdown",
        key=f"download_{report_key}"   # ← unique key fixes DuplicateWidgetID
    )


def render_competitor_card(c: dict):
    score = c.get("momentum_score", 0)
    score_color = momentum_color(score)
    tone = c.get("messaging_tone", "hybrid")

    with st.expander(
        f"**{c.get('name', 'Unknown')}** — {c.get('domain', '')}   |   "
        f"Momentum: {score}/10   |   Tone: {tone.upper()}",
        expanded=True
    ):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(tone_badge(tone), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Domain:** {c.get('domain', '')}")
            pages = c.get("pages_analyzed", [])
            st.markdown(f"**Pages analyzed:** {', '.join(pages)}")
        with col2:
            st.markdown(f"**Momentum Score: {score}/10**")
            st.progress(score / 10)
            label = (
                "🔥 High momentum" if score >= 8
                else "⚡ Active" if score >= 5
                else "😴 Low momentum"
            )
            st.markdown(
                f'<div style="color:{score_color};font-size:0.8rem;">'
                f'{label}</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        r1, r2 = st.columns(2)

        with r1:
            st.markdown("**🎯 Core Offering**")
            st.markdown(
                f'<div class="signal-box">'
                f'{c.get("core_offering", "N/A")}</div>',
                unsafe_allow_html=True
            )
            st.markdown("**👤 Ideal Customer Profile**")
            st.markdown(
                f'<div class="signal-box">{c.get("icp", "N/A")}</div>',
                unsafe_allow_html=True
            )
            st.markdown("**💰 Pricing Signals**")
            st.markdown(
                f'<div class="signal-box">'
                f'{c.get("pricing_signals", "N/A")}</div>',
                unsafe_allow_html=True
            )

        with r2:
            st.markdown("**👥 Hiring Signals**")
            st.markdown(
                f'<div class="signal-box">'
                f'{c.get("hiring_signals", "N/A")}</div>',
                unsafe_allow_html=True
            )
            st.markdown("**🚀 Recent Launches**")
            render_list(c.get("recent_launches", []))
            st.markdown("**📈 Growth Signals**")
            render_list(c.get("growth_signals", []))

        if c.get("risk_flags"):
            st.markdown("**⚠️ Risk Flags**")
            render_list(c["risk_flags"], style="risk")

        if c.get("strategic_keywords"):
            st.markdown("**🔑 Strategic Keywords**")
            st.markdown(
                keyword_tags(c["strategic_keywords"]),
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="analyst-note">'
            f'💡 <b>Analyst Note:</b> {c.get("analyst_note", "N/A")}'
            f'</div>',
            unsafe_allow_html=True
        )


def momentum_color(score: int) -> str:
    if score >= 8:
        return "#10B981"
    elif score >= 5:
        return "#F59E0B"
    else:
        return "#EF4444"


if __name__ == "__main__":
    main()
