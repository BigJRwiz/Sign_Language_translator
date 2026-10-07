"""Interface Streamlit — V6.

Page Signes -> Texte : flux vidéo en direct (streamlit-webrtc) avec
détection de main et prédiction de lettre en temps réel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import av
import cv2
import joblib
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from src.detection.hand_detector import HandDetector

MODEL_PATH = "data/models/alphabet_classifier.joblib"


class SignProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        self.detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
        try:
            self.model = joblib.load(MODEL_PATH)
        except FileNotFoundError:
            self.model = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img, landmarks_list = self.detector.find_hands(img)

        if landmarks_list and self.model is not None:
            hand = landmarks_list[0]
            features = []
            for pt in hand:
                features += [pt.x, pt.y, pt.z]

            prediction = self.model.predict([features])[0]
            confidence = max(self.model.predict_proba([features])[0])

            text = f"{prediction} ({confidence:.0%})"
            cv2.putText(img, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        elif landmarks_list and self.model is None:
            cv2.putText(img, "Modele non trouve", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


st.set_page_config(page_title="Signes -> Texte", layout="centered")
st.title("Reconnaissance de l'alphabet LSF")
st.caption("Prototype V2 -- modèle entraîné sur un seul signeur, résultats préliminaires.")

webrtc_streamer(
    key="sign-recognition",
    video_processor_factory=SignProcessor,
    media_stream_constraints={"video": True, "audio": False},
)
"""Interface Streamlit — Signes -> Texte (lettres + mots)."""

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

MODEL_PATH = "data/models/alphabet_classifier.joblib"
CONF_THRESHOLD = 0.6
STABILITY_FRAMES = 10
COOLDOWN_FRAMES = 20


class SignProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        self.detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
        try:
            self.model = joblib.load(MODEL_PATH)
        except FileNotFoundError:
            self.model = None

        self.result_queue = queue.Queue()
        self._last_label = None
        self._stable_count = 0
        self._cooldown = 0

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img, landmarks_list = self.detector.find_hands(img)

        if self._cooldown > 0:
            self._cooldown -= 1

        if landmarks_list and self.model is not None:
            hand = landmarks_list[0]
            features = []
            for pt in hand:
                features += [pt.x, pt.y, pt.z]

            prediction = self.model.predict([features])[0]
            confidence = max(self.model.predict_proba([features])[0])

            cv2.putText(img, f"{prediction} ({confidence:.0%})", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3)

            if confidence >= CONF_THRESHOLD:
                if prediction == self._last_label:
                    self._stable_count += 1
                else:
                    self._last_label = prediction
                    self._stable_count = 1

                if self._stable_count >= STABILITY_FRAMES and self._cooldown == 0:
                    self.result_queue.put(prediction)
                    self._cooldown = COOLDOWN_FRAMES
                    self._stable_count = 0

                progress = min(self._stable_count, STABILITY_FRAMES)
                cv2.putText(img, f"maintien: {progress}/{STABILITY_FRAMES}", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
            else:
                self._last_label = None
                self._stable_count = 0
        elif landmarks_list and self.model is None:
            cv2.putText(img, "Modele non trouve", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        else:
            self._last_label = None
            self._stable_count = 0

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

if ctx.state.playing:
    phrase_placeholder = st.empty()
    confirmed = []
    while ctx.state.playing:
        if ctx.video_processor:
            try:
                symbol = ctx.video_processor.result_queue.get(timeout=1.0)
                confirmed.append(symbol)
                phrase_placeholder.markdown(f"### Texte reconnu :\n\n**{' '.join(confirmed)}**")
            except queue.Empty:
                continue
else:
    st.info("Clique sur START puis réalise un signe devant la caméra.")
