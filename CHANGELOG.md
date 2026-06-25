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

