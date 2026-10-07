"""Session de collecte automatisée pour les 26 lettres de l'alphabet LSF (V2).

Touches, pendant la collecte d'une lettre :
  's' : sauvegarder un échantillon (si une main est détectée)
  'r' : annuler le dernier échantillon sauvegardé pour cette lettre
  'n' : passer à la lettre suivante avant d'avoir atteint le quota
  'q' : quitter la session (les lettres déjà complétées restent enregistrées)

Usage :
    python -m src.recognition.collect_alphabet_session --signer signeur1
"""

import argparse
import csv
import os

import cv2

from src.detection.hand_detector import HandDetector

OUTPUT_CSV = "data/raw/landmarks_dataset.csv"
NUM_LANDMARKS = 21
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
WINDOW_NAME = "Collecte alphabet LSF"


def _ensure_csv_header() -> None:
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    if not os.path.exists(OUTPUT_CSV):
        header = ["label", "signer"]
        for i in range(NUM_LANDMARKS):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        with open(OUTPUT_CSV, "w", newline="") as f:
            csv.writer(f).writerow(header)


def _landmarks_to_row(label: str, signer: str, hand_landmarks) -> list:
    row = [label, signer]
    for pt in hand_landmarks:
        row += [pt.x, pt.y, pt.z]
    return row


def _draw_overlay(frame, letter: str, saved: int, target: int) -> None:
    lines = [
        f"Lettre : {letter}   ({saved}/{target} echantillons)",
        "[s] sauver  [r] annuler dernier  [n] lettre suivante  [q] quitter",
    ]
    y = 30
    for line in lines:
        cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y += 35


def _flush_rows(rows: list) -> None:
    if not rows:
        return
    with open(OUTPUT_CSV, "a", newline="") as f:
        csv.writer(f).writerows(rows)


def run_session(signer: str, samples_per_letter: int = 30, camera_index: int = 0) -> None:
    _ensure_csv_header()

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Impossible d'ouvrir la webcam (index {camera_index}).")

    detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    quit_session = False

    for letter in ALPHABET:
        if quit_session:
            break

        letter_rows = []

        while len(letter_rows) < samples_per_letter:
            ret, frame = cap.read()
            if not ret:
                break

            frame, landmarks_list = detector.find_hands(frame)
            _draw_overlay(frame, letter, len(letter_rows), samples_per_letter)
            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                quit_session = True
                break
            if key == ord("n"):
                break
            if key == ord("s"):
                if landmarks_list:
                    letter_rows.append(_landmarks_to_row(letter, signer, landmarks_list[0]))
                else:
                    print(f"[{letter}] Aucune main détectée, échantillon ignoré.")
            if key == ord("r") and letter_rows:
                letter_rows.pop()
                print(f"[{letter}] Dernier échantillon annulé ({len(letter_rows)} restants).")

        _flush_rows(letter_rows)
        print(f"Lettre '{letter}' terminée : {len(letter_rows)} échantillons enregistrés.")

    detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Session de collecte terminée.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collecte automatisée de l'alphabet LSF.")
    parser.add_argument("--signer", required=True, help="Identifiant du signeur (ex: signeur1)")
    parser.add_argument("--samples-per-letter", type=int, default=30)
    parser.add_argument("--camera-index", type=int, default=0)
    args = parser.parse_args()
    run_session(args.signer, args.samples_per_letter, args.camera_index)
