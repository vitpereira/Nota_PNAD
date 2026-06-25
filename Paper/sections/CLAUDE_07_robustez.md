# §7 Robustez — CLAUDE.md

## Estado atual

Arquivo: `07_robustez.tex`

Cobre:
- Atrito do painel (link_ok=0)
- §7.1 Efeito-férias e timing de mensuração
- Comparação versões v0, v1, v2 (Q1 vs Q≥2 vs Q2-Q3)
- Tabela T5 efeito-férias within-person
- Outras sensibilidades (janela intra-ano, EJA, idade-padrão)
- Estabilidade pré/pós 2016 (mudança de códigos)

## O que deve entrar / atualizar (rodada 4)

- [ ] **Adicionar comparação Spec A vs Spec B**
  - Spec A: t{Q2,Q3,Q4} t+1{Q2,Q3} → numbers
  - Spec B: t{Q3,Q4} t+1{Q2,Q3,Q4} → numbers
- [ ] **Atualizar tabela T5** com v4 numbers
- [ ] **Adicionar discussão**: por que Spec A vs Spec B podem diferir
  (Q4 em t inflando nivel via reporte antecipado de série seguinte?)
- [ ] **Tratamento de atrito**: discutir explicitamente os adolescentes saindo
  do domicílio no EM
- [ ] **Sensibilidade IPS reweight**: implementar e reportar?

## Decisões pendentes

1. **Spec A ou Spec B como principal?** Debate em aberto
2. **Janela "Q3-Q3"** (apenas Q3 em ambos): testar como sensibilidade?
3. **Sensibilidade para tratamento de atrito**:
   - drop (atual)
   - count as evasão (upper bound)
   - IPS reweight
4. **Quanto detalhe sobre o "efeito-férias"** (mantido de v3)?

## Perguntas em aberto

- Tabela com as 3+ versões (v0, v1, v2, v3, v4 Spec A, v4 Spec B) lado a lado?
- Como apresentar o trade-off de Spec A (mais amostra, possível viés Q4) vs
  Spec B (menor amostra, melhor t+1)?

## Dependências

- T5 efeito-férias: `T5_efeito_ferias_within.tex`
- F6 efeito-férias: `F6_efeito_ferias_within.pdf`

## Histórico

- v1: discussão básica de atrito
- v2: §7.1 efeito-férias introduzida
- v3: tabela T5 e figura F6 com within-person
- v4 (a fazer): comparação Spec A vs B
