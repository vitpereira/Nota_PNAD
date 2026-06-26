# -------------------------------------------------------------------------
# C27_T1_exclude_covid.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Regenera T1 com os anos 2020 e 2021 EXCLUIDOS (mostrados como ---).
#   Decisao do autor: nao reportar taxas durante a pandemia.
# -------------------------------------------------------------------------

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

# Read v5 CSV
inter = defaultdict(dict)
with open(OUT / "T1_brasil_inter_v5_main.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        inter[(int(r["ano_t"]), r["macroetapa"])] = r

# Read abandono
intra = defaultdict(dict)
for fname in ["T_abandono_norot1.csv", "T_abandono_fullyear.csv"]:
    p = OUT / fname
    if p.exists():
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                year_key = r.get("ano_t") or r.get("ano_cal")
                intra[(int(year_key), r["macroetapa"])] = r
        break

def fmt_pct(x):
    if x in (None, "", "."): return "---"
    try: return f"{float(x)*100:.1f}"
    except: return "---"
def fmt_n(x):
    if x in (None, "", "."): return "---"
    try: return f"{int(float(x)):,}".replace(",", ".")
    except: return "---"

years = sorted({k[0] for k in inter.keys()})
panels = [
    ("EF iniciais", r"\textit{Painel A: EF iniciais (1\textsuperscript{o}--5\textsuperscript{o} ano)}"),
    ("EF finais",   r"\textit{Painel B: EF finais (6\textsuperscript{o}--9\textsuperscript{o} ano)}"),
    ("EM",          r"\textit{Painel C: Ensino M\'edio (regular + t\'ecnico, 1\textsuperscript{o}--4\textsuperscript{o} ano)}"),
]

# COVID years to exclude from main table
COVID_YEARS = {2020, 2021}

lines = []
lines.append("% C27 v5 - main com 2020 e 2021 excluidos")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano. Janela $t,t{+}1 \in \{Q_2,Q_3\}$ com $\max(\textit{nivel})$. Inclui EM t\'ecnico. Corre\c{c}\~ao de conclus\~ao via $V3014$. \textbf{Anos 2020 e 2021 omitidos da tabela principal} em virtude do paradoxo de auto-relato discutido na Se\c{c}\~ao~\ref{ssec:paradoxo_covid}.}")
lines.append(r"\label{tab:t1_brasil}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrrrrrr}")
lines.append(r"\toprule")
lines.append(r"Ano & Promo\c{c}\~ao & Repet\^encia & Evas\~ao & Migra\c{c}\~ao EJA & Abandono$^{a}$ & N \\")
lines.append(r"    & (\%)            & (\%)        & (\%)     & (\%)               & (\%)            &   \\")
lines.append(r"\midrule")
for etapa, label in panels:
    lines.append(rf"\multicolumn{{7}}{{l}}{{{label}}} \\")
    lines.append(r"\midrule")
    for y in years:
        if y in COVID_YEARS:
            continue   # SKIP 2020 e 2021
        r = inter.get((y, etapa), {})
        ri = intra.get((y, etapa), {})
        prom = fmt_pct(r.get("flag_promocao"))
        rep = fmt_pct(r.get("flag_repetencia"))
        evas = fmt_pct(r.get("flag_evasao"))
        eja = fmt_pct(r.get("flag_migracao_eja"))
        aband = fmt_pct(ri.get("flag_abandono"))
        n = fmt_n(r.get("n_pessoa"))
        # Mark 2022 e 2023 com note especial sobre anomalia residual pos-COVID
        ano_label = f"{y}$^{{\\ddagger}}$" if y in (2022, 2023) else str(y)
        lines.append(rf"{ano_label} & {prom} & {rep} & {evas} & {eja} & {aband} & {n} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} PNADC trimestral, IBGE, 2012Q1--2024Q4.")
lines.append(r"\item \textit{Notas:} As taxas de promo\c{c}\~ao, repet\^encia, evas\~ao e migra\c{c}\~ao para EJA s\~ao \emph{entre-anos} ($t$ a $t+1$). Refer\^encia em $t$: obs.\ com maior n\'ivel entre $Q_2$ e $Q_3$ de $t$. Refer\^encia em $t+1$: idem para $t+1$. Conclus\~ao do 3\textsuperscript{o} EM regular ou 4\textsuperscript{o} EM t\'ecnico via $V3014=1$ classificada como promo\c{c}\~ao.")
lines.append(r"\item $^{a}$Abandono \'e \emph{intra-ano} (Tabela~\ref{tab:abandono_fullyear}, calculado separadamente).")
lines.append(r"\item Anos 2020 e 2021 omitidos: durante a pandemia, o auto-relato familiar e o registro administrativo (INEP) divergem sistematicamente (Se\c{c}\~ao~\ref{ssec:paradoxo_covid}).")
lines.append(r"\item $^{\ddagger}$Anos 2022 e 2023: a repet\^encia reportada permanece elevada, padr\~ao incompat\'ivel com a estabilidade da idade m\'edia por s\'erie (Tabela~\ref{tab:idade_serie}). Interpretar com cautela; aguardar divulga\c{c}\~ao do INEP para 2022/2023 para resolver a ambiguidade.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT / "T1_brasil_inter_por_serie_ano.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out_tex}")
print(f"Years omitted: {sorted(COVID_YEARS)}")
print(f"Years kept: {[y for y in years if y not in COVID_YEARS]}")
