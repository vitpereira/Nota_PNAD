# -------------------------------------------------------------------------
# C38_attendance_stable_15_17.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Restringe C33 micro a jovens 15-17 anos e agrega series por grupo
#   (classificacao estavel). Outcomes:
#     - em_regular
#     - em_or_eja_or_done (EM reg OR EJA EM OR formou)
#     - engage (freq escola OU formou EM)
#
# Outputs:
#   ../output/C38_attendance_15_17_em.csv
#   ../output/C38_attendance_15_17_em_or_eja.csv
#   ../output/C38_attendance_15_17_engage.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

print("Loading micro...")
d = pd.read_parquet(OUT_DIR / "C33_micro_em_15_19.parquet")
d = d[d["idade"].between(15, 17)].copy()
print(f"  15-17 obs: {len(d):,}")

LABEL = {"extreme": "Renda < R$ 230",
         "low":     "R$ 230 a 1/2 SM",
         "control": "Renda > 1/2 SM"}

def aggregate(df, outcome_col, rate_name):
    rows = []
    for (a, q, g), sub in df.groupby(["Ano", "Trimestre", "grupo"]):
        if sub["wt"].sum() == 0: continue
        rate = np.average(sub[outcome_col], weights=sub["wt"])
        rows.append({"Ano": int(a), "Trim": int(q), "grupo": LABEL[g],
                      rate_name: rate, "n": len(sub),
                      "ano_trim": f"{int(a)}Q{int(q)}"})
    return pd.DataFrame(rows).sort_values(["Ano", "Trim", "grupo"])

aggregate(d, "em_regular", "em_rate").to_csv(
    OUT_DIR / "C38_attendance_15_17_em.csv", index=False)
aggregate(d, "em_or_eja_or_done", "em_engage").to_csv(
    OUT_DIR / "C38_attendance_15_17_em_or_eja.csv", index=False)
aggregate(d, "escola_ou_em_completo", "engagement").to_csv(
    OUT_DIR / "C38_attendance_15_17_engage.csv", index=False)
print("Saved 3 CSVs.")
