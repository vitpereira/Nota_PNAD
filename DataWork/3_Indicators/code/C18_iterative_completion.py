# -------------------------------------------------------------------------
# C18_iterative_completion.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Compara tres taxas de conclusao do EF e do EM:
#     A. INEP-projetada: simulacao de coorte aplicando as taxas de
#        transicao do INEP por serie e ano de forma iterativa.
#     B. PNADC observada: percentual de jovens de 19-24 anos com
#        VD3004 indicando conclusao do EF ou do EM, por ano da PNADC.
#     C. PNADC-projetada: mesma simulacao de coorte, com taxas medias
#        da PNADC (Tabela 1 corrigida v3, media 2017-2019 ex-COVID).
#
#   Pergunta: as taxas do INEP sao consistentes com a conclusao
#   observada na PNADC? Se nao, a divergencia indica que algum
#   componente do fluxo (evasao, repetencia) esta mal medido.
#
# Inputs:
#   ../../4_INEP_Comparison/output/inep_transicao_long.csv
#   ../../1_DownloadPNADC/tmp/pnad_parsed/pnadc_*.parquet  (VD3004, idade)
#   ../output/T1_brasil_inter_v3_corrected.csv             (taxas v3)
#
# Outputs:
#   ../output/T7_iterative_completion.csv
#   ../output/T7_iterative_completion.tex
#   ../../5_Figures/output/F9_completion_comparison.pdf
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
INEP = ROOT / "DataWork/4_INEP_Comparison/output/inep_transicao_long.csv"
PARSED_DIR = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
PNADC_T1_V3 = ROOT / "DataWork/3_Indicators/output/T1_brasil_inter_v3_corrected.csv"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"
FIG_DIR = ROOT / "DataWork/5_Figures/output"

# ===========================================================
# Step 1: Load INEP rates
# ===========================================================
print("Loading INEP transition rates...", flush=True)
inep = pd.read_csv(INEP)
inep = inep[inep["unidade"] == "Brasil"].copy()
print(f"  {len(inep):,} rows", flush=True)

# Filter to per-series rates (not aggregated)
series_codes = ["EF_1", "EF_2", "EF_3", "EF_4", "EF_5", "EF_6", "EF_7", "EF_8", "EF_9",
                "EM_1", "EM_2", "EM_3"]
inep = inep[inep["etapa"].isin(series_codes)].copy()

# Pivot: index = (etapa, ano_t), columns = indicador
inep_w = inep.pivot_table(
    index=["etapa", "ano_t"], columns="indicador", values="valor",
    aggfunc="first"
).reset_index()

# Convert from % to fraction
for c in ["promocao", "repetencia", "evasao", "migracao_eja"]:
    if c in inep_w.columns:
        inep_w[c] = inep_w[c] / 100.0

print(f"  INEP wide: {len(inep_w):,}", flush=True)
print(inep_w.head(), flush=True)

# Build a function to get rates for (etapa, year)
def get_inep_rates(etapa, year):
    """Returns (p, r, e, m) for the given etapa and year.
    Falls back to nearest available year if not present."""
    sub = inep_w[(inep_w["etapa"] == etapa)].copy()
    if len(sub) == 0:
        return None
    # exact
    exact = sub[sub["ano_t"] == year]
    if len(exact) == 1:
        r = exact.iloc[0]
        return (r["promocao"], r["repetencia"], r["evasao"],
                r.get("migracao_eja", 0))
    # closest
    sub["dist"] = (sub["ano_t"] - year).abs()
    sub = sub.sort_values("dist")
    r = sub.iloc[0]
    return (r["promocao"], r["repetencia"], r["evasao"],
            r.get("migracao_eja", 0))

# ===========================================================
# Step 2: Simulation of cohort - INEP rates
# ===========================================================
def simulate_cohort(rate_fn, year_start, n_years=18, use_avg=False, year_avg_start=2014, year_avg_end=2019):
    """
    Simulate 100 kids starting EF_1 in year_start.
    Apply rates iteratively for n_years.
    Returns: dict with cumulative outcomes.

    If use_avg=True, rates are averaged across years_avg_start..year_avg_end.
    """
    series_order = ["EF_1", "EF_2", "EF_3", "EF_4", "EF_5",
                    "EF_6", "EF_7", "EF_8", "EF_9",
                    "EM_1", "EM_2", "EM_3"]
    K = len(series_order)  # 12 series
    pop = np.zeros(K)  # current stock by series
    pop[0] = 100.0  # 100 kids start at EF_1
    completed_ef = 0
    completed_em = 0
    evaded_total = 0
    migrated_eja = 0

    for t in range(n_years):
        new_pop = np.zeros(K)
        yr = year_start + t
        for s in range(K):
            if pop[s] == 0:
                continue
            if use_avg:
                # Average rates over a stable period
                rates_list = []
                for y_avg in range(year_avg_start, year_avg_end + 1):
                    rt = rate_fn(series_order[s], y_avg)
                    if rt is not None:
                        rates_list.append(rt)
                if not rates_list:
                    continue
                p = np.mean([r[0] for r in rates_list])
                r_rate = np.mean([r[1] for r in rates_list])
                e = np.mean([r[2] for r in rates_list])
                m = np.mean([r[3] for r in rates_list])
            else:
                rates = rate_fn(series_order[s], yr)
                if rates is None:
                    continue
                p, r_rate, e, m = rates

            n_here = pop[s]
            # Promoted
            promoted = n_here * p
            if s == 8:  # EF_9 promoted -> EM_1 AND counts as EF completion
                new_pop[9] += promoted
                completed_ef += promoted
            elif s == 11:  # EM_3 promoted = EM completion
                completed_em += promoted
                # Also count as EF completion (they finished EF earlier)
            elif s < K - 1:
                new_pop[s + 1] += promoted

            # Repetentes
            new_pop[s] += n_here * r_rate

            # Evaded
            evaded_total += n_here * e
            # Migration to EJA
            migrated_eja += n_here * m
        pop = new_pop

    return {
        "completed_ef": completed_ef,
        "completed_em": completed_em,
        "evaded": evaded_total,
        "migrated_eja": migrated_eja,
        "remaining_in_school": pop.sum(),
    }

print("\n=== INEP cohort simulation (average rates 2014-2019) ===", flush=True)
inep_result = simulate_cohort(get_inep_rates, year_start=2005, n_years=20,
                                use_avg=True,
                                year_avg_start=2014, year_avg_end=2019)
print(f"  EF completed: {inep_result['completed_ef']:.1f}%", flush=True)
print(f"  EM completed: {inep_result['completed_em']:.1f}%", flush=True)
print(f"  Evaded:       {inep_result['evaded']:.1f}%", flush=True)
print(f"  Migrated EJA: {inep_result['migrated_eja']:.1f}%", flush=True)
print(f"  Still in school: {inep_result['remaining_in_school']:.1f}%", flush=True)

# ===========================================================
# Step 3: Build PNADC rates from v3 and run the same simulation
# We need rates by series. v3 only has by macroetapa. So we'll
# spread macroetapa rates uniformly to each series within that group.
# ===========================================================
print("\nLoading PNADC v3 corrected rates...", flush=True)
pnadc_t1 = pd.read_csv(PNADC_T1_V3)

# Average 2017-2019 (pre-COVID, post-2016 codes)
sub_pnadc = pnadc_t1[pnadc_t1["ano_t"].isin([2017, 2018, 2019])]
pnadc_rates_macro = sub_pnadc.groupby("macroetapa").agg({
    "flag_promocao": "mean",
    "flag_repetencia": "mean",
    "flag_evasao": "mean",
    "flag_migracao_eja": "mean",
}).reset_index()
print(pnadc_rates_macro, flush=True)

# Map to series
def get_pnadc_rates(etapa, year):
    if etapa.startswith("EF_"):
        s_num = int(etapa.split("_")[1])
        me = "EF iniciais" if s_num <= 5 else "EF finais"
    elif etapa.startswith("EM_"):
        me = "EM"
    else:
        return None
    row = pnadc_rates_macro[pnadc_rates_macro["macroetapa"] == me]
    if len(row) == 0:
        return None
    r = row.iloc[0]
    return (r["flag_promocao"], r["flag_repetencia"],
            r["flag_evasao"], r["flag_migracao_eja"])

print("\n=== PNADC cohort simulation (v3 rates, 2017-2019 avg) ===", flush=True)
pnadc_result = simulate_cohort(get_pnadc_rates, year_start=2005, n_years=20,
                                  use_avg=False)
print(f"  EF completed: {pnadc_result['completed_ef']:.1f}%", flush=True)
print(f"  EM completed: {pnadc_result['completed_em']:.1f}%", flush=True)
print(f"  Evaded:       {pnadc_result['evaded']:.1f}%", flush=True)
print(f"  Migrated EJA: {pnadc_result['migrated_eja']:.1f}%", flush=True)

# ===========================================================
# Step 4: Direct PNADC completion via VD3004
# Load select years and compute % of young adults (19-24)
# with VD3004 >= 3 (EF completed) or >= 5 (EM completed)
# ===========================================================
print("\nLoading VD3004 from raw parquets...", flush=True)
vd_frames = []
for p in sorted(PARSED_DIR.glob("pnadc_*.parquet")):
    name = p.stem
    try:
        d = pd.read_parquet(p, columns=["VD3004", "Ano", "Trimestre",
                                         "V2009", "V1028"])
    except Exception:
        continue
    if "VD3004" not in d.columns:
        continue
    d = d.dropna(subset=["VD3004", "V2009"])
    d["VD3004"] = pd.to_numeric(d["VD3004"], errors="coerce")
    d["V2009"] = pd.to_numeric(d["V2009"], errors="coerce")
    d["V1028"] = pd.to_numeric(d["V1028"], errors="coerce")
    d = d.dropna(subset=["VD3004"])
    vd_frames.append(d)

vd = pd.concat(vd_frames, ignore_index=True)
print(f"  Total VD3004 rows: {len(vd):,}", flush=True)

# Completion flags
# VD3004 codes (PNADC convention):
#   1 = Sem instrucao
#   2 = EF incompleto
#   3 = EF completo
#   4 = EM incompleto
#   5 = EM completo
#   6 = Superior incompleto
#   7 = Superior completo
vd["completed_ef"] = (vd["VD3004"] >= 3).astype(int)
vd["completed_em"] = (vd["VD3004"] >= 5).astype(int)

# Young adults aged 19-24 (allow for some delay)
ya = vd[vd["V2009"].between(19, 24)].copy()
print(f"  Young adults 19-24: {len(ya):,}", flush=True)

# Per year
pnadc_obs = ya.groupby("Ano").apply(lambda g: pd.Series({
    "completed_ef": np.average(g["completed_ef"], weights=g["V1028"]),
    "completed_em": np.average(g["completed_em"], weights=g["V1028"]),
    "n": len(g),
})).reset_index()

pnadc_obs.to_csv(OUT_DIR / "T7_pnadc_observed_completion.csv", index=False)
print("\n=== PNADC observed completion (age 19-24) ===", flush=True)
print(pnadc_obs.to_string(index=False), flush=True)

# ===========================================================
# Step 5: Comparison table
# ===========================================================
# Use PNADC obs at 2019 (closest to pre-COVID, stable)
pnadc_obs_2019 = pnadc_obs[pnadc_obs["Ano"] == 2019].iloc[0]
comparison = pd.DataFrame({
    "source": ["INEP (projetada)", "PNADC (projetada)",
               "PNADC (observada 2019, 19-24)"],
    "completion_ef": [inep_result["completed_ef"],
                       pnadc_result["completed_ef"],
                       pnadc_obs_2019["completed_ef"] * 100],
    "completion_em": [inep_result["completed_em"],
                       pnadc_result["completed_em"],
                       pnadc_obs_2019["completed_em"] * 100],
})
print("\n=== COMPARACAO FINAL ===", flush=True)
print(comparison.to_string(index=False), flush=True)
comparison.to_csv(OUT_DIR / "T7_iterative_completion.csv", index=False)

# Build LaTeX
lines = []
lines.append("% Auto-gerado por C18_iterative_completion.py")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Taxa de conclus\~ao do EF e do EM: simula\c{c}\~ao de coorte (INEP), simula\c{c}\~ao de coorte (PNADC) e taxa observada (PNADC, jovens 19--24).}")
lines.append(r"\label{tab:t7_completion}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrr}")
lines.append(r"\toprule")
lines.append(r"Fonte & Concl.\ EF (\%) & Concl.\ EM (\%) \\")
lines.append(r"\midrule")
for _, row in comparison.iterrows():
    lines.append(rf"{row['source']} & {row['completion_ef']:.1f} & {row['completion_em']:.1f} \\")
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fontes:} INEP Indicadores de Trajet\'oria (taxas m\'edias 2014--2019) e PNADC longitudinal v3 (m\'edia 2017--2019, ap\'os corre\c{c}\~ao de conclus\~ao do 3\textsuperscript{o} EM).")
lines.append(r"\item \textit{Notas:} A simula\c{c}\~ao de coorte aplica iterativamente as taxas por s\'erie por 20 anos a uma coorte de 100 crian\c{c}as entrando no 1\textsuperscript{o} EF. A taxa observada PNADC \'e o percentual de jovens de 19--24 anos em 2019 com \texttt{VD3004} indicando conclus\~ao do n\'ivel correspondente (EF $\geq$ 3, EM $\geq$ 5).")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")
out_tex = OUT_DIR / "T7_iterative_completion.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved {out_tex}", flush=True)

# Also save observed by-year for figure
pnadc_obs.to_csv(OUT_DIR / "F9_completion_by_year.csv", index=False)
print(f"Saved F9 data CSV", flush=True)
