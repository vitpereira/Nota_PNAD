# -------------------------------------------------------------------------
# C35_engagement_by_renda.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Serie trimestral 2022Q1-2025Q4 do indicador de ENGAJAMENTO ESCOLAR:
#     y = 1 se (frequenta escola V3002=1) OU (ja concluiu EM VD3004>=5)
#   Universo: jovens 15-19 anos. Grupos por renda dom. per capita.
#
# Outputs:
#   ../output/C35_engagement_by_renda.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# Reuse the micro built by C33
micro = pd.read_parquet(OUT_DIR / "C33_micro_em_15_19.parquet")
print(f"Loaded micro: {len(micro):,} rows")

# Aggregate by (Ano, Trim, grupo)
rows = []
for (a, q, g), sub in micro.groupby(["Ano", "Trimestre", "grupo"]):
    if sub["wt"].sum() == 0: continue
    rate = np.average(sub["escola_ou_em_completo"], weights=sub["wt"])
    rows.append({"Ano": int(a), "Trim": int(q), "grupo": g,
                  "engagement": rate, "n": len(sub),
                  "ano_trim": f"{int(a)}Q{int(q)}"})

# Map grupo to readable label
LABEL = {"extreme": "Renda < R$ 230",
         "low":     "R$ 230 a 1/2 SM",
         "control": "Renda > 1/2 SM"}
agg = pd.DataFrame(rows)
agg["grupo"] = agg["grupo"].map(LABEL)
agg = agg.sort_values(["Ano", "Trim", "grupo"])
agg.to_csv(OUT_DIR / "C35_engagement_by_renda.csv", index=False)
print(f"Saved C35_engagement_by_renda.csv ({len(agg)} rows)")
print(agg.to_string(index=False))
