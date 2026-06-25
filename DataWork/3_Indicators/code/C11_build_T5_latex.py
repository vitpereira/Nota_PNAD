# -------------------------------------------------------------------------
# C11_build_T5_latex.py
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Produz a Tabela 5: efeito do timing (Q1 vs Q2+) within-person sobre
#   repetencia e promocao. Tabela compacta para a secao de robustez.
#
# Inputs:
#   ../output/C10_within_person_by_year.csv
#
# Outputs:
#   ../output/T5_efeito_ferias_within.tex
# -------------------------------------------------------------------------

import csv
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "output"

# Aggregate over all years, weighted by n
agg = defaultdict(lambda: {"n": 0,
                            "prom_Q1": 0.0, "prom_Q2p": 0.0,
                            "rep_Q1": 0.0,  "rep_Q2p": 0.0,
                            "evas_Q1": 0.0, "evas_Q2p": 0.0})

with open(OUT / "C10_within_person_by_year.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        me = row["macroetapa_t"]
        n  = float(row["n"])
        if n == 0: continue
        d = agg[me]
        d["n"] += n
        for k in ("prom_Q1", "prom_Q2p", "rep_Q1", "rep_Q2p", "evas_Q1", "evas_Q2p"):
            d[k] += float(row[k]) * n

# Compute weighted means
for me, d in agg.items():
    n = d["n"]
    for k in list(d.keys()):
        if k != "n":
            d[k] = d[k] / n if n > 0 else 0.0

def f(x): return f"{x*100:5.1f}"
def fn(x): return f"{int(x):,}".replace(",", ".")

panels = [("EF iniciais", "EF iniciais (1\\textsuperscript{o}--5\\textsuperscript{o} ano)"),
          ("EF finais",   "EF finais (6\\textsuperscript{o}--9\\textsuperscript{o} ano)"),
          ("EM",          "Ensino M\\'edio (1\\textsuperscript{o}--3\\textsuperscript{o} ano)")]

lines = []
lines.append("% Auto-gerado por C11_build_T5_latex.py")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Efeito do timing da observa\c{c}\~ao de $t+1$ sobre as taxas de fluxo \emph{within-person}, Brasil, 2012--2023.}")
lines.append(r"\label{tab:t5_efeito_ferias}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lcccccccc}")
lines.append(r"\toprule")
lines.append(r"& & \multicolumn{3}{c}{Medido em Q1 de $t+1$} & \multicolumn{3}{c}{Medido em Q2--Q4 de $t+1$} & $\Delta$ Rep. \\")
lines.append(r"\cmidrule(lr){3-5} \cmidrule(lr){6-8}")
lines.append(r"Macroetapa & N & Prom. & Rep. & Evas. & Prom. & Rep. & Evas. & (pp) \\")
lines.append(r"\midrule")

for me, label in panels:
    d = agg.get(me, None)
    if d is None: continue
    delta_rep = (d["rep_Q2p"] - d["rep_Q1"]) * 100
    lines.append(
        rf"{label} & {fn(d['n'])} & "
        rf"{f(d['prom_Q1'])} & {f(d['rep_Q1'])} & {f(d['evas_Q1'])} & "
        rf"{f(d['prom_Q2p'])} & {f(d['rep_Q2p'])} & {f(d['evas_Q2p'])} & "
        rf"{delta_rep:+5.1f} \\"
    )

lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} PNADC trimestral, painel longitudinal, 2012--2023. Subamostra \emph{within-person}: alunos com observa\c{c}\~ao tanto no Q1 quanto em algum Q$\geq$2 de $t+1$ (cerca de 65\% dos casos com obs.\ em Q1 de $t+1$).")
lines.append(r"\item \textit{Notas:} A medi\c{c}\~ao em Q1 (jan--mar) coincide com o per\'iodo de f\'erias e in\'icio do ano letivo, em que parte das fam\'ilias ainda reporta a s\'erie anterior. Quando o mesmo aluno \'e remedido em Q2--Q4 (abr--dez, j\'a com a s\'erie nova consolidada), a repet\^encia cai $\sim$5pp e a promo\c{c}\~ao sobe $\sim$3--4pp. Evas\~ao $= 0$ nesta subamostra por constru\c{c}\~ao (exige matr\'icula em ambos os momentos).")
lines.append(r"\item Coluna $\Delta$ Rep.\ = (Rep.\ Q2--Q4) $-$ (Rep.\ Q1) em pontos percentuais.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT / "T5_efeito_ferias_within.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out_tex} ({len(lines)} lines)")

# Quick console summary
print("\n=== Summary ===")
for me, _ in panels:
    d = agg.get(me, {})
    if not d: continue
    print(f"{me:<14}: N={int(d['n']):>7,}, "
          f"Rep Q1={d['rep_Q1']*100:.1f}% Rep Q2+={d['rep_Q2p']*100:.1f}% "
          f"(Δ={ (d['rep_Q2p']-d['rep_Q1'])*100:+.1f}pp), "
          f"Prom Q1={d['prom_Q1']*100:.1f}% Q2+={d['prom_Q2p']*100:.1f}% "
          f"(Δ={ (d['prom_Q2p']-d['prom_Q1'])*100:+.1f}pp)")
