# -------------------------------------------------------------------------
# C40_completion_2023_2025.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   % de jovens 14-21 que ja concluiram o EM (VD3004 >= 5), por idade
#   individual, em 2023 (pre-PdM) e 2025 (pos-PdM), por grupo de renda.
#
#   Compara coorte EXPOSTA ao PdM (2025) com coorte CONTROLE (2023)
#   no MESMO eixo de idade.
#
# Outputs:
#   ../output/C40_completion_2023_2025.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

LINHA_EXTREMA = 230
SM = {2023: 1320, 2025: 1518}


def load_year(year):
    """Carrega PNADC todos os trimestres do ano, 14-21 anos."""
    frames = []
    for q in [1, 2, 3, 4]:
        p = PD_TRI / f"pnadc_0{q}{year}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["UF", "UPA", "V1008", "V1014",
                                          "Ano", "Trimestre",
                                          "V2001", "V2009", "VD3004",
                                          "V403312", "V1028"])
        for c in ["V2009", "VD3004", "V1028", "V403312", "V2001"]:
            d[c] = pd.to_numeric(d[c], errors="coerce")
        d = d[d["V2009"].between(14, 21)]
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def add_renda(df, year):
    """Adiciona renda_pc do HH-trimestre."""
    frames = []
    for q in [1, 2, 3, 4]:
        p = PD_TRI / f"pnadc_0{q}{year}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["UF", "UPA", "V1008", "V1014",
                                          "Ano", "Trimestre", "V2001", "V403312"])
        d["V403312"] = pd.to_numeric(d["V403312"], errors="coerce").fillna(0)
        d["V2001"] = pd.to_numeric(d["V2001"], errors="coerce")
        d["hh_yr_q"] = (d["UF"].astype(str) + "_" + d["UPA"].astype(str)
                         + "_" + d["V1008"].astype(str) + "_" + d["V1014"].astype(str)
                         + "_" + d["Ano"].astype(str) + "Q" + d["Trimestre"].astype(str))
        hh = d.groupby("hh_yr_q").agg(renda_total=("V403312", "sum"),
                                         n_membros=("V2001", "first")).reset_index()
        frames.append(hh)
    hh_renda = pd.concat(frames, ignore_index=True)
    hh_renda["renda_pc"] = hh_renda["renda_total"] / hh_renda["n_membros"].replace(0, np.nan)
    df["hh_yr_q"] = (df["UF"].astype(str) + "_" + df["UPA"].astype(str)
                      + "_" + df["V1008"].astype(str) + "_" + df["V1014"].astype(str)
                      + "_" + df["Ano"].astype(str) + "Q" + df["Trimestre"].astype(str))
    return df.merge(hh_renda[["hh_yr_q", "renda_pc"]], on="hh_yr_q", how="left")


def classify(r, meio_sm):
    if pd.isna(r): return None
    if r < LINHA_EXTREMA: return "Renda < R$ 230"
    if r > meio_sm:        return "Renda > 1/2 SM"
    return "R$ 230 a 1/2 SM"


all_rows = []
for year in [2023, 2025]:
    print(f"Loading {year}...")
    d = load_year(year)
    d = add_renda(d, year)
    meio_sm = SM[year] / 2
    d["grupo"] = d["renda_pc"].apply(lambda r: classify(r, meio_sm))
    d = d.dropna(subset=["grupo"])
    d["completed_em"] = (d["VD3004"] >= 5).astype(int)
    d["wt"] = d["V1028"].fillna(0)
    d = d[d["wt"] > 0]

    print(f"  obs: {len(d):,}")
    for (idade, grupo), sub in d.groupby(["V2009", "grupo"]):
        if sub["wt"].sum() == 0: continue
        rate = np.average(sub["completed_em"], weights=sub["wt"])
        all_rows.append({"ano": year, "idade": int(idade), "grupo": grupo,
                          "completed_rate": rate, "n": len(sub)})

agg = pd.DataFrame(all_rows).sort_values(["grupo", "ano", "idade"])
agg.to_csv(OUT_DIR / "C40_completion_2023_2025.csv", index=False)
print(f"\nSaved C40_completion_2023_2025.csv")
print(agg.to_string(index=False))
