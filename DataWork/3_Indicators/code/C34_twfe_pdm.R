# -------------------------------------------------------------------------
# C34_twfe_pdm.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Estima TWFE (FE de UF + FE de trimestre) do impacto do Pe-de-Meia
#   sobre matricula em EM regular entre jovens 15-19, usando 3 grupos
#   por renda:
#     control: renda > 1/2 SM (referencia)
#     low:     1/4 SM <= renda <= 1/2 SM (CadUnico-elegivel)
#     extreme: renda < 1/4 SM (extrema pobreza)
#
#   Tres definicoes de post:
#     post_anuncio: q >= 2023Q4 (anuncio/aprovacao Congresso dez/2023)
#     post_implem:  q >= 2024Q1 (primeira parcela mar/2024)
#     post_expand:  q >= 2024Q3 (expansao CadUnico ago/2024)
#
#   Modelo:
#     em_regular_iqt = alpha_uf + gamma_q +
#                       delta_low * 1[low] + delta_ex * 1[extreme] +
#                       beta_low * (1[low] * post) +
#                       beta_ex  * (1[extreme] * post) +
#                       controles + epsilon
#     Pesos: V1028. SE clustered em hh_id.
#
# Inputs:
INPUT <- "../output/C33_micro_em_15_19.parquet"
#
# Outputs:
OUT_TXT <- "../output/C34_twfe_pdm_results.txt"
OUT_TEX <- "../output/T_twfe_pdm.tex"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(arrow, fixest, modelsummary, tidyverse, kableExtra)

cat("Loading microdata...\n")
d <- read_parquet(INPUT)
cat(sprintf("Rows: %s\n", format(nrow(d), big.mark = ".")))

# Outcomes em % (0/1 to 0/100)
d <- d %>%
    mutate(em_regular = em_regular * 100,
           em_any     = em_any * 100,
           grupo = factor(grupo, levels = c("control", "low", "extreme")),
           hh_id = factor(hh_id),
           UF    = factor(UF),
           yr_q  = factor(yr_q),
           idade_grp = case_when(
               idade <= 17 ~ "15-17",
               TRUE        ~ "18-19"
           ))

# { Modelos DiD com 3 definicoes de post ----
# Modelo 1: post_anuncio
m1 <- feols(em_regular ~ treat_low + treat_extreme + post_anuncio:treat_low + post_anuncio:treat_extreme
                          | UF + yr_q,
             data = d, weights = ~wt, cluster = ~hh_id)

# Modelo 2: post_implem
m2 <- feols(em_regular ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme
                          | UF + yr_q,
             data = d, weights = ~wt, cluster = ~hh_id)

# Modelo 3: post_expand
m3 <- feols(em_regular ~ treat_low + treat_extreme + post_expand:treat_low + post_expand:treat_extreme
                          | UF + yr_q,
             data = d, weights = ~wt, cluster = ~hh_id)

# Modelo 4: controles demograficos (post_implem)
m4 <- feols(em_regular ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme +
                           idade + sexo_f + preta_parda
                           | UF + yr_q,
             data = d, weights = ~wt, cluster = ~hh_id)

# Modelo 5: por faixa 15-17
m5 <- feols(em_regular ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme
                          | UF + yr_q,
             data = d %>% filter(idade_grp == "15-17"),
             weights = ~wt, cluster = ~hh_id)

# Modelo 6: por faixa 18-19
m6 <- feols(em_regular ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme
                          | UF + yr_q,
             data = d %>% filter(idade_grp == "18-19"),
             weights = ~wt, cluster = ~hh_id)

# Modelos 7-9: outcome alternativo (engajamento escolar)
# y = 100 * 1[V3002=1 OR VD3004>=5] (frequenta OU formou EM)
d <- d %>% mutate(engage = escola_ou_em_completo * 100)
m7 <- feols(engage ~ treat_low + treat_extreme + post_anuncio:treat_low + post_anuncio:treat_extreme
                       | UF + yr_q,
             data = d, weights = ~wt, cluster = ~hh_id)
m8 <- feols(engage ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme
                       | UF + yr_q,
             data = d, weights = ~wt, cluster = ~hh_id)
m9 <- feols(engage ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme +
                       idade + sexo_f + preta_parda
                       | UF + yr_q,
             data = d, weights = ~wt, cluster = ~hh_id)
m10 <- feols(engage ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme
                        | UF + yr_q,
              data = d %>% filter(idade_grp == "15-17"),
              weights = ~wt, cluster = ~hh_id)
m11 <- feols(engage ~ treat_low + treat_extreme + post_implem:treat_low + post_implem:treat_extreme
                        | UF + yr_q,
              data = d %>% filter(idade_grp == "18-19"),
              weights = ~wt, cluster = ~hh_id)
# } ----

# { Print results ----
sink(OUT_TXT)
cat("============================================\n")
cat(" TWFE: PdM x Matricula em EM Regular (15-19)\n")
cat("============================================\n\n")
cat("Variavel dependente: 100 * 1[V3002=1 AND V3003A=6]\n")
cat("Universo: jovens 15-19 anos, 2022Q1-2025Q4\n")
cat("Pesos: V1028 (peso PNADC)\n")
cat("Clustered SE: hh_id\n\n")
cat("\n\n=== OUTCOME 1: Matricula em EM regular (V3002=1 AND V3003A=6) ===\n\n")
etable(m1, m2, m3, m4, m5, m6,
        headers = c("Pos Anuncio", "Pos Implem", "Pos Expand",
                     "Implem+Ctrl", "15-17", "18-19"),
        signif.code = c("***"=0.01, "**"=0.05, "*"=0.10),
        depvar = FALSE)

cat("\n\n=== OUTCOME 2: Engajamento (V3002=1 OR VD3004>=5 EM completo) ===\n\n")
etable(m7, m8, m9, m10, m11,
        headers = c("Pos Anuncio", "Pos Implem",
                     "Implem+Ctrl", "15-17", "18-19"),
        signif.code = c("***"=0.01, "**"=0.05, "*"=0.10),
        depvar = FALSE)
sink()
cat(sprintf("\nResults written to %s\n", OUT_TXT))

# Save LaTeX table
sink(OUT_TEX)
etable(m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11,
        headers = c("EM-Anun", "EM-Imp", "EM-Exp", "EM-Ctrl", "EM-1517", "EM-1819",
                     "EnA", "EnI", "EnIC", "En1517", "En1819"),
        signif.code = c("***"=0.01, "**"=0.05, "*"=0.10),
        depvar = FALSE,
        tex = TRUE,
        title = "TWFE: efeito do Pé-de-Meia sobre matrícula em EM regular e engajamento escolar (jovens 15-19)",
        label = "tab:twfe_pdm")
sink()
cat(sprintf("LaTeX table written to %s\n", OUT_TEX))
# } ----
