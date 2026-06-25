* -------------------------------------------------------------------------
* D3_decompose.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Decomposicao da diferenca Delta = inep - pnadc em 5 fontes:
*     R - Retorno: % de alunos que estudaram em t e mudaram de rede/modalidade
*                  entre t e t+1 (limite superior estimavel via PNADC)
*     U - Universo: |denom_inep / denom_pnadc - 1|
*     S - Sampling: IC 95% via bootstrap (a fazer com Stata-MP)
*     C - sub-Cobertura: % de pop estudando PNADC > matriculas Censo
*     M - residual: Delta - (R + U + S + C)
*
* Inputs:
local COMP    "$OUTDIR/comparacao_pnadc_inep.dta"
local CAPT_R  "$PRJ_ROOT/DataWork/3_Indicators/output/F3_captura_retorno_por_macroetapa.csv"
*
* Outputs:
local DECOMP  "$OUTDIR/decomposicao_RUSC M.dta"
local DEC_CSV "$OUTDIR/decomposicao_R_U_S_C_M.csv"
* -------------------------------------------------------------------------

//{ Carregar dados de comparacao
use "`COMP'", clear

//{ Componente R (retorno)
preserve
import delimited using "`CAPT_R'", clear varnames(1)
gen str etapa_str = ""
replace etapa_str = "EF iniciais" if macroetapa == 1
replace etapa_str = "EF finais"   if macroetapa == 2
replace etapa_str = "EM"          if macroetapa == 3
keep etapa_str mudou_rede mudou_modalidade
rename mudou_rede component_R_rede
rename mudou_modalidade component_R_modalidade
gen component_R = component_R_rede + component_R_modalidade
tempfile R
save `R'
restore

merge m:1 etapa_str using `R', keepusing(component_R) nogenerate
//}

//{ Componentes U, S, C - PLACEHOLDER
* Por enquanto, U=., S=., C=. - serao preenchidos quando dados INEP estiverem disponiveis
gen component_U = .
gen component_S = .
gen component_C = .

* Componente M (residual) = Delta - (R + U + S + C)
gen component_M = .
replace component_M = delta - component_R if !missing(delta, component_R) ///
    & missing(component_U, component_S, component_C)
//}

//{ Exportar
keep ano etapa_str indicador pnadc_valor inep_valor delta ///
     component_R component_U component_S component_C component_M

save "`DECOMP'", replace
export delimited using "`DEC_CSV'", replace
di "D3 OK (decomposicao parcial - U/S/C pendentes)"
//}
