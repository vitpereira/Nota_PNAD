* -------------------------------------------------------------------------
* C5_capture_retorno.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   "Captura de retorno": dos alunos que estavam estudando em t e
*   continuaram estudando em t+1, qual % mudou de rede, mudou de UF, ou
*   mudou de modalidade?
*
*   Essa medida e o LIMITE SUPERIOR do gap entre INEP e PNADC que se deve
*   a "alunos que o Censo perdeu de vista mas que continuam estudando".
*
*   Recortes: por macroetapa, quintil renda, perfil CadU, rede em t.
*
* Inputs:
local PANEL_INTER  "$PANEL_INTER"
*
* Outputs:
*   F3_captura_retorno_por_subgrupo.csv
* -------------------------------------------------------------------------

use "`PANEL_INTER'", clear

* Universo: estudava em t E continua estudando em t+1
keep if freq_escola_t == 1 & freq_escola_t1 == 1
keep if !missing(rede_t, rede_t1)

* Tipos de mudanca
gen byte mudou_rede     = (rede_t != rede_t1)
gen byte mudou_publica_privada = .
replace mudou_publica_privada = 1 if rede_t == 1 & inlist(rede_t1, 2,3,4)  // priv->pub
replace mudou_publica_privada = 2 if inlist(rede_t, 2,3,4) & rede_t1 == 1  // pub->priv
replace mudou_publica_privada = 0 if !missing(rede_t, rede_t1) & missing(mudou_publica_privada)

* Mudanca de modalidade (regular -> EJA ou vice-versa)
gen byte mudou_modalidade = 0
replace mudou_modalidade = 1 if !inlist(etapa_t, 20, 21) & inlist(etapa_t1, 20, 21)  // regular -> EJA
replace mudou_modalidade = 2 if inlist(etapa_t, 20, 21) & !inlist(etapa_t1, 20, 21)  // EJA -> regular

keep if inrange(ano_t, 2018, 2023)

//{ Por macroetapa
preserve
collapse (mean) mudou_rede mudou_modalidade ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa)
export delimited using "$OUTDIR/F3_captura_retorno_por_macroetapa.csv", replace
restore

* Por quintil renda
preserve
keep if !missing(quintil_renda)
collapse (mean) mudou_rede mudou_modalidade ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa quintil_renda)
export delimited using "$OUTDIR/F3_captura_retorno_por_quintil.csv", replace
restore

* Por perfil CadU
preserve
keep if !missing(perfil_cadu)
collapse (mean) mudou_rede mudou_modalidade ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa perfil_cadu)
export delimited using "$OUTDIR/F3_captura_retorno_por_cadu.csv", replace
restore
//}

di "C5 OK"
