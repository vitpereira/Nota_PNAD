# -------------------------------------------------------------------------
# C30_abandono_v5_corrected.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Recalcula abandono intra-ano APLICANDO A CORREÇÃO V3014.
#
#   Bug identificado em C15_abandono_fullyear.py e C22b_abandono_rev.py:
#   alunos do 3o EM (nivel=12) ou 4o EM tecnico (nivel=13) que concluiram
#   o ano letivo (V3014=1 em alguma obs do ano) e param de estudar em Q4
#   ESTAVAM SENDO CONTADOS COMO ABANDONO. Isso eh ERRADO --- eles
#   concluiram, nao abandonaram.
#
#   Esta versao:
#     1) Identifica concluintes terminais (nivel_first in [12,13] AND
#        any V3014=1 in year)
#     2) Exclui esses da contagem de abandono (mesmo se V3002=2 em Q4)
#     3) Mantem todos os outros criterios identicos a C15
#
# Inputs:
#   ../../2_PanelBuild/tmp/pnadc_linked.dta   (panel)
#   ../output/C19_v4_lookup.parquet           (V3014 + nivel)
#
# Outputs:
#   ../output/T_abandono_v5_corrected.csv
#   ../output/T_abandono_v5_diagnostico.csv  (comparacao com sem correcao)
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# { 1. Load lookup (has V3014, nivel) ----
print("Loading lookup...", flush=True)
lookup = pd.read_parquet(OUT_DIR / "C19_v4_lookup.parquet",
                          columns=["UF", "UPA", "V1008", "V1014", "V2003",
                                   "Ano", "Trimestre", "V3002", "V3014",
                                   "V3003", "V3003A", "V3006", "V2009"])
for c in ["V3002", "V3014", "V3003", "V3003A", "V3006", "V2009"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")
lookup = lookup[lookup["V2009"].between(4, 24)].copy()

# Build curso, nivel
ano = lookup["Ano"].values; v3 = lookup["V3003"].values; v3a = lookup["V3003A"].values
curso = np.full(len(lookup), 900.0)
mp = ano <= 2015
curso[mp & (v3 == 3)] = 100; curso[mp & (v3 == 4)] = 300
curso[mp & (v3 == 5)] = 200; curso[mp & (v3 == 6)] = 310; curso[mp & (v3 == 7)] = 210
mo = ano >= 2016
curso[mo & (v3a == 4)] = 100; curso[mo & (v3a == 5)] = 300
curso[mo & (v3a == 6)] = 200; curso[mo & (v3a == 7)] = 210
curso[np.isnan(v3) & np.isnan(v3a)] = np.nan
lookup["curso"] = curso

serie = lookup["V3006"].values
nivel = np.full(len(lookup), np.nan)
nivel[(curso == 100) & (serie >= 1) & (serie <= 9)] = serie[(curso == 100) & (serie >= 1) & (serie <= 9)]
nivel[(curso == 200) & (serie >= 1) & (serie <= 3)] = 9 + serie[(curso == 200) & (serie >= 1) & (serie <= 3)]
nivel[(curso == 210) & (serie >= 1) & (serie <= 4)] = 9 + serie[(curso == 210) & (serie >= 1) & (serie <= 4)]
lookup["nivel"] = nivel
lookup["concluiu"] = (lookup["V3014"] == 1).astype(int)
# } ----

# { 2. Load linked panel ----
print("Loading panel...", flush=True)
df, _ = pyreadstat.read_dta(str(LINK),
    usecols=["person_id", "Ano", "Trimestre", "UF", "UPA", "V1008", "V1014",
              "V2003", "freq_escola", "etapa_consolid", "serie",
              "peso_v1028", "link_ok"])
df = df[df["link_ok"] == 1].copy()
df = df[df["person_id"].astype(str).str.strip() != ""].copy()
print(f"  Panel: {len(df):,}", flush=True)
# } ----

# { 3. Merge V3014/nivel onto panel ----
for c in ["UF", "UPA", "V1008", "V1014", "V2003"]:
    df[c] = df[c].astype(int)
    lookup[c] = lookup[c].astype(int)
merge_keys = ["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003"]
panel = df.merge(lookup[merge_keys + ["nivel", "concluiu", "curso"]],
                  on=merge_keys, how="left")
del df, lookup
print(f"  After merge: {len(panel):,}", flush=True)
# } ----

# { 4. Macroetapa label ----
etc = panel["etapa_consolid"]
me = pd.Series(np.where(etc == 4, "EF iniciais",
                np.where(etc == 5, "EF finais",
                  np.where(etc.isin([10, 11, 12]), "EM",
                    np.where(etc == 20, "EJA EF",
                      np.where(etc == 21, "EJA EM", None))))), index=panel.index)
panel["macroetapa"] = me
# } ----

# { 5. Identify persons with all 4 quarters in same year ----
trims = panel.groupby(["person_id", "Ano"])["Trimestre"].nunique()
full4 = trims[trims == 4].reset_index()[["person_id", "Ano"]]
print(f"  Person-years with full Q1-Q4: {len(full4):,}", flush=True)
df_full = panel.merge(full4, on=["person_id", "Ano"], how="inner")
print(f"  Obs in full-coverage: {len(df_full):,}", flush=True)
# } ----

# { 6. Build Q1 universe and Q4 outcome ----
df_q1 = df_full[df_full["Trimestre"] == 1].copy()
df_q1 = df_q1[df_q1["etapa_consolid"].isin([4, 5, 10, 11, 12])]
df_q1 = df_q1[df_q1["freq_escola"] == 1]

df_q4 = df_full[df_full["Trimestre"] == 4][["person_id", "Ano", "freq_escola",
                                              "etapa_consolid", "serie"]].copy()
df_q4 = df_q4.rename(columns={"freq_escola": "freq_q4",
                                "etapa_consolid": "etapa_q4",
                                "serie": "serie_q4"})

# Aggregate over year: max(concluiu), max(nivel) over Q1-Q4
year_agg = (df_full.groupby(["person_id", "Ano"], as_index=False)
              .agg(concluiu_any=("concluiu", "max"),
                   nivel_max=("nivel", "max")))

abandono = (df_q1.merge(df_q4, on=["person_id", "Ano"], how="left")
                  .merge(year_agg, on=["person_id", "Ano"], how="left"))
# } ----

# { 7. Define abandono SEM correcao (legacy) ----
abandono["flag_abandono_raw"] = (abandono["freq_q4"] == 0).astype(int)
# } ----

# { 8. Define abandono COM correcao V3014 ----
# Conclusao terminal: nivel_max in {12, 13} AND concluiu_any=1
# Esses NAO sao abandono (concluiram)
is_terminal_concluinte = (
    abandono["nivel_max"].isin([12.0, 13.0]) &
    (abandono["concluiu_any"] == 1)
)
abandono["concluinte_terminal"] = is_terminal_concluinte.astype(int)

# Abandono corrigido: igual a raw, EXCETO se for concluinte terminal
abandono["flag_abandono"] = abandono["flag_abandono_raw"].copy()
abandono.loc[is_terminal_concluinte, "flag_abandono"] = 0

# EJA intra (mantido)
abandono["flag_eja_intra"] = abandono["etapa_q4"].isin([20, 21]).astype(int)
# } ----

# { 9. Aggregate ----
abandono["wt"] = abandono["peso_v1028"]
grp = abandono.groupby(["Ano", "macroetapa"])
rows = []
for (a, m), g in grp:
    rows.append({
        "ano_t": int(a), "macroetapa": m,
        "flag_abandono_raw":   np.average(g.flag_abandono_raw,   weights=g.wt),
        "flag_abandono":       np.average(g.flag_abandono,       weights=g.wt),
        "flag_eja_intra":      np.average(g.flag_eja_intra,      weights=g.wt),
        "pct_concluinte_term": np.average(g.concluinte_terminal, weights=g.wt),
        "n": int(len(g)),
    })
agg = pd.DataFrame(rows)
agg = agg[agg["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()
agg = agg.sort_values(["macroetapa", "ano_t"])

# Save raw + corrected
agg.to_csv(OUT_DIR / "T_abandono_v5_diagnostico.csv", index=False)

# Save only corrected version (for figure)
keep = agg[["ano_t", "macroetapa", "flag_abandono", "flag_eja_intra", "n"]]
keep.to_csv(OUT_DIR / "T_abandono_v5_corrected.csv", index=False)
print(f"\nSaved T_abandono_v5_corrected.csv ({len(keep)} rows)", flush=True)
# } ----

# { 10. Print summary ----
print("\n=== DIAGNOSTICO (RAW vs CORRECTED) ===\n")
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"--- {et} ---")
    print(f"{'Ano':>5} {'Raw':>7} {'Corr':>7} {'Diff':>7} {'%Concl':>7} {'N':>7}")
    sub = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub.iterrows():
        diff = r.flag_abandono_raw - r.flag_abandono
        print(f"{int(r.ano_t):>5} {r.flag_abandono_raw*100:>6.1f}% "
              f"{r.flag_abandono*100:>6.1f}% {diff*100:>6.1f}pp "
              f"{r.pct_concluinte_term*100:>6.1f}% {int(r.n):>7,}")
    print()
# } ----
