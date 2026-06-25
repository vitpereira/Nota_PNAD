# -------------------------------------------------------------------------
# C20_v5_main.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Versao v5 (principal). Combina:
#     - Janela v3: t in {Q2,Q3}, t+1 in {Q2,Q3} (revertendo a expansao v4)
#     - max(nivel) em ambas as janelas
#     - Correcao V3014 sempre aplicada (3o EM regular ou 4o EM tecnico)
#     - Inclusao de EM tecnico (V3003A=07) com niveis 10-13
#     - Entrada no sistema (recalculada com mesma janela)
#
#   Spec A (v4: t{Q2-Q4}) e Spec B (v4: t{Q3,Q4}) ficam como sensibilidade.
#
# Inputs:
#   ../output/C19_v4_lookup.parquet
#   ../../2_PanelBuild/tmp/pnadc_linked.dta
#
# Outputs:
#   ../output/T1_brasil_inter_por_serie_ano.tex  (NEW main, v5)
#   ../output/T1_brasil_inter_v5_main.csv
#   ../output/C20_transitions_v5.parquet
#   ../output/T_entrada_no_sistema.tex           (recalculada)
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np
import shutil

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

lookup_path = OUT_DIR / "C19_v4_lookup.parquet"
print(f"Loading {lookup_path}", flush=True)
lookup = pd.read_parquet(lookup_path)
print(f"  rows: {len(lookup):,}", flush=True)

for c in ["V3002", "V3014", "V3003", "V3003A", "V3006",
          "V2007", "V2009", "V1028"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")
lookup = lookup[lookup["V2009"].between(4, 24)].copy()

# Build curso, nivel (incluindo técnico EM)
ano = lookup["Ano"].values
v3 = lookup["V3003"].values
v3a = lookup["V3003A"].values
curso = np.full(len(lookup), 900.0)
mp = ano <= 2015
curso[mp & (v3 == 3)] = 100
curso[mp & (v3 == 4)] = 300
curso[mp & (v3 == 5)] = 200
curso[mp & (v3 == 6)] = 310
curso[mp & (v3 == 7)] = 210
mo = ano >= 2016
curso[mo & (v3a == 4)] = 100
curso[mo & (v3a == 5)] = 300
curso[mo & (v3a == 6)] = 200
curso[mo & (v3a == 7)] = 210
both_na = np.isnan(v3) & np.isnan(v3a)
curso[both_na] = np.nan
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
me[curso == 300] = "EJA EF"
me[curso == 310] = "EJA EM"
lookup["macroetapa"] = me

lookup["in_eja"] = ((curso == 300) | (curso == 310)).astype(int)
lookup["in_regular"] = (~np.isnan(nivel)).astype(int)
lookup["freq_zero"] = (lookup["V3002"] == 2).astype(int)
lookup["freq_one"] = (lookup["V3002"] == 1).astype(int)
lookup["concluiu"] = (lookup["V3014"] == 1).astype(int)

# Merge with link
print("Loading link...", flush=True)
link, _ = pyreadstat.read_dta(
    str(LINK),
    usecols=["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003",
              "person_id", "link_ok", "renda_dom_pc", "raca"]
)
link = link[link["link_ok"] == 1]
for c in ["UF", "UPA", "V1008", "V1014", "V2003"]:
    link[c] = link[c].astype(int)
    lookup[c] = lookup[c].astype(int)
merge_keys = ["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003"]
panel = link.merge(lookup, on=merge_keys, how="inner")
del link, lookup
print(f"Merged panel: {len(panel):,}", flush=True)

# ============ v5: Q2-Q3 window in both t and t+1 ============
WINDOW = [2, 3]

print(f"\nBuilding refs for v5 (Q2-Q3 in both t and t+1)...", flush=True)
sub = panel[panel["Trimestre"].isin(WINDOW)].copy()
print(f"  Q2-Q3 obs: {len(sub):,}", flush=True)

# Best ref with max(nivel)
reg = sub[sub["nivel"].notna()].copy()
reg = reg.sort_values(["person_id", "Ano", "nivel", "Trimestre"],
                      ascending=[True, True, False, False])
ref_reg = reg.drop_duplicates(subset=["person_id", "Ano"], keep="first")[
    ["person_id", "Ano", "nivel", "V3006", "curso",
     "macroetapa", "Trimestre", "V1028", "V2009",
     "V2007", "raca", "renda_dom_pc"]
].copy()
ref_reg.columns = ["person_id", "Ano", "nivel_ref", "serie_ref", "curso_ref",
                    "macroetapa_ref", "trim_ref", "wt_ref", "idade_ref",
                    "sexo_ref", "raca_ref", "renda_ref"]
del reg

# Aggregate flags
agg = sub.groupby(["person_id", "Ano"]).agg(
    any_in_regular=("in_regular", "max"),
    any_in_eja=("in_eja", "max"),
    any_freq_zero=("freq_zero", "max"),
    any_freq_one=("freq_one", "max"),
    any_concluiu=("concluiu", "max"),
    max_idade=("V2009", "max"),
    any_wt=("V1028", "max"),
).reset_index()
refs = ref_reg.merge(agg, on=["person_id", "Ano"], how="outer")
del sub

# Split refs for t and t+1
print("Building t -> t+1 transitions...", flush=True)
t = refs[refs["any_in_regular"] == 1].copy()
t = t.rename(columns={
    "Ano": "ano_t", "nivel_ref": "nivel_t",
    "serie_ref": "serie_t", "curso_ref": "curso_t",
    "macroetapa_ref": "macroetapa_t", "trim_ref": "trim_t",
    "wt_ref": "wt_t", "idade_ref": "idade_t",
    "sexo_ref": "sexo_t", "raca_ref": "raca_t",
    "renda_ref": "renda_t",
    "any_in_regular": "in_reg_t",
    "any_in_eja": "in_eja_t",
    "any_freq_zero": "freq_zero_t",
    "any_freq_one": "freq_one_t",
    "any_concluiu": "concluiu_t",
})
t["ano_t1"] = t["ano_t"] + 1

t1 = refs.rename(columns={
    "Ano": "ano_t1", "nivel_ref": "nivel_t1",
    "serie_ref": "serie_t1", "curso_ref": "curso_t1",
    "macroetapa_ref": "macroetapa_t1", "trim_ref": "trim_t1",
    "any_in_regular": "in_reg_t1",
    "any_in_eja": "in_eja_t1",
    "any_freq_zero": "freq_zero_t1",
    "any_freq_one": "freq_one_t1",
    "any_concluiu": "concluiu_t1",
})[["person_id", "ano_t1", "nivel_t1", "serie_t1", "curso_t1",
    "macroetapa_t1", "trim_t1", "in_reg_t1", "in_eja_t1",
    "freq_zero_t1", "freq_one_t1", "concluiu_t1"]]

trans = t.merge(t1, on=["person_id", "ano_t1"], how="left")
trans["has_t1"] = (trans["in_reg_t1"].fillna(0)
                    + trans["in_eja_t1"].fillna(0)
                    + trans["freq_zero_t1"].fillna(0)) > 0
trans = trans[trans["ano_t"] <= 2023].copy()
print(f"  transitions: {len(trans):,}, with t+1: {trans['has_t1'].sum():,}",
      flush=True)

# Flags
for c in ["in_reg_t1", "in_eja_t1", "freq_zero_t1", "concluiu_t1"]:
    trans[c] = trans[c].fillna(0).astype(int)
t_main = trans[trans["has_t1"]].copy()

t_main["flag_migracao_eja"] = (
    (t_main["in_eja_t1"] == 1) & (t_main["in_reg_t1"] == 0)
).astype(int)
t_main["flag_evasao_raw"] = (
    (t_main["freq_zero_t1"] == 1) &
    (t_main["in_reg_t1"] == 0) &
    (t_main["in_eja_t1"] == 0)
).astype(int)
t_main["flag_promocao_raw"] = (
    (t_main["in_reg_t1"] == 1) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] > t_main["nivel_t"])
).astype(int)
t_main["flag_repetencia_raw"] = (
    (t_main["in_reg_t1"] == 1) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] == t_main["nivel_t"])
).astype(int)

# V3014 correction
correction = (
    (t_main["nivel_t"].isin([12, 13])) &
    (t_main["concluiu_t1"] == 1) &
    (t_main["flag_evasao_raw"] == 1)
)
t_main["correction_applied"] = correction.astype(int)
t_main["flag_promocao"] = t_main["flag_promocao_raw"]
t_main["flag_repetencia"] = t_main["flag_repetencia_raw"]
t_main["flag_evasao"] = t_main["flag_evasao_raw"]
t_main.loc[correction, "flag_promocao"] = 1
t_main.loc[correction, "flag_evasao"] = 0
t_main["wt"] = t_main["wt_t"]

print(f"v5 main: {len(t_main):,}, corrected: {t_main['correction_applied'].sum():,}",
      flush=True)
t_main.to_parquet(OUT_DIR / "C20_transitions_v5.parquet", index=False)

# Aggregate
rows = []
for (a, m), g in t_main.groupby(["ano_t", "macroetapa_t"]):
    rows.append({
        "ano_t": a, "macroetapa": m,
        "flag_promocao": np.average(g.flag_promocao, weights=g.wt),
        "flag_repetencia": np.average(g.flag_repetencia, weights=g.wt),
        "flag_evasao": np.average(g.flag_evasao, weights=g.wt),
        "flag_migracao_eja": np.average(g.flag_migracao_eja, weights=g.wt),
        "n_pessoa": len(g),
    })
agg = pd.DataFrame(rows)
agg = agg[agg["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()
agg.to_csv(OUT_DIR / "T1_brasil_inter_v5_main.csv", index=False)

print("\n=== v5 (Q2-Q3 + V3014 + técnico + entrada) ===", flush=True)
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n  {et}:", flush=True)
    sub_agg = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub_agg.iterrows():
        total = r.flag_promocao + r.flag_repetencia + r.flag_evasao + r.flag_migracao_eja
        print(f"    {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
              f"rep={r.flag_repetencia*100:.1f}% "
              f"evas={r.flag_evasao*100:.1f}% "
              f"eja={r.flag_migracao_eja*100:.1f}% "
              f"sum={total*100:.1f}% n={int(r.n_pessoa)}", flush=True)

# ============ ENTRADA NO SISTEMA (recalculada com janela v5) ============
print("\n=== ENTRADA (janela v5: Q2-Q3) ===", flush=True)
# Use refs (already restricted to Q2-Q3)
ref_t_full = refs.copy()
ref_t_full = ref_t_full.rename(columns={
    "Ano": "ano_t", "any_in_regular": "in_reg_t",
    "any_in_eja": "in_eja_t", "wt_ref": "wt_t",
    "idade_ref": "idade_t", "max_idade": "max_idade_t",
    "any_wt": "any_wt_t",
})
ref_t_full["ano_t1"] = ref_t_full["ano_t"] + 1

ref_t1_full = refs.rename(columns={
    "Ano": "ano_t1", "any_in_regular": "in_reg_t1",
})[["person_id", "ano_t1", "in_reg_t1"]]

ent = ref_t_full.merge(ref_t1_full, on=["person_id", "ano_t1"], how="left")
ent = ent[ent["in_reg_t1"].notna()].copy()
ent = ent[ent["in_reg_t"] == 0].copy()
ent["idade_use"] = ent["idade_t"].fillna(ent["max_idade_t"])
ent["wt_use"] = ent["wt_t"].fillna(ent["any_wt_t"])
ent = ent[ent["idade_use"].notna() & ent["wt_use"].notna()].copy()
ent = ent[ent["ano_t"] <= 2023].copy()
ent["flag_entrada"] = (ent["in_reg_t1"] == 1).astype(int)
print(f"Entrada universe: {len(ent):,}", flush=True)

def idade_bin(a):
    if a <= 6: return "4-6 anos"
    if a <= 10: return "7-10 anos"
    if a <= 14: return "11-14 anos"
    if a <= 17: return "15-17 anos"
    return "18-24 anos"
ent["idade_bin"] = ent["idade_use"].apply(idade_bin)

rows = []
for ib in ["4-6 anos", "7-10 anos", "11-14 anos", "15-17 anos", "18-24 anos"]:
    g = ent[ent["idade_bin"] == ib]
    if len(g) == 0:
        rows.append({"idade_bin": ib, "taxa_entrada": np.nan, "n": 0})
        continue
    rows.append({
        "idade_bin": ib,
        "taxa_entrada": np.average(g.flag_entrada, weights=g.wt_use),
        "n": len(g),
    })
ent_avg = pd.DataFrame(rows)
ent_avg.to_csv(OUT_DIR / "T_entrada_no_sistema.csv", index=False)
print(ent_avg.to_string(index=False), flush=True)

# By year
rows = []
for (a, ib), g in ent.groupby(["ano_t", "idade_bin"]):
    if len(g) < 20: continue
    rows.append({"ano_t": a, "idade_bin": ib,
                  "taxa_entrada": np.average(g.flag_entrada, weights=g.wt_use),
                  "n": len(g)})
ent_year = pd.DataFrame(rows)
ent_year.to_csv(OUT_DIR / "T_entrada_por_ano.csv", index=False)

# ============ LATEX outputs ============
def fmt_pct(x):
    try: return f"{float(x)*100:.1f}"
    except: return "---"
def fmt_n(x):
    try: return f"{int(float(x)):,}".replace(",", ".")
    except: return "---"

# Backup current T1
backup_v4 = OUT_DIR / "T1_v4_specA.tex"
old_tex = OUT_DIR / "T1_brasil_inter_por_serie_ano.tex"
if old_tex.exists() and not backup_v4.exists():
    shutil.copy(old_tex, backup_v4)

# Load intra
intra = {}
intra_csv = OUT_DIR / "T_abandono_fullyear.csv"
if intra_csv.exists():
    import csv
    with open(intra_csv, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            intra[(int(r["ano_t"]), r["macroetapa"])] = r

years = sorted(agg["ano_t"].unique())
panels = [
    ("EF iniciais", r"\textit{Painel A: EF iniciais (1\textsuperscript{o}--5\textsuperscript{o} ano)}"),
    ("EF finais",   r"\textit{Painel B: EF finais (6\textsuperscript{o}--9\textsuperscript{o} ano)}"),
    ("EM",          r"\textit{Painel C: Ensino M\'edio (regular + t\'ecnico, 1\textsuperscript{o}--4\textsuperscript{o} ano)}"),
]

lines = []
lines.append("% C20 v5 - main: Q2-Q3 + max(nivel) + V3014 + tecnico + entrada")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano. Janela: $t \\in \\{Q_2, Q_3\\}$, $t{+}1 \\in \\{Q_2, Q_3\\}$, $\\max(\\textit{nivel})$ em ambas. Inclui EM t\'ecnico. Conclus\~ao do 3\textsuperscript{o} EM e 4\textsuperscript{o} EM t\'ecnico via $V3014=1$ classificada como promo\c{c}\~ao.}")
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
    sub_agg = agg[agg["macroetapa"] == etapa].sort_values("ano_t")
    for _, r in sub_agg.iterrows():
        y = int(r.ano_t)
        ri = intra.get((y, etapa), {})
        ano_label = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(rf"{ano_label} & {fmt_pct(r.flag_promocao)} & {fmt_pct(r.flag_repetencia)} & "
                      rf"{fmt_pct(r.flag_evasao)} & {fmt_pct(r.flag_migracao_eja)} & "
                      rf"{fmt_pct(ri.get('flag_abandono'))} & {fmt_n(r.n_pessoa)} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal PNADC trimestral, IBGE.")
lines.append(r"\item $^{a}$Abandono: Tabela~\ref{tab:abandono_fullyear} (sub-amostra Q1--Q4 do mesmo ano).")
lines.append(r"\item $^{\dagger}$Anos COVID-19. Interpretar com cautela.")
lines.append(r"\item Sensibilidades com janelas alternativas (Spec A: $Q_2$--$Q_4$ em $t$; Spec B: $Q_3$--$Q_4$ em $t$, $Q_2$--$Q_4$ em $t{+}1$) reportadas na Se\c{c}\~ao~\ref{sec:robustez}.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")
(OUT_DIR / "T1_brasil_inter_por_serie_ano.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nWrote T1_brasil_inter_por_serie_ano.tex (v5)", flush=True)

# Entrada LaTeX
lines = []
lines.append("% C20 entrada v5")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Taxa de entrada no sistema escolar regular (EF + EM regular + t\'ecnico) por faixa et\'aria, Brasil, m\'edia 2012--2023.}")
lines.append(r"\label{tab:entrada_sistema}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrr}")
lines.append(r"\toprule")
lines.append(r"Faixa et\'aria em $t$ & Taxa de entrada (\%) & N \\")
lines.append(r"\midrule")
for _, r in ent_avg.iterrows():
    lines.append(rf"{r.idade_bin} & {fmt_pct(r.taxa_entrada)} & {fmt_n(r.n)} \\")
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal PNADC, $Q_2$--$Q_3$ de $t$ e $Q_2$--$Q_3$ de $t+1$.")
lines.append(r"\item \textit{Universo:} indiv\'iduos de 4--24 anos em $t$ n\~ao observados em EF/EM regular ou t\'ecnico em $Q_2$/$Q_3$ de $t$. \textit{Numerador:} matriculados em $Q_2$/$Q_3$ de $t+1$.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")
(OUT_DIR / "T_entrada_no_sistema.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("\nDone.", flush=True)
