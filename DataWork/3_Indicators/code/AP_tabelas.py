# -------------------------------------------------------------------------
# AP_tabelas.py
# -------------------------------------------------------------------------
# Description:
#   Tabelas LaTeX resumo para o apendice descritivo.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

# Helper
def to_latex_table(df, fname, caption, label, fmts=None):
    DBL = "\\" + "\\"
    lines = []
    lines.append(f"% Auto: AP_tabelas.py")
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\label{{{label}}}")
    lines.append(r"\small")
    cols = "l" + "r" * (len(df.columns) - 1)
    lines.append(rf"\begin{{tabular}}{{{cols}}}")
    lines.append(r"\toprule")
    # Header
    header = " & ".join([str(c).replace("_","\\_") for c in df.columns]) + " " + DBL
    lines.append(header)
    lines.append(r"\midrule")
    # Rows
    for _, r in df.iterrows():
        cells = []
        for i, c in enumerate(df.columns):
            v = r[c]
            if pd.isna(v): cells.append("---")
            elif isinstance(v, str): cells.append(str(v).replace("_","\\_"))
            elif fmts and c in fmts: cells.append(fmts[c].format(v))
            elif isinstance(v, (int, np.integer)): cells.append(f"{int(v):,}".replace(",","."))
            else: cells.append(f"{v:.2f}")
        lines.append(" & ".join(cells) + " " + DBL)
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    (OUT / fname).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {fname}")


# T_A1: tamanho amostral
d = pd.read_csv(OUT / "AP_A1_amostra_por_ano.csv")
d.columns = ["Ano", "Observações", "População (mi)"]
to_latex_table(d, "TA_A1_amostra.tex",
    "Tamanho amostral PNADC por ano, 4-24 anos.",
    "tab:ap_a1_amostra",
    fmts={"Observações":"{:,.0f}", "População (mi)":"{:.1f}"})

# T_BR: fluxo Brasil x macroetapa x ano (resumo)
d = pd.read_csv(OUT / "AP_BR_identidade_contabil.csv")
d = d[~d.ano.isin([2020, 2021])].copy()
d_em = d[d.macroetapa == "EM"].copy()
d_em = d_em[["ano","prom","rep","evas","eja","n"]]
d_em["ano"] = d_em["ano"].astype(int)
d_em.columns = ["Ano","Prom.","Rep.","Evas.","EJA","N"]
for c in ["Prom.","Rep.","Evas.","EJA"]:
    d_em[c] = (d_em[c] * 100).round(1)
to_latex_table(d_em, "TA_BR_fluxo_em.tex",
    "Taxas de fluxo no Ensino Médio, Brasil, por ano (%).",
    "tab:ap_br_em",
    fmts={"Prom.":"{:.1f}","Rep.":"{:.1f}","Evas.":"{:.1f}","EJA":"{:.1f}"})

# T_C: abandono por serie (media 2017-2019 vs 2022-2024)
d = pd.read_csv(OUT / "AP_C_abandono_por_serie.csv")
d = d[~d.ano.isin([2020, 2021])].copy()
d_pre = d[d.ano.isin([2017,2018,2019])].groupby("serie")["flag_abandono"].mean()
d_pos = d[d.ano.isin([2022,2023,2024])].groupby("serie")["flag_abandono"].mean()
SERIE_ORDER = ["1o EF","2o EF","3o EF","4o EF","5o EF",
                "6o EF","7o EF","8o EF","9o EF","1o EM","2o EM","3o EM"]
res = pd.DataFrame({"Série": SERIE_ORDER,
                     "2017-2019 (%)": [d_pre.get(s, np.nan)*100 for s in SERIE_ORDER],
                     "2022-2024 (%)": [d_pos.get(s, np.nan)*100 for s in SERIE_ORDER]})
res["Δ (p.p.)"] = res["2022-2024 (%)"] - res["2017-2019 (%)"]
to_latex_table(res, "TA_C_abandono_serie.tex",
    "Abandono intra-ano por série, médias 2017-2019 vs 2022-2024 (\\%).",
    "tab:ap_c_abandono",
    fmts={"2017-2019 (%)":"{:.2f}","2022-2024 (%)":"{:.2f}","Δ (p.p.)":"{:+.2f}"})

# T_E: % concluiu EM aos 21 por quintil x ano
d = pd.read_csv(OUT / "AP_E_conclusao_por_quintil.csv")
d21 = d[d.idade == 21].copy()
d21 = d21.pivot(index="ano", columns="quintil", values="em")
ORDER = ["Q1 (mais pobre)","Q2","Q3","Q4","Q5 (mais rico)"]
d21 = (d21[ORDER] * 100).round(1).reset_index()
d21["ano"] = d21["ano"].astype(int)
d21.columns = ["Ano"] + ORDER
fmts = {c: "{:.1f}" for c in ORDER}
to_latex_table(d21, "TA_E_em_21_quintil.tex",
    "% concluiu Ensino Médio aos 21 anos por quintil de renda dom. per capita e ano.",
    "tab:ap_e_em21_quintil",
    fmts=fmts)

print("Tabelas LaTeX salvas.")
