"""Heri Kwetu Sign — Interface Streamlit (Signes -> Texte).

Refonte de la couche présentation uniquement. La reconnaissance
(SignProcessor : MediaPipe, modèle, stabilité, confiance) est identique
à la version précédente ; seuls trois ajouts d'intégration y figurent :
  - current_label / current_conf : exposent la détection en cours à l'UI ;
  - reset_detection()            : bouton « Nouvelle détection ».

Mise en page : caméra à gauche, résultats à droite (rafraîchis par un
fragment Streamlit, sans recharger la page ni interrompre la webcam).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import queue
import time

import av
import cv2
import joblib
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from src.detection.hand_detector import HandDetector
from src.gui import theme
from src.gui.state import add_recognition
from src.gui.ui_logic import (
    MODE_ALPHABET, MODE_WORDS, NAV_ITEMS, PAGE_HISTORY, PAGE_RECO, PAGE_SETTINGS,
    PAGE_SIGNS, detection_view, mode_accepts,
)
from src.gui.views import history as history_view
from src.gui.views import signs as signs_view
from src.recognition.features import landmarks_object_to_features

MODEL_PATH = "data/models/alphabet_classifier.joblib"
CONF_THRESHOLD = 0.6
STABILITY_FRAMES = 10
MAX_PROC_RETRIES = 30
RECENT_COUNT = 6


# ==========================================================================
# RECONNAISSANCE (logique inchangée)
# ==========================================================================
class SignProcessor(VideoProcessorBase):
    """Traite chaque frame du flux WebRTC : détection + prédiction stabilisée."""

    def __init__(self) -> None:
        self.detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
        try:
            self.model = joblib.load(MODEL_PATH)
        except FileNotFoundError:
            self.model = None

        self.result_queue: queue.Queue = queue.Queue()
        self.validated_conf: queue.Queue = queue.Queue()  # confiance du signe validé
        self._last_label = None
        self._stable_count = 0
        self._awaiting_release = False

        # Ajouts d'intégration UI (lecture seule côté interface)
        self.current_label = None
        self.current_conf = 0.0

    def reset_detection(self) -> None:
        """Permet de re-détecter le même signe sans retirer la main."""
        self._last_label = None
        self._stable_count = 0
        self._awaiting_release = False

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img, landmarks_list = self.detector.find_hands(img)

        if landmarks_list and self.model is not None:
            features = landmarks_object_to_features(landmarks_list[0])
            prediction = self.model.predict([features])[0]
            confidence = max(self.model.predict_proba([features])[0])

            self.current_label = str(prediction)
            self.current_conf = float(confidence)

            cv2.putText(
                img, f"{prediction} ({confidence:.0%})", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3,
            )

            if confidence >= CONF_THRESHOLD:
                if prediction != self._last_label:
                    self._last_label = prediction
                    self._stable_count = 1
                    self._awaiting_release = False
                else:
                    self._stable_count += 1

                ready = self._stable_count >= STABILITY_FRAMES
                if ready and not self._awaiting_release:
                    self.validated_conf.put(float(confidence))
                    self.result_queue.put(prediction)
                    self._awaiting_release = True

                progress = min(self._stable_count, STABILITY_FRAMES)
                cv2.putText(
                    img, f"maintien: {progress}/{STABILITY_FRAMES}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2,
                )
            else:
                self._last_label = None
                self._stable_count = 0
                self._awaiting_release = False

        elif landmarks_list and self.model is None:
            cv2.putText(
                img, "Modele non trouve", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2,
            )
        else:
            self._last_label = None
            self._stable_count = 0
            self._awaiting_release = False
            self.current_label = None
            self.current_conf = 0.0

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# ==========================================================================
# ÉTAT DE SESSION ET ACTIONS (boutons)
# ==========================================================================
def _init_state() -> None:
    if "confirmed_text" not in st.session_state:
        st.session_state.confirmed_text = []
    if "mode" not in st.session_state:
        st.session_state.mode = MODE_ALPHABET
    if "paused" not in st.session_state:
        st.session_state.paused = False
    if "proc_retries" not in st.session_state:
        st.session_state.proc_retries = 0
    if "history_log" not in st.session_state:
        st.session_state.history_log = []
    if "page" not in st.session_state:
        st.session_state.page = PAGE_RECO


def _goto(page: str) -> None:
    st.session_state.page = page


def _set_mode(mode: str) -> None:
    st.session_state.mode = mode


def _toggle_pause() -> None:
    st.session_state.paused = not st.session_state.paused


def _remove_last() -> None:
    if st.session_state.confirmed_text:
        st.session_state.confirmed_text.pop()


def _clear_all() -> None:
    st.session_state.confirmed_text = []


def _new_detection(proc) -> None:
    if proc is not None:
        proc.reset_detection()


def _capture(proc) -> None:
    """Ajoute immédiatement le signe actuellement détecté (si valide)."""
    if proc is None or st.session_state.paused:
        return
    label, conf = proc.current_label, proc.current_conf
    if label and conf >= CONF_THRESHOLD and mode_accepts(label, st.session_state.mode):
        add_recognition(label, conf)
        st.toast(f"« {label} » ajouté")


def _drain_queue(proc) -> None:
    """Récupère les signes validés par le processeur et les ajoute au texte."""
    if proc is None:
        return
    while True:
        try:
            symbol = proc.result_queue.get_nowait()
        except queue.Empty:
            break
        try:
            conf = proc.validated_conf.get_nowait()
        except queue.Empty:
            conf = proc.current_conf
        if st.session_state.paused:
            continue
        if mode_accepts(symbol, st.session_state.mode):
            add_recognition(symbol, conf)


# ==========================================================================
# PANNEAU DE DROITE (fragment : se rafraîchit seul, la webcam n'est pas touchée)
# ==========================================================================
@st.fragment(run_every=0.5)
def live_panel(proc) -> None:
    _drain_queue(proc)

    label = proc.current_label if proc is not None else None
    conf = proc.current_conf if proc is not None else 0.0
    view = detection_view(
        label, conf, st.session_state.paused, st.session_state.mode, CONF_THRESHOLD
    )

    with st.container(key="detect_card"):
        st.markdown(theme.card_title("target", "Signe détecté"), unsafe_allow_html=True)
        st.markdown(theme.detection_html(view), unsafe_allow_html=True)

    history = st.session_state.confirmed_text
    with st.container(key="text_card"):
        st.markdown(theme.card_title("file", "Texte reconnu"), unsafe_allow_html=True)
        st.markdown(theme.text_html(" ".join(history)), unsafe_allow_html=True)
        st.markdown(theme.recent_html(history[-RECENT_COUNT:]), unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1.25, 1, 1.35])
        with c1:
            st.button("Supprimer dernier", key="btn_last", on_click=_remove_last)
        with c2:
            st.button("Effacer", key="btn_clear", on_click=_clear_all)
        with c3:
            st.button(
                "Nouvelle détection", key="btn_new",
                on_click=_new_detection, args=(proc,),
            )


# ==========================================================================
# PAGE « RECONNAISSANCE » (mise en page inchangée, simplement encapsulée)
# ==========================================================================
def render_recognition() -> None:
    head_left, head_right = st.columns([5, 1.4])
    with head_left:
        st.markdown(theme.header_html(), unsafe_allow_html=True)
    with head_right:
        status_slot = st.empty()

    col_cam, col_info = st.columns([1.35, 1], gap="large")

    with col_cam:
        with st.container(key="cam_card"):
            ctx = webrtc_streamer(
                key="sign-recognition",
                video_processor_factory=SignProcessor,
                media_stream_constraints={"video": True, "audio": False},
            )
            playing = bool(ctx.state.playing)
            proc = ctx.video_processor if playing else None

            st.markdown(theme.chips_html(playing), unsafe_allow_html=True)

            b1, b2, b3 = st.columns([1, 1.5, 0.45])
            with b1:
                st.button("📷 Capture", key="btn_capture", on_click=_capture, args=(proc,))
            with b2:
                st.button(
                    "Reprendre la détection" if st.session_state.paused else "Arrêter la détection",
                    key="btn_pause",
                    on_click=_toggle_pause,
                )
            with b3:
                with st.popover("⚙"):
                    st.markdown("**Paramètres de détection**")
                    st.caption(f"Seuil de confiance : {CONF_THRESHOLD:.0%}")
                    st.caption(f"Maintien requis : {STABILITY_FRAMES} images")
                    st.caption("Modèle : Random Forest sur landmarks MediaPipe")

        with st.container(key="mode_card"):
            st.markdown(
                theme.card_title(
                    "target", "Mode de reconnaissance",
                    "Choisissez le type de signe à reconnaître.",
                ),
                unsafe_allow_html=True,
            )
            m1, m2 = st.columns(2)
            with m1:
                st.button("A · Alphabet", key="mode_alpha", on_click=_set_mode, args=(MODE_ALPHABET,))
            with m2:
                st.button("✋ Signes courants", key="mode_words", on_click=_set_mode, args=(MODE_WORDS,))

    with col_info:
        live_panel(proc)

    status_slot.markdown(theme.status_html(playing), unsafe_allow_html=True)
    st.markdown(theme.footer_html(), unsafe_allow_html=True)

    # Le processeur n'existe qu'un instant après le démarrage du flux : on
    # relance brièvement la page jusqu'à ce qu'il soit disponible (borné).
    if playing and proc is None:
        if st.session_state.proc_retries < MAX_PROC_RETRIES:
            st.session_state.proc_retries += 1
            time.sleep(0.4)
            st.rerun()
    else:
        st.session_state.proc_retries = 0


# ==========================================================================
# PAGES PAS ENCORE DISPONIBLES (étapes suivantes)
# ==========================================================================
def render_placeholder(icon_name: str, title: str) -> None:
    st.markdown(
        theme.page_header_html(icon_name, title, "Cette section arrive prochainement."),
        unsafe_allow_html=True,
    )
    with st.container(key="card_placeholder"):
        st.markdown(theme.note_html("Bientôt disponible."), unsafe_allow_html=True)


# ==========================================================================
# CONFIGURATION, SIDEBAR ET ROUTAGE
# ==========================================================================
st.set_page_config(
    page_title="Heri Kwetu Sign",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded",
)
_init_state()

st.markdown(theme.CSS, unsafe_allow_html=True)
st.markdown(
    theme.dynamic_css(
        "mode_alpha" if st.session_state.mode == MODE_ALPHABET else "mode_words",
        st.session_state.paused,
    ),
    unsafe_allow_html=True,
)
st.markdown(theme.nav_css(NAV_ITEMS, st.session_state.page), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(theme.sidebar_brand_html(), unsafe_allow_html=True)
    for _key, _label, _icon in NAV_ITEMS:
        st.button(_label, key=f"nav_{_key}", on_click=_goto, args=(_key,))
    st.markdown(theme.sidebar_footer_html(), unsafe_allow_html=True)

_page = st.session_state.page
if _page == PAGE_SIGNS:
    signs_view.render()
elif _page == PAGE_HISTORY:
    history_view.render()
elif _page == PAGE_SETTINGS:
    render_placeholder("sliders", "Paramètres")
else:
    render_recognition()
