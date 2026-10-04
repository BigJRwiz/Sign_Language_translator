"""Traduction Texte -> Signes (V5 du cahier des charges).

Recherche chaque mot d'un message dans un dictionnaire de concepts
validés, plutôt que de tenter une traduction mot-à-mot supposée
parfaite (cf. cahier des charges, section 18). Un mot absent du
dictionnaire est explicitement signalé comme non reconnu, jamais
inventé ou approximé (cf. section 23, gestion des signes inconnus).
"""

import json
import os
import re
import unicodedata

DICTIONARY_PATH = "data/config/dictionnaire_signes.json"


def _load_dictionary(path: str = DICTIONARY_PATH) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dictionnaire de signes introuvable : {path}. "
            "Vérifie qu'il a bien été créé avant d'utiliser ce module."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _normalize(word: str) -> str:
    """Minuscules, sans accents, sans ponctuation : pour une recherche robuste."""
    word = word.lower().strip()
    word = unicodedata.normalize("NFKD", word)
    word = "".join(c for c in word if not unicodedata.combining(c))
    word = re.sub(r"[^\w\s]", "", word)
    return word


def _tokenize(text: str) -> list:
    return [w for w in text.split() if w.strip()]


class TextToSignTranslator:
    """Traduit un message texte en une suite de signes connus."""

    def __init__(self, dictionary_path: str = DICTIONARY_PATH):
        self.dictionary = _load_dictionary(dictionary_path)

    def translate(self, text: str) -> list:
        """Renvoie une liste de résultats, un par mot du message.

        Chaque résultat est un dict :
            {"word": str, "recognized": bool, "label_fr": str|None, "asset": str|None}
        Un mot non reconnu a recognized=False et les autres champs à None
        -- jamais de signe approximé ou inventé.
        """
        results = []
        for raw_word in _tokenize(text):
            key = _normalize(raw_word)
            entry = self.dictionary.get(key)

            if entry is None:
                results.append({
                    "word": raw_word,
                    "recognized": False,
                    "label_fr": None,
                    "asset": None,
                })
            else:
                asset_exists = os.path.exists(entry["asset"])
                results.append({
                    "word": raw_word,
                    "recognized": True,
                    "label_fr": entry["label_fr"],
                    "asset": entry["asset"] if asset_exists else None,
                })

        return results


if __name__ == "__main__":
    translator = TextToSignTranslator()
    message = "Bonjour, merci beaucoup"
    for result in translator.translate(message):
        if result["recognized"]:
            status = "OK" if result["asset"] else "reconnu mais image manquante"
            print(f"{result['word']!r:15} -> {result['label_fr']} ({status})")
        else:
            print(f"{result['word']!r:15} -> Signe non reconnu.")
