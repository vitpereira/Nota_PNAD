# Research Brief — Nota_PNAD

## Título provisório

**Indicadores de fluxo escolar via painel longitudinal da PNAD Contínua: três décadas depois do PROFLUXO**

## Research Question

Como construir indicadores de fluxo escolar (aprovação, reprovação, abandono, evasão, não-progressão) usando o painel longitudinal de 5 trimestres da PNAD Contínua, e em que medida essas estimativas (i) convergem com as do INEP, (ii) capturam dimensões — heterogeneidade socioeconômica e tempestividade — inacessíveis com a publicação oficial agregada?

## Contribuição

A nota revisita a tradição **PROFLUXO-CESGRANRIO** (Fletcher, Ribeiro, Klein; 1985-1991), que inferia fluxo escolar a partir da matriz idade-série de um corte da PNAD via modelo de estado estacionário. A nova arquitetura longitudinal da PNADC (5 trimestres por domicílio) substitui inferência por **observação direta** das transições, removendo as hipóteses estacionárias. Quatro vantagens sobre as estatísticas oficiais:

1. **Tempestividade** — PNADC trimestral; INEP defasa anos.
2. **Desagregação socioeconômica** — renda PC, BFA, raça, CadÚnico-proxy; INEP publica só agregado.
3. **Independência da fonte** — pesquisa domiciliar valida registro administrativo.
4. **Captura de retorno** — Censo perde quem muda de rede/UF/modalidade; PNADC segue.

## Dados

- **Fonte primária:** PNADC Trimestral, IBGE (2012Q1 a 2024Q4 — 52 trimestres).
- **Fonte primária 2:** PNADC Anual Visita 5 (2019-2024) para variáveis de programas sociais (BFA).
- **Fonte comparadora:** INEP — Indicadores de Rendimento (aprovação, reprovação, abandono); Indicadores de Trajetória/Fluxo (promoção, repetência, evasão).
- **Variáveis-chave:** `V3002` (frequenta escola), `V3002A` (rede), `V3006`/`V3014` (série), `V3003A`/`V3009A` (etapa), `V2007`/`V2009`/`V2010` (sexo/idade/raça), `VD5008` (renda dom. PC), `V5002A` (BFA, só Visita 5).
- **Identificadores do painel:** `UF + UPA + V1008 + V1014` (domicílio); `+ V2003` (indivíduo) com validação por sexo+idade.
- **Amostra:** indivíduos 4-24 anos com `V3002=1` na primeira observação do ano t (EF, EM, EJA). Painel separado para EJA.

## Estratégia de identificação

**Descritiva, com observação direta de transições.**

- **Painel longitudinal:** linkagem dos 5 trimestres pelo identificador domiciliar; validação individual por consistência de sexo/idade.
- **Janela do indicador:** (a) intra-ano (abandono): primeira obs. ano t → última obs. mesmo ano; (b) entre-anos (evasão/promoção/repetência): primeira obs. ano t → última obs. ano t+1.
- **Reponderação:** P1 (peso da primeira visita) na tabela principal; P3 (inverse propensity para correção de atrito) em apêndice.
- **Comparação com INEP:** decomposição da diferença em 5 fontes — Retorno (R), Universo (U), Sampling (S), sub-Cobertura (C), erro de Medida (M residual).

### Pressupostos centrais (a discutir e testar)
1. **Atrito ignorable:** dada a longitudinalidade restrita a 5 trimestres, o atrito (saída do painel) não correlaciona com a transição estudada. Teste: comparar características observáveis dos retidos vs. perdidos.
2. **Estabilidade do identificador individual:** match por ordem+sexo+idade é robusto. Teste: % de "elo quebrado" por características demográficas.
3. **Captura uniforme de "frequenta escola":** a pergunta `V3002` capta status atualizado, não retrospectivo. Teste: comparar consistência intra-domicílio.

## Status

| Componente | Status | Notas |
|---|---|---|
| Literature review | em curso | PROFLUXO-CESGRANRIO + contemporâneos; sem Fernanda Castro |
| Data download | em curso | PNADC trimestral 2012-24 em background |
| Data cleaning | pendente | depende do download |
| Construção do painel | pendente | módulo 2_PanelBuild |
| Cálculo de indicadores | pendente | módulo 3_Indicators |
| Comparação INEP | pendente | módulo 4_INEP_Comparison |
| Tables and figures | pendente | 4 tabelas + 4 figuras + 3 caixas-texto |
| Draft sections | pendente | 8 seções + 2 apêndices |
| Robustness | pendente | atrito, reponderação, definição |

## Restrições

- Não modificar arquivos em `DataWork/*/input/`.
- Tabelas/figuras finais são `\input{}`-eadas por `Paper/main.tex` de `DataWork/.../output/`.
- Alvo: working paper → submissão a *Estudos Econômicos* (USP) ou *Pesquisa e Planejamento Econômico* (IPEA).

## Arquivos de referência

- `master_supporting_docs/PROFLUXO/` — Fletcher (1985, 1993), Ribeiro (1991), Klein & Ribeiro (1991), Klein (2006).
- `master_supporting_docs/IMDS/` — três relatórios IMDS (2022).
- `master_supporting_docs/INEP/` — notas técnicas dos Indicadores de Rendimento e Trajetória.
- `master_supporting_docs/IBGE/` — nota metodológica do painel PNADC.

## Bibliografia (esqueleto)

**PROFLUXO-CESGRANRIO (núcleo histórico):**
- Fletcher, P. R. (1985). [Primeiro PROFLUXO]
- Fletcher, P. R. & Ribeiro, S. C. (1989). *Modelagem do sistema educacional brasileiro*.
- Ribeiro, S. C. (1991). *A pedagogia da repetência*. Estudos Avançados, 5(12).
- Klein, R. & Ribeiro, S. C. (1991). *O Censo Educacional e o modelo de fluxo*.
- Fletcher, P. R. (1993). *À procura do ensino eficaz*. Cadernos MEC.
- Klein, R. (2006). *Como está a educação no Brasil?* Ensaio: Av. Pol. Públicas em Educação, 14(51).

**Contemporâneos (extensão):**
- Soares, T. M.; Alves, M. T. G.; Ferrão, M. E. — fluxo escolar e modelos longitudinais.
- Riani, J. L. R.; Rios-Neto, E. L. G. (2008) — *background familiar*.
- Alves, M. T. G.; Soares, J. F. — *contexto escolar e indicadores*.
- IMDS (2022) — três relatórios sobre evasão.
- Cameron, S. V.; Heckman, J. J. (1993) — *nonequivalence of high school equivalents*.

**Metodologia INEP/IBGE:**
- INEP — notas técnicas dos Indicadores de Rendimento e Trajetória.
- IBGE — nota metodológica PNADC longitudinal.
