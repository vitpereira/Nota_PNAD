* -------------------------------------------------------------------------
* B1b_process_per_year.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-25
*
* Description:
*   Versao alternativa de B1 que processa cada ano em arquivo separado para
*   evitar o hang no bysort global. Cada yearly .dta vai virar
*   pnadc_h_<ANO>.dta. Depois, B1c faz append rapido.
*
* Outputs:
*   tmp/yearly_processed/pnadc_h_<ANO>.dta (1 por ano)
* -------------------------------------------------------------------------

global PRJ_ROOT "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
global MOD_ROOT  "$PRJ_ROOT/DataWork/2_PanelBuild"
global YEARLY_DIR "$PRJ_ROOT/DataWork/1_DownloadPNADC/output/yearly"
global TMPDIR    "$MOD_ROOT/tmp/yearly_processed"
cap mkdir "$TMPDIR"

cap log close
log using "$MOD_ROOT/output/B1b_run.log", replace text

local ano_target = `1'  // ano passado como argumento

local out_year "$TMPDIR/pnadc_h_`ano_target'.dta"

cap confirm file "`out_year'"
if !_rc {
    di "Ja processado: `ano_target'"
    exit 0
}

di "Carregando `ano_target'..."
use "$YEARLY_DIR/pnadc_`ano_target'.dta", clear

* Padronizar tipos
foreach v in UF V1008 V1014 V1016 V1028 V2001 V2003 V2005 V2007 V2009 V2010 ///
             V3001 V3001A V3002 V3002A V3003 V3003A V3006 V403312 {
    cap confirm string variable `v'
    if !_rc destring `v', replace force
}

* hh_id
cap confirm string variable UPA
if _rc gen str9 UPA_s = string(UPA, "%09.0f") if !missing(UPA)
else gen str9 UPA_s = UPA
gen str hh_id = string(UF, "%02.0f") + "_" + UPA_s + "_" + ///
                string(V1008, "%02.0f") + "_" + string(V1014, "%02.0f")
drop UPA_s

* etapa harmonizada
gen etapa = .
cap confirm variable V3003
if !_rc replace etapa = V3003 if Ano <= 2015
cap confirm variable V3003A
if !_rc replace etapa = V3003A if Ano >= 2016

gen serie = V3006

gen byte freq_escola = (V3002 == 1) if !missing(V3002)
gen byte sexo  = V2007
gen byte idade = V2009
gen byte raca  = V2010
gen byte rede  = V3002A
gen peso_v1028 = V1028
gen byte visita = V1016

* RENDA: usar uma versao mais leve - precompute hashed hh_yr index
* Em vez de gerar string, usar group(hh_id Ano Trimestre)
cap confirm variable V403312
if !_rc {
    gen renda_trab_ind = V403312
    replace renda_trab_ind = 0 if missing(renda_trab_ind)
    egen long hh_grp = group(hh_id Ano Trimestre)
    bysort hh_grp: egen renda_dom_total = total(renda_trab_ind)
    gen renda_dom_pc = renda_dom_total / V2001
    drop hh_grp renda_dom_total renda_trab_ind
}
else {
    gen renda_dom_pc = .
}

* etapa_consolid com fix pre/pos 2016
gen byte etapa_consolid = .
replace etapa_consolid = 30 if inlist(etapa, 1, 2)
replace etapa_consolid = 30 if Ano >= 2016 & etapa == 3
replace etapa_consolid = 4  if Ano <= 2015 & etapa == 3 & inrange(serie, 1, 5)
replace etapa_consolid = 5  if Ano <= 2015 & etapa == 3 & inrange(serie, 6, 9)
replace etapa_consolid = 4  if Ano >= 2016 & etapa == 4 & inrange(serie, 1, 5)
replace etapa_consolid = 5  if Ano >= 2016 & etapa == 4 & inrange(serie, 6, 9)
replace etapa_consolid = 10 if Ano <= 2015 & etapa == 5 & serie == 1
replace etapa_consolid = 11 if Ano <= 2015 & etapa == 5 & serie == 2
replace etapa_consolid = 12 if Ano <= 2015 & etapa == 5 & serie == 3
replace etapa_consolid = 10 if Ano >= 2016 & etapa == 6 & serie == 1
replace etapa_consolid = 11 if Ano >= 2016 & etapa == 6 & serie == 2
replace etapa_consolid = 12 if Ano >= 2016 & etapa == 6 & serie == 3
replace etapa_consolid = 20 if Ano <= 2015 & etapa == 4
replace etapa_consolid = 20 if Ano >= 2016 & etapa == 5
replace etapa_consolid = 21 if Ano <= 2015 & etapa == 6
replace etapa_consolid = 21 if Ano >= 2016 & etapa == 7

keep if inrange(idade, 4, 24)
drop if missing(peso_v1028)

keep hh_id Ano Trimestre visita UF UPA V1008 V1014 V2003 V2007 V2009 ///
     freq_escola sexo idade raca rede etapa etapa_consolid serie ///
     renda_dom_pc peso_v1028
compress
save "`out_year'", replace
di "OK: `ano_target' salvo com `=_N' obs"

log close
