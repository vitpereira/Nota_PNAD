* -------------------------------------------------------------------------
* C2_heterogeneity_socio.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Heterogeneidade socioeconomica dos 5 indicadores.
*   Recortes: quintil renda PC, perfil CadU (<=1/2 SM), BFA observado V5,
*             raca/cor, sexo.
*
*   Para a tabela principal do paper, focamos em:
*     - Macroetapa: EF iniciais, EF finais, EM (3 painéis em uma tabela)
*     - Anos: media 2018-2023 (5 anos pre-COVID + 1 ano apos)
*       (OU 2023 sozinho se preferir snapshot recente)
*
* Inputs:
local PANEL_INTER  "$PANEL_INTER"
local PANEL_INTRA  "$PANEL_INTRA"
*
* Outputs:
*   T2_heterog_quintil_renda.csv
*   T2_heterog_perfil_cadu.csv
*   T2_heterog_raca.csv
*   T2_heterog_sexo.csv
*   T2_heterog_combined.csv     -- merge das anteriores
* -------------------------------------------------------------------------

//{ Por quintil de renda
use "`PANEL_INTER'", clear
_flag_inter

* Periodo de referencia: 2018-2023 (6 anos, mais robusto que ponto unico)
keep if inrange(ano_t, 2018, 2023)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa quintil_renda)
gen str grupo = "renda Q" + string(quintil_renda)
export delimited using "$OUTDIR/T2_heterog_quintil_renda.csv", replace
restore

* Intra-ano: abandono por quintil
use "`PANEL_INTRA'", clear
* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename sexo_first sexo

_flag_intra
keep if inrange(ano_cal, 2018, 2023)

preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(macroetapa quintil_renda)
gen str grupo = "renda Q" + string(quintil_renda)
export delimited using "$OUTDIR/T2_heterog_quintil_renda_intra.csv", replace
restore
//}

//{ Por perfil CadU (<=1/2 SM)
use "`PANEL_INTER'", clear
_flag_inter
keep if inrange(ano_t, 2018, 2023)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa perfil_cadu)
gen str grupo = cond(perfil_cadu==1, "Perfil CadU (<=1/2 SM)", "Renda > 1/2 SM")
export delimited using "$OUTDIR/T2_heterog_perfil_cadu.csv", replace
restore

use "`PANEL_INTRA'", clear
* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename sexo_first sexo

_flag_intra
keep if inrange(ano_cal, 2018, 2023)
preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(macroetapa perfil_cadu)
gen str grupo = cond(perfil_cadu==1, "Perfil CadU (<=1/2 SM)", "Renda > 1/2 SM")
export delimited using "$OUTDIR/T2_heterog_perfil_cadu_intra.csv", replace
restore
//}

//{ Por raca/cor
use "`PANEL_INTER'", clear
_flag_inter
keep if inrange(ano_t, 2018, 2023)
keep if inrange(raca, 1, 5)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa raca)
label define raca_l 1 "Branca" 2 "Preta" 3 "Amarela" 4 "Parda" 5 "Indigena"
label values raca raca_l
export delimited using "$OUTDIR/T2_heterog_raca.csv", replace
restore

use "`PANEL_INTRA'", clear
* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename sexo_first sexo

_flag_intra
keep if inrange(ano_cal, 2018, 2023)
keep if inrange(raca, 1, 5)
preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(macroetapa raca)
label define raca_l 1 "Branca" 2 "Preta" 3 "Amarela" 4 "Parda" 5 "Indigena", replace
label values raca raca_l
export delimited using "$OUTDIR/T2_heterog_raca_intra.csv", replace
restore
//}

//{ Por sexo
use "`PANEL_INTER'", clear
_flag_inter
keep if inrange(ano_t, 2018, 2023)
keep if inlist(sexo, 1, 2)

preserve
collapse (mean) flag_promocao flag_repetencia flag_evasao flag_naoprog ///
         (count) n_pessoa=idade_t ///
         [aw=peso_v1_t], by(macroetapa sexo)
label define sexo_l 1 "Homem" 2 "Mulher"
label values sexo sexo_l
export delimited using "$OUTDIR/T2_heterog_sexo.csv", replace
restore

use "`PANEL_INTRA'", clear
* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename sexo_first sexo

_flag_intra
keep if inrange(ano_cal, 2018, 2023)
keep if inlist(sexo, 1, 2)
preserve
collapse (mean) flag_abandono (count) n_pessoa=idade_first ///
         [aw=peso_v1028_first], by(macroetapa sexo)
label define sexo_l 1 "Homem" 2 "Mulher", replace
label values sexo sexo_l
export delimited using "$OUTDIR/T2_heterog_sexo_intra.csv", replace
restore
//}

di "C2 OK"
