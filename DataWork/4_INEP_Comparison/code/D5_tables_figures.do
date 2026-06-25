* -------------------------------------------------------------------------
* D5_tables_figures.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Gera Tabela 4 (comparacao PNADC x INEP com decomposicao) e dados para
*   Figura 1 (series temporais sobrepostas).
*
* Outputs:
*   output/T4_comparacao_pnadc_inep.tex   (booktabs)
*   output/T4_comparacao_pnadc_inep.csv
* -------------------------------------------------------------------------

use "$OUTDIR/decomposicao_R_U_S_C_M.dta", clear

* Snapshot: ano 2023 (ou ultimo disponivel)
keep if ano == 2023

* Reorganizar para formato de tabela
sort etapa_str indicador
list etapa_str indicador pnadc_valor inep_valor delta ///
     component_R component_U component_S component_C component_M, sep(0)

* Exportar
export delimited using "$OUTDIR/T4_comparacao_pnadc_inep_2023.csv", replace

di "D5 OK"
