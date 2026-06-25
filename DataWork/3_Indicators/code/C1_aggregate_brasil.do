* -------------------------------------------------------------------------
* C1_aggregate_brasil.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Indicadores agregados para o Brasil, por etapa-serie x ano (2012-2024).
*   Resultado: Tabela 1 + Figura 1 do paper.
*
* Inputs:
local PANEL_INTER  "$PANEL_INTER"
local PANEL_INTRA  "$PANEL_INTRA"
*
* Outputs:
*   output/T1_brasil_inter_por_serie_ano.csv  (Tabela 1 entre-anos)
*   output/T1_brasil_intra_por_serie_ano.csv  (Tabela 1 intra-ano)
*   output/F1_serie_temporal_indicadores.csv  (Figura 1 - serie 2012-24)
* -------------------------------------------------------------------------

//{ Entre-anos: 4 indicadores
use "`PANEL_INTER'", clear
_flag_inter

* Por (ano_t, etapa_t, serie_t)
preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (rawsum) n_obs=peso_v1_t (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(ano_t etapa_t serie_t)

label var flag_promocao   "Taxa de Promocao"
label var flag_repetencia "Taxa de Repetencia"
label var flag_evasao     "Taxa de Evasao"
label var flag_naoprog    "Taxa de Nao-progressao"
label var n_pessoa        "N pessoas no painel"

export delimited using "$OUTDIR/T1_brasil_inter_por_serie_ano.csv", replace
restore

* Por (ano_t, macroetapa)
preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(ano_t macroetapa)

export delimited using "$OUTDIR/T1_brasil_inter_por_macroetapa_ano.csv", replace
restore
//}

//{ Intra-ano: abandono
use "`PANEL_INTRA'", clear
_flag_intra

* Por (ano_cal, etapa_consolid_first, serie_first)
preserve
collapse (mean) flag_abandono ///
         (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(ano_cal etapa_consolid_first serie_first)

label var flag_abandono "Taxa de Abandono (intra-ano)"
export delimited using "$OUTDIR/T1_brasil_intra_por_serie_ano.csv", replace
restore

* Por (ano_cal, macroetapa)
preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(ano_cal macroetapa)

export delimited using "$OUTDIR/T1_brasil_intra_por_macroetapa_ano.csv", replace
restore
//}

//{ Consolidar para Figura 1 (serie temporal)
import delimited using "$OUTDIR/T1_brasil_inter_por_macroetapa_ano.csv", clear varnames(1)
gen ano = ano_t
drop ano_t
save "$TMPDIR/_inter_tmp.dta", replace

import delimited using "$OUTDIR/T1_brasil_intra_por_macroetapa_ano.csv", clear
gen ano = ano_cal
drop ano_cal

merge 1:1 ano macroetapa using "$TMPDIR/_inter_tmp.dta", nogenerate

export delimited using "$OUTDIR/F1_serie_temporal_indicadores.csv", replace
//}

di "C1 OK"
