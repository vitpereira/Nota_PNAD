# Spec — Nota PNADC: Indicadores de Fluxo Escolar via Painel Longitudinal

**Data:** 2026-06-24
**Status:** APROVADO (brainstorming completo, seções 1-4 confirmadas pelo autor)
**Autor:** Vitor Pereira

---

## 1. Pergunta de pesquisa (MUST)

Como construir indicadores de fluxo escolar — aprovação, reprovação, abandono, evasão, não-progressão — usando o painel longitudinal de cinco trimestres da PNAD Contínua (IBGE, 2012-2024), e em que medida essas estimativas (i) convergem com as do INEP, (ii) viabilizam desagregações socioeconômicas inacessíveis com a publicação oficial agregada, (iii) corrigem vieses do registro administrativo via captura de retorno do aluno?

**CLEAR.**

## 2. Tese central e contribuição (MUST)

A nota **revisita a tradição PROFLUXO-CESGRANRIO** (Fletcher 1985; Fletcher & Ribeiro 1989; Ribeiro 1991; Klein & Ribeiro 1991; Klein 2006) substituindo inferência cross-sectional pela **observação direta** das transições no painel longitudinal da PNADC. Quatro vantagens sobre as estatísticas oficiais do INEP:

1. **Tempestividade** (PNADC trimestral vs. INEP defasado/descontinuado).
2. **Desagregação socioeconômica** (renda PC, raça, BFA, defasagem; INEP só agregado).
3. **Independência da fonte** (pesquisa domiciliar valida registro administrativo).
4. **Captura de retorno** (PNADC segue indivíduo entre redes/UF/modalidades; Censo perde).

**CLEAR.**

## 3. Escopo dos indicadores (MUST)

Cinco indicadores, com definição operacional via painel:

### 3.1. Abandono (intra-ano), série S
- Universo: i com V3002=1 e série S em **primeira observação do ano t** (em EF/EM regular ou EJA, painel separado).
- Numerador: i com V3002=2 (não frequenta) em **última observação do mesmo ano t**.
- Denominador: i com ≥ 2 observações no ano t.
- **Sutileza:** mudança de modalidade dentro do ano (EM regular → EJA) **não** é abandono.

### 3.2. Evasão (entre-anos), série S
- Universo: i com V3002=1 e série S em **primeira observação do ano t**.
- Numerador: i com V3002=2 em observação no ano t+1.
- Denominador: i observado em t e t+1.

### 3.3. Promoção/Aprovação (entre-anos), série S
- Universo: i com V3002=1 e série S em t.
- Numerador: i com V3002=1 e série S+1 (ou etapa seguinte) em t+1.
- Casos especiais: 9º EF → 1º EM = promoção; 3º EM → superior ou "concluiu EM" = promoção.

### 3.4. Repetência/Reprovação (entre-anos), série S
- Universo: idem 3.3.
- Numerador: i com V3002=1 e **mesma série S** em t+1.

### 3.5. Não-progressão (entre-anos)
- Definição contábil: Não-progressão = Repetência + Evasão = 1 − Promoção.

**Identidade contábil verificada:** Promoção + Repetência + Evasão = 1 (entre-anos).
**Abandono é medida adicional** (intra-ano), fora da identidade.

**CLEAR.**

## 4. Dados (MUST)

### 4.1. PNADC Trimestral 2012Q1-2024Q4
- 52 trimestres.
- Variáveis: `Ano`, `Trimestre`, `UF`, `UPA`, `V1008`, `V1014`, `V1016` (visita), `V1032` (peso), `V2003`, `V2005`, `V2007`, `V2009`, `V2010`, `V3001`, `V3002`, `V3002A`, `V3003A`/`V3009A`, `V3006`/`V3014`, `VD3004`, `VD3005`, `VD5002`, `VD5007`, `VD5008`.
- Download: FTP do IBGE.
- Volume: ~3-4 GB compactado.

### 4.2. PNADC Anual Visita 5 (2019-2024) — para BFA
- Variável adicional: `V5002A` (recebe BFA?).
- Já parseada em `C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Novo_plano/code_v3/pnad/` — reutilizar.
- Cobertura: ~20% das transições do painel terão BFA observado.

### 4.3. INEP (Censo Escolar)
- **Indicadores de Rendimento:** aprovação, reprovação, abandono (2007-2024) por etapa × rede × UF.
- **Indicadores de Trajetória/Fluxo:** promoção, repetência, evasão.
- Download via portal INEP (CSV/XLSX).

**CLEAR.**

## 5. Construção do painel longitudinal (MUST)

### 5.1. Identificador domiciliar
`hh_id = UF + UPA + V1008 + V1014` (estável por construção; 5 visitas em trimestres consecutivos).

### 5.2. Identificador individual
- Match preliminar: `hh_id + V2003`.
- Validação: `V2007` (sexo) idêntico; `V2009` (idade) cresce ~0 ou +1 por visita (tolerância ±1).
- Reconciliação: match alternativo por sexo+idade compatível; se mismatch persiste, marcar como "elo quebrado" e descartar.

### 5.3. Janela do indicador
- **Intra-ano:** primeira × última observação no ano t (≥ 2 trimestres de distância).
- **Entre-anos:** primeira observação no ano t × última observação no ano t+1 (≥ 12 meses).

### 5.4. Filtros amostrais
- Idade 4-24 anos.
- Status na primeira observação = estudando (`V3002=1`).
- EF, EM (regular) — painel principal. EJA — painel separado.
- Sem missing em variáveis-chave (série, etapa).
- Pelo menos as duas observações requeridas pelo indicador.

### 5.5. Reponderação
- **P1 (recomendada para tabela principal):** peso da primeira visita (`V1032` no trimestre da primeira observação).
- **P3 (apêndice de robustez):** inverse propensity para correção de atrito.

**CLEAR.**

## 6. Variáveis de heterogeneidade (MUST)

| Dimensão | Categorias | Tabela |
|---|---|---|
| Etapa-série | 1º EF a 3º EM (12 categorias) + EJA | Principal |
| Idade × série | Em dia / 1 ano defasado / 2+ anos defasado | Principal |
| Sexo | M / F | Principal |
| Raça/cor | Branca / Parda / Preta / Amarela / Indígena | Principal |
| Quintil de renda dom. PC nacional | Q1-Q5 + linha "≤ ½ SM" | Principal |
| **BFA observado (subamostra V5)** | Sim / Não em renda comparável | Robustez |
| Rede | Pública / Privada | Principal |
| Modalidade | Regular / EJA | Painéis separados |
| UF (27) | — | Apêndice + mapa |

**CadÚnico:** PNADC não tem variável direta. Usar **perfil de renda** (renda dom. PC ≤ ½ SM OU recebe BFA) como proxy declarado em nota de rodapé.

**CLEAR.**

## 7. Comparação com INEP e decomposição (MUST)

Para cada indicador-coorte-grupo, computar:

$$\Delta_{ind} = \underbrace{R}_{retorno} + \underbrace{U}_{universo} + \underbrace{S}_{amostra} + \underbrace{C}_{sub\text{-}cobertura} + \underbrace{M}_{medida\ residual}$$

- **R (retorno):** % de alunos PNADC com V3002=1 em t+1 que mudaram de rede/modalidade entre t e t+1. **Diretamente estimável.**
- **U (universo):** diferença entre denominadores (PNADC pop. estudando × Censo matrículas).
- **S (sampling):** IC 95% pelo bootstrap com cluster em UPA.
- **C (sub-cobertura do Censo):** estimar via comparação de denominadores.
- **M (residual):** Δ − (R + U + S + C). Reportar explicitamente, não esconder.

**Comparação cobre todos os anos em que INEP publicou cada indicador** (não restringir à era CPF do INEP).

**CLEAR.**

## 8. Estrutura do paper (SHOULD)

Working paper, ~36-44 páginas. Veículo provisório: UFRJ-IE WP → submissão a *Estudos Econômicos* (USP) ou *Pesquisa e Planejamento Econômico* (IPEA).

| # | Seção | Páginas |
|---|---|---|
| 1 | Introdução | 2,5 |
| 2 | A medição do fluxo escolar no Brasil: três eras | 5-6 |
| 3 | Dados e método | 5-6 |
| 4 | Resultados agregados | 4 |
| 5 | Heterogeneidade socioeconômica | 6 |
| 6 | Comparação INEP × PNADC: validação e decomposição | 4-5 |
| 7 | Robustez | 2-3 |
| 8 | Conclusões e agenda | 2 |
| A | Apêndice A — Tabelas por UF | 3-5 |
| B | Apêndice B — Construção das variáveis | 1-2 |
| — | Referências | 2-3 |

### Outputs canônicos

- **Tabela 1:** 5 indicadores × etapa-série × ano (Brasil).
- **Tabela 2:** 5 indicadores × (quintil renda, BFA, raça, sexo) — 2023.
- **Tabela 3:** 5 indicadores × (defasagem, rede, macroregião).
- **Tabela 4:** INEP × PNADC + decomposição R/U/S/C/M.
- **Figura 1:** séries 2012-24, 4 painéis (aprov/repro/aband/evasão).
- **Figura 2:** gradientes por renda e raça.
- **Figura 3:** captura de retorno por subgrupo.
- **Figura 4** (robustez): retidos × perdidos no painel.
- **Caixa-texto 1:** cronologia PROFLUXO.
- **Caixa-texto 2:** atraso INEP.
- **Caixa-texto 3:** exemplo de família no painel.

**CLEAR.**

## 9. Pipeline computacional (MUST)

```
Stage 0: Download PNADC Trimestral 2012Q1-2024Q4 (Python, ~4h, background)
         Download INEP Indicadores (Python, ~30min)
         Download PROFLUXO bibliography (manual web search + zotero)
         ↓
Stage 1: Parse PNADC fixed-width → .dta long (Python pyreadstat)
         ↓
Stage 2: Construir painel longitudinal (Stata)
         ↓
Stage 3: Calcular 5 indicadores + tabelas de heterogeneidade (Stata)
         ↓
Stage 4: Comparação INEP + decomposição R/U/S/C/M (Stata)
         ↓
Stage 5: Figuras (R + ggplot2)
         ↓
Stage 6: Redigir paper (LaTeX) + critics + submeter
```

### Naming convention
- Chain A: parsing PNADC (Python).
- Chain B: painel + indicadores (Stata).
- Chain C: comparação INEP (Stata).
- Chain D: figuras (R).
- Chain E: tabelas LaTeX finais (Stata `esttab`).

## 10. Pressupostos centrais (SHOULD, testáveis)

1. **Atrito ignorable:** atrito do painel não correlaciona com a transição. Teste em Seção 7: comparar observáveis (idade, sexo, renda, raça) entre retidos e perdidos.
2. **Identificador individual estável:** match por ordem+sexo+idade é robusto. Teste: % de "elo quebrado".
3. **`V3002` capta status atual:** sem ambiguidade entre frequenta semana × frequenta ano. Cuidado em janela de férias (Q3-Q4 brasileiros).

## 11. Riscos e mitigação (MAY)

| Risco | Mitigação |
|---|---|
| Tamanho amostral fino em células de heterogeneidade fina | Sempre reportar N efetivo e IC; agregar quintis se necessário |
| Mudança metodológica PNADC entre 2012-2024 | Documentar em Apêndice B; padronizar variáveis (versões V3006 pré-2019 vs. V3014 pós-2019) |
| Definição de "frequenta escola" sensível a férias | Excluir/sinalizar trimestres atípicos; usar janela larga |
| Atraso/descontinuação do INEP | Documentar datas; usar última publicação disponível |
| Mais-de-um membro do domicílio match ambíguo | Reportar % de "elo quebrado" e fazer robustez em apêndice |

## 12. Bibliografia esqueleto (já parcialmente conhecida)

**PROFLUXO-CESGRANRIO:** Fletcher 1985, 1993; Fletcher & Ribeiro 1989; Ribeiro 1991; Klein & Ribeiro 1991; Klein 2006.
**Contemporâneos:** Soares-Alves-Ferrão; Riani-Rios Neto; IMDS (2022); Cameron & Heckman (1993).
**Metodologia:** INEP — notas técnicas; IBGE — nota metodológica PNADC longitudinal.

**NÃO incluir:** dissertação Fernanda Castro (orientação explícita do autor).

## 13. Não-objetivos (escopo excluído)

- **Análise causal** do impacto do Pé-de-Meia (separadamente em outro paper).
- **Modelos estruturais** de fluxo escolar (PROFLUXO já cobre essa frente; aqui é assumption-light).
- **Comparação internacional** detalhada (mencionar apenas para benchmarking de OECD).
- **Análise por município** (UF é o nível mínimo viável com PNADC).
- **Indicadores de aprendizagem** (SAEB; outro paper).

---

## Self-review (post-write)

- [x] Placeholder scan — nenhum TBD remanescente.
- [x] Consistência interna — Seção 3 (5 indicadores) ↔ Seção 8 (4 tabelas que contêm os 5); coerente.
- [x] Escopo focado em uma nota empírica única (não decomposta em sub-projetos).
- [x] Ambiguidades resolvidas:
  - "Janela do indicador" definida operacionalmente (5.3).
  - "BFA proxy vs. observado" diferenciado (Tabela 6, Subamostra V5).
  - "Decomposição" formalizada em equação (Seção 7).
  - "Não-objetivos" explicitados (Seção 13).
