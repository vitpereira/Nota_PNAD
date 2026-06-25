* -------------------------------------------------------------------------
* ._compute_indicator.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Programs reutilizaveis para calcular os 5 indicadores a partir do
*   painel. Servem para os diferentes recortes (por etapa, por ano, por UF,
*   por subgrupo socioeconomico).
*
*   Defincoes operacionais:
*     - PROMOCAO (entre-anos): freq_escola_t1=1 & ((etapa_t1 > etapa_t) OR
*                              (etapa_t1==etapa_t & serie_t1==serie_t+1) OR
*                              (etapa==12 & freq_escola_t1==1 & curso_superior))
*     - REPETENCIA (entre-anos): freq_escola_t1=1 & etapa_t1==etapa_t &
*                                serie_t1==serie_t
*     - EVASAO (entre-anos):    freq_escola_t1==2
*     - NAO-PROGRESSAO = REPETENCIA + EVASAO = 1 - PROMOCAO
*
*     - ABANDONO (intra-ano): freq_escola_first==1 & freq_escola_last==2
* -------------------------------------------------------------------------

* Programa 1: cria flags 0/1 dos indicadores entre-anos
capture program drop _flag_inter
program define _flag_inter
    * Cria as variaveis flag_promocao, flag_repetencia, flag_evasao,
    * flag_naoprog (todas 0/1)

    gen byte flag_promocao = 0
    gen byte flag_repetencia = 0
    gen byte flag_evasao = 0

    * Evasao: simplesmente nao frequenta em t+1
    replace flag_evasao = 1 if freq_escola_t1 != 1 & !missing(freq_escola_t1)

    * Promocao: frequenta + avancou na trajetoria
    * (a) Avanco de serie dentro da mesma etapa
    replace flag_promocao = 1 if freq_escola_t1 == 1 & ///
        etapa_t1 == etapa_t & serie_t1 == serie_t + 1 & !missing(serie_t, serie_t1)
    * (b) Transicao 9o EF (etapa 5, serie 9) -> 1o EM (etapa 10, serie 1)
    replace flag_promocao = 1 if freq_escola_t1 == 1 & ///
        etapa_t == 5 & serie_t == 9 & etapa_t1 == 10
    * (c) Transicao 3o EM (etapa 12) -> superior ou completou
    replace flag_promocao = 1 if freq_escola_t1 == 1 & ///
        etapa_t == 12 & etapa_t1 > 12 & etapa_t1 < 30
    * (d) Avanco entre series do EF iniciais consolidados (etapa 4)
    replace flag_promocao = 1 if freq_escola_t1 == 1 & ///
        etapa_t == 4 & etapa_t1 == 4 & serie_t1 == serie_t + 1
    replace flag_promocao = 1 if freq_escola_t1 == 1 & ///
        etapa_t == 4 & serie_t == 5 & etapa_t1 == 5 & serie_t1 == 6   // 5o -> 6o
    replace flag_promocao = 1 if freq_escola_t1 == 1 & ///
        etapa_t == 5 & etapa_t1 == 5 & serie_t1 == serie_t + 1        // dentro EF finais

    * Repetencia: frequenta mesma serie/etapa
    replace flag_repetencia = 1 if freq_escola_t1 == 1 & ///
        etapa_t == etapa_t1 & serie_t == serie_t1

    * Migracao para EJA: frequenta em t+1 mas mudou para EJA
    gen byte flag_migracao_eja = 0
    replace flag_migracao_eja = 1 if freq_escola_t1 == 1 & ///
        inlist(etapa_t1, 20, 21) & !inlist(etapa_t, 20, 21)

    * "Demais" - frequenta mas nao classificavel (etapa_t1 sup, mudanca grande, etc)
    * Coloca como promocao se etapa_t1 > etapa_t, repetencia se igual
    gen byte _restante = (freq_escola_t1 == 1) & ///
        flag_promocao == 0 & flag_repetencia == 0 & ///
        flag_evasao == 0 & flag_migracao_eja == 0
    * Default conservador: classificar como promocao se subiu etapa, repetencia se igual
    replace flag_promocao = 1 if _restante & etapa_t1 > etapa_t & !missing(etapa_t1)
    replace flag_repetencia = 1 if _restante & etapa_t1 == etapa_t & ///
        serie_t1 != serie_t + 1 & !missing(serie_t1)
    drop _restante

    * Nao-progressao = Repetencia + Evasao + Migracao EJA
    gen byte flag_naoprog = (flag_repetencia + flag_evasao + flag_migracao_eja >= 1)

    * Validacao: identidade contabil
    gen byte _check_total = flag_promocao + flag_repetencia + flag_evasao + flag_migracao_eja
end


* Programa 2: cria flag de abandono intra-ano
capture program drop _flag_intra
program define _flag_intra
    gen byte flag_abandono = 0
    replace flag_abandono = 1 if freq_escola_last != 1 & !missing(freq_escola_last)
end


* Programa 3: calcular medias ponderadas por subgrupo
capture program drop _aggregate
program define _aggregate, rclass
    syntax varname, by(varlist) [if(string)] WEIGHTvar(varname)

    if "`if'" == "" local if "1"

    tempfile temp_out
    preserve
    keep if `if'
    collapse (mean) `varlist' [aw=`weightvar'], by(`by')
    rename `varlist' mean_`varlist'
    save `temp_out', replace
    restore

    return local file = "`temp_out'"
end
