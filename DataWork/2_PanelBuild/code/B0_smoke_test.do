* -------------------------------------------------------------------------
* B0_smoke_test.do
* -------------------------------------------------------------------------
* Smoke test: roda B1+B2+B3 em 2012 sozinho para validar o pipeline
* antes de processar todos os 13 anos.
* -------------------------------------------------------------------------

clear all
set more off

global PRJ_ROOT "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
global MOD_ROOT  "$PRJ_ROOT/DataWork/2_PanelBuild"
global TMPDIR    "$MOD_ROOT/tmp"
global OUTDIR    "$MOD_ROOT/output"

cap mkdir "$TMPDIR"
cap mkdir "$OUTDIR"

cd "$MOD_ROOT/code"

cap log close
log using "$OUTDIR/smoke_test.log", replace text

//{ 1. Carregar 2012
di "{txt}=== Carregar pnadc_2012.dta ==="
use "$PRJ_ROOT/DataWork/1_DownloadPNADC/output/yearly/pnadc_2012.dta", clear
di "  Obs: `=_N'"
//}

//{ 2. Padronizar tipos
foreach v in UF UPA V1008 V1014 V1016 V2003 V2007 V2009 V2010 V3002 V3002A V3003 V3006 V2001 {
    cap confirm string variable `v'
    if !_rc {
        destring `v', replace force
    }
}

* UPA precisa ser string para concatenacao (mantem zeros a esquerda)
gen str9 UPA_s = string(UPA, "%09.0f") if !missing(UPA)
//}

//{ 3. hh_id e variaveis nucleares
gen str hh_id = string(UF, "%02.0f") + "_" + UPA_s + ///
                "_" + string(V1008, "%02.0f") + "_" + string(V1014, "%02.0f")

gen byte freq_escola = (V3002 == 1) if !missing(V3002)
gen byte sexo        = V2007       // 1=H, 2=M
gen byte idade       = V2009
gen byte raca        = V2010

* Serie (V3006 em todos os anos)
gen serie = V3006

* Etapa (V3003 ate 2015; V3003A a partir de 2016)
gen etapa = V3003

di ""
di "{txt}=== Verificacao das variaveis ==="
sum freq_escola sexo idade raca etapa serie

di ""
di "{txt}=== Filtrar 4-24 anos ==="
qui count
di "  Antes: `=r(N)'"
keep if inrange(idade, 4, 24)
qui count
di "  Depois: `=r(N)'"
//}

//{ 4. Identificador individual provisorio
gen str pid_provis = hh_id + "_" + string(V2003, "%02.0f")

* Quantas observacoes por pid (deveria ser 1-5)
bysort pid_provis: gen n_visitas = _N

tab n_visitas
di "  Total indivíduos distintos: `=r(r)'"  // numero de levels de n_visitas

* Quantos com >= 2 visitas (eleg ivel para painel)
qui count if n_visitas >= 2
di "  Pessoas com >= 2 visitas: `=r(N)'"
//}

//{ 5. Build transitions intra-ano (smoke version)
* Para cada (pid_provis, ano), encontrar primeira e ultima observacao
gen ano_cal = 2012

sort pid_provis ano_cal V1016
bysort pid_provis ano_cal (V1016): gen first_obs = (_n == 1)
bysort pid_provis ano_cal (V1016): gen last_obs  = (_n == _N)
bysort pid_provis ano_cal: gen n_obs_yr = _N

* Universo: estudando na primeira, com >= 2 obs no ano
preserve
keep if n_obs_yr >= 2 & first_obs
keep if freq_escola == 1
keep if inrange(etapa, 1, 8)  // EF/EM/EJA validos
qui count
di "  Universo abandono intra-ano (estudando em t0): `=r(N)'"
restore

di ""
di "{txt}=== Smoke test B1 OK ==="
//}

log close
