# -------------------------------------------------------------------------
# AP_E2_fluxos_quintil.py
# -------------------------------------------------------------------------
# Description:
#   Fluxos (prom, rep, evas) por quintil de renda dom. per capita,
#   macroetapa, ano. Usa as transicoes v5 + renda do trim_t.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

t = pd.read_parquet(OUT / "C20_transitions_v5.parquet")
# renda_t ja vem normalizada nas transicoes

# Quintis dentro de cada ano
rows = []
for ano, sub in t.groupby("ano_t"):
    sub = sub.dropna(subset=["renda_t"]).copy()
    if len(sub) == 0: continue
    qtl = sub["renda_t"].quantile([0.2, 0.4, 0.6, 0.8]).values
    def to_q(r):
        if r < qtl[0]: return "Q1"
        if r < qtl[1]: return "Q2"
        if r < qtl[2]: return "Q3"
        if r < qtl[3]: return "Q4"
        return "Q5"
    sub["quintil"] = sub["renda_t"].apply(to_q)
    for (macro, q), s in sub.groupby(["macroetapa_t","quintil"]):
        if s["wt"].sum() == 0: continue
        rows.append({"ano":int(ano), "macroetapa":macro, "quintil":q,
                      "prom":  np.average(s.flag_promocao,    weights=s.wt),
                      "rep":   np.average(s.flag_repetencia,  weights=s.wt),
                      "evas":  np.average(s.flag_evasao,      weights=s.wt),
                      "eja":   np.average(s.flag_migracao_eja,weights=s.wt),
                      "n":     len(s)})
out = pd.DataFrame(rows).sort_values(["macroetapa","quintil","ano"])
out.to_csv(OUT / "AP_E_fluxos_por_quintil.csv", index=False)
print(f"AP_E fluxos: {len(out)} rows")
