"""Module de capture vidéo (V0) : accès webcam via OpenCV."""

import cv2

WINDOW_NAME = "Test webcam - V0"


def _window_was_closed() -> bool:
    """Renvoie True si la fenêtre a été fermée par l'utilisateur (icône X)."""
    try:
        return cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1
    except cv2.error:
        return True


def run_camera_test(camera_index: int = 0) -> None:
    """Ouvre la webcam et affiche le flux. Arrêt par 'q' ou fermeture de fenêtre."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Impossible d'ouvrir la webcam (index {camera_index}).")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if _window_was_closed():
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_camera_test()
