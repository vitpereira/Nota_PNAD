* -------------------------------------------------------------------------
* C4_by_uf.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Indicadores por UF (27 unidades). Vai para Apendice A.
*
* Inputs:
local PANEL_INTER  "$PANEL_INTER"
local PANEL_INTRA  "$PANEL_INTRA"
*
* Outputs:
*   A1_indicadores_por_uf.csv  -- todos 5 indicadores x 27 UFs x macroetapa
* -------------------------------------------------------------------------

//{ Entre-anos por UF
use "`PANEL_INTER'", clear
_flag_inter
keep if inrange(ano_t, 2018, 2023)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(UF macroetapa)
export delimited using "$OUTDIR/A1_inter_por_uf.csv", replace
restore
//}

//{ Intra-ano (abandono) por UF
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
         [aw=peso_v1028_first], by(UF macroetapa)
export delimited using "$OUTDIR/A1_intra_por_uf.csv", replace
restore
//}

di "C4 OK"
