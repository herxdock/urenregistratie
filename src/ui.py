import streamlit as st


def inject_mobile_css():
    st.markdown(
        """
        <style>
        /* ---------- Basis ---------- */
        html, body, [class*="css"] {
            font-size: 18px;
            -webkit-tap-highlight-color: transparent;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2.5rem;
            max-width: 720px;
        }

        /* ---------- Koppen ---------- */
        h1 { font-size: 1.65rem !important; line-height: 1.25; margin-bottom: .35rem !important; }
        h2 { font-size: 1.35rem !important; margin-top: .5rem !important; }
        h3 { font-size: 1.15rem !important; }

        /* ---------- Knoppen ---------- */
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            font-size: 1.05rem !important;
            font-weight: 600;
            padding: 0.85rem 1rem !important;
            border-radius: 14px !important;
            width: 100%;
            min-height: 52px;
        }
        /* Primary = duidelijke actiekleur */
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            background: linear-gradient(180deg,#0d6efd,#0a58ca) !important;
            border: none !important;
            box-shadow: 0 2px 6px rgba(13,110,253,.35);
        }

        /* ---------- Invoervelden ---------- */
        .stTextInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stTimeInput input,
        div[data-baseweb="select"] > div {
            font-size: 1.08rem !important;
            padding: 0.6rem 0.7rem !important;
            border-radius: 10px !important;
        }

        /* ---------- Labels ---------- */
        label, .stSelectbox label, .stTextArea label,
        .stDateInput label, .stTimeInput label {
            font-size: 0.98rem !important;
            font-weight: 600;
            color: #334155;
        }

        /* ---------- Shift-kaarten ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            border: 1px solid #e2e8f0 !important;
            background: #ffffff;
            padding: 4px 2px;
            box-shadow: 0 1px 3px rgba(15,23,42,.05);
        }
        /* Ruimte tussen kaarten */
        div[data-testid="stVerticalBlockBorderWrapper"] + div[data-testid="stVerticalBlockBorderWrapper"] {
            margin-top: .75rem;
        }

        /* ---------- Metrics strak ---------- */
        div[data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
            color: #0d6efd;
        }
        div[data-testid="stMetricLabel"] {
            font-size: .85rem !important;
        }

        /* ---------- Sidebar (indien gebruikt) ---------- */
        section[data-testid="stSidebar"] {
            background: #f8fafc;
        }
        section[data-testid="stSidebar"] a {
            font-size: 1.05rem !important;
            padding: .55rem .75rem !important;
            border-radius: 10px;
        }

        /* ---------- Radio/checkbox iets groter ---------- */
        .stRadio label, .stCheckbox label { font-size: 1rem !important; }

        /* ---------- Tabs (voor later) ---------- */
        button[data-baseweb="tab"] {
            font-size: 1rem !important;
            padding: .6rem 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
