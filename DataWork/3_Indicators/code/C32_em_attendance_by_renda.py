# -------------------------------------------------------------------------
# C32_em_attendance_by_renda.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Serie trimestral 2022Q1-2025Q4 de matricula em EM regular entre
#   jovens 15-19 anos, dividida em 3 grupos por renda domiciliar per
#   capita (renda_dom_pc):
#     - Renda < 1/4 SM (extrema pobreza, faixa prioritaria CadUnico)
#     - 1/4 SM <= renda <= 1/2 SM (CadUnico-elegivel)
#     - Renda > 1/2 SM (fora CadUnico)
#
# Inputs:
#   ../../1_DownloadPNADC/tmp/pnad_parsed/pnadc_{TT}{ANO}.parquet
#
# Outputs:
#   ../output/C32_em_attendance_by_renda.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# Salario minimo R$/mes
SM = {2022: 1212, 2023: 1320, 2024: 1412, 2025: 1518}

# { 1. Load PNADC trimestral 2022-2025 ----
print("Loading PNADC trimestral 2022-2025...", flush=True)
frames = []
for y in [2022, 2023, 2024, 2025]:
    for q in [1, 2, 3, 4]:
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists():
            print(f"  MISSING {p.name}"); continue
        d = pd.read_parquet(p, columns=["UF", "UPA", "V1008", "V1014", "V2003",
                                          "Ano", "Trimestre",
                                          "V2001", "V2009", "V3002", "V3003A",
                                          "V403312", "V1028"])
        for c in ["V2009", "V3002", "V3003A", "V1028", "V403312", "V2001"]:
            d[c] = pd.to_numeric(d[c], errors="coerce")
        # Filter age 15-19
        d = d[d["V2009"].between(15, 19)]
        frames.append(d)
df = pd.concat(frames, ignore_index=True)
print(f"  EM-age obs 2022-2025: {len(df):,}", flush=True)
# } ----

# { 2. Compute renda_dom_pc per HH-trim ----
print("\nComputing renda_dom_pc per HH-trim...", flush=True)
renda_frames = []
for y in [2022, 2023, 2024, 2025]:
    for q in [1, 2, 3, 4]:
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["UF", "UPA", "V1008", "V1014",
                                          "Ano", "Trimestre", "V2001", "V403312"])
        d["V403312"] = pd.to_numeric(d["V403312"], errors="coerce").fillna(0)
        d["V2001"] = pd.to_numeric(d["V2001"], errors="coerce")
        d["hh_yr_q"] = (d["UF"].astype(str) + "_" + d["UPA"].astype(str)
                         + "_" + d["V1008"].astype(str) + "_" + d["V1014"].astype(str)
                         + "_" + d["Ano"].astype(str) + "Q" + d["Trimestre"].astype(str))
        hh_renda = d.groupby("hh_yr_q").agg(renda_total=("V403312", "sum"),
                                              n_membros=("V2001", "first")).reset_index()
        renda_frames.append(hh_renda)
hh_renda_all = pd.concat(renda_frames, ignore_index=True)
hh_renda_all["renda_pc"] = hh_renda_all["renda_total"] / hh_renda_all["n_membros"].replace(0, np.nan)
print(f"  HH-trim renda computed: {len(hh_renda_all):,}", flush=True)
# } ----

# { 3. Merge renda_pc onto EM-age df ----
df["hh_yr_q"] = (df["UF"].astype(str) + "_" + df["UPA"].astype(str)
                  + "_" + df["V1008"].astype(str) + "_" + df["V1014"].astype(str)
                  + "_" + df["Ano"].astype(str) + "Q" + df["Trimestre"].astype(str))
df = df.merge(hh_renda_all[["hh_yr_q", "renda_pc"]], on="hh_yr_q", how="left")

# Salario minimo do ano
df["sm"] = df["Ano"].map(SM)
df["quarto_sm"] = df["sm"] / 4.0
df["meio_sm"]   = df["sm"] / 2.0
# } ----

# { 4. Classify by renda ----
def classify(row):
    if pd.isna(row["renda_pc"]):
        return None  # exclude
    if row["renda_pc"] < row["quarto_sm"]:
        return "Renda < 1/4 SM"
    if row["renda_pc"] <= row["meio_sm"]:
        return "1/4 a 1/2 SM"
    return "Renda > 1/2 SM"

print("\nClassifying groups...", flush=True)
df["grupo"] = df.apply(classify, axis=1)
df = df[df["grupo"].notna()].copy()
print(df["grupo"].value_counts(), flush=True)
# } ----

# { 5. EM regular flag and aggregate ----
df["em_regular"] = ((df["V3002"] == 1) & (df["V3003A"] == 6)).astype(int)
df["wt"] = df["V1028"].fillna(0)

rows = []
for (a, q, g), sub in df.groupby(["Ano", "Trimestre", "grupo"]):
    if sub["wt"].sum() == 0: continue
    rate = np.average(sub["em_regular"], weights=sub["wt"])
    rows.append({"Ano": int(a), "Trim": int(q), "grupo": g,
                  "em_rate": rate, "n": len(sub),
                  "ano_trim": f"{int(a)}Q{int(q)}"})

agg = pd.DataFrame(rows).sort_values(["Ano", "Trim", "grupo"])
agg.to_csv(OUT_DIR / "C32_em_attendance_by_renda.csv", index=False)
print(f"\nSaved {OUT_DIR / 'C32_em_attendance_by_renda.csv'}", flush=True)
print(agg.to_string(index=False), flush=True)
# } ----
