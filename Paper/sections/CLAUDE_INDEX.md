# Index dos CLAUDE.md por seção

Cada seção do paper tem um arquivo `CLAUDE_NN_xxx.md` para registrar
decisões pendentes, perguntas em aberto, histórico de revisões e
dependências.

## Mapa das seções

| # | Seção                            | Arquivo TeX              | CLAUDE                     |
|---|-----------------------------------|--------------------------|----------------------------|
| 1 | Introdução                       | `01_introducao.tex`      | `CLAUDE_01_introducao.md`  |
| 2 | Trabalhos prévios                | `02_tres_eras.tex`       | `CLAUDE_02_literatura.md`  |
| 3 | Dados e método                   | `03_dados_metodo.tex`    | `CLAUDE_03_dados_metodo.md`|
| 4 | Resultados agregados             | `04_resultados_agregados.tex` | `CLAUDE_04_resultados.md` |
| 5 | Heterogeneidade                  | `05_heterogeneidade.tex` | `CLAUDE_05_heterogeneidade.md` |
| 6 | Comparação INEP                  | `06_comparacao_inep.tex` | `CLAUDE_06_inep.md`        |
| 6B| Razões da discrepância           | `06b_razoes_discrepancia.tex` | (mesmo `CLAUDE_06_inep.md`) |
| 6C| Iteração de coorte              | `06c_iteracao_taxas.tex` | (mesmo `CLAUDE_06_inep.md`) |
| 7 | Robustez                         | `07_robustez.tex`        | `CLAUDE_07_robustez.md`    |
| 8 | Conclusão                        | `08_conclusao.tex`       | `CLAUDE_08_conclusao.md`   |
| A1| Apêndice UF                      | `A1_apendice_uf.tex`     | (sem CLAUDE específico)    |
| A2| Apêndice variáveis               | `A2_apendice_variaveis.tex` | (sem CLAUDE específico) |

## Como usar

Quando trabalhamos em uma seção específica, leio o CLAUDE da seção, discuto
com você:
1. O que está atualmente na seção
2. O que está pendente
3. As decisões em aberto
4. As perguntas que precisam de resposta

Depois faço as mudanças, atualizo o CLAUDE.md correspondente e o paper.

## Pendências globais (cross-section)

1. **Atualizar todos os números** para v4 Spec A (rodada 4 em curso)
2. **Adicionar Soares-Alves UFMG** à literatura (§2, bibliografia)
3. **Decidir Spec A vs B** como principal (§3, §7)
4. **Esclarecer PNADC 2024/2025**: 2024 disponível, 2025 não. Transições
   até 2023→2024; abandono intra até 2024
5. **Implementar B4 BFA observado**: análise de subamostra com V5002A
   da PNADC anual (Visita 5)
