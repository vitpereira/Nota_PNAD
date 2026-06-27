# -------------------------------------------------------------------------
# AP_FG_demo_uf.py
# -------------------------------------------------------------------------
# Description:
#   F. Conclusao EM por raca x sexo x idade
#   G. Conclusao EM aos 21 anos por UF, ano (para mapas)
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT = ROOT / "DataWork/3_Indicators/output"

YEARS = [2015, 2017, 2019, 2021, 2023, 2025]

UF_NAME = {11:"RO",12:"AC",13:"AM",14:"RR",15:"PA",16:"AP",17:"TO",
            21:"MA",22:"PI",23:"CE",24:"RN",25:"PB",26:"PE",27:"AL",28:"SE",29:"BA",
            31:"MG",32:"ES",33:"RJ",35:"SP",
            41:"PR",42:"SC",43:"RS",
            50:"MS",51:"MT",52:"GO",53:"DF"}
REGIAO = {11:"N",12:"N",13:"N",14:"N",15:"N",16:"N",17:"N",
           21:"NE",22:"NE",23:"NE",24:"NE",25:"NE",26:"NE",27:"NE",28:"NE",29:"NE",
           31:"SE",32:"SE",33:"SE",35:"SE",
           41:"S",42:"S",43:"S",
           50:"CO",51:"CO",52:"CO",53:"CO"}


def load_year(y, age_lo=14, age_hi=29):
    frames = []
    for q in [1,2,3,4]:
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["UF","V2009","V2007","V2010",
                                          "VD3004","V1028"])
        for c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
        d = d[d["V2009"].between(age_lo, age_hi)]
        frames.append(d)
    if not frames: return None
    return pd.concat(frames, ignore_index=True)


# F: raca x sexo x idade
print("F section...")
rows = []
for y in YEARS:
    df = load_year(y, 14, 24)
    if df is None: continue
    df["wt"] = df["V1028"].fillna(0)
    df = df[df["wt"] > 0]
    df["em_completo"] = (df["VD3004"] >= 5).astype(int)
    df["raca"] = df["V2010"].map({1:"Branca",2:"Preta",4:"Parda"})
    df["sexo"] = df["V2007"].map({1:"Homem",2:"Mulher"})
    df = df.dropna(subset=["raca","sexo"])
    for (idade, rc, sx), sub in df.groupby(["V2009","raca","sexo"]):
        if sub["wt"].sum() == 0: continue
        rate = np.average(sub.em_completo, weights=sub.wt)
        rows.append({"ano":y, "idade":int(idade), "raca":rc, "sexo":sx,
                      "em":rate, "n":len(sub)})
out_f = pd.DataFrame(rows)
out_f.to_csv(OUT / "AP_F_em_por_raca_sexo.csv", index=False)
print(f"  AP_F: {len(out_f)} rows")

# G: UF (concluiu EM aos 19-21)
print("G section...")
rows = []
for y in YEARS:
    df = load_year(y, 19, 21)
    if df is None: continue
    df["wt"] = df["V1028"].fillna(0)
    df = df[df["wt"] > 0]
    df["em_completo"] = (df["VD3004"] >= 5).astype(int)
    df["uf_name"] = df["UF"].map(UF_NAME)
    df["regiao"] = df["UF"].map(REGIAO)
    df = df.dropna(subset=["uf_name"])
    for (uf, regiao), sub in df.groupby(["uf_name","regiao"]):
        if sub["wt"].sum() == 0: continue
        rate = np.average(sub.em_completo, weights=sub.wt)
        rows.append({"ano":y, "uf":uf, "regiao":regiao,
                      "em":rate, "n":len(sub)})
out_g = pd.DataFrame(rows)
out_g.to_csv(OUT / "AP_G_em_aos_19_21_por_uf.csv", index=False)
print(f"  AP_G: {len(out_g)} rows")
