# -------------------------------------------------------------------------
# C19b_entrada_patch.py
# -------------------------------------------------------------------------
# Patch para calcular entrada no sistema usando refs com weight de qualquer
# observação da janela (não apenas das em regular).
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# Load v4 lookup
lookup = pd.read_parquet(OUT_DIR / "C19_v4_lookup.parquet")
print(f"Lookup: {len(lookup):,}", flush=True)

# Type cast
for c in ["V3002", "V3014", "V3003", "V3003A", "V3006",
          "V2007", "V2009", "V1028"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")

lookup = lookup[lookup["V2009"].between(4, 24)].copy()

# Build curso, nivel (compact reproduction)
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
lookup["in_regular"] = (lookup["nivel"].notna()).astype(int)

# Load link
print("Loading link...", flush=True)
link, _ = pyreadstat.read_dta(
    str(ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"),
    usecols=["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003",
              "person_id", "link_ok"]
)
link = link[link["link_ok"] == 1]
for c in ["UF", "UPA", "V1008", "V1014", "V2003"]:
    link[c] = link[c].astype(int)
    lookup[c] = lookup[c].astype(int)

merge_keys = ["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003"]
panel = link.merge(lookup, on=merge_keys, how="inner")
del link, lookup
print(f"Panel: {len(panel):,}", flush=True)

# Build per-person-year for Spec A windows
def aggregate_window(panel, quarters):
    sub = panel[panel["Trimestre"].isin(quarters)]
    # For each person-year:
    #   - any in regular
    #   - idade max
    #   - V1028 (max, or first non-NaN)
    agg = sub.groupby(["person_id", "Ano"]).agg(
        any_in_regular=("in_regular", "max"),
        max_idade=("V2009", "max"),
        wt=("V1028", "max"),
    ).reset_index()
    return agg

print("Aggregating Spec A t window (Q2-Q4)...", flush=True)
agg_t = aggregate_window(panel, [2, 3, 4]).rename(
    columns={"Ano": "ano_t", "any_in_regular": "in_reg_t",
              "max_idade": "idade_t", "wt": "wt_t"})
agg_t["ano_t1"] = agg_t["ano_t"] + 1

print("Aggregating Spec A t+1 window (Q2-Q3)...", flush=True)
agg_t1 = aggregate_window(panel, [2, 3]).rename(
    columns={"Ano": "ano_t1", "any_in_regular": "in_reg_t1"})[
    ["person_id", "ano_t1", "in_reg_t1"]]
del panel

ent = agg_t.merge(agg_t1, on=["person_id", "ano_t1"], how="left")
ent = ent[ent["in_reg_t1"].notna()].copy()
ent = ent[ent["in_reg_t"] == 0].copy()  # NOT in regular in t
ent = ent[ent["idade_t"].notna() & ent["wt_t"].notna()].copy()
ent = ent[ent["ano_t"] <= 2023].copy()
ent["flag_entrada"] = (ent["in_reg_t1"] == 1).astype(int)
print(f"Entrada universe: {len(ent):,}", flush=True)

def idade_bin(a):
    if a <= 6: return "4-6 anos"
    if a <= 10: return "7-10 anos"
    if a <= 14: return "11-14 anos"
    if a <= 17: return "15-17 anos"
    return "18-24 anos"
ent["idade_bin"] = ent["idade_t"].apply(idade_bin)

# Average rates
rows = []
for ib in ["4-6 anos", "7-10 anos", "11-14 anos", "15-17 anos", "18-24 anos"]:
    g = ent[ent["idade_bin"] == ib]
    if len(g) == 0:
        rows.append({"idade_bin": ib, "taxa_entrada": np.nan, "n": 0})
        continue
    rows.append({
        "idade_bin": ib,
        "taxa_entrada": np.average(g.flag_entrada, weights=g.wt_t),
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
                  "taxa_entrada": np.average(g.flag_entrada, weights=g.wt_t),
                  "n": len(g)})
ent_year = pd.DataFrame(rows)
ent_year.to_csv(OUT_DIR / "T_entrada_por_ano.csv", index=False)

# Build LaTeX
def fmt_pct(x):
    try: return f"{float(x)*100:.1f}"
    except: return "---"
def fmt_n(x):
    try: return f"{int(float(x)):,}".replace(",", ".")
    except: return "---"
lines = []
lines.append("% C19b entrada (patched)")
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
lines.append(r"\item \textit{Fonte:} Painel longitudinal PNADC, trimestres $Q_2$-$Q_4$ de $t$ e $Q_2$-$Q_3$ de $t+1$ (Spec A).")
lines.append(r"\item \textit{Universo:} indiv\'iduos com idade 4--24 anos em $t$ \emph{n\~ao} observados em EF/EM regular nem em EM t\'ecnico em nenhum trimestre $Q_2$-$Q_4$ de $t$. Inclui (i) crian\c{c}as muito jovens que ainda n\~ao iniciaram, (ii) jovens que abandonaram em anos anteriores, (iii) jovens em EJA, e (iv) jovens em outras modalidades. \textit{Numerador:} indiv\'iduos cuja refer\^encia em $t+1$ ($Q_2$ ou $Q_3$) os mostra matriculados em EF/EM regular ou t\'ecnico.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")
(OUT_DIR / "T_entrada_no_sistema.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved {OUT_DIR / 'T_entrada_no_sistema.tex'}", flush=True)
