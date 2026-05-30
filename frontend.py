import os
import json
import html
import ast
from pathlib import Path
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #080d14;
}

/* ── Hero ── */
.hero-wrapper {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
    height: 280px;
}
.hero-bg {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: brightness(0.35);
    position: absolute;
    top: 0; left: 0;
}
.hero-content {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
}
.hero-badge {
    background: rgba(58,123,213,0.25);
    border: 1px solid rgba(58,123,213,0.5);
    color: #7ab8f5 !important;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 0.9rem;
    display: inline-block;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.6rem;
    line-height: 1.2;
}
.hero-sub {
    color: #94adc8;
    font-size: 1rem;
    max-width: 560px;
}

/* ── Input card ── */
.input-card {
    background: #0e1623;
    border: 1px solid #1e2e44;
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.5rem;
}
.input-label {
    color: #7ab8f5;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Quick destinations ── */
.dest-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 0.8rem 0 1.2rem;
}
.dest-chip {
    background: #111b2b;
    border: 1px solid #1e3050;
    color: #f7fdf4;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
}
.dest-chip:hover { background: #1a2e47; border-color: #3a7bd5; color: #fff; }

/* ── Generate button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1a6bbf 0%, #0d4a8a 50%, #0a3d75 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2.5rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    width: 100% !important;
    box-shadow: 0 0 24px rgba(26,107,191,0.35), 0 4px 15px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 0 40px rgba(26,107,191,0.6), 0 6px 20px rgba(0,0,0,0.5) !important;
    transform: translateY(-2px) !important;
    background: linear-gradient(135deg, #2278d4 0%, #1057a0 50%, #0d4a8a 100%) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
}

/* ── Agent status cards ── */
[data-testid="stStatusWidget"] {
    background: #0e1a2e !important;
    border: 1px solid #1e3050 !important;
    border-radius: 12px !important;
}
[data-testid="stStatusWidget"] > div:first-child {
    background: #0e1a2e !important;
    border-radius: 12px 12px 0 0 !important;
}
[data-testid="stStatusWidget"] details,
[data-testid="stStatusWidget"] details > div,
[data-testid="stStatusWidget"] [data-testid="stVerticalBlock"] {
    background: #0a1520 !important;
    color: #ffffff !important;
    padding: 0.25rem 0.5rem !important;
}
[data-testid="stStatusWidget"] * { color: #ffffff !important; }
[data-testid="stStatusWidget"] a { color: #4ea8f0 !important; }
[data-testid="stStatusWidget"] hr { border-color: #1e3050 !important; }

/* ── Section headers ── */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e2e44;
}
.sec-head span { font-size: 1.15rem; font-weight: 600; color: #e0edf8; }

/* ── Metric bar ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-box {
    flex: 1;
    background: #0e1623;
    border: 1px solid #1e2e44;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-val { font-size: 1.8rem; font-weight: 700; color: #4ea8f0; }
.metric-lbl { font-size: 0.78rem; color: #5a7a96; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Final plan ── */
.final-card {
    background: linear-gradient(160deg, #0c1a2e 0%, #0a1520 100%);
    border: 1px solid #1e3a5c;
    border-left: 4px solid #3a7bd5;
    border-radius: 14px;
    padding: 1.8rem;
    line-height: 1.8;
    color: #cce0f5;
    font-size: 0.95rem;
}

/* ── Save bar ── */
.save-bar {
    background: #0e1623;
    border: 1px solid #1e2e44;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    color: #5a8ab0;
    font-size: 0.88rem;
    margin-top: 0.5rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #090e18 !important;
    border-right: 1px solid #141f30 !important;
}
.sidebar-chip {
    background: #0e1a2b;
    border: 1px solid #1a2e44;
    border-radius: 8px;
    padding: 0.45rem 0.75rem;
    margin-bottom: 0.4rem;
    font-size: 0.83rem;
    color: #7aa8cc;
}
.sidebar-title { color: #e0edf8; font-size: 1rem; font-weight: 600; margin: 1rem 0 0.5rem; }

/* Hide branding (keep header/MainMenu so sidebar toggle remains accessible) */
footer { visibility: hidden; }

/* Textarea */
.stTextArea textarea {
    background: #0a1520 !important;
    border: 1px solid #1e2e44 !important;
    border-radius: 10px !important;
    color: #e8f4ff !important;
    font-size: 0.95rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,0.2) !important;
}
.stTextArea textarea::placeholder { color: #4a6a85 !important; }

/* Text input (sidebar User ID field) */
input[type="text"], .stTextInput input {
    background: #0e1a2b !important;
    border: 1px solid #1a2e44 !important;
    border-radius: 8px !important;
    color: #e0edf8 !important;
}
input[type="text"]:focus, .stTextInput input:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,0.2) !important;
}
input[type="text"]::placeholder { color: #3a5570 !important; }

/* All Streamlit labels — dark bg → light text */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {
    color: #7ab8f5 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
}

/* General markdown / paragraph text */
.stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th {
    color: #cce0f5 !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #e8f4ff !important; }
.stMarkdown code {
    background: #0e1a2b !important;
    color: #7ab8f5 !important;
    padding: 0.15em 0.4em;
    border-radius: 4px;
}

/* Agent output preformatted box */
.agent-pre {
    background: #071019;
    border: 1px solid #142833;
    border-radius: 8px;
    padding: 0.85rem;
    color: #cfe9ff;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
    font-size: 0.9rem;
    white-space: pre-wrap;
}
.agent-error { color: #ff8b8b; font-weight: 700; }

.detail-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.detail-row:last-child { border-bottom: none; }
.detail-key { color: #8ab8d8; font-weight: 600; }
.detail-val { color: #e8f4ff; text-align: right; }

/* Metric labels — was #5a7a96 (too dim on dark bg) */
.metric-lbl { color: #7aa8cc !important; }

/* Save bar — was #5a8ab0 (slightly dim) */
.save-bar { color: #8ab8d8 !important; }
.save-bar code { color: #7ab8f5 !important; background: #0a1520 !important; }

/* Streamlit warning / info / success on dark bg */
.stAlert { background: #0e1a2b !important; border-radius: 10px !important; }
.stAlert p, .stAlert div { color: #e0edf8 !important; }

/* Sidebar text & dividers */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown { color: #a0c4e0 !important; }
section[data-testid="stSidebar"] hr { border-color: #1a2e44 !important; }

/* Download button — light bg → dark text  */
div[data-testid="stDownloadButton"] > button {
    background: #1a3a5c !important;
    color: #e8f4ff !important;
    border: 1px solid #2a5080 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
# Agent metadata (defined early so sidebar can reference it)
AGENT_META = {
    "flight_agent":    ("✈️", "Flight Agent", "flight_results"),
    "hotel_agent":     ("🏨", "Hotel Agent", "hotel_results"),
    "visa_agent":      ("🛂", "Visa Agent", "visa_info"),
    "currency_agent":  ("💱", "Currency Agent", "currency_info"),
    "budget_agent":    ("💰", "Budget Agent", "budget_info"),
    "weather_agent":   ("☀️", "Weather Agent", "weather_info"),
    "transport_agent": ("🚍", "Transport Agent", "transport_info"),
    "itinerary_agent": ("🗓️", "Itinerary Agent", "itinerary"),
    "final_agent":     ("🧠", "Final Agent", None),
}


def render_key_value_card(title, rows):
    st.markdown(f"**{title}**")
    st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
    for key, value in rows:
        st.markdown(
            f"<div class='detail-row'><div class='detail-key'>{html.escape(str(key))}</div><div class='detail-val'>{html.escape(str(value))}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_weather_card(title, data: dict):
    city = data.get("city") or data.get("name") or "Unknown"
    temp = data.get("temperature") or data.get("temp")
    feels = data.get("feels_like")
    humidity = data.get("humidity")
    desc = data.get("description") or ""
    wind = data.get("wind_speed") or data.get("wind")

    sentence_parts = []
    if desc:
        sentence_parts.append(desc.capitalize())
    if temp is not None:
        sentence_parts.append(f"{temp}°C")
    if feels is not None:
        sentence_parts.append(f"(feels like {feels}°C)")

    sentence = ", ".join(sentence_parts) if sentence_parts else "No weather summary available."

    st.markdown(f"**{title}**")
    st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
    st.markdown(f"<div style='padding:0.35rem 0;'>{html.escape(city)} — {html.escape(sentence)}</div>", unsafe_allow_html=True)

    rows = []
    if humidity is not None:
        rows.append(("Humidity", humidity))
    if wind is not None:
        rows.append(("Wind Speed", f"{wind} m/s"))
    if rows:
        for key, value in rows:
            st.markdown(f"<div class='detail-row'><div class='detail-key'>{html.escape(str(key))}</div><div class='detail-val'>{html.escape(str(value))}</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def normalize_agent_payload(value):
    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        candidate = value.strip()
        if candidate.startswith("{") or candidate.startswith("["):
            try:
                return json.loads(candidate)
            except Exception:
                try:
                    return ast.literal_eval(candidate)
                except Exception:
                    return value

    return value


def render_friendly_error(title, value):
    error_text = ""

    if isinstance(value, dict):
        error_text = str(value.get("error", ""))
    else:
        error_text = str(value)

    lowered = error_text.lower()

    if "request_denied" in lowered:
        message = f"{title}: the mapping service denied the request."
    elif "weather data unavailable" in lowered:
        message = f"{title}: weather data is currently unavailable."
    elif error_text:
        message = f"{title}: {error_text}"
    else:
        message = f"{title}: no data returned."

    st.markdown(f"<div class='agent-error'>{html.escape(message)}</div>", unsafe_allow_html=True)


def get_downloads_dir():
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        downloads_dir = Path(user_profile) / "Downloads"
    else:
        downloads_dir = Path.home() / "Downloads"

    if downloads_dir.exists():
        return downloads_dir

    fallback_dir = Path.home() / "Downloads"
    if fallback_dir.exists():
        return fallback_dir

    return Path.cwd() / "Downloads"


def render_agent_value(field, title, value):
    value = normalize_agent_payload(value)

    if isinstance(value, dict) and not value:
        render_friendly_error(title, {})
        return

    if isinstance(value, dict) and "error" in value:
        render_friendly_error(title, value)
        return

    if field == "currency_info" and isinstance(value, dict):
        render_key_value_card(title, [
            ("From Currency", value.get("from_currency", "N/A")),
            ("To Currency", value.get("to_currency", "N/A")),
            ("Amount", value.get("amount", "N/A")),
            ("Exchange Rate", value.get("exchange_rate", "N/A")),
            ("Converted Amount", value.get("converted_amount", "N/A")),
        ])
        return

    if field == "budget_info" and isinstance(value, dict):
        render_key_value_card(title, [
            ("Flight Cost", value.get("flight_cost", "N/A")),
            ("Hotel Cost", value.get("hotel_cost", "N/A")),
            ("Food Cost", value.get("food_cost", "N/A")),
            ("Transport Cost", value.get("transport_cost", "N/A")),
            ("Activities Cost", value.get("activities_cost", "N/A")),
            ("Total Budget", value.get("total_budget", "N/A")),
        ])
        return

    # Ensure weather payloads (dict or stringified dict) render as a friendly card
    if field == "weather_info":
        parsed = value
        if isinstance(value, str):
            candidate = value.strip()
            try:
                parsed = json.loads(candidate)
            except Exception:
                try:
                    parsed = ast.literal_eval(candidate)
                except Exception:
                    parsed = value

        if isinstance(parsed, dict):
            render_weather_card(title, parsed)
            return

    # Ensure transport payloads (dict or stringified dict) render as a friendly card
    if field == "transport_info":
        parsed = value
        if isinstance(value, str):
            candidate = value.strip()
            try:
                parsed = json.loads(candidate)
            except Exception:
                try:
                    parsed = ast.literal_eval(candidate)
                except Exception:
                    parsed = value

        if isinstance(parsed, dict):
            origin = parsed.get("origin") or parsed.get("start_address") or "Unknown"
            destination = parsed.get("destination") or parsed.get("end_address") or "Unknown"

            # distance may be provided as text or as numeric kilometers
            distance = parsed.get("distance") or parsed.get("distance_km") or parsed.get("distance_text")
            if isinstance(distance, (int, float)):
                distance_str = f"{distance} km"
            else:
                distance_str = str(distance) if distance is not None else "N/A"

            # duration may be given as text or minutes
            duration = parsed.get("duration") or parsed.get("duration_minutes") or parsed.get("duration_text")
            duration_str = "N/A"
            try:
                if isinstance(duration, (int, float)):
                    mins = int(duration)
                    hrs = mins // 60
                    rem = mins % 60
                    duration_str = f"{hrs}h {rem}m" if hrs else f"{rem}m"
                elif isinstance(duration, str) and duration.strip():
                    duration_str = duration
            except Exception:
                duration_str = str(duration)

            st.markdown(f"**{title}**")
            st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
            st.markdown(f"<div style='padding:0.35rem 0;'>{html.escape(origin)} → {html.escape(destination)} — {html.escape(distance_str)} ({html.escape(duration_str)})</div>", unsafe_allow_html=True)

            rows = []
            if origin:
                rows.append(("Origin", origin))
            if destination:
                rows.append(("Destination", destination))
            if distance is not None:
                rows.append(("Distance", distance_str))
            if duration_str != "N/A":
                rows.append(("Duration", duration_str))

            for key, value in rows:
                st.markdown(f"<div class='detail-row'><div class='detail-key'>{html.escape(str(key))}</div><div class='detail-val'>{html.escape(str(value))}</div></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
            return

    st.markdown(f"**{title}**")
    try:
        if isinstance(value, (dict, list)):
            pretty = json.dumps(value, indent=2, ensure_ascii=False)
            st.markdown(f"<pre class='agent-pre'>{html.escape(pretty)}</pre>", unsafe_allow_html=True)
        else:
            if isinstance(value, str) and "error" in value.lower():
                st.markdown(f"<div class='agent-error'>{html.escape(value)}</div>", unsafe_allow_html=True)
            else:
                st.markdown(value)
    except Exception:
        st.markdown(str(value))

with st.sidebar:
    st.markdown("<div class='sidebar-title'>🌍 AI Travel Planner</div>", unsafe_allow_html=True)
    st.markdown("---")

    thread_id = st.text_input("👥 MADE BY", value="THE HACKERS GROUP",
                              help="Your session ID — keeps travel history across queries")

    st.markdown("<div class='sidebar-title'>Powered by</div>", unsafe_allow_html=True)
    for tech in ["🔗 LangGraph", "🧠 Groq · LLaMA 3.3 70B", "🐘 PostgreSQL", "🔍 Tavily Search", "✈️ AviationStack"]:
        st.markdown(f"<div class='sidebar-chip'>{tech}</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>Agent Pipeline</div>", unsafe_allow_html=True)
    # Render all agents from AGENT_META so new agents appear automatically
    for key, meta in AGENT_META.items():
        icon, label, _ = meta
        st.markdown(f"<div class='sidebar-chip'>{icon} {label}</div>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <img class="hero-bg"
         src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
         alt="airplane above clouds"/>
    <div class="hero-content">
        <div class="hero-badge">✦ Multi-Agent AI System</div>
        <div class="hero-title">✈️ AI Travel Booking System</div>
        <div class="hero-sub">Four specialized agents work together — searching flights, hotels, building an itinerary, and delivering your perfect trip plan.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Destination image strip ───────────────────────────────────────────────────
DESTINATIONS = [
    ("🇯🇵 Tokyo",     "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("🇫🇷 Paris",     "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("🇹🇭 Bangkok",   "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("🇮🇹 Rome",      "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("🇦🇪 Dubai",     "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]

cols = st.columns(5)
for col, (name, img_url) in zip(cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div style="border-radius:10px;overflow:hidden;position:relative;height:90px;cursor:pointer;">
            <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;filter:brightness(0.55);" />
            <div style="position:absolute;bottom:8px;left:0;right:0;text-align:center;
                        color:#fff;font-size:0.8rem;font-weight:600;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='input-label'>🗺️ Describe your trip</div>", unsafe_allow_html=True)

QUICK = ["7-day Japan under $2L", "Paris trip for 5 days", "Dubai weekend trip", "Bali backpacking 10 days"]
qcols = st.columns(len(QUICK))
quick_fill = ""
for qc, label in zip(qcols, QUICK):
    with qc:
        if st.button(label, key=f"q_{label}"):
            quick_fill = label

user_query = st.text_area(
    "",
    value=quick_fill,
    placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing under $2L",
    height=100,
    label_visibility="collapsed",
)

generate = st.button("🚀  Generate My Travel Plan", use_container_width=True)

# ── Agent pipeline ────────────────────────────────────────────────────────────
# `AGENT_META` is defined above (before the sidebar) so it's available to the sidebar.

if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        collected = {
            "flight_results": "", "hotel_results": "",
            "itinerary": "", "final_response": "", "llm_calls": 0,
            "transport_info": "", "visa_info": "", "budget_info": "",
            "currency_info": "", "weather_info": "",
        }

        st.markdown("---")
        st.markdown("<div class='sec-head'><span>🤖 Agent Pipeline — Live</span></div>",
                    unsafe_allow_html=True)

        # Include new agents' result placeholders in the streaming input
        stream_init = {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "transport_info": "",
            "visa_info": "",
            "budget_info": "",
            "currency_info": "",
            "weather_info": "",
            "llm_calls": 0,
        }

        for chunk in app.stream(stream_init, config=config, stream_mode="updates"):
            # Debug: show incoming chunk keys (helps verify backend field names)
            # st.write(list(chunk.keys()))  # uncomment for interactive debugging
            for node_name, state_update in chunk.items():
                meta = AGENT_META.get(node_name, ("🔧", node_name, None))
                icon, label, result_field = meta

                with st.status(f"{icon}  {label}", state="complete", expanded=True):
                    if node_name == "final_agent":
                        msgs = state_update.get("messages", [])
                        text = msgs[-1].content if msgs else ""
                        collected["final_response"] = text
                        # final text is plain string
                        st.markdown(text or "_No final response._")
                    else:
                        if result_field:
                            text = state_update.get(result_field, "")
                            collected[result_field] = text
                            render_agent_value(result_field, label, text)

                    collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])

        # Metrics
        agents_run = len(AGENT_META)
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box"><div class="metric-val">{agents_run}</div><div class="metric-lbl">Agents Run</div></div>
            <div class="metric-box"><div class="metric-val">{collected['llm_calls']}</div><div class="metric-lbl">LLM Calls</div></div>
            <div class="metric-box"><div class="metric-val">✅</div><div class="metric-lbl">Status</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Final plan card and individual agent sections
        st.markdown("<div class='sec-head'><span>🧠 Agent Outputs</span></div>", unsafe_allow_html=True)
        # Show each agent's collected output (if any) using field names from backend
        for field, title in [
            ("flight_results", "✈️ Flight Results"),
            ("hotel_results", "🏨 Hotel Results"),
            ("transport_info", "🚍 Transport Results"),
            ("visa_info", "🛂 Visa Results"),
            ("budget_info", "💰 Budget Results"),
            ("currency_info", "💱 Currency Results"),
            ("weather_info", "☀️ Weather Results"),
            ("itinerary", "🗓️ Itinerary"),
        ]:
            val = collected.get(field, "_N/A_") or "_N/A_"
            render_agent_value(field, title, val)

        if collected["final_response"]:
            st.markdown("<div class='sec-head'><span>🧠 Final Travel Plan</span></div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='final-card'>{collected['final_response']}</div>",
                        unsafe_allow_html=True)

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"
        save_dir = get_downloads_dir()
        save_dir.mkdir(parents=True, exist_ok=True)

        file_content = f"""# Travel Plan
    **Query:** {user_query}
    **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    **User ID:** {thread_id}

    ---

    ## ✈️ Flight Information
    {collected['flight_results'] or 'N/A'}

    ---

    ## 🏨 Hotel Information
    {collected['hotel_results'] or 'N/A'}

    ---

    ## 🚍 Transport Information
    {collected['transport_info'] or 'N/A'}

    ---

    ## 🛂 Visa Information
    {collected['visa_info'] or 'N/A'}

    ---

    ## 💰 Budget / Costing
    {collected['budget_info'] or 'N/A'}

    ---

    ## 💱 Currency Info
    {collected['currency_info'] or 'N/A'}

    ---

    ## ☀️ Weather Notes
    {collected['weather_info'] or 'N/A'}

    ---

    ## 🗓️ Itinerary
    {collected['itinerary'] or 'N/A'}

    ---

    ## 🧠 Final Travel Plan
    {collected['final_response'] or 'N/A'}

    ---
    *LLM Calls: {collected['llm_calls']}*
    """
        with open(save_dir / filename, "w", encoding="utf-8") as f:
            f.write(file_content)

        dl_col, info_col = st.columns([1, 3])
        with dl_col:
            st.download_button("⬇️ Download Plan", data=file_content,
                               file_name=filename, mime="text/markdown",
                               use_container_width=True)
        with info_col:
            st.markdown(f"<div class='save-bar'>📁 Auto-saved → <code>{html.escape(str(save_dir / filename))}</code></div>",
                        unsafe_allow_html=True)