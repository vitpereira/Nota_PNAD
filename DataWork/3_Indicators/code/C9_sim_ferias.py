# -------------------------------------------------------------------------
# C9_sim_ferias.py
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Simulacao do efeito do periodo de ferias (Q1 = jan-mar) sobre os
#   indicadores de fluxo inter-anuais. Hipotese: quando a obs de t+1 cai
#   em Q1 (jan-mar), capturamos o periodo de ferias/transicao em que a
#   familia ainda reporta a serie do ano anterior, gerando FALSA repetencia.
#
# Tres versoes:
#   A. Baseline: usa todos os pares (trim_t, trim_t1) — corresponde a tab
#   B. Exclui trim_t1 == 1: medir t+1 apenas em Q2-Q4 (apos volta as aulas)
#   C. Restrito a Q2-Q4 nos dois lados (mais conservador)
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PANEL = ROOT / "DataWork/2_PanelBuild/output/painel_pnadc_2012_2024.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

print(f"Reading {PANEL}...")
df, meta = pyreadstat.read_dta(str(PANEL))
print(f"Loaded: {len(df):,} rows × {len(df.columns)} cols")

# Decode macroetapa from int codes to string labels for output readability
ME_LABELS = meta.variable_value_labels.get("macroetapa",
                {1: "EF iniciais", 2: "EF finais", 3: "EM",
                 4: "EJA EF", 5: "EJA EM"})
df["macroetapa_lbl"] = df["macroetapa"].map(ME_LABELS)

# Universe: EF + EM regular (codes 1, 2, 3)
df = df[df["macroetapa"].isin([1, 2, 3])].copy()
df = df[df["freq_escola_t1"].notna()].copy()
df = df[df["serie_t"].notna()].copy()

print(f"After universe filter: {len(df):,} rows")

# Diagnostic: distribution of (trim_t, trim_t1) pairs
print("\n=== Distribuicao de pares (trim_t, trim_t1) - baseline ===")
trim_pairs = df.groupby(["trim_t", "trim_t1"]).size().reset_index(name="n")
trim_pairs["pct"] = 100 * trim_pairs["n"] / trim_pairs["n"].sum()
trim_pairs = trim_pairs.sort_values(["trim_t", "trim_t1"])
print(trim_pairs.to_string(index=False))
trim_pairs.to_csv(OUT_DIR / "C9_distrib_trim.csv", index=False)

# Quanto cada combinacao representa
print(f"\n% transicoes com trim_t1 == 1 (Q1 de t+1): "
      f"{100*df[df.trim_t1==1].shape[0]/len(df):.1f}%")
print(f"% transicoes com trim_t1 >= 2: "
      f"{100*df[df.trim_t1>=2].shape[0]/len(df):.1f}%")
print(f"% transicoes com trim_t >= 2 & trim_t1 >= 2: "
      f"{100*df[(df.trim_t>=2)&(df.trim_t1>=2)].shape[0]/len(df):.1f}%")

# Flags
df["flag_promocao"]   = ((df["freq_escola_t1"] == 1) &
                         (df["serie_t1"] == df["serie_t"] + 1)).astype(int)
df["flag_repetencia"] = ((df["freq_escola_t1"] == 1) &
                         (df["serie_t1"] == df["serie_t"])).astype(int)
df["flag_evasao"]     = (df["freq_escola_t1"] == 0).astype(int)
df["flag_naoprog"]    = (df["flag_repetencia"] | df["flag_evasao"]).astype(int)
df["wt"] = df["peso_v1_t"]


def tabula(sub, label):
    """Weighted mean by (ano_t, macroetapa)."""
    grp = sub.groupby(["ano_t", "macroetapa_lbl"])
    out = pd.DataFrame({
        "flag_promocao":   grp.apply(
            lambda g: np.average(g.flag_promocao,   weights=g.wt)),
        "flag_repetencia": grp.apply(
            lambda g: np.average(g.flag_repetencia, weights=g.wt)),
        "flag_evasao":     grp.apply(
            lambda g: np.average(g.flag_evasao,     weights=g.wt)),
        "flag_naoprog":    grp.apply(
            lambda g: np.average(g.flag_naoprog,    weights=g.wt)),
        "n_pessoa":        grp.size(),
    }).reset_index()
    out["versao"] = label
    return out

print("\nComputing scenarios...")
A = tabula(df,                                        "A_baseline")
B = tabula(df[df["trim_t1"] >= 2],                    "B_sem_Q1_t1")
C = tabula(df[(df["trim_t"] >= 2) & (df["trim_t1"] >= 2)], "C_Q2Q4_ambos")

for v, name in [(A, "A_baseline"), (B, "B_sem_Q1_t1"), (C, "C_Q2Q4_ambos")]:
    f = OUT_DIR / f"C9_sim_{name}.csv"
    v.to_csv(f, index=False)
    print(f"Saved {f}")

# Comparison wide format
def widen(d, suf):
    d = d.copy()
    for c in ["flag_promocao", "flag_repetencia", "flag_evasao",
              "flag_naoprog", "n_pessoa"]:
        d = d.rename(columns={c: f"{c}_{suf}"})
    return d.drop(columns=["versao"])

wide = widen(A, "A").merge(widen(B, "B"), on=["ano_t", "macroetapa_lbl"]) \
                    .merge(widen(C, "C"), on=["ano_t", "macroetapa_lbl"])
wide = wide.sort_values(["macroetapa_lbl", "ano_t"])
wide.to_csv(OUT_DIR / "C9_sim_comparison.csv", index=False)
print(f"Saved {OUT_DIR / 'C9_sim_comparison.csv'}")

# Print key years
print("\n=== Promocao (%) - 2017-2023 ===")
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n--- {et} ---")
    sub = wide[wide["macroetapa_lbl"] == et].copy()
    sub = sub[sub["ano_t"].isin([2017, 2018, 2019, 2022, 2023])]
    print(f"{'Ano':>5} | {'A (atual)':>10} {'B (no Q1 t+1)':>14} {'C (Q2-Q4 both)':>16}")
    for _, r in sub.iterrows():
        print(f"{int(r.ano_t):>5} | "
              f"{r.flag_promocao_A*100:>9.1f} "
              f"{r.flag_promocao_B*100:>13.1f} "
              f"{r.flag_promocao_C*100:>15.1f}")

print("\n=== Repetencia (%) - 2017-2023 ===")
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n--- {et} ---")
    sub = wide[wide["macroetapa_lbl"] == et].copy()
    sub = sub[sub["ano_t"].isin([2017, 2018, 2019, 2022, 2023])]
    print(f"{'Ano':>5} | {'A (atual)':>10} {'B (no Q1 t+1)':>14} {'C (Q2-Q4 both)':>16}")
    for _, r in sub.iterrows():
        print(f"{int(r.ano_t):>5} | "
              f"{r.flag_repetencia_A*100:>9.1f} "
              f"{r.flag_repetencia_B*100:>13.1f} "
              f"{r.flag_repetencia_C*100:>15.1f}")

print("\n=== Evasao (%) - 2017-2023 ===")
for et in ["EF iniciais", "EF finais", "EM"]:
    print(f"\n--- {et} ---")
    sub = wide[wide["macroetapa_lbl"] == et].copy()
    sub = sub[sub["ano_t"].isin([2017, 2018, 2019, 2022, 2023])]
    print(f"{'Ano':>5} | {'A (atual)':>10} {'B (no Q1 t+1)':>14} {'C (Q2-Q4 both)':>16}")
    for _, r in sub.iterrows():
        print(f"{int(r.ano_t):>5} | "
              f"{r.flag_evasao_A*100:>9.1f} "
              f"{r.flag_evasao_B*100:>13.1f} "
              f"{r.flag_evasao_C*100:>15.1f}")

print("\nDone.")
