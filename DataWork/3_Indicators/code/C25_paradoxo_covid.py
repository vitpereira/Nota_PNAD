# -------------------------------------------------------------------------
# C25_paradoxo_covid.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Tabela comparativa PNADC v5 vs INEP nos anos COVID e adjacentes
#   (2018-2021). Documenta o paradoxo: INEP mostra promocao SUBINDO em 2020
#   (aprovacao automatica), PNADC mostra promocao CAINDO. Hipotese:
#   PNADC capta auto-relato familiar (mae nao sabe que filho foi promovido
#   automaticamente, ou continua reportando serie antiga).
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# PNADC v5
pnadc = pd.read_csv(OUT_DIR / "T1_brasil_inter_v5_main.csv")
pnadc = pnadc[pnadc["ano_t"].between(2018, 2021)]

# INEP
inep = pd.read_csv(ROOT / "DataWork/4_INEP_Comparison/output/inep_transicao_long.csv")
inep = inep[(inep.unidade == "Brasil") &
             (inep.etapa.isin(["EF_AI", "EF_AF", "Total_EM"]))].copy()
inep = inep[inep.ano_t.between(2018, 2021)]
inep["macroetapa"] = inep["etapa"].map({"EF_AI": "EF iniciais",
                                          "EF_AF": "EF finais",
                                          "Total_EM": "EM"})
inep_w = inep.pivot_table(index=["ano_t", "macroetapa"],
                            columns="indicador", values="valor").reset_index()

def fmt(x):
    try: return f"{float(x)*100:.1f}" if abs(x) < 1.5 else f"{float(x):.1f}"
    except: return "---"

# Build LaTeX table: rows = (macroetapa, ano), cols = INEP/PNADC for prom/rep/evas
panels = [("EF iniciais", "EF iniciais"),
           ("EF finais", "EF finais"),
           ("EM", "EM")]

lines = []
lines.append("% C25 paradoxo COVID")
lines.append(r"\begin{table}[htbp]\centering")
lines.append(r"\caption{Paradoxo COVID: comparac\~ao direta entre INEP e PNADC v5 nos anos 2018--2021. Durante 2020 e 2021, o INEP registra promoc\~ao mais alta e repet\^encia mais baixa (compat\'ivel com aprovac\~ao autom\'atica), enquanto a PNADC registra o oposto.}")
lines.append(r"\label{tab:paradoxo_covid}")
lines.append(r"\begin{threeparttable}\small")
lines.append(r"\begin{tabular}{lrrrrrrrr}\toprule")
lines.append(r"& \multicolumn{2}{c}{Promo\c{c}\~ao (\%)} & \multicolumn{2}{c}{Repet\^encia (\%)} & \multicolumn{2}{c}{Evas\~ao (\%)} & \multicolumn{2}{c}{$\Delta$ prom.\ (pp)} \\")
lines.append(r"\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7} \cmidrule(lr){8-9}")
lines.append(r"Ano $t$ & INEP & PNADC & INEP & PNADC & INEP & PNADC & 2020/19 & 2021/19 \\")
lines.append(r"\midrule")

for _, label in panels:
    lines.append(rf"\multicolumn{{9}}{{l}}{{\textit{{{label}}}}} \\")
    lines.append(r"\midrule")
    # Get reference 2019 for delta
    p19 = pnadc[(pnadc.ano_t == 2019) & (pnadc.macroetapa == label)]
    i19 = inep_w[(inep_w.ano_t == 2019) & (inep_w.macroetapa == label)]

    for ano in [2018, 2019, 2020, 2021]:
        p_row = pnadc[(pnadc.ano_t == ano) & (pnadc.macroetapa == label)]
        i_row = inep_w[(inep_w.ano_t == ano) & (inep_w.macroetapa == label)]
        if len(p_row) == 0 or len(i_row) == 0: continue
        p_prom = p_row.iloc[0].flag_promocao * 100
        p_rep  = p_row.iloc[0].flag_repetencia * 100
        p_evas = p_row.iloc[0].flag_evasao * 100
        i_prom = i_row.iloc[0].promocao
        i_rep  = i_row.iloc[0].repetencia
        i_evas = i_row.iloc[0].evasao
        # Delta de promoção INEP e PNADC vs 2019
        if ano == 2020 and len(p19) > 0 and len(i19) > 0:
            d_inep = i_prom - i19.iloc[0].promocao
            d_pnadc = p_prom - p19.iloc[0].flag_promocao * 100
            delta_str = f" & I:{d_inep:+.1f} P:{d_pnadc:+.1f} &"
        elif ano == 2021 and len(p19) > 0 and len(i19) > 0:
            d_inep = i_prom - i19.iloc[0].promocao
            d_pnadc = p_prom - p19.iloc[0].flag_promocao * 100
            delta_str = f" & & I:{d_inep:+.1f} P:{d_pnadc:+.1f}"
        else:
            delta_str = " & & "
        lines.append(rf"{ano} & {i_prom:.1f} & {p_prom:.1f} & "
                      rf"{i_rep:.1f} & {p_rep:.1f} & "
                      rf"{i_evas:.1f} & {p_evas:.1f}"
                      rf"{delta_str} \\")
    lines.append(r"\\[0.3em]")
if lines[-1] == r"\\[0.3em]": lines.pop()
lines.append(r"\bottomrule\end{tabular}")
lines.append(r"\begin{tablenotes}\footnotesize")
lines.append(r"\item \textit{Fontes:} INEP Indicadores de Trajet\'oria (Brasil) e painel longitudinal PNADC v5.")
lines.append(r"\item \textit{Notas:} ``$\Delta$ prom.\ 2020/19'' \'e a varia\c{c}\~ao da promoc\~ao em 2020 em relac\~ao a 2019, pelas duas fontes (I = INEP, P = PNADC). Sinais opostos entre INEP e PNADC indicam que as duas fontes capturam dimens\~oes distintas do mesmo fen\^omeno: registro administrativo de matr\'icula vs.\ auto-relato familiar sobre a situac\~ao escolar.")
lines.append(r"\end{tablenotes}\end{threeparttable}\end{table}")

(OUT_DIR / "T_paradoxo_covid.tex").write_text("\n".join(lines) + "\n",
                                                 encoding="utf-8")
print("Saved T_paradoxo_covid.tex")
print()
# Print to console
for _, label in panels:
    print(f"=== {label} ===")
    for ano in [2019, 2020, 2021]:
        p_row = pnadc[(pnadc.ano_t == ano) & (pnadc.macroetapa == label)]
        i_row = inep_w[(inep_w.ano_t == ano) & (inep_w.macroetapa == label)]
        if len(p_row) == 0 or len(i_row) == 0: continue
        p_prom = p_row.iloc[0].flag_promocao * 100
        p_rep  = p_row.iloc[0].flag_repetencia * 100
        i_prom = i_row.iloc[0].promocao
        i_rep  = i_row.iloc[0].repetencia
        print(f"  {ano}: INEP prom={i_prom:.1f}%/rep={i_rep:.1f}% | "
              f"PNADC prom={p_prom:.1f}%/rep={p_rep:.1f}%")
