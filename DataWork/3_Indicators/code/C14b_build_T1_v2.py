# -------------------------------------------------------------------------
# C14b_build_T1_v2.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Gera T1_brasil_inter_por_serie_ano.tex (v2) a partir de T1_brasil_inter_v2.csv.
#   Preserva a versao v1 como T1_v1_calibrated_Qge2fallback.tex.
# -------------------------------------------------------------------------

import csv
from collections import defaultdict
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "output"

# Backup the v1 file
old_tex = OUT / "T1_brasil_inter_por_serie_ano.tex"
backup_v1 = OUT / "T1_v1_calibrated_Qge2fallback.tex"
if old_tex.exists() and not backup_v1.exists():
    shutil.copy(old_tex, backup_v1)
    print(f"Backed up v1 to {backup_v1}")

# Read v2 CSV
inter = defaultdict(dict)
with open(OUT / "T1_brasil_inter_v2.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        inter[(int(r["ano_t"]), r["macroetapa"])] = r

# Read intra (abandono) — placeholder; will be updated by C15
intra = defaultdict(dict)
intra_path = OUT / "T1_brasil_intra_por_macroetapa_ano.csv"
if intra_path.exists():
    with open(intra_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            year_key = r.get("ano_t") or r.get("ano_cal")
            intra[(int(year_key), r["macroetapa"])] = r

def fmt_pct(x):
    if x in (None, "", "."): return "---"
    try: return f"{float(x)*100:.1f}"
    except (TypeError, ValueError): return "---"

def fmt_n(x):
    if x in (None, "", "."): return "---"
    try: return f"{int(float(x)):,}".replace(",", ".")
    except (TypeError, ValueError): return "---"

years = sorted({k[0] for k in inter.keys()})

panels = [
    ("EF iniciais", r"\textit{Painel A: EF iniciais (1\textsuperscript{o}--5\textsuperscript{o} ano)}"),
    ("EF finais",   r"\textit{Painel B: EF finais (6\textsuperscript{o}--9\textsuperscript{o} ano)}"),
    ("EM",          r"\textit{Painel C: Ensino M\'edio (1\textsuperscript{o}--3\textsuperscript{o} ano)}"),
]

lines = []
lines.append("% Auto-gerado por C14b_build_T1_v2.py - versao v2 (Q2-Q3 + max(nivel) em t+1)")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano. Painel longitudinal da PNADC, 2012--2023, janela de transi\c{c}\~ao restrita a Q2 e Q3.}")
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
        r = inter.get((y, etapa), {})
        ri = intra.get((y, etapa), {})
        prom  = fmt_pct(r.get("flag_promocao"))
        rep   = fmt_pct(r.get("flag_repetencia"))
        evas  = fmt_pct(r.get("flag_evasao"))
        eja   = fmt_pct(r.get("flag_migracao_eja"))
        aband = fmt_pct(ri.get("flag_abandono"))
        n     = fmt_n(r.get("n_pessoa"))
        ano_label = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(rf"{ano_label} & {prom} & {rep} & {evas} & {eja} & {aband} & {n} \\")
    lines.append(r"\\[0.3em]")

if lines[-1] == r"\\[0.3em]":
    lines.pop()

lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal da PNADC trimestral (IBGE), 2012Q1--2024Q4.")
lines.append(r"\item \textit{Notas:} As taxas de promo\c{c}\~ao, repet\^encia, evas\~ao e migra\c{c}\~ao para EJA s\~ao \emph{entre-anos} (do ano $t$ ao ano $t+1$). A observa\c{c}\~ao de refer\^encia em $t$ \'e a obs.\ com maior n\'ivel educacional entre Q2 e Q3 do ano $t$; a refer\^encia em $t+1$ \'e a obs.\ com maior n\'ivel entre Q2 e Q3 de $t+1$. Observa\c{c}\~oes em Q1 (jan-mar) e Q4 (out-dez) s\~ao exclu\'idas porque coincidem com per\'iodos de f\'erias e in\'icio/encerramento de ano letivo, em que a s\'erie declarada pode estar desatualizada. Abandono \'e \emph{intra-ano} (Tabela~\ref{tab:abandono_fullyear}, calculado separadamente com fam\'ilias que cobrem todos os quatro trimestres).")
lines.append(r"\item $^{a}$Abandono refere-se \`a taxa intra-ano calculada na Tabela~\ref{tab:abandono_fullyear}. Inter e intra n\~ao somam 100\% porque medem fen\^omenos em janelas temporais distintas.")
lines.append(r"\item $^{\dagger}$Anos afetados pela pandemia COVID-19. Interpretar com cautela.")
lines.append(r"\item \emph{N} \'e o n\'umero de transi\c{c}\~oes individuais (n\~ao ponderado). As taxas s\~ao ponderadas pelo peso amostral $w_i^{P1}$. O total prom.\ + repet.\ + evas.\ + EJA $\sim$97\% no EF e $\sim$90\% no EM, residual atribu\'ido a transi\c{c}\~oes para ensino superior, modalidades n\~ao classificadas e atrito no domic\'ilio.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT / "T1_brasil_inter_por_serie_ano.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out_tex}")
