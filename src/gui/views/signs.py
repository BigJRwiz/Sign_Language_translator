"""Page « Signes » : bibliothèque du vocabulaire pris en charge.

Lecture seule : cette page lit les classes du modèle déjà entraîné et le
nombre d'échantillons du jeu de données. Elle ne modifie ni le modèle,
ni la reconnaissance.
"""

import csv
import os
import string

import joblib
import streamlit as st

from src.gui import theme
from src.gui.ui_logic import KNOWN_LIMITS, split_vocabulary

MODEL_PATH = "data/models/alphabet_classifier.joblib"
DATASET_PATH = "data/raw/landmarks_dataset.csv"


def _mtime(path: str) -> float:
    return os.path.getmtime(path) if os.path.exists(path) else 0.0


@st.cache_data(show_spinner=False)
def _load_vocabulary(model_mtime: float, dataset_mtime: float):
    """Renvoie (classes, compteurs d'échantillons) ; mis en cache tant que
    les fichiers ne changent pas (les mtime servent de clé de cache)."""
    classes = []
    if os.path.exists(MODEL_PATH):
        classes = [str(c) for c in joblib.load(MODEL_PATH).classes_]

    counts = {}
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, newline="") as f:
            for row in csv.DictReader(f):
                counts[row["label"]] = counts.get(row["label"], 0) + 1
    return classes, counts


def _tile(label: str, counts: dict, learned: set) -> dict:
    return {
        "label": label,
        "count": counts.get(label, 0),
        "available": label in learned,
        "note": KNOWN_LIMITS.get(label, ""),
    }


def render() -> None:
    st.markdown(
        theme.page_header_html(
            "book", "Signes",
            "Vocabulaire actuellement reconnu par le système.",
        ),
        unsafe_allow_html=True,
    )

    classes, counts = _load_vocabulary(_mtime(MODEL_PATH), _mtime(DATASET_PATH))
    if not classes:
        with st.container(key="card_signs_empty"):
            st.markdown(
                theme.note_html(
                    "Aucun modèle entraîné trouvé. Lance d'abord : "
                    "python -m src.recognition.train"
                ),
                unsafe_allow_html=True,
            )
        return

    letters, words = split_vocabulary(classes)
    learned = set(classes)

    st.markdown(
        theme.stat_cards_html([
            (len(letters), "lettres reconnues"),
            (len(words), "signes courants"),
            (sum(counts.get(c, 0) for c in classes), "échantillons d'entraînement"),
        ]),
        unsafe_allow_html=True,
    )

    with st.container(key="card_signs_alpha"):
        st.markdown(theme.card_title("hand", "Alphabet A–Z"), unsafe_allow_html=True)
        tiles = [_tile(c, counts, learned) for c in string.ascii_uppercase]
        st.markdown(theme.signs_grid_html(tiles), unsafe_allow_html=True)
        st.markdown(
            theme.legend_html(
                "⚠ Signe dynamique (mouvement) : reconnaissance moins fiable. "
                "Les lettres grisées ne sont pas encore apprises."
            ),
            unsafe_allow_html=True,
        )

    with st.container(key="card_signs_words"):
        st.markdown(theme.card_title("book", "Signes courants"), unsafe_allow_html=True)
        if words:
            tiles = [_tile(w, counts, learned) for w in words]
            st.markdown(theme.signs_grid_html(tiles, word=True), unsafe_allow_html=True)
        else:
            st.markdown(
                theme.note_html(
                    "Aucun signe courant dans le modèle actuel. Collecte-en avec "
                    "collect_words_session puis réentraîne le modèle."
                ),
                unsafe_allow_html=True,
            )
