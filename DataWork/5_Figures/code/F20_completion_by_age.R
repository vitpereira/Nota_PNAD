# -------------------------------------------------------------------------
# F20_completion_by_age.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   % de jovens 14-24 que ja concluiram o EM (VD3004 >= 5), por idade
#   individual, comparando renda < R$ 230 com renda > 1/2 SM.
#   Highlight de coortes:
#     EXPOSTAS ao PdM: idade <= 18 em 2025 (era <= 17 quando PdM comecou)
#     NAO EXPOSTAS:    idade >= 22 em 2025 (era >= 21 quando PdM comecou)
#
# Inputs:
INPUT <- "../../3_Indicators/output/C39_completion_by_age.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F20_completion_by_age.pdf"
OUTPUT_PNG <- "../output/F20_completion_by_age.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    filter(grupo %in% c("Renda < R$ 230", "Renda > 1/2 SM")) %>%
    mutate(grupo = factor(grupo, levels = c(
                "Renda < R$ 230",
                "Renda > 1/2 SM"
           )))

p <- ggplot(df, aes(x = idade, y = completed_rate * 100,
                       color = grupo, linetype = grupo, shape = grupo)) +
    # Coortes
    annotate("rect", xmin = 13.5, xmax = 18.5, ymin = -Inf, ymax = Inf,
              alpha = 0.10, fill = "#1A5276") +
    annotate("rect", xmin = 21.5, xmax = 24.5, ymin = -Inf, ymax = Inf,
              alpha = 0.10, fill = "gray40") +
    annotate("text", x = 16, y = 95,
              label = "Coorte EXPOSTA ao PdM\n(tinha ≤17 anos quando\nprograma começou em mar/2024)",
              size = 2.8, family = "serif", color = "#1A5276") +
    annotate("text", x = 23, y = 30,
              label = "Coorte NÃO EXPOSTA\n(já tinha ≥21 anos\nem mar/2024)",
              size = 2.8, family = "serif", color = "gray30") +
    geom_line(linewidth = 0.9) +
    geom_point(size = 2.4) +
    scale_x_continuous(breaks = 14:24,
                        sec.axis = sec_axis(~. - 1,
                                              breaks = 13:23,
                                              name = "Idade em mar/2024 (início PdM)")) +
    scale_y_continuous(labels = function(x) paste0(x, "%"),
                        breaks = seq(0, 100, 20),
                        limits = c(0, 100)) +
    scale_color_manual(values = c(
        "Renda < R$ 230"  = "#922B21",
        "Renda > 1/2 SM"  = "#1A5276"
    ), name = NULL) +
    scale_linetype_manual(values = c(
        "Renda < R$ 230"  = "solid",
        "Renda > 1/2 SM"  = "dotdash"
    ), name = NULL) +
    scale_shape_manual(values = c(
        "Renda < R$ 230"  = 16,
        "Renda > 1/2 SM"  = 15
    ), name = NULL) +
    labs(x = "Idade em 2025",
          y = "% que já concluiu o ensino médio",
          caption = paste0(
              "Universo: jovens 14-24 anos observados em PNADC 2025 (Q1-Q4). ",
              "Numerador: VD3004 ≥ 5 (ensino médio completo ou superior). ",
              "Renda dom. per capita calculada do trimestre corrente. ",
              "Pesos: V1028."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))

ggsave(OUTPUT_PDF, p, width = 9, height = 5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 9, height = 5, dpi = 150)
cat("Saved F20\n")
