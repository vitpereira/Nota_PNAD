# -------------------------------------------------------------------------
# F16_engagement_15_19.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Figura trimestral 2022Q1-2025Q4 do indicador de ENGAJAMENTO ESCOLAR:
#     y = 1 se (frequenta escola V3002=1) OU (ja concluiu EM VD3004>=5)
#   Universo: jovens 15-19 anos. 3 grupos por renda dom. per capita.
#   Linhas verticais: aprovacao Congresso (dez/2023), primeira parcela
#   BFA (mar/2024), expansao CadUnico (ago/2024).
#
# Inputs:
INPUT <- "../../3_Indicators/output/C37_attendance_stable_engage.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F16_engagement_15_19.pdf"
OUTPUT_PNG <- "../output/F16_engagement_15_19.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    mutate(
        x = Ano + (Trim - 0.5) / 4,
        grupo = factor(grupo, levels = c(
            "Renda < R$ 230",
            "R$ 230 a 1/2 SM",
            "Renda > 1/2 SM"
        ))
    )

x_pdm_anuncio <- 2023.875
x_pdm_implem  <- 2024.25
x_pdm_expand  <- 2024.625

p <- ggplot(df, aes(x = x, y = engagement * 100,
                       color = grupo, linetype = grupo, shape = grupo)) +
    geom_vline(xintercept = x_pdm_anuncio, linetype = "dotted",
                color = "gray30", linewidth = 0.5) +
    geom_vline(xintercept = x_pdm_implem, linetype = "dotted",
                color = "gray30", linewidth = 0.5) +
    geom_vline(xintercept = x_pdm_expand, linetype = "dotted",
                color = "gray30", linewidth = 0.5) +
    annotate("text", x = x_pdm_anuncio, y = 100,
              label = "Aprovação\nCongresso\n(dez/2023)",
              size = 2.6, family = "serif", color = "gray25",
              hjust = 1.05, vjust = 1) +
    annotate("text", x = x_pdm_implem, y = 100,
              label = "Primeira\nparcela BFA\n(mar/2024)",
              size = 2.6, family = "serif", color = "gray25",
              hjust = -0.05, vjust = 1) +
    annotate("text", x = x_pdm_expand, y = 100,
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
                        breaks = seq(50, 100, 5)) +
    scale_color_manual(values = c(
        "Renda < R$ 230" = "#922B21",
        "R$ 230 a 1/2 SM"   = "#7D6608",
        "Renda > 1/2 SM" = "#1A5276"
    ), name = NULL) +
    scale_linetype_manual(values = c(
        "Renda < R$ 230" = "solid",
        "R$ 230 a 1/2 SM"   = "dashed",
        "Renda > 1/2 SM" = "dotdash"
    ), name = NULL) +
    scale_shape_manual(values = c(
        "Renda < R$ 230" = 16,
        "R$ 230 a 1/2 SM"   = 17,
        "Renda > 1/2 SM" = 15
    ), name = NULL) +
    labs(x = NULL, y = NULL,
          caption = paste0(
              "Universo: jovens 15-19 anos. Numerador: frequenta escola (V3002=1) OU já concluiu EM (VD3004 ≥ 5). ",
              "Renda = renda domiciliar per capita classificada por fração do salário mínimo do ano."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))

ggsave(OUTPUT_PDF, p, width = 9, height = 5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 9, height = 5, dpi = 150)
cat("Saved F16\n")
