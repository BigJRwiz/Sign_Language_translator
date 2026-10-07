# Installation de ce correctif

Ce zip contient une version complète et cohérente de la partie
« Signes -> Texte » du projet. Il remplace entièrement les fichiers
correspondants dans ton dépôt existant.

## 1. Sauvegarde rapide (sécurité, 10 secondes)

Depuis la racine de ton projet (`~/Github/Sign_Language_translator`) :

```bash
git add -A
git commit -m "wip: sauvegarde avant application du correctif"
```

Même si c'est un peu cassé, ça te permet de revenir en arrière avec
`git reset --hard HEAD~1` si jamais besoin.

## 2. Copier les fichiers de ce zip dans ton projet

Dézippe ce fichier, puis copie-colle (écrase) les dossiers et fichiers
suivants dans ton dépôt, en conservant exactement cette structure :

```
main.py                                    -> racine du projet
src/camera/camera.py                       -> écrase l'existant
src/detection/hand_detector.py             -> écrase l'existant
src/recognition/features.py                -> NOUVEAU fichier
src/recognition/augment.py                 -> écrase l'existant
src/recognition/train.py                   -> écrase l'existant
src/recognition/generate_dummy_data.py     -> écrase l'existant
src/recognition/collect_alphabet_session.py -> écrase l'existant
src/recognition/collect_words_session.py   -> écrase l'existant
src/gui/app.py                             -> écrase l'existant
```

Ne touche à rien d'autre (src/translation/ reste intact, inchangé).

Si tu es à l'aise avec un gestionnaire de fichiers graphique, glisse
simplement le contenu du dossier `src/` de ce zip par-dessus le `src/`
de ton projet, en acceptant le remplacement des fichiers existants.

## 3. Réentraîner le modèle AVANT de lancer l'interface

Important : le modèle sauvegardé précédemment (`data/models/alphabet_classifier.joblib`)
correspond à l'ancien code. Il faut le régénérer avec le nouveau
`train.py`, sinon l'application et le modèle ne seront plus cohérents.

```bash
source .venv/bin/activate
python -m src.recognition.train
```

Si tu vois « ATTENTION : un seul signeur... », c'est normal, c'est le
même avertissement que d'habitude -- le modèle s'entraîne quand même.

## 4. Lancer l'interface

```bash
streamlit run src/gui/app.py
```

Clique sur START, autorise la caméra, fais une lettre ou un mot
(PAPA, MAMAN, SOEUR, FRERE, SALUT si tu les as déjà collectés).
Maintiens le signe stable environ 1 seconde -- un repère visuel
« maintien: X/10 » s'affiche à l'écran pour te guider. Une fois à 10/10,
la lettre ou le mot s'ajoute au texte affiché sous la vidéo.

Bouton **Effacer** pour recommencer une phrase sans redémarrer le flux.

## 5. Si tu n'as pas encore collecté les mots

```bash
python -m src.recognition.collect_words_session --signer signeur1
python -m src.recognition.train
```

## Ce qui a changé par rapport à avant (pour comprendre, pas juste copier)

- `src/recognition/features.py` est NOUVEAU : une seule fonction
  d'extraction de features, utilisée à la fois par `train.py` et
  `app.py`. Avant, chacun recalculait ça séparément à sa façon, ce qui
  a fini par désynchroniser entraînement et inférence -- c'est ce qui
  causait "tout reconnu comme Q".
- `app.py` ne contient plus de boucle `while` bloquante. C'est elle qui
  causait l'erreur `StreamlitDuplicateElementKey`. Le texte s'accumule
  maintenant via `st.session_state` + `st.rerun()`, le mécanisme
  recommandé par Streamlit pour ce type d'interface.
- La normalisation des landmarks (centrage/mise à l'échelle) a été
  retirée. C'est une piste d'amélioration réelle mais risquée à tester
  sous pression de temps -- à regarder calmement après la démo, pas avant.
