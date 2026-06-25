* -------------------------------------------------------------------------
* B1_harmonize_pnadc.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-25
*
* Description:
*   Le os yearly .dta gerados pelo parsing Python, harmoniza variaveis
*   cujos nomes mudaram entre 2012-2024 e gera o arquivo consolidado
*   pnadc_harmonized.dta para uso em B2 (link individuos).
*
*   Variaveis harmonizadas:
*     - V3003 (ate 2015) -> V3003A (a partir de 2016) -> etapa
*     - V3001 -> V3001A -> le_escreve
*     - V3005 -> V3005A -> curso_anterior
*   V3006 (serie) eh constante em todos os anos.
*
*   Filtros aplicados:
*     - Idade 4-24 anos
*     - Peso V1028 nao missing
*
* Inputs:
local PNADC_YEARLY_DIR  "$PRJ_ROOT/DataWork/1_DownloadPNADC/output/yearly"
*
* Outputs:
local PNADC_H     "$TMPDIR/pnadc_harmonized.dta"
* -------------------------------------------------------------------------

clear
tempfile master_b1
gen byte _placeholder = .
drop _placeholder
save `master_b1', emptyok

foreach ano of numlist 2012/2024 {
    cap confirm file "`PNADC_YEARLY_DIR'/pnadc_`ano'.dta"
    if _rc {
        di "AVISO: pnadc_`ano'.dta nao encontrado, pulando"
        continue
    }

    di "Carregando `ano'..."
    use "`PNADC_YEARLY_DIR'/pnadc_`ano'.dta", clear

    //{ Padronizar tipos (todas variaveis vem como string ou double do pyreadstat)
    foreach v in UF V1008 V1014 V1016 V1028 V2001 V2003 V2005 V2007 V2009 V2010 ///
                 V3001 V3001A V3002 V3002A V3003 V3003A V3005 V3005A V3006 V3006A ///
                 V3013 V3013A V3014 VD3004 VD3005 VD4001 VD4002 V403312 VD4019 {
        cap confirm string variable `v'
        if !_rc {
            destring `v', replace force
        }
    }
    //}

    //{ Identificador domiciliar (preserva zeros a esquerda)
    cap confirm string variable UPA
    if _rc {
        gen str9 UPA_s = string(UPA, "%09.0f") if !missing(UPA)
    }
    else {
        gen str9 UPA_s = UPA
    }
    gen str hh_id = string(UF, "%02.0f") + "_" + UPA_s + "_" + ///
                    string(V1008, "%02.0f") + "_" + string(V1014, "%02.0f")
    drop UPA_s
    //}

    //{ Person-quarter ID
    gen str person_q_id = hh_id + "_" + string(V2003, "%02.0f") + "_" + ///
                          string(Ano, "%04.0f") + "Q" + string(Trimestre, "%01.0f")
    //}

    //{ Harmonizar etapa
    gen etapa = .
    cap confirm variable V3003
    if !_rc {
        replace etapa = V3003 if Ano <= 2015
    }
    cap confirm variable V3003A
    if !_rc {
        replace etapa = V3003A if Ano >= 2016
    }
    //}

    //{ Serie (V3006 em todos os anos)
    cap confirm variable V3006
    if !_rc {
        gen serie = V3006
    }
    else {
        gen serie = .
    }
    //}

    //{ Le e escreve
    gen le_escreve = .
    cap confirm variable V3001
    if !_rc {
        replace le_escreve = V3001 if Ano <= 2015
    }
    cap confirm variable V3001A
    if !_rc {
        replace le_escreve = V3001A if Ano >= 2016
    }
    //}

    //{ Variaveis nucleares
    gen byte freq_escola = (V3002 == 1) if !missing(V3002)
    gen byte sexo        = V2007
    gen byte idade       = V2009
    gen byte raca        = V2010
    gen byte rede        = V3002A
    gen peso_v1028       = V1028
    gen byte visita      = V1016
    //}

    //{ Renda dom PC manual (sem VD5008 que so existe em V5)
    cap confirm variable V403312
    if _rc {
        gen renda_dom_pc = .
    }
    else {
        gen renda_trab_ind = V403312
        replace renda_trab_ind = 0 if missing(renda_trab_ind)
        gen str _hh_yr = hh_id + "_" + string(Ano, "%04.0f") + "Q" + string(Trimestre, "%01.0f")
        bysort _hh_yr: egen renda_dom_total = total(renda_trab_ind)
        gen renda_dom_pc = renda_dom_total / V2001
        drop _hh_yr renda_dom_total
    }
    //}

    //{ Codificacao consolidada de etapa (PRE-2016 vs POS-2016)
    * IMPORTANTE: PNADC mudou os codigos de etapa em 2016:
    * PRE-2016 (V3003):  3=Regular Fundamental, 4=Supletivo Fund, 5=Regular Medio, 6=Supletivo Medio
    * POS-2016 (V3003A): 4=Regular Fundamental, 5=Supletivo Fund, 6=Regular Medio, 7=Supletivo Medio
    * (Codigos infantis 1, 2 sao iguais. Classe alfabetizacao = 3 apenas pos-2016.)
    gen byte etapa_consolid = .

    * Educacao infantil
    replace etapa_consolid = 30 if inlist(etapa, 1, 2)
    replace etapa_consolid = 30 if Ano >= 2016 & etapa == 3

    * EF Regular: etapa==3 pre-2016, etapa==4 pos-2016
    replace etapa_consolid = 4  if Ano <= 2015 & etapa == 3 & inrange(serie, 1, 5)
    replace etapa_consolid = 5  if Ano <= 2015 & etapa == 3 & inrange(serie, 6, 9)
    replace etapa_consolid = 4  if Ano >= 2016 & etapa == 4 & inrange(serie, 1, 5)
    replace etapa_consolid = 5  if Ano >= 2016 & etapa == 4 & inrange(serie, 6, 9)

    * EM Regular: etapa==5 pre-2016, etapa==6 pos-2016
    replace etapa_consolid = 10 if Ano <= 2015 & etapa == 5 & serie == 1
    replace etapa_consolid = 11 if Ano <= 2015 & etapa == 5 & serie == 2
    replace etapa_consolid = 12 if Ano <= 2015 & etapa == 5 & serie == 3
    replace etapa_consolid = 10 if Ano >= 2016 & etapa == 6 & serie == 1
    replace etapa_consolid = 11 if Ano >= 2016 & etapa == 6 & serie == 2
    replace etapa_consolid = 12 if Ano >= 2016 & etapa == 6 & serie == 3

    * EJA Fundamental
    replace etapa_consolid = 20 if Ano <= 2015 & etapa == 4
    replace etapa_consolid = 20 if Ano >= 2016 & etapa == 5

    * EJA Medio
    replace etapa_consolid = 21 if Ano <= 2015 & etapa == 6
    replace etapa_consolid = 21 if Ano >= 2016 & etapa == 7
    //}

    //{ Filtros
    keep if inrange(idade, 4, 24)
    drop if missing(peso_v1028)
    //}

    //{ Manter so variaveis core
    keep hh_id person_q_id Ano Trimestre visita UF UPA V1008 V1014 V2003 V2007 V2009 ///
         freq_escola sexo idade raca rede etapa etapa_consolid serie ///
         le_escreve renda_dom_pc peso_v1028
    //}

    di "  obs: `=_N'"
    append using `master_b1', force
    save `master_b1', replace
}

use `master_b1', clear
compress
save "`PNADC_H'", replace
di ""
di "{txt}=== B1 OK: pnadc_harmonized salvo (`=_N' obs) ==="
