"""Détection de la main via l'API MediaPipe Tasks (V1, mediapipe >= 1.0).

Pipeline : image -> détection -> 21 landmarks -> coordonnées x, y, z.
Nécessite le modèle hand_landmarker.task téléchargé dans models/.
"""

import time

import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Connexions standard du squelette de la main (21 points), utilisées pour
# le dessin car mp.solutions.drawing_utils n'existe plus dans l'API Tasks.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # pouce
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (0, 9), (9, 10), (10, 11), (11, 12),     # majeur
    (0, 13), (13, 14), (14, 15), (15, 16),   # annulaire
    (0, 17), (17, 18), (18, 19), (19, 20),   # auriculaire
    (5, 9), (9, 13), (13, 17),               # paume
]


class HandDetector:
    """Encapsule HandLandmarker (API Tasks) pour un flux vidéo en direct."""

    def __init__(
        self,
        model_path: str = "models/hand_landmarker.task",
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.5,
    ):
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self._start_time = time.time()

    def find_hands(self, frame_bgr, draw: bool = True):
        """Détecte les mains dans une image BGR (format OpenCV).

        Renvoie (frame_annotée, liste_de_landmarks). Chaque élément de la
        liste contient 21 points normalisés (x, y, z) pour une main.
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int((time.time() - self._start_time) * 1000)

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        landmarks_list = result.hand_landmarks

        if draw:
            height, width = frame_bgr.shape[:2]
            for hand in landmarks_list:
                points = [(int(pt.x * width), int(pt.y * height)) for pt in hand]
                for x, y in points:
                    cv2.circle(frame_bgr, (x, y), 4, (0, 255, 0), -1)
                for start, end in HAND_CONNECTIONS:
                    cv2.line(frame_bgr, points[start], points[end], (255, 255, 255), 2)

        return frame_bgr, landmarks_list

    def close(self) -> None:
        self.landmarker.close()
