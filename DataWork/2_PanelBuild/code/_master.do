* -------------------------------------------------------------------------
* _master.do - Modulo 2: Construcao do Painel Longitudinal da PNADC
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Constroi o painel longitudinal da PNADC trimestral (2012Q1-2024Q4) ligando
*   indivíduos ao longo das 5 visitas do painel rotativo. Output principal:
*   um arquivo .dta com pares (pessoa, transicao) que serve de base para o
*   modulo 3_Indicators.
*
*   Pipeline:
*     B1: carregar pnadc_long, criar IDs, harmonizar variaveis EF/EM/serie
*     B2: matching individuo entre visitas (hh_id + ordem + validacao sexo/idade)
*     B3: construir base de transicoes intra-ano e entre-anos
*     B4: anexar variaveis de programas sociais (BFA) de Visita 5 quando disponivel
*     B5: criar variaveis derivadas (defasagem idade-serie, quintis renda, perfil CadU-proxy)
*
* Inputs:
local PNADC_LONG  "$PRJ_ROOT/DataWork/1_DownloadPNADC/output/pnadc_long_2012_2024.dta"
local PNADC_V5    "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Novo_plano/tmp/v3/pnad_raw/parsed/"
*
* Outputs:
*   $OUTDIR/painel_pnadc_2012_2024.dta            (long: pessoa x transicao)
*   $OUTDIR/painel_pnadc_eja_2012_2024.dta        (subset EJA)
*   $OUTDIR/attrition_summary.csv                  (estatisticas de atrito)
*   $OUTDIR/panel_build_log.txt                    (log da execucao)
* -------------------------------------------------------------------------

clear all
clear mata
set more off

//{ Paths
if "`c(username)'" == "vitor" {
    global PRJ_ROOT "C:/Users/vitor/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
}
if "`c(username)'" == "Vitor" {
    global PRJ_ROOT "D:/Dropbox (Pessoal)/MEC_Pe_de_Meia/Nota_PNAD"
}
if "`c(username)'" == "vitpe" {
    global PRJ_ROOT "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
}

global MOD_ROOT  "$PRJ_ROOT/DataWork/2_PanelBuild"
global INPDIR    "$MOD_ROOT/input"
global CODDIR    "$MOD_ROOT/code"
global OUTDIR    "$MOD_ROOT/output"
global TMPDIR    "$MOD_ROOT/tmp"
//}

//{ Executables
global rscript  "C:\Program Files\R\R-4.5.0\bin\Rscript.exe"
global stata    "C:\Program Files\StataNow19\StataMP-64.exe"
//}

cd "$CODDIR"

//{ Log
cap log close
log using "$OUTDIR/panel_build_log.txt", replace text
//}

//{ Pipeline
do "$CODDIR/B1_harmonize_pnadc.do"
do "$CODDIR/B2_link_individuals.do"
do "$CODDIR/B3_build_transitions.do"
do "$CODDIR/B4_attach_bfa_v5.do"
do "$CODDIR/B5_derive_variables.do"
//}

log close
