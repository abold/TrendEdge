# utils/theming.py
import streamlit as st
import plotly.io as pio

PALETTE = {
    "bg": "#0b1220",
    "panel": "rgba(15, 23, 42, 0.85)",
    "border": "rgba(255,255,255,0.08)",
    "text": "#e5e7eb",
    "muted": "#9aa4b2",
    "accent": "#f97316",   # ← orange accent
    "up": "#22c55e",
    "down": "#ef4444",
}

# extra derived colors (kept local to avoid breaking callers)
_SURFACE = "rgba(30, 41, 59, 0.95)"     # slate-800
_CODE_BG = "#0a0f1a"                     # near-bg, high contrast with text

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": PALETTE["text"]},
        "xaxis": {"gridcolor": "rgba(255,255,255,0.08)"},
        "yaxis": {"gridcolor": "rgba(255,255,255,0.08)"},
        "legend": {"bgcolor": "rgba(0,0,0,0)"},
    }
}

def apply_base_css():
    """Inject global CSS + register Plotly template (full theme + larger fonts)."""
    st.markdown(
        f"""
        <style>
        /* ===== Global font scaling ===== */
        html, body {{
          font-size: 1.4rem !important;   /* ~6% larger overall */
          line-height: 1.6 !important;
        }}

        /* ===== App background ===== */
        .stApp {{
          background: linear-gradient(135deg, #0a0f1a 0%, #1e1b4b 100%) !important;
          color: {PALETTE['text']};
        }}

        /* ===== Panels / cards ===== */
        section.main > div > div,
        .st-emotion-cache-1y4p8pa,
        .st-emotion-cache-1wmy9hl {{
          background: {_SURFACE} !important;
          border: 1px solid {PALETTE['border']} !important;
          border-radius: 18px !important;
          box-shadow: 0 8px 24px rgba(0,0,0,.25);
        }}

        /* ===== Sidebar ===== */
        [data-testid="stSidebar"] > div {{
          background: linear-gradient(180deg, #1e1b4b 0%, #0a0f1a 80%) !important;
          border-right: 1px solid {PALETTE['border']} !important;
          box-shadow: inset -2px 0 12px rgba(255,136,0,.25) !important;
        }}
        [data-testid="stSidebar"] {{
          width: 340px !important;     /* wider than default */
          min-width: 320px !important;
          max-width: 380px !important;
        }}
        /* ===== Beautiful primary buttons (global + sidebar) ===== */
        .stButton > button,
        [data-testid="stSidebar"] .stButton > button {{
          position: relative;
          overflow: hidden;
          display: inline-flex;
          align-items: center;
          justify-content: center;

          background: linear-gradient(90deg, {PALETTE['accent']} 0%, #fb923c 100%) !important; /* orange gradient */
          color: #0b1220 !important;

          border: 1px solid rgba(255,255,255,0.18) !important;       /* soft glass edge */
          border-radius: 14px !important;
          padding: .8rem 1.25rem !important;
          font-weight: 800 !important;
          font-size: 1.06rem !important;
          letter-spacing: .02em;

          box-shadow:
            0 8px 24px rgba(249,115,22,.25),           /* outer colored glow */
            inset 0 1px 0 rgba(255,255,255,.35),       /* top highlight */
            inset 0 -1px 0 rgba(0,0,0,.25);            /* bottom shade */

          transition:
            transform .18s ease,
            box-shadow .18s ease,
            filter .18s ease;
        }}

        /* glossy sheen sweep */
        .stButton > button::before,
        [data-testid="stSidebar"] .stButton > button::before {{
          content: "";
          position: absolute;
          inset: 0;
          background: linear-gradient(
            120deg,
            rgba(255,255,255,.15) 0%,
            rgba(255,255,255,0) 35%,
            rgba(255,255,255,.10) 60%,
            rgba(255,255,255,0) 100%
          );
          transform: translateX(-120%);
          transition: transform .6s ease;
          pointer-events: none;
        }}

        /* hover: brighter, slight lift, sheen slides across */
        .stButton > button:hover,
        [data-testid="stSidebar"] .stButton > button:hover {{
          filter: brightness(1.06);
          transform: translateY(-1px);
          box-shadow:
            0 10px 28px rgba(249,115,22,.30),
            inset 0 1px 0 rgba(255,255,255,.45),
            inset 0 -1px 0 rgba(0,0,0,.22);
        }}
        .stButton > button:hover::before,
        [data-testid="stSidebar"] .stButton > button:hover::before {{
          transform: translateX(0%);
        }}

        /* active: crisp press */
        .stButton > button:active,
        [data-testid="stSidebar"] .stButton > button:active {{
          transform: translateY(0);
          filter: brightness(1.0);
          box-shadow:
            0 6px 16px rgba(249,115,22,.22),
            inset 0 1px 0 rgba(255,255,255,.30),
            inset 0 -2px 0 rgba(0,0,0,.28);
        }}

        /* keyboard focus */
        .stButton > button:focus-visible,
        [data-testid="stSidebar"] .stButton > button:focus-visible {{
          outline: 3px solid rgba(251,146,60,.9) !important;   /* bright orange */
          outline-offset: 2px;
        }}

        /* disabled */
        .stButton > button:disabled,
        [data-testid="stSidebar"] .stButton > button:disabled {{
          filter: saturate(.6) brightness(.9);
          cursor: not-allowed !important;
          box-shadow:
            0 4px 12px rgba(0,0,0,.25),
            inset 0 1px 0 rgba(255,255,255,.25),
            inset 0 -1px 0 rgba(0,0,0,.2) !important;
        }}

        /* optional: full-width sidebar buttons feel nicer */
        [data-testid="stSidebar"] .stButton {{ width: 100%; }}
        [data-testid="stSidebar"] .stButton > button {{ width: 100%; }}


        /* ===== Sidebar labels & helper text ===== */
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {{
          font-size: 1.05rem !important;
          font-weight: 800 !important;
          letter-spacing: .01em;
        }}
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stMarkdown p {{
          color: {PALETTE['muted']} !important;
          font-size: 1rem !important;           /* bigger */
          font-weight: 600 !important;
        }}

        /* ===== Inputs (main + sidebar) ===== */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox [role="combobox"],
        .stDateInput input {{
          font-size: 1rem !important;           /* bigger */
          height: 2.5rem !important;            /* taller */
          padding: .45rem .75rem !important;
        }}
        ::placeholder {{ color: {PALETTE['muted']} !important; opacity: 1; }}

        /* Sidebar input surfaces */
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] [role="combobox"],
        [data-testid="stSidebar"] .stDateInput input {{
          background: rgba(17,24,39,.8) !important;
          color: {PALETTE['text']} !important;
          border: 1px solid rgba(255,255,255,.08) !important;
          border-radius: 12px !important;
          box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
        }}
        [data-testid="stSidebar"] input:focus,
        [data-testid="stSidebar"] [role="combobox"]:focus,
        [data-testid="stSidebar"] .stDateInput input:focus {{
          outline: 2px solid rgba(249,115,22,.75) !important;
          outline-offset: 2px;
          border-color: rgba(249,115,22,.4) !important;
        }}

        /* Number/date step buttons */
        [data-testid="stSidebar"] .stNumberInput button,
        [data-testid="stSidebar"] .stDateInput button {{
          color: {PALETTE['text']} !important;
          background: rgba(255,255,255,.06) !important;
          border: 1px solid rgba(255,255,255,.10) !important;
          border-radius: 10px !important;
        }}
        [data-testid="stSidebar"] .stNumberInput button:hover,
        [data-testid="stSidebar"] .stDateInput button:hover {{ filter: brightness(1.1); }}

        /* ===== Typography ===== */
        html {{ -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
        body {{ line-height: 1.6; }}

        h1, .stMarkdown h1 {{
          font-size: 2.4rem !important;         /* bigger */
          font-weight: 800;
          letter-spacing: -.02em;
          color: {PALETTE['text']};
        }}
        h2, .stMarkdown h2 {{
          font-size: 1.6rem !important;         /* bigger */
          font-weight: 700;
          letter-spacing: -.01em;
          margin-top: .6rem;
          color: {PALETTE['text']};
        }}
        h3, .stMarkdown h3 {{
          font-size: 1.25rem !important;        /* bigger */
          font-weight: 700;
          color: {PALETTE['text']};
        }}
        h4, .stMarkdown h4 {{
          font-size: 1.05rem !important;        /* bigger */
          font-weight: 600;
          color: {PALETTE['text']};
        }}

        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {{
          color: {PALETTE['text']};
          font-size: 1rem !important;           /* bigger */
        }}

        small, .stCaption, .stMarkdown small {{ color: {PALETTE['muted']} !important; }}

        /* ===== Tabs ===== */
        .stTabs [role="tab"] {{
          color: {PALETTE['muted']} !important;
          font-weight: 600 !important;
          padding: .6rem .9rem !important;
          font-size: 1rem !important;
        }}
        .stTabs [role="tab"][aria-selected="true"] {{
          color: {PALETTE['text']} !important;
          border-bottom: 2px solid {PALETTE['accent']} !important;
        }}

        /* ===== Expanders ===== */
        .st-expanderHeader {{ 
          color: {PALETTE['text']} !important; 
          font-weight: 600; 
        }}
        .st-expanderHeader:hover {{ filter: brightness(1.05); }}

        /* ===== “Pill” tag ===== */
        .pill {{
          background: rgba(249,115,22,.18);
          border: 1px solid rgba(249,115,22,.5);
          color: {PALETTE['text']};
          font-size: .85rem;                    /* slightly bigger */
          border-radius: 999px;
          padding: .25rem .6rem;
        }}

        /* ===== Metrics ===== */
        [data-testid="stMetric"]{{
          background: rgba(30,41,59,.85) !important;
          border: 1px solid rgba(255,255,255,0.08) !important;
          border-radius: 14px !important;
          padding: .9rem 1rem !important;
          box-shadow: 0 6px 16px rgba(0,0,0,.25);
        }}
        [data-testid="stMetricLabel"] > div {{
          color: {PALETTE['muted']} !important;
          font-weight: 500 !important;
          letter-spacing: .02em;
        }}
        [data-testid="stMetricValue"] > div {{
          font-weight: 900 !important;
          font-size: clamp(1.9rem, 2.8vw, 3rem) !important;  /* bigger */
          line-height: 1.1 !important;
        }}
        [data-testid="stMetricValue"] > div.positive {{
          color: #39FF14 !important;
          text-shadow: 0 0 8px rgba(57,255,20,0.8), 0 0 16px rgba(57,255,20,0.5);
        }}
        [data-testid="stMetricValue"] > div.violet {{
          color: #a855f7 !important;
          text-shadow: 0 0 8px rgba(168,85,247,0.8), 0 0 16px rgba(168,85,247,0.5);
        }}
        [data-testid="stMetricValue"] > div.negative {{
          color: #FF073A !important;
          text-shadow: 0 0 8px rgba(255,7,58,0.8), 0 0 16px rgba(255,7,58,0.5);
        }}
        [data-testid="stMetricDelta"] {{
          font-weight: 700 !important;
          opacity: .95 !important;
        }}
        [data-testid="stMetricDelta"]:has(svg[aria-label="caret-up"]) {{ color: {PALETTE['up']} !important; }}
        [data-testid="stMetricDelta"]:has(svg[aria-label="caret-down"]) {{ color: {PALETTE['down']} !important; }}
        [data-testid="stMetricDelta"] svg {{ fill: currentColor !important; }}
        [data-testid="stMetric"] div:where(.st-emotion-cache-ue6h4q, .st-emotion-cache-12w0qpk, .st-emotion-cache-ocqkz7) {{ 
          margin: 0 !important;
        }}

        /* ===== Mobile ===== */
        @media (max-width: 640px) {{
          h1, .stMarkdown h1 {{ font-size: 1.7rem !important; }}
          h2, .stMarkdown h2 {{ font-size: 1.3rem !important; }}
          .block-container {{ padding: 0.5rem 0.8rem; }}
          .stButton > button {{ padding: 0.6rem 1rem !important; font-size: 1rem !important; }}
          html, body {{ overflow-x: hidden; }}

          [data-testid="stSidebar"] {{ width: 100% !important; }}

          .stPlotlyChart,
          .stPlotlyChart > div,
          .stPlotlyChart .js-plotly-plot,
          .stPlotlyChart .plot-container,
          .stPlotlyChart canvas {{
            width: 100% !important;
            max-width: 100% !important;
          }}
          .stPlotlyChart {{ margin-left: 0 !important; margin-right: 0 !important; }}

          .stDataFrame {{ width: 100% !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Plotly template stays the same
    pio.templates["te_dark"] = PLOTLY_TEMPLATE
    pio.templates.default = "te_dark"


