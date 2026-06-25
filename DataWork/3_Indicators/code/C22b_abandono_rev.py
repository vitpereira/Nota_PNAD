# -------------------------------------------------------------------------
# C22b_abandono_rev.py
# -------------------------------------------------------------------------
# Description:
#   Abandono revisado: primeira obs vs ultima obs do ano, excluindo rotacao 1.
#   Compute direct from C19 lookup (parquet) for speed.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np
import sys

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

print("Loading lookup...", flush=True)
lookup = pd.read_parquet(OUT_DIR / "C19_v4_lookup.parquet",
                          columns=["UF", "UPA", "V1008", "V1014", "V2003",
                                   "V3002", "V3003", "V3003A", "V3006",
                                   "V2009", "V1028", "Ano", "Trimestre"])
for c in ["V3002", "V3003", "V3003A", "V3006", "V2009", "V1028"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")
lookup = lookup[lookup["V2009"].between(4, 24)].copy()
print(f"  {len(lookup):,} rows", flush=True)

# Build curso, nivel, macroetapa, in_regular
ano = lookup["Ano"].values; v3 = lookup["V3003"].values; v3a = lookup["V3003A"].values
curso = np.full(len(lookup), 900.0)
mp = ano <= 2015
curso[mp & (v3 == 3)] = 100; curso[mp & (v3 == 4)] = 300
curso[mp & (v3 == 5)] = 200; curso[mp & (v3 == 6)] = 310; curso[mp & (v3 == 7)] = 210
mo = ano >= 2016
curso[mo & (v3a == 4)] = 100; curso[mo & (v3a == 5)] = 300
curso[mo & (v3a == 6)] = 200; curso[mo & (v3a == 7)] = 210
curso[np.isnan(v3) & np.isnan(v3a)] = np.nan
lookup["curso"] = curso

serie = lookup["V3006"].values
nivel = np.full(len(lookup), np.nan)
nivel[(curso == 100) & (serie >= 1) & (serie <= 9)] = serie[(curso == 100) & (serie >= 1) & (serie <= 9)]
nivel[(curso == 200) & (serie >= 1) & (serie <= 3)] = 9 + serie[(curso == 200) & (serie >= 1) & (serie <= 3)]
nivel[(curso == 210) & (serie >= 1) & (serie <= 4)] = 9 + serie[(curso == 210) & (serie >= 1) & (serie <= 4)]
lookup["nivel"] = nivel

me = np.full(len(lookup), None, dtype=object)
me[(nivel >= 1) & (nivel <= 5)] = "EF iniciais"
me[(nivel >= 6) & (nivel <= 9)] = "EF finais"
me[(nivel >= 10) & (nivel <= 13)] = "EM"
me[curso == 300] = "EJA EF"; me[curso == 310] = "EJA EM"
lookup["macroetapa"] = me
lookup["in_regular"] = (~np.isnan(nivel)).astype(int)
lookup["in_eja"] = ((curso == 300) | (curso == 310)).astype(int)

# Need visita to identify rotação. Pull from .dta — but that's slow.
# Instead: identify rotação 1 households by HH key = (UF, UPA, V1008, V1014).
# Heuristic: a household is rotação 1 if at any trimestre we see it with V3002 obs and (Trimestre, visita) of rot 1.
# Better approach: since hh_id = UF_UPA_V1008_V1014 is stable, find HH that appear in Q1 of multiple years.
# A rot-1 HH appears Q1y, Q2y, Q3y, Q4y, Q1y+1 (5 trimestres including 2 Q1s)
# A rot-2 HH appears Q2y, Q3y, Q4y, Q1y+1, Q2y+1 (1 Q1)
# A rot-3 HH appears Q3y, Q4y, Q1y+1, Q2y+1, Q3y+1 (1 Q1)
# A rot-4 HH appears Q4y, Q1y+1, Q2y+1, Q3y+1, Q4y+1 (1 Q1)
# So: rot 1 HH have 2 obs in Q1, others have 0 or 1.

lookup["hh_key"] = (lookup["UF"].astype(str) + "_"
                     + lookup["UPA"].astype(str) + "_"
                     + lookup["V1008"].astype(str) + "_"
                     + lookup["V1014"].astype(str))

print("Identifying rot 1 households...", flush=True)
hh_q1count = lookup[lookup["Trimestre"] == 1].groupby("hh_key").size()
rot1_hh = set(hh_q1count[hh_q1count >= 2].index)
print(f"  Rot 1 HHs: {len(rot1_hh):,}", flush=True)

# Filter out rot 1
lookup_norot1 = lookup[~lookup["hh_key"].isin(rot1_hh)].copy()
print(f"  After filter: {len(lookup_norot1):,}", flush=True)

# Compute abandono: first vs last obs in year, in regular EF/EM
# pid = hh_key + V2003
lookup_norot1["pid"] = lookup_norot1["hh_key"] + "_" + lookup_norot1["V2003"].astype(str)

# Filter: needs >=2 obs per (pid, Ano), first obs must be in regular EF/EM
print("Aggregating per pid x ano...", flush=True)
sub = lookup_norot1[["pid", "Ano", "Trimestre", "in_regular", "macroetapa",
                       "V3002", "in_eja", "V1028"]].copy()

# Get first and last obs per (pid, Ano)
sub = sub.sort_values(["pid", "Ano", "Trimestre"])
first = sub.drop_duplicates(subset=["pid", "Ano"], keep="first").copy()
last = sub.drop_duplicates(subset=["pid", "Ano"], keep="last").copy()

# Count obs per pid-Ano
n_obs = sub.groupby(["pid", "Ano"]).size().reset_index(name="n_obs")

first = first.rename(columns={"in_regular": "reg_first", "macroetapa": "me_first",
                                "V3002": "freq_first", "in_eja": "eja_first",
                                "V1028": "wt_first", "Trimestre": "trim_first"})
last = last.rename(columns={"in_regular": "reg_last", "macroetapa": "me_last",
                              "V3002": "freq_last", "in_eja": "eja_last",
                              "Trimestre": "trim_last"})[["pid", "Ano", "freq_last",
                                                            "trim_last", "reg_last", "eja_last", "me_last"]]

ab = first.merge(last, on=["pid", "Ano"], how="inner")
ab = ab.merge(n_obs, on=["pid", "Ano"], how="left")
ab = ab[ab["n_obs"] >= 2].copy()
ab = ab[ab["reg_first"] == 1].copy()  # universe: in regular EF/EM in first obs
ab["flag_abandono"] = (ab["freq_last"] == 2).astype(int)
ab["flag_eja_intra"] = (ab["eja_last"] == 1).astype(int)
ab = ab[ab["me_first"].isin(["EF iniciais", "EF finais", "EM"])].copy()
print(f"  Abandono sample: {len(ab):,}", flush=True)

# Aggregate
rows = []
for (a, m), g in ab.groupby(["Ano", "me_first"]):
    rows.append({"ano_t": a, "macroetapa": m,
        "flag_abandono": np.average(g.flag_abandono, weights=g.wt_first),
        "flag_eja_intra": np.average(g.flag_eja_intra, weights=g.wt_first),
        "n": len(g)})
agg = pd.DataFrame(rows)
agg.to_csv(OUT_DIR / "T_abandono_norot1.csv", index=False)
print(f"\nSaved T_abandono_norot1.csv", flush=True)

# Print summary
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n--- {et} ---", flush=True)
    sub_agg = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub_agg.iterrows():
        print(f"  {int(r.ano_t)}: aband={r.flag_abandono*100:.2f}% "
              f"eja_intra={r.flag_eja_intra*100:.2f}% n={int(r.n)}", flush=True)

# LaTeX
def fmt_pct(x):
    try: return f"{float(x)*100:.1f}"
    except: return "---"
def fmt_n(x):
    try: return f"{int(float(x)):,}".replace(",", ".")
    except: return "---"

lines = []
lines.append("% C22b abandono norot1")
lines.append(r"\begin{table}[htbp]\centering")
lines.append(r"\caption{Taxa de abandono intra-ano (primeira obs.\ vs.\ \'ultima obs.\ do mesmo ano), households de rota\c{c}\~ao 1 exclu\'idos, Brasil, 2012--2024.}")
lines.append(r"\label{tab:abandono_fullyear}")
lines.append(r"\begin{threeparttable}\small")
lines.append(r"\begin{tabular}{lrrr}\toprule")
lines.append(r"Ano & Abandono (\%) & Migra\c{c}\~ao EJA intra (\%) & N \\\midrule")
for et in ["EF iniciais", "EF finais", "EM"]:
    lines.append(rf"\multicolumn{{4}}{{l}}{{\textit{{{et}}}}} \\")
    lines.append(r"\midrule")
    sub_agg = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub_agg.iterrows():
        y = int(r.ano_t)
        ano_lbl = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(rf"{ano_lbl} & {fmt_pct(r.flag_abandono)} & {fmt_pct(r.flag_eja_intra)} & {fmt_n(r.n)} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} PNADC trimestral. Households com primeira visita em $Q_1$ (rota\c{c}\~ao 1) exclu\'idos.")
lines.append(r"\item Universo: alunos em regular EF/EM/t\'ecnico na primeira observa\c{c}\~ao do ano. Numerador: $V3002 = 2$ na \'ultima observa\c{c}\~ao do mesmo ano (rota\c{c}\~oes 2 e 3 cobrem $Q_2$--$Q_4$).")
lines.append(r"\item $^{\dagger}$Anos COVID-19.")
lines.append(r"\end{tablenotes}\end{threeparttable}\end{table}")
out_tex = OUT_DIR / "T_abandono_fullyear.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved {out_tex}", flush=True)
