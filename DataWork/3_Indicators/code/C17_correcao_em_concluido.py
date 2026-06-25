# -------------------------------------------------------------------------
# C17_correcao_em_concluido.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Aplica a correcao para EM concluido. Alunos no 3o EM (nivel=12) ou
#   4o ano de EM tecnico em t, que em t+1 reportam V3002=2 (nao frequenta)
#   mas V3014=1 (concluiu o curso), sao reclassificados como PROMOCAO em
#   vez de EVASAO. Esta correcao alinha a definicao da PNADC com a do
#   INEP, que conta a conclusao do EM como promocao independentemente de
#   matricula posterior.
#
# Inputs:
#   ../../1_DownloadPNADC/tmp/pnad_parsed/pnadc_qYYYY.parquet  (raw, V3014)
#   ../../2_PanelBuild/tmp/pnadc_linked.dta  (linked panel)
#   ../output/C14_transitions_v2.parquet     (transitions v2)
#
# Outputs:
#   ../output/T1_brasil_inter_v3_corrected.csv
#   ../output/T1_brasil_inter_por_serie_ano.tex      (NEW main, v3)
#   ../output/T1_v2_pre_completion.tex               (backup da v2)
#   ../output/C17_transitions_v3.parquet
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np
import shutil

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSED_DIR = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# === Step 1: extract V3014 from all parquets (cache if exists) ===
lookup_path = OUT_DIR / "C17_V3014_lookup.parquet"
if lookup_path.exists():
    print(f"Using cached {lookup_path}", flush=True)
    V3014_lookup = pd.read_parquet(lookup_path)
    print(f"  rows: {len(V3014_lookup):,}", flush=True)
else:
    parquets = sorted(PARSED_DIR.glob("pnadc_*.parquet"))
    print(f"Found {len(parquets)} parquet files", flush=True)

    frames = []
    for p in parquets:
        name = p.stem
        q = int(name[6])
        y = int(name[7:])
        cols_wanted = ["UF", "UPA", "V1008", "V1014", "V2003",
                       "V3002", "V3014", "Ano", "Trimestre"]
        try:
            d = pd.read_parquet(p, columns=cols_wanted)
        except Exception:
            d_meta = pd.read_parquet(p, columns=None).head(0)
            avail = [c for c in cols_wanted if c in d_meta.columns]
            d = pd.read_parquet(p, columns=avail)
        if "V3014" not in d.columns:
            continue
        if "Ano" not in d.columns: d["Ano"] = y
        if "Trimestre" not in d.columns: d["Trimestre"] = q
        d = d[["UF", "UPA", "V1008", "V1014", "V2003", "V3002", "V3014",
               "Ano", "Trimestre"]].copy()
        frames.append(d)
        if y % 5 == 0:
            print(f"  loaded {name}: {len(d)} rows", flush=True)

    V3014_df = pd.concat(frames, ignore_index=True)
    print(f"\nTotal V3014 rows: {len(V3014_df):,}", flush=True)
    print(f"V3014 non-NaN: {V3014_df['V3014'].notna().sum():,}", flush=True)

    V3014_df["hh_id"] = (V3014_df["UF"].astype(int).astype(str) + "_" +
                         V3014_df["UPA"].astype(str) + "_" +
                         V3014_df["V1008"].astype(str) + "_" +
                         V3014_df["V1014"].astype(str))
    V3014_df["pid_provis"] = V3014_df["hh_id"] + "_" + V3014_df["V2003"].astype(str)

    V3014_lookup = V3014_df[["pid_provis", "Ano", "Trimestre", "V3002", "V3014"]].copy()
    V3014_lookup.to_parquet(lookup_path, index=False)
    print(f"Saved {lookup_path} ({len(V3014_lookup):,} rows)", flush=True)

# === Step 2: load linked panel to get person_id ↔ pid_provis map ===
print("\nLoading linked panel to map person_id...", flush=True)
KEEP_LINK = ["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003",
             "person_id", "link_ok"]
link_df, _ = pyreadstat.read_dta(str(LINK), usecols=KEEP_LINK)
link_df = link_df[link_df["link_ok"] == 1].copy()

link_df["pid_provis"] = (link_df["UF"].astype(int).astype(str) + "_" +
                          link_df["UPA"].astype(int).astype(str) + "_" +
                          link_df["V1008"].astype(int).astype(str) + "_" +
                          link_df["V1014"].astype(int).astype(str) + "_" +
                          link_df["V2003"].astype(int).astype(str))

# Merge V3014 into link
print("Merging V3014 to linked panel...", flush=True)
link_with_v3014 = link_df.merge(
    V3014_lookup, on=["pid_provis", "Ano", "Trimestre"], how="left")
print(f"  After merge: {len(link_with_v3014):,}", flush=True)
print(f"  V3014 non-NaN after merge: {link_with_v3014['V3014'].notna().sum():,}",
      flush=True)

# V3014 is stored as string in raw parquets; coerce comparison
link_with_v3014["concluiu_curso"] = (
    link_with_v3014["V3014"].astype(str) == "1"
).astype(int)
concluiu_per_year = (link_with_v3014.groupby(["person_id", "Ano"])
                     ["concluiu_curso"].max().reset_index())
concluiu_per_year = concluiu_per_year.rename(
    columns={"Ano": "ano_t1", "concluiu_curso": "concluiu_curso_t1"})

# === Step 3: load v2 transitions and apply correction ===
print("\nLoading C14_transitions_v2...", flush=True)
t = pd.read_parquet(OUT_DIR / "C14_transitions_v2.parquet")
print(f"  {len(t):,} transitions", flush=True)

t = t.merge(concluiu_per_year, on=["person_id", "ano_t1"], how="left")
t["concluiu_curso_t1"] = t["concluiu_curso_t1"].fillna(0).astype(int)
print(f"  concluiu_curso_t1=1: {t['concluiu_curso_t1'].sum():,}", flush=True)

# Restrict to main sample (drop attrition)
t_main = t[t["freq_t1"].notna()].copy()
print(f"  Main sample: {len(t_main):,}", flush=True)

# Original flags from C14
t_main["any_eja_t1"] = t_main["any_eja_t1"].astype(bool)
t_main["flag_migracao_eja"] = t_main["any_eja_t1"].astype(int)
t_main["flag_evasao_raw"] = (
    (t_main["freq_t1"] == 0) & (~t_main["any_eja_t1"])
).astype(int)
t_main["flag_promocao_raw"] = (
    (t_main["freq_t1"] == 1) &
    (~t_main["any_eja_t1"]) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] > t_main["nivel_t"])
).astype(int)
t_main["flag_repetencia_raw"] = (
    (t_main["freq_t1"] == 1) &
    (~t_main["any_eja_t1"]) &
    t_main["nivel_t1"].notna() &
    (t_main["nivel_t1"] == t_main["nivel_t"])
).astype(int)

# === CORRECTION: kid in 3rd EM (nivel_t == 12) and concluiu_curso_t1==1 ===
# These get reclassified from evasão to promoção
t_main["was_em_terminal"] = (t_main["nivel_t"] == 12).astype(int)
t_main["correction_applied"] = (
    (t_main["was_em_terminal"] == 1) &
    (t_main["concluiu_curso_t1"] == 1) &
    (t_main["flag_evasao_raw"] == 1)  # was being counted as evasion
).astype(int)
n_corr = t_main["correction_applied"].sum()
print(f"  Correction applied to {n_corr:,} transitions", flush=True)

# Apply correction: move from evasão to promoção for 3rd EM completers
t_main["flag_promocao"] = t_main["flag_promocao_raw"]
t_main["flag_repetencia"] = t_main["flag_repetencia_raw"]
t_main["flag_evasao"] = t_main["flag_evasao_raw"]

mask = t_main["correction_applied"] == 1
t_main.loc[mask, "flag_promocao"] = 1
t_main.loc[mask, "flag_evasao"] = 0

t_main["flag_naoprog"] = (
    (t_main["flag_repetencia"] + t_main["flag_evasao"]
     + t_main["flag_migracao_eja"]) >= 1
).astype(int)
t_main["wt"] = t_main["wt_t"]

# Save corrected transitions
t_main.to_parquet(OUT_DIR / "C17_transitions_v3.parquet", index=False)
print(f"Saved C17_transitions_v3.parquet", flush=True)

# Aggregate
grp = t_main.groupby(["ano_t", "macroetapa_t"])
agg = pd.DataFrame({
    "flag_promocao":      grp.apply(lambda g: np.average(g.flag_promocao, weights=g.wt)),
    "flag_repetencia":    grp.apply(lambda g: np.average(g.flag_repetencia, weights=g.wt)),
    "flag_evasao":        grp.apply(lambda g: np.average(g.flag_evasao, weights=g.wt)),
    "flag_migracao_eja":  grp.apply(lambda g: np.average(g.flag_migracao_eja, weights=g.wt)),
    "n_pessoa":           grp.size(),
}).reset_index()
agg.columns = ["ano_t", "macroetapa", "flag_promocao", "flag_repetencia",
               "flag_evasao", "flag_migracao_eja", "n_pessoa"]
agg = agg[agg["macroetapa"].isin(["EF iniciais", "EF finais", "EM"])].copy()
agg.to_csv(OUT_DIR / "T1_brasil_inter_v3_corrected.csv", index=False)
print(f"\nSaved T1_brasil_inter_v3_corrected.csv", flush=True)

# Print summary EM (where correction matters)
print("\n=== EM (com correcao) ===", flush=True)
em = agg[agg["macroetapa"] == "EM"].sort_values("ano_t")
for _, r in em.iterrows():
    total = r.flag_promocao + r.flag_repetencia + r.flag_evasao + r.flag_migracao_eja
    print(f"  {int(r.ano_t)}: prom={r.flag_promocao*100:.1f}% "
          f"rep={r.flag_repetencia*100:.1f}% "
          f"evas={r.flag_evasao*100:.1f}% "
          f"eja={r.flag_migracao_eja*100:.1f}% "
          f"(sum={total*100:.1f}%) n={int(r.n_pessoa)}", flush=True)

# Also show pre-correction comparison for EM
print("\n=== Comparison EM 2019 ===", flush=True)
em2019 = t_main[(t_main["ano_t"] == 2019) & (t_main["macroetapa_t"] == "EM")]
print(f"  Before correction (v2): "
      f"prom={np.average(em2019.flag_promocao_raw, weights=em2019.wt)*100:.1f}% "
      f"evas={np.average(em2019.flag_evasao_raw, weights=em2019.wt)*100:.1f}%", flush=True)
print(f"  After correction  (v3): "
      f"prom={np.average(em2019.flag_promocao, weights=em2019.wt)*100:.1f}% "
      f"evas={np.average(em2019.flag_evasao, weights=em2019.wt)*100:.1f}%", flush=True)

# Build LaTeX
def fmt_pct(x):
    if x in (None, "", ".") or pd.isna(x): return "---"
    try: return f"{float(x)*100:.1f}"
    except (TypeError, ValueError): return "---"

def fmt_n(x):
    if x in (None, "", ".") or pd.isna(x): return "---"
    try: return f"{int(float(x)):,}".replace(",", ".")
    except (TypeError, ValueError): return "---"

# Backup v2
old_tex = OUT_DIR / "T1_brasil_inter_por_serie_ano.tex"
backup_v2 = OUT_DIR / "T1_v2_pre_completion.tex"
if old_tex.exists() and not backup_v2.exists():
    shutil.copy(old_tex, backup_v2)
    print(f"Backed up v2 to {backup_v2}", flush=True)

# Load intra (abandono)
intra = {}
intra_path = OUT_DIR / "T_abandono_fullyear.csv"
if intra_path.exists():
    import csv
    with open(intra_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            intra[(int(r["ano_t"]), r["macroetapa"])] = r

years = sorted(agg["ano_t"].unique())
panels = [
    ("EF iniciais", r"\textit{Painel A: EF iniciais (1\textsuperscript{o}--5\textsuperscript{o} ano)}"),
    ("EF finais",   r"\textit{Painel B: EF finais (6\textsuperscript{o}--9\textsuperscript{o} ano)}"),
    ("EM",          r"\textit{Painel C: Ensino M\'edio (1\textsuperscript{o}--3\textsuperscript{o} ano)}"),
]

lines = []
lines.append("% Auto-gerado por C17_correcao_em_concluido.py - versao v3 (com correcao EM concluido)")
lines.append(r"\begin{table}[htbp]")
lines.append(r"\centering")
lines.append(r"\caption{Indicadores agregados de fluxo escolar, Brasil, por macroetapa e ano. Painel longitudinal da PNADC, 2012--2023, com corre\c{c}\~ao de EM conclu\'ido via \texttt{V3014}.}")
lines.append(r"\label{tab:t1_brasil}")
lines.append(r"\begin{threeparttable}")
lines.append(r"\small")
lines.append(r"\begin{tabular}{lrrrrrr}")
lines.append(r"\toprule")
lines.append(r"Ano & Promo\c{c}\~ao & Repet\^encia & Evas\~ao & Migra\c{c}\~ao EJA & Abandono$^{a}$ & N \\")
lines.append(r"    & (\%)            & (\%)        & (\%)     & (\%)               & (\%)            &   \\")
lines.append(r"\midrule")
for et, label in panels:
    lines.append(rf"\multicolumn{{7}}{{l}}{{{label}}} \\")
    lines.append(r"\midrule")
    sub = agg[agg["macroetapa"] == et].sort_values("ano_t")
    for _, r in sub.iterrows():
        y = int(r.ano_t)
        ri = intra.get((y, et), {})
        ano_label = f"{y}$^{{\\dagger}}$" if y in (2020, 2021) else str(y)
        lines.append(rf"{ano_label} & {fmt_pct(r.flag_promocao)} & {fmt_pct(r.flag_repetencia)} & "
                     rf"{fmt_pct(r.flag_evasao)} & {fmt_pct(r.flag_migracao_eja)} & "
                     rf"{fmt_pct(ri.get('flag_abandono'))} & {fmt_n(r.n_pessoa)} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule")
lines.append(r"\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} Painel longitudinal da PNADC trimestral (IBGE), 2012Q1--2024Q4.")
lines.append(r"\item \textit{Notas:} Refer\^encia em $t$ e $t+1$ tomada entre $Q_2$ e $Q_3$, com $\max(\text{n\'ivel})$ em $t+1$. Alunos no terceiro ano do EM em $t$ que reportam $\texttt{V3014}=1$ (concluiu o curso) em $t+1$ s\~ao classificados como promo\c{c}\~ao, mesmo com $\texttt{V3002}=2$ em $t+1$, em alinhamento com a defini\c{c}\~ao do INEP. Abandono \'e a m\'edia da Tabela~\ref{tab:abandono_fullyear}.")
lines.append(r"\item $^{a}$Abandono refere-se \`a taxa intra-ano da Tabela~\ref{tab:abandono_fullyear}.")
lines.append(r"\item $^{\dagger}$Anos afetados pela pandemia COVID-19.")
lines.append(r"\item \emph{N} \'e o n\'umero de transi\c{c}\~oes individuais (n\~ao ponderado). Taxas ponderadas pelo peso amostral $w_i^{P1}$.")
lines.append(r"\end{tablenotes}")
lines.append(r"\end{threeparttable}")
lines.append(r"\end{table}")

out_tex = OUT_DIR / "T1_brasil_inter_por_serie_ano.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nWrote {out_tex}", flush=True)
