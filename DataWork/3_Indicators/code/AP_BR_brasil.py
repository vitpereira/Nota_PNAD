# -------------------------------------------------------------------------
# AP_BR_brasil.py
# -------------------------------------------------------------------------
# Description:
#   B.1 Brasil agregado: serie temporal dos fluxos por macroetapa (ja
#   temos no F1_serie_temporal). Calculamos a IDENTIDADE CONTABIL e
#   o residuo por ano.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

t = pd.read_parquet(OUT / "C20_transitions_v5.parquet")

# Identidade contabil: sum = 1 (idealmente)
rows = []
for (ano, macro), sub in t.groupby(["ano_t","macroetapa_t"]):
    if sub["wt"].sum() == 0: continue
    prom = np.average(sub.flag_promocao, weights=sub.wt)
    rep  = np.average(sub.flag_repetencia, weights=sub.wt)
    evas = np.average(sub.flag_evasao, weights=sub.wt)
    eja  = np.average(sub.flag_migracao_eja, weights=sub.wt)
    total = prom + rep + evas + eja
    rows.append({"ano":int(ano), "macroetapa":macro,
                  "prom":prom, "rep":rep, "evas":evas, "eja":eja,
                  "total":total, "residuo":1 - total,
                  "n":len(sub)})
out = pd.DataFrame(rows)
out.to_csv(OUT / "AP_BR_identidade_contabil.csv", index=False)
print(f"AP_BR identidade: {len(out)} rows")
