# -------------------------------------------------------------------------
# C33_micro_for_twfe.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Gera microdados individuais (1 linha por pessoa-trimestre) para
#   estimacao TWFE de matricula em EM regular em funcao de:
#     - tratamento por faixa de renda dom. per capita
#     - dummy post (anuncio dez/2023 OR implementacao mar/2024)
#   Grupos:
#     control: renda > 1/2 SM  (excluindo extremos para identificacao)
#     treat_low: 1/4 SM <= renda <= 1/2 SM
#     treat_extreme: renda < 1/4 SM
#
# Outputs:
#   ../output/C33_micro_em_15_19.parquet
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

SM = {2022: 1212, 2023: 1320, 2024: 1412, 2025: 1518}

# { 1. Load PNADC trimestral 2022-2025 ----
print("Loading PNADC trimestral 2022-2025...", flush=True)
frames = []
for y in [2022, 2023, 2024, 2025]:
    for q in [1, 2, 3, 4]:
        p = PD_TRI / f"pnadc_0{q}{y}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["UF", "UPA", "V1008", "V1014", "V2003",
                                          "Ano", "Trimestre",
                                          "V2001", "V2007", "V2009", "V2010",
                                          "V3002", "V3003A", "VD3004",
                                          "V403312", "V1028"])
        for c in ["V2009", "V2007", "V2010", "V3002", "V3003A", "VD3004",
                   "V1028", "V403312", "V2001"]:
            d[c] = pd.to_numeric(d[c], errors="coerce")
        d = d[d["V2009"].between(15, 19)]
        frames.append(d)
df = pd.concat(frames, ignore_index=True)
print(f"  obs 15-19: {len(df):,}", flush=True)
# } ----

# { 2. Compute renda_dom_pc ----
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
# } ----

# { 3. Merge ----
df["hh_yr_q"] = (df["UF"].astype(str) + "_" + df["UPA"].astype(str)
                  + "_" + df["V1008"].astype(str) + "_" + df["V1014"].astype(str)
                  + "_" + df["Ano"].astype(str) + "Q" + df["Trimestre"].astype(str))
df = df.merge(hh_renda_all[["hh_yr_q", "renda_pc"]], on="hh_yr_q", how="left")

df["hh_id"] = (df["UF"].astype(str) + "_" + df["UPA"].astype(str)
                + "_" + df["V1008"].astype(str) + "_" + df["V1014"].astype(str))

df["sm"] = df["Ano"].map(SM)
df["quarto_sm"] = df["sm"] / 4.0
df["meio_sm"]   = df["sm"] / 2.0
# } ----

# { 4. Define groups (mutually exclusive) ----
df = df.dropna(subset=["renda_pc"]).copy()
df["treat_extreme"] = (df["renda_pc"] < df["quarto_sm"]).astype(int)
df["treat_low"]     = ((df["renda_pc"] >= df["quarto_sm"]) &
                        (df["renda_pc"] <= df["meio_sm"])).astype(int)
df["control"]       = (df["renda_pc"] > df["meio_sm"]).astype(int)
df["grupo"] = np.where(df["treat_extreme"] == 1, "extreme",
              np.where(df["treat_low"] == 1, "low",
                       "control"))
# } ----

# { 5. Outcome and time vars ----
df["em_regular"] = ((df["V3002"] == 1) & (df["V3003A"] == 6)).astype(int)
df["em_any"]     = (df["V3002"] == 1).astype(int)
# Outcome para F16: frequenta escola OU ja completou EM (VD3004 >= 5)
df["escola_ou_em_completo"] = (
    (df["V3002"] == 1) | (df["VD3004"] >= 5)
).astype(int)
# Outcome principal PdM: matriculado em EM regular OU EJA EM OU ja concluiu EM
df["em_or_eja_or_done"] = (
    ((df["V3002"] == 1) & (df["V3003A"].isin([6, 7]))) |
    (df["VD3004"] >= 5)
).astype(int)

# Quarter index (continuous): 1 = 2022Q1, 16 = 2025Q4
df["q_idx"] = (df["Ano"] - 2022) * 4 + df["Trimestre"]
df["yr_q"]  = df["Ano"].astype(int).astype(str) + "Q" + df["Trimestre"].astype(int).astype(str)

# Post indicators
# Anuncio em dez/2023 (PL aprovado Camara 13/12, Senado 19/12)
# Trimestre 2023Q4 (Out-Dez 2023) covers the announcement.
# Choose: post_anuncio = (q_idx >= 8) ie 2023Q4
df["post_anuncio"] = (df["q_idx"] >= 8).astype(int)
# Implementacao primeira parcela em mar/2024 -> Q1/2024 e seguintes
df["post_implem"]  = (df["q_idx"] >= 9).astype(int)
# Expansao CadUnico em ago/2024 -> Q3/2024 e seguintes
df["post_expand"]  = (df["q_idx"] >= 11).astype(int)
# } ----

# { 6. Demograficos ----
df["sexo_f"] = (df["V2007"] == 2).astype(int)
df["preta_parda"] = df["V2010"].isin([2, 4]).astype(int)
df["idade"] = df["V2009"]
# } ----

# { 7. Save microdados ----
keep_cols = ["hh_id", "UF", "Ano", "Trimestre", "q_idx", "yr_q",
              "V2003", "V2009", "idade", "sexo_f", "preta_parda",
              "renda_pc", "quarto_sm", "meio_sm",
              "grupo", "treat_extreme", "treat_low", "control",
              "post_anuncio", "post_implem", "post_expand",
              "em_regular", "em_any", "escola_ou_em_completo",
              "em_or_eja_or_done", "VD3004", "V1028"]
micro = df[keep_cols].copy()
micro = micro.rename(columns={"V1028": "wt"})
micro["wt"] = pd.to_numeric(micro["wt"], errors="coerce").fillna(0)
micro = micro[micro["wt"] > 0]
micro.to_parquet(OUT_DIR / "C33_micro_em_15_19.parquet", index=False)
print(f"\nSaved C33_micro_em_15_19.parquet ({len(micro):,} rows)", flush=True)
print(micro.groupby("grupo").size())
# } ----
