# -------------------------------------------------------------------------
# AP_D_conclusao.py
# -------------------------------------------------------------------------
# Description:
#   % concluiu cada etapa por idade, ano, grupo demografico:
#     - EF completo (VD3004 >= 3)
#     - EM completo (VD3004 >= 5)
#     - Superior (VD3004 >= 7)
#   Por ano de observacao 2015/17/19/21/23/25 e idade 14-29.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT = ROOT / "DataWork/3_Indicators/output"

YEARS = [2015, 2017, 2019, 2021, 2023, 2025]

def load_year(y, age_lo, age_hi):
    frames = []
    for q in [1,2,3,4]:
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["V2009","V2007","V2010","VD3004","V1028"])
        for c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
        d = d[d["V2009"].between(age_lo, age_hi)]
        frames.append(d)
    if not frames: return None
    df = pd.concat(frames, ignore_index=True)
    df["wt"] = df["V1028"].fillna(0)
    df = df[df["wt"] > 0]
    return df

# Conclusao por idade, ano, sexo, raca
print("Computing conclusao...")
rows = []
for y in YEARS:
    df = load_year(y, 14, 29)
    if df is None: continue
    df["ef_completo"]  = (df["VD3004"] >= 3).astype(int)
    df["em_completo"]  = (df["VD3004"] >= 5).astype(int)
    df["sup_completo"] = (df["VD3004"] >= 7).astype(int)
    df["raca"] = df["V2010"].map({1:"Branca",2:"Preta",4:"Parda",
                                       3:"Amarela",5:"Indigena"})
    df["sexo"] = df["V2007"].map({1:"Homem",2:"Mulher"})

    # Total
    for idade, sub in df.groupby("V2009"):
        if sub["wt"].sum() == 0: continue
        rows.append({"ano":y, "idade":int(idade), "categoria":"total",
                      "valor":"Total",
                      "ef": np.average(sub.ef_completo, weights=sub.wt),
                      "em": np.average(sub.em_completo, weights=sub.wt),
                      "sup": np.average(sub.sup_completo, weights=sub.wt),
                      "n": len(sub)})

    # Por sexo
    for (idade, sx), sub in df.groupby(["V2009","sexo"]):
        if pd.isna(sx) or sub["wt"].sum() == 0: continue
        rows.append({"ano":y, "idade":int(idade), "categoria":"sexo",
                      "valor":sx,
                      "ef": np.average(sub.ef_completo, weights=sub.wt),
                      "em": np.average(sub.em_completo, weights=sub.wt),
                      "sup": np.average(sub.sup_completo, weights=sub.wt),
                      "n": len(sub)})

    # Por raca
    for (idade, rc), sub in df.groupby(["V2009","raca"]):
        if pd.isna(rc) or sub["wt"].sum() == 0: continue
        rows.append({"ano":y, "idade":int(idade), "categoria":"raca",
                      "valor":rc,
                      "ef": np.average(sub.ef_completo, weights=sub.wt),
                      "em": np.average(sub.em_completo, weights=sub.wt),
                      "sup": np.average(sub.sup_completo, weights=sub.wt),
                      "n": len(sub)})

out = pd.DataFrame(rows).sort_values(["categoria","valor","ano","idade"])
out.to_csv(OUT / "AP_D_conclusao_por_etapa.csv", index=False)
print(f"Saved AP_D ({len(out)} rows)")
