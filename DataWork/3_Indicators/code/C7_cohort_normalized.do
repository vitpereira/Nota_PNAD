* -------------------------------------------------------------------------
* C7_cohort_normalized.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-25
*
* Description:
*   Replica Figuras 2/3 do Fernandes (2011) - IMDS A002 (Pereira 2022) usando
*   PNADC trimestral, MAS normalizando cada coorte para 100 no inicio do
*   8o EF (ou primeiro ponto de observacao da serie). Isso elimina o problema
*   de calibracao do V1028 mudar entre 2012-2024.
*
*   Para cada coorte cohort_year c:
*     - 8o EF em ano c, trim 1-4 => tempo_rel = 0,1,2,3
*     - 1o EM em ano c+1, trim 1-4 => tempo_rel = 4,5,6,7
*     - 2o EM em ano c+2, trim 1-4 => tempo_rel = 8,9,10,11
*     - 3o EM em ano c+3, trim 1-4 => tempo_rel = 12,13,14,15
*   Normalizar para 100 no tempo_rel = 0 do 8o EF dessa coorte.
*
*   Linhas separadas por cohort_year c.
*
* Inputs:
local PNADC_H  "$PRJ_ROOT/DataWork/2_PanelBuild/tmp/pnadc_harmonized.dta"
*
* Outputs:
*   $OUTDIR/F4_cohort_normalized.csv       (total)
*   $OUTDIR/F4_cohort_normalized_emdia.csv  (sem defasagem)
* -------------------------------------------------------------------------

use "`PNADC_H'", clear

* So estudantes do EF finais e EM regular
keep if inlist(etapa_consolid, 5, 10, 11, 12) & freq_escola == 1

* Defasagem
gen byte idade_padrao = .
replace idade_padrao = serie + 5  if etapa_consolid == 5
replace idade_padrao = 15 if etapa_consolid == 10
replace idade_padrao = 16 if etapa_consolid == 11
replace idade_padrao = 17 if etapa_consolid == 12
gen byte em_dia = (idade - idade_padrao <= 0)

* Codifica serie e offset
gen byte serie_cohort = .
replace serie_cohort = 8  if etapa_consolid == 5 & serie == 8
replace serie_cohort = 10 if etapa_consolid == 10
replace serie_cohort = 11 if etapa_consolid == 11
replace serie_cohort = 12 if etapa_consolid == 12

gen byte serie_offset = .
replace serie_offset = 0 if serie_cohort == 8
replace serie_offset = 1 if serie_cohort == 10
replace serie_offset = 2 if serie_cohort == 11
replace serie_offset = 3 if serie_cohort == 12
keep if !missing(serie_cohort)

gen int cohort_year = Ano - serie_offset
gen byte tempo_rel = serie_offset*4 + (Trimestre - 1)

* Manter coortes 2015-2020 (panel maduro, exclui anos iniciais com poucos linkados
* e exclui 2021+ para ter 4 anos completos antes de 2024)
keep if cohort_year >= 2015 & cohort_year <= 2020

* { Versao total ----
preserve
collapse (sum) total_matr = peso_v1028 (count) n_obs = idade, ///
    by(cohort_year tempo_rel serie_cohort)

* Normalizar para 100 no primeiro ponto de 8o EF (tempo_rel = 0)
bysort cohort_year (tempo_rel): gen double baseline = total_matr[1] if tempo_rel == 0
bysort cohort_year (tempo_rel): replace baseline = baseline[1]
gen double indice = 100 * total_matr / baseline

* Tambem normalizar por serie (cada serie comeca em 100 no seu primeiro trim)
bysort cohort_year serie_cohort (tempo_rel): gen double base_serie = total_matr[1]
gen double indice_serie = 100 * total_matr / base_serie

gen str serie_lbl = ""
replace serie_lbl = "8o EF"  if serie_cohort == 8
replace serie_lbl = "1o EM"  if serie_cohort == 10
replace serie_lbl = "2o EM"  if serie_cohort == 11
replace serie_lbl = "3o EM"  if serie_cohort == 12

export delimited using "$OUTDIR/F4_cohort_normalized.csv", replace
restore
* } ----

* { Versao em dia ----
preserve
keep if em_dia == 1
collapse (sum) total_matr = peso_v1028 (count) n_obs = idade, ///
    by(cohort_year tempo_rel serie_cohort)

bysort cohort_year (tempo_rel): gen double baseline = total_matr[1] if tempo_rel == 0
bysort cohort_year (tempo_rel): replace baseline = baseline[1]
gen double indice = 100 * total_matr / baseline

bysort cohort_year serie_cohort (tempo_rel): gen double base_serie = total_matr[1]
gen double indice_serie = 100 * total_matr / base_serie

gen str serie_lbl = ""
replace serie_lbl = "8o EF"  if serie_cohort == 8
replace serie_lbl = "1o EM"  if serie_cohort == 10
replace serie_lbl = "2o EM"  if serie_cohort == 11
replace serie_lbl = "3o EM"  if serie_cohort == 12

export delimited using "$OUTDIR/F4_cohort_normalized_emdia.csv", replace
restore
* } ----

di "C7 OK"
