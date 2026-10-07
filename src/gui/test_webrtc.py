"""Test minimal de streamlit-webrtc, sans traitement (sanity check)."""

import streamlit as st
from streamlit_webrtc import webrtc_streamer

st.title("Test flux vidéo en direct")

webrtc_streamer(key="test-camera")
