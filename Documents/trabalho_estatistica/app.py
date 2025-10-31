import streamlit as st

from data_models import DEFAULT_DATA
from ui_components import render_dashboard, render_editor


st.set_page_config(
    page_title="Analise de Lancamento: Apple iPhone (2021-2025)",
    layout="wide",
    page_icon=":iphone:",
)


def init_state() -> None:
    if "dataset" not in st.session_state:
        st.session_state["dataset"] = DEFAULT_DATA.copy()


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #0c101b;
                color: #f1f5f9;
                font-family: 'Inter', sans-serif;
            }
            .stDataFrame {
                background-color: rgba(30, 41, 59, 0.6);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    init_state()
    inject_base_styles()

    st.sidebar.title("Exibicao")
    view = st.sidebar.radio("Escolha a tela", ("Dashboard", "Editor"), key="view_selector")

    if st.sidebar.button("Restaurar valores originais"):
        st.session_state["dataset"] = DEFAULT_DATA.copy()
        st.experimental_rerun()

    current_df = st.session_state["dataset"].copy()

    if view == "Dashboard":
        render_dashboard(current_df)
    else:
        render_editor(current_df)


if __name__ == "__main__":
    main()
