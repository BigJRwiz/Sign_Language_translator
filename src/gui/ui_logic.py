"""Logique d'affichage pure, sans dépendance à Streamlit.

Isolée de l'interface pour être testable : décide quoi afficher
(libellé, confiance, badge) à partir de l'état réel de la détection.
Aucune de ces fonctions ne modifie la reconnaissance elle-même.
"""

MODE_ALPHABET = "alphabet"
MODE_WORDS = "mots"


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
