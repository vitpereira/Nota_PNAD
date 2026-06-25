# Nota_PNAD — Indicadores de Fluxo Escolar via Painel Longitudinal da PNADC

**Autor:** Vitor Pereira (UFRJ-IE / 3ie / CEHD-UChicago)
**Tipo:** Working paper (~36-44 pgs)
**Status:** draft inicial
**Última atualização:** 2026-06-24

## Quick Facts

| Item | Value |
|---|---|
| Pergunta de pesquisa | Como construir indicadores de fluxo escolar (aprovação, reprovação, abandono, evasão, não-progressão) usando o painel longitudinal de 5 trimestres da PNADC, comparar com INEP, e mostrar heterogeneidade socioeconômica inviável com dados agregados oficiais? |
| Tese central | Revisitar a tradição **PROFLUXO-CESGRANRIO** (Fletcher, Ribeiro, Klein, 1985-1991) com observação **direta** das transições no painel longitudinal da PNADC, em vez de inferência a partir de matriz idade-série cross-sectional. |
| Estratégia de identificação | Descritiva (estimação direta) com painel longitudinal de 5 trimestres; teste de robustez para atrito; reponderação P3 em apêndice. |
| Amostra | PNADC Trimestral 2012Q1 a 2024Q4, todos os indivíduos 4-24 anos, EF + EM + EJA, públicas e privadas. |
| Veículo-alvo | Working paper UFRJ-IE → submissão a *Estudos Econômicos* (USP). Alternativas: Revista Brasileira de Economia (RBE), Pesquisa e Planejamento Econômico (IPEA). |

## Os 5 indicadores

1. **Abandono** (intra-ano): primeira obs. estudando em ano t → última obs. não estudando no mesmo ano t.
2. **Evasão** (entre-anos): obs. estudando em t → obs. não estudando em t+1.
3. **Promoção/Aprovação** (entre-anos): obs. série S em t → obs. série S+1 em t+1.
4. **Repetência/Reprovação** (entre-anos): obs. série S em t → obs. mesma série S em t+1.
5. **Não-progressão** (entre-anos) = Repetência + Evasão = 1 − Promoção.

Identidade contábil: Promoção + Repetência + Evasão = 1 (entre-anos).

## Quatro vantagens da PNADC sobre INEP

| # | Vantagem | Mensurável |
|---|---|---|
| 1 | **Tempestividade** — PNADC trimestral; INEP atrasa anos | Sim — cronologia comparada |
| 2 | **Desagregação socioeconômica** — PNADC tem renda, raça, BFA; INEP só agrega | Sim — Tabelas 2 e 3 são impossíveis com INEP |
| 3 | **Independência da fonte** — pesquisa domiciliar × registro administrativo | Sim — validação cruzada |
| 4 | **Captura de retorno** — PNADC segue indivíduo; Censo perde quem muda de rede/UF/modalidade | Sim — % mudança de rede t→t+1 = upper bound do gap |

## Estrutura de pastas

```
Nota_PNAD/
├── CLAUDE.md, README.md, RESEARCH_BRIEF.md, MEMORY.md, SESSION_REPORT.md
├── Bibliography_base.bib
├── .claude/                            hooks + settings
├── DataWork/
│   ├── 1_DownloadPNADC/{code,input,output,tmp,misc}/    download bruto PNADC trimestral 2012-24
│   ├── 2_PanelBuild/{...}/                              construção do painel longitudinal
│   ├── 3_Indicators/{...}/                              cálculo dos 5 indicadores + heterogeneidade
│   └── 4_INEP_Comparison/{...}/                         download INEP, comparação, decomposição
├── Paper/
│   ├── main.tex
│   └── sections/
├── Talks/                              vazio até apresentação
├── Preambles/
├── master_supporting_docs/             PDFs de referência (CESGRANRIO, IMDS, etc.)
├── quality_reports/
│   ├── specs/                          requisitos
│   ├── plans/                          planos de implementação
│   ├── reviews/                        relatórios de critics
│   └── session_logs/                   logs de sessão
├── explorations/                       sandboxes
└── templates/
```

`Paper/main.tex` `\input{}`-eia tabelas e figuras diretamente de `DataWork/{módulo}/output/`. Sem `Tables/` ou `Figures/` no root.

## Restrições

- NÃO modificar nada em `DataWork/*/input/` — dados originais.
- NÃO reorganizar a estrutura de pastas.
- Scripts seguem `~/.claude/rules/R-standards.md` e `~/.claude/rules/stata-standards.md`.
- Nomenclatura por chain: `A1_…`, `A2_…`, `B1_…`, etc.
- Helpers começam com ponto: `._panel_helpers.do`.

## Stack computacional

| Etapa | Linguagem | Por que |
|---|---|---|
| Download PNADC + parse fixed-width | Python | Existe infraestrutura no projeto-pai; pandas é eficiente para parse |
| Conversão para .dta | Python (`pyreadstat`) | Output em formato Stata |
| Construção do painel longitudinal | Stata | Match com `merge` + lógica de validação familiar do autor |
| Cálculo dos 5 indicadores | Stata | Preferência declarada para regressão e tabulação |
| Comparação com INEP | Stata | Integra com painel já em .dta |
| Figuras | R (ggplot2) | Padrão de qualidade do autor para publicação |
| Tabelas LaTeX | Stata (`esttab`, `estout`) | Reproduz padrão Em-dash, booktabs |

## Quality Gates

| Score | Gate | Applies to |
|---|---|---|
| 80 | Commit | Weighted aggregate |
| 90 | PR | Weighted aggregate |
| 95 | Submission | Aggregate + all components ≥ 80 |

Ver `~/.claude/rules/quality.md`.

## Cronograma indicativo

| Fase | Tempo | Status |
|---|---|---|
| Spec + plano de implementação | 1h | em curso |
| Download PNADC trimestral 2012-24 | 4-6h (background) | em curso |
| Parse + construção do painel | 2h | pendente |
| Cálculo dos 5 indicadores + heterogeneidade | 2h | pendente |
| Download INEP + comparação | 1h | pendente |
| Redação do draft completo | 4h | pendente |
| Critics + revisão | 2h | pendente |
