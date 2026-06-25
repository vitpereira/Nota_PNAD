# -------------------------------------------------------------------------
# F4_atrito_robustez.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-24
#
# Description:
#   Figura 4 (robustez) - comparacao de caracteristicas observaveis entre
#   indivíduos RETIDOS no painel (>= 2 visitas) e PERDIDOS (so 1 visita).
#
#   Distribuicoes: idade, renda PC, % mulheres, % preta+parda, % publica.
#
# Inputs:
#   2_PanelBuild/output/link_stats.csv (resumo de matching)
#   2_PanelBuild/output/painel_pnadc_2012_2024.dta (long, mas usaremos
#   um summary aggregado salvo separadamente)
#
# Outputs:
#   output/F4_atrito_caracteristicas.pdf
# -------------------------------------------------------------------------

F4_INPUT <- file.path(ROOT, "DataWork", "2_PanelBuild", "output", "attrition_summary.csv")

if (!file.exists(F4_INPUT)) {
    cat("F4 SKIP: input nao encontrado em", F4_INPUT, "\n")
    cat("        (sera produzido pelo modulo 2_PanelBuild via B2_link_individuals.do)\n")
} else {
    df <- read_csv(F4_INPUT, show_col_types = FALSE)
    cat("F4 PENDING: figura sera escrita quando attrition_summary.csv estiver populado\n")
}
