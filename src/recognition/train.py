"""Entraînement et évaluation du classifieur (alphabet + mots, V2/V3).

Features : coordonnées brutes des landmarks (cf. recognition/features.py).
Augmentation appliquée UNIQUEMENT sur le jeu d'entraînement (rotation,
échelle, bruit, miroir) pour limiter le biais du signeur unique.
Séparation train/test par SIGNEUR quand plusieurs signeurs existent,
sinon découpage aléatoire avec avertissement explicite.
"""

import csv
import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

from src.recognition.augment import augment_sample, mirror_sample

DATA_CSV = "data/raw/landmarks_dataset.csv"
MODEL_PATH = "data/models/alphabet_classifier.joblib"


def load_dataset(path: str):
    """Charge le CSV collecté. Renvoie (X, y, signers) en numpy arrays."""
    labels, signers, features = [], [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels.append(row["label"])
            signers.append(row["signer"])
            coords = [float(row[k]) for k in row if k not in ("label", "signer")]
            features.append(coords)
    return np.array(features), np.array(labels), np.array(signers)


def _split(X, y, signers, test_signer: str | None):
    unique_signers = sorted(set(signers))

    if len(unique_signers) < 2:
        print(
            "ATTENTION : un seul signeur présent dans le dataset "
            f"({unique_signers[0]}). Évaluation sur un découpage ALÉATOIRE, "
            "pas par signeur indépendant -- le score ci-dessous est "
            "optimiste et ne garantit pas la généralisation à une autre "
            "personne. À refaire dès qu'un 2e signeur est collecté."
        )
        from sklearn.model_selection import train_test_split

        return train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    test_signer = test_signer or unique_signers[-1]
    test_mask = signers == test_signer
    print(f"Signeurs disponibles : {unique_signers} -- test = {test_signer!r}")
    return X[~test_mask], X[test_mask], y[~test_mask], y[test_mask]


def _augment_training_set(X_train, y_train):
    rng = np.random.default_rng(42)
    X_aug, y_aug = [], []
    for features, label in zip(X_train, y_train):
        for _ in range(4):
            X_aug.append(augment_sample(features, rng))
            y_aug.append(label)
        X_aug.append(mirror_sample(features))
        y_aug.append(label)

    X_out = np.vstack([X_train, np.array(X_aug)])
    y_out = np.concatenate([y_train, np.array(y_aug)])
    print(f"Jeu d'entraînement après augmentation : {len(X_out)} échantillons.")
    return X_out, y_out


def train_and_evaluate(test_signer: str | None = None) -> None:
    if not os.path.exists(DATA_CSV):
        raise FileNotFoundError(
            f"Dataset introuvable : {DATA_CSV}. Lance d'abord une session "
            "de collecte (collect_alphabet_session.py et/ou "
            "collect_words_session.py)."
        )

    X, y, signers = load_dataset(DATA_CSV)
    print(f"Dataset chargé : {len(X)} échantillons, {len(set(y))} classes.")

    X_train, X_test, y_train, y_test = _split(X, y, signers, test_signer)
    X_train, y_train = _augment_training_set(X_train, y_train)

    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print("\n--- Rapport de classification ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    labels_sorted = sorted(set(y))
    print("--- Matrice de confusion ---")
    print("Classes :", labels_sorted)
    print(confusion_matrix(y_test, y_pred, labels=labels_sorted))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"\nModèle sauvegardé : {MODEL_PATH}")


if __name__ == "__main__":
    train_and_evaluate()
