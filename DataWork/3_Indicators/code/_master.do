* -------------------------------------------------------------------------
* _master.do - Modulo 3: Calculo dos 5 indicadores de fluxo
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Calcula os 5 indicadores de fluxo escolar usando o painel longitudinal:
*     - Abandono (intra-ano)
*     - Evasao (entre-anos)
*     - Promocao/Aprovacao (entre-anos)
*     - Repetencia/Reprovacao (entre-anos)
*     - Nao-progressao (entre-anos)
*
*   Para cada indicador, calcula:
*     C1: agregados Brasil por etapa/serie/ano
*     C2: heterogeneidade socioeconomica (renda, raca, sexo, BFA)
*     C3: heterogeneidade idade-serie e rede
*     C4: por UF e regiao
*     C5: serie temporal de captura de retorno (mudanca de rede)
*
*   Outputs em CSV (para R/ggplot) e .tex (booktabs + threeparttable).
* -------------------------------------------------------------------------

clear all
clear mata
set more off

//{ Paths
if "`c(username)'" == "vitpe" {
    global PRJ_ROOT "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
}

global MOD_ROOT  "$PRJ_ROOT/DataWork/3_Indicators"
global INPDIR    "$MOD_ROOT/input"
global CODDIR    "$MOD_ROOT/code"
global OUTDIR    "$MOD_ROOT/output"
global TMPDIR    "$MOD_ROOT/tmp"

* Input vem do modulo 2
global PANEL_INTER "$PRJ_ROOT/DataWork/2_PanelBuild/output/painel_pnadc_2012_2024.dta"
global PANEL_INTRA "$PRJ_ROOT/DataWork/2_PanelBuild/output/painel_pnadc_intra_2012_2024.dta"
global PANEL_EJA   "$PRJ_ROOT/DataWork/2_PanelBuild/output/painel_pnadc_eja_2012_2024.dta"
//}

cd "$CODDIR"

cap log close
log using "$OUTDIR/indicators_log.txt", replace text

//{ Carregar funcoes auxiliares
do "$CODDIR/._compute_indicator.do"
//}

//{ Pipeline
do "$CODDIR/C1_aggregate_brasil.do"
do "$CODDIR/C2_heterogeneity_socio.do"
do "$CODDIR/C3_heterogeneity_age_rede.do"
do "$CODDIR/C4_by_uf.do"
do "$CODDIR/C5_capture_retorno.do"
//}

log close
