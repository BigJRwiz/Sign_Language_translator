"""Extraction de features à partir des landmarks MediaPipe.

Une seule fonction, utilisée à la fois par l'entraînement (train.py) et
par l'inférence en direct (gui/app.py), pour garantir que les deux
calculent strictement la même chose. Toute divergence entre ces deux
usages rend un modèle inutilisable en direct même s'il est bon à
l'évaluation -- c'est la cause du bug rencontré précédemment.

Features = coordonnées brutes (x, y, z) des 21 points, telles que
renvoyées par MediaPipe. Volontairement simple : pas de normalisation
(centrage/mise à l'échelle), cette piste d'amélioration est documentée
comme perspective future mais n'est plus modifiée avant la démo.
"""

NUM_LANDMARKS = 21


def landmarks_object_to_features(hand_landmarks) -> list:
    """Depuis un objet landmarks MediaPipe (21 points) -> liste de 63 floats."""
    features = []
    for pt in hand_landmarks:
        features += [pt.x, pt.y, pt.z]
    return features
