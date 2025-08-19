# utils/theming.py
import streamlit as st
import plotly.io as pio

PALETTE = {
    "bg": "#0b1220",
    "panel": "rgba(15, 23, 42, 0.85)",
    "border": "rgba(255,255,255,0.08)",
    "text": "#e5e7eb",
    "muted": "#9aa4b2",
    "accent": "#8b5cf6",
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
    """Inject global CSS + register Plotly template."""
    st.markdown(
        f"""
        <style>
        /* ===== App background ===== */
        .stApp {{
          background:
            radial-gradient(1200px 600px at 0% -10%, rgba(139,92,246,.08), transparent),
            radial-gradient(900px 500px at 100% 0%, rgba(236,72,153,.06), transparent),
            #0f172a; /* slate-900 */
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
          background: linear-gradient(180deg, rgba(15,23,42,.9), rgba(15,23,42,.6));
          border-right: 1px solid {PALETTE['border']};
        }}
        [data-testid="stSidebar"] * {{ color: {PALETTE['text']} !important; }}

        /* ===== Typography ===== */
        h1, h2, h3, h4 {{ letter-spacing: -.02em; color: {PALETTE['text']}; }}
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {{ color: {PALETTE['text']}; }}
        ::placeholder {{ color: {PALETTE['muted']} !important; opacity:.95; }}

        /* ===== Inputs ===== */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox [role="combobox"],
        .stDateInput input {{
          background: {_SURFACE} !important;
          color: {PALETTE['text']} !important;
          border: 1px solid {PALETTE['border']} !important;
          border-radius: 12px !important;
        }}
        .stNumberInput button, .stDateInput button {{ color: {PALETTE['text']} !important; }}

        /* ===== Buttons ===== */
        .stButton > button {{
          background: {PALETTE['accent']} !important;
          color: #0b1220 !important;
          border: none !important;
          border-radius: 12px !important;
          padding: .6rem 1rem !important;
          font-weight: 600;
          box-shadow: 0 2px 8px rgba(0,0,0,.2);
        }}
        .stButton > button:hover {{ filter: brightness(1.06); transform: translateY(-1px); }}
        .stButton > button:focus {{ outline: 2px solid rgba(34,211,238,.9); outline-offset: 2px; }}

        /* ===== Code & Tracebacks (the unreadable part) ===== */
        pre, code, kbd, samp {{
          background: {_CODE_BG} !important;
          color: {PALETTE['text']} !important;
          border-radius: 8px !important;
          border: 1px solid {PALETTE['border']} !important;
        }}
        .stException, div[role="alert"] {{
          background: {_SURFACE} !important;
          border: 1px solid {PALETTE['border']} !important;
          color: {PALETTE['text']} !important;
        }}
        .stException pre, .stException code {{
          background: {_CODE_BG} !important;
          color: {PALETTE['text']} !important;
        }}
        /* left color bars for quick scanning */
        .stSuccess, .stAlert-success {{ border-left: 4px solid {PALETTE['up']} !important; }}
        .stWarning, .stAlert-warning {{ border-left: 4px solid #f59e0b !important; }}
        .stError, .stAlert-error, .stException {{ border-left: 4px solid {PALETTE['down']} !important; }}

        /* ===== Tables / DataFrames ===== */
        .stDataFrame, .stDataFrame tbody, .stDataFrame thead {{
          color: {PALETTE['text']} !important;
          background: {_SURFACE} !important;
        }}

        /* ===== Links ===== */
        a, .stMarkdown a {{ color: {PALETTE['accent']} !important; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}

        /* ===== Version pill (kept) ===== */
        .pill {{
          display:inline-block; padding:.25rem .6rem; border-radius:999px;
          background: rgba(139,92,246,.18); border:1px solid rgba(139,92,246,.5);
          color:{PALETTE['text']}; font-size:.8rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Plotly template stays the same
    pio.templates["te_dark"] = PLOTLY_TEMPLATE
    pio.templates.default = "te_dark"
