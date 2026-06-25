# -------------------------------------------------------------------------
# C19_v4_unified.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Pipeline unificada v4. Inclui tecnico EM, computa entrada no sistema,
#   roda duas specs de janela. Otimizada para evitar groupby+apply lento.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSED_DIR = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# ---------- Step 1: Load raw lookup (cached if available) ----------
lookup_path = OUT_DIR / "C19_v4_lookup.parquet"
if lookup_path.exists():
    print(f"Cached lookup found", flush=True)
    lookup = pd.read_parquet(lookup_path)
    print(f"  rows: {len(lookup):,}", flush=True)
else:
    parquets = sorted(PARSED_DIR.glob("pnadc_*.parquet"))
    print(f"Building lookup from {len(parquets)} parquets", flush=True)
    cols_wanted = ["UF", "UPA", "V1008", "V1014", "V2003",
                   "V3002", "V3003", "V3003A", "V3006",
                   "V3014", "V2007", "V2009", "V1028",
                   "Ano", "Trimestre"]
    frames = []
    for p in parquets:
        try:
            d = pd.read_parquet(p, columns=cols_wanted)
        except Exception:
            d_meta = pd.read_parquet(p, columns=None).head(0)
            avail = [c for c in cols_wanted if c in d_meta.columns]
            d = pd.read_parquet(p, columns=avail)
            for c in cols_wanted:
                if c not in d.columns: d[c] = None
            d = d[cols_wanted]
        frames.append(d)
    lookup = pd.concat(frames, ignore_index=True)
    lookup.to_parquet(lookup_path, index=False)
    print(f"  Saved: {len(lookup):,}", flush=True)

# Numeric casts (V3014 etc are stored as strings in raw parquets)
for c in ["V3002", "V3014", "V3003", "V3003A", "V3006",
          "V2007", "V2009", "V1028"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")

# Filter to age 4-24 immediately
lookup = lookup[lookup["V2009"].between(4, 24)].copy()
print(f"After age 4-24 filter: {len(lookup):,}", flush=True)

# ---------- Step 2: Build curso + nivel + macroetapa ----------
print("Computing curso/nivel...", flush=True)
# curso codes: 100=Reg EF, 200=Reg EM, 210=Tec EM, 300=EJA EF, 310=EJA EM, 900=Outros
curso = np.full(len(lookup), 900.0)
ano = lookup["Ano"].values
v3 = lookup["V3003"].values
v3a = lookup["V3003A"].values

# pre-2016 using V3003
mask_pre = ano <= 2015
curso[mask_pre & (v3 == 3)] = 100
curso[mask_pre & (v3 == 4)] = 300
curso[mask_pre & (v3 == 5)] = 200
curso[mask_pre & (v3 == 6)] = 310
curso[mask_pre & (v3 == 7)] = 210

# 2016+ using V3003A
mask_post = ano >= 2016
curso[mask_post & (v3a == 4)] = 100
curso[mask_post & (v3a == 5)] = 300
curso[mask_post & (v3a == 6)] = 200
curso[mask_post & (v3a == 7)] = 210

# NaN if neither V3003 nor V3003A defined
both_na = np.isnan(v3) & np.isnan(v3a)
curso[both_na] = np.nan

lookup["curso"] = curso

# Nivel: 1-9 EF, 10-12 EM regular, 10-13 EM tecnico
serie = lookup["V3006"].values
nivel = np.full(len(lookup), np.nan)
nivel[(curso == 100) & (serie >= 1) & (serie <= 9)] = serie[(curso == 100) & (serie >= 1) & (serie <= 9)]
nivel[(curso == 200) & (serie >= 1) & (serie <= 3)] = 9 + serie[(curso == 200) & (serie >= 1) & (serie <= 3)]
nivel[(curso == 210) & (serie >= 1) & (serie <= 4)] = 9 + serie[(curso == 210) & (serie >= 1) & (serie <= 4)]
lookup["nivel"] = nivel

# Macroetapa
me = np.full(len(lookup), None, dtype=object)
me[(nivel >= 1) & (nivel <= 5)] = "EF iniciais"
me[(nivel >= 6) & (nivel <= 9)] = "EF finais"
me[(nivel >= 10) & (nivel <= 13)] = "EM"
me[curso == 300] = "EJA EF"
me[curso == 310] = "EJA EM"
lookup["macroetapa"] = me

print("nivel dist:")
print(lookup["nivel"].value_counts(dropna=False).sort_index().head(20))
print("macroetapa dist:")
print(lookup["macroetapa"].value_counts(dropna=False))

# ---------- Step 3: Load link panel and merge ----------
print("\nLoading link panel...", flush=True)
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

# ---------- Step 4: Pre-compute window-level flags VECTORIZED ----------
# For each (person_id, Ano), we want:
#   - max nivel observed in {Q in window}
#   - the row (serie, freq, etc) at max nivel
#   - any V3014=1 in window
#   - any in_eja in window
#   - any freq_zero in window
#   - any in_regular in window

panel["in_eja"] = ((panel["curso"] == 300) | (panel["curso"] == 310)).astype(int)
panel["in_regular"] = (panel["nivel"].notna()).astype(int)
panel["freq_zero"] = (panel["V3002"] == 2).astype(int)
panel["freq_one"] = (panel["V3002"] == 1).astype(int)
panel["concluiu"] = (panel["V3014"] == 1).astype(int)

def build_window_refs(panel, t_quarters):
    """Vectorized: per (person_id, Ano), pick row with max(nivel) in window
    and compute aggregate flags."""
    sub = panel[panel["Trimestre"].isin(t_quarters)].copy()
    print(f"  Window obs ({t_quarters}): {len(sub):,}", flush=True)

    # Best row per (person, ano): max nivel, then latest Trimestre
    reg = sub[sub["nivel"].notna()].copy()
    reg = reg.sort_values(["person_id", "Ano", "nivel", "Trimestre"],
                          ascending=[True, True, False, False])
    ref_reg = reg.drop_duplicates(subset=["person_id", "Ano"], keep="first")
    ref_reg = ref_reg[["person_id", "Ano", "nivel", "V3006", "curso",
                       "macroetapa", "Trimestre", "V1028", "V2009",
                       "V2007", "raca", "renda_dom_pc"]]
    ref_reg.columns = ["person_id", "Ano", "nivel_ref", "serie_ref", "curso_ref",
                        "macroetapa_ref", "trim_ref", "wt_ref", "idade_ref",
                        "sexo_ref", "raca_ref", "renda_ref"]

    # Aggregate flags (groupby + sum)
    agg = sub.groupby(["person_id", "Ano"]).agg(
        any_in_regular=("in_regular", "max"),
        any_in_eja=("in_eja", "max"),
        any_freq_zero=("freq_zero", "max"),
        any_freq_one=("freq_one", "max"),
        any_concluiu=("concluiu", "max"),
        max_idade=("V2009", "max"),
        any_obs=("V3002", "size"),
    ).reset_index()

    out = ref_reg.merge(agg, on=["person_id", "Ano"], how="outer")
    return out

print("\nBuilding refs Spec A t {Q2,Q3,Q4}...", flush=True)
refsA_t = build_window_refs(panel, [2, 3, 4])
print(f"  rows: {len(refsA_t):,}", flush=True)

print("Building refs Spec A t+1 {Q2,Q3}...", flush=True)
refsA_t1 = build_window_refs(panel, [2, 3])
print(f"  rows: {len(refsA_t1):,}", flush=True)

print("Building refs Spec B t {Q3,Q4}...", flush=True)
refsB_t = build_window_refs(panel, [3, 4])
print(f"  rows: {len(refsB_t):,}", flush=True)

print("Building refs Spec B t+1 {Q2,Q3,Q4}...", flush=True)
refsB_t1 = build_window_refs(panel, [2, 3, 4])
print(f"  rows: {len(refsB_t1):,}", flush=True)

# Free memory
del panel

# ---------- Step 5: Build transitions for each spec ----------
def build_trans(ref_t, ref_t1, spec):
    """Build t->t+1 transitions. ref_t is enrolled, ref_t1 is any state."""
    t = ref_t[ref_t["any_in_regular"] == 1].copy()
    t = t.rename(columns={
        "Ano": "ano_t", "nivel_ref": "nivel_t",
        "serie_ref": "serie_t", "curso_ref": "curso_t",
        "macroetapa_ref": "macroetapa_t", "trim_ref": "trim_t",
        "wt_ref": "wt_t", "idade_ref": "idade_t",
        "sexo_ref": "sexo_t", "raca_ref": "raca_t",
        "renda_ref": "renda_t",
        "any_in_regular": "in_reg_t", "any_in_eja": "in_eja_t",
        "any_freq_zero": "freq_zero_t", "any_freq_one": "freq_one_t",
        "any_concluiu": "concluiu_t",
    })
    t["ano_t1"] = t["ano_t"] + 1

    t1 = ref_t1.rename(columns={
        "Ano": "ano_t1", "nivel_ref": "nivel_t1",
        "serie_ref": "serie_t1", "curso_ref": "curso_t1",
        "macroetapa_ref": "macroetapa_t1", "trim_ref": "trim_t1",
        "wt_ref": "wt_t1",
        "any_in_regular": "in_reg_t1", "any_in_eja": "in_eja_t1",
        "any_freq_zero": "freq_zero_t1", "any_freq_one": "freq_one_t1",
        "any_concluiu": "concluiu_t1",
    })[["person_id", "ano_t1", "nivel_t1", "serie_t1", "curso_t1",
        "macroetapa_t1", "trim_t1", "in_reg_t1", "in_eja_t1",
        "freq_zero_t1", "freq_one_t1", "concluiu_t1"]]

    out = t.merge(t1, on=["person_id", "ano_t1"], how="left")
    out["spec"] = spec
    out["has_t1"] = (out["in_reg_t1"].fillna(0)
                      + out["in_eja_t1"].fillna(0)
                      + out["freq_zero_t1"].fillna(0)) > 0
    return out

ta = build_trans(refsA_t, refsA_t1, "A")
tb = build_trans(refsB_t, refsB_t1, "B")
print(f"\nSpec A transitions: {len(ta):,}, with t+1: {ta['has_t1'].sum():,}", flush=True)
print(f"Spec B transitions: {len(tb):,}, with t+1: {tb['has_t1'].sum():,}", flush=True)

# ---------- Step 6: Compute flags ----------
def compute_flags(t):
    t = t.copy()
    for c in ["in_reg_t1", "in_eja_t1", "freq_zero_t1", "concluiu_t1"]:
        t[c] = t[c].fillna(0).astype(int)
    # Restrict to has_t1
    t_main = t[t["has_t1"] == True].copy()

    # Migracao EJA: kid in EJA in t+1 AND not in regular in t+1
    t_main["flag_migracao_eja"] = (
        (t_main["in_eja_t1"] == 1) & (t_main["in_reg_t1"] == 0)
    ).astype(int)

    # Evasao: freq_zero in t+1 AND not in reg AND not in EJA
    t_main["flag_evasao_raw"] = (
        (t_main["freq_zero_t1"] == 1) &
        (t_main["in_reg_t1"] == 0) &
        (t_main["in_eja_t1"] == 0)
    ).astype(int)

    # Promocao: in reg t+1 with higher nivel
    t_main["flag_promocao_raw"] = (
        (t_main["in_reg_t1"] == 1) &
        t_main["nivel_t1"].notna() &
        (t_main["nivel_t1"] > t_main["nivel_t"])
    ).astype(int)

    # Repetencia: same nivel
    t_main["flag_repetencia_raw"] = (
        (t_main["in_reg_t1"] == 1) &
        t_main["nivel_t1"].notna() &
        (t_main["nivel_t1"] == t_main["nivel_t"])
    ).astype(int)

    # V3014 correction: kid at terminal level (12=3o EM or 13=4o tec)
    # and concluiu_t1=1 and was being counted as evasao
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
    return t_main

ta_main = compute_flags(ta)
tb_main = compute_flags(tb)
print(f"\nSpec A main: {len(ta_main):,}, corrected: {ta_main['correction_applied'].sum():,}", flush=True)
print(f"Spec B main: {len(tb_main):,}, corrected: {tb_main['correction_applied'].sum():,}", flush=True)

ta_main.to_parquet(OUT_DIR / "C19_transitions_specA.parquet", index=False)
tb_main.to_parquet(OUT_DIR / "C19_transitions_specB.parquet", index=False)

# ---------- Step 7: Aggregate ----------
def aggregate(t_main, label):
    t_use = t_main[t_main["ano_t"] <= 2023].copy()
    grp = t_use.groupby(["ano_t", "macroetapa_t"])
    rows = []
    for (a, m), g in grp:
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
    agg.to_csv(OUT_DIR / f"T1_brasil_inter_v4_{label}.csv", index=False)
    print(f"\n=== {label} ===", flush=True)
    for et in ["EF iniciais", "EF finais", "EM"]:
        print(f"  {et}:", flush=True)
        sub = agg[agg["macroetapa"] == et].sort_values("ano_t")
        for _, r in sub.iterrows():
            total = r.flag_promocao + r.flag_repetencia + r.flag_evasao + r.flag_migracao_eja
            print(f"    {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
                  f"rep={r.flag_repetencia*100:.1f}% "
                  f"evas={r.flag_evasao*100:.1f}% "
                  f"eja={r.flag_migracao_eja*100:.1f}% "
                  f"sum={total*100:.1f}% n={int(r.n_pessoa)}", flush=True)
    return agg

agg_A = aggregate(ta_main, "specA")
agg_B = aggregate(tb_main, "specB")

# ---------- Step 8: Entrada no sistema ----------
print("\n=== ENTRADA NO SISTEMA ===", flush=True)
# Sample: in t, kid was NOT in regular (no in_reg_t == 1).
# Build from ALL refs (not restricting to in_reg)
ref_t_full_A = refsA_t.copy()
ref_t1_full_A = refsA_t1.copy()
ref_t_full_A = ref_t_full_A.rename(columns={
    "Ano": "ano_t", "any_in_regular": "in_reg_t",
    "any_in_eja": "in_eja_t", "wt_ref": "wt_t",
    "idade_ref": "idade_t", "max_idade": "max_idade_t",
})
ref_t_full_A["ano_t1"] = ref_t_full_A["ano_t"] + 1
ref_t1_full_A = ref_t1_full_A.rename(columns={
    "Ano": "ano_t1", "any_in_regular": "in_reg_t1",
})[["person_id", "ano_t1", "in_reg_t1"]]

ent = ref_t_full_A.merge(ref_t1_full_A, on=["person_id", "ano_t1"], how="left")
ent = ent[ent["in_reg_t1"].notna()].copy()  # must have t+1 obs
ent = ent[ent["in_reg_t"] == 0].copy()  # NOT in regular in t (the universe)
ent["flag_entrada"] = (ent["in_reg_t1"] == 1).astype(int)
# idade
ent["idade_use"] = ent["idade_t"].fillna(ent["max_idade_t"])
ent = ent[ent["idade_use"].notna() & ent["wt_t"].notna()].copy()
ent = ent[ent["ano_t"] <= 2023].copy()

def idade_bin(a):
    if a <= 6: return "4-6 anos"
    if a <= 10: return "7-10 anos"
    if a <= 14: return "11-14 anos"
    if a <= 17: return "15-17 anos"
    return "18-24 anos"

ent["idade_bin"] = ent["idade_use"].apply(idade_bin)

# By idade_bin (pooled years)
rows = []
for ib in ["4-6 anos", "7-10 anos", "11-14 anos", "15-17 anos", "18-24 anos"]:
    g = ent[ent["idade_bin"] == ib]
    if len(g) == 0: continue
    rows.append({"idade_bin": ib,
                  "taxa_entrada": np.average(g.flag_entrada, weights=g.wt_t),
                  "n": len(g)})
ent_avg = pd.DataFrame(rows)
ent_avg.to_csv(OUT_DIR / "T_entrada_no_sistema.csv", index=False)
print(ent_avg.to_string(index=False), flush=True)

# By year and idade_bin
rows = []
for (a, ib), g in ent.groupby(["ano_t", "idade_bin"]):
    rows.append({"ano_t": a, "idade_bin": ib,
                  "taxa_entrada": np.average(g.flag_entrada, weights=g.wt_t),
                  "n": len(g)})
ent_by_year = pd.DataFrame(rows)
ent_by_year.to_csv(OUT_DIR / "T_entrada_por_ano.csv", index=False)

# ---------- Step 9: Build LaTeX tables ----------
def build_t1_latex(agg, out_path, spec_label, intra_csv):
    intra = {}
    if intra_csv.exists():
        import csv
        with open(intra_csv, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                intra[(int(r["ano_t"]), r["macroetapa"])] = r
    def fmt_pct(x):
        try: return f"{float(x)*100:.1f}"
        except: return "---"
    def fmt_n(x):
        try: return f"{int(float(x)):,}".replace(",", ".")
        except: return "---"
    years = sorted(agg["ano_t"].unique())
    panels = [
        ("EF iniciais", r"\textit{Painel A: EF iniciais (1\textsuperscript{o}--5\textsuperscript{o} ano)}"),
        ("EF finais",   r"\textit{Painel B: EF finais (6\textsuperscript{o}--9\textsuperscript{o} ano)}"),
        ("EM",          r"\textit{Painel C: Ensino M\'edio (regular + t\'ecnico, 1\textsuperscript{o}--4\textsuperscript{o} ano)}"),
    ]
    lines = []
    lines.append(f"% C19 - {spec_label}")
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(rf"\caption{{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano. {spec_label}.}}")
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
        sub = agg[agg["macroetapa"] == etapa].sort_values("ano_t")
        for _, r in sub.iterrows():
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
    lines.append(rf"\item \textit{{Janela:}} {spec_label}. M\'ax($nivel$) na janela. Inclui EM t\'ecnico ($V3003A=07$). Conclus\~ao do 3\textsuperscript{{o}} EM (regular) e do 4\textsuperscript{{o}} EM (t\'ecnico) via $V3014=1$ reclassificada como promo\c{{c}}\~ao.")
    lines.append(r"\item \textit{Fonte:} PNADC trimestral, IBGE.")
    lines.append(r"\item $^{a}$Abandono refere-se \`a Tabela~\ref{tab:abandono_fullyear} (sub-amostra com cobertura Q1--Q4).")
    lines.append(r"\item $^{\dagger}$Anos COVID-19. Interpretar com cautela.")
    lines.append(r"\end{tablenotes}")
    lines.append(r"\end{threeparttable}")
    lines.append(r"\end{table}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)

intra_csv = OUT_DIR / "T_abandono_fullyear.csv"

backup_v3 = OUT_DIR / "T1_v3_em_concluido.tex"
old_tex = OUT_DIR / "T1_brasil_inter_por_serie_ano.tex"
if old_tex.exists() and not backup_v3.exists():
    shutil.copy(old_tex, backup_v3)

build_t1_latex(agg_A, OUT_DIR / "T1_brasil_inter_por_serie_ano.tex",
                "Spec A: $t \\in \\{Q_2, Q_3, Q_4\\}$, $t{+}1 \\in \\{Q_2, Q_3\\}$",
                intra_csv)
build_t1_latex(agg_B, OUT_DIR / "T1_brasil_inter_specB.tex",
                "Spec B: $t \\in \\{Q_3, Q_4\\}$, $t{+}1 \\in \\{Q_2, Q_3, Q_4\\}$",
                intra_csv)

# Entrada LaTeX
def fmt_pct(x):
    try: return f"{float(x)*100:.1f}"
    except: return "---"
def fmt_n(x):
    try: return f"{int(float(x)):,}".replace(",", ".")
    except: return "---"
lines = []
lines.append("% C19 entrada")
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
lines.append(r"\item \textit{Fonte:} Painel longitudinal PNADC.")
lines.append(r"\item \textit{Notas:} Universo: indiv\'iduos com idade 4--24 anos em $t$ que n\~ao foram observados em EF regular nem em EM regular ou t\'ecnico no per\'iodo de refer\^encia (Spec A: $Q_2$, $Q_3$ ou $Q_4$ do ano $t$). Numerador: indiv\'iduos cuja refer\^encia em $t+1$ ($Q_2$ ou $Q_3$ de $t+1$) os mostra matriculados em EF regular ou EM regular/t\'ecnico.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")
(OUT_DIR / "T_entrada_no_sistema.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Saved T_entrada_no_sistema.tex", flush=True)

print("\n=== Done ===", flush=True)
