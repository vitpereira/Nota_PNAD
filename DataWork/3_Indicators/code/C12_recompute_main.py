# -------------------------------------------------------------------------
# C12_recompute_main.py
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Recalibracao do indicador principal inter-anual. A regra de selecao
#   de trimestre de referencia agora prefere o primeiro Q>=2 (apos voltas
#   as aulas) e cai para Q1 (jan-mar) apenas se nao houver alternativa.
#   Aplicada a ambos t e t+1.
#
#   A logica de flags reproduz fielmente ._compute_indicator.do (Stata),
#   incluindo migracao EJA e a logica de "restante".
#
# Inputs:
#   ../../2_PanelBuild/tmp/pnadc_linked.dta  (raw panel, 8.6M rows)
#
# Outputs:
#   ../output/T1_brasil_inter_por_serie_ano.tex          (NEW, calibrada)
#   ../output/T1_brasil_inter_calibrated.csv             (CSV)
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
print(f"  Loaded {len(df):,} rows")

df = df[df["link_ok"] == 1].copy()
print(f"  link_ok==1: {len(df):,}")

def me_label(etc):
    if etc == 4:  return "EF iniciais"
    if etc == 5:  return "EF finais"
    if etc in (10, 11, 12): return "EM"
    if etc == 20: return "EJA EF"
    if etc == 21: return "EJA EM"
    return None

df["macroetapa"] = df["etapa_consolid"].map(me_label)

# Build "best ref per person-year": prefer earliest Q>=2, fallback Q1
def best_ref_table(d):
    d = d.copy()
    d["_is_q1"] = (d["Trimestre"] == 1).astype(int)
    d = d.sort_values(["person_id", "Ano", "_is_q1", "Trimestre"])
    d = d.drop_duplicates(subset=["person_id", "Ano"], keep="first")
    return d.drop(columns=["_is_q1"])

# For the t reference, we need kids enrolled in EF/EM regular (universe = etc in {4,5,10,11,12})
df_enrolled = df[df["etapa_consolid"].isin([4, 5, 10, 11, 12])].copy()
df_enrolled = df_enrolled[df_enrolled["serie"].notna()].copy()
print(f"  Enrolled in EF/EM regular: {len(df_enrolled):,}")

ref_t = best_ref_table(df_enrolled)
print(f"  Refs t (one per person-year, enrolled): {len(ref_t):,}")

# For the t+1 reference, we want ANY plausible state of the kid (could be
# evading; could be in EJA; etc.). Use the full df, filtered to idade 4-24
df_scope = df[df["idade"].between(4, 24)].copy()
ref_all = best_ref_table(df_scope)
print(f"  Refs t+1 (any in scope): {len(ref_all):,}")

# --- Build transitions ---
ref_t_use = ref_t.rename(columns={
    "Ano": "ano_t", "Trimestre": "trim_t", "serie": "serie_t",
    "freq_escola": "freq_t", "etapa_consolid": "etapa_t",
    "macroetapa": "macroetapa_t", "peso_v1028": "wt_t",
    "idade": "idade_t",
})[["person_id", "ano_t", "trim_t", "serie_t", "freq_t",
    "etapa_t", "macroetapa_t", "wt_t", "idade_t"]]
ref_t_use["ano_t1"] = ref_t_use["ano_t"] + 1

ref_t1_use = ref_all.rename(columns={
    "Ano": "ano_t1", "Trimestre": "trim_t1", "serie": "serie_t1",
    "freq_escola": "freq_t1", "etapa_consolid": "etapa_t1",
    "macroetapa": "macroetapa_t1",
})[["person_id", "ano_t1", "trim_t1", "serie_t1", "freq_t1",
    "etapa_t1", "macroetapa_t1"]]

t = ref_t_use.merge(ref_t1_use, on=["person_id", "ano_t1"], how="left")
print(f"\nTotal transitions: {len(t):,}")
print(f"  With freq_t1 observed: {t['freq_t1'].notna().sum():,}")

print(f"\ntrim_t1 distribution under new rule:")
print(t["trim_t1"].value_counts(dropna=False).sort_index())

# ============================================================
# Flags following ._compute_indicator.do exactly
# ============================================================

et   = t["etapa_t"]
et1  = t["etapa_t1"]
st   = t["serie_t"]
st1  = t["serie_t1"]
f1   = t["freq_t1"]

t["flag_evasao"]    = ((f1 != 1) & f1.notna()).astype(int)
t["flag_promocao"]  = 0
t["flag_repetencia"] = 0

# (a) Avanco de serie dentro da mesma etapa
mask = (f1 == 1) & (et1 == et) & (st1 == st + 1) & st.notna() & st1.notna()
t.loc[mask, "flag_promocao"] = 1

# (b) 9 EF (et=5, s=9) -> 1 EM (et=10)
mask = (f1 == 1) & (et == 5) & (st == 9) & (et1 == 10)
t.loc[mask, "flag_promocao"] = 1

# (c) 3 EM (et=12) -> superior
mask = (f1 == 1) & (et == 12) & (et1 > 12) & (et1 < 30)
t.loc[mask, "flag_promocao"] = 1

# (d) 5 EF iniciais (et=4, s=5) -> 6 EF finais (et=5, s=6)
mask = (f1 == 1) & (et == 4) & (st == 5) & (et1 == 5) & (st1 == 6)
t.loc[mask, "flag_promocao"] = 1

# Repetencia: same etapa, same serie
mask = (f1 == 1) & (et == et1) & (st == st1)
t.loc[mask, "flag_repetencia"] = 1

# Migration to EJA
t["flag_migracao_eja"] = (
    (f1 == 1) & et1.isin([20, 21]) & ~et.isin([20, 21])
).astype(int)

# _restante: enrolled but unclassified yet
restante = (
    (f1 == 1) &
    (t["flag_promocao"] == 0) &
    (t["flag_repetencia"] == 0) &
    (t["flag_evasao"] == 0) &
    (t["flag_migracao_eja"] == 0)
)
# Restante: if etapa advanced -> promocao
mask = restante & (et1 > et) & et1.notna()
t.loc[mask, "flag_promocao"] = 1
# Restante: same etapa, wrong serie progression -> repetencia
mask = restante & (et1 == et) & (st1 != st + 1) & st1.notna()
t.loc[mask, "flag_repetencia"] = 1

# Validation: sum should be ~1 within universe
t["flag_naoprog"] = (
    (t["flag_repetencia"] + t["flag_evasao"] + t["flag_migracao_eja"]) >= 1
).astype(int)
t["_total"] = (
    t["flag_promocao"] + t["flag_repetencia"] + t["flag_evasao"] + t["flag_migracao_eja"]
)

# Restrict universe: only observations with f_t1 measured (otherwise
# transitions are unobserved, not "no progression"). Also drop 2024 base
# (since 2025 PNADC not yet downloaded).
t = t[t["freq_t1"].notna()].copy()
t = t[t["ano_t"] <= 2023].copy()
print(f"\nFinal transitions (f1 observed, ano_t<=2023): {len(t):,}")

t["wt"] = t["wt_t"]

# Diagnostic: check identity by macroetapa-year
print("\nIdentity check (sum of flags) by macroetapa-year [should be ~1]:")
diag = t.groupby("macroetapa_t").apply(lambda g: np.average(g["_total"], weights=g.wt))
print(diag)

# Aggregate
grp = t.groupby(["ano_t", "macroetapa_t"])

def w_avg(g, col):
    return np.average(g[col], weights=g.wt)

agg = pd.DataFrame({
    "flag_promocao":      grp.apply(lambda g: w_avg(g, "flag_promocao")),
    "flag_repetencia":    grp.apply(lambda g: w_avg(g, "flag_repetencia")),
    "flag_evasao":        grp.apply(lambda g: w_avg(g, "flag_evasao")),
    "flag_migracao_eja":  grp.apply(lambda g: w_avg(g, "flag_migracao_eja")),
    "flag_naoprog":       grp.apply(lambda g: w_avg(g, "flag_naoprog")),
    "n_pessoa":           grp.size(),
}).reset_index()

agg.columns = ["ano_t", "macroetapa", "flag_promocao", "flag_repetencia",
               "flag_evasao", "flag_migracao_eja", "flag_naoprog", "n_pessoa"]

# Keep only main macroetapas
agg = agg[agg["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()

agg.to_csv(OUT_DIR / "T1_brasil_inter_calibrated.csv", index=False)
print(f"\nSaved CSV: {OUT_DIR / 'T1_brasil_inter_calibrated.csv'}")

# Print key years
for et_name in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n--- {et_name} ---")
    sub = agg[agg["macroetapa"] == et_name].sort_values("ano_t")
    for _, r in sub.iterrows():
        total = r.flag_promocao + r.flag_repetencia + r.flag_evasao + r.flag_migracao_eja
        print(f"  {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
              f"rep={r.flag_repetencia*100:.1f}% "
              f"evas={r.flag_evasao*100:.1f}% "
              f"eja={r.flag_migracao_eja*100:.1f}% "
              f"(sum={total*100:.1f}%) n={int(r.n_pessoa)}")
