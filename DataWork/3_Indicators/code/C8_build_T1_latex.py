# -------------------------------------------------------------------------
# C8_build_T1_latex.py
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Reads T1_brasil_inter_por_macroetapa_ano.csv and produces a
#   publication-quality LaTeX table (booktabs + threeparttable) with three
#   panels (EF iniciais, EF finais, EM) and 12 years of data (2012-2023).
#   COVID years (2020-2021) are visually flagged with daggers.
#
# Inputs:
#   ../output/T1_brasil_inter_por_macroetapa_ano.csv
#   ../output/T1_brasil_intra_por_macroetapa_ano.csv  (for abandono col)
#
# Outputs:
#   ../output/T1_brasil_inter_por_serie_ano.tex
# -------------------------------------------------------------------------

import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "output"

# --- Read inter (between-year transitions: prom/rep/evas/naoprog) ---
inter = defaultdict(dict)  # inter[(ano, macroetapa)] = row
with open(OUT / "T1_brasil_inter_por_macroetapa_ano.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        inter[(int(r["ano_t"]), r["macroetapa"])] = r

# --- Read intra (within-year: abandono) ---
intra = defaultdict(dict)
intra_path = OUT / "T1_brasil_intra_por_macroetapa_ano.csv"
if intra_path.exists():
    with open(intra_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            year_key = r.get("ano_t") or r.get("ano_cal")
            intra[(int(year_key), r["macroetapa"])] = r

def fmt_pct(x):
    if x in (None, "", "."):
        return "---"
    try:
        return f"{float(x)*100:.1f}"
    except (TypeError, ValueError):
        return "---"

def fmt_n(x):
    if x in (None, "", "."):
        return "---"
    try:
        n = int(float(x))
        return f"{n:,}".replace(",", ".")
    except (TypeError, ValueError):
        return "---"

# Year set (sorted)
years = sorted({k[0] for k in inter.keys()})

# Panels (ordered) and their human labels
panels = [
    ("EF iniciais", r"\textit{Painel A: EF iniciais (1\textsuperscript{o}--5\textsuperscript{o} ano)}"),
    ("EF finais",   r"\textit{Painel B: EF finais (6\textsuperscript{o}--9\textsuperscript{o} ano)}"),
    ("EM",          r"\textit{Painel C: Ensino M\'edio (1\textsuperscript{o}--3\textsuperscript{o} ano)}"),
]

lines = []
lines.append("% Auto-gerado por C8_build_T1_latex.py - NÃO editar à mão")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano (PNADC longitudinal, 2012--2023).}")
lines.append(r"\label{tab:t1_brasil}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrrrrrr}")
lines.append(r"\toprule")
lines.append(r"Ano & Promoção & Repetência & Evasão & Não-progr. & Abandono$^{a}$ & N \\")
lines.append(r"    & (\%)     & (\%)        & (\%)   & (\%)        & (\%)             &   \\")
lines.append(r"\midrule")

for etapa, label in panels:
    lines.append(rf"\multicolumn{{7}}{{l}}{{{label}}} \\")
    lines.append(r"\midrule")
    for y in years:
        r = inter.get((y, etapa), {})
        ri = intra.get((y, etapa), {})
        prom = fmt_pct(r.get("flag_promocao"))
        rep  = fmt_pct(r.get("flag_repetencia"))
        evas = fmt_pct(r.get("flag_evasao"))
        nprog= fmt_pct(r.get("flag_naoprog"))
        aband= fmt_pct(ri.get("flag_abandono"))
        n    = fmt_n(r.get("n_pessoa"))
        # Mark COVID years with dagger
        ano_label = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(rf"{ano_label} & {prom} & {rep} & {evas} & {nprog} & {aband} & {n} \\")
    lines.append(r"\\[0.3em]")

# Remove trailing empty row
if lines[-1] == r"\\[0.3em]":
    lines.pop()

lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal da PNADC trimestral (IBGE), 2012Q1--2024Q4.")
lines.append(r"\item \textit{Notas:} Promoção, repetência, evasão e não-progressão são taxas \emph{entre-anos} (entre o ano calendário $t$ e $t+1$). Abandono é \emph{intra-ano} (entre o início e o final de cada ano letivo).")
lines.append(r"\item $^{a}$Abandono refere-se ao percentual de alunos com \texttt{V3002=1} no 1º trimestre de $t$ que reportam não frequentar escola no 4º trimestre do mesmo ano. As taxas inter e intra não somam 100\% porque medem fenômenos em janelas temporais distintas.")
lines.append(r"\item $^{\dagger}$Anos afetados pela pandemia COVID-19 (suspensão de aulas presenciais, mudanças metodológicas na coleta da PNADC e adoção de aprovação automática em diversos estados). Interpretar com cautela.")
lines.append(r"\item \emph{N} reporta o número de observações individuais (não ponderado) usadas no cálculo. As taxas são ponderadas pelo peso amostral $w_i^{P1}$ (peso PNADC longitudinalmente válido).")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT / "T1_brasil_inter_por_serie_ano.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out_tex} ({len(lines)} lines)")
