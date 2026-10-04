"""Outil de collecte de landmarks pour l'entraînement (V2).

Capture les 21 landmarks (x, y, z) de la main détectée et les enregistre
dans un CSV avec leur étiquette. Réutilisable pour les données placeholder
et, plus tard, pour la collecte réelle au Centre Heri Kwetu.

Usage : python src/recognition/collect_landmarks.py --label A
Touches : 's' pour enregistrer un échantillon, 'q' pour quitter.
"""

import argparse
import csv
import os
import time

import cv2

from src.detection.hand_detector import HandDetector

OUTPUT_CSV = "data/raw/landmarks_dataset.csv"
NUM_LANDMARKS = 21


def _ensure_csv_header() -> None:
    """Crée le CSV avec son en-tête s'il n'existe pas encore."""
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    if not os.path.exists(OUTPUT_CSV):
        header = ["label"]
        for i in range(NUM_LANDMARKS):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        with open(OUTPUT_CSV, "w", newline="") as f:
            csv.writer(f).writerow(header)


def _landmarks_to_row(label: str, hand_landmarks) -> list:
    """Aplati les 21 points (x, y, z) en une seule ligne CSV."""
    row = [label]
    for pt in hand_landmarks:
        row += [pt.x, pt.y, pt.z]
    return row


def collect(label: str, camera_index: int = 0) -> None:
    _ensure_csv_header()

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Impossible d'ouvrir la webcam (index {camera_index}).")

    detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
    window_name = f"Collecte - lettre {label} (s=sauver, q=quitter)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, landmarks_list = detector.find_hands(frame)
        cv2.putText(
            frame, f"Echantillons sauves : {saved_count}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
        )
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s") and landmarks_list:
            row = _landmarks_to_row(label, landmarks_list[0])
            with open(OUTPUT_CSV, "a", newline="") as f:
                csv.writer(f).writerow(row)
            saved_count += 1
            print(f"Échantillon {saved_count} enregistré pour '{label}'.")
        elif key == ord("s") and not landmarks_list:
            print("Aucune main détectée, échantillon ignoré.")

    detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print(f"Terminé : {saved_count} échantillons enregistrés pour '{label}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collecte de landmarks pour une lettre.")
    parser.add_argument("--label", required=True, help="Étiquette à enregistrer (ex: A)")
    args = parser.parse_args()
    collect(args.label.upper())
