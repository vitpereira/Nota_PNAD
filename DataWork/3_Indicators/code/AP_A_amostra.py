# -------------------------------------------------------------------------
# AP_A_amostra.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Caracterizacao da amostra para o apendice descritivo.
#   - A.1.1: Tamanho amostral por ano (pessoa-trim, 4-24 anos)
#   - A.1.2: Distribuicao de idade por ano
#   - A.1.3: Distribuicao por sexo e raca por ano
#
# Outputs:
#   ../output/AP_A1_amostra_por_ano.csv
#   ../output/AP_A2_idade_por_ano.csv
#   ../output/AP_A3_sexo_raca_por_ano.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT = ROOT / "DataWork/3_Indicators/output"

YEARS = list(range(2012, 2026))

# A.1.1: Tamanho amostral por ano
rows = []
for y in YEARS:
    n_total = 0
    n_pop = 0  # populacao ponderada
    for q in [1,2,3,4]:
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["V2009","V1028"])
        d["V2009"] = pd.to_numeric(d["V2009"], errors="coerce")
        d["V1028"] = pd.to_numeric(d["V1028"], errors="coerce")
        d = d[d["V2009"].between(4,24)]
        n_total += len(d)
        n_pop   += d["V1028"].fillna(0).sum()
    rows.append({"ano": y, "n_obs": n_total,
                  "n_pop_milhoes": n_pop/1e6/4})  # divide por 4 trimestres
df = pd.DataFrame(rows)
df.to_csv(OUT / "AP_A1_amostra_por_ano.csv", index=False)
print(f"A1: {len(df)} anos")

# A.1.2: Distribuicao de idade por ano
rows = []
for y in YEARS:
    for q in [2]:  # Q2 representativo
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["V2009","V1028"])
        d["V2009"] = pd.to_numeric(d["V2009"], errors="coerce")
        d["V1028"] = pd.to_numeric(d["V1028"], errors="coerce")
        d = d[d["V2009"].between(4,24)].copy()
        d["wt"] = d["V1028"].fillna(0)
        agg = d.groupby("V2009")["wt"].sum().reset_index()
        agg["ano"] = y
        agg = agg.rename(columns={"V2009":"idade","wt":"pop"})
        agg["share"] = agg["pop"] / agg["pop"].sum()
        rows.append(agg)
out = pd.concat(rows, ignore_index=True)
out.to_csv(OUT / "AP_A2_idade_por_ano.csv", index=False)
print(f"A2: {len(out)} rows")

# A.1.3: Sexo e raca por ano (Q2)
rows = []
for y in YEARS:
    p = PD_TRI / f"pnadc_02{y}.parquet"
    if not p.exists(): continue
    d = pd.read_parquet(p, columns=["V2007","V2010","V2009","V1028"])
    for c in ["V2007","V2010","V2009","V1028"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d["V2009"].between(4,24)].copy()
    d["wt"] = d["V1028"].fillna(0)
    # Sexo
    sex = d.groupby("V2007")["wt"].sum()
    total_w = sex.sum()
    # Raca
    rac = d.groupby("V2010")["wt"].sum()
    raca_label = {1:"Branca",2:"Preta",3:"Amarela",4:"Parda",5:"Indigena",9:"Ignorada"}
    for r,label in raca_label.items():
        rows.append({"ano":y, "categoria":"raca", "valor":label,
                      "share": rac.get(r,0)/total_w})
    for s,label in {1:"Homem",2:"Mulher"}.items():
        rows.append({"ano":y, "categoria":"sexo", "valor":label,
                      "share": sex.get(s,0)/total_w})
out = pd.DataFrame(rows)
out.to_csv(OUT / "AP_A3_sexo_raca_por_ano.csv", index=False)
print(f"A3: {len(out)} rows")

print("\nAll AP_A files saved.")
