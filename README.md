# Nota_PNAD — Indicadores de fluxo escolar via painel PNADC

**Autor:** Vitor Pereira (UFRJ-IE / 3ie / CEHD)
**Última atualização:** 2026-06-25
**Status:** draft v1 — 38 páginas compilando

## O que é este projeto

Working paper propondo cinco indicadores de fluxo escolar — **abandono**
(intra-ano), **evasão**, **promoção**, **repetência**, **não-progressão**
(entre-anos) — construídos a partir do **painel longitudinal de cinco
trimestres** da PNAD Contínua (IBGE, 2012-2024), comparados com as
estatísticas oficiais do INEP. A proposta dialoga com a tradição
PROFLUXO-CESGRANRIO (Fletcher–Ribeiro–Klein, 1985-2006), oferecendo uma
nova família de indicadores baseados em observação direta das transições.

## Estado do projeto

| Componente | Status | Localização |
|---|---|---|
| Working paper LaTeX | ✅ 38 pgs, 600 KB | `Paper/main.pdf` |
| 5 figuras (F1-F5) | ✅ Geradas | `DataWork/5_Figures/output/` |
| Tabela 4 PNADC×INEP | ✅ Renderizada | `DataWork/4_INEP_Comparison/output/T4_*.tex` |
| 30 CSVs indicadores | ✅ Computados | `DataWork/3_Indicators/output/` |
| Painel longitudinal | ✅ 806k transições | `DataWork/2_PanelBuild/output/painel_*.dta` |
| Microdados PNADC 2012-2024 | ✅ 4.86M obs harmonizadas | `DataWork/1_DownloadPNADC/` |
| Dados INEP Transição | ✅ 2007-2021 parseado | `DataWork/4_INEP_Comparison/output/inep_*.csv` |
| Bibliografia | ✅ 42 entradas | `Bibliography_base.bib` |
| **R Package publicado** | ✅ **github.com/vitpereira/fluxoescolar** | `RPackage/fluxoescolar/` |
| Critics | ✅ Writer 87/100, Strategist 82/100 | `quality_reports/reviews/` |

## Reprodução

### 1. Download da PNADC (~4-6h, 11 GB)

```bash
cd DataWork/1_DownloadPNADC/code
python A1_download_pnadc_trimestral.py
```

### 2. Parse + harmonização (~1.5h)

```bash
python A2_parse_pnadc_trimestral.py
# Converter parquets para .dta yearly
python /tmp/conv_year.py 2012  # repetir 2012-2024

cd ../../2_PanelBuild/code
"C:/Program Files/StataNow19/StataMP-64.exe" -e do B1_harmonize_pnadc.do
```

### 3. Cálculo dos indicadores (~30 min)

```bash
cd ../3_Indicators/code
"C:/Program Files/StataNow19/StataMP-64.exe" -e do _master.do
```

### 4. Download e parse INEP (~30 min)

```bash
cd ../../4_INEP_Comparison/code
python A1_download_inep.py
python A3_parse_inep_transicao.py
```

### 5. Figuras (~5 min)

```bash
cd ../../5_Figures/code
"C:/Program Files/R/R-4.5.0/bin/Rscript.exe" _master.R
```

### 6. Compilar paper

```bash
cd ../../../Paper
TEXINPUTS=../Preambles: pdflatex -interaction=nonstopmode main.tex
BIBINPUTS=.. bibtex main
TEXINPUTS=../Preambles: pdflatex -interaction=nonstopmode main.tex
TEXINPUTS=../Preambles: pdflatex -interaction=nonstopmode main.tex
```

## R Package `fluxoescolar`

Publicado em https://github.com/vitpereira/fluxoescolar.

Para instalar e usar:
```r
remotes::install_github("vitpereira/fluxoescolar")
library(fluxoescolar)

# Pipeline básico
baixar_pnadc(dir_destino = "~/dados/pnadc")
parsear_pnadc(dir_zips = "~/dados/pnadc", dir_destino = "~/dados/parsed")
# ... ver vignette para detalhes
```

## Achados substantivos (2019, Brasil)

- **EM evasão**: 24.5% (PNADC) vs 6.9% (INEP) — gap principalmente definicional
- **EM promoção**: 49% (PNADC) vs 82.7% (INEP)
- **EF iniciais promoção**: subiu de 65% (2012) para 76% (2019)
- **COVID 2020**: EF iniciais promoção cai a 57% (aprovação automática)
- **Quintil renda**: gap promoção Q1/Q5 = 9.6pp EF, 3.3pp EM (atenuado)
- **Defasagem 2+ anos**: evasão 28% no EM vs 17% em dia
- **Mulheres**: melhor promoção em todas etapas (+2-3pp)

## Limitações conhecidas

1. **Atrito do painel**: ~20% dos indivíduos perdem link entre visitas
   (sexo/idade mismatch). Reponderação P3 corrige parcialmente.
2. **COVID 2020-2021**: aprovação automática distorce os indicadores.
   Excluímos esses anos das médias multianuais.
3. **Gap PNADC × INEP**: ~33pp na promoção do EM é principalmente
   definicional (componente M da decomposição). Refinamento futuro
   usando V3013A para identificar conclusão do EM.
4. **Rotation-group bias**: o painel cobre indivíduos cujas 5 visitas
   atravessam 2 anos calendário. Heterogeneidade entre grupos de rotação
   não testada (item 2.2 do strategist-critic).

## Próximos passos

1. Refinar promoção 3º EM com V3013A
2. Rotation-group placebo  
3. Subamostra BFA observado (Visita 5)
4. Push completo do projeto para GitHub
5. Submissão a *Estudos Econômicos* (USP) ou *PPE* (IPEA)

## Estrutura

Ver `CLAUDE.md` para a estrutura completa e convenções.

## Licença

MIT © 2026 Vitor Azevedo Pereira

## Citação

Pereira, V. A. (2026). *Indicadores de fluxo escolar via painel
longitudinal da PNAD Contínua: três décadas depois do PROFLUXO*.
Working paper, UFRJ-IE.

R Package: Pereira, V. A. (2026). *fluxoescolar: Indicadores de Fluxo
Escolar via Painel Longitudinal da PNAD Contínua*. R package version
0.1.0. https://github.com/vitpereira/fluxoescolar
