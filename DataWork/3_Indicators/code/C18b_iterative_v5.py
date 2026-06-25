# -------------------------------------------------------------------------
# C18b_iterative_v5.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Re-roda iteracao de coorte usando taxas v5 (Q2-Q3 + V3014 + tecnico).
#   Substitui C18 que usava v3.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
INEP = ROOT / "DataWork/4_INEP_Comparison/output/inep_transicao_long.csv"
PNADC_T1_V5 = ROOT / "DataWork/3_Indicators/output/T1_brasil_inter_v5_main.csv"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# INEP rates
inep = pd.read_csv(INEP)
inep = inep[inep["unidade"] == "Brasil"].copy()
series_codes = ["EF_1", "EF_2", "EF_3", "EF_4", "EF_5", "EF_6", "EF_7", "EF_8", "EF_9",
                "EM_1", "EM_2", "EM_3"]
inep = inep[inep["etapa"].isin(series_codes)].copy()
inep_w = inep.pivot_table(
    index=["etapa", "ano_t"], columns="indicador", values="valor",
    aggfunc="first").reset_index()
for c in ["promocao", "repetencia", "evasao", "migracao_eja"]:
    if c in inep_w.columns:
        inep_w[c] = inep_w[c] / 100.0

def get_inep_rates(etapa, year):
    sub = inep_w[inep_w["etapa"] == etapa].copy()
    if len(sub) == 0: return None
    sub["dist"] = (sub["ano_t"] - year).abs()
    sub = sub.sort_values("dist")
    r = sub.iloc[0]
    return (r["promocao"], r["repetencia"], r["evasao"], r.get("migracao_eja", 0))

def simulate_cohort(rate_fn, year_start, n_years, use_avg=False,
                     year_avg_start=2014, year_avg_end=2019):
    series_order = ["EF_1", "EF_2", "EF_3", "EF_4", "EF_5",
                    "EF_6", "EF_7", "EF_8", "EF_9",
                    "EM_1", "EM_2", "EM_3"]
    K = len(series_order)
    pop = np.zeros(K); pop[0] = 100.0
    completed_ef = 0; completed_em = 0; evaded_total = 0; migrated_eja = 0
    for t in range(n_years):
        new_pop = np.zeros(K)
        for s in range(K):
            if pop[s] == 0: continue
            if use_avg:
                rates_list = []
                for y_avg in range(year_avg_start, year_avg_end + 1):
                    rt = rate_fn(series_order[s], y_avg)
                    if rt is not None: rates_list.append(rt)
                if not rates_list: continue
                p = np.mean([r[0] for r in rates_list])
                r_rate = np.mean([r[1] for r in rates_list])
                e = np.mean([r[2] for r in rates_list])
                m = np.mean([r[3] for r in rates_list])
            else:
                rates = rate_fn(series_order[s], year_start + t)
                if rates is None: continue
                p, r_rate, e, m = rates
            n_here = pop[s]
            promoted = n_here * p
            if s == 8:
                new_pop[9] += promoted; completed_ef += promoted
            elif s == 11:
                completed_em += promoted
            elif s < K - 1:
                new_pop[s + 1] += promoted
            new_pop[s] += n_here * r_rate
            evaded_total += n_here * e
            migrated_eja += n_here * m
        pop = new_pop
    return {"completed_ef": completed_ef, "completed_em": completed_em,
             "evaded": evaded_total, "migrated_eja": migrated_eja,
             "remaining_in_school": pop.sum()}

# INEP simulation
print("INEP cohort simulation (2014-2019 avg)...")
inep_result = simulate_cohort(get_inep_rates, year_start=2005, n_years=20,
                                use_avg=True)
print(f"  EF completed: {inep_result['completed_ef']:.1f}%")
print(f"  EM completed: {inep_result['completed_em']:.1f}%")

# PNADC v5 simulation
print("\nLoading PNADC v5 corrected rates...")
pnadc_t1 = pd.read_csv(PNADC_T1_V5)
sub_pnadc = pnadc_t1[pnadc_t1["ano_t"].isin([2017, 2018, 2019])]
pnadc_rates_macro = sub_pnadc.groupby("macroetapa").agg({
    "flag_promocao": "mean", "flag_repetencia": "mean",
    "flag_evasao": "mean", "flag_migracao_eja": "mean",
}).reset_index()
print(pnadc_rates_macro)

def get_pnadc_rates(etapa, year):
    if etapa.startswith("EF_"):
        s_num = int(etapa.split("_")[1])
        me = "EF iniciais" if s_num <= 5 else "EF finais"
    elif etapa.startswith("EM_"):
        me = "EM"
    else: return None
    row = pnadc_rates_macro[pnadc_rates_macro["macroetapa"] == me]
    if len(row) == 0: return None
    r = row.iloc[0]
    return (r["flag_promocao"], r["flag_repetencia"],
             r["flag_evasao"], r["flag_migracao_eja"])

print("\nPNADC v5 cohort simulation...")
pnadc_result = simulate_cohort(get_pnadc_rates, year_start=2005, n_years=20)
print(f"  EF completed: {pnadc_result['completed_ef']:.1f}%")
print(f"  EM completed: {pnadc_result['completed_em']:.1f}%")

# Observed completion from VD3004 (use existing CSV)
print("\nLoading observed completion (T7_pnadc_observed_completion.csv)...")
obs = pd.read_csv(OUT_DIR / "T7_pnadc_observed_completion.csv")
pnadc_obs_2019 = obs[obs["Ano"] == 2019].iloc[0]
print(f"  Observed 2019 EF (19-24): {pnadc_obs_2019['completed_ef']*100:.1f}%")
print(f"  Observed 2019 EM (19-24): {pnadc_obs_2019['completed_em']*100:.1f}%")

# Comparison
comparison = pd.DataFrame({
    "source": ["INEP (projetada)", "PNADC v5 (projetada)",
                "PNADC (observada 2019, 19-24)"],
    "completion_ef": [inep_result["completed_ef"],
                       pnadc_result["completed_ef"],
                       pnadc_obs_2019["completed_ef"] * 100],
    "completion_em": [inep_result["completed_em"],
                       pnadc_result["completed_em"],
                       pnadc_obs_2019["completed_em"] * 100],
})
print("\n=== FINAL ===")
print(comparison.to_string(index=False))
comparison.to_csv(OUT_DIR / "T7_iterative_completion.csv", index=False)

# LaTeX table
lines = []
lines.append("% C18b v5 iterative completion")
lines.append(r"\begin{table}[htbp]\centering")
lines.append(r"\caption{Taxa de conclus\~ao do EF e do EM: simula\c{c}\~ao de coorte (INEP), simula\c{c}\~ao de coorte (PNADC v5) e taxa observada (PNADC, jovens 19--24).}")
lines.append(r"\label{tab:t7_completion}")
lines.append(r"\begin{threeparttable}\small")
lines.append(r"\begin{tabular}{lrr}\toprule")
lines.append(r"Fonte & Concl.\ EF (\%) & Concl.\ EM (\%) \\\midrule")
for _, row in comparison.iterrows():
    lines.append(rf"{row['source']} & {row['completion_ef']:.1f} & {row['completion_em']:.1f} \\")
lines.append(r"\bottomrule\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fontes:} INEP Indicadores de Trajet\'oria (m\'edia 2014--2019) e PNADC v5 (m\'edia 2017--2019, com corre\c{c}\~ao V3014).")
lines.append(r"\item \textit{Notas:} Simula\c{c}\~ao iterativa de 100 crian\c{c}as entrando no 1\textsuperscript{o} EF, aplicando taxas por s\'erie ao longo de 20 anos. A taxa observada PNADC \'e o percentual de jovens de 19--24 anos em 2019 com \texttt{VD3004} indicando conclus\~ao do n\'ivel correspondente.")
lines.append(r"\end{tablenotes}\end{threeparttable}\end{table}")
(OUT_DIR / "T7_iterative_completion.tex").write_text("\n".join(lines) + "\n",
                                                       encoding="utf-8")
print(f"\nSaved T7_iterative_completion.tex")
