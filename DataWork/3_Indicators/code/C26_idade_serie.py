# -------------------------------------------------------------------------
# C26_idade_serie.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Idade media por serie/curso ao longo dos anos. Teste critico:
#   se a repetencia tivesse aumentado de forma real pos-COVID, a idade
#   media por serie deveria ter aumentado. Caso contrario, o aumento
#   na rep PNADC eh artefato de medicao.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"
PARSED_DIR = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"

rows = []
for ano in [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
    df = pd.read_parquet(PARSED_DIR / f"pnadc_02{ano}.parquet",
                          columns=["V3003A", "V3006", "V2009", "V3002", "V1028"])
    df["idade"] = pd.to_numeric(df["V2009"], errors="coerce")
    df["peso"] = pd.to_numeric(df["V1028"], errors="coerce")
    # EF regular (V3003A=04) e EM regular (V3003A=06)
    for curso_lbl, curso_code, series in [
        ("EF iniciais", "04", ["01", "02", "03", "04", "05"]),
        ("EF finais",   "04", ["06", "07", "08", "09"]),
        ("EM",          "06", ["01", "02", "03"]),
    ]:
        for s in series:
            sub = df[(df["V3003A"] == curso_code) &
                      (df["V3002"] == "1") &
                      (df["V3006"] == s)]
            if len(sub) < 50: continue
            sub = sub.dropna(subset=["idade", "peso"])
            idade_avg = np.average(sub.idade, weights=sub.peso)
            idade_med = sub.idade.median()
            rows.append({"ano": ano, "curso": curso_lbl, "serie": s,
                          "idade_avg": idade_avg, "idade_med": idade_med,
                          "n": len(sub)})

df_idade = pd.DataFrame(rows)
df_idade.to_csv(OUT_DIR / "T_idade_serie.csv", index=False)

# Print pivot for EM
print("EM regular - idade média por série e ano:")
em = df_idade[df_idade.curso == "EM"]
piv = em.pivot_table(index="ano", columns="serie", values="idade_avg")
print(piv.round(1))
print()
print("EF iniciais (5o ano) - idade média por ano:")
ef5 = df_idade[(df_idade.curso == "EF iniciais") & (df_idade.serie == "05")]
print(ef5[["ano", "idade_avg"]].to_string(index=False))
print()
print("EF finais (9o ano) - idade média por ano:")
ef9 = df_idade[(df_idade.curso == "EF finais") & (df_idade.serie == "09")]
print(ef9[["ano", "idade_avg"]].to_string(index=False))

# Build LaTeX table
def fmt(x):
    try: return f"{float(x):.1f}"
    except: return "---"

lines = []
lines.append("% C26 idade por serie")
lines.append(r"\begin{table}[htbp]\centering")
lines.append(r"\caption{Idade m\'edia (ponderada) por s\'erie e ano, alunos do EM regular (V3003A=06) frequentando no $Q_2$. Teste cr\'itico: se a repet\^encia real tivesse aumentado em 2022--2023, a idade m\'edia por s\'erie deveria ter aumentado.}")
lines.append(r"\label{tab:idade_serie}")
lines.append(r"\begin{threeparttable}\small")
lines.append(r"\begin{tabular}{lrrrrrr}\toprule")
lines.append(r"Ano & 1\textsuperscript{o} EM & 2\textsuperscript{o} EM & 3\textsuperscript{o} EM & 5\textsuperscript{o} EF & 9\textsuperscript{o} EF & N$^{a}$ EM\\")
lines.append(r"\midrule")
for ano in sorted(df_idade.ano.unique()):
    em1 = em[(em.ano == ano) & (em.serie == "01")]
    em2 = em[(em.ano == ano) & (em.serie == "02")]
    em3 = em[(em.ano == ano) & (em.serie == "03")]
    ef5_a = ef5[ef5.ano == ano]
    ef9_a = ef9[ef9.ano == ano]
    n_em = em1.n.iloc[0] + em2.n.iloc[0] + em3.n.iloc[0] if len(em1) and len(em2) and len(em3) else 0
    em1_v = em1.idade_avg.iloc[0] if len(em1) else None
    em2_v = em2.idade_avg.iloc[0] if len(em2) else None
    em3_v = em3.idade_avg.iloc[0] if len(em3) else None
    ef5_v = ef5_a.idade_avg.iloc[0] if len(ef5_a) else None
    ef9_v = ef9_a.idade_avg.iloc[0] if len(ef9_a) else None
    # Marcar 2020 e 2021 com dagger
    ano_lbl = f"{ano}$^{{\\dagger}}$" if ano in (2020, 2021) else str(ano)
    lines.append(rf"{ano_lbl} & {fmt(em1_v)} & {fmt(em2_v)} & {fmt(em3_v)} & {fmt(ef5_v)} & {fmt(ef9_v)} & {n_em:,} \\")
lines.append(r"\bottomrule\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fonte:} PNADC trimestral, $Q_2$ de cada ano. Idade m\'edia ponderada por $V1028$.")
lines.append(r"\item $^{a}$N total para 1\textsuperscript{o} + 2\textsuperscript{o} + 3\textsuperscript{o} EM em $Q_2$.")
lines.append(r"\item $^{\dagger}$Anos COVID-19.")
lines.append(r"\end{tablenotes}\end{threeparttable}\end{table}")
out_tex = OUT_DIR / "T_idade_serie.tex"
out_tex.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved {out_tex}")
