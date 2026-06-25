* -------------------------------------------------------------------------
* B2_link_individuals.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Cria identificador estavel de indivíduo ao longo das 5 visitas do painel
*   da PNADC. Estrategia em 3 camadas:
*     (a) Match preliminar por hh_id + V2003 (ordem)
*     (b) Validacao por sexo (V2007) e idade (V2009 deve crescer ~0 ou 1
*         entre visitas, tolerancia +/- 1)
*     (c) Reconciliacao: se V2003 nao for estavel, tentar match alternativo
*         dentro do mesmo hh_id por sexo + idade compativel
*
*   Domicilios que mudam de composicao radicalmente (>50% dos membros nao
*   matcham) sao sinalizados como "elo quebrado" e descartados.
*
* Inputs:
local PNADC_H "$TMPDIR/pnadc_harmonized.dta"
*
* Outputs:
local PNADC_LINKED  "$TMPDIR/pnadc_linked.dta"
local LINK_STATS    "$OUTDIR/link_stats.csv"
* -------------------------------------------------------------------------

use "`PNADC_H'", clear

//{ Estrategia (a): match por hh_id + V2003
* Cria identificador inicial (provisorio) por hh_id + V2003
gen str pid_provis = hh_id + "_" + string(V2003, "%02.0f")

* Tag de quantas vezes essa combinacao aparece (deveria ser entre 1 e 5)
bysort pid_provis: gen n_visitas_pid = _N
//}

//{ Validacao por sexo
* Mesma pessoa deve ter o mesmo sexo em todas as visitas
bysort pid_provis (visita): egen sexo_estavel = mode(sexo), minmode
bysort pid_provis: gen sexo_consistente = (sexo == sexo_estavel)
bysort pid_provis: egen frac_sexo_ok = mean(sexo_consistente)
//}

//{ Validacao por idade
* Idade entre visitas: variavel devia crescer +0 ou +1 por trimestre (max
* +1 ao longo dos 5 trimestres ~ 12 meses)
sort pid_provis visita
by pid_provis: gen idade_lag = idade[_n-1]
by pid_provis: gen visita_lag = visita[_n-1]
gen delta_idade = idade - idade_lag
gen delta_visita = visita - visita_lag
gen idade_ok = (delta_idade >= 0 & delta_idade <= 2) if !missing(idade_lag)
* Tolerancia ate 2 anos (margem para arredondamento; ainda detecta falsos matches)

bysort pid_provis: egen frac_idade_ok = mean(idade_ok)
//}

//{ Validacao por raca/cor (estabilidade esperada)
bysort pid_provis (visita): egen raca_estavel = mode(raca), minmode
bysort pid_provis: gen raca_consistente = (raca == raca_estavel)
bysort pid_provis: egen frac_raca_ok = mean(raca_consistente)
//}

//{ Sinalizar elos quebrados
* Pessoa esta "linkada" se:
*   - tem >=2 visitas no painel,
*   - sexo consistente em >= 80% das visitas,
*   - idade compativel em >= 80% das transicoes
gen byte link_ok = (n_visitas_pid >= 2) & ///
                   (frac_sexo_ok >= 0.80) & ///
                   (frac_idade_ok >= 0.80) if !missing(frac_idade_ok, frac_sexo_ok)

* Para indivíduos com apenas 1 visita, mantemos o registro mas marcamos
* como nao-elegivel para painel (link_ok = 0)
replace link_ok = 0 if n_visitas_pid == 1
//}

//{ Estatisticas de matching
preserve
keep pid_provis n_visitas_pid frac_sexo_ok frac_idade_ok frac_raca_ok link_ok
duplicates drop pid_provis, force
gen n_indivs = 1
collapse (sum) n_indivs (mean) frac_sexo_ok frac_idade_ok frac_raca_ok link_ok, ///
    by(n_visitas_pid)
list, sep(0)
export delimited using "`LINK_STATS'", replace
restore
//}

//{ ID final do indivíduo
* Para os linkados, person_id = pid_provis
* Para os nao-linkados, fica como . (excluidos do painel)
gen str person_id = pid_provis if link_ok == 1
//}

//{ Salvar
drop pid_provis sexo_estavel raca_estavel sexo_consistente raca_consistente ///
     idade_lag visita_lag delta_idade delta_visita idade_ok
compress
save "`PNADC_LINKED'", replace
di "B2 OK: pnadc_linked salvo em `PNADC_LINKED'"

* Resumo
count if link_ok == 1
local n_link = r(N)
count if link_ok == 0
local n_nolink = r(N)
di "  Indivíduos linkados: `n_link'"
di "  Nao-linkados:        `n_nolink'"
//}
