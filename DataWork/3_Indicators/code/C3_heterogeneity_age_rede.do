* -------------------------------------------------------------------------
* C3_heterogeneity_age_rede.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Heterogeneidade dos 5 indicadores por:
*     - defasagem idade-serie (em dia / 1 ano def / 2+ anos def)
*     - rede agrupada (publica / privada)
*     - macroregiao (N, NE, SE, S, CO)
*
* Inputs:
local PANEL_INTER  "$PANEL_INTER"
local PANEL_INTRA  "$PANEL_INTRA"
*
* Outputs:
*   T3_heterog_defasagem.csv
*   T3_heterog_rede.csv
*   T3_heterog_regiao.csv
* -------------------------------------------------------------------------

//{ Por defasagem idade-serie
use "`PANEL_INTER'", clear
_flag_inter
keep if inrange(ano_t, 2018, 2023)
keep if !missing(defasagem_cat)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa defasagem_cat)
export delimited using "$OUTDIR/T3_heterog_defasagem.csv", replace
restore

use "`PANEL_INTRA'", clear
* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename sexo_first sexo

_flag_intra
keep if inrange(ano_cal, 2018, 2023)
keep if !missing(defasagem_cat)

preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(macroetapa defasagem_cat)
export delimited using "$OUTDIR/T3_heterog_defasagem_intra.csv", replace
restore
//}

//{ Por rede agrupada (Publica/Privada)
use "`PANEL_INTER'", clear
_flag_inter
keep if inrange(ano_t, 2018, 2023)
keep if !missing(rede_agrupada)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa rede_agrupada)
export delimited using "$OUTDIR/T3_heterog_rede.csv", replace
restore

use "`PANEL_INTRA'", clear
* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename sexo_first sexo

_flag_intra
keep if inrange(ano_cal, 2018, 2023)
keep if !missing(rede_agrupada)
preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(macroetapa rede_agrupada)
export delimited using "$OUTDIR/T3_heterog_rede_intra.csv", replace
restore
//}

//{ Por macroregiao
use "`PANEL_INTER'", clear
_flag_inter
keep if inrange(ano_t, 2018, 2023)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa regiao)
export delimited using "$OUTDIR/T3_heterog_regiao.csv", replace
restore

use "`PANEL_INTRA'", clear
* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename sexo_first sexo

_flag_intra
keep if inrange(ano_cal, 2018, 2023)
preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(macroetapa regiao)
export delimited using "$OUTDIR/T3_heterog_regiao_intra.csv", replace
restore
//}

di "C3 OK"
