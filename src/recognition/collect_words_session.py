"""Session de collecte pour des mots/signes LSF (V3).

Même mécanique que collect_alphabet_session.py, mais pour une liste de
mots personnalisée plutôt que l'alphabet. Les labels mots sont stockés
en MAJUSCULES pour rester cohérents avec les labels de lettres.

Pour un signe avec mouvement (la plupart des mots en LSF), fige ta main
sur sa position la plus caractéristique au moment d'appuyer sur 's' --
limite connue du prototype statique, à documenter dans le rapport.

Usage :
    python -m src.recognition.collect_words_session --signer signeur1
"""

import argparse
import csv
import os

import cv2

from src.detection.hand_detector import HandDetector

OUTPUT_CSV = "data/raw/landmarks_dataset.csv"
NUM_LANDMARKS = 21
WORDS = ["PAPA", "MAMAN", "SOEUR", "FRERE", "SALUT"]
WINDOW_NAME = "Collecte mots LSF"


def _ensure_csv_header() -> None:
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    if not os.path.exists(OUTPUT_CSV):
        header = ["label", "signer"] + [
            f"{axis}{i}" for i in range(NUM_LANDMARKS) for axis in ("x", "y", "z")
        ]
        with open(OUTPUT_CSV, "w", newline="") as f:
            csv.writer(f).writerow(header)


def _row(label, signer, hand_landmarks):
    row = [label, signer]
    for pt in hand_landmarks:
        row += [pt.x, pt.y, pt.z]
    return row


def _overlay(frame, word, saved, target):
    cv2.putText(
        frame, f"Mot : {word}  ({saved}/{target})", (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
    )
    cv2.putText(
        frame, "[s] sauver  [n] mot suivant  [q] quitter", (10, 65),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
    )


def run(signer: str, samples_per_word: int = 30, camera_index: int = 0) -> None:
    _ensure_csv_header()
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Impossible d'ouvrir la webcam.")

    detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    quit_all = False

    for word in WORDS:
        if quit_all:
            break
        rows = []
        while len(rows) < samples_per_word:
            ret, frame = cap.read()
            if not ret:
                break
            frame, landmarks_list = detector.find_hands(frame)
            _overlay(frame, word, len(rows), samples_per_word)
            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                quit_all = True
                break
            if key == ord("n"):
                break
            if key == ord("s") and landmarks_list:
                rows.append(_row(word, signer, landmarks_list[0]))

        with open(OUTPUT_CSV, "a", newline="") as f:
            csv.writer(f).writerows(rows)
        print(f"Mot '{word}' terminé : {len(rows)} échantillons.")

    detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Session mots terminée.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--signer", required=True)
    parser.add_argument("--samples-per-word", type=int, default=30)
    parser.add_argument("--camera-index", type=int, default=0)
    args = parser.parse_args()
    run(args.signer, args.samples_per_word, args.camera_index)
