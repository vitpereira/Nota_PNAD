# -------------------------------------------------------------------------
# C16_distorcao_conditional.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Calcula as taxas de fluxo condicionais ao aluno iniciar o painel com
#   defasagem idade-serie de pelo menos dois anos (idade >= idade-padrao + 2).
#
#   Idade-padrao: entrada aos 6 anos no 1o EF.
#     1o EF: 6      4o EF: 9     7o EF: 12    1o EM: 15
#     2o EF: 7      5o EF: 10    8o EF: 13    2o EM: 16
#     3o EF: 8      6o EF: 11    9o EF: 14    3o EM: 17
#
# Inputs:
#   ../output/C14_transitions_v2.parquet
#
# Outputs:
#   ../output/T6_distorcao_conditional.csv
#   ../output/T6_distorcao_conditional.tex
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

print("Loading C14 transitions v2...", flush=True)
t = pd.read_parquet(OUT_DIR / "C14_transitions_v2.parquet")
print(f"  {len(t):,} transitions", flush=True)

# Compute idade-padrao based on nivel_t
# nivel 1 = 1o EF -> 6 anos
# nivel n in {1..9} -> 5 + n
# nivel 10 = 1o EM -> 15
# nivel 11 = 2o EM -> 16
# nivel 12 = 3o EM -> 17
def idade_padrao(n):
    if pd.isna(n): return np.nan
    n = float(n)
    if 1 <= n <= 9:
        return 5 + n
    if n == 10: return 15
    if n == 11: return 16
    if n == 12: return 17
    return np.nan

t["idade_padrao"] = t["nivel_t"].map(idade_padrao)
t["defasagem"] = t["idade_t"] - t["idade_padrao"]

# Flag: distorted = defasagem >= 2
t["distorted"] = (t["defasagem"] >= 2).astype(int)

# Compute flags (already done in C14; recompute for safety from raw)
t["any_eja_t1"] = t["any_eja_t1"].astype(bool)
t["flag_migracao_eja"] = t["any_eja_t1"].astype(int)
t["flag_evasao"] = (
    (t["freq_t1"] == 0) & (~t["any_eja_t1"])
).astype(int)
t["flag_promocao"] = (
    (t["freq_t1"] == 1) &
    (~t["any_eja_t1"]) &
    t["nivel_t1"].notna() &
    (t["nivel_t1"] > t["nivel_t"])
).astype(int)
t["flag_repetencia"] = (
    (t["freq_t1"] == 1) &
    (~t["any_eja_t1"]) &
    t["nivel_t1"].notna() &
    (t["nivel_t1"] == t["nivel_t"])
).astype(int)

# Drop missing t1 (attrition) and drop missing defasagem
t = t[t["freq_t1"].notna() & t["defasagem"].notna()].copy()
t["wt"] = t["wt_t"]
print(f"  Valid sample: {len(t):,}", flush=True)

# Aggregate by macroetapa x distorted (mean across all years 2018-2023, ex-COVID)
t_ex = t[
    t["ano_t"].between(2018, 2023) &
    (~t["ano_t"].isin([2020, 2021]))
].copy()
print(f"  2018-2023 ex-COVID: {len(t_ex):,}", flush=True)

def agg_group(g):
    return pd.Series({
        "prom":  np.average(g.flag_promocao, weights=g.wt),
        "rep":   np.average(g.flag_repetencia, weights=g.wt),
        "evas":  np.average(g.flag_evasao, weights=g.wt),
        "eja":   np.average(g.flag_migracao_eja, weights=g.wt),
        "n":     len(g),
    })

result = t_ex.groupby(["macroetapa_t", "distorted"]).apply(
    agg_group).reset_index()
result.to_csv(OUT_DIR / "T6_distorcao_conditional.csv", index=False)
print(f"\nSaved {OUT_DIR / 'T6_distorcao_conditional.csv'}", flush=True)
print(result, flush=True)

# Build LaTeX
def fmt_pct(x): return f"{x*100:.1f}"
def fmt_n(x): return f"{int(x):,}".replace(",", ".")

lines = []
lines.append("% Auto-gerado por C16_distorcao_conditional.py")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Taxas de fluxo condicionais \`a defasagem idade-s\'erie no in\'icio do painel, Brasil, m\'edia 2018--2023 (ex-COVID).}")
lines.append(r"\label{tab:distorcao}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrrrrrr}")
lines.append(r"\toprule")
lines.append(r"& \multicolumn{4}{c}{Taxas (\%)} & & \\")
lines.append(r"\cmidrule(lr){2-5}")
lines.append(r"Subgrupo & Promo\c{c}\~ao & Repet\^encia & Evas\~ao & Migra\c{c}\~ao EJA & Soma & N \\")
lines.append(r"\midrule")
for et in ["EF iniciais", "EF finais", "EM"]:
    lines.append(rf"\multicolumn{{7}}{{l}}{{\textit{{{et}}}}} \\")
    lines.append(r"\midrule")
    sub_em_dia = result[(result["macroetapa_t"] == et) & (result["distorted"] == 0)]
    sub_def    = result[(result["macroetapa_t"] == et) & (result["distorted"] == 1)]
    for label, sub in [("Em dia", sub_em_dia), ("Defasagem $\\geq 2$ anos", sub_def)]:
        if len(sub) == 0:
            continue
        r = sub.iloc[0]
        total = r.prom + r.rep + r.evas + r.eja
        lines.append(rf"{label} & {fmt_pct(r.prom)} & {fmt_pct(r.rep)} & {fmt_pct(r.evas)} & {fmt_pct(r.eja)} & {fmt_pct(total)} & {fmt_n(r.n)} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal da PNADC.")
lines.append(r"\item \textit{Notas:} Defasagem idade-s\'erie computada como diferen\c{c}a entre idade observada e idade-padr\~ao (entrada aos 6 anos no 1\textsuperscript{o} EF). Defasagem $\geq 2$ anos: idade $\geq$ idade-padr\~ao $+\,2$.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT_DIR / "T6_distorcao_conditional.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Saved {out_tex}", flush=True)
