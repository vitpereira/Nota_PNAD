# -------------------------------------------------------------------------
# C39_completion_by_age.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Computa % de jovens 14-24 que ja concluiram o EM (VD3004 >= 5),
#   por idade individual e grupo de renda dom. per capita.
#
#   Idea: comparar coortes EXPOSTAS ao PdM (tinham <=17 quando PdM
#   comecou em Mar/2024) com coortes NAO EXPOSTAS (>=21 em Mar/2024,
#   ja tinham saido do EM antes do programa).
#
#   Usa amostra de 2025 (Q1-Q4) para maximizar tamanho de amostra
#   no periodo pos-PdM. Renda classificada contemporaneamente.
#
# Outputs:
#   ../output/C39_completion_by_age.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

LINHA_EXTREMA = 230
SM_2025 = 1518
MEIO_SM = SM_2025 / 2

# { Carrega PNADC 2025 (Q1-Q4) ----
print("Loading 2025 PNADC...")
frames = []
for q in [1, 2, 3, 4]:
    p = PD_TRI / f"pnadc_0{q}2025.parquet"
    if not p.exists():
        continue
    d = pd.read_parquet(p, columns=["UF", "UPA", "V1008", "V1014",
                                      "Ano", "Trimestre",
                                      "V2001", "V2009", "VD3004",
                                      "V403312", "V1028"])
    for c in ["V2009", "VD3004", "V1028", "V403312", "V2001"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d["V2009"].between(14, 24)]
    frames.append(d)
df = pd.concat(frames, ignore_index=True)
print(f"  14-24 obs: {len(df):,}")
# } ----

# { Renda dom. per capita ----
print("Computing renda_dom_pc...")
renda_frames = []
for q in [1, 2, 3, 4]:
    p = PD_TRI / f"pnadc_0{q}2025.parquet"
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
    renda_frames.append(hh)
hh_renda = pd.concat(renda_frames, ignore_index=True)
hh_renda["renda_pc"] = hh_renda["renda_total"] / hh_renda["n_membros"].replace(0, np.nan)
print(f"  HH-trim com renda: {len(hh_renda):,}")
# } ----

# { Merge e classifica ----
df["hh_yr_q"] = (df["UF"].astype(str) + "_" + df["UPA"].astype(str)
                  + "_" + df["V1008"].astype(str) + "_" + df["V1014"].astype(str)
                  + "_" + df["Ano"].astype(str) + "Q" + df["Trimestre"].astype(str))
df = df.merge(hh_renda[["hh_yr_q", "renda_pc"]], on="hh_yr_q", how="left")
df = df.dropna(subset=["renda_pc"]).copy()

def classify(r):
    if r < LINHA_EXTREMA: return "Renda < R$ 230"
    if r > MEIO_SM:        return "Renda > 1/2 SM"
    return "R$ 230 a 1/2 SM"
df["grupo"] = df["renda_pc"].apply(classify)
# } ----

# { Outcome: ja completou EM (VD3004 >= 5) ----
df["completed_em"] = (df["VD3004"] >= 5).astype(int)
df["wt"] = df["V1028"].fillna(0)
df = df[df["wt"] > 0]

# Idade em 2024 (Mar/2024 = inicio PdM)
# Em 2025: idade_2024 = idade_atual - (Ano - 2024) = idade - 1
df["idade_pdm"] = df["V2009"] - (df["Ano"] - 2024)
# } ----

# { Agrega ----
print("\nAggregating by age x grupo...")
rows = []
for (idade, grupo), sub in df.groupby(["V2009", "grupo"]):
    if sub["wt"].sum() == 0: continue
    rate = np.average(sub["completed_em"], weights=sub["wt"])
    rows.append({"idade": int(idade), "grupo": grupo,
                  "completed_rate": rate, "n": len(sub)})

agg = pd.DataFrame(rows).sort_values(["grupo", "idade"])
agg.to_csv(OUT_DIR / "C39_completion_by_age.csv", index=False)
print(f"Saved {OUT_DIR / 'C39_completion_by_age.csv'}")
print(agg.to_string(index=False))
# } ----
