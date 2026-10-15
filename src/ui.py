import streamlit as st


def inject_mobile_css():
    st.markdown(
        """
        <style>
        /* ---------- Basis ---------- */
        html, body, [class*="css"] {
            font-size: 20px;
            -webkit-tap-highlight-color: transparent;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2.5rem;
            max-width: 720px;
        }

        /* ---------- Koppen ---------- */
        h1 { font-size: 1.9rem !important; line-height: 1.25; margin-bottom: .4rem !important; }
        h2 { font-size: 1.55rem !important; margin-top: .6rem !important; }
        h3 { font-size: 1.3rem !important; }

        /* ---------- Knoppen ---------- */
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            font-size: 1.15rem !important;
            font-weight: 600;
            padding: 1rem 1.1rem !important;
            border-radius: 14px !important;
            width: 100%;
            min-height: 58px;
        }

        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background: #6b8dab !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 2px 6px rgba(107,141,171,.25);
        }
        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primary"]:hover {
            background: #5a7a95 !important;
        }

        .stButton > button[kind="secondary"] {
            background: #eef2f6 !important;
            color: #334155 !important;
            border: 1px solid #d8e0e8 !important;
        }
        .stButton > button[kind="secondary"]:hover {
            background: #e3e9ef !important;
        }

        /* ---------- Invoervelden ---------- */
        .stTextInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stTimeInput input,
        div[data-baseweb="select"] > div {
            font-size: 1.15rem !important;
            padding: 0.7rem 0.8rem !important;
            border-radius: 10px !important;
        }

        /* ---------- Labels ---------- */
        label, .stSelectbox label, .stTextArea label,
        .stDateInput label, .stTimeInput label, .stRadio label {
            font-size: 1.05rem !important;
            font-weight: 600;
            color: #334155;
        }

        /* ---------- Kaarten ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            border: 1px solid #e2e8f0 !important;
            background: #ffffff;
            padding: 8px 6px;
            box-shadow: 0 1px 3px rgba(15,23,42,.05);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] + div[data-testid="stVerticalBlockBorderWrapper"] {
            margin-top: .85rem;
        }

        /* ---------- KPI-grid ---------- */
        .kpi-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: .25rem;
        }
        .kpi-card {
            background: #f5f8fb;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 96px;
        }
        .kpi-label {
            font-size: 0.92rem;
            color: #64748b;
            font-weight: 600;
            line-height: 1.2;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 1.7rem;
            color: #4a6b8a;
            font-weight: 700;
            line-height: 1.05;
            word-break: break-word;
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: #f8fafc;
        }
        section[data-testid="stSidebar"] a {
            font-size: 1.15rem !important;
            padding: .65rem .8rem !important;
            border-radius: 10px;
        }

        /* ---------- Tabs ---------- */
        button[data-baseweb="tab"] {
            font-size: 1.05rem !important;
            padding: .65rem 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_grid(items):
    """items: list van (label, value) tuples. Rendert een 2-koloms grid van kaartjes."""
    cards = "".join(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'</div>'
        for label, value in items
    )
    st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)
