# §6 Comparação com INEP + §6B Razões + §6C Iteração — CLAUDE.md

## Estado atual

Três arquivos em sequência:
- `06_comparacao_inep.tex` — comparação direta, decomposição R+U+S+C+M
- `06b_razoes_discrepancia.tex` — cinco fontes da discrepância em prosa
- `06c_iteracao_taxas.tex` — exercício de simulação de coorte iterativa

## O que deve entrar / atualizar (rodada 4)

- [ ] **Atualizar números** com v4 Spec A
  - EM 2019: PNADC 67.6% vs INEP 82.7% (gap 15pp, menor que v3)
  - Gap residual menor após correção V3014
- [ ] **Refazer Tabela 4** (T4_pnadc_vs_inep) com v4
- [ ] **Refazer Figura 5** (F5_pnadc_vs_inep) com v4
- [ ] **Atualizar §6C** com novos números da iteração de coorte
  - INEP projetada EM: 46.3% (mantida)
  - PNADC v4 projetada EM: a recalcular
  - PNADC observada (VD3004 19-24): 68.2% (mantida)

## Decisões pendentes

1. **Manter três seções (§6, §6B, §6C) separadas ou consolidar?**
   - Argumento pró-separar: cada seção tem foco claro
   - Argumento contra: 3 seções pode ser excessivo
2. **Reordenar**: §6 → §6C → §6B faria mais sentido (apresenta achado depois discute)?
3. **Adicionar tabela com decomposição R+U+S+C+M quantitativa**?
4. **Figura F9** (completion comparison): ajustar para v4

## Perguntas em aberto

- A iteração de coorte deveria estar separada como §7 (com numeração própria)?
- Apresentar resultados de Spec A e Spec B com gaps INEP diferentes?
- Quanto enfatizar o gap residual de 15pp como "fechado o suficiente"?

## Dependências

- T4 (PNADC vs INEP): `T4_pnadc_vs_inep_2019.tex`
- T7 (iteração): `T7_iterative_completion.tex`
- F3 (captura retorno): `F3_captura_retorno.pdf`
- F5 (PNADC vs INEP): `F5_pnadc_vs_inep.pdf`
- F9 (completion): `F9_completion_comparison.pdf`

## Histórico

- v0: §6 básica
- v1: writing_rules.md
- v2: prosa contínua
- v3: §6B e §6C adicionadas
- v4 (a fazer): atualizar números
