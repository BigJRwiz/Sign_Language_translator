"""Extraction de features normalisées à partir des landmarks MediaPipe.

Rend la reconnaissance invariante à la position de la main dans l'image
et à sa distance à la caméra : centrage sur le poignet (landmark 0),
mise à l'échelle par la distance poignet -> base du majeur (landmark 9),
repère stable quelle que soit la forme du signe réalisé.
"""

import numpy as np

NUM_LANDMARKS = 21
WRIST = 0
MIDDLE_MCP = 9


def normalize_landmarks(flat_coords) -> np.ndarray:
    """flat_coords : 63 valeurs (21 x,y,z) brutes -> 63 valeurs normalisées."""
    points = np.array(flat_coords, dtype=float).reshape(NUM_LANDMARKS, 3)
    centered = points - points[WRIST]

    scale_ref = np.linalg.norm(centered[MIDDLE_MCP])
    if scale_ref < 1e-6:
        scale_ref = 1.0

    return (centered / scale_ref).flatten()


def landmarks_object_to_features(hand_landmarks) -> np.ndarray:
    """Depuis un objet landmarks MediaPipe (format HandDetector) -> features normalisées."""
    flat = []
    for pt in hand_landmarks:
        flat += [pt.x, pt.y, pt.z]
    return normalize_landmarks(flat)
