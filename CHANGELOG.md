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
