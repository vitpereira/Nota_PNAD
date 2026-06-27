# -------------------------------------------------------------------------
# F21_completion_2023_2025.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Comparacao de coortes: % concluiu EM por idade (14-21), 4 curvas:
#     - Renda < R$ 230 em 2023 (coorte pre-PdM)
#     - Renda < R$ 230 em 2025 (coorte exposta ao PdM)
#     - Renda > 1/2 SM em 2023
#     - Renda > 1/2 SM em 2025
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
                "Renda < R$ 230 — 2023",
                "Renda < R$ 230 — 2025",
                "Renda > 1/2 SM — 2023",
                "Renda > 1/2 SM — 2025"
           )))

p <- ggplot(df, aes(x = idade, y = completed_rate * 100,
                       color = serie, linetype = serie, shape = serie)) +
    geom_line(linewidth = 0.9) +
    geom_point(size = 2.4) +
    scale_x_continuous(breaks = 14:21) +
    scale_y_continuous(labels = function(x) paste0(x, "%"),
                        breaks = seq(0, 100, 20),
                        limits = c(0, 90)) +
    scale_color_manual(values = c(
        "Renda < R$ 230 — 2023" = "#922B21",
        "Renda < R$ 230 — 2025" = "#922B21",
        "Renda > 1/2 SM — 2023" = "#1A5276",
        "Renda > 1/2 SM — 2025" = "#1A5276"
    ), name = NULL) +
    scale_linetype_manual(values = c(
        "Renda < R$ 230 — 2023" = "dashed",
        "Renda < R$ 230 — 2025" = "solid",
        "Renda > 1/2 SM — 2023" = "dashed",
        "Renda > 1/2 SM — 2025" = "solid"
    ), name = NULL) +
    scale_shape_manual(values = c(
        "Renda < R$ 230 — 2023" = 1,
        "Renda < R$ 230 — 2025" = 16,
        "Renda > 1/2 SM — 2023" = 0,
        "Renda > 1/2 SM — 2025" = 15
    ), name = NULL) +
    labs(x = "Idade",
          y = "% que já concluiu o ensino médio",
          caption = paste0(
              "Universo: jovens 14-21 anos observados em PNADC 2023 e 2025 (Q1-Q4 de cada ano). ",
              "Numerador: VD3004 ≥ 5. ",
              "Renda dom. per capita contemporânea ao trimestre. Pesos: V1028. ",
              "Linhas sólidas: coortes parcialmente expostas ao PdM (2025). ",
              "Linhas tracejadas: coortes pré-PdM (2023, antes do anúncio em dez/2023)."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          legend.box = "vertical",
          legend.spacing.y = unit(0.05, "cm"),
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25")) +
    guides(color = guide_legend(nrow = 2, byrow = TRUE))

ggsave(OUTPUT_PDF, p, width = 9, height = 5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 9, height = 5, dpi = 150)
cat("Saved F21\n")
