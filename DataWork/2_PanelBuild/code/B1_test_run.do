* Test run B1 com poucos anos para validar pipeline
clear all
set more off
global PRJ_ROOT "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
global MOD_ROOT  "$PRJ_ROOT/DataWork/2_PanelBuild"
global TMPDIR    "$MOD_ROOT/tmp"
global OUTDIR    "$MOD_ROOT/output"

cap mkdir "$TMPDIR"
cap mkdir "$OUTDIR"

cap log close
log using "$OUTDIR/b1_test.log", replace text

local PNADC_YEARLY_DIR  "$PRJ_ROOT/DataWork/1_DownloadPNADC/output/yearly"

clear
tempfile master_b1
gen byte _placeholder = .
drop _placeholder
save `master_b1', emptyok

* Apenas 2012-2014 (disponiveis agora)
foreach ano of numlist 2012/2014 {
    cap confirm file "`PNADC_YEARLY_DIR'/pnadc_`ano'.dta"
    if _rc continue

    di "Carregando `ano'..."
    use "`PNADC_YEARLY_DIR'/pnadc_`ano'.dta", clear
    qui count
    di "  Obs raw: `=r(N)'"

    * Padronizar tipos das variaveis numericas
    foreach v in UF V1008 V1014 V1016 V1028 V2001 V2003 V2007 V2009 V2010 ///
                 V3002 V3002A V3003 V3006 V403312 {
        cap confirm string variable `v'
        if !_rc destring `v', replace force
    }

    * UPA string
    cap confirm string variable UPA
    if _rc gen str9 UPA_s = string(UPA, "%09.0f")
    else gen str9 UPA_s = UPA

    gen str hh_id = string(UF, "%02.0f") + "_" + UPA_s + "_" + ///
                    string(V1008, "%02.0f") + "_" + string(V1014, "%02.0f")
    drop UPA_s

    * Variaveis nucleares
    gen byte freq_escola = (V3002 == 1) if !missing(V3002)
    gen byte sexo  = V2007
    gen byte idade = V2009
    gen byte raca  = V2010
    gen byte rede  = V3002A
    gen serie      = V3006
    gen etapa      = V3003
    gen peso_v1028 = V1028
    gen byte visita = V1016

    * Renda dom PC manual
    gen renda_trab_ind = V403312
    replace renda_trab_ind = 0 if missing(renda_trab_ind)
    gen str _hht = hh_id + "_" + string(Ano,"%04.0f") + "Q" + string(Trimestre,"%01.0f")
    bysort _hht: egen renda_dom_total = total(renda_trab_ind)
    gen renda_dom_pc = renda_dom_total / V2001
    drop _hht renda_dom_total renda_trab_ind

    * Filtros
    keep if inrange(idade, 4, 24)
    drop if missing(peso_v1028)

    keep hh_id Ano Trimestre visita UF V2003 V2007 V2009 ///
         freq_escola sexo idade raca rede etapa serie ///
         renda_dom_pc peso_v1028

    qui count
    di "  Apos filtros: `=r(N)'"

    append using `master_b1', force
    save `master_b1', replace
}

use `master_b1', clear
qui count
di "{txt}Total apos concat: `=_N'"

* Counter por ano
tab Ano

compress
save "$TMPDIR/pnadc_harmonized_test.dta", replace
di "{txt}=== B1 TEST OK ==="

log close
