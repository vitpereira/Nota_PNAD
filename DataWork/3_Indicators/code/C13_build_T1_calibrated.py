# -------------------------------------------------------------------------
# C13_build_T1_calibrated.py
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Constroi a Tabela 1 (versao calibrada com Q>=2 fallback Q1) em LaTeX.
#   Preserva a versao original (Q1-only) como T1_v0_uncalibrated.tex.
#
# Inputs:
#   ../output/T1_brasil_inter_calibrated.csv         (NEW main, calibrada)
#   ../output/T1_brasil_intra_por_macroetapa_ano.csv (abandono intra-ano)
#
# Outputs:
#   ../output/T1_brasil_inter_por_serie_ano.tex      (NEW main)
#   ../output/T1_v0_uncalibrated.tex                 (backup do antigo)
# -------------------------------------------------------------------------

import csv
from collections import defaultdict
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "output"

# Backup old T1 (Q1-based) if it exists and is not the auto-gen one
old_tex = OUT / "T1_brasil_inter_por_serie_ano.tex"
backup_tex = OUT / "T1_v0_uncalibrated.tex"
if old_tex.exists() and not backup_tex.exists():
    shutil.copy(old_tex, backup_tex)
    print(f"Backed up old T1 to {backup_tex}")

# Read calibrated CSV
inter = defaultdict(dict)
with open(OUT / "T1_brasil_inter_calibrated.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        inter[(int(r["ano_t"]), r["macroetapa"])] = r

# Read intra (abandono) — unchanged
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
lines.append("% Auto-gerado por C13_build_T1_calibrated.py - versao calibrada (Q>=2 fallback Q1)")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano (PNADC longitudinal, 2012--2023). Calibra\c{c}\~ao $t$+1 em Q$\geq$2 com fallback Q1.}")
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
lines.append(r"\item \textit{Notas:} As taxas de promo\c{c}\~ao, repet\^encia, evas\~ao e migra\c{c}\~ao para EJA s\~ao \emph{entre-anos} (do ano $t$ ao ano $t+1$). A obs.\ de refer\^encia em $t$ e em $t+1$ \'e, por crit\'erio, o primeiro trimestre Q$\geq$2 observado no ano correspondente; se o domic\'ilio aparece apenas no Q1, esta obs.\ \'e usada (Se\c{c}\~ao~\ref{ssec:efeito_ferias}). Abandono \'e \emph{intra-ano}: primeiro vs.\ \'ultimo trimestre observado no mesmo ano $t$.")
lines.append(r"\item $^{a}$Abandono refere-se ao percentual de alunos com \texttt{V3002=1} no primeiro trimestre de $t$ que reportam n\~ao frequentar escola na \'ultima obs.\ do mesmo ano $t$. As taxas inter e intra n\~ao somam 100\% porque medem fen\^omenos em janelas temporais distintas.")
lines.append(r"\item $^{\dagger}$Anos afetados pela pandemia COVID-19 (suspens\~ao de aulas presenciais, mudan\c{c}as metodol\'ogicas na coleta da PNADC e ado\c{c}\~ao de aprova\c{c}\~ao autom\'atica em diversos estados). Interpretar com cautela.")
lines.append(r"\item \emph{N} reporta o n\'umero de observa\c{c}\~oes individuais (n\~ao ponderado) usadas no c\'alculo. As taxas s\~ao ponderadas pelo peso amostral $w_i^{P1}$ (peso PNADC longitudinalmente v\'alido). O total prom.\ + repet.\ + evas.\ + EJA $\sim$100\% no EF, mas $\sim$92\% no EM, devido a transi\c{c}\~oes do 3\textsuperscript{o} EM para o ensino superior, modalidades n\~ao classificadas e abandono escolar que se manifesta em forma de migra\c{c}\~ao para o mercado de trabalho.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT / "T1_brasil_inter_por_serie_ano.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out_tex}")
