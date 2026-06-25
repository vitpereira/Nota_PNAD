* -------------------------------------------------------------------------
* B3_build_transitions.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Para cada indivíduo linkado, monta a base de TRANSICOES que sera a
*   base do calculo dos 5 indicadores.
*
*   Dois tipos de transicao:
*     (i)  INTRA-ANO: primeira observacao de t -> ultima observacao de t
*          (no minimo 2 trimestres no mesmo ano) -- base do ABANDONO
*     (ii) ENTRE-ANOS: primeira obs de t -> primeira obs de t+1
*          (no minimo 1 obs em t e 1 obs em t+1) -- base de EVASAO,
*          PROMOCAO, REPETENCIA, NAO-PROGRESSAO
*
*   Output: arquivo wide com:
*     pessoa_id, ano_t, ano_t1,
*     obs_t (sexo, idade_t, raca, etapa_t, serie_t, freq_t, rede_t, renda_t, ...)
*     obs_t1 (... mesmos campos para t1)
*     peso_v1 (peso da primeira visita)
*
* Inputs:
local PNADC_LINKED   "$TMPDIR/pnadc_linked.dta"
*
* Outputs:
local TRANS_INTRA    "$TMPDIR/transitions_intra.dta"
local TRANS_INTER    "$TMPDIR/transitions_inter.dta"
* -------------------------------------------------------------------------

//{ TRANSICOES INTRA-ANO (para ABANDONO) ----
use "`PNADC_LINKED'", clear
keep if link_ok == 1
keep if !missing(person_id)

* Para cada pessoa-ano, identifica primeira e ultima observacao
gen ano_cal = Ano  // ano calendario (ja eh o ano da PNADC)

* Ordenar por pessoa-ano-trimestre
sort person_id ano_cal Trimestre visita

* Para cada (person_id, ano), pegar primeira e ultima observacao
gen long obs_seq = _n
bysort person_id ano_cal (Trimestre visita): gen first_obs_yr = (_n == 1)
bysort person_id ano_cal (Trimestre visita): gen last_obs_yr  = (_n == _N)

* Contar quantas visitas a pessoa teve no ano
bysort person_id ano_cal: gen n_obs_yr = _N

* Manter apenas pessoas com >=2 observacoes no mesmo ano (para abandono intra-ano)
preserve
keep if n_obs_yr >= 2

* Criar versao wide: linha = (person_id, ano)
* Colunas first_* e last_*
keep if first_obs_yr | last_obs_yr

* Tag para tipo de observacao
gen str tipo = "first" if first_obs_yr
replace tipo = "last" if last_obs_yr
* Caso em que primeira = ultima (so 2 obs): vai gerar 2 linhas. Mas filtramos n_obs_yr>=2

keep person_id hh_id UF ano_cal tipo Trimestre visita idade freq_escola sexo raca etapa_consolid serie rede renda_dom_pc peso_v1028

* Reshape para wide: prefixo first_ e last_
* Para isso, primeiro renomear cada coluna com prefixo tipo_
foreach v of varlist Trimestre visita idade freq_escola sexo raca etapa_consolid serie rede renda_dom_pc peso_v1028 {
    rename `v' `v'_T
}

reshape wide Trimestre_T visita_T idade_T freq_escola_T sexo_T raca_T etapa_consolid_T ///
        serie_T rede_T renda_dom_pc_T peso_v1028_T, ///
        i(person_id ano_cal) j(tipo) string

* Renomear para clareza
rename *_Tfirst *_first
rename *_Tlast  *_last

* Filtros: ambas observacoes existem e a primeira esta estudando
drop if missing(freq_escola_first) | missing(freq_escola_last)
keep if freq_escola_first == 1   // primeiro estava estudando

* Manter so EF/EM regular ou EJA (etapa_consolid valida)
keep if !missing(etapa_consolid_first)

label var ano_cal "Ano calendario da transicao intra-ano"
label var freq_escola_first "Frequentava escola na primeira obs do ano"
label var freq_escola_last  "Frequentava escola na ultima obs do ano"
label var etapa_consolid_first "Etapa consolidada na primeira obs"
label var serie_first "Serie na primeira obs"
label var peso_v1028_first "Peso da primeira observacao do ano"

compress
save "`TRANS_INTRA'", replace
di "B3 OK: transitions_intra salvo em `TRANS_INTRA'"
restore
//}

//{ TRANSICOES ENTRE-ANOS (para EVASAO, PROMOCAO, REPETENCIA) ----
use "`PNADC_LINKED'", clear
keep if link_ok == 1
keep if !missing(person_id)

* Para cada pessoa, escolher 1 obs por ano (a primeira do ano)
sort person_id Ano Trimestre visita
bysort person_id Ano (Trimestre visita): keep if _n == 1

* Agora cada linha eh (person_id, Ano). Vamos criar uma versao lagged.
sort person_id Ano
by person_id: gen ano_next = Ano[_n+1]
by person_id: gen freq_escola_next  = freq_escola[_n+1]
by person_id: gen idade_next        = idade[_n+1]
by person_id: gen etapa_next        = etapa_consolid[_n+1]
by person_id: gen serie_next        = serie[_n+1]
by person_id: gen rede_next         = rede[_n+1]
by person_id: gen renda_pc_next     = renda_dom_pc[_n+1]
by person_id: gen peso_next         = peso_v1028[_n+1]
by person_id: gen trim_next         = Trimestre[_n+1]

* Manter apenas transicoes ano_t -> ano_t+1 (ano_next deve ser exatamente Ano + 1)
keep if !missing(ano_next) & (ano_next == Ano + 1)

* Filtros: primeira observacao deve ser estudando (V3002=1) e em EF/EM/EJA
keep if freq_escola == 1
keep if !missing(etapa_consolid)

* Renomear para clareza (sufixo _t = primeira obs; _t1 = obs no ano seguinte)
rename Ano        ano_t
rename ano_next       ano_t1
rename Trimestre           trim_t
rename trim_next      trim_t1
rename idade          idade_t
rename idade_next     idade_t1
rename freq_escola    freq_escola_t
rename freq_escola_next freq_escola_t1
rename etapa_consolid etapa_t
rename etapa_next     etapa_t1
rename serie          serie_t
rename serie_next     serie_t1
rename rede           rede_t
rename rede_next      rede_t1
rename renda_dom_pc   renda_pc_t
rename renda_pc_next  renda_pc_t1
rename peso_v1028     peso_v1_t
rename peso_next      peso_v1_t1

* Variaveis demograficas (estaveis - ficam do ano t)
keep person_id hh_id UF ano_t ano_t1 trim_t trim_t1 ///
     sexo raca idade_t idade_t1 ///
     freq_escola_t freq_escola_t1 etapa_t etapa_t1 serie_t serie_t1 ///
     rede_t rede_t1 renda_pc_t renda_pc_t1 peso_v1_t peso_v1_t1

label var ano_t  "Ano da observacao base (t)"
label var ano_t1 "Ano da observacao seguinte (t+1)"
label var freq_escola_t  "Frequentava escola em t (=1)"
label var freq_escola_t1 "Frequenta escola em t+1"
label var etapa_t  "Etapa em t"
label var serie_t  "Serie em t"
label var etapa_t1 "Etapa em t+1"
label var serie_t1 "Serie em t+1"
label var rede_t   "Rede da escola em t"
label var rede_t1  "Rede da escola em t+1"
label var peso_v1_t "Peso da primeira observacao em t (V1028)"

compress
save "`TRANS_INTER'", replace
di "B3 OK: transitions_inter salvo em `TRANS_INTER'"

count
di "  Total de transicoes entre-anos: " r(N)
//}
