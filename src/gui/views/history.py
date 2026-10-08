"""Page « Historique » : journal des reconnaissances validées.

Les entrées sont enregistrées par src.gui.state.add_recognition dans
st.session_state.history_log (conservé tant que la session du navigateur
reste ouverte). Cette page ne fait que lire et exporter ce journal.
"""

import streamlit as st

from src.gui import theme
from src.gui.ui_logic import history_stats, history_to_csv

DISPLAY_LIMIT = 100


def _clear_history() -> None:
    st.session_state.history_log = []


def render() -> None:
    st.markdown(
        theme.page_header_html(
            "clock", "Historique",
            "Signes reconnus pendant cette session.",
        ),
        unsafe_allow_html=True,
    )

    entries = st.session_state.history_log
    stats = history_stats(entries)

    st.markdown(
        theme.stat_cards_html([
            (stats["total"], "reconnaissances"),
            (stats["letters"], "lettres"),
            (stats["words"], "signes courants"),
            (f'{stats["avg_conf"]:.0f} %' if stats["total"] else "—", "confiance moyenne"),
        ]),
        unsafe_allow_html=True,
    )

    with st.container(key="card_history"):
        st.markdown(theme.card_title("clock", "Reconnaissances récentes"), unsafe_allow_html=True)
        if entries:
            st.markdown(theme.history_table_html(entries, DISPLAY_LIMIT), unsafe_allow_html=True)
            if len(entries) > DISPLAY_LIMIT:
                st.caption(f"Les {DISPLAY_LIMIT} plus récentes sont affichées ({len(entries)} au total).")
        else:
            st.markdown(
                theme.note_html(
                    "Aucune reconnaissance pour l'instant. Fais un signe sur la page "
                    "Reconnaissance : il apparaîtra ici."
                ),
                unsafe_allow_html=True,
            )

        c1, c2, _ = st.columns([1, 1, 1.4])
        with c1:
            st.download_button(
                "Exporter en CSV",
                data=history_to_csv(entries),
                file_name="historique_signes.csv",
                mime="text/csv",
                disabled=not entries,
                key="btn_export",
            )
        with c2:
            st.button(
                "Vider l'historique", key="btn_history_clear",
                on_click=_clear_history, disabled=not entries,
            )
