# -------------------------------------------------------------------------
# C21_specC_minmax.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Spec C: min(nivel) em t {Q2,Q3,Q4} + max(nivel) em t+1 {Q1,Q2,Q3,Q4}
#
#   Combina conservadorismo em t (evita inflação por reporte antecipado em Q4)
#   com expansividade em t+1 (captura promoção mesmo se reportada tardiamente).
#
# Outputs:
#   ../output/T1_brasil_inter_v6_specC.csv
#   ../output/T1_brasil_inter_specC.tex
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

lookup = pd.read_parquet(OUT_DIR / "C19_v4_lookup.parquet")
for c in ["V3002", "V3014", "V3003", "V3003A", "V3006",
          "V2007", "V2009", "V1028"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")
lookup = lookup[lookup["V2009"].between(4, 24)].copy()
print(f"lookup age 4-24: {len(lookup):,}", flush=True)

ano = lookup["Ano"].values
v3 = lookup["V3003"].values
v3a = lookup["V3003A"].values
curso = np.full(len(lookup), 900.0)
mp = ano <= 2015
curso[mp & (v3 == 3)] = 100
curso[mp & (v3 == 4)] = 300
curso[mp & (v3 == 5)] = 200
curso[mp & (v3 == 6)] = 310
curso[mp & (v3 == 7)] = 210
mo = ano >= 2016
curso[mo & (v3a == 4)] = 100
curso[mo & (v3a == 5)] = 300
curso[mo & (v3a == 6)] = 200
curso[mo & (v3a == 7)] = 210
both_na = np.isnan(v3) & np.isnan(v3a)
curso[both_na] = np.nan
lookup["curso"] = curso

serie = lookup["V3006"].values
nivel = np.full(len(lookup), np.nan)
nivel[(curso == 100) & (serie >= 1) & (serie <= 9)] = serie[(curso == 100) & (serie >= 1) & (serie <= 9)]
nivel[(curso == 200) & (serie >= 1) & (serie <= 3)] = 9 + serie[(curso == 200) & (serie >= 1) & (serie <= 3)]
nivel[(curso == 210) & (serie >= 1) & (serie <= 4)] = 9 + serie[(curso == 210) & (serie >= 1) & (serie <= 4)]
lookup["nivel"] = nivel

me = np.full(len(lookup), None, dtype=object)
me[(nivel >= 1) & (nivel <= 5)] = "EF iniciais"
me[(nivel >= 6) & (nivel <= 9)] = "EF finais"
me[(nivel >= 10) & (nivel <= 13)] = "EM"
me[curso == 300] = "EJA EF"
me[curso == 310] = "EJA EM"
lookup["macroetapa"] = me
lookup["in_eja"] = ((curso == 300) | (curso == 310)).astype(int)
lookup["in_regular"] = (~np.isnan(nivel)).astype(int)
lookup["freq_zero"] = (lookup["V3002"] == 2).astype(int)
lookup["concluiu"] = (lookup["V3014"] == 1).astype(int)

# Merge link
link, _ = pyreadstat.read_dta(
    str(LINK),
    usecols=["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003",
              "person_id", "link_ok"]
)
link = link[link["link_ok"] == 1]
for c in ["UF", "UPA", "V1008", "V1014", "V2003"]:
    link[c] = link[c].astype(int)
    lookup[c] = lookup[c].astype(int)
merge_keys = ["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003"]
panel = link.merge(lookup, on=merge_keys, how="inner")
del link, lookup

# ============ Spec C: t in {Q2,Q3,Q4} MIN, t+1 in {Q1,Q2,Q3,Q4} MAX ============

# t window: Q2-Q4, take MIN nivel
sub_t = panel[panel["Trimestre"].isin([2, 3, 4])].copy()
reg_t = sub_t[sub_t["nivel"].notna()].copy()
# Sort ascending by nivel, get the LOWEST first
reg_t = reg_t.sort_values(["person_id", "Ano", "nivel", "Trimestre"],
                          ascending=[True, True, True, True])
ref_t = reg_t.drop_duplicates(subset=["person_id", "Ano"], keep="first")[
    ["person_id", "Ano", "nivel", "V3006", "curso",
     "macroetapa", "Trimestre", "V1028", "V2009", "V2007"]
].copy()
ref_t.columns = ["person_id", "Ano", "nivel_min", "serie_min", "curso_min",
                  "macroetapa_min", "trim_min", "wt_min", "idade_min", "sexo_min"]

# Aggregate flags from t window
agg_t = sub_t.groupby(["person_id", "Ano"]).agg(
    any_in_reg_t=("in_regular", "max"),
    any_in_eja_t=("in_eja", "max"),
).reset_index()
refs_t = ref_t.merge(agg_t, on=["person_id", "Ano"], how="outer")
print(f"refs_t: {len(refs_t):,}", flush=True)

# t+1 window: Q1-Q4, take MAX nivel
sub_t1 = panel.copy()  # all quarters
reg_t1 = sub_t1[sub_t1["nivel"].notna()].copy()
reg_t1 = reg_t1.sort_values(["person_id", "Ano", "nivel", "Trimestre"],
                            ascending=[True, True, False, False])
ref_t1 = reg_t1.drop_duplicates(subset=["person_id", "Ano"], keep="first")[
    ["person_id", "Ano", "nivel", "V3006", "curso",
     "macroetapa", "Trimestre"]
].copy()
ref_t1.columns = ["person_id", "Ano", "nivel_max", "serie_max", "curso_max",
                   "macroetapa_max", "trim_max"]

agg_t1 = sub_t1.groupby(["person_id", "Ano"]).agg(
    any_in_reg=("in_regular", "max"),
    any_in_eja=("in_eja", "max"),
    any_freq_zero=("freq_zero", "max"),
    any_concluiu=("concluiu", "max"),
).reset_index()
refs_t1 = ref_t1.merge(agg_t1, on=["person_id", "Ano"], how="outer")
print(f"refs_t1: {len(refs_t1):,}", flush=True)

del panel, sub_t, sub_t1, reg_t, reg_t1

# Build transitions
t = refs_t[refs_t["any_in_reg_t"] == 1].copy()
t = t.rename(columns={
    "Ano": "ano_t", "nivel_min": "nivel_t",
    "serie_min": "serie_t", "curso_min": "curso_t",
    "macroetapa_min": "macroetapa_t", "trim_min": "trim_t",
    "wt_min": "wt_t", "idade_min": "idade_t", "sexo_min": "sexo_t",
    "any_in_reg_t": "in_reg_t", "any_in_eja_t": "in_eja_t",
})
t["ano_t1"] = t["ano_t"] + 1

t1 = refs_t1.rename(columns={
    "Ano": "ano_t1", "nivel_max": "nivel_t1",
    "serie_max": "serie_t1", "curso_max": "curso_t1",
    "macroetapa_max": "macroetapa_t1", "trim_max": "trim_t1",
    "any_in_reg": "in_reg_t1", "any_in_eja": "in_eja_t1",
    "any_freq_zero": "freq_zero_t1", "any_concluiu": "concluiu_t1",
})[["person_id", "ano_t1", "nivel_t1", "serie_t1", "curso_t1",
    "macroetapa_t1", "trim_t1", "in_reg_t1", "in_eja_t1",
    "freq_zero_t1", "concluiu_t1"]]

trans = t.merge(t1, on=["person_id", "ano_t1"], how="left")
trans["has_t1"] = (trans["in_reg_t1"].fillna(0)
                    + trans["in_eja_t1"].fillna(0)
                    + trans["freq_zero_t1"].fillna(0)) > 0
trans = trans[trans["ano_t"] <= 2023].copy()
print(f"transitions: {len(trans):,}, with t+1: {trans['has_t1'].sum():,}", flush=True)

for c in ["in_reg_t1", "in_eja_t1", "freq_zero_t1", "concluiu_t1"]:
    trans[c] = trans[c].fillna(0).astype(int)
t_main = trans[trans["has_t1"]].copy()

t_main["flag_migracao_eja"] = (
    (t_main["in_eja_t1"] == 1) & (t_main["in_reg_t1"] == 0)
).astype(int)
t_main["flag_evasao_raw"] = (
    (t_main["freq_zero_t1"] == 1) &
    (t_main["in_reg_t1"] == 0) &
    (t_main["in_eja_t1"] == 0)
).astype(int)
t_main["flag_promocao_raw"] = (
    (t_main["in_reg_t1"] == 1) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] > t_main["nivel_t"])
).astype(int)
t_main["flag_repetencia_raw"] = (
    (t_main["in_reg_t1"] == 1) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] == t_main["nivel_t"])
).astype(int)

correction = (
    (t_main["nivel_t"].isin([12, 13])) &
    (t_main["concluiu_t1"] == 1) &
    (t_main["flag_evasao_raw"] == 1)
)
t_main["correction_applied"] = correction.astype(int)
t_main["flag_promocao"] = t_main["flag_promocao_raw"]
t_main["flag_repetencia"] = t_main["flag_repetencia_raw"]
t_main["flag_evasao"] = t_main["flag_evasao_raw"]
t_main.loc[correction, "flag_promocao"] = 1
t_main.loc[correction, "flag_evasao"] = 0
t_main["wt"] = t_main["wt_t"]

print(f"main: {len(t_main):,}, corrected: {t_main['correction_applied'].sum():,}", flush=True)

rows = []
for (a, m), g in t_main.groupby(["ano_t", "macroetapa_t"]):
    rows.append({
        "ano_t": a, "macroetapa": m,
        "flag_promocao": np.average(g.flag_promocao, weights=g.wt),
        "flag_repetencia": np.average(g.flag_repetencia, weights=g.wt),
        "flag_evasao": np.average(g.flag_evasao, weights=g.wt),
        "flag_migracao_eja": np.average(g.flag_migracao_eja, weights=g.wt),
        "n_pessoa": len(g),
    })
agg = pd.DataFrame(rows)
agg = agg[agg["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()
agg.to_csv(OUT_DIR / "T1_brasil_inter_v6_specC.csv", index=False)

print("\n=== Spec C (min(Q2-Q4) em t, max(Q1-Q4) em t+1) ===", flush=True)
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n  {et}:", flush=True)
    sub_agg = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub_agg.iterrows():
        total = r.flag_promocao + r.flag_repetencia + r.flag_evasao + r.flag_migracao_eja
        print(f"    {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
              f"rep={r.flag_repetencia*100:.1f}% "
              f"evas={r.flag_evasao*100:.1f}% "
              f"eja={r.flag_migracao_eja*100:.1f}% "
              f"sum={total*100:.1f}% n={int(r.n_pessoa)}", flush=True)
print("\nDone.", flush=True)
