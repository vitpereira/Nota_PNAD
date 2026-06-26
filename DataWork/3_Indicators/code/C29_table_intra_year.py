# -------------------------------------------------------------------------
# C29_table_intra_year.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Constroi tabela LaTeX com a queda abrupta de inconsistencia intra-ano
#   de V3006 pos-2020, evidencia central da Rodada 20 (hipotese CATI).
#
# Outputs:
#   ../output/T_inconsistencia_intra_ano.tex
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

within = pd.read_csv(OUT / "C28_within_year_consistency.csv")
visit  = pd.read_csv(OUT / "C28_visit_pair_changes.csv")
visit = visit.rename(columns={'Ano':'ano'})
within = within.rename(columns={'Ano':'ano'})

# Merge
merged = visit.merge(within[['ano','pct_changed']], on='ano')

lines = []
lines.append(r"% C29 - inconsistencia intra-ano por ano e por par de visitas")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Inconsist\^encia da declara\c{c}\~ao de s\'erie/etapa dentro do mesmo ano civil, por par de visitas consecutivas. PNADC, 2012--2024.}")
lines.append(r"\label{tab:inconsistencia_intra}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrrrrr}")
lines.append(r"\toprule")
lines.append(r"Ano & V1$\to$V2 & V2$\to$V3 & V3$\to$V4 & V4$\to$V5 & Algum$^{a}$ \\")
lines.append(r"    & (\%)      & (\%)      & (\%)      & (\%)      & (\%) \\")
lines.append(r"\midrule")
for _, r in merged.iterrows():
    ano = int(r['ano'])
    p12 = r['1->2']
    p23 = r['2->3']
    p34 = r['3->4']
    p45 = r['4->5']
    any_chg = r['pct_changed']
    ano_lbl = f"{ano}"
    if ano == 2020:
        ano_lbl = f"\\textbf{{{ano}}}"  # bold for COVID/CATI shift year
    lines.append(rf"{ano_lbl} & {p12:.1f} & {p23:.1f} & {p34:.1f} & {p45:.1f} & {any_chg:.1f} \\")
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} PNADC, IBGE, microdados trimestrais. Pain\'eis 5-trimestres com \texttt{link\_ok}.")
lines.append(r"\item \textit{Notas:} Para cada par de visitas consecutivas (V$k$$\to$V$k$+1) dentro do mesmo ano civil, registra-se a propor\c{c}\~ao de indiv\'iduos cuja combina\c{c}\~ao etapa $\times$ s\'erie declarada difere entre as duas visitas. $^{a}$Coluna \emph{Algum} reporta a propor\c{c}\~ao de pessoas-ano com pelo menos uma mudan\c{c}a entre quaisquer dos quatro pares.")
lines.append(r"\item Pr\'e-2020, cerca de 20--30\% dos respondentes alteram a declara\c{c}\~ao entre visitas consecutivas, capturando naturalmente a transi\c{c}\~ao do ano letivo. A partir de 2\textsuperscript{o} trimestre de 2020 com a substitui\c{c}\~ao de coleta presencial (CAPI) por coleta telef\^onica (CATI) na PNADC, essa propor\c{c}\~ao cai abruptamente para 6--12\% e permanece nesse patamar at\'e 2023, com recupera\c{c}\~ao parcial em 2024.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out = OUT / "T_inconsistencia_intra_ano.tex"
out.write_text("\n".join(lines)+"\n", encoding="utf-8")
print(f"Wrote {out}")
