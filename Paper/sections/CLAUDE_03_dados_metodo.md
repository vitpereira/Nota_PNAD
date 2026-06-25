# §3 Dados e método — CLAUDE.md

## Estado atual

Arquivo: `03_dados_metodo.tex`

Cobre:
- A PNADC e seu desenho amostral
- §3.1 Esquema rotativo 1-2(5) (subseção)
- Construção do painel longitudinal (linkagem)
- Variáveis educacionais e harmonização entre 2012-2024
- §3.4 Definições operacionais dos 5 indicadores (subseção)
- Caixa 3: exemplo de família ao longo de 5 trimestres
- Contraste com PROFLUXO (tabela)
- Variáveis de heterogeneidade

## O que deve entrar (a definir / atualizar)

- [ ] **Atualizar metodologia para v4**:
  - Janela inter-ano: Spec A = t{Q2,Q3,Q4}, t+1{Q2,Q3, Q4} (principal)
  - Sensibilidade Spec B: t{Q3,Q4}, t+1{Q2,Q3,Q4}
  - Max(nível) em ambas janelas
- [ ] **Incluir EM técnico** (V3003A=07) com séries 1-4 e definir nível
- [ ] **Definir nível ordinal monotônico** (1-13) explicitamente
- [ ] **Adicionar definição de entrada no sistema** como sexto indicador
- [ ] **Correção V3014** para 3º EM regular e 4º EM técnico (já implementada)
- [ ] **Discussão sobre tratamento de atrito** (saída do domicílio)

## Subseções
- O esquema rotativo da PNADC
  - Aqui deve entrar bo grafico mostrando o esquema rotativo da PNADC
- Definições operacionais


## Decisões pendentes

1. **Quantas subseções**: o usuário pediu evitar subseções não-essenciais.
   Atualmente 4 subseções restantes. Reduzir mais?
2. **Caixa 3 (família M.)**: atualizar exemplo para refletir Spec A? Sim
3. **Tabela de harmonização**: já está. Atualizar com EM técnico (V3003A=07)? Sim
4. **Equações operacionais**: tem várias. Mover para apêndice? Sim, escrever todas as equações no apêndice

## Perguntas em aberto

- Como apresentar os DOIS specs de janela (A principal, B sensibilidade)? A B deve ser apresentada posteriormente, na análise de sensibilidade
- A discussão de PROFLUXO em §3.5 ainda faz sentido aqui ou deveria estar
  em §2 (literatura)? O Profluxo não servia muito para alem dos anos iniciais, mas pode ficar aqui
- Apresentar a entrada no sistema aqui ou criar §4.5 separada? Separada

## Dependências

- Subseções referenciadas:
  - `ssec:rotativo` (§3.1) — referenciada em §3 e §7
  - `ssec:definicoes` (§3.4) — referenciada em §4 e §6

## Histórico

- v0: contrast PROFLUXO usando subseções
- v1: writing_rules.md aplicada
- v2: regra de seleção Q≥2 fallback Q1 incorporada
- v3: Q2-Q3 exclusivo + max(nivel)
- v4 (a fazer): Spec A com Q2-Q4 e técnico
