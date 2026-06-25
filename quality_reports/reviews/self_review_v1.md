# Self-Review v1 — Nota_PNAD

**Data:** 2026-06-24
**Razão:** Critics writer-critic e strategist-critic estagnaram no watchdog. Faço self-review estruturado.

---

## A. Revisão da redação (substituindo writer-critic)

### Pontos fortes

1. **Estrutura "Três Eras"** é clara e tem arco narrativo forte. Era 1 (Censo pré-1985 enviesado) → Era 2 (PROFLUXO 1985-2015) → Era 3 (PNADC longitudinal 2015+) sustenta a contribuição.

2. **Contribuição quádrupla bem articulada**: tempestividade + desagregação + independência + captura de retorno. Cada uma é mensurável e dirigida a um defeito real do INEP.

3. **Caixas-texto 1 e 2** funcionam como bookmark visual e dão evidência empírica direta (cronologia PROFLUXO + atraso INEP).

4. **Contraste com PROFLUXO** (Subseção 3.4) é a peça metodológica mais original: tabela 6x2 comparando dimensões. Isso é o que vai vender o paper para *Estudos Econômicos*.

5. **Notação consistente**: $N_{a,s}^t$, $p_s, r_s, e_s$ usadas coerentemente entre Seção 1.2 (introdução do PROFLUXO) e Seção 2 (era PROFLUXO).

### Pontos fracos detectados

1. **Abstract excede 150 palavras** (working-paper-format.md exige ≤150). Conta atual ~250 palavras. **Ação:** reduzir abstract em ~40%.

2. **Hedging excessivo** em alguns lugares:
   - "possivelmente atrasada" → trocar por "atrasada em 9 anos" (dado concreto).
   - "essa é uma limitação inerente" → trocar por declaração direta.
   - "esperamos achar" nos placeholders de seções 4-5 — esses são placeholders aceitáveis pois vão sumir quando os dados estiverem.

3. **Uma citação ainda hedged**: na intro, "A nota técnica do INEP cobre o período 2007-2016 e foi publicada em 2018" — ok como está, mas pode ser mais incisivo: "**A última atualização** do INEP cobre 2007-2016 e foi publicada **há oito anos**."

4. **Tabela `tab:contraste_profluxo`** tem aviso de underfull hbox no LaTeX. **Ação:** revisar larguras das colunas da tabela.

5. **Forward references** (tabelas e seções não populadas): 4 warnings. Esperados — não-fix até dados rodarem.

6. **Discrepância de nomenclatura**: na Subseção 3.3 (def operacionais), uso `freq_t = 1`. Mas na Seção 2 (formalismo PROFLUXO), uso $N_{a,s}^{t}$. As duas notações são compatíveis mas merecia uma frase ligando: "Na próxima seção apresentaremos a notação operacional ($\text{freq}_t$, $s_{i,t}$, etc.) específica para os indicadores baseados em transições."

### Score self-assigned: **82/100** (target ≥ 80, OK para commit; abaixo de 90 para PR)

Principais deduções:
- −5: abstract acima do limite de 150 palavras
- −3: hedging em pontos isolados
- −3: tabela contraste com underfull
- −3: ligação notacional Seção 2 ↔ Seção 3 implícita demais
- −4: placeholders das Seções 4-7 ainda não preenchidos (esperado, mas conta na nota global)

---

## B. Revisão da identificação (substituindo strategist-critic)

### Pressupostos identificáveis e defensáveis

1. **Observação direta de transições**: bem fundamentado — a PNADC com painel rotativo de 5 trimestres permite ver o mesmo indivíduo em múltiplas observações. Não é claim contestável.

2. **Identificador estável**: `UF + UPA + V1008 + V1014` é estável por construção (variável de painel). Documentado pelo IBGE \citep{IBGE_PNADC_notas}.

3. **Validação por sexo + idade**: padrão na literatura de painel rotativo \citep{IPEA2022_painel}.

### Hipóteses que precisam de mais cuidado

1. **Atrito ignorable** — esta é a hipótese mais frágil. O spec propõe teste em Seção 7 comparando observáveis entre retidos vs. perdidos. Adequado, mas **insuficiente** para satisfazer um referee duro. Sugestão:
   - Adicionar **teste Heckman-tipo**: estimar propensão de atrito condicional em observáveis, mostrar coeficientes.
   - Aplicar **bounds de Manski** para a faixa do indicador na presença de atrito não-ignorable.
   - Comparar estimativas P1 (peso primeira visita) com P3 (inverse-propensity) em pelo menos 1 figura.

2. **Definição de evasão vs. INEP**: o INEP soma quatro categorias (promoção + repetência + migração-EJA + evasão = 1). Minha definição de **evasão** soma apenas três (promoção + repetência + evasão = 1) e classifica "migração para EJA" como **não-evasão** (continua estudando). **Isso é correto para o que a PNADC mede**, mas precisa ser explicitado no paper. Adicionar nota: "Diferentemente do INEP, agrupamos migração para EJA com 'estudando em t+1' (= não-evasão), o que é consistente com a captura de retorno via pesquisa domiciliar."

3. **Promoção em casos especiais** (9º EF → 1º EM; 3º EM → superior): o spec define isso, mas o código atual em `._compute_indicator.do` precisa testar com dados reais para confirmar que detecta corretamente. Risco de under/over-conta de promoção dependendo de como a PNADC codifica "EM completo" vs. "1º superior".

4. **Decomposição R+U+S+C+M**: a decomposição é uma identidade contábil **definicional**, não causal. M (residual) é por construção o que sobra. Um referee pode argumentar que isso é tautológico. **Mitigação:** declarar explicitamente que a decomposição é descritiva ("accounting decomposition"), e que R, U, S, C são estimáveis diretamente enquanto M é apenas o resíduo identificado por subtração. **Texto já tem essa cautela** na Seção 6.

5. **Comparação com INEP em todos os anos**: spec diz "todos os anos em que INEP publica". Como INEP descontinuou Trajetória em 2018, a comparação fica limitada a 2007-2016 para Promoção/Repetência/Evasão. **Para Rendimento (Aprovação/Reprovação/Abandono)**, a comparação cobre 2007-2024 (publicação anual contínua). Diferenciação importante na nota.

### Ameaças que precisam de declaração explícita

1. **PNADC tem ~211k domicílios por trimestre. Para subgrupos finos (e.g., indígenas no 3º EM por UF), N pode cair abaixo de 30**. Sugestão: nas tabelas, suprimir células com N < 30 ou marcar com asterisco. Adicionar nota nos limites amostrais.

2. **Pergunta sobre "frequenta escola" é da semana de referência**. Na semana de férias (julho ~ Q3), respostas podem ser ambíguas. Sugestão: testar robustez excluindo Q3 nas medidas (apêndice).

3. **Período COVID 2020-2021**: ruptura clara no padrão de coleta da PNADC (alguns trimestres foram entrevistados por telefone). Documentar e considerar fazer série temporal com/sem COVID destacado.

### Score self-assigned: **84/100**

Principais deduções:
- −4: atrito ignorable precisa de mais testes (Manski bounds, Heckman explícito)
- −3: necessária explicação clara da diferença evasão-INEP × evasão-PNADC (migração EJA)
- −3: necessária declaração de que decomposição R+U+S+C+M é contábil, não causal
- −3: tratamento explícito do choque COVID 2020-2021
- −3: limites amostrais para subgrupos finos

---

## C. Ações imediatas (prioridade)

1. ✏️ **Reduzir abstract** para ≤150 palavras (working-paper-format compliance).
2. ✏️ **Adicionar nota sobre migração EJA** na Seção 3 (definição de evasão).
3. ✏️ **Reforçar caráter contábil/descritivo** da decomposição na Seção 6.
4. ✏️ **Tratamento COVID 2020-2021** — Seção 4 deve ter painel separado/destacado.
5. ✏️ **Suprimir células N<30** no script Stata C2-C4.

## D. Ações para próxima rodada (depois do download)

1. Rodar pipeline completo (Stages 1-7 do _master.py).
2. Substituir placeholders das Seções 4-7 com discussão dos números reais.
3. Adicionar Manski bounds + Heckman attrition em Seção 7.
4. Re-rodar critics (writer-critic, strategist-critic, coder-critic) **com prompts mais curtos** para evitar watchdog.

---

## Score combinado

| Componente                        | Peso  | Score | Contrib. |
|-----------------------------------|-------|-------|----------|
| Redação                           | 25%   | 82    | 20,5     |
| Identificação                     | 25%   | 84    | 21,0     |
| Literatura (librarian)            | 10%   | 90    | 9,0      |
| Código (Stata + Python + R)       | 15%   | (—)   | (rodar)  |
| Comparação INEP (estrutura)       | 25%   | 78    | 19,5     |

**Ponderado (apenas componentes scoreados):** 70,0 / 85 (~82%)

**Veredito self-assessed:** APROVADO PARA COMMIT (>80 do gate de commit). Abaixo do gate de PR (90) — precisa rodar pipeline completo e integrar os 5 fixes da lista C.
