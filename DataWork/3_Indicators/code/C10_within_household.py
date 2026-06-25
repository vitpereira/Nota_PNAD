# -------------------------------------------------------------------------
# C10_within_household.py
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Teste within-household para isolar o efeito calendario de Q1 de t+1
#   sobre repetencia/promocao, livre de vies de selecao.
#
#   Estrategia:
#     1. Identifica pessoas com obs em Q1 de y+1 E obs em Q2/Q3/Q4 de y+1
#     2. Tambem obs em algum trim de y (referencia de t)
#     3. Para cada pessoa, mede:
#        - serie em t (ultima obs em y)
#        - serie em Q1 de t+1 (jan-mar)
#        - serie em Q2+ de t+1 (>= abril)
#     4. Compara flag_repetencia/promocao usando Q1 vs Q2+ medicao,
#        within-person.
#
# Inputs:
#   ../tmp/pnadc_linked.dta (8.6M rows, person-quarter level)
#
# Outputs:
#   ../../3_Indicators/output/C10_within_person_*.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

KEEP = ["Ano", "Trimestre", "person_id", "etapa_consolid", "serie",
        "freq_escola", "idade", "peso_v1028", "link_ok"]

print(f"Reading {LINK}...")
df, meta = pyreadstat.read_dta(str(LINK), usecols=KEEP)
print(f"Loaded {len(df):,} rows")

# Keep only validated links
df = df[df["link_ok"] == 1].copy()
print(f"After link_ok==1: {len(df):,} rows")

# Universe: EF + EM regular. Use the SAME macroetapa derivation as B5.
# etapa_consolid is the harmonized code. Treat numbers:
#   we need EF anos iniciais, EF anos finais, EM, regardless of EJA codes
# Looking at the original derivation: macroetapa from etapa_consolid + serie.
# Let's filter by etapa_consolid in 4 (EF regular) and 6 (EM regular)
# These are the V3003A codes (post 2016). If the harmonized has it stored
# uniformly, this works. Otherwise we'd need to look at etapa.
print(f"\netapa_consolid unique values:")
print(df.etapa_consolid.value_counts(dropna=False).head(20))

# Correct etapa_consolid mapping (per B1_harmonize_pnadc.do):
#   4 = EF iniciais (serie 1-5)
#   5 = EF finais  (serie 6-9)
#   10 = EM 1, 11 = EM 2, 12 = EM 3
#   20 = EJA EF, 21 = EJA EM, 30 = pre-escola/alfab, others = superior
df = df[df["etapa_consolid"].isin([4, 5, 10, 11, 12])].copy()
print(f"After etapa_consolid in regular EF/EM: {len(df):,} rows")

# Drop missing serie/freq
df = df[df["serie"].notna() & df["freq_escola"].notna()].copy()
print(f"After non-missing serie/freq: {len(df):,} rows")

# Define macroetapa from etapa_consolid directly
def macroetapa_from_etc(etc):
    if etc == 4:
        return "EF iniciais"
    if etc == 5:
        return "EF finais"
    if etc in (10, 11, 12):
        return "EM"
    return None

df["macroetapa"] = df["etapa_consolid"].map(macroetapa_from_etc)

print("\nmacroetapa distribution:")
print(df.macroetapa.value_counts(dropna=False))

# ----- Reshape: for each (person, year), keep min and max trimester -----
# Build per-person-year summary: for each (person_id, Ano), capture
# the obs at Q1 and the obs at max trimester (Q2+ if present)

df_q1 = df[df["Trimestre"] == 1].copy()
df_q1["v_type"] = "Q1"

df_q2p = df[df["Trimestre"] >= 2].copy()
# Within (person, Ano), keep the EARLIEST trim>=2 to be closest to school year start
df_q2p = df_q2p.sort_values(["person_id", "Ano", "Trimestre"])
df_q2p = df_q2p.drop_duplicates(subset=["person_id", "Ano"], keep="first")
df_q2p["v_type"] = "Q2p"

# ----- Build the "year t" reference for each person -----
# For each person, last observation of year t (greatest Trimestre)
df_t = df.sort_values(["person_id", "Ano", "Trimestre"])
df_t_last = df_t.drop_duplicates(
    subset=["person_id", "Ano"], keep="last").copy()
df_t_last = df_t_last.rename(columns={
    "serie": "serie_t", "Ano": "ano_t",
    "Trimestre": "trim_t_last",
    "macroetapa": "macroetapa_t",
    "peso_v1028": "wt_t",
})[["person_id", "ano_t", "serie_t", "trim_t_last",
    "macroetapa_t", "wt_t", "idade"]]

# t+1 in Q1: serie when measured in Q1 of next year
df_q1_t1 = df_q1.rename(columns={
    "Ano": "ano_t1", "serie": "serie_t1_Q1",
    "freq_escola": "freq_t1_Q1", "macroetapa": "macroetapa_t1_Q1",
})[["person_id", "ano_t1", "serie_t1_Q1", "freq_t1_Q1", "macroetapa_t1_Q1"]]

# t+1 in Q2+: serie when measured in earliest Q>=2 of next year
df_q2p_t1 = df_q2p.rename(columns={
    "Ano": "ano_t1", "serie": "serie_t1_Q2p",
    "freq_escola": "freq_t1_Q2p", "Trimestre": "trim_t1_Q2p",
    "macroetapa": "macroetapa_t1_Q2p",
})[["person_id", "ano_t1", "serie_t1_Q2p", "freq_t1_Q2p",
    "trim_t1_Q2p", "macroetapa_t1_Q2p"]]

# Build year_t -> year_t1 transitions
df_t_last["ano_t1"] = df_t_last["ano_t"] + 1
trans = df_t_last.merge(df_q1_t1, on=["person_id", "ano_t1"], how="left")
trans = trans.merge(df_q2p_t1, on=["person_id", "ano_t1"], how="left")

print(f"\nTotal transitions built: {len(trans):,}")
print(f"  with Q1 obs of t+1:   {trans['serie_t1_Q1'].notna().sum():,}")
print(f"  with Q2+ obs of t+1:  {trans['serie_t1_Q2p'].notna().sum():,}")
print(f"  with BOTH (within-person sample): "
      f"{(trans['serie_t1_Q1'].notna() & trans['serie_t1_Q2p'].notna()).sum():,}")

# ----- Compute within-person comparison -----
within = trans[
    trans["serie_t1_Q1"].notna() &
    trans["serie_t1_Q2p"].notna() &
    trans["macroetapa_t"].notna() &
    trans["serie_t"].notna()
].copy()
print(f"\nWithin-person analyzable sample: {len(within):,}")

# Helper: detect cross-etapa promotion (9th EF -> 1st EM, or 3rd EM -> finished)
def is_cross_etapa_promotion(me_t, me_t1, s_t, s_t1):
    # EF finais kid in 9th grade → EM 1º ano in t+1
    if me_t == "EF finais" and s_t == 9 and me_t1 == "EM" and s_t1 == 1:
        return True
    # 3rd EM doesn't transition to a next series within EM in this universe
    # (would go to ensino superior; we don't track that here)
    return False

# Flags under Q1 measurement of t+1
within["prom_Q1"]  = (
    (within["freq_t1_Q1"] == 1) &
    (
        (within["serie_t1_Q1"] == within["serie_t"] + 1) |
        within.apply(lambda r: is_cross_etapa_promotion(
            r["macroetapa_t"], r["macroetapa_t1_Q1"],
            r["serie_t"], r["serie_t1_Q1"]), axis=1)
    )
).astype(int)
within["rep_Q1"]   = ((within["freq_t1_Q1"] == 1) &
                     (within["serie_t1_Q1"] == within["serie_t"]) &
                     (within["macroetapa_t1_Q1"] == within["macroetapa_t"])
                     ).astype(int)
within["evas_Q1"]  = (within["freq_t1_Q1"] == 0).astype(int)

# Flags under Q2+ measurement of t+1
within["prom_Q2p"] = (
    (within["freq_t1_Q2p"] == 1) &
    (
        (within["serie_t1_Q2p"] == within["serie_t"] + 1) |
        within.apply(lambda r: is_cross_etapa_promotion(
            r["macroetapa_t"], r["macroetapa_t1_Q2p"],
            r["serie_t"], r["serie_t1_Q2p"]), axis=1)
    )
).astype(int)
within["rep_Q2p"]  = ((within["freq_t1_Q2p"] == 1) &
                     (within["serie_t1_Q2p"] == within["serie_t"]) &
                     (within["macroetapa_t1_Q2p"] == within["macroetapa_t"])
                     ).astype(int)
within["evas_Q2p"] = (within["freq_t1_Q2p"] == 0).astype(int)

# Year of base
within["ano_base"] = within["ano_t"]

# Summary by macroetapa (pooled years, then by year)
def summary(g):
    w = g["wt_t"]
    out = pd.Series({
        "n": len(g),
        "prom_Q1":   np.average(g["prom_Q1"],  weights=w),
        "rep_Q1":    np.average(g["rep_Q1"],   weights=w),
        "evas_Q1":   np.average(g["evas_Q1"],  weights=w),
        "prom_Q2p":  np.average(g["prom_Q2p"], weights=w),
        "rep_Q2p":   np.average(g["rep_Q2p"],  weights=w),
        "evas_Q2p":  np.average(g["evas_Q2p"], weights=w),
    })
    return out

print("\n=== WITHIN-PERSON: medido em Q1 vs Q2+ de t+1 (pooled 2012-2023) ===")
print(f"{'macroetapa':<14} | {'n':>7} | "
      f"{'prom Q1':>8} {'prom Q2+':>8} | "
      f"{'rep Q1':>7} {'rep Q2+':>7} | "
      f"{'evas Q1':>8} {'evas Q2+':>8}")
print("-" * 95)
for et in ["EF iniciais", "EF finais", "EM"]:
    g = within[within["macroetapa_t"] == et]
    if len(g) == 0:
        continue
    s = summary(g)
    print(f"{et:<14} | {int(s['n']):>7} | "
          f"{s['prom_Q1']*100:>7.1f}% {s['prom_Q2p']*100:>7.1f}% | "
          f"{s['rep_Q1']*100:>6.1f}% {s['rep_Q2p']*100:>6.1f}% | "
          f"{s['evas_Q1']*100:>7.1f}% {s['evas_Q2p']*100:>7.1f}%")

# Save full
within_summary = within.groupby(["ano_base", "macroetapa_t"]).apply(summary).reset_index()
within_summary.to_csv(OUT_DIR / "C10_within_person_by_year.csv", index=False)
print(f"\nSaved {OUT_DIR / 'C10_within_person_by_year.csv'}")

# By trim_t1_Q2p value (Q2 vs Q3 vs Q4): does the answer depend on which?
print("\n=== Q2+ measurement, broken by which Q (2/3/4) ===")
for et in ["EF iniciais", "EF finais", "EM"]:
    g = within[within["macroetapa_t"] == et].copy()
    if len(g) == 0:
        continue
    print(f"\n--- {et} ---")
    print(f"{'trim_t1':>7} | {'n':>6} | {'prom':>6} {'rep':>6} {'evas':>6}")
    for tq in [2, 3, 4]:
        gt = g[g["trim_t1_Q2p"] == tq]
        if len(gt) == 0:
            continue
        w = gt["wt_t"]
        print(f"{tq:>7} | {len(gt):>6} | "
              f"{np.average(gt['prom_Q2p'], weights=w)*100:>5.1f}% "
              f"{np.average(gt['rep_Q2p'], weights=w)*100:>5.1f}% "
              f"{np.average(gt['evas_Q2p'], weights=w)*100:>5.1f}%")

# ----- Direct discordance check: for same person, what fraction of the time
# does the Q1 measurement say "repetencia" but the Q2+ measurement say something
# else (and vice versa)? -----
print("\n=== Discordancia entre medicoes Q1 e Q2+ (within-person) ===")
within["disc_rep_Q1_only"]   = ((within["rep_Q1"] == 1) & (within["rep_Q2p"] == 0)).astype(int)
within["disc_rep_Q2p_only"]  = ((within["rep_Q1"] == 0) & (within["rep_Q2p"] == 1)).astype(int)
within["disc_prom_Q1_only"]  = ((within["prom_Q1"] == 1) & (within["prom_Q2p"] == 0)).astype(int)
within["disc_prom_Q2p_only"] = ((within["prom_Q1"] == 0) & (within["prom_Q2p"] == 1)).astype(int)
within["disc_evas_Q1_only"]  = ((within["evas_Q1"] == 1) & (within["evas_Q2p"] == 0)).astype(int)
within["disc_evas_Q2p_only"] = ((within["evas_Q1"] == 0) & (within["evas_Q2p"] == 1)).astype(int)

print(f"{'macroetapa':<14} | "
      f"{'rep Q1 only':>11} {'rep Q2+ only':>13} | "
      f"{'prom Q1 only':>12} {'prom Q2+ only':>14} | "
      f"{'evas Q1 only':>12} {'evas Q2+ only':>14}")
for et in ["EF iniciais", "EF finais", "EM"]:
    g = within[within["macroetapa_t"] == et]
    if len(g) == 0:
        continue
    w = g["wt_t"]
    print(f"{et:<14} | "
          f"{np.average(g['disc_rep_Q1_only'],  weights=w)*100:>10.2f}% "
          f"{np.average(g['disc_rep_Q2p_only'], weights=w)*100:>12.2f}% | "
          f"{np.average(g['disc_prom_Q1_only'], weights=w)*100:>11.2f}% "
          f"{np.average(g['disc_prom_Q2p_only'],weights=w)*100:>13.2f}% | "
          f"{np.average(g['disc_evas_Q1_only'], weights=w)*100:>11.2f}% "
          f"{np.average(g['disc_evas_Q2p_only'],weights=w)*100:>13.2f}%")

print("\nDone.")
