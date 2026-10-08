"""Actions partagées sur l'état de session (texte reconnu et historique).

Un seul point d'entrée pour enregistrer une reconnaissance valide : le
texte affiché et le journal d'historique ne peuvent pas se désynchroniser.
"""

from datetime import datetime

import streamlit as st

from src.gui.ui_logic import category_of


def add_recognition(label, conf) -> None:
    """Ajoute un signe validé au texte et au journal d'historique."""
    label = str(label)
    st.session_state.confirmed_text.append(label)
    st.session_state.history_log.append({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "label": label,
        "category": category_of(label),
        "conf": float(conf),
    })
