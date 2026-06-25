* -------------------------------------------------------------------------
* D2_merge_pnadc_inep.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Faz merge dos resultados PNADC (modulo 3) com os indicadores INEP
*   (D1). Output: tabela longa com colunas pnadc_valor e inep_valor lado
*   a lado, com diferenca Delta = inep_valor - pnadc_valor.
*
* Inputs:
local INEP_LONG  "$OUTDIR/inep_indicadores_long.dta"
*
* Outputs:
local COMP       "$OUTDIR/comparacao_pnadc_inep.dta"
local COMP_CSV   "$OUTDIR/comparacao_pnadc_inep.csv"
* -------------------------------------------------------------------------

//{ Carregar PNADC C1 (macroetapa) ----
import delimited using "$PNADC_C1", clear varnames(1)
rename macroetapa etapa_num
gen str etapa_str = ""
replace etapa_str = "EF iniciais" if etapa_num == 1
replace etapa_str = "EF finais"   if etapa_num == 2
replace etapa_str = "EM"          if etapa_num == 3
replace etapa_str = "EJA EF"      if etapa_num == 4
replace etapa_str = "EJA EM"      if etapa_num == 5

gen ano = ano_t
keep ano etapa_str flag_promocao flag_repetencia flag_evasao flag_naoprog n_pessoa

* Reshape long
rename flag_promocao   pnadc_promocao
rename flag_repetencia pnadc_repetencia
rename flag_evasao     pnadc_evasao
rename flag_naoprog    pnadc_naoprog

reshape long pnadc_, i(ano etapa_str) j(indicador) string

* Adicionar abandono (intra-ano)
preserve
import delimited using "$PRJ_ROOT/DataWork/3_Indicators/output/T1_brasil_intra_por_macroetapa_ano.csv", clear varnames(1)
rename macroetapa etapa_num
gen str etapa_str = ""
replace etapa_str = "EF iniciais" if etapa_num == 1
replace etapa_str = "EF finais"   if etapa_num == 2
replace etapa_str = "EM"          if etapa_num == 3
replace etapa_str = "EJA EF"      if etapa_num == 4
replace etapa_str = "EJA EM"      if etapa_num == 5
gen ano = ano_cal
keep ano etapa_str flag_abandono
rename flag_abandono pnadc_
gen str indicador = "abandono"
tempfile abandono
save `abandono'
restore

append using `abandono'
rename pnadc_ pnadc_valor

save "$TMPDIR/pnadc_long.dta", replace
//}

//{ Merge com INEP ----
* Esperamos que INEP_LONG tenha colunas: ano, etapa, indicador, valor
* INEP usa nomenclatura propria de etapa - precisaremos mapear
use "`INEP_LONG'", clear
* Por enquanto, INEP_LONG esta vazio. Se nao vazio, faria merge aqui.

count
if r(N) > 0 {
    rename valor inep_valor
    rename etapa etapa_str
    keep ano etapa_str indicador inep_valor

    merge 1:1 ano etapa_str indicador using "$TMPDIR/pnadc_long.dta", nogenerate
    gen delta = inep_valor - pnadc_valor

    save "`COMP'", replace
    export delimited using "`COMP_CSV'", replace
}
else {
    * Placeholder - so PNADC, sem INEP
    use "$TMPDIR/pnadc_long.dta", clear
    gen inep_valor = .
    gen delta = .
    save "`COMP'", replace
    export delimited using "`COMP_CSV'", replace
    di "D2: INEP vazio - so PNADC nas tabelas de comparacao"
}
//}

di "D2 OK"
