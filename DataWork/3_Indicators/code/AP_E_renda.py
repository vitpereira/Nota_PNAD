# -------------------------------------------------------------------------
# AP_E_renda.py
# -------------------------------------------------------------------------
# Description:
#   % concluiu EM por quintil de renda dom. per capita, por idade e ano.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT = ROOT / "DataWork/3_Indicators/output"

YEARS = [2015, 2017, 2019, 2021, 2023, 2025]

def load_with_renda(y):
    pessoa_frames = []
    renda_frames = []
    for q in [1,2,3,4]:
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["UF","UPA","V1008","V1014",
                                          "Ano","Trimestre",
                                          "V2001","V2009","V2007","V2010",
                                          "VD3004","V403312","V1028"])
        for c in d.columns:
            if c not in ("UF","UPA","V1008","V1014","Ano","Trimestre"):
                d[c] = pd.to_numeric(d[c], errors="coerce")
        d["hh_yr_q"] = (d["UF"].astype(str) + "_" + d["UPA"].astype(str)
                         + "_" + d["V1008"].astype(str) + "_" + d["V1014"].astype(str)
                         + "_" + d["Ano"].astype(str) + "Q" + d["Trimestre"].astype(str))
        d["renda_ind"] = d["V403312"].fillna(0)
        # Renda dom
        hh = d.groupby("hh_yr_q").agg(renda_total=("renda_ind","sum"),
                                         n_membros=("V2001","first")).reset_index()
        hh["renda_pc"] = hh["renda_total"] / hh["n_membros"].replace(0, np.nan)
        d = d[d["V2009"].between(14, 24)].copy()
        d = d.merge(hh[["hh_yr_q","renda_pc"]], on="hh_yr_q", how="left")
        d["ano_y"] = y
        pessoa_frames.append(d)
    if not pessoa_frames: return None
    return pd.concat(pessoa_frames, ignore_index=True)

rows = []
for y in YEARS:
    print(f"  {y}...")
    df = load_with_renda(y)
    if df is None: continue
    df = df.dropna(subset=["renda_pc"]).copy()
    df["wt"] = df["V1028"].fillna(0)
    df = df[df["wt"] > 0]

    # Quintis (ponderados) dentro do ano
    qtl = df["renda_pc"].quantile([0.2,0.4,0.6,0.8]).values
    def to_q(r):
        if r < qtl[0]: return "Q1 (mais pobre)"
        if r < qtl[1]: return "Q2"
        if r < qtl[2]: return "Q3"
        if r < qtl[3]: return "Q4"
        return "Q5 (mais rico)"
    df["quintil"] = df["renda_pc"].apply(to_q)
    df["em_completo"] = (df["VD3004"] >= 5).astype(int)
    df["ef_completo"] = (df["VD3004"] >= 3).astype(int)

    for (idade, q), sub in df.groupby(["V2009","quintil"]):
        if sub["wt"].sum() == 0: continue
        rows.append({"ano":y, "idade":int(idade), "quintil":q,
                      "ef": np.average(sub.ef_completo, weights=sub.wt),
                      "em": np.average(sub.em_completo, weights=sub.wt),
                      "n": len(sub)})

out = pd.DataFrame(rows).sort_values(["ano","quintil","idade"])
out.to_csv(OUT / "AP_E_conclusao_por_quintil.csv", index=False)
print(f"Saved AP_E ({len(out)} rows)")
