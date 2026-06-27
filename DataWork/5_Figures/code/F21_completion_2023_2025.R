# -------------------------------------------------------------------------
# F21_completion_2023_2025.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Comparacao de coortes: % concluiu EM por idade (14-21), 6 curvas:
#     - Renda < R$ 230 em 2021, 2023, 2025
#     - Renda > 1/2 SM em 2021, 2023, 2025
#
#   2021: coorte pre-PdM e em pico da pandemia (COVID)
#   2023: coorte pre-PdM, pos-pandemia
#   2025: coorte parcialmente exposta ao PdM
#
# Inputs:
INPUT <- "../../3_Indicators/output/C40_completion_2023_2025.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F21_completion_2023_2025.pdf"
OUTPUT_PNG <- "../output/F21_completion_2023_2025.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    filter(grupo %in% c("Renda < R$ 230", "Renda > 1/2 SM")) %>%
    mutate(serie = paste0(grupo, " — ", ano),
           serie = factor(serie, levels = c(
                "Renda < R$ 230 — 2021",
                "Renda < R$ 230 — 2023",
                "Renda < R$ 230 — 2025",
                "Renda > 1/2 SM — 2021",
                "Renda > 1/2 SM — 2023",
                "Renda > 1/2 SM — 2025"
           )))

# Cores: tons da mesma palette (claro = 2021, medio = 2023, escuro = 2025)
p <- ggplot(df, aes(x = idade, y = completed_rate * 100,
                       color = serie, linetype = serie, shape = serie)) +
    geom_line(linewidth = 0.85) +
    geom_point(size = 2.2) +
    scale_x_continuous(breaks = 14:21) +
    scale_y_continuous(labels = function(x) paste0(x, "%"),
                        breaks = seq(0, 100, 20),
                        limits = c(0, 90)) +
    scale_color_manual(values = c(
        "Renda < R$ 230 — 2021" = "#D98880",
        "Renda < R$ 230 — 2023" = "#C0392B",
        "Renda < R$ 230 — 2025" = "#641E16",
        "Renda > 1/2 SM — 2021" = "#7FB3D5",
        "Renda > 1/2 SM — 2023" = "#2874A6",
        "Renda > 1/2 SM — 2025" = "#1B2631"
    ), name = NULL) +
    scale_linetype_manual(values = c(
        "Renda < R$ 230 — 2021" = "dotted",
        "Renda < R$ 230 — 2023" = "dashed",
        "Renda < R$ 230 — 2025" = "solid",
        "Renda > 1/2 SM — 2021" = "dotted",
        "Renda > 1/2 SM — 2023" = "dashed",
        "Renda > 1/2 SM — 2025" = "solid"
    ), name = NULL) +
    scale_shape_manual(values = c(
        "Renda < R$ 230 — 2021" = 2,
        "Renda < R$ 230 — 2023" = 1,
        "Renda < R$ 230 — 2025" = 16,
        "Renda > 1/2 SM — 2021" = 5,
        "Renda > 1/2 SM — 2023" = 0,
        "Renda > 1/2 SM — 2025" = 15
    ), name = NULL) +
    labs(x = "Idade",
          y = "% que já concluiu o ensino médio",
          caption = paste0(
              "Universo: jovens 14-21 anos observados em PNADC 2021, 2023 e 2025 (Q1-Q4 de cada ano). ",
              "Numerador: VD3004 ≥ 5. Renda dom. per capita contemporânea ao trimestre. Pesos: V1028. ",
              "2021 = coorte em plena pandemia, pré-PdM. 2023 = coorte pré-PdM pós-pandemia. ",
              "2025 = coorte parcialmente exposta ao PdM."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          legend.box = "vertical",
          legend.spacing.y = unit(0.05, "cm"),
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25")) +
    guides(color = guide_legend(nrow = 2, byrow = TRUE))

ggsave(OUTPUT_PDF, p, width = 10, height = 5.5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 10, height = 5.5, dpi = 150)
cat("Saved F21\n")
