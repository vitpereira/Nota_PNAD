# §3 Dados e método — CLAUDE.md

## Estado atual (rodada 9 — atualizado 25/06/2026)

Arquivo: `03_dados_metodo.tex`

Cobre:
- Parágrafo introdutório PNADC (211k domicílios, 460k pessoas)
- §3.1 Esquema rotativo 1-2(5) COM FIGURA F0 ilustrativa
- Caixa 1 (família M.) atualizada para metodologia v5 (Q2-Q3)
- §3.2 Harmonização de variáveis (incluindo EM técnico V3003A=07)
- Tabela de harmonização atualizada com V3014 e técnico
- §3.4 Definições operacionais (em prosa, sem equações no corpo)
- Equações operacionais movidas para Apêndice A2
- Contraste PROFLUXO mantido (decisão "pode ficar aqui")
- Discussão de variáveis de heterogeneidade

## Mudanças aplicadas (rodada 9)

✅ **Figura F0 esquema rotativo adicionada** — gráfico em ggplot mostrando
   as 4 rotações × 8 trimestres, com janela v5 (verde Q2-Q3) e férias (cinza Q1)
   destacadas
✅ **Caixa 3 → Caixa 1, atualizada** para v5: família entra em 2023Q2
   (rotação 2), Pedro mantém 1º EM em Q2-Q3 de 2023 e é promovido a 2º EM
   em 2024Q2. Exemplo da correção V3014 explicado.
✅ **EM técnico (V3003A=07) incluído** no texto e na tabela de
   harmonização; nível 13 = 4º ano técnico
✅ **Equações operacionais movidas para A2** — apêndice ganhou seção
   "Fórmulas dos indicadores" com fórmulas das 5 taxas (promoção,
   repetência, evasão, migração EJA, abandono)
✅ **Texto de §3.4 em prosa** — descreve indicadores sem equações no corpo
✅ **Rotação 1 mencionada** — figura e texto explicam exclusão por construção
✅ **Contraste PROFLUXO mantido** com tabela

## Estrutura final §3

1. Parágrafo introdutório
2. §3.1 Esquema rotativo COM Figura F0
3. Janelas natural (intra-ano e entre-anos)
4. Construção do painel (matching)
5. Pesos e regras amostrais
6. Caixa 1: família M. ao longo dos trimestres
7. §3.2 Harmonização (Tabela 1)
8. §3.4 Definições operacionais em prosa
9. Contraste PROFLUXO (Tabela 2)
10. Variáveis de heterogeneidade

## Pendente

- [ ] **B4 BFA observado**: implementar análise da Visita 5 anual
  (V5002A) — anotado em §3 que cobre ~20% da amostra
- [ ] Atualizar Apêndice A2 com seção "Fórmulas" (✅ feito)
- [ ] Verificar dependências de subseções: ainda 3 (rotativo, harmonização,
  definições). Manter?

## Histórico

- v0 (24/06): 6 subseções
- v1 (25/06 manhã): writing_rules.md
- v2-v4 (25/06): metodologia atualizada para v5
- v9 (atual): figura F0 do rotativo, EM técnico, equações para apêndice
