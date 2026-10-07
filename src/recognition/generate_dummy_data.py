"""Génère un CSV de landmarks factices pour TESTER le pipeline uniquement.

Ne jamais confondre ce fichier avec de vraies données d'entraînement.
"""

import csv
import os
import random

OUTPUT = "data/raw/landmarks_dataset.csv"
LABELS = list("ABCDE") + ["SALUT"]
SIGNERS = ["dummy_signer1", "dummy_signer2"]

header = ["label", "signer"] + [f"{axis}{i}" for i in range(21) for axis in ("x", "y", "z")]

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for label in LABELS:
        base = [random.random() for _ in range(63)]
        for signer in SIGNERS:
            for _ in range(15):
                row = [label, signer] + [v + random.uniform(-0.02, 0.02) for v in base]
                writer.writerow(row)

print(f"Fichier factice généré : {OUTPUT}")
