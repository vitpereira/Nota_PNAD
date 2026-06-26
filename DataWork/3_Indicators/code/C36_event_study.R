# -------------------------------------------------------------------------
# C36_event_study.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   DOIS event studies separados. Convencao da literatura:
#   omitir o trimestre IMEDIATAMENTE ANTERIOR ao choque (k=-1).
#     (A) Renda < 1/4 SM: choque = 2023Q4 (anuncio dez/2023)
#         Trimestre omitido: 2023Q3 (k=-1)
#     (B) 1/4 SM <= renda <= 1/2 SM: choque = 2024Q3 (Portaria 792 ago/2024)
#         Trimestre omitido: 2024Q2 (k=-1)
#   Cada modelo compara o grupo respectivo contra controle = renda > 1/2 SM,
#   excluindo o outro grupo da amostra.
#
#   Modelo:
#     y_it = alpha_uf + gamma_q + delta * 1[treat] +
#            sum_{k != T0} beta_k * 1[treat] * 1[q=k] + eps
#
#   Outcomes:
#     1. em_regular (V3002=1 AND V3003A=6)
#     2. engage (V3002=1 OR VD3004>=5)
#
# Inputs:
INPUT <- "../output/C33_micro_em_15_19.parquet"
#
# Outputs:
OUT_A_EM <- "../output/C36_event_extreme_em.csv"
OUT_A_EN <- "../output/C36_event_extreme_engage.csv"
OUT_B_EM <- "../output/C36_event_low_em.csv"
OUT_B_EN <- "../output/C36_event_low_engage.csv"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(arrow, fixest, tidyverse, broom)

cat("Loading microdata...\n")
d <- read_parquet(INPUT)
cat(sprintf("Rows: %s\n", format(nrow(d), big.mark = ".")))

d <- d %>%
    mutate(em_regular = em_regular * 100,
           em_engage  = em_or_eja_or_done * 100,
           engage     = escola_ou_em_completo * 100,
           yr_q       = factor(yr_q,
                                  levels = c("2022Q1","2022Q2","2022Q3","2022Q4",
                                              "2023Q1","2023Q2","2023Q3","2023Q4",
                                              "2024Q1","2024Q2","2024Q3","2024Q4",
                                              "2025Q1","2025Q2","2025Q3","2025Q4")),
           UF         = factor(UF))

run_event <- function(data, treat_var, base_q, outcome_var, label) {
    f <- as.formula(sprintf(
        "%s ~ %s + i(yr_q, %s, ref = '%s') | UF + yr_q",
        outcome_var, treat_var, treat_var, base_q
    ))
    m <- feols(f, data = data, weights = ~wt, cluster = ~hh_id)
    co <- tidy(m, conf.int = TRUE, conf.level = 0.95) %>%
        filter(str_detect(term, treat_var)) %>%
        filter(str_detect(term, "yr_q::")) %>%
        mutate(yr_q = str_extract(term, "20\\d{2}Q\\d"),
               ano  = as.integer(str_sub(yr_q, 1, 4)),
               trim = as.integer(str_sub(yr_q, 6, 6)),
               x    = ano + (trim - 0.5) / 4,
               grupo = label)
    # Add baseline row
    base_ano <- as.integer(str_sub(base_q, 1, 4))
    base_trim <- as.integer(str_sub(base_q, 6, 6))
    base_row <- tibble(grupo = label, yr_q = base_q,
                       ano = base_ano, trim = base_trim,
                       x = base_ano + (base_trim - 0.5) / 4,
                       estimate = 0, std.error = NA, statistic = NA,
                       p.value = NA, conf.low = 0, conf.high = 0,
                       term = NA)
    bind_rows(co, base_row) %>% arrange(x)
}

# { Estudo A: Renda < 1/4 SM vs controle (T0 = 2023Q4) ----
cat("\n=== Estudo A: extreme vs control (T0 = 2023Q4) ===\n")
dA <- d %>% filter(grupo %in% c("control", "extreme"))
cat(sprintf("  N obs: %s\n", format(nrow(dA), big.mark = ".")))

coA_em <- run_event(dA, "treat_extreme", "2023Q3", "em_engage",
                     "Renda < R$ 230")
write_csv(coA_em, OUT_A_EM)
cat(sprintf("  Saved %s\n", OUT_A_EM))
# } ----

# { Estudo B: 1/4-1/2 SM vs controle (T0 = 2024Q3) ----
cat("\n=== Estudo B: low vs control (T0 = 2024Q3) ===\n")
dB <- d %>% filter(grupo %in% c("control", "low"))
cat(sprintf("  N obs: %s\n", format(nrow(dB), big.mark = ".")))

coB_em <- run_event(dB, "treat_low", "2024Q2", "em_engage",
                     "R$ 230 a 1/2 SM")
write_csv(coB_em, OUT_B_EM)
cat(sprintf("  Saved %s\n", OUT_B_EM))
# } ----

cat("\nDone.\n")
