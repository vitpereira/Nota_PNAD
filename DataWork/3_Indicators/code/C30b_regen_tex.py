# -------------------------------------------------------------------------
# C30b_regen_tex.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Regenera T_abandono_fullyear.tex a partir de T_abandono_v5_corrected.csv,
#   substituindo o output buggy de C15/C22b por valores com correção V3014.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT  = ROOT / "DataWork/3_Indicators/output"

agg = pd.read_csv(OUT / "T_abandono_v5_corrected.csv")

def fmt_pct(x):
    try: return f"{float(x)*100:.1f}"
    except: return "---"
def fmt_n(x):
    try: return f"{int(float(x)):,}".replace(",", ".")
    except: return "---"

DBL = "\\" + "\\"  # double backslash for LaTeX row end
ROW_GAP = DBL + "[0.3em]"

lines = []
lines.append("% C30b - abandono v5 corrected (V3014 aplicada)")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Taxa de abandono intra-ano (cobertura completa Q1--Q4) com corre\c{c}\~ao \texttt{V3014} para conclus\~ao terminal do EM, Brasil, 2012--2024.}")
lines.append(r"\label{tab:abandono_fullyear}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrrr}")
lines.append(r"\toprule")
lines.append(r"Ano & Abandono (\%) & Migra\c{c}\~ao EJA intra-ano (\%) & N " + DBL)
lines.append(r"\midrule")
for et in ["EF iniciais", "EF finais", "EM"]:
    lines.append(r"\multicolumn{4}{l}{\textit{" + et + r"}} " + DBL)
    lines.append(r"\midrule")
    sub = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub.iterrows():
        y = int(r.ano_t)
        ano_lbl = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(f"{ano_lbl} & {fmt_pct(r.flag_abandono)} & "
                     f"{fmt_pct(r.flag_eja_intra)} & {fmt_n(r.n)} " + DBL)
    lines.append(ROW_GAP)
if lines[-1] == ROW_GAP: lines.pop()
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal da PNADC.")
lines.append(r"\item \textit{Notas:} Subamostra restrita aos alunos com observa\c{c}\~oes em todos os quatro trimestres do mesmo ano (\emph{rota\c{c}\~ao 1}). Abandono \'e definido como \texttt{V3002=1} em Q1 e \texttt{V3002=0} em Q4 do mesmo ano, \emph{exceto} para alunos no terceiro ano do EM regular ou no quarto ano do EM t\'ecnico (\emph{n\'ivel}~12--13) cuja \texttt{V3014=1} em alguma observa\c{c}\~ao do ano (conclus\~ao terminal). Esses s\~ao reclassificados como conclus\~ao, n\~ao abandono.")
lines.append(r"\item $^{\dagger}$Anos afetados pela pandemia COVID-19.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

(OUT / "T_abandono_fullyear.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote T_abandono_fullyear.tex")
