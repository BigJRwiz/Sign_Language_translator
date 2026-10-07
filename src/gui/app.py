"""Interface Streamlit — Signes -> Texte (lettres + mots).

Flux vidéo en direct (streamlit-webrtc) ; le texte reconnu s'accumule
en dessous au fur et à mesure. Un signe doit être maintenu stable un
court instant avant d'être ajouté, et il faut changer de signe (ou
retirer la main) avant qu'il puisse être réaccepté -- évite les
répétitions parasites comme "AMORRRRRRR".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import queue

import av
import cv2
import joblib
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from src.detection.hand_detector import HandDetector
from src.recognition.features import landmarks_object_to_features

MODEL_PATH = "data/models/alphabet_classifier.joblib"
CONF_THRESHOLD = 0.6
STABILITY_FRAMES = 10


class SignProcessor(VideoProcessorBase):
    """Traite chaque frame du flux WebRTC : détection + prédiction stabilisée."""

    def __init__(self) -> None:
        self.detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
        try:
            self.model = joblib.load(MODEL_PATH)
        except FileNotFoundError:
            self.model = None

        self.result_queue: queue.Queue = queue.Queue()
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

        return av.VideoFrame.from_ndarray(img, format="bgr24")


st.set_page_config(page_title="Signes -> Texte", layout="centered")
st.title("Centre Heri Kwetu — Reconnaissance de signes")
st.caption(
    "Prototype V1 — alphabet LSF et signes courants. Maintiens un signe "
    "stable un court instant pour qu'il soit ajouté au texte ci-dessous."
)

ctx = webrtc_streamer(
    key="sign-recognition",
    video_processor_factory=SignProcessor,
    media_stream_constraints={"video": True, "audio": False},
)

if "confirmed_text" not in st.session_state:
    st.session_state.confirmed_text = []

col1, col2, col3 = st.columns([3, 1, 1])
with col2:
    if st.button("Supprimer dernier"):
        if st.session_state.confirmed_text:
            st.session_state.confirmed_text.pop()
with col3:
    if st.button("Effacer tout"):
        st.session_state.confirmed_text = []

phrase_placeholder = st.empty()
displayed = " ".join(st.session_state.confirmed_text) or "…"
phrase_placeholder.markdown(f"### Texte reconnu :\n\n**{displayed}**")

if ctx.state.playing and ctx.video_processor:
    try:
        symbol = ctx.video_processor.result_queue.get(timeout=1.0)
        st.session_state.confirmed_text.append(symbol)
        st.rerun()
    except queue.Empty:
        st.rerun()
elif not ctx.state.playing:
    st.info("Clique sur START puis réalise un signe devant la caméra.")
