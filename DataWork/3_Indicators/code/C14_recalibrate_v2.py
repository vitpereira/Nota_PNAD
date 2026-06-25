# -------------------------------------------------------------------------
# C14_recalibrate_v2.py
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Reformulacao das taxas de transicao inter-anual (rodada 2).
#
#   M1. Excluir Q4 e Q1. So Q2 e Q3 sao validas.
#   M2. Em t+1, usar a observacao com MAX(nivel) entre Q2-Q3.
#   M3. Migracao EJA reportada como categoria separada.
#   M4. Atrito (pessoa sem obs valida em Q2/Q3 de t+1) excluida.
#
# Inputs:
#   ../../2_PanelBuild/tmp/pnadc_linked.dta
#
# Outputs:
#   ../output/T1_brasil_inter_v2.csv
#   ../output/C14_transitions_v2.parquet
#   ../output/C14_attrition_rates.csv
#   ../output/C14_transition_validation.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np
import sys

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

KEEP = ["Ano", "Trimestre", "person_id", "etapa_consolid", "serie",
        "freq_escola", "idade", "peso_v1028", "link_ok"]

print(f"Reading {LINK}...", flush=True)
df, meta = pyreadstat.read_dta(str(LINK), usecols=KEEP)
print(f"  Loaded {len(df):,} rows", flush=True)

df = df[df["link_ok"] == 1].copy()
print(f"  link_ok==1: {len(df):,}", flush=True)

# Vectorized nivel computation
etc = df["etapa_consolid"]
ser = df["serie"]
nivel = np.full(len(df), np.nan)
m_efi = (etc == 4) & ser.between(1, 5)
m_eff = (etc == 5) & ser.between(6, 9)
m_em1 = (etc == 10)
m_em2 = (etc == 11)
m_em3 = (etc == 12)
nivel[m_efi] = ser[m_efi].values
nivel[m_eff] = ser[m_eff].values
nivel[m_em1] = 10.0
nivel[m_em2] = 11.0
nivel[m_em3] = 12.0
df["nivel"] = nivel

me = pd.Series(np.where(etc == 4, "EF iniciais",
                np.where(etc == 5, "EF finais",
                  np.where(etc.isin([10, 11, 12]), "EM",
                    np.where(etc == 20, "EJA EF",
                      np.where(etc == 21, "EJA EM", None))))), index=df.index)
df["macroetapa"] = me

# === M1: keep only Q2 and Q3 observations for transition computation ===
df_q23 = df[df["Trimestre"].isin([2, 3])].copy()
print(f"  Q2/Q3 obs only: {len(df_q23):,}", flush=True)

# ============================================================
# t reference: enrolled regular EF/EM, max(nivel) within Q2/Q3
# ============================================================
df_t = df_q23[
    df_q23["etapa_consolid"].isin([4, 5, 10, 11, 12]) &
    (df_q23["freq_escola"] == 1) &
    df_q23["nivel"].notna()
].copy()
print(f"  Universe in t (enrolled EF/EM, Q2/Q3): {len(df_t):,}", flush=True)

# For year t reference: pick obs with MAX nivel (tie: latest Trimestre)
df_t = df_t.sort_values(["person_id", "Ano", "nivel", "Trimestre"],
                       ascending=[True, True, False, False])
ref_t = df_t.drop_duplicates(subset=["person_id", "Ano"], keep="first").copy()
print(f"  Refs t (one per person-year): {len(ref_t):,}", flush=True)

# ============================================================
# t+1 reference: vectorized
# We need per (person, year):
#   - max(nivel) and the row that achieves it (for nivel_t1, serie_t1, etapa_t1)
#   - any obs in EJA (for migracao flag)
#   - latest-Trimestre obs for fallback freq_t1 / trim_t1
# ============================================================
print("Computing t+1 references (vectorized)...", flush=True)

# Subset: Q2/Q3 obs only, any status (already in df_q23)
df_t1 = df_q23.copy()

# For "ref with max nivel": sort and dedupe
df_reg = df_t1[df_t1["nivel"].notna()].copy()
df_reg = df_reg.sort_values(["person_id", "Ano", "nivel", "Trimestre"],
                            ascending=[True, True, False, False])
ref_reg = df_reg.drop_duplicates(subset=["person_id", "Ano"], keep="first")[
    ["person_id", "Ano", "nivel", "serie", "etapa_consolid", "freq_escola",
     "Trimestre", "macroetapa"]
].rename(columns={
    "nivel": "nivel_t1_reg", "serie": "serie_t1_reg",
    "etapa_consolid": "etapa_t1_reg", "freq_escola": "freq_t1_reg",
    "Trimestre": "trim_t1_reg", "macroetapa": "macroetapa_t1_reg",
})

# For "any EJA in t+1"
df_eja = df_t1[df_t1["etapa_consolid"].isin([20, 21])].copy()
has_eja = (df_eja.groupby(["person_id", "Ano"]).size() > 0).rename("any_eja_t1") \
            .reset_index()

# For latest obs in t+1 (fallback) - regardless of universe
df_latest = df_t1.sort_values(["person_id", "Ano", "Trimestre"],
                              ascending=[True, True, False])
ref_latest = df_latest.drop_duplicates(subset=["person_id", "Ano"], keep="first")[
    ["person_id", "Ano", "freq_escola", "Trimestre", "etapa_consolid", "serie"]
].rename(columns={
    "freq_escola": "freq_t1_late", "Trimestre": "trim_t1_late",
    "etapa_consolid": "etapa_t1_late", "serie": "serie_t1_late"
})

# Merge: prefer reg ref if exists; else use latest
agg = ref_latest.merge(ref_reg, on=["person_id", "Ano"], how="left")
agg = agg.merge(has_eja, on=["person_id", "Ano"], how="left")
agg["any_eja_t1"] = agg["any_eja_t1"].fillna(False)

# Final t+1 fields: prefer regular ref; if missing, use latest
agg["nivel_t1"]      = agg["nivel_t1_reg"]
agg["serie_t1"]      = agg["serie_t1_reg"].fillna(agg["serie_t1_late"])
agg["etapa_t1"]      = agg["etapa_t1_reg"].fillna(agg["etapa_t1_late"])
agg["freq_t1"]       = agg["freq_t1_reg"].fillna(agg["freq_t1_late"])
agg["trim_t1"]       = agg["trim_t1_reg"].fillna(agg["trim_t1_late"])
agg["macroetapa_t1"] = agg["macroetapa_t1_reg"]
agg = agg.rename(columns={"Ano": "ano_t1"})[
    ["person_id", "ano_t1", "nivel_t1", "serie_t1", "etapa_t1", "freq_t1",
     "trim_t1", "macroetapa_t1", "any_eja_t1"]
]
print(f"  T+1 candidate refs: {len(agg):,}", flush=True)

# Prepare ref_t for merge
ref_t = ref_t.rename(columns={
    "Ano": "ano_t", "Trimestre": "trim_t", "serie": "serie_t",
    "freq_escola": "freq_t", "etapa_consolid": "etapa_t",
    "macroetapa": "macroetapa_t", "peso_v1028": "wt_t",
    "idade": "idade_t", "nivel": "nivel_t"
})[["person_id", "ano_t", "trim_t", "serie_t", "freq_t",
    "etapa_t", "macroetapa_t", "nivel_t", "wt_t", "idade_t"]]
ref_t["ano_t1"] = ref_t["ano_t"] + 1

# Merge t with t+1
t = ref_t.merge(agg, on=["person_id", "ano_t1"], how="left")
print(f"\nTotal t transitions built: {len(t):,}", flush=True)
print(f"  With t+1 obs (any kind): {t['freq_t1'].notna().sum():,}", flush=True)
print(f"  Without t+1 obs (attrition): {t['freq_t1'].isna().sum():,}", flush=True)

# Drop 2024 (no 2025 data yet)
t = t[t["ano_t"] <= 2023].copy()

# Save full transitions table for downstream (incl. attrition)
t.to_parquet(OUT_DIR / "C14_transitions_v2.parquet", index=False)
print(f"Saved C14_transitions_v2.parquet ({len(t):,} rows)", flush=True)

# Attrition diagnostics
attrit = t.copy()
attrit["has_t1"] = attrit["freq_t1"].notna()
attrit_rate = attrit.groupby(["ano_t", "macroetapa_t"]).apply(
    lambda g: 1 - np.average(g.has_t1, weights=g.wt_t)).reset_index()
attrit_rate.columns = ["ano_t", "macroetapa", "atrito_rate"]
attrit_rate.to_csv(OUT_DIR / "C14_attrition_rates.csv", index=False)
print(f"Saved C14_attrition_rates.csv", flush=True)

# Sample for MAIN analysis: drop attrition
t_main = t[t["freq_t1"].notna()].copy()
print(f"\nMain analysis sample (with t+1 obs): {len(t_main):,}", flush=True)

# Flags
t_main["any_eja_t1"] = t_main["any_eja_t1"].astype(bool)
t_main["flag_migracao_eja"] = t_main["any_eja_t1"].astype(int)
t_main["flag_evasao"] = (
    (t_main["freq_t1"] == 0) & (~t_main["any_eja_t1"])
).astype(int)
t_main["flag_promocao"] = (
    (t_main["freq_t1"] == 1) &
    (~t_main["any_eja_t1"]) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] > t_main["nivel_t"])
).astype(int)
t_main["flag_repetencia"] = (
    (t_main["freq_t1"] == 1) &
    (~t_main["any_eja_t1"]) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] == t_main["nivel_t"])
).astype(int)
t_main["flag_naoprog"] = (
    (t_main["flag_repetencia"] + t_main["flag_evasao"]
     + t_main["flag_migracao_eja"]) >= 1
).astype(int)
t_main["_total"] = (t_main["flag_promocao"] + t_main["flag_repetencia"]
                    + t_main["flag_evasao"] + t_main["flag_migracao_eja"])
t_main["wt"] = t_main["wt_t"]

# Identity check
diag = t_main.groupby("macroetapa_t").apply(
    lambda g: np.average(g["_total"], weights=g.wt))
print("\nIdentity check (sum of flags) by macroetapa:", flush=True)
print(diag, flush=True)
diag.reset_index().to_csv(OUT_DIR / "C14_transition_validation.csv", index=False)

# Aggregate
grp = t_main.groupby(["ano_t", "macroetapa_t"])
agg_out = pd.DataFrame({
    "flag_promocao":      grp.apply(lambda g: np.average(g.flag_promocao, weights=g.wt)),
    "flag_repetencia":    grp.apply(lambda g: np.average(g.flag_repetencia, weights=g.wt)),
    "flag_evasao":        grp.apply(lambda g: np.average(g.flag_evasao, weights=g.wt)),
    "flag_migracao_eja":  grp.apply(lambda g: np.average(g.flag_migracao_eja, weights=g.wt)),
    "flag_naoprog":       grp.apply(lambda g: np.average(g.flag_naoprog, weights=g.wt)),
    "n_pessoa":           grp.size(),
}).reset_index()
agg_out.columns = ["ano_t", "macroetapa", "flag_promocao", "flag_repetencia",
                   "flag_evasao", "flag_migracao_eja", "flag_naoprog", "n_pessoa"]
agg_out = agg_out[agg_out["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()
agg_out.to_csv(OUT_DIR / "T1_brasil_inter_v2.csv", index=False)
print(f"\nSaved {OUT_DIR / 'T1_brasil_inter_v2.csv'}", flush=True)

for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n--- {et} ---", flush=True)
    sub = agg_out[agg_out["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub.iterrows():
        total = r.flag_promocao + r.flag_repetencia + r.flag_evasao + r.flag_migracao_eja
        print(f"  {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
              f"rep={r.flag_repetencia*100:.1f}% "
              f"evas={r.flag_evasao*100:.1f}% "
              f"eja={r.flag_migracao_eja*100:.1f}% "
              f"(sum={total*100:.1f}%) n={int(r.n_pessoa)}", flush=True)

print("\nDone.", flush=True)
