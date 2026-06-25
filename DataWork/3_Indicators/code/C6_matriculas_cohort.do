* -------------------------------------------------------------------------
* C6_matriculas_cohort.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-25
*
* Description:
*   Replica as Figuras 2 e 3 de Fernandes (2011), analisadas no IMDS A002
*   (Pereira 2022). Mostra o numero total de matriculas por trimestre ao
*   longo de pseudocoortes que comecam no 8o EF e progridem ate o 3o EM.
*
*   Cada coorte cobre 16 trimestres (4 anos x 4 trimestres). Quedas dentro
*   do ano = abandono. Quedas entre anos = evasao + repetencia + migracao.
*
*   Versao 1: todos os alunos
*   Versao 2: apenas alunos SEM defasagem idade-serie (em dia)
*
* Inputs:
local PNADC_H  "$PRJ_ROOT/DataWork/2_PanelBuild/tmp/pnadc_harmonized.dta"
*
* Outputs:
*   $OUTDIR/F4_matriculas_cohort_full.csv
*   $OUTDIR/F4_matriculas_cohort_emdia.csv
* -------------------------------------------------------------------------

use "`PNADC_H'", clear

* Defasagem idade-serie (para versao 2 / Figura 3)
gen byte idade_padrao = .
replace idade_padrao = serie + 5  if inlist(etapa_consolid, 4, 5)  // EF
replace idade_padrao = 15 if etapa_consolid == 10
replace idade_padrao = 16 if etapa_consolid == 11
replace idade_padrao = 17 if etapa_consolid == 12
gen def_anos = idade - idade_padrao
gen byte em_dia = (def_anos <= 0)

* Manter so EF finais (etapa 5) e EM (10, 11, 12)
keep if inlist(etapa_consolid, 5, 10, 11, 12) & freq_escola == 1

* Marcar serie consolidada (8 = 8o EF, 91 = 9o EF, 10 = 1o EM, 11 = 2o EM, 12 = 3o EM)
gen byte serie_cohort = .
replace serie_cohort = 8  if etapa_consolid == 5 & serie == 8
replace serie_cohort = 9  if etapa_consolid == 5 & serie == 9
replace serie_cohort = 10 if etapa_consolid == 10
replace serie_cohort = 11 if etapa_consolid == 11
replace serie_cohort = 12 if etapa_consolid == 12
keep if !missing(serie_cohort)

* Tempo (ano-trimestre como decimal)
gen double tempo = Ano + (Trimestre - 1)/4

* Periodo: 2014 (8o EF) ate 2024 (varias coortes possiveis)
* Cada coorte: comeca em 8o EF no ano c, vai ate 3o EM no ano c+4
* Mas como nossa serie comeca em 2012, podemos ter coortes 2014, 2015, ..., 2020

* { Versao Full (Figura 2 estilo IMDS) ----
preserve
collapse (sum) total_matr = peso_v1028 (count) n_obs = idade, ///
    by(Ano Trimestre serie_cohort tempo)
gen serie_lbl = ""
replace serie_lbl = "8o EF"  if serie_cohort == 8
replace serie_lbl = "9o EF"  if serie_cohort == 9
replace serie_lbl = "1o EM"  if serie_cohort == 10
replace serie_lbl = "2o EM"  if serie_cohort == 11
replace serie_lbl = "3o EM"  if serie_cohort == 12

export delimited using "$OUTDIR/F4_matriculas_serie_trimestre.csv", replace
restore
* } ----

* { Versao Em dia (Figura 3 estilo IMDS) ----
preserve
keep if em_dia == 1
collapse (sum) total_matr = peso_v1028 (count) n_obs = idade, ///
    by(Ano Trimestre serie_cohort tempo)
gen serie_lbl = ""
replace serie_lbl = "8o EF"  if serie_cohort == 8
replace serie_lbl = "9o EF"  if serie_cohort == 9
replace serie_lbl = "1o EM"  if serie_cohort == 10
replace serie_lbl = "2o EM"  if serie_cohort == 11
replace serie_lbl = "3o EM"  if serie_cohort == 12

export delimited using "$OUTDIR/F4_matriculas_serie_trimestre_emdia.csv", replace
restore
* } ----

* { Versao de Coorte (linha por cohort entry year) ----
* Para cada ano-coorte c, criar uma linha com 5 sub-paineis (8oEF, 9oEF, 1oEM, 2oEM, 3oEM)
* sequenciados temporalmente: 8oEF ano c, 9oEF c+1, 1oEM c+2, 2oEM c+3, 3oEM c+4
* OU mais simples: cohort = "8o EF em ano c", e gerar curve de 16 trimestres

use "`PNADC_H'", clear
keep if inlist(etapa_consolid, 5, 10, 11, 12) & freq_escola == 1
gen byte idade_padrao = .
replace idade_padrao = serie + 5  if etapa_consolid == 5
replace idade_padrao = 15 if etapa_consolid == 10
replace idade_padrao = 16 if etapa_consolid == 11
replace idade_padrao = 17 if etapa_consolid == 12
gen def_anos = idade - idade_padrao
gen byte em_dia = (def_anos <= 0)

gen byte serie_cohort = .
replace serie_cohort = 8  if etapa_consolid == 5 & serie == 8
replace serie_cohort = 10 if etapa_consolid == 10
replace serie_cohort = 11 if etapa_consolid == 11
replace serie_cohort = 12 if etapa_consolid == 12

collapse (sum) total_matr = peso_v1028, by(Ano Trimestre serie_cohort em_dia)

* Para cada cohort entry ano c, gerar linha sequencial:
*   8o EF: Ano = c
*   1o EM: Ano = c+1
*   2o EM: Ano = c+2
*   3o EM: Ano = c+3
* tempo_t na linha = trimestre desde o inicio da coorte (0 a 15)

gen byte serie_offset = .
replace serie_offset = 0 if serie_cohort == 8     // 8oEF: ano 0
replace serie_offset = 1 if serie_cohort == 10    // 1oEM: ano 1
replace serie_offset = 2 if serie_cohort == 11    // 2oEM: ano 2
replace serie_offset = 3 if serie_cohort == 12    // 3oEM: ano 3
keep if !missing(serie_offset)

* Cohort entry year = Ano - serie_offset
gen int cohort_year = Ano - serie_offset
* Trimestre relativo na coorte (0-15)
gen byte tempo_rel = serie_offset*4 + (Trimestre - 1)

* Manter coortes que entraram entre 2013 e 2020 (com 4 anos de seguimento ate 2024)
keep if cohort_year >= 2013 & cohort_year <= 2020

preserve
keep if em_dia == 0  // versao com TODOS (Figura 2 IMDS)
* Para ter "Total" precisa somar em_dia=0 e em_dia=1
restore

* Para a Figura 2 (estilo IMDS): total
preserve
collapse (sum) total_matr, by(cohort_year tempo_rel serie_cohort)
gen serie_lbl = ""
replace serie_lbl = "8o EF"  if serie_cohort == 8
replace serie_lbl = "1o EM"  if serie_cohort == 10
replace serie_lbl = "2o EM"  if serie_cohort == 11
replace serie_lbl = "3o EM"  if serie_cohort == 12
export delimited using "$OUTDIR/F4_cohort_total.csv", replace
restore

* Para a Figura 3 (estilo IMDS): apenas em dia
preserve
keep if em_dia == 1
collapse (sum) total_matr, by(cohort_year tempo_rel serie_cohort)
gen serie_lbl = ""
replace serie_lbl = "8o EF"  if serie_cohort == 8
replace serie_lbl = "1o EM"  if serie_cohort == 10
replace serie_lbl = "2o EM"  if serie_cohort == 11
replace serie_lbl = "3o EM"  if serie_cohort == 12
export delimited using "$OUTDIR/F4_cohort_emdia.csv", replace
restore
* } ----

di "C6 OK"
