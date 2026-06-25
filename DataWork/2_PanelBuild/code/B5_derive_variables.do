* -------------------------------------------------------------------------
* B5_derive_variables.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Cria variaveis derivadas necessarias para os indicadores de heterogeneidade:
*     - defasagem idade-serie (em-dia / 1 ano def / 2+ anos def)
*     - quintis de renda dom. PC nacionais por ano (Q1-Q5)
*     - faixa "<=1/2 SM" (perfil CadUnico/BFA proxy)
*     - rede agrupada (publica vs. privada)
*     - macroregioes (N, NE, SE, S, CO)
*     - macroetapas (EF iniciais / EF finais / EM)
*
* Inputs:
local TRANS_INTER   "$TMPDIR/transitions_inter_bfa.dta"
local TRANS_INTRA   "$TMPDIR/transitions_intra_bfa.dta"
*
* Outputs:
local PAINEL_FINAL  "$OUTDIR/painel_pnadc_2012_2024.dta"        // entre-anos
local PAINEL_INTRA  "$OUTDIR/painel_pnadc_intra_2012_2024.dta"  // intra-ano (abandono)
local PAINEL_EJA    "$OUTDIR/painel_pnadc_eja_2012_2024.dta"
* -------------------------------------------------------------------------

//{ Helper: aplicar derivacoes em uma transicao
program drop _all
program define _derive
    syntax, transtype(string)
    * transtype = "inter" ou "intra"

    if "`transtype'" == "inter" {
        local SUF "_t"
        local IDADE_VAR "idade_t"
        local SERIE_VAR "serie_t"
        local ETAPA_VAR "etapa_t"
        local RENDA_VAR "renda_pc_t"
        local REDE_VAR  "rede_t"
        local ANO_VAR   "ano_t"
        local PESO_VAR  "peso_v1_t"
    }
    else {
        local SUF "_first"
        local IDADE_VAR "idade_first"
        local SERIE_VAR "serie_first"
        local ETAPA_VAR "etapa_consolid_first"
        local RENDA_VAR "renda_dom_pc_first"
        local REDE_VAR  "rede_first"
        local ANO_VAR   "ano_cal"
        local PESO_VAR  "peso_v1028_first"
    }

    //{ Defasagem idade-serie
    * Idade-padrao por serie/etapa (assumindo entrada aos 6 anos no 1o EF):
    *   1o EF = 6;  2o EF = 7;  ...  9o EF = 14
    *   1o EM = 15; 2o EM = 16; 3o EM = 17
    gen byte idade_padrao = .
    replace idade_padrao = `SERIE_VAR' + 5  if `ETAPA_VAR' == 4 | `ETAPA_VAR' == 5
    replace idade_padrao = 15 if `ETAPA_VAR' == 10
    replace idade_padrao = 16 if `ETAPA_VAR' == 11
    replace idade_padrao = 17 if `ETAPA_VAR' == 12

    gen def_anos = `IDADE_VAR' - idade_padrao
    gen byte defasagem_cat = .
    replace defasagem_cat = 1 if def_anos <= 0
    replace defasagem_cat = 2 if def_anos == 1
    replace defasagem_cat = 3 if def_anos >= 2 & !missing(def_anos)

    label define def_lbl ///
        1 "Em dia" ///
        2 "1 ano defasado" ///
        3 "2+ anos defasado"
    label values defasagem_cat def_lbl
    //}

    //{ Quintis de renda PC nacionais por ano
    * Calcular quintis ponderados pelo peso V1028
    gen quintil_renda = .
    qui levelsof `ANO_VAR', local(anos)
    foreach a of local anos {
        cap _pctile `RENDA_VAR' [aw=`PESO_VAR'] if `ANO_VAR' == `a' & !missing(`RENDA_VAR'), ///
            percentiles(20 40 60 80)
        if !_rc {
            local p20 = r(r1)
            local p40 = r(r2)
            local p60 = r(r3)
            local p80 = r(r4)
            replace quintil_renda = 1 if `ANO_VAR' == `a' & `RENDA_VAR' <= `p20'
            replace quintil_renda = 2 if `ANO_VAR' == `a' & `RENDA_VAR' > `p20' & `RENDA_VAR' <= `p40'
            replace quintil_renda = 3 if `ANO_VAR' == `a' & `RENDA_VAR' > `p40' & `RENDA_VAR' <= `p60'
            replace quintil_renda = 4 if `ANO_VAR' == `a' & `RENDA_VAR' > `p60' & `RENDA_VAR' <= `p80'
            replace quintil_renda = 5 if `ANO_VAR' == `a' & `RENDA_VAR' > `p80' & !missing(`RENDA_VAR')
        }
    }
    label define q_renda ///
        1 "Q1 (mais pobre)" ///
        2 "Q2" ///
        3 "Q3" ///
        4 "Q4" ///
        5 "Q5 (mais rico)"
    label values quintil_renda q_renda
    //}

    //{ Faixa <=1/2 SM (perfil CadU)
    * SM em vigor (valor a partir do 4o trim)
    matrix input SM_anos = (2012, 622 \ 2013, 678 \ 2014, 724 \ 2015, 788 \ ///
                            2016, 880 \ 2017, 937 \ 2018, 954 \ 2019, 998 \ ///
                            2020, 1045 \ 2021, 1100 \ 2022, 1212 \ 2023, 1320 \ ///
                            2024, 1412)

    gen sm_ano = .
    forvalues i = 1/13 {
        local ya = SM_anos[`i', 1]
        local va = SM_anos[`i', 2]
        replace sm_ano = `va' if `ANO_VAR' == `ya'
    }

    gen byte perfil_cadu = (`RENDA_VAR' <= 0.5 * sm_ano) if !missing(`RENDA_VAR', sm_ano)
    label define cadu_lbl 0 "Renda PC > 1/2 SM" 1 "Renda PC <= 1/2 SM (perfil CadU)"
    label values perfil_cadu cadu_lbl
    //}

    //{ Rede agrupada
    gen byte rede_agrupada = .
    replace rede_agrupada = 1 if `REDE_VAR' == 1                  // privada
    replace rede_agrupada = 2 if inlist(`REDE_VAR', 2, 3, 4)      // publica
    label define rede_lbl 1 "Privada" 2 "Publica"
    label values rede_agrupada rede_lbl
    //}

    //{ Macroregioes
    gen byte regiao = .
    replace regiao = 1 if inlist(UF, 11, 12, 13, 14, 15, 16, 17)      // N
    replace regiao = 2 if inlist(UF, 21, 22, 23, 24, 25, 26, 27, 28, 29)  // NE
    replace regiao = 3 if inlist(UF, 31, 32, 33, 35)                     // SE
    replace regiao = 4 if inlist(UF, 41, 42, 43)                         // S
    replace regiao = 5 if inlist(UF, 50, 51, 52, 53)                     // CO
    label define reg_lbl 1 "Norte" 2 "Nordeste" 3 "Sudeste" 4 "Sul" 5 "Centro-Oeste"
    label values regiao reg_lbl
    //}

    //{ Macroetapa
    gen byte macroetapa = .
    replace macroetapa = 1 if `ETAPA_VAR' == 4                    // EF iniciais
    replace macroetapa = 2 if `ETAPA_VAR' == 5                    // EF finais
    replace macroetapa = 3 if inlist(`ETAPA_VAR', 10, 11, 12)    // EM
    replace macroetapa = 4 if `ETAPA_VAR' == 20                  // EJA EF
    replace macroetapa = 5 if `ETAPA_VAR' == 21                  // EJA EM
    label define macroet_lbl ///
        1 "EF iniciais" 2 "EF finais" 3 "EM" 4 "EJA EF" 5 "EJA EM"
    label values macroetapa macroet_lbl
    //}
end
//}

//{ Aplicar para inter-anos
use "`TRANS_INTER'", clear
_derive, transtype("inter")

* Separar EJA do regular
preserve
keep if inlist(etapa_t, 20, 21)
compress
save "`PAINEL_EJA'", replace
di "B5: PAINEL_EJA salvo com `=r(N)' obs"
restore

keep if inlist(etapa_t, 4, 5, 10, 11, 12)
compress
save "`PAINEL_FINAL'", replace
di "B5 OK: PAINEL_FINAL (regular, inter-anos) salvo"
//}

//{ Aplicar para intra-ano
use "`TRANS_INTRA'", clear
_derive, transtype("intra")
compress
save "`PAINEL_INTRA'", replace
di "B5 OK: PAINEL_INTRA (regular, intra-ano) salvo"
//}
