* -------------------------------------------------------------------------
* B4_attach_bfa_v5.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Anexa as variaveis V5002A (recebe BFA?) e V5002A2 (valor BFA) do
*   suplemento PNADC Anual Visita 5 (modulo de Programas Sociais).
*
*   A Visita 5 esta disponivel para os anos 2019-2024 (anteriormente era em
*   outras visitas). O modulo Programas Sociais foi reestruturado em 2019.
*
*   Para cada transicao no painel, busca se o domicilio (hh_id) tem dado de
*   Visita 5 disponivel naquele ano fiscal. Se sim, atribui V5002A.
*   Caso contrario, marca V5002A = . (missing). Mantemos uma linha-flag para
*   sinalizar "BFA observado" vs. "nao observado".
*
* Inputs:
local TRANS_INTER   "$TMPDIR/transitions_inter.dta"
local TRANS_INTRA   "$TMPDIR/transitions_intra.dta"
local V5_DIR        "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Novo_plano/tmp/v3/pnad_raw/parsed"
*
* Outputs:
local TRANS_INTER_BFA  "$TMPDIR/transitions_inter_bfa.dta"
local TRANS_INTRA_BFA  "$TMPDIR/transitions_intra_bfa.dta"
* -------------------------------------------------------------------------

* {{ Verificacao se ha V5 disponivel ----
local v5_anos ""
local v5_anos_disp ""
foreach y of numlist 2019 2020 2021 2022 2023 2024 {
    cap confirm file "`V5_DIR'/pnadc_v5_`y'.parquet"
    if !_rc {
        local v5_anos_disp "`v5_anos_disp' `y'"
    }
}
di "V5 anos disponiveis: `v5_anos_disp'"
* }}

* {{ Carregar V5 (concatenar todos os anos) ----
* Como esta em parquet, convertemos via R/Python ou usamos so 1 ano de cada vez
* Para simplificar agora, deixar V5 como missing - o codigo de attach roda depois
* via subprocess Python quando necessario. Versao final fara o merge.

* PLACEHOLDER: por ora, gera tudo com bfa_observado=0
* (sera atualizado depois que tivermos a versao .dta da V5)

use "`TRANS_INTER'", clear
gen byte bfa_observado_t = 0
gen byte recebe_bfa_t = .
save "`TRANS_INTER_BFA'", replace

use "`TRANS_INTRA'", clear
gen byte bfa_observado_intra = 0
gen byte recebe_bfa_intra = .
save "`TRANS_INTRA_BFA'", replace

di "B4 OK (placeholder - V5 attach feito na proxima rodada com .dta da V5)"
* }}

* TODO (proxima iteracao):
*   1. Converter os parquet pnadc_v5_YYYY.parquet para .dta
*   2. Para cada ano, fazer merge por (UF, UPA, V1008, V1014, V2003)
*   3. Trazer V5002A (=1 sim, 2 nao, .b se nao perguntado)
*   4. Atribuir recebe_bfa = (V5002A == 1)
*   5. bfa_observado_t = 1 se o domicilio teve V5 no mesmo ano fiscal
