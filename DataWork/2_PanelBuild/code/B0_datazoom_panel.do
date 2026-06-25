* -------------------------------------------------------------------------
* B0_datazoom_panel.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-25
*
* Description:
*   Usa o pacote datazoom_social da PUC-Rio para harmonizar e construir o
*   painel longitudinal da PNADC trimestral 2012-2024.
*
*   O datazoom faz tudo que tentamos fazer manualmente em B1-B2:
*     - Le os zips originais do IBGE
*     - Padroniza nomes de variaveis entre versoes (V3003/V3003A etc.)
*     - Constroi identificadores domiciliares e individuais via metodologia
*       Ribas-Soares (2008) com a opcao `idrs`
*     - Salva o resultado em .dta
*
* Instalacao (uma vez):
*   net install datazoom_social, from("https://raw.githubusercontent.com/datazoompuc/datazoom_social_stata/master/") force
*
* Inputs:
*   $RAW_DIR  = $PRJ_ROOT/DataWork/1_DownloadPNADC/tmp/pnad_raw  (52 zips)
*
* Outputs:
*   $TMPDIR/datazoom_<ANO>.dta             (1 por ano, ja harmonizado)
*   $OUTDIR/pnadc_painel_datazoom.dta      (consolidado, todos os anos)
* -------------------------------------------------------------------------

clear all
clear mata
set more off

//{ Paths
if "`c(username)'" == "vitpe" {
    global PRJ_ROOT "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
}

global MOD_ROOT  "$PRJ_ROOT/DataWork/2_PanelBuild"
global RAW_DIR   "$PRJ_ROOT/DataWork/1_DownloadPNADC/tmp/pnad_raw"
global TMPDIR    "$MOD_ROOT/tmp/datazoom"
global OUTDIR    "$MOD_ROOT/output"

cap mkdir "$TMPDIR"
cap mkdir "$OUTDIR"
//}

//{ Install datazoom_social (uma vez)
cap which datazoom_social
if _rc {
    di "Instalando datazoom_social..."
    net install datazoom_social, from("https://raw.githubusercontent.com/datazoompuc/datazoom_social_stata/master/") force
}
//}

//{ Rodar datazoom_pnadcontinua para cada ano com a opcao idrs (Ribas-Soares)
local years 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024

foreach y of local years {
    di "{txt}{hline 60}"
    di "ANO: `y'"
    di "{hline 60}"

    local out_year "$TMPDIR/datazoom_`y'.dta"

    cap confirm file "`out_year'"
    if !_rc {
        di "  Ja processado, pulando."
        continue
    }

    * Datazoom espera: original = pasta com zips do IBGE; saving = pasta destino
    * idrs ativa identificacao Ribas-Soares (versao avancada)
    datazoom_pnadcontinua, years(`y') ///
        original("$RAW_DIR") ///
        saving("$TMPDIR") ///
        idrs

    * O datazoom salva como PNADC_<ANO>.dta; renomeamos para clareza
    cap confirm file "$TMPDIR/PNADC_`y'.dta"
    if !_rc {
        copy "$TMPDIR/PNADC_`y'.dta" "`out_year'", replace
        erase "$TMPDIR/PNADC_`y'.dta"
    }

    di "  OK: `out_year'"
}
//}

//{ Consolidar todos os anos em um painel longo
local first_year = 2012
local last_year  = 2024

local i = 0
foreach y of numlist `first_year'/`last_year' {
    cap confirm file "$TMPDIR/datazoom_`y'.dta"
    if _rc continue

    if `i' == 0 {
        use "$TMPDIR/datazoom_`y'.dta", clear
        local i = 1
    }
    else {
        append using "$TMPDIR/datazoom_`y'.dta", force
    }
    di "  Anexado: `y' (total obs = `=_N')"
}

compress
save "$OUTDIR/pnadc_painel_datazoom.dta", replace
di "OK: pnadc_painel_datazoom.dta salvo em $OUTDIR ({c -(c-)} `=_N' obs)"
//}
