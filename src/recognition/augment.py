"""Augmentation de landmarks (V2).

Ne remplace PAS un deuxième signeur réel -- réduit seulement le risque
de surapprentissage sur les conditions exactes de capture d'un signeur
unique. À documenter comme mesure d'atténuation, pas comme solution
définitive, tant qu'un second signeur n'est pas collecté.
"""

import numpy as np

NUM_LANDMARKS = 21


def _reshape(row):
    return np.array(row, dtype=float).reshape(NUM_LANDMARKS, 3)


def _flatten(points):
    return points.flatten().tolist()


def augment_sample(row, rng: np.random.Generator):
    """Génère une variante légèrement modifiée d'un échantillon."""
    points = _reshape(row)
    wrist = points[0].copy()
    centered = points - wrist

    # Rotation légère dans le plan x,y (simule l'angle de la main), +/-15°
    angle = rng.uniform(-15, 15) * np.pi / 180
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    rot = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    centered[:, :2] = centered[:, :2] @ rot.T

    # Variation d'échelle (simule la distance à la caméra), +/-10%
    centered *= rng.uniform(0.9, 1.1)

    # Bruit léger (simule l'imprécision de détection)
    centered += rng.normal(0, 0.01, size=centered.shape)

    return _flatten(centered + wrist)


def mirror_sample(row):
    """Simule la même forme réalisée de l'autre main."""
    points = _reshape(row)
    points[:, 0] = 1.0 - points[:, 0]
    return _flatten(points)
