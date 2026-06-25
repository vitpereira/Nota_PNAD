* -------------------------------------------------------------------------
* C9_sim_ferias.do
* -------------------------------------------------------------------------
* Author: Vitor (auto-generated)
* Last update: 2026-06-25
*
* Description:
*   Simulacao do efeito do periodo de ferias (Q1 = jan-mar) sobre os
*   indicadores de fluxo inter-anuais. Hipotese: ao medir a serie em Q1
*   de t+1 (logo apos a virada do ano), o sistema escolar ainda esta em
*   periodo de transicao/ferias, e familias podem reportar a serie do ano
*   anterior, gerando FALSA repetencia.
*
*   Compara 3 versoes:
*     A. Baseline: trim_t e trim_t1 livres (atual)
*     B. Exclui Q1 de t+1: trim_t1 >= 2
*     C. Apenas Q2-Q4 nos dois lados: trim_t >= 2 & trim_t1 >= 2
*
* Inputs:
local PANEL "DataWork/2_PanelBuild/output/painel_pnadc_2012_2024.dta"
*
* Outputs:
local OUT_A "DataWork/3_Indicators/output/C9_sim_A_baseline.csv"
local OUT_B "DataWork/3_Indicators/output/C9_sim_B_sem_Q1_t1.csv"
local OUT_C "DataWork/3_Indicators/output/C9_sim_C_Q2Q4_ambos.csv"
local OUT_COMP "DataWork/3_Indicators/output/C9_sim_comparison.csv"
local OUT_TRIM "DataWork/3_Indicators/output/C9_distrib_trim.csv"

set more off

* =========================================================================
* 0. Diagnostico: distribuicao de (trim_t, trim_t1) no baseline
* =========================================================================
use "`PANEL'", clear

* Restringir ao universo principal: EF + EM (excluir EJA)
keep if inlist(macroetapa, "EF iniciais", "EF finais", "EM")
keep if freq_escola_t == 1   // entrou matriculado em t

* Distribuicao dos pares (trim_t, trim_t1)
preserve
    contract trim_t trim_t1, freq(_freq)
    rename _freq n_pares
    gen pct = 100 * n_pares / r(N)
    export delimited using "`OUT_TRIM'", replace
    list trim_t trim_t1 n_pares, sepby(trim_t) noobs
restore

* =========================================================================
* 1. Definir flags de transicao (igual ao calculo principal)
* =========================================================================
gen flag_promocao  = (freq_escola_t1 == 1) & (serie_t1 == serie_t + 1)
gen flag_repetencia = (freq_escola_t1 == 1) & (serie_t1 == serie_t)
gen flag_evasao    = (freq_escola_t1 == 0)
gen flag_naoprog   = flag_repetencia | flag_evasao

* Cobertura: tem que ter freq_escola_t1 nao-missing
keep if !missing(freq_escola_t1)
keep if !missing(serie_t) & !missing(serie_t1)
* Promocao=missing se freq em t+1 mas serie missing — manter conservadoramente

* Peso
gen wt = peso_v1_t

* =========================================================================
* 2. Funcao para tabular indicadores por macroetapa-ano com um peso/filtro
* =========================================================================
capture program drop _tabula
program define _tabula
    syntax , out(string) [filter(string)]
    preserve
    if "`filter'" != "" {
        keep if `filter'
    }
    collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
             (count) n_pessoa = flag_promocao ///
             [aw=wt], by(ano_t macroetapa)
    export delimited using "`out'", replace
    di "Saved: `out'"
    restore
end

* =========================================================================
* 3. Tres cenarios
* =========================================================================
_tabula, out("`OUT_A'") filter("")
_tabula, out("`OUT_B'") filter("trim_t1 >= 2")
_tabula, out("`OUT_C'") filter("trim_t >= 2 & trim_t1 >= 2")

* =========================================================================
* 4. Build comparacao lado-a-lado
* =========================================================================
foreach v in A B C {
    preserve
    if "`v'" == "A" import delimited "`OUT_A'", clear
    if "`v'" == "B" import delimited "`OUT_B'", clear
    if "`v'" == "C" import delimited "`OUT_C'", clear
    foreach var in flag_promocao flag_repetencia flag_evasao flag_naoprog n_pessoa {
        rename `var' `var'_`v'
    }
    tempfile t`v'
    save `t`v''
    restore
}

use `tA', clear
merge 1:1 ano_t macroetapa using `tB', nogen
merge 1:1 ano_t macroetapa using `tC', nogen
order ano_t macroetapa flag_promocao_A flag_promocao_B flag_promocao_C ///
      flag_repetencia_A flag_repetencia_B flag_repetencia_C ///
      flag_evasao_A flag_evasao_B flag_evasao_C ///
      n_pessoa_A n_pessoa_B n_pessoa_C
sort macroetapa ano_t
export delimited using "`OUT_COMP'", replace
di "Saved: `OUT_COMP'"

* =========================================================================
* 5. Reporte: tabela compacta promocao + repetencia A vs B vs C
* =========================================================================
di "=== PROMOCAO ==="
format flag_promocao_* flag_repetencia_* flag_evasao_* %5.3f
list ano_t macroetapa flag_promocao_A flag_promocao_B flag_promocao_C ///
     if inlist(ano_t, 2018, 2019, 2022, 2023), sepby(macroetapa) noobs abbrev(20)

di " "
di "=== REPETENCIA ==="
list ano_t macroetapa flag_repetencia_A flag_repetencia_B flag_repetencia_C ///
     if inlist(ano_t, 2018, 2019, 2022, 2023), sepby(macroetapa) noobs abbrev(20)

di " "
di "=== EVASAO ==="
list ano_t macroetapa flag_evasao_A flag_evasao_B flag_evasao_C ///
     if inlist(ano_t, 2018, 2019, 2022, 2023), sepby(macroetapa) noobs abbrev(20)

exit
