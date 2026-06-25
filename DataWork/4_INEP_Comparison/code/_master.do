* -------------------------------------------------------------------------
* _master.do - Modulo 4: Comparacao PNADC x INEP + decomposicao
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Compara os 5 indicadores calculados via PNADC (modulo 3) com os
*   Indicadores Educacionais do INEP. Decompoe a diferenca em 5 fontes:
*     R - Retorno (PNADC capta, INEP nao)
*     U - Universo (diferenca de denominadores)
*     S - Sampling (IC 95% por bootstrap com cluster em UPA)
*     C - sub-Cobertura do Censo
*     M - erro de Medida (residual)
*
*   Equacao: Delta_ind = R + U + S + C + M
*
* Pipeline:
*   D0: importar INEP (do .xlsx baixado em A1)
*   D1: harmonizar series INEP (etapa, ano, UF)
*   D2: merge com PNADC
*   D3: decomposicao Delta = R+U+S+C+M
*   D4: bootstrap para CI
*   D5: tabelas e figuras de comparacao
* -------------------------------------------------------------------------

clear all
clear mata
set more off

//{ Paths
if "`c(username)'" == "vitpe" {
    global PRJ_ROOT "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
}

global MOD_ROOT  "$PRJ_ROOT/DataWork/4_INEP_Comparison"
global INPDIR    "$MOD_ROOT/input"
global CODDIR    "$MOD_ROOT/code"
global OUTDIR    "$MOD_ROOT/output"
global TMPDIR    "$MOD_ROOT/tmp"

* PNADC results
global PNADC_C1   "$PRJ_ROOT/DataWork/3_Indicators/output/T1_brasil_inter_por_macroetapa_ano.csv"
global PNADC_C1_S "$PRJ_ROOT/DataWork/3_Indicators/output/T1_brasil_inter_por_serie_ano.csv"
//}

cd "$CODDIR"

cap log close
log using "$OUTDIR/comparison_log.txt", replace text

//{ Pipeline
* D0: download INEP foi feito via Python (A1_download_inep.py)
shell python "$CODDIR/A1_download_inep.py"

do "$CODDIR/D1_import_inep.do"
do "$CODDIR/D2_merge_pnadc_inep.do"
do "$CODDIR/D3_decompose.do"
* do "$CODDIR/D4_bootstrap_ci.do"     (depois - exige Stata-MP)
do "$CODDIR/D5_tables_figures.do"
//}

log close
