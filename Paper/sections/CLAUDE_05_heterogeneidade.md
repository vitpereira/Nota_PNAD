# §5 Heterogeneidade socioeconômica — CLAUDE.md

## Estado atual

Arquivo: `05_heterogeneidade.tex`

Cobre:
- Gradiente por quintil de renda
- Gradiente por raça
- Diferenças por sexo
- Diferenças por série
- Defasagem idade-série (variável mais forte)
- Rede pública vs privada
- Figuras F8a-d (sexo, raça, renda, defasagem)
- Tabela T6 condicional a defasagem ≥ 2 anos

DECISÃO 25/06/2026: a regressão multivariada foi RETIRADA do paper
após a inserção. A T_regressao_evasao.tex permanece em
DataWork/3_Indicators/output/ para uso futuro ou em material
suplementar, mas não é referenciada no main.tex.

## O que deve entrar / atualizar

- [ ] **Atualizar números** com v4 (Spec A)
- [ ] **Recompilar Figuras F8a-d** com novos dados v4
- [ ] **Tabela T6 distorção**: já existe, atualizar com v4
- [ ] **Adicionar figura desagregando entrada no sistema** por idade × renda?

# Regressão
 - Rodar regressão para explicar evasão: Etapa, série, ditorção idade serie, idade, rede da escola, capital vs interior, renda dominicilar per capita, sexo, cor, gravidez, filhos, etc... Incuir controles pouco a pouco, por blocos. 

- Rodar um especificação com efeitos fixos, para verificar o efeito da gravidez e outros eventos que possam ocorrer durante o painel (renda domiciliar percapita, perda de emprego de um dos provedores, etc...)

## Decisões pendentes

1. **Adicionar mais dimensões**: rede pública vs privada já está mencionada
   mas sem figura dedicada. Criar F8e? Sim
2. **Macrorregião**: ainda não tem figura. Criar? Sim
3. **CadÚnico / BFA observado** (V5002A da PNAD anual): apenas mencionado.
   Implementar B4 e adicionar tabela? Sim
4. **Tabelas longas no corpo vs apêndice**: T6 está no corpo, com 5
   colunas. Mantém ou move? Apendice

## Perguntas em aberto

- Existem outras dimensões interessantes? (e.g., status migratório,
  imediatamente posterior a mudança de domicílio) Sim
- Comparar heterogeneidade ENTRE specs A e B? Não
- Análise por coorte (ano de nascimento) faria sentido aqui ou em §4? Sim

## Dependências

- Figuras: F8a, F8b, F8c, F8d, F8_combined
- Tabela T6: `T6_distorcao_conditional.tex`
- Dados: `C19_transitions_specA.parquet`

## Histórico

- v0: placeholders
- v1: writing_rules.md
- v2-v3: números atualizados
- v4 (a fazer): atualizar com Spec A
