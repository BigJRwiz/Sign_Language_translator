"""Entraînement et évaluation du classifieur de l'alphabet LSF (V2).

Sépare les données par SIGNEUR (pas au hasard) pour le jeu de test,
afin de vérifier que le modèle reconnaît la forme du signe et non la
main d'une personne précise (cf. cahier des charges, section 32).
"""

import csv

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

DATA_CSV = "data/raw/landmarks_dataset.csv"
MODEL_PATH = "data/models/alphabet_classifier.joblib"


def load_dataset(path: str):
    labels, signers, features = [], [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels.append(row["label"])
            signers.append(row["signer"])
            coords = [float(row[k]) for k in row if k not in ("label", "signer")]
            features.append(coords)
    return np.array(features), np.array(labels), np.array(signers)


def split_by_signer(X, y, signers, test_signer: str | None):
    """Jeu de test = un signeur entier, laissé hors de l'entraînement.

    Si test_signer est None (un seul signeur dans les données), on
    prévient explicitement : pas de vraie évaluation d'indépendance
    possible tant qu'un deuxième signeur n'a pas été collecté.
    """
    unique_signers = sorted(set(signers))
    if test_signer is None:
        test_signer = unique_signers[-1]

    test_mask = signers == test_signer
    train_mask = ~test_mask
    return X[train_mask], X[test_mask], y[train_mask], y[test_mask], unique_signers


def train_and_evaluate(test_signer: str | None = None) -> None:
    X, y, signers = load_dataset(DATA_CSV)
    unique_signers = sorted(set(signers))

    if len(unique_signers) < 2:
        print(
            "ATTENTION : un seul signeur présent dans le dataset "
            f"({unique_signers[0]}). L'évaluation ci-dessous se fait sur un "
            "découpage aléatoire, PAS par signeur indépendant — les résultats "
            "seront optimistes et ne garantissent pas la généralisation à "
            "une autre personne. À corriger dès qu'un 2e signeur est collecté."
        )
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test, unique_signers = split_by_signer(
            X, y, signers, test_signer
        )
        print(f"Signeurs disponibles : {unique_signers}")
        print(f"Jeu de test = signeur laissé hors entraînement.")

    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    print("\n--- Rapport de classification ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("--- Matrice de confusion ---")
    labels_sorted = sorted(set(y))
    cm = confusion_matrix(y_test, y_pred, labels=labels_sorted)
    print("Classes :", labels_sorted)
    print(cm)

    import os
    os.makedirs("data/models", exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"\nModèle sauvegardé : {MODEL_PATH}")


if __name__ == "__main__":
    train_and_evaluate()
