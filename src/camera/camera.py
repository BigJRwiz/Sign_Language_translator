"""Module de capture vidéo + détection de main (V1)."""

import cv2

from src.detection.hand_detector import HandDetector

WINDOW_NAME = "Détection de la main - V1"


def _window_was_closed() -> bool:
    """Renvoie True si la fenêtre a été fermée par l'utilisateur (icône X)."""
    try:
        return cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1
    except cv2.error:
        return True


def run_camera_test(camera_index: int = 0) -> None:
    """Ouvre la webcam, détecte la main via MediaPipe, affiche les landmarks.

    Arrêt possible par la touche 'q' ou en fermant la fenêtre (icône X).
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Impossible d'ouvrir la webcam (index {camera_index}).")

    detector = HandDetector(max_num_hands=1, min_detection_confidence=0.7)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, landmarks_list = detector.find_hands(frame)

        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if _window_was_closed():
            break

    detector.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_camera_test()
