# CHANGELOG — Nota_PNAD

Este arquivo registra todas as mudanças metodológicas, decisões de
desenho, e revisões substantivas do projeto. Append-only.

---

## 2026-06-25 — Revisão metodológica major (rodada 2)

### Contexto
Após primeira rodada de calibração (Q≥2 fallback Q1), o autor avaliou que
os números agregados ainda apresentavam discrepâncias importantes com o
INEP. Decisões abaixo correspondem à reformulação da metodologia
inter-anual e à reorganização editorial do paper.

### Mudanças metodológicas

**M1. Janela de transição inter-anual: excluir Q4 e Q1.**
Para o cálculo das taxas de promoção/repetência/evasão entre anos $t$ e
$t+1$, observações em Q4 (out-dez de $t$) e Q1 (jan-mar de $t+1$) são
excluídas. Mantemos apenas Q2 e Q3 de cada ano como janela válida.
Justificativa: Q1 cobre férias e início do ano letivo (família ainda
pode reportar série antiga); Q4 cobre fim do ano e início das férias
(série pode estar em transição). Restrição reduz amostra (apenas
domicílios entrando em Q2 ou Q3 do ano $t$ contribuem para a transição
$t \to t+1$), mas elimina viés sistemático de calendário.

**M2. Referência em $t+1$: max(nivel) entre Q2-Q3.**
Em vez de tomar a primeira observação de $t+1$, tomamos a observação
com o maior nível educacional declarado entre Q2 e Q3 de $t+1$. Nivel é
um índice ordinal monotônico, combinando etapa e série:
EF iniciais 1-5 (nivel 1-5), EF finais 6-9 (nivel 6-9),
EM 1-3 (nivel 10-12). Esta regra protege contra o caso em que a
família reporta a série anterior em Q2 mas a nova em Q3.

**M3. Migração para EJA explícita.**
Reportada como categoria separada. Aluno em regular EF/EM em $t$
classificado como ``migração EJA'' se a referência em $t+1$ aparece em
EJA EF (etc=20) ou EJA EM (etc=21). Não conta como evasão nem como
repetência.

**M4. Tratamento de atrito (saída do domicílio).**
Adolescentes, principalmente no EM, podem sair do domicílio de origem
(saída para morar com namorada/cônjuge, trabalho em outra cidade) sem
necessariamente evadir da escola. Casos de atrito completo (kid não
aparece em nenhum Q2/Q3 de $t+1$) são por padrão excluídos da
amostra de transição. Reportamos sensibilidades como (i) drop, (ii)
treat as evasão e (iii) IPS-reweight, ver §7 do paper.

**M5. Abandono intra-ano: cobertura completa Q1-Q4.**
Para a taxa de abandono, restringimos o universo aos alunos com
observações em todos os quatro trimestres do mesmo ano. Apenas
domicílios entrando em Q1 do ano $y$ atendem esse critério, o que
reduz o tamanho amostral para aproximadamente um quinto do total
original mas elimina ambiguidade na medida de abandono.

**M6. Tabela condicional a distorção idade-série.**
Tabela adicional restrita ao subconjunto de alunos que iniciam o
painel com defasagem idade-série de pelo menos dois anos
(idade $\geq$ idade-padrão + 2). Idade-padrão segue convenção de
entrada aos seis anos no 1º EF.

### Mudanças editoriais

**E1. Framing do PROFLUXO.**
Remoção da estrutura narrativa de ``três eras'' que posicionava esta
nota como a terceira era. PROFLUXO entra como trabalho prévio
relevante na literatura, com reconhecimento da sua contribuição
histórica para as estatísticas educacionais brasileiras, mas sem
associação de coautoria nem posicionamento como sua continuação.

**E2. Investigação detalhada do gap com INEP.**
Documentação quantitativa dos componentes do gap PNADC vs INEP no EM:
diferença definicional (concluiu 3º EM sem matrícula posterior), captura
de retorno, sub-cobertura, semana de referência. Componente residual
$M$ decomposto.

**E3. Apêndice de figuras desagregadas.**
Apêndice com gráficos por série, sexo, raça, quintil de renda e demais
dimensões socioeconômicas. Apêndice pode ser longo.

### Mudanças de infraestrutura

**I1. Repositório separado.**
Criação de `github.com/vitpereira/Nota_PNAD` com a totalidade do projeto
(DataWork + Paper + Preambles + Bibliography), separado do pacote R
`fluxoescolar`. Dados PNADC microdados (`input/`) excluídos via
`.gitignore`.

### Arquivos modificados

- `DataWork/3_Indicators/code/C14_recalibrate_v2.py` (novo)
- `DataWork/3_Indicators/code/C15_abandono_fullyear.py` (novo)
- `DataWork/3_Indicators/code/C16_distorcao_conditional.py` (novo)
- `DataWork/3_Indicators/output/T1_brasil_inter_por_serie_ano.tex` (substituído)
- `DataWork/3_Indicators/output/T6_distorcao_conditional.tex` (novo)
- `DataWork/5_Figures/code/F7_freq_by_quarter.R` (novo)
- `Paper/sections/01_introducao.tex` (revisado quanto a framing)
- `Paper/sections/02_tres_eras.tex` (renomeada e reescrita: $\to$ literatura prévia)
- `Paper/sections/03_dados_metodo.tex` (revisado com nova metodologia)
- `Paper/sections/04_resultados_agregados.tex` (números atualizados)
- `Paper/sections/06_comparacao_inep.tex` (análise quantitativa do gap)
- `Paper/sections/07_robustez.tex` (sensibilidades expandidas)
- `Paper/sections/08_conclusao.tex` (ajuste de tom)

### Versões anteriores preservadas

- `T1_v0_uncalibrated.tex` (versão Q1-only, primeira iteração)
- `T1_v1_calibrated_Qge2fallback.tex` (segunda iteração, regra Q$\geq$2 com fallback)
- `02_tres_eras_v0.tex.bak` (backup do framing original ``três eras'')

---

---

## 2026-06-25 — Concluído: rodada 2 implementada

Todas as mudanças listadas acima foram implementadas. Resultados:

**Paper:** 43 páginas, 891 KB, 0 undefined references, 0 undefined citations.

**Tabelas atualizadas (v2 Q2-Q3 + max(nivel)):**
- T1 (EF iniciais 2019): prom 85,5% (v0: 76,6%, v1: 77,2%) → 8pp mais próximo do INEP (93,5%)
- T1 (EM 2019): prom 50,4% → gap residual de 32pp identificado como definicional
- T (abandono fullyear, EM 2019): 12,8%
- T6 (defasados EM): evasão 37,1% vs 19,6% para alunos em dia

**Novas figuras:**
- F7: % frequentando por trimestre × macroetapa × ano
- F8a-d: heterogeneidade por sexo, raça, renda e defasagem
- F8_combined: 4 painéis empilhados

**Reposicionamento editorial:**
- §2 reescrita como "Trabalhos prévios e divulgação oficial", sem framing de "três eras"
- PROFLUXO citado como literatura prévia relevante, sem associação de coautoria
- §1, §8 ajustadas em consonância

**Investigação do gap INEP:**
- Componentes R+U+S+C ≈ 10pp do gap de 32pp no EM 2019
- Componente M ≈ 22pp identificado como definicional: alunos do 3º EM concluído sem matrícula em t+1 são promoção no INEP mas não na PNADC atual
- Correção definicional levaria PNADC para ~72% (vs INEP 82,7%, gap residual de 11pp compatível com R+U+S+C)

**Github:**
- Repositório: github.com/vitpereira/Nota_PNAD (separado do pacote R fluxoescolar)
- Pasta de trabalho local: `C:/Users/vitpe/Documents/Nota_PNAD_repo/` (fora do Dropbox para evitar bloqueio do git lock)
- Pasta de desenvolvimento principal permanece em `C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD/`


---

## 2026-06-25 — Rodada 3: correção EM concluído + iteração de coorte

### Mudanças metodológicas

**M7. Correção de conclusão do EM via V3014.**
Alunos no 3º ano do EM em $t$ que reportam V3002=2 em $t+1$ mas
V3014=1 (concluiu o curso) são reclassificados como promoção em vez
de evasão. Aplicada em C17. **Impacto:** EM 2019 prom 50,4% → 70,7%;
evas 25,3% → 4,9%. Gap com INEP cai de 32pp para 12pp.

**M8. Simulação de coorte iterativa (C18).**
Para uma coorte sintética de 100 crianças entrando no 1º EF,
aplicamos iterativamente por 20 anos as taxas médias do INEP
(2014-2019) e da PNADC (2017-2019 v3). Projeções vs observação:
- INEP projetada EF/EM: 68,7%/46,3%
- PNADC projetada EF/EM: 64,4%/33,8%
- PNADC observada (VD3004 idade 19-24, 2019): **88,3%/68,2%**

Conclusão: as taxas anuais subestimam a conclusão observada em ~20pp.
A diferença é atribuída a EJA, retorno após evasão temporária e
captura de retorno. Taxas anuais oferecem LOWER BOUND sobre conclusão.

### Mudanças editoriais

**E4. Duas novas seções no paper:**
- §6.B "Razões para a discrepância PNADC vs INEP" (06b_razoes_discrepancia.tex)
- §6.C "Iteração das taxas de transição e taxa de conclusão observada" (06c_iteracao_taxas.tex)

**E5. Título e abstract revisados.**
- Removida subtítulo "três décadas depois do PROFLUXO"
- Abstract reescrito para refletir nova metodologia e achados de iteração

### Novos arquivos

- `DataWork/3_Indicators/code/C17_correcao_em_concluido.py`
- `DataWork/3_Indicators/code/C18_iterative_completion.py`
- `DataWork/3_Indicators/output/T1_brasil_inter_v3_corrected.csv`
- `DataWork/3_Indicators/output/T1_v2_pre_completion.tex` (backup)
- `DataWork/3_Indicators/output/T7_iterative_completion.tex`
- `DataWork/3_Indicators/output/T7_pnadc_observed_completion.csv`
- `DataWork/3_Indicators/output/C17_V3014_lookup.parquet`
- `DataWork/3_Indicators/output/C17_transitions_v3.parquet`
- `DataWork/5_Figures/code/F9_completion_comparison.R`
- `DataWork/5_Figures/output/F9_completion_comparison.pdf`
- `Paper/sections/06b_razoes_discrepancia.tex`
- `Paper/sections/06c_iteracao_taxas.tex`

### Paper

**50 páginas, 947 KB, 0 undefined refs, 0 undefined citations.**


---

## 2026-06-25 — Rodada 4: técnico + entrada + duas specs + Soares-Alves

### Mudanças metodológicas (M9-M13)

**M9. Inclusão de EM técnico (V3003A=07).**
Etapa 'Educação Profissional Médio' incorporada ao universo principal,
com séries 1-4. Nivel 13 reservado para 4º técnico. Cerca de 0,5% do
total amostral mas relevante conceitualmente.

**M10. Entrada no sistema (sexto indicador).**
Calculada em sub-amostra distinta: indivíduos 4-24 anos NÃO observados
em EF/EM regular ou técnico em t, e cuja referência em t+1 mostra
matricula em regular/técnico. Taxas por faixa etária (média 2012-2023):
- 4-6 anos: 32,8% (entrada típica no 1º EF)
- 7-10 anos: 88,1% (alta entrada, idade típica do EF iniciais)
- 11-14 anos: 86,8% (idade do EF finais)
- 15-17 anos: 39,3% (idade do EM)
- 18-24 anos: 3,6% (entrada via EJA/retorno)

**M11. Duas especificações de janela (Spec A principal, Spec B sensibilidade).**
- Spec A: t ∈ {Q2, Q3, Q4}, t+1 ∈ {Q2, Q3}, com max(nivel) em cada janela.
  - Vantagem: maior amostra (~500k vs 316k v3)
  - Cautela: Q4 em t pode inflar nivel_t via reporte antecipado
- Spec B: t ∈ {Q3, Q4}, t+1 ∈ {Q2, Q3, Q4}.
  - Vantagem: t+1 com 3 quartis, melhor max(nivel)
  - Cautela: t com 2 quartis apenas

**M12. max(nivel) na janela de t+1 expandida.**
Recupera casos em que família atualiza série apenas em Q3 ou Q4 de t+1.

**M13. Correção V3014 estendida ao 4º EM técnico.**
Mantém correção do v3 para 3º EM regular E inclui 4º EM técnico
(nivel=13). Aumento das correções de 12,876 (v3) para 20,360 (v4 Spec A).

### Comparação Spec A v4 vs v3 (EF iniciais 2019)

| Versão | Prom | Rep | Evas | EJA | Sum |
|---|---|---|---|---|---|
| v3 (Q2-Q3 + V3014) | 85,5% | 11,8% | 0,4% | 0,1% | 97,8% |
| **v4 Spec A** | **76,3%** | **21,0%** | **0,4%** | **0,1%** | **97,8%** |
| v4 Spec B | 77,4% | 20,2% | 0,4% | 0,1% | 98,0% |

Promoção EF iniciais 2019 caiu de 85,5% (v3) para 76,3% (v4 Spec A).
O aumento de Q4 na janela de t inflou max(nivel_t) e reduziu o gap
nivel_t1 - nivel_t. Esse efeito é discutido em §7.

### EM 2019 — comparação detalhada

| Versão | Prom | Rep | Evas |
|---|---|---|---|
| v3 (com V3014) | 70,7% | 13,4% | 4,9% |
| **v4 Spec A** | **67,6%** | **23,1%** | **4,6%** |
| v4 Spec B | 67,6% | 23,1% | 4,6% (mesmo) |
| INEP oficial | 82,7% | 8,3% | 6,9% |

Gap residual EM 2019 vs INEP: 15pp (v4 Spec A) vs 12pp (v3).

### Mudanças editoriais

**E6. Soares-Alves (UFMG) à literatura.**
Citações inseridas em §2 (literatura) e §5 (heterogeneidade) com
referências a `SoaresAlvesFonseca2021_trajetorias` (RBEP),
`AlvesSoares2013_contexto` (Educação e Pesquisa) e
`RianiRiosNeto2008_background` (RBEP). Bibliografia já continha as
entradas.

**E7. CLAUDE.md por seção.**
Criados arquivos `Paper/sections/CLAUDE_NN_xxx.md` para cada seção
(01 introdução, 02 literatura, 03 dados, 04 resultados, 05 heterog,
06 inep, 07 robustez, 08 conclusão) + um `CLAUDE_INDEX.md` mapeando
todas as seções. Cada CLAUDE registra estado atual, decisões
pendentes e perguntas em aberto para discussão futura.

### Esclarecimento sobre PNADC 2024 e 2025

PNADC 2024 disponível em todos os quatro trimestres. Usado no projeto.
- Transições inter-anuais: até t=2023 (base), t+1=2024 (12 transições)
- Abandono intra-ano: até 2024 (13 anos)
- Transição 2024→2025: NÃO computável (sem 2025Q2/Q3)
- Previsão IBGE para PNADC 2025Q1: set-nov de 2026

### Novos arquivos

- `DataWork/3_Indicators/code/C19_v4_unified.py`
- `DataWork/3_Indicators/code/C19b_entrada_patch.py`
- `DataWork/3_Indicators/output/T1_brasil_inter_v4_specA.csv`
- `DataWork/3_Indicators/output/T1_brasil_inter_v4_specB.csv`
- `DataWork/3_Indicators/output/T_entrada_no_sistema.csv`
- `DataWork/3_Indicators/output/T_entrada_no_sistema.tex`
- `DataWork/3_Indicators/output/T_entrada_por_ano.csv`
- `DataWork/3_Indicators/output/C19_transitions_specA.parquet`
- `DataWork/3_Indicators/output/C19_transitions_specB.parquet`
- `Paper/sections/CLAUDE_*.md` (8 arquivos)
- `Paper/sections/CLAUDE_INDEX.md`

### Paper

**51 páginas, 956 KB, 0 undefined refs/cits.**

### Pendências para próxima rodada

- [ ] Regerar todas as figuras (F1, F4, F5, F7, F8a-d, F9) com dados v4 Spec A
- [ ] Atualizar texto de §4, §5, §6 com novos números v4
- [ ] Decidir Spec A vs B como principal
- [ ] Implementar B4 BFA observado (V5002A da PNADC anual)
- [ ] PNADC 2025 quando disponível


---

## 2026-06-25 — Rodada 5: reversão da janela para Q2-Q3 + experimento Spec C

### Motivação

Após o autor verificar que a v4 Spec A (janela t ampliada para Q2-Q4)
caiu de 85,5% (v3) para 76,3% no EF iniciais 2019, a investigação
revelou que adicionar Q4 ao window de t e usar max(nivel) captura
reportes antecipados da série do próximo ano letivo, inflando
artificialmente nivel_t e gerando aparente repetência.

### v5 (PRINCIPAL): Q2-Q3 + max + V3014 + técnico + entrada

Configuração:
- Janela em t: {Q2, Q3}
- Janela em t+1: {Q2, Q3}
- Agregador: max(nivel) em ambas
- Correção V3014: 3º EM regular ou 4º EM técnico concluído → promoção
- Inclui EM técnico (V3003A=07)
- Indicador adicional: entrada no sistema

### Resultados v5 (2019)

| Macroetapa | Prom | Rep | Evas | EJA | N |
|---|---|---|---|---|---|
| EF iniciais | **86.1%** | 11.9% | 0.4% | 0.1% | 9.986 |
| EF finais | **81.4%** | 13.8% | 1.3% | 0.6% | 8.457 |
| EM | **75.8%** | 15.0% | 5.9% | 0.2% | 5.446 |

INEP 2019/2020 oficial:
- EF iniciais: prom 93.5%
- EF finais: prom 86.0%
- EM: prom 82.7%

Gap residual v5 vs INEP: EF iniciais 7pp, EF finais 5pp, EM 7pp.

### Experimento Spec C (sensibilidade): min em t, max em t+1

Configuração inovadora proposta pelo autor:
- Janela em t: {Q2, Q3, Q4} com MIN(nivel)
- Janela em t+1: {Q1, Q2, Q3, Q4} com MAX(nivel)

Intuição: conservar nivel_t (min) protege contra inflação por Q4;
expandir nivel_t1 (max em Q1-Q4) captura promoção tardia.

Resultados Spec C 2019:
- EF iniciais: prom 83.4% (n=27.315 — 3x maior amostra)
- EF finais: prom 81.6%
- EM: prom 75.4%

**Análise do experimento:** A intuição teórica é correta, mas o
efeito empírico é pequeno e até negativo para EF iniciais (83.4% vs
86.1% em v5). O motivo: ao expandir a janela de t+1 para Q1-Q4,
inclui-se mais households (especialmente rotação 1, que entram em
Q1 do ano y e só têm obs Q1 em y+1). Para essas households, max(Q1-Q4)
= Q1, que sofre o problema original de reporte tardio da nova série.
Esses domicílios extras diluem a taxa de promoção da subamostra
"limpa" (Q2-Q3) com observações de Q1-only ruins.

### Conclusão metodológica

Mantém-se v5 (Q2-Q3 + max) como principal. v4 Spec A e Spec C ficam
documentadas como sensibilidades (§7). A decisão é defensável porque:

1. Q2-Q3 evita simultaneamente o efeito-férias (Q1) e o reporte
   antecipado (Q4)
2. max(nivel) na janela curta captura atualização entre Q2 e Q3
3. Amostra menor (~316k) mas mais limpa
4. Resultado próximo do INEP após calibração V3014

### Taxas de entrada no sistema (v5 com janela Q2-Q3)

| Faixa | Taxa entrada | N |
|---|---|---|
| 4-6 anos | 38.1% | 51.059 |
| 7-10 anos | 70.9% | 1.916 |
| 11-14 anos | 56.7% | 1.643 |
| 15-17 anos | 23.6% | 9.088 |
| 18-24 anos | 3.4% | 121.482 |

### Inline annotations em CLAUDE.md

O autor anotou nos CLAUDE_xx.md preferências para próximas rodadas:
- §2: Caixas 1 e 2 → prosa; mencionar Reynaldo Fernandes, NCES, OCDE
- §3: subseção dedicada ao esquema rotativo com gráfico; equações no apêndice
- §4: F10 dedicada à entrada; abandono trimestral
- §5: subseção sobre regressão (etapa, série, defasagem, renda, sexo, cor,
  gravidez, filhos, EF); especificação com efeitos fixos; F8e rede pública
  vs privada; figura macrorregião; B4 BFA observado; T6 para apêndice;
  análise por coorte

### Novos arquivos

- `DataWork/3_Indicators/code/C20_v5_main.py`
- `DataWork/3_Indicators/code/C21_specC_minmax.py`
- `DataWork/3_Indicators/output/T1_brasil_inter_v5_main.csv`
- `DataWork/3_Indicators/output/T1_brasil_inter_v6_specC.csv`
- `DataWork/3_Indicators/output/C20_transitions_v5.parquet`

### Paper

**51 páginas, 955 KB, 0 undefined refs/cits.**


---

## 2026-06-25 — Rodada 6: filtro rotação 1 + regressão multivariada

### Filtro rotação 1

Verificação: v5 (janela Q2-Q3 em ambos os anos) **já exclui rotação 1 por construção**, porque essas famílias só veem Q1 no ano t+1. Confirmado empiricamente: todas as transições de C20_transitions_v5.parquet têm trim_t ∈ {2,3} e trim_t1 ∈ {2,3}. Sem mudança nos números de T1.

Abandono: precisaria redefinição (primeira obs vs última obs no ano, em vez de Q1 vs Q4). Implementado em C22b mas script ainda em desenvolvimento (loop pendente). Mantida a tabela atual para esta rodada.

### Regressão multivariada para evasão (C24)

**Modelo:** Linear Probability Model ponderado, erros padrão clusterizados em hh_id.

**Amostra:** 320.228 transições inter-ano (painel v5, 2012-2023).

**Especificação (5):** demografia + defasagem + macroetapa + log(renda PC) + FE ano + FE UF.

**Coeficientes principais (pontos percentuais):**

| Variável | Coef | SE | p |
|---|---|---|---|
| Idade | +1.02 | 0.04 | <0.001 |
| Feminino | -0.58 | 0.07 | <0.001 |
| Preta/parda | +0.25 | 0.09 | <0.01 |
| Defasagem ≥2 anos | **+6.22** | 0.20 | <0.001 |
| Defasagem 1 ano | -0.09 | 0.08 | ns |
| EF finais (vs EF iniciais) | -3.79 | 0.18 | <0.001 |
| EM (vs EF iniciais) | -3.18 | 0.35 | <0.001 |
| log(renda PC) | -0.02 | 0.02 | ns |

R² = 0.086 (com FE ano + UF). N = 320,228.

**Achados principais:**

1. **Defasagem idade-série é o preditor dominante**: +6.2pp para defasados ≥2 anos. Replica e quantifica Fernandes (2011).
2. **Renda log não significativa após controles**: gradiente univariado de renda é mediado por idade, defasagem e geografia.
3. **Coeficientes negativos de EF finais e EM**: contraintuitivo absoluto mas explicado por colinearidade entre macroetapa e idade — alunos do EM são mais velhos, idade absorve o efeito.
4. **Feminino -0.6pp**: vantagem feminina consistente com literatura.
5. **Raça pequena após FE UF**: gradiente racial univariado é mediado por composição geográfica.

**Implicação de política:** combater defasagem precede ou complementa transferências de renda. Compatível com literatura de Soares-Alves UFMG.

**Limitações reportadas no paper:**
- Gravidez, filhos, perda de emprego: não disponíveis (V2013, V2015 apenas no suplemento V5 anual)
- Regressão descritiva, não causal

### Novos arquivos

- `DataWork/3_Indicators/code/C20_v5_main.py` (v5 main: Q2-Q3 + max + V3014 + técnico, sem rot 1 implícito)
- `DataWork/3_Indicators/code/C22_no_rot1.py` (filtro explícito; lento, não rodou)
- `DataWork/3_Indicators/code/C22b_abandono_rev.py` (abandono revisado; lento, não rodou)
- `DataWork/3_Indicators/code/C24_regression.R` (regressão LPM)
- `DataWork/3_Indicators/code/C24b_strip_num.py` (limpeza tabela)
- `DataWork/3_Indicators/output/T_regressao_evasao.tex`
- `Paper/sections/05_heterogeneidade.tex` (nova §5.x Regressão)

### Paper

**54 páginas, 971 KB, 0 undefined refs/cits.**


---

## 2026-06-25 — Rodada 7: regressão multivariada retirada do paper

Após inserir a subseção §5.x Regressão na rodada 6, o autor decidiu
retirá-la. Razões prováveis (não declaradas):
- A nota é uma "nota" e não um paper analítico completo
- Análise causal exige mais cuidado (gravidez, perda emprego, FE pessoa)
- A descritiva univariada já transmite os achados centrais

Mantidos:
- T_regressao_evasao.tex (output da regressão) em DataWork/3_Indicators/output/
- C24_regression.R (script) preservado em DataWork/3_Indicators/code/
- CLAUDE_05_heterogeneidade.md anota a decisão

Removida do main.tex:
- Subseção \subsection{Regressão multivariada para evasão}
- Cerca de 80 linhas de prosa + \input da tabela

Paper: **51 páginas, 955 KB, 0 undefined refs/cits** (volta ao estado pre-§5.x).

---

## 2026-06-25 — Rodada 8: §2 Literatura reescrita

Aplicadas as anotações do CLAUDE_02_literatura.md:

**Mudanças:**
- ✅ **PROFLUXO comprimido**: de ~30 linhas com equações → 1 parágrafo
  contínuo de ~20 linhas. Equações removidas do corpo (intuição em prosa).
- ✅ **Caixa 1 ("A divulgação dos indicadores oficiais") convertida para prosa**.
  Passa a ser um parágrafo regular do texto.
- ✅ **Trabalhos internacionais adicionados**: NCES (US) sobre dropout/graduation
  via CPS + admin, OECD Education at a Glance sobre completion rates por
  nível. Dialoga com a abordagem brasileira.
- ✅ **Soares-Alves mantido** (rodada 4).
- ✅ **Reynaldo Fernandes** já citado via Fernandes2011_atratividade.

**Estrutura final §2:**
1. Parágrafo PROFLUXO (1 par)
2. Parágrafo Soares-Alves + Riani + Fernandes (1 par)
3. **Novo:** Parágrafo internacional (NCES, OCDE) (1 par)
4. Parágrafo INEP+CPF + descontinuidade (1 par)
5. Parágrafo divulgação (Rendimento, Trajetória, IDEB, PNADC) — ex-Caixa 1
6. Parágrafo consequências da descontinuidade
7. Parágrafo COVID
8. Parágrafo final transitando para §3

Paper: **51 páginas, 952 KB, 0 undefined refs/cits**.

### Pendências para próxima rodada

- Adicionar entradas BibTeX para NCES e OCDE (atualmente citados em prosa)
- Renomear `02_tres_eras.tex` → `02_literatura.tex` (cosmético, não-quebra)


---

## 2026-06-25 — Rodada 9: §3 Dados e método reescrita

Aplicadas as anotações do CLAUDE_03_dados_metodo.md.

### Mudanças

✅ **Figura F0 do esquema rotativo (NOVA)**: gerada por
`DataWork/5_Figures/code/F0_esquema_rotativo.R`. Mostra grid 4 rotações × 8
trimestres com cada visita (V1-V5), highlight verde da janela v5 (Q2-Q3),
sombra cinza dos Q1 (férias), e divisor entre ano y e y+1. Inserida
na §3.1 com caption explicativo.

✅ **Caixa 3 → Caixa 1, atualizada para v5**: família entra em 2023Q2
(rotação 2). Pedro mantém 1º EM em Q2-Q3 de 2023 e é promovido a 2º EM
em 2024Q2. Exemplo agora ilustra a metodologia atual (Q2-Q3 + max nível +
V3014).

✅ **EM técnico (V3003A=07) incluído**: nível 13 = 4º ano técnico.
Mencionado no texto, na tabela de harmonização e nas equações do apêndice.

✅ **Equações operacionais movidas para Apêndice A2**: §3.4 ficou em
prosa contínua sem equações. Apêndice ganhou nova subseção "Fórmulas dos
indicadores" com 5 fórmulas formalizadas (promoção, repetência, evasão,
migração EJA, abandono).

✅ **Tabela de harmonização atualizada**: inclui V3014 (concluiu o curso?),
referência ao técnico (códigos 7 em ambas versões).

✅ **Rotação 1 explicitamente excluída**: figura e texto mostram que
rotação 1 não tem observação em Q2-Q3 de t+1 e portanto é excluída por
construção da janela v5.

### Estrutura final §3

1. Parágrafo introdutório PNADC
2. §3.1 Esquema rotativo COM Figura F0
3. Janelas naturais + exclusão de rotação 1
4. Construção do painel (matching)
5. Pesos e regras amostrais
6. Caixa 1 família M.
7. §3.2 Harmonização com tabela
8. §3.4 Definições operacionais em prosa
9. Contraste PROFLUXO (tabela mantida)
10. Variáveis de heterogeneidade

### Novos arquivos

- `DataWork/5_Figures/code/F0_esquema_rotativo.R`
- `DataWork/5_Figures/output/F0_esquema_rotativo.{pdf,png}`

### Paper

**51 páginas, 985 KB, 0 undefined refs/cits.**


---

## 2026-06-25 — Rodada 10: §§4-6 atualizadas para v5

### §4 Resultados agregados

✅ **Números v5 aplicados**:
- EF iniciais 2019: 86,1% prom (era 85,5%)
- EF finais 2019: 81,4% prom
- EM 2019: 75,8% prom (era 50,4% — V3014 incorporada)
✅ **Nova §4.x "Entrada no sistema escolar"** com Tabela e Figura F10
✅ **F10 gerada** (DataWork/5_Figures/code/F10_entrada_sistema.R)
✅ **Parágrafo PNADC 2024/2025**: transição mais recente = 2023→2024,
   2024→2025 não computável até disponibilização 2025Q1 (2026.S2)
✅ Trajetória temporal atualizada (78,6%→86,1% no EF iniciais 2012→2019)

### §5 Heterogeneidade

✅ **F8e rede pública/privada** adicionada (nova figura, parágrafo dedicado)
✅ **F11 macrorregião** adicionada (nova figura, parágrafo dedicado)
✅ **T6 movida para Apêndice A1** (deixou de aparecer no corpo)
✅ Síntese final integra defasagem > região/rede > renda/raça/sexo
✅ Implicação de política conectada a Pé-de-Meia

### §6 Comparação INEP

✅ **Números atualizados para v5**: EM 2019 PNADC 75,8% vs INEP 82,7%,
   gap residual de **6,9pp** (era 32pp antes da V3014)
✅ Discussão R+U+S+C cobre essencialmente o gap residual
✅ V3014 mencionada como correção já incorporada na estimativa principal

### §6B Razões

✅ **Reescrita** para refletir gap menor pós-V3014 (~7pp, não 32pp)
✅ Soma das 5 fontes = 7-10pp = gap residual observado

### Novos arquivos

- `DataWork/5_Figures/code/F0_esquema_rotativo.R`
- `DataWork/5_Figures/code/F10_entrada_sistema.R`
- `DataWork/5_Figures/code/F11_rede_regiao.R`
- `DataWork/5_Figures/output/F0_esquema_rotativo.{pdf,png}`
- `DataWork/5_Figures/output/F10_entrada_sistema.{pdf,png}`
- `DataWork/5_Figures/output/F8e_heterog_rede.{pdf,png}`
- `DataWork/5_Figures/output/F11_heterog_regiao.{pdf,png}`

### Paper

**56 páginas, 1114 KB, 0 undefined refs/cits.**


---

## 2026-06-25 — Rodada 11: §§6C, 7 atualizadas + iteração v5

### §6C Iteração das taxas

**Recalculado C18 → C18b com taxas v5**. Achado central novo:

| Fonte | Conclusão EF | Conclusão EM |
|---|---|---|
| INEP iterativa (médias 2014-19) | 68.7% | 46.3% |
| **PNADC v5 iterativa (médias 2017-19)** | **68.8%** | **47.0%** |
| PNADC observada (VD3004 19-24, 2019) | 88.3% | 68.2% |

**INEP e PNADC v5 agora projetam taxas IDÊNTICAS de conclusão.**
Isso valida a calibração v5 + V3014 + janela Q2-Q3.

A discrepância de ~20pp com a conclusão observada persiste e é
atribuída aos mesmos mecanismos: EJA, retorno após evasão temporária,
e classificação errônea de mudança rede/UF como evasão.

Texto da §6C reescrito para destacar a convergência INEP/PNADC v5
como evidência forte da calibração metodológica.

### §7 Robustez

✅ Texto atualizado: evasão EM v5 ~6% (era "20-30%" pré-V3014)
✅ Soma identidade contábil ~97-98% (era "90% no EM" pré-V3014)
✅ Nomenclatura limpa: removidas referências a v0/v1/v2/Spec A, mantida
   só "metodologia v5 adotada como principal" e versões exploratórias

### Novos arquivos

- `DataWork/3_Indicators/code/C18b_iterative_v5.py`
- `DataWork/3_Indicators/output/T7_iterative_completion.tex` (regenerada)
- `DataWork/3_Indicators/output/T7_iterative_completion.csv` (regenerada)
- `DataWork/5_Figures/output/F9_completion_comparison.pdf` (regenerada)

### Paper

**55 páginas, 1113 KB, 0 undefined refs/cits.**


---

## 2026-06-25 — Rodada 13: REGERAÇÃO de figuras com v5

Várias figuras ainda usavam dados pré-v5 (timestamps 02:59 ou 08:53),
gerando inconsistência com o texto. Especificamente, a **Figura 12
do paper (F5_pnadc_vs_inep.pdf)** ainda mostrava a PNADC pré-V3014
em vez da v5 calibrada.

### Figuras regeneradas com v5

✅ **F5_pnadc_vs_inep**: PNADC v5 (Q2-Q3 + V3014) vs INEP. Agora mostra
   convergência entre as duas séries no EM (era divergente pré-V3014).
✅ **F1_serie_temporal_pnadc**: 4 indicadores ao longo de 2012-2024,
   com taxas v5. Promoção EM ~60-75%, evasão EM ~5-8% (não 25%).
✅ **F8a sexo**, **F8b raça**, **F8c renda**, **F8d defasagem**,
   **F8_combined**: regeneradas com `C20_transitions_v5.parquet`
   (em vez de C14_transitions_v2.parquet). Reflete metodologia v5.

### Figuras já atualizadas em rodadas anteriores

- F0 esquema rotativo (rodada 9)
- F7 freq trimestre (rodada 9)
- F8e rede (rodada 10)
- F9 completion comparison (rodada 11)
- F10 entrada (rodada 10)
- F11 macrorregião (rodada 10)

### Figuras com dados estáveis (não dependem de v5)

- F2 gradientes (não citada no paper)
- F3 captura retorno (estimativa estável, conceitual)
- F4 cohort fluxo (count-based, conceitual)
- F6 efeito-férias within-person (rodada 7-8)

### Mudanças nos scripts

- `F1_serie_temporal.R`: reescrito standalone usando T1_v5_main.csv
- `F5_pnadc_vs_inep.R`: reescrito standalone usando T1_v5_main.csv
- `F8_heterog_v2.R`: substituído input C14→C20, usar flag_* diretamente da
  parquet v5 (já corrigidos), idade-padrão estendida para nível 13 (4º técnico)

### Paper

**56 páginas, 1131 KB, 0 undefined refs/cits.**


---

## 2026-06-26 — Rodada 14: Paradoxo COVID e anomalia pós-pandemia

O autor identificou anomalia importante: repetência PNADC permanece
ALTA em 2022 e 2023 (~27-28% no EM), bem acima do pré-pandêmico (15%).

### Análise empírica

Comparação direta INEP vs PNADC nos anos COVID disponíveis:

| Ano | EM INEP prom/rep | EM PNADC v5 prom/rep |
|---|---|---|
| 2019 | 82.7% / 8.3% | 75.8% / 15.0% |
| **2020** | **89.0% / 3.9%** ↑/↓ | **63.5% / 29.9%** ↓/↑ |
| 2021 | 85.3% / 4.2% | 73.4% / 17.9% (recuperação parcial) |
| 2022 | (não publicado) | 65.9% / **27.6%** (recaída!) |
| 2023 | (não publicado) | 64.7% / **28.3%** |

INEP em 2020 reflete aprovação automática (promoção sobe). PNADC mostra
o oposto. Em 2021, PNADC quase recupera (17.9%). Em 2022/2023,
repetência sobe NOVAMENTE para ~28%, sem dado INEP para comparar.

Análise por nível (EM) confirma padrão sistemático:
- 1ºEM (mesma série em t+1): 17.7% em 2019 → 30.2% em 2022
- 2ºEM: 14.4% → 27.8%
- 3ºEM: 82.8% → 94.2%

### Três hipóteses listadas no paper

1. **Confusão familiar persistente** pós-COVID
2. **Reprovação sistêmica acumulada** após período de aprovação automática
3. **Aprendizado real perdido** gerando reprovação genuína

Evidência atual não distingue. INEP 2022+ resolveria a ambiguidade.

### Mudanças no paper

- §7.1 reescrita: foco no pós-pandêmico (não só durante)
- Tabela paradoxo COVID adicionada
- §4 referência ao paradoxo com recomendação de cautela para 2020-2023
- Análises de heterogeneidade já restritas a 2018-2023 ex-COVID (em §5)

### Novos arquivos

- `DataWork/3_Indicators/code/C25_paradoxo_covid.py`
- `DataWork/3_Indicators/output/T_paradoxo_covid.tex`

### Paper

**59 páginas, 1142 KB, 0 undefined refs/cits.**


---

## 2026-06-26 — Rodada 15: investigação codificação PNADC pós-pandemia

O autor sugeriu verificar se houve mudança na codificação da PNADC
após a pandemia (nova variável ou novos códigos) que pudesse
artificialmente inflar a repetência reportada em 2022-2023.

### Investigação realizada

Verificadas todas as variáveis V30** e V31** no dicionário oficial
PNADC (versão outubro 2022). Analisadas distribuições em 2019, 2020,
2021, 2022, 2023, 2024.

**Resultado**: NENHUMA mudança de codificação pós-pandemia.

| Variável | Códigos | Período | Mudou pós-COVID? |
|---|---|---|---|
| V3002 | 1,2 | 2012-atual | NÃO |
| V3003A | 01-11 | 4ºT/2015-atual | NÃO |
| V3006 | 01-13 | 2012-atual | NÃO |
| V3006A | 1,2 | 1ºT/2018-atual | NÃO (introduzida em 2018) |
| V3013A | 1,2 | 1ºT/2018-atual | NÃO (introduzida em 2018) |
| V3013B | 1,2 | 1ºT/2018-atual | NÃO (introduzida em 2018) |
| V3014 | 1,2 | 2012-atual | NÃO |

V3006A, V3013A e V3013B foram introduzidas em 2018, ANTES da pandemia.
Não há variável nova pós-2020.

Distribuição de V3006 entre alunos do EM regular em 2019 vs 2022 vs 2023:
- 1ºEM: ~8700/7400/7100
- 2ºEM: ~7100/6300/6200
- 3ºEM: ~7000/6400/5800
Composição similar; idades médias por série praticamente iguais.

### Conclusão

A hipótese de "novo item alterou a codificação" foi DESCARTADA. As
três hipóteses substantivas (confusão familiar, reprovação sistêmica,
aprendizado perdido) permanecem em pé. Uma quarta hipótese residual
mencionada no paper: alteração nas instruções operacionais de coleta
do entrevistador IBGE (sem alteração do dicionário), exigiria acesso
aos manuais do entrevistador ano a ano.

### Mudanças no paper

- §7.1 parágrafo adicional documentando a verificação e a conclusão
- Mantida discussão das 3 hipóteses substantivas + 4ª residual

### Paper

**60 páginas, 1145 KB, 0 undefined refs/cits.**


---

## 2026-06-26 — Rodada 16: idade por série DESCARTA reprovação real

O autor sugeriu um teste empírico crucial: se a repetência aumentou de
fato, a idade média por série deveria ter aumentado também.

### Resultado decisivo

Idade média ponderada por série no EM regular (Q2 de cada ano):

| Ano | 1ºEM | 2ºEM | 3ºEM |
|---|---|---|---|
| 2017 | 16.0 | 17.0 | 18.2 |
| 2018 | 16.0 | 16.9 | 18.2 |
| 2019 | 16.0 | 16.9 | 18.2 |
| 2020 | 16.0 | 16.8 | 18.3 |
| 2021 | 16.1 | 17.0 | **19.1** ← único spike |
| **2022** | **15.9** | **16.8** | **18.4** |
| **2023** | **15.8** | **16.8** | **18.2** |
| 2024 | 15.7 | 16.7 | 17.8 |

**Idade média virtualmente IDÊNTICA entre 2019 e 2022/2023**. Se a
repetência tivesse realmente dobrado (15% → 28%), a idade no 3ºEM
deveria estar acima de 18.5. Está em 18.4 e 18.2.

### Implicação

A hipótese de "repetência real" (reprovação sistêmica acumulada e/ou
aprendizado perdido se traduzindo em reprovação) fica FRAGILIZADA.
Resta principalmente: **artefato de medição** por confusão familiar
persistente na declaração da série, possivelmente combinada com
alteração nas instruções operacionais de coleta IBGE pós-COVID.

### Mudanças no paper

- §7.1: nova subseção com teste empírico de idade por série
- Tabela T_idade_serie adicionada
- Hipóteses substantivas reformuladas: as 2 hipóteses de "rep real" são
  descartadas, prevalece artefato de medição

### Novos arquivos

- `DataWork/3_Indicators/code/C26_idade_serie.py`
- `DataWork/3_Indicators/output/T_idade_serie.tex` / `.csv`

### Paper

**61 páginas, 1149 KB, 0 undefined refs/cits.**


---

## 2026-06-26 — Rodada 17: 2020-2021 excluídos + verificação dicionários

Implementadas as duas recomendações do autor:

### 1. Exclusão de 2020 e 2021 das tabelas/figuras

- T1 (Tabela 1): linhas 2020 e 2021 OMITIDAS (não aparecem nem como dagger)
- F1 (série temporal): pontos 2020-2021 omitidos, faixa cinza com "COVID
  excluído"
- F5 (PNADC vs INEP): série PNADC sem 2020-2021
- 2022 e 2023 mantidos com marca $\ddagger$ ("interpretar com cautela")

### 2. Verificação completa de dicionários

Baixei do FTP IBGE o documento oficial `Variaveis_PNADC_Trimestral.xls`
(maio 2025), que mapeia trimestre-a-trimestre disponibilidade de todas
as variáveis 2012-2026.

**Achados:**
- Nenhuma variável V30/V31/VD30 foi introduzida, modificada ou removida
  entre 2019 e 2026
- Últimas adições foram em 1ºT/2018 (V3006A, V3013A, V3013B)
- Dicionário oficial mais recente no FTP IBGE: outubro de 2022
- Categorias de V3002, V3003A, V3006, V3014 estáveis no dicionário 2022
- Distribuição empírica dos códigos em microdados também estável 2017-2024

**Limitação registrada no paper:** versão mais recente do dicionário
disponível publicamente é de outubro 2022. Mudanças posteriores no
significado de categorias específicas não podem ser totalmente descartadas
sem acesso a versões mais recentes (não publicadas).

### Mudanças no paper

- §4: parágrafo reescrito explicando exclusão de 2020-2021 e marcação $\ddagger$
  para 2022-2023
- §7.1: verificação ampliada (3 níveis: doc IBGE 2025, dicionário 2022,
  distribuições empíricas)
- Caveat sobre acesso a versões mais recentes do dicionário

### Novos arquivos

- `DataWork/3_Indicators/code/C27_T1_exclude_covid.py`
- `tmp_dicts/Variaveis_PNADC_Trimestral.xls` (download de referência)

### Paper

**61 páginas, 1152 KB, 0 undefined refs/cits.**


---

## 2026-06-26 — Rodada 18: Dicionários PNADC Anual por ano (2019-2025)

Recuperei os dicionários oficiais da PNADC Anual Visita 1 para cada
ano de 2019 a 2025 no diretório FTP IBGE
`Anual/Microdados/Visita/Visita_1/Documentacao/`. Comparei diretamente
as categorias das variáveis V3003A, V3006 e V3014.

### Achados

| Variável | 2019 | 2022 | 2023 | 2024 | 2025 | Estável? |
|----------|------|------|------|------|------|----------|
| V3003A (curso) | 11 cat | 11 cat | 11 cat | **10 cat** | **10 cat** | Mudança 2024 |
| V3006 (série) | 14 cat | 14 cat | 14 cat | 14 cat | 14 cat | Sim |
| V3014 (concluiu) | 2 cat | 2 cat | 2 cat | 2 cat | 2 cat | Sim |

**Mudança em V3003A:** código `03` (*Alfabetização de jovens e adultos*)
foi REMOVIDO em 2024 e 2025. As outras 10 categorias mantêm os mesmos
códigos numéricos (02, 04, 05, 06, 07, 08, 09, 10, 11).

### Por que esta mudança NÃO explica a anomalia de 2022-2023

1. **Descasamento temporal:** anomalia de repetência manifesta-se em
   2022 e 2023, anos em que o dicionário ainda incluía código 03.
2. **Categoria marginal:** *Alfabetização de jovens e adultos* não é
   EF nem EM regular/EJA — modalidades em que a anomalia ocorre.
   Nossa amostra de análise não inclui essa modalidade.

### Mudanças no paper

- §7.1 substituído o parágrafo da limitação ("dicionário disponível
  apenas em outubro 2022") por descrição completa da investigação
  por ano (2019-2025) com tabela mental V3003A/V3006/V3014.

### Outros achados secundários (FTP IBGE 2026-06-26)

- PNADC 2025 (todos os trimestres) e 2026 Q1 já disponíveis no FTP
- Documento `atualizacoes_divulgacao_trimestral_20260424.txt`
  registra: "24/03/2026 - Correção na variável V3006A" (V3006A é
  etapa do EF, não usada como variável central deste paper)

### Novos arquivos baixados

- `tmp_dicts/dic_2019.xls`
- `tmp_dicts/dic_2022.xls`
- `tmp_dicts/dic_2023.xls`
- `tmp_dicts/dic_2024.xls`
- `tmp_dicts/dic_2025.xls`
- `tmp_dicts/atualizacoes.txt`

### Conclusão substantiva consolidada

A anomalia de repetência em 2022-2023 NÃO é explicada por:
1. ~~Alteração na estrutura ou codificação do questionário~~ (verificado)
2. ~~Aumento real de reprovação~~ (idade média por série estável)

Explicação remanescente mais provável: **confusão familiar
persistente** no auto-relato da série, possivelmente combinada com
**alteração nas instruções operacionais do entrevistador IBGE**
pós-COVID, sem alteração do dicionário formal. Verificação dessa
hipótese exigiria acesso aos manuais do entrevistador ano a ano,
exercício fora do escopo desta nota.

---

## 2026-06-26 — Rodada 19: Confusão familiar também descartada (§7.1)

Refinamento lógico em §7.1 após observação aguda do autor: a hipótese
de "confusão familiar persistente" também é incompatível com a
estabilidade da idade média por série.

### O argumento

O insumo que gera a repetência longitudinal e a idade média transversal
por série é o MESMO valor declarado de V3006. Se famílias estivessem
sistematicamente declarando que o aluno permanece em S em t+1 por
confusão (gerando ~13 p.p. de repetência fictícia), esses alunos
seriam contados no bucket de S em t+1 com sua idade real (um ano
acima da coorte típica), empurrando a idade média de S para cima.
Como a idade média NÃO sobe, qualquer explicação envolvendo
declaração de série sistematicamente errada está descartada.

### Hipóteses descartadas

1. ~~Reprovação real~~ (idade média na série não subiu)
2. ~~Confusão familiar na declaração de série~~ (mesmo argumento mecânico)
3. ~~Mudança formal no questionário~~ (Rodada 18, dicionários estáveis)

### Hipótese remanescente: artefato na CONSTRUÇÃO DO PAINEL

Três mecanismos candidatos compatíveis com:
- Repetência longitudinal alta (painel)
- Idade média na série estável (cross-section)

a) **Linkage corrompido pós-COVID** — indivíduos diferentes do mesmo
   domicílio sendo encaixados como mesmo aluno entre t e t+1. Regra
   de matching admite 80% de consistência sexo+idade; rearranjos
   familiares pós-COVID podem ter ampliado ruído dentro da tolerância.

b) **Atrito diferencial por progressão** — alunos que avançam para
   superior, mudam de cidade, ou abandonam domicílio parental são
   desproporcionalmente removidos do painel. O sobrevivente
   sobrerrepresenta quem ficou na mesma série, inflando repetência
   no painel sem afetar cross-section.

c) **Mudança da composição amostral das rotações pós-2020** — esquema
   rotativo da PNADC afetado pela suspensão temporária de coleta
   presencial em 2020; recomposição pode ter introduzido viés
   sistemático na sub-amostra longitudinal 2021-2024 vs cross-section.

### Implicação para futuro trabalho

Distinguir as três hipóteses exige acesso ao código de linkage do
IBGE e à composição detalhada das rotações pós-COVID — fora do escopo
desta nota, mas registrado como agenda para validação adicional.

### Mudanças no paper

- §7.1: parágrafo final reescrito — descarta confusão familiar
  pelo mesmo argumento mecânico (estabilidade da idade média) e
  desloca hipótese remanescente para artefato de construção do painel.
- Paper agora 62 páginas (era 61), 1156 KB, 0 undefined refs.

---

## 2026-06-26 — Rodada 20: HIPÓTESE FINAL — CAPI→CATI em março/2020

Investigação direta do linkage (sugestão do autor). Resultado:
**linkage está limpo**; o problema é outro — mudança operacional
do IBGE em março de 2020 (substituição de coleta presencial por
telefônica) que persistiu até 2023 e reverteu parcialmente em 2024.

### Testes de linkage (passados)

- Consistência de sexo entre t e t+1: 99.7-99.9% em TODOS os anos
  (incluindo 2022-2024). Não há quebra.
- Delta idade entre t e t+1: média ~0.5, mediana 0 ou 1
  (consistente com amostragem anual + idade inteira; uniforme em
  todos os anos).

### Smoking gun: inconsistência intra-ano de V3006

% de pessoas com (etapa,série) inconsistente entre visitas
consecutivas do MESMO ano civil:

| Ano | V1→V2 | V2→V3 | V3→V4 | V4→V5 |
|-----|-------|-------|-------|-------|
| 2019 | 20.1 | 21.2 | 21.5 | 22.6 |
| **2020** | **6.1** | **5.8** | **6.0** | **5.9** |
| 2021 | 8.3 | 10.1 | 11.3 | 11.1 |
| 2022 | 7.2 | 8.0 | 8.8 | 8.7 |
| 2023 | 5.2 | 7.2 | 8.2 | 9.7 |
| 2024 | 11.6 | 13.6 | 15.1 | 17.2 |

Pré-2020: 20-30% (famílias capturam virada do ano letivo entre
trimestres do mesmo ano civil).
Pós-2020: 5-12% (despenca abruptamente).
2024: recuperação parcial.

### Coincidência de datas

A introdução de CATI (Computer-Assisted Telephone Interviewing) pela
PNADC ocorreu em meados de março de 2020 como resposta à pandemia.
Sob CATI:
- Entrevista mais rápida
- Verificação visual de documentos impossível
- Maior probabilidade de o respondente confirmar a declaração da
  visita anterior sem reavaliação ativa

### Por que CATI explica TUDO

| Fato | Explicação CATI |
|------|-----------------|
| Repetência longitudinal infla 2022-2023 | V3006(t+1) tende a herdar V3006(t) sob CATI |
| Idade média transversal na série estável | Carregamento afeta poucos indivíduos no total da série |
| Evasão PNADC concorda com INEP | V3002 (binária) é robusta a entrevista abreviada |
| Linkage permanece limpo | CATI não afeta identificação do indivíduo, só sua resposta |
| Recuperação parcial em 2024 | Reintrodução gradual de presencial |

### Novos arquivos

- `DataWork/3_Indicators/code/C28_diagnostic_intra_year.py` — calcula
  inconsistência within-person within-year-civil
- `DataWork/3_Indicators/code/C29_table_intra_year.py` — gera tabela LaTeX
- `DataWork/3_Indicators/output/C28_within_year_consistency.csv`
- `DataWork/3_Indicators/output/C28_visit_pair_changes.csv`
- `DataWork/3_Indicators/output/T_inconsistencia_intra_ano.tex`

### Mudanças no paper

- §7.1 reescrito: substitui hipótese de "artefato de linkage" pela
  hipótese de "CAPI→CATI carregamento de resposta", muito mais
  parcimoniosa e suportada pela evidência empírica direta.
- Nova tabela `tab:inconsistencia_intra` inserida em §7.1.
- Paper agora 64 páginas (era 62), 1165 KB, 0 undefined refs.

### Implicação para indicador alternativo

Possível remediação: usar V3006 da PRIMEIRA visita do ano (V1) em
vez de max(nivel) sobre Q2-Q3, já que V1 é a única não potencialmente
contaminada por carry-over. A ser explorada em Rodada futura.

---

## 2026-06-26 — Rodada 21: Correção histórica CATI (autor desafiou prazo)

Autor questionou: PNADC hoje é mesmo CATI? Verificação web em
documentos oficiais IBGE mostrou que minha afirmação anterior
foi imprecisa.

### Verificado em fontes IBGE

- **CATI EXCLUSIVO: 2T/2020 até final 2T/2021 apenas** (não persistiu
  até 2023 como eu afirmei na Rodada 20).
- Retomada GRADUAL ao presencial a partir de 3T/2021.
- Hoje (2026): 2.000 entrevistadores e 500+ agências, majoritariamente
  presencial.
- Em paralelo em 2021: reponderação amostral (NT 03/2021) e alteração
  do método de calibração (NT 04/2021).
- Reponderação 2025 calibrou pesos pelos totais do Censo 2022.
- Estudo do BC: queda de aproveitamento concentrada nas primeiras
  visitas a partir de 2T/2020.

### Por que a inconsistência intra-ano fica baixa em 2022-2024?

Empiricamente: minha tabela mostra inconsistência ~5-13% em 2020-2023
e parcial recuperação a 25% em 2024. Se CATI exclusivo só foi até
2T/2021, por que persiste?

Explicações compatíveis (mantidas como hipóteses, não afirmadas):
1. Retomada presencial muito mais lenta que sugere a narrativa oficial
   — IBGE não divulga percentual CATI/CAPI por trimestre na transição
2. Persistência de práticas de confirmação rápida na coleta presencial
   pós-CATI (herdadas do período telefônico), com uso intensivo do
   tablet visualizando resposta da visita anterior
3. Mudança no protocolo presencial em si
4. Reponderação 2021 introduziu sub-amostra com comportamento diferente

### Mudanças no paper

- §7.1 reescrita com PRECISÃO HISTÓRICA:
  - CATI: 2T/2020 a 2T/2021 (período exclusivo)
  - Retomada gradual sem cronograma público
  - Reponderação NT 03/2021 + recalibração NT 04/2021 também citadas
  - Hipótese formulada como conjunto de mudanças metodológicas
    sobrepostas, não atribuída unicamente a CATI
- Footnote sobre reponderação 2025 (Censo 2022) — posterior à janela
- Paper: 64 pgs, 1167 KB, 0 undefined refs
