"""Logique d'affichage pure, sans dépendance à Streamlit.

Isolée de l'interface pour être testable : décide quoi afficher
(libellé, confiance, badge) à partir de l'état réel de la détection.
Aucune de ces fonctions ne modifie la reconnaissance elle-même.
"""

MODE_ALPHABET = "alphabet"
MODE_WORDS = "mots"

CATEGORY_LETTER = "Alphabet"
CATEGORY_WORD = "Signe courant"

PAGE_RECO = "reconnaissance"
PAGE_HISTORY = "historique"
PAGE_SIGNS = "signes"
PAGE_SETTINGS = "parametres"

# (clé de page, libellé, icône) — ordre d'affichage dans la sidebar
NAV_ITEMS = [
    (PAGE_RECO, "Reconnaissance", "camera"),
    (PAGE_HISTORY, "Historique", "clock"),
    (PAGE_SIGNS, "Signes", "book"),
    (PAGE_SETTINGS, "Paramètres", "sliders"),
]

# Limites déjà constatées lors de l'évaluation du modèle (cf. docs/resultats_v2_alphabet.md)
KNOWN_LIMITS = {
    "J": "Signe dynamique (rotation) : reconnaissance peu fiable en mode statique",
}


def is_letter(label: str) -> bool:
    """Une lettre de l'alphabet est un label d'un seul caractère."""
    return len(label) == 1


def mode_accepts(label: str, mode: str) -> bool:
    """Le mode sélectionné filtre ce qui est ajouté au texte.

    Alphabet -> lettres uniquement ; Signes courants -> mots uniquement.
    La détection tourne identique en arrière-plan, seul l'ajout est filtré.
    """
    if mode == MODE_ALPHABET:
        return is_letter(label)
    if mode == MODE_WORDS:
        return not is_letter(label)
    return True


def detection_view(label, conf, paused, mode, threshold):
    """Décrit l'état à afficher dans la carte « Signe détecté ».

    Renvoie un dict : word, conf_pct (0-100), kind, message.
    kind : idle | ok | low | wrong_mode | paused
    """
    if paused:
        return {"word": label or "—", "conf_pct": (conf or 0.0) * 100,
                "kind": "paused", "message": "Détection en pause"}

    if not label:
        return {"word": "—", "conf_pct": 0.0, "kind": "idle",
                "message": "En attente d'un signe…"}

    conf_pct = conf * 100
    if conf < threshold:
        return {"word": label, "conf_pct": conf_pct, "kind": "low",
                "message": "Confiance insuffisante, maintenez le signe"}

    if not mode_accepts(label, mode):
        wanted = "Alphabet" if mode == MODE_ALPHABET else "Signes courants"
        return {"word": label, "conf_pct": conf_pct, "kind": "wrong_mode",
                "message": f"Hors du mode « {wanted} »"}

    return {"word": label, "conf_pct": conf_pct, "kind": "ok",
            "message": "Signe correctement reconnu"}


def category_of(label: str) -> str:
    """Catégorie d'affichage d'un label reconnu."""
    return CATEGORY_LETTER if is_letter(label) else CATEGORY_WORD


def split_vocabulary(classes) -> tuple:
    """Sépare les classes du modèle en (lettres, signes courants), triées."""
    labels = [str(c) for c in classes]
    letters = sorted(c for c in labels if is_letter(c))
    words = sorted(c for c in labels if not is_letter(c))
    return letters, words


def history_stats(entries: list) -> dict:
    """Statistiques simples du journal : total, lettres, signes courants, confiance moyenne."""
    total = len(entries)
    letters = sum(1 for e in entries if e["category"] == CATEGORY_LETTER)
    avg = (sum(e["conf"] for e in entries) / total * 100) if total else 0.0
    return {"total": total, "letters": letters, "words": total - letters, "avg_conf": avg}


def history_to_csv(entries: list) -> str:
    """Export CSV du journal (BOM UTF-8 pour une ouverture correcte dans Excel)."""
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "heure", "signe", "categorie", "confiance_pct"])
    for e in entries:
        date, _, hour = e["ts"].partition("T")
        writer.writerow([date, hour, e["label"], e["category"], f"{e['conf'] * 100:.1f}"])
    return "\ufeff" + buf.getvalue()
