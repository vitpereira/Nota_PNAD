# -------------------------------------------------------------------------
# F15_em_attendance_by_renda_15_19.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Figura trimestral 2022Q1-2025Q4 de matricula em EM regular entre
#   jovens 15-19 anos, 3 grupos por renda dom. per capita:
#     - Renda < 1/4 SM (extrema pobreza)
#     - 1/4 a 1/2 SM (CadUnico-elegivel)
#     - Renda > 1/2 SM (fora CadUnico)
#   Linhas verticais nas datas-chave do Pe-de-Meia.
#
# Inputs:
INPUT <- "../../3_Indicators/output/C32_em_attendance_by_renda.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F15_em_attendance_by_renda_15_19.pdf"
OUTPUT_PNG <- "../output/F15_em_attendance_by_renda_15_19.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    mutate(
        x = Ano + (Trim - 0.5) / 4,
        grupo = factor(grupo, levels = c(
            "Renda < 1/4 SM",
            "1/4 a 1/2 SM",
            "Renda > 1/2 SM"
        ))
    )

# Datas-chave PdM
x_pdm_implem <- 2024.25
x_pdm_expand <- 2024.625

p <- ggplot(df, aes(x = x, y = em_rate * 100,
                       color = grupo, linetype = grupo, shape = grupo)) +
    geom_vline(xintercept = x_pdm_implem, linetype = "dotted",
                color = "gray30", linewidth = 0.5) +
    geom_vline(xintercept = x_pdm_expand, linetype = "dotted",
                color = "gray30", linewidth = 0.5) +
    annotate("text", x = x_pdm_implem, y = 60,
              label = "Pé-de-Meia\nimplementação\n(mar/2024)",
              size = 2.6, family = "serif", color = "gray25",
              hjust = 1.05, vjust = 1) +
    annotate("text", x = x_pdm_expand, y = 60,
              label = "Expansão\nCadÚnico\n(ago/2024)",
              size = 2.6, family = "serif", color = "gray25",
              hjust = -0.05, vjust = 1) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.6) +
    scale_x_continuous(
        breaks = seq(2022.125, 2025.875, 0.25),
        labels = c("2022Q1","Q2","Q3","Q4",
                    "2023Q1","Q2","Q3","Q4",
                    "2024Q1","Q2","Q3","Q4",
                    "2025Q1","Q2","Q3","Q4")
    ) +
    scale_y_continuous(labels = function(x) paste0(x, "%"),
                        limits = c(40, 60), breaks = seq(40, 60, 2)) +
    scale_color_manual(values = c(
        "Renda < 1/4 SM" = "#922B21",
        "1/4 a 1/2 SM"   = "#7D6608",
        "Renda > 1/2 SM" = "#1A5276"
    ), name = NULL) +
    scale_linetype_manual(values = c(
        "Renda < 1/4 SM" = "solid",
        "1/4 a 1/2 SM"   = "dashed",
        "Renda > 1/2 SM" = "dotdash"
    ), name = NULL) +
    scale_shape_manual(values = c(
        "Renda < 1/4 SM" = 16,
        "1/4 a 1/2 SM"   = 17,
        "Renda > 1/2 SM" = 15
    ), name = NULL) +
    labs(x = NULL, y = NULL,
          caption = paste0(
              "Universo: jovens 15-19 anos. Numerador: matriculados em EM regular (V3002=1, V3003A=6). ",
              "Renda = renda domiciliar per capita (V403312 somada por domicílio dividida por V2001), ",
              "classificada por fração do salário mínimo do ano (R$1.212 em 2022, R$1.320 em 2023, R$1.412 em 2024, R$1.518 em 2025)."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))

ggsave(OUTPUT_PDF, p, width = 12, height = 5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 12, height = 5, dpi = 200)
cat("Saved F15\n")
