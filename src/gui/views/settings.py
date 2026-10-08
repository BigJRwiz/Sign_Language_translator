"""Page « Paramètres » : réglages utiles à l'utilisateur.

Les valeurs sont conservées sous des clés « cfg_* » (persistantes), les
widgets utilisent des clés « w_* » : Streamlit supprime l'état d'un widget
lorsqu'il n'est plus affiché, la valeur réelle doit donc vivre ailleurs.
Aucun paramètre interne du modèle d'IA n'est exposé.
"""

import streamlit as st

from src.gui import theme
from src.gui.ui_logic import MODE_ALPHABET, MODE_WORDS

DEFAULT_THRESHOLD = 0.6
MODE_LABELS = {MODE_ALPHABET: "Alphabet (lettres)", MODE_WORDS: "Signes courants (mots)"}


def _sync_threshold() -> None:
    st.session_state.cfg_threshold = st.session_state.w_threshold / 100


def _sync_landmarks() -> None:
    st.session_state.cfg_show_landmarks = bool(st.session_state.w_landmarks)


def _sync_mode() -> None:
    st.session_state.mode = st.session_state.w_mode


def _reset_defaults() -> None:
    st.session_state.cfg_threshold = DEFAULT_THRESHOLD
    st.session_state.cfg_show_landmarks = True
    st.session_state.mode = MODE_ALPHABET
    # les widgets gardent leur propre état : on le réaligne aussi
    st.session_state.w_threshold = round(DEFAULT_THRESHOLD * 100)
    st.session_state.w_landmarks = True
    st.session_state.w_mode = MODE_ALPHABET


def render() -> None:
    st.markdown(
        theme.page_header_html(
            "sliders", "Paramètres",
            "Ajustez le comportement de la reconnaissance.",
        ),
        unsafe_allow_html=True,
    )

    with st.container(key="card_settings_reco"):
        st.markdown(theme.card_title("target", "Reconnaissance"), unsafe_allow_html=True)
        st.slider(
            "Seuil minimal de confiance",
            min_value=50, max_value=95, step=5,
            value=round(st.session_state.cfg_threshold * 100),
            format="%d%%", key="w_threshold", on_change=_sync_threshold,
            help="En dessous de ce score, un signe n'est pas ajouté au texte.",
        )
        st.radio(
            "Mode de reconnaissance",
            options=[MODE_ALPHABET, MODE_WORDS],
            index=0 if st.session_state.mode == MODE_ALPHABET else 1,
            format_func=lambda m: MODE_LABELS[m],
            horizontal=True, key="w_mode", on_change=_sync_mode,
        )

    with st.container(key="card_settings_display"):
        st.markdown(theme.card_title("eye", "Affichage"), unsafe_allow_html=True)
        st.checkbox(
            "Afficher les landmarks MediaPipe sur la vidéo",
            value=st.session_state.cfg_show_landmarks,
            key="w_landmarks", on_change=_sync_landmarks,
        )
        st.selectbox("Langue d'affichage", ["Français"], disabled=True, key="w_lang")
        st.caption("Le kiswahili sera proposé lorsque cette fonctionnalité sera prête.")

    with st.container(key="card_settings_camera"):
        st.markdown(theme.card_title("camera", "Caméra"), unsafe_allow_html=True)
        st.markdown(
            theme.note_html(
                "La caméra se choisit directement dans le lecteur vidéo de la page "
                "Reconnaissance (bouton « SELECT DEVICE »)."
            ),
            unsafe_allow_html=True,
        )

    st.button("Réinitialiser les paramètres", key="btn_settings_reset", on_click=_reset_defaults)
    st.caption("Les réglages s'appliquent dès le retour sur la page Reconnaissance.")
