# -------------------------------------------------------------------------
# AP_B_fluxo_serie.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Calcula taxas de fluxo (promocao, repetencia, evasao, mig EJA) por
#   SERIE INDIVIDUAL (1o EF a 4o EM tecnico) e ano.
#
# Outputs:
#   ../output/AP_B_fluxo_por_serie_ano.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

t = pd.read_parquet(OUT / "C20_transitions_v5.parquet")

# nivel_t define a serie (1-13)
SERIE_LABEL = {
    1:"1o EF", 2:"2o EF", 3:"3o EF", 4:"4o EF", 5:"5o EF",
    6:"6o EF", 7:"7o EF", 8:"8o EF", 9:"9o EF",
    10:"1o EM", 11:"2o EM", 12:"3o EM", 13:"4o EM tec",
}

rows = []
for (ano, nivel), sub in t.groupby(["ano_t", "nivel_t"]):
    if pd.isna(nivel) or nivel not in SERIE_LABEL: continue
    if sub["wt"].sum() == 0: continue
    rows.append({
        "ano_t": int(ano),
        "nivel": int(nivel),
        "serie": SERIE_LABEL[int(nivel)],
        "flag_promocao": np.average(sub["flag_promocao"], weights=sub["wt"]),
        "flag_repetencia": np.average(sub["flag_repetencia"], weights=sub["wt"]),
        "flag_evasao": np.average(sub["flag_evasao"], weights=sub["wt"]),
        "flag_migracao_eja": np.average(sub["flag_migracao_eja"], weights=sub["wt"]),
        "n": len(sub),
    })
agg = pd.DataFrame(rows).sort_values(["nivel","ano_t"])
agg.to_csv(OUT / "AP_B_fluxo_por_serie_ano.csv", index=False)
print(f"Saved AP_B_fluxo_por_serie_ano.csv ({len(agg)} rows)")
