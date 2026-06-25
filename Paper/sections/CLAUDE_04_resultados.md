# §4 Resultados agregados — CLAUDE.md

## Estado atual

Arquivo: `04_resultados_agregados.tex`

Cobre:
- Tabela 1 principal (5 indicadores × 3 macroetapas × 12 anos)
- Tabela de abandono full-coverage
- Figura 7: % frequentando por trimestre
- Figura 4: pseudocoortes
- Trajetória temporal 2012-2024 + tratamento COVID
- Nota sobre Pé-de-Meia

## O que deve entrar / atualizar (rodada 4)

- [ ] **Atualizar Tabela 1** com números v4 (Spec A)
  - EF iniciais 2019: prom 76.3%, rep 21.0% (era 85.5% antes)
  - EF finais 2019: prom 73.4% (Spec B) ou 66.5% (Spec A)
  - EM 2019: prom 67.6%, rep 23.1%, evas 4.6%
- [ ] **Adicionar Tabela 1B** com Spec B (apenas no apêndice ou inline?)
- [ ] **Adicionar Tabela de entrada no sistema**
  - 4-6 anos: 32.8% entrada
  - 7-10 anos: 88.1%
  - 18-24 anos: 3.6%
- [ ] **Texto sobre entrada**: discutir o que significa cada faixa etária
- [ ] **Atualizar texto** com as novas %  (atualmente 85.5% pra EF iniciais que era v3)

## Decisões pendentes

1. **Spec A vs B como principal**: Spec A (Q2-Q4 em t) ou Spec B (Q3-Q4)?
   - Spec A: maior amostra, Q4 em t pode inflar nivel_t
   - Spec B: menor amostra (~80% de A), Q4 em t+1 dá max(nivel) com mais info
2. **Onde colocar a tabela de entrada**: aqui ou em §4.x nova?
3. **Tabela de abandono 2024**: incluir? Falta a transição 2024→2025 mas
   abandono intra 2024 está disponível
4. **PNADC 2025**: discutir disponibilidade e plano para próxima rodada

## Perguntas em aberto

- A entrada no sistema é interessante o suficiente para uma figura própria?
  (F10 sugerida)
- Mostrar abandono trimestral (Q1→Q2, Q2→Q3, Q3→Q4) para mostrar perfil?
- Como tratar transição 2023→2024 vs 2024→2025?
  - Transição 2023→2024: COMPUTADA (último t base)
  - Transição 2024→2025: NÃO POSSÍVEL (sem 2025Q2)
  - Abandono 2024: COMPUTADO (intra-ano, todos Q1-Q4 disponíveis)

## Dependências

- Tabela 1 puxa de `T1_brasil_inter_por_serie_ano.tex`
- Tabela abandono puxa de `T_abandono_fullyear.tex`
- Figura 4 puxa de `F4_cohort_fluxo.pdf`
- Figura 7 puxa de `F7_freq_por_trimestre.pdf`

## Histórico

- v0: placeholder
- v1: dados reais inseridos
- v2: regra Q2-Q3 + max
- v3: correção V3014
- v4 (a fazer): Spec A + técnico + entrada
