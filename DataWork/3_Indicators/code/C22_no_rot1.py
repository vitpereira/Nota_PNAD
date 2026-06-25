# -------------------------------------------------------------------------
# C22_no_rot1.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   v5 com filtro explicito de rotacao 1.
#   Rotacao da observacao = (Trimestre - visita) mod 4. Rotacao 1 = 0.
#   Filtro: remove obs com rotacao = 0.
#   Tambem redefine abandono: primeira obs do ano vs ultima obs do ano
#   (em vez de exigir Q1 e Q4), aplicavel a rotacoes 2 e 3.
#
# Outputs:
#   ../output/T1_brasil_inter_v5_norot1.csv
#   ../output/T_abandono_norot1.csv / .tex
#   ../output/C22_transitions_v5_norot1.parquet
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np
import shutil

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

lookup = pd.read_parquet(OUT_DIR / "C19_v4_lookup.parquet")
for c in ["V3002", "V3014", "V3003", "V3003A", "V3006", "V2007", "V2009", "V1028"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")
lookup = lookup[lookup["V2009"].between(4, 24)].copy()

# Curso / nivel
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
lookup["in_eja"] = ((curso == 300) | (curso == 310)).astype(int)
lookup["in_regular"] = (~np.isnan(nivel)).astype(int)
lookup["freq_zero"] = (lookup["V3002"] == 2).astype(int)
lookup["concluiu"] = (lookup["V3014"] == 1).astype(int)

# Load link (need visita too!)
print("Loading link with visita...", flush=True)
link, _ = pyreadstat.read_dta(
    str(LINK),
    usecols=["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003",
              "person_id", "link_ok", "renda_dom_pc", "raca", "rede", "visita"]
)
link = link[link["link_ok"] == 1]
for c in ["UF", "UPA", "V1008", "V1014", "V2003", "visita"]:
    link[c] = link[c].astype(int)
    if c in lookup.columns:
        lookup[c] = lookup[c].astype(int)

# Rotacao: (Trimestre - visita) mod 4. Filter rotacao 1 (where mod == 0).
link["rot"] = ((link["Trimestre"] - link["visita"]) % 4).astype(int)
print("Rotacao distribution:", flush=True)
print(link["rot"].value_counts().sort_index(), flush=True)

# Build set of rotation-1 person_id (any obs with rot==0)
rot1_persons = set(link.loc[link["rot"] == 0, "person_id"].unique())
print(f"Persons in rotacao 1: {len(rot1_persons):,}", flush=True)
print(f"Persons total: {link['person_id'].nunique():,}", flush=True)

# Filter link to exclude rotacao 1 persons
link_filt = link[~link["person_id"].isin(rot1_persons)].copy()
print(f"Link after filter: {len(link_filt):,}", flush=True)

# Merge with lookup
merge_keys = ["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003"]
panel = link_filt.merge(lookup, on=merge_keys, how="inner")
del link, link_filt, lookup
print(f"Panel after merge: {len(panel):,}", flush=True)

# ============ v5 transitions: Q2-Q3 in both years ============
WIN = [2, 3]
sub = panel[panel["Trimestre"].isin(WIN)].copy()

# ref with max(nivel)
reg = sub[sub["nivel"].notna()].copy()
reg = reg.sort_values(["person_id", "Ano", "nivel", "Trimestre"],
                      ascending=[True, True, False, False])
ref_reg = reg.drop_duplicates(subset=["person_id", "Ano"], keep="first")[
    ["person_id", "Ano", "nivel", "V3006", "curso", "macroetapa",
     "Trimestre", "V1028", "V2009", "V2007", "raca", "renda_dom_pc", "rede"]
].copy()
ref_reg.columns = ["person_id", "Ano", "nivel_ref", "serie_ref", "curso_ref",
                    "macroetapa_ref", "trim_ref", "wt_ref", "idade_ref",
                    "sexo_ref", "raca_ref", "renda_ref", "rede_ref"]

# Aggregate flags
agg_w = sub.groupby(["person_id", "Ano"]).agg(
    any_in_reg=("in_regular", "max"),
    any_in_eja=("in_eja", "max"),
    any_freq_zero=("freq_zero", "max"),
    any_concluiu=("concluiu", "max"),
).reset_index()
refs = ref_reg.merge(agg_w, on=["person_id", "Ano"], how="outer")
del sub, reg

# Build transitions
t = refs[refs["any_in_reg"] == 1].copy()
t = t.rename(columns={"Ano": "ano_t", "nivel_ref": "nivel_t",
    "serie_ref": "serie_t", "curso_ref": "curso_t",
    "macroetapa_ref": "macroetapa_t", "trim_ref": "trim_t",
    "wt_ref": "wt_t", "idade_ref": "idade_t",
    "sexo_ref": "sexo_t", "raca_ref": "raca_t",
    "renda_ref": "renda_t", "rede_ref": "rede_t",
    "any_in_reg": "in_reg_t", "any_in_eja": "in_eja_t",
    "any_freq_zero": "freq_zero_t", "any_concluiu": "concluiu_t"})
t["ano_t1"] = t["ano_t"] + 1

t1 = refs.rename(columns={"Ano": "ano_t1", "nivel_ref": "nivel_t1",
    "serie_ref": "serie_t1", "curso_ref": "curso_t1",
    "macroetapa_ref": "macroetapa_t1", "trim_ref": "trim_t1",
    "any_in_reg": "in_reg_t1", "any_in_eja": "in_eja_t1",
    "any_freq_zero": "freq_zero_t1", "any_concluiu": "concluiu_t1",
})[["person_id", "ano_t1", "nivel_t1", "serie_t1", "macroetapa_t1",
    "in_reg_t1", "in_eja_t1", "freq_zero_t1", "concluiu_t1", "trim_t1"]]

trans = t.merge(t1, on=["person_id", "ano_t1"], how="left")
trans["has_t1"] = (trans["in_reg_t1"].fillna(0) + trans["in_eja_t1"].fillna(0)
                    + trans["freq_zero_t1"].fillna(0)) > 0
trans = trans[trans["ano_t"] <= 2023].copy()
for c in ["in_reg_t1", "in_eja_t1", "freq_zero_t1", "concluiu_t1"]:
    trans[c] = trans[c].fillna(0).astype(int)
t_main = trans[trans["has_t1"]].copy()
print(f"v5 norot1 transitions: {len(t_main):,}", flush=True)

# Flags
t_main["flag_migracao_eja"] = ((t_main["in_eja_t1"] == 1) & (t_main["in_reg_t1"] == 0)).astype(int)
t_main["flag_evasao_raw"] = ((t_main["freq_zero_t1"] == 1) & (t_main["in_reg_t1"] == 0)
                              & (t_main["in_eja_t1"] == 0)).astype(int)
t_main["flag_promocao_raw"] = ((t_main["in_reg_t1"] == 1) & t_main["nivel_t1"].notna()
                                & (t_main["nivel_t1"] > t_main["nivel_t"])).astype(int)
t_main["flag_repetencia_raw"] = ((t_main["in_reg_t1"] == 1) & t_main["nivel_t1"].notna()
                                  & (t_main["nivel_t1"] == t_main["nivel_t"])).astype(int)
correction = ((t_main["nivel_t"].isin([12, 13])) & (t_main["concluiu_t1"] == 1)
              & (t_main["flag_evasao_raw"] == 1))
t_main["correction_applied"] = correction.astype(int)
t_main["flag_promocao"] = t_main["flag_promocao_raw"]
t_main["flag_repetencia"] = t_main["flag_repetencia_raw"]
t_main["flag_evasao"] = t_main["flag_evasao_raw"]
t_main.loc[correction, "flag_promocao"] = 1
t_main.loc[correction, "flag_evasao"] = 0
t_main["wt"] = t_main["wt_t"]

t_main.to_parquet(OUT_DIR / "C22_transitions_v5_norot1.parquet", index=False)
print(f"Saved C22_transitions_v5_norot1.parquet", flush=True)

# Aggregate
rows = []
for (a, m), g in t_main.groupby(["ano_t", "macroetapa_t"]):
    rows.append({"ano_t": a, "macroetapa": m,
        "flag_promocao": np.average(g.flag_promocao, weights=g.wt),
        "flag_repetencia": np.average(g.flag_repetencia, weights=g.wt),
        "flag_evasao": np.average(g.flag_evasao, weights=g.wt),
        "flag_migracao_eja": np.average(g.flag_migracao_eja, weights=g.wt),
        "n_pessoa": len(g)})
agg = pd.DataFrame(rows)
agg = agg[agg["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()
agg.to_csv(OUT_DIR / "T1_brasil_inter_v5_norot1.csv", index=False)

print("\n=== v5 norot1 EF iniciais ===", flush=True)
ef = agg[agg["macroetapa"] == "EF iniciais"].sort_values("ano_t")
for _, r in ef.iterrows():
    print(f"  {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
          f"rep={r.flag_repetencia*100:.1f}% "
          f"evas={r.flag_evasao*100:.1f}% n={int(r.n_pessoa)}", flush=True)
print("\n=== v5 norot1 EM ===", flush=True)
em = agg[agg["macroetapa"] == "EM"].sort_values("ano_t")
for _, r in em.iterrows():
    print(f"  {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
          f"rep={r.flag_repetencia*100:.1f}% "
          f"evas={r.flag_evasao*100:.1f}% n={int(r.n_pessoa)}", flush=True)

# ============ Abandono redefinido: first obs vs last obs in same year ============
# Sample: kids with >= 2 obs in same year, in regular EF/EM
# Numerator: freq=0 at last obs, freq=1 at first obs
print("\n=== Abandono norot1 (first obs vs last obs in year) ===", flush=True)
panel_full = panel.copy()  # already excludes rot 1
# For each person-year with >= 2 obs, get first and last
panel_full = panel_full.sort_values(["person_id", "Ano", "Trimestre"])
panel_full["obs_idx"] = panel_full.groupby(["person_id", "Ano"]).cumcount()
n_obs = panel_full.groupby(["person_id", "Ano"]).size().reset_index(name="n_obs_year")
panel_full = panel_full.merge(n_obs, on=["person_id", "Ano"], how="left")
panel_full = panel_full[panel_full["n_obs_year"] >= 2].copy()

# Get first obs (rank 0) and last obs
first = panel_full[panel_full["obs_idx"] == 0][[
    "person_id", "Ano", "in_regular", "macroetapa", "V3002", "V1028", "Trimestre"
]].rename(columns={"in_regular": "reg_first", "macroetapa": "me_first",
                   "V3002": "freq_first", "V1028": "wt_first",
                   "Trimestre": "trim_first"})

last_idx = panel_full.groupby(["person_id", "Ano"])["obs_idx"].transform("max")
last = panel_full[panel_full["obs_idx"] == last_idx][[
    "person_id", "Ano", "V3002", "Trimestre", "in_regular", "in_eja"
]].rename(columns={"V3002": "freq_last", "Trimestre": "trim_last",
                   "in_regular": "reg_last", "in_eja": "eja_last"})

aband = first.merge(last, on=["person_id", "Ano"], how="inner")
# Universe: in regular EF/EM in first obs
aband = aband[aband["reg_first"] == 1].copy()
# Abandono: not frequenting in last obs
aband["flag_abandono"] = (aband["freq_last"] == 2).astype(int)
aband["flag_eja_intra"] = (aband["eja_last"] == 1).astype(int)
aband = aband[aband["me_first"].isin(["EF iniciais", "EF finais", "EM"])].copy()

# Aggregate
rows = []
for (a, m), g in aband.groupby(["Ano", "me_first"]):
    rows.append({"ano_t": a, "macroetapa": m,
        "flag_abandono": np.average(g.flag_abandono, weights=g.wt_first),
        "flag_eja_intra": np.average(g.flag_eja_intra, weights=g.wt_first),
        "n": len(g)})
ab = pd.DataFrame(rows)
ab.to_csv(OUT_DIR / "T_abandono_norot1.csv", index=False)
print(f"Saved T_abandono_norot1.csv. EM samples:", flush=True)
em_ab = ab[ab["macroetapa"] == "EM"].sort_values("ano_t")
for _, r in em_ab.iterrows():
    print(f"  {int(r.ano_t)}: aband={r.flag_abandono*100:.2f}% n={int(r.n)}", flush=True)

# ============ LaTeX output: update T1 ============
def fmt_pct(x):
    try: return f"{float(x)*100:.1f}"
    except: return "---"
def fmt_n(x):
    try: return f"{int(float(x)):,}".replace(",", ".")
    except: return "---"

# Backup
old = OUT_DIR / "T1_brasil_inter_por_serie_ano.tex"
bk = OUT_DIR / "T1_v5_with_rot1.tex"
if old.exists() and not bk.exists():
    shutil.copy(old, bk)

intra = {(int(r["ano_t"]), r["macroetapa"]): r
          for _, r in ab.iterrows()}

panels = [
    ("EF iniciais", r"\textit{Painel A: EF iniciais (1\textsuperscript{o}--5\textsuperscript{o} ano)}"),
    ("EF finais",   r"\textit{Painel B: EF finais (6\textsuperscript{o}--9\textsuperscript{o} ano)}"),
    ("EM",          r"\textit{Painel C: Ensino M\'edio (regular + t\'ecnico, 1\textsuperscript{o}--4\textsuperscript{o} ano)}"),
]
lines = []
lines.append("% C22 v5 norot1")
lines.append(r"\begin{table}[htbp]\centering")
lines.append(r"\caption{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano. Households de rota\c{c}\~ao~1 (entrada em $Q_1$ do ano $y$) exclu\'idos.}")
lines.append(r"\label{tab:t1_brasil}")
lines.append(r"\begin{threeparttable}\small")
lines.append(r"\begin{tabular}{lrrrrrr}\toprule")
lines.append(r"Ano & Promo\c{c}\~ao & Repet\^encia & Evas\~ao & Migra\c{c}\~ao EJA & Abandono$^{a}$ & N \\")
lines.append(r"    & (\%) & (\%) & (\%) & (\%) & (\%) & \\")
lines.append(r"\midrule")
for etapa, label in panels:
    lines.append(rf"\multicolumn{{7}}{{l}}{{{label}}} \\")
    lines.append(r"\midrule")
    sub = agg[agg["macroetapa"] == etapa].sort_values("ano_t")
    for _, r in sub.iterrows():
        y = int(r.ano_t)
        ri = intra.get((y, etapa), {})
        ano_lbl = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(rf"{ano_lbl} & {fmt_pct(r.flag_promocao)} & {fmt_pct(r.flag_repetencia)} & "
                      rf"{fmt_pct(r.flag_evasao)} & {fmt_pct(r.flag_migracao_eja)} & "
                      rf"{fmt_pct(ri.get('flag_abandono') if isinstance(ri, dict) else getattr(ri, 'flag_abandono', None))} & {fmt_n(r.n_pessoa)} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} PNADC trimestral, IBGE. Janela: $t,t{+}1 \in \{Q_2,Q_3\}$ com $\max(\textit{nivel})$. Households com primeira visita em $Q_1$ exclu\'idos.")
lines.append(r"\item $^{a}$Abandono: primeira obs.\ vs.\ \'ultima obs.\ no mesmo ano $t$ (sub-amostra de rota\c{c}\~oes 2 e 3 com $\geq 2$ obs.).")
lines.append(r"\item $^{\dagger}$Anos COVID-19.")
lines.append(r"\end{tablenotes}\end{threeparttable}\end{table}")
(OUT_DIR / "T1_brasil_inter_por_serie_ano.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote T1_brasil_inter_por_serie_ano.tex (v5 norot1)", flush=True)
print("\nDone.", flush=True)
