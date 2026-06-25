# -------------------------------------------------------------------------
# C15_abandono_fullyear.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Calcula a taxa de abandono intra-ano restringindo o universo aos alunos
#   com observacoes em TODOS os quatro trimestres do mesmo ano. Apenas
#   domicilios entrando em Q1 do ano y cumprem esse criterio.
#
#   Abandono = freq_escola == 1 em Q1 AND freq_escola == 0 em Q4 (mesmo ano).
#
# Inputs:
#   ../../2_PanelBuild/tmp/pnadc_linked.dta
#
# Outputs:
#   ../output/T_abandono_fullyear.csv
#   ../output/T_abandono_fullyear.tex
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

print(f"Reading {LINK}...", flush=True)
df, meta = pyreadstat.read_dta(str(LINK), usecols=KEEP)
print(f"  Loaded {len(df):,}", flush=True)

df = df[df["link_ok"] == 1].copy()

# Macroetapa label
etc = df["etapa_consolid"]
me = pd.Series(np.where(etc == 4, "EF iniciais",
                np.where(etc == 5, "EF finais",
                  np.where(etc.isin([10, 11, 12]), "EM",
                    np.where(etc == 20, "EJA EF",
                      np.where(etc == 21, "EJA EM", None))))), index=df.index)
df["macroetapa"] = me

# Identify persons with obs in ALL 4 quarters of the same year
trims = df.groupby(["person_id", "Ano"])["Trimestre"].nunique()
full4 = trims[trims == 4].reset_index()[["person_id", "Ano"]]
print(f"  Person-years with full Q1-Q4 coverage: {len(full4):,}", flush=True)

df_full = df.merge(full4, on=["person_id", "Ano"], how="inner")
print(f"  Obs in full-coverage sample: {len(df_full):,}", flush=True)

# Filter to universe: enrolled in regular EF/EM at Q1 of year
df_q1 = df_full[df_full["Trimestre"] == 1].copy()
df_q1 = df_q1[df_q1["etapa_consolid"].isin([4, 5, 10, 11, 12])]
df_q1 = df_q1[df_q1["freq_escola"] == 1]
print(f"  Q1 enrolled (universe): {len(df_q1):,}", flush=True)

df_q4 = df_full[df_full["Trimestre"] == 4][["person_id", "Ano", "freq_escola",
                                              "etapa_consolid", "serie"]].copy()
df_q4 = df_q4.rename(columns={"freq_escola": "freq_q4",
                              "etapa_consolid": "etapa_q4",
                              "serie": "serie_q4"})

# Merge Q1 and Q4
abandono = df_q1.merge(df_q4, on=["person_id", "Ano"], how="left")

# Abandono: freq_escola=1 em Q1 e freq=0 em Q4 (e nao em EJA)
abandono["flag_abandono"] = (
    (abandono["freq_q4"] == 0)
).astype(int)

# Migracao EJA dentro do ano (Q1 regular -> Q4 EJA)
abandono["flag_eja_intra"] = (
    abandono["etapa_q4"].isin([20, 21])
).astype(int)

# Aggregate by ano x macroetapa
abandono["wt"] = abandono["peso_v1028"]
grp = abandono.groupby(["Ano", "macroetapa"])
agg = pd.DataFrame({
    "flag_abandono":   grp.apply(lambda g: np.average(g.flag_abandono, weights=g.wt)),
    "flag_eja_intra":  grp.apply(lambda g: np.average(g.flag_eja_intra, weights=g.wt)),
    "n":               grp.size(),
}).reset_index()
agg.columns = ["ano_t", "macroetapa", "flag_abandono", "flag_eja_intra", "n"]
agg = agg[agg["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()

agg.to_csv(OUT_DIR / "T_abandono_fullyear.csv", index=False)
print(f"\nSaved {OUT_DIR / 'T_abandono_fullyear.csv'}", flush=True)

# Print summary
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n--- {et} ---", flush=True)
    sub = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub.iterrows():
        print(f"  {int(r.ano_t)}: aband={r.flag_abandono*100:.2f}% "
              f"eja_intra={r.flag_eja_intra*100:.2f}% n={int(r.n)}",
              flush=True)

# Build LaTeX
def fmt_pct(x): return f"{x*100:.1f}"
def fmt_n(x): return f"{int(x):,}".replace(",", ".")

years = sorted({(int(r["ano_t"]), r["macroetapa"]) for _, r in agg.iterrows()})
years_list = sorted({y for y, _ in years})

lines = []
lines.append("% Auto-gerado por C15_abandono_fullyear.py")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Taxa de abandono intra-ano com cobertura completa Q1--Q4 e migra\c{c}\~ao para EJA dentro do ano, Brasil, 2012--2024.}")
lines.append(r"\label{tab:abandono_fullyear}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrrr}")
lines.append(r"\toprule")
lines.append(r"Ano & Abandono (\%) & Migra\c{c}\~ao EJA intra-ano (\%) & N \\")
lines.append(r"\midrule")
for et in ["EF iniciais", "EF finais", "EM"]:
    lines.append(rf"\multicolumn{{4}}{{l}}{{\textit{{{et}}}}} \\")
    lines.append(r"\midrule")
    sub = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub.iterrows():
        y = int(r.ano_t)
        ano_label = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(rf"{ano_label} & {fmt_pct(r.flag_abandono)} & {fmt_pct(r.flag_eja_intra)} & {fmt_n(r.n)} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal da PNADC.")
lines.append(r"\item \textit{Notas:} Subamostra restrita aos alunos com observa\c{c}\~oes em todos os quatro trimestres do mesmo ano (apenas domic\'ilios que entram no painel em Q1 cumprem esse crit\'erio, correspondendo a cerca de um quinto do total amostral). Abandono \'e definido como \texttt{V3002=1} em Q1 e \texttt{V3002=0} em Q4 do mesmo ano. Migra\c{c}\~ao EJA intra-ano refere-se a alunos em regular EF/EM em Q1 cuja etapa em Q4 \'e EJA.")
lines.append(r"\item $^{\dagger}$Anos afetados pela pandemia COVID-19.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT_DIR / "T_abandono_fullyear.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved {out_tex}", flush=True)
