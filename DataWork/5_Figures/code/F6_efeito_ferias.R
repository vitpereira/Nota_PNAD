# -------------------------------------------------------------------------
# F6_efeito_ferias.R
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Figura ilustrando o efeito do timing de medicao em t+1 (Q1 jan-mar
#   vs Q2+ abr-dez) sobre repetencia e promocao no painel within-person.
#
# Inputs:
INPUT  <- "../../3_Indicators/output/C10_within_person_by_year.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F6_efeito_ferias_within.pdf"
OUTPUT_PNG <- "../output/F6_efeito_ferias_within.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, patchwork)

df <- read_csv(INPUT, show_col_types = FALSE)

# Tidy
long <- df %>%
    rename(
        macroetapa = macroetapa_t,
        ano = ano_base
    ) %>%
    select(ano, macroetapa, n,
           prom_Q1, prom_Q2p,
           rep_Q1,  rep_Q2p,
           evas_Q1, evas_Q2p) %>%
    pivot_longer(
        cols = -c(ano, macroetapa, n),
        names_to = c("indicador", "timing"),
        names_pattern = "(prom|rep|evas)_(Q1|Q2p)"
    ) %>%
    mutate(
        indicador = recode(indicador,
                           prom = "Promoção",
                           rep  = "Repetência",
                           evas = "Evasão"),
        timing = recode(timing,
                        Q1  = "Medido em Q1 de t+1 (jan-mar)",
                        Q2p = "Medido em Q2-Q4 de t+1 (abr-dez)"),
        macroetapa = factor(macroetapa, levels = c("EF iniciais", "EF finais", "EM"))
    ) %>%
    filter(!is.na(macroetapa))

# Filter to prom and rep (evas is 0 by construction of within sample)
long_pr <- long %>% filter(indicador %in% c("Promoção", "Repetência"))

# Plot: 2 panels (Promocao, Repetencia), x=ano, y=indicador, colors=timing
p <- ggplot(long_pr,
            aes(x = ano, y = value, color = timing,
                linetype = timing, group = timing)) +
    geom_line(linewidth = 0.6) +
    geom_point(size = 1.4) +
    facet_grid(indicador ~ macroetapa, scales = "free_y") +
    scale_y_continuous(labels = percent_format(accuracy = 1)) +
    scale_x_continuous(breaks = seq(2012, 2023, 2)) +
    scale_color_manual(values = c(
        "Medido em Q1 de t+1 (jan-mar)" = "#C0392B",
        "Medido em Q2-Q4 de t+1 (abr-dez)" = "#2E86C1"
    )) +
    scale_linetype_manual(values = c(
        "Medido em Q1 de t+1 (jan-mar)"      = "solid",
        "Medido em Q2-Q4 de t+1 (abr-dez)" = "dashed"
    )) +
    annotate("rect", xmin = 2020, xmax = 2021,
             ymin = -Inf, ymax = Inf,
             alpha = 0.10, fill = "gray50") +
    labs(x = NULL, y = NULL, color = NULL, linetype = NULL,
         caption = paste0(
             "Painel within-person: alunos observados em Q1 E em Q2+ do ano t+1 (n=",
             format(sum(long_pr$n[long_pr$indicador == "Promoção" & long_pr$timing == "Medido em Q1 de t+1 (jan-mar)"]),
                    big.mark = "."), ").\n",
             "Faixa cinza = anos COVID 2020-2021.")
         ) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray35"))

ggsave(OUTPUT_PDF, p, width = 9, height = 5.2, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 9, height = 5.2, dpi = 200)

cat("Saved", OUTPUT_PDF, "and", OUTPUT_PNG, "\n")
