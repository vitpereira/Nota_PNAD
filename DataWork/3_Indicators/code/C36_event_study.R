# -------------------------------------------------------------------------
# C36_event_study.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Event study TWFE do efeito do Pe-de-Meia.
#   Baseline (omitido): 2023Q3 (ultimo trimestre antes do anuncio Dez/23).
#   Para cada trimestre k != 2023Q3, estima beta_k^{low} e beta_k^{extreme}.
#
#   Modelo:
#     y_it = alpha_uf + gamma_q +
#            delta_low * 1[low] + delta_ex * 1[extreme] +
#            sum_{k != base} beta_k^{low} * 1[low] * 1[q=k] +
#            sum_{k != base} beta_k^{extreme} * 1[extreme] * 1[q=k] + eps
#
#   Outcomes:
#     1. em_regular (V3002=1 AND V3003A=6)
#     2. engage (V3002=1 OR VD3004>=5)
#
#   FE: UF + yr_q. Pesos: V1028. SE clustered hh_id.
#
# Inputs:
INPUT <- "../output/C33_micro_em_15_19.parquet"
#
# Outputs:
OUT_CSV_EM <- "../output/C36_event_em.csv"
OUT_CSV_EN <- "../output/C36_event_engage.csv"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(arrow, fixest, tidyverse, broom)

cat("Loading microdata...\n")
d <- read_parquet(INPUT)
cat(sprintf("Rows: %s\n", format(nrow(d), big.mark = ".")))

d <- d %>%
    mutate(em_regular = em_regular * 100,
           engage     = escola_ou_em_completo * 100,
           yr_q       = factor(yr_q,
                                  levels = c("2022Q1","2022Q2","2022Q3","2022Q4",
                                              "2023Q1","2023Q2","2023Q3","2023Q4",
                                              "2024Q1","2024Q2","2024Q3","2024Q4",
                                              "2025Q1","2025Q2","2025Q3","2025Q4")),
           UF         = factor(UF))

BASE_Q <- "2023Q3"  # baseline omitido

# { Outcome 1: EM regular ----
cat("\nEvent study EM regular...\n")
m_em <- feols(em_regular ~ treat_low + treat_extreme +
                            i(yr_q, treat_low,     ref = BASE_Q) +
                            i(yr_q, treat_extreme, ref = BASE_Q) |
                            UF + yr_q,
               data = d, weights = ~wt, cluster = ~hh_id)
co_em <- tidy(m_em, conf.int = TRUE, conf.level = 0.95) %>%
    filter(str_detect(term, "treat_(low|extreme)")) %>%
    filter(str_detect(term, "yr_q::"))

# Extract group and quarter
co_em <- co_em %>%
    mutate(grupo = case_when(
                str_detect(term, "treat_low")     ~ "1/4 a 1/2 SM",
                str_detect(term, "treat_extreme") ~ "Renda < 1/4 SM",
                TRUE ~ NA_character_),
           yr_q = str_extract(term, "20\\d{2}Q\\d"),
           ano = as.integer(str_sub(yr_q, 1, 4)),
           trim = as.integer(str_sub(yr_q, 6, 6)),
           x = ano + (trim - 0.5) / 4)

# Add baseline row (zero)
base_x <- 2023 + (3 - 0.5) / 4
base_rows <- tibble(grupo = c("1/4 a 1/2 SM", "Renda < 1/4 SM"),
                     yr_q = BASE_Q, ano = 2023, trim = 3, x = base_x,
                     estimate = 0, std.error = NA, statistic = NA,
                     p.value = NA, conf.low = 0, conf.high = 0,
                     term = NA)
co_em <- bind_rows(co_em, base_rows) %>% arrange(grupo, x)
write_csv(co_em, OUT_CSV_EM)
cat(sprintf("Saved %s (%d rows)\n", OUT_CSV_EM, nrow(co_em)))
# } ----

# { Outcome 2: Engajamento ----
cat("\nEvent study engajamento...\n")
m_en <- feols(engage ~ treat_low + treat_extreme +
                        i(yr_q, treat_low,     ref = BASE_Q) +
                        i(yr_q, treat_extreme, ref = BASE_Q) |
                        UF + yr_q,
               data = d, weights = ~wt, cluster = ~hh_id)
co_en <- tidy(m_en, conf.int = TRUE, conf.level = 0.95) %>%
    filter(str_detect(term, "treat_(low|extreme)")) %>%
    filter(str_detect(term, "yr_q::")) %>%
    mutate(grupo = case_when(
                str_detect(term, "treat_low")     ~ "1/4 a 1/2 SM",
                str_detect(term, "treat_extreme") ~ "Renda < 1/4 SM",
                TRUE ~ NA_character_),
           yr_q = str_extract(term, "20\\d{2}Q\\d"),
           ano = as.integer(str_sub(yr_q, 1, 4)),
           trim = as.integer(str_sub(yr_q, 6, 6)),
           x = ano + (trim - 0.5) / 4)
co_en <- bind_rows(co_en, base_rows) %>% arrange(grupo, x)
write_csv(co_en, OUT_CSV_EN)
cat(sprintf("Saved %s (%d rows)\n", OUT_CSV_EN, nrow(co_en)))
# } ----

cat("\nDone.\n")
