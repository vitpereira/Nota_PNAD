# -------------------------------------------------------------------------
# C37_attendance_stable.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Re-aggrega series trimestrais de attendance/engagement por grupo de
#   renda usando a CLASSIFICACAO ESTAVEL definida em C33 (renda fixada na
#   primeira observacao do HH). Universo: jovens 15-19 anos.
#
#   Outcomes:
#     1. em_regular: matricula em EM regular (V3002=1 AND V3003A=6)
#     2. em_engage:  matricula em EM regular OU EJA EM OU concluiu EM
#     3. engage:     frequenta escola OU concluiu EM
#
# Inputs:
#   ../output/C33_micro_em_15_19.parquet
#
# Outputs:
#   ../output/C37_attendance_stable_em.csv
#   ../output/C37_attendance_stable_engage.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

print("Loading micro from C33...", flush=True)
d = pd.read_parquet(OUT_DIR / "C33_micro_em_15_19.parquet")
print(f"  {len(d):,} rows, {d['hh_id'].nunique():,} HHs", flush=True)

LABEL = {"extreme": "Renda < R$ 230",
         "low":     "R$ 230 a 1/2 SM",
         "control": "Renda > 1/2 SM"}

def aggregate(df, outcome_col):
    rows = []
    for (a, q, g), sub in df.groupby(["Ano", "Trimestre", "grupo"]):
        if sub["wt"].sum() == 0: continue
        rate = np.average(sub[outcome_col], weights=sub["wt"])
        rows.append({"Ano": int(a), "Trim": int(q), "grupo": LABEL[g],
                      "valor": rate, "n": len(sub),
                      "ano_trim": f"{int(a)}Q{int(q)}"})
    return pd.DataFrame(rows).sort_values(["Ano", "Trim", "grupo"])

# Outcome 1: em_regular (matricula em EM regular V3002=1 AND V3003A=6)
agg_em = aggregate(d, "em_regular")
agg_em = agg_em.rename(columns={"valor": "em_rate"})
agg_em.to_csv(OUT_DIR / "C37_attendance_stable_em.csv", index=False)
print(f"\nSaved C37_attendance_stable_em.csv")

# Outcome 2: engage (frequenta OU formou EM)
agg_en = aggregate(d, "escola_ou_em_completo")
agg_en = agg_en.rename(columns={"valor": "engagement"})
agg_en.to_csv(OUT_DIR / "C37_attendance_stable_engage.csv", index=False)
print(f"Saved C37_attendance_stable_engage.csv")

# Outcome 3: em_engage (EM regular OU EJA EM OU formou)
agg_emen = aggregate(d, "em_or_eja_or_done")
agg_emen = agg_emen.rename(columns={"valor": "em_engage"})
agg_emen.to_csv(OUT_DIR / "C37_attendance_stable_em_or_eja.csv", index=False)
print(f"Saved C37_attendance_stable_em_or_eja.csv")
