# -------------------------------------------------------------------------
# C31_em_attendance_by_bfa.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Constroi serie trimestral 2022Q1-2024Q4 de matricula em EM regular
#   entre adolescentes 15-17 anos, dividida em 3 grupos:
#     - Bolsa Familia (BFA): qualquer membro do HH com V5002A=1 em V5
#     - CadUnico sem BFA: HH sem BFA observado AND renda_dom_pc <= 1/2 SM
#     - Fora do CadUnico: HH sem BFA observado AND renda_dom_pc > 1/2 SM
#
# Inputs:
#   ../../1_DownloadPNADC/tmp/pnad_parsed/pnadc_{TT}{ANO}.parquet (2022-2024)
#   PNADC Anual V5: pnadc_v5_{ANO}.parquet (BFA receipt)
#
# Outputs:
#   ../output/C31_em_attendance_by_bfa.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
V5_DIR = Path("C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Novo_plano/tmp/v3/pnad_raw/parsed")
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# Salario minimo R$/mes
SM = {2022: 1212, 2023: 1320, 2024: 1412, 2025: 1518}

# { 1. Load V5 e construir HH-level BFA flag por ano ----
print("Loading V5...", flush=True)
v5_frames = []
for y in [2022, 2023, 2024]:
    d = pd.read_parquet(V5_DIR / f"pnadc_v5_{y}.parquet",
                         columns=["UF", "UPA", "V1008", "V1014", "V5002A"])
    d["V5002A"] = pd.to_numeric(d["V5002A"], errors="coerce")
    d["Ano_v5"] = y
    v5_frames.append(d)
v5 = pd.concat(v5_frames, ignore_index=True)
v5["hh"] = (v5["UF"].astype(str) + "_" + v5["UPA"].astype(str)
            + "_" + v5["V1008"].astype(str) + "_" + v5["V1014"].astype(str))

# HH-Ano: any V5002A=1? all V5002A=2?
hh_bfa_year = (v5.groupby(["hh", "Ano_v5"])
                .agg(any_bfa=("V5002A", lambda x: (x == 1).any()),
                     any_obs=("V5002A", lambda x: x.notna().any())))
hh_bfa_year = hh_bfa_year.reset_index()
hh_bfa_year["any_bfa"] = hh_bfa_year["any_bfa"].astype(int)
hh_bfa_year["any_obs"] = hh_bfa_year["any_obs"].astype(int)
print(f"  HH-Ano with V5 obs: {len(hh_bfa_year):,}", flush=True)

# Forward/backward fill BFA status by HH (use V5 of any year if needed)
# Aggregate to HH-level: BFA flag = HH ever observed with BFA = 1, else if observed
# with all V5002A=2 = 0, else NA
hh_flag = (hh_bfa_year.groupby("hh")
            .agg(ever_bfa=("any_bfa", "max"),
                 ever_obs=("any_obs", "max"))
            .reset_index())
hh_flag["bfa_status"] = np.where(hh_flag["ever_bfa"] == 1, "BFA",
                       np.where(hh_flag["ever_obs"] == 1, "no_BFA",
                                "unknown"))
print("HH bfa_status counts:", hh_flag["bfa_status"].value_counts().to_dict(), flush=True)
# } ----

# { 2. Load PNADC trimestral 2022-2025 ----
print("\nLoading PNADC trimestral 2022-2025...", flush=True)
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
        # Filter age 15-24 (will be split into 3 faixas below)
        d = d[d["V2009"].between(15, 24)]
        frames.append(d)
df = pd.concat(frames, ignore_index=True)
print(f"  EM-age obs 2022-2024: {len(df):,}", flush=True)
# } ----

# { 3. Renda domiciliar per capita por HH-trimestre ----
df["renda_ind"] = df["V403312"].fillna(0)
df["hh"] = (df["UF"].astype(str) + "_" + df["UPA"].astype(str)
            + "_" + df["V1008"].astype(str) + "_" + df["V1014"].astype(str))
df["hh_yr_q"] = df["hh"] + "_" + df["Ano"].astype(str) + "Q" + df["Trimestre"].astype(str)

# Sum renda_ind per HH-Trimestre to get renda_dom_total — BUT we need all HH members
# We only have age 15-17 here. Renda_dom_pc requires all members.
# Solution: re-read full PNADC for renda_dom calculation, then merge in.
# } ----

# { 3b. Re-load to compute renda_dom_pc properly ----
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

# { 4. Merge BFA status and renda_pc onto EM-age df ----
df = df.merge(hh_flag[["hh", "bfa_status"]], on="hh", how="left")
df["bfa_status"] = df["bfa_status"].fillna("unknown")
df = df.merge(hh_renda_all[["hh_yr_q", "renda_pc"]], on="hh_yr_q", how="left")

# Salario minimo do ano
df["sm"] = df["Ano"].map(SM)
df["meio_sm"] = df["sm"] / 2.0

# Classify final group
def classify(row):
    if row["bfa_status"] == "BFA":
        return "Bolsa Familia"
    if row["bfa_status"] == "no_BFA":
        if pd.notna(row["renda_pc"]) and row["renda_pc"] <= row["meio_sm"]:
            return "CadUnico (sem BFA)"
        elif pd.notna(row["renda_pc"]):
            return "Fora do CadUnico"
    # unknown V5 status: classify by income only (proxy)
    if pd.notna(row["renda_pc"]) and row["renda_pc"] <= row["meio_sm"]:
        return "CadUnico (sem BFA)"
    return "Fora do CadUnico"

print("\nClassifying groups...", flush=True)
df["grupo"] = df.apply(classify, axis=1)
print(df["grupo"].value_counts(), flush=True)
# } ----

# { 5. Faixa etaria ----
def faixa(a):
    if 15 <= a <= 17: return "15-17"
    if 18 <= a <= 20: return "18-20"
    if 21 <= a <= 24: return "21-24"
    return None
df["faixa"] = df["V2009"].apply(faixa)
df = df[df["faixa"].notna()].copy()
# } ----

# { 6. Compute weighted enrollment rate in regular EM by group x trim x faixa ----
df["em_regular"] = ((df["V3002"] == 1) & (df["V3003A"] == 6)).astype(int)

# Weight: V1028
df["wt"] = df["V1028"].fillna(0)

rows = []
for (a, q, g, f), sub in df.groupby(["Ano", "Trimestre", "grupo", "faixa"]):
    if sub["wt"].sum() == 0: continue
    rate = np.average(sub["em_regular"], weights=sub["wt"])
    rows.append({"Ano": int(a), "Trim": int(q), "grupo": g, "faixa": f,
                  "em_rate": rate, "n": len(sub),
                  "ano_trim": f"{int(a)}Q{int(q)}"})

agg = pd.DataFrame(rows).sort_values(["faixa", "Ano", "Trim", "grupo"])
agg.to_csv(OUT_DIR / "C31_em_attendance_by_bfa.csv", index=False)
print(f"\nSaved {OUT_DIR / 'C31_em_attendance_by_bfa.csv'}", flush=True)
print(agg.to_string(index=False), flush=True)
# } ----
