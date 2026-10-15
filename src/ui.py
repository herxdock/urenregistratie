import streamlit as st


def inject_mobile_css():
    st.markdown(
        """
        <style>
        html, body, [class*="css"] { font-size: 18px; }
        h1 { font-size: 1.7rem !important; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.2rem !important; }
        .stButton > button {
            font-size: 1.05rem;
            padding: 0.85rem 1rem;
            border-radius: 12px;
            width: 100%;
        }
        .stTextInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stTimeInput input {
            font-size: 1.1rem !important;
            padding: 0.6rem !important;
        }
        div[data-baseweb="select"] > div {
            font-size: 1.1rem !important;
            padding: 0.4rem !important;
        }
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
