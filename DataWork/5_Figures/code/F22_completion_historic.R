# -------------------------------------------------------------------------
# F22_completion_historic.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   % concluiu EM por idade (14-21), em 2015, 2017, 2019, 2021, 2023, 2025.
#   Dois paineis lado-a-lado: Renda < R$ 230 e Renda > 1/2 SM.
#
# Inputs:
INPUT <- "../../3_Indicators/output/C41_completion_historic.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F22_completion_historic.pdf"
OUTPUT_PNG <- "../output/F22_completion_historic.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, RColorBrewer)

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    filter(grupo %in% c("Renda < R$ 230", "Renda > 1/2 SM")) %>%
    mutate(ano = factor(ano,
                          levels = c("2015","2017","2019","2021","2023","2025")),
           grupo = factor(grupo, levels = c("Renda < R$ 230",
                                              "Renda > 1/2 SM")))

# Cor gradiente sequencial por ano: claro -> escuro
cores <- c("2015" = "#FDD0A2",
            "2017" = "#FDAE6B",
            "2019" = "#FD8D3C",
            "2021" = "#E6550D",
            "2023" = "#A63603",
            "2025" = "#000000")

p <- ggplot(df, aes(x = idade, y = completed_rate * 100,
                       color = ano, group = ano)) +
    geom_line(linewidth = 0.85) +
    geom_point(size = 2.0) +
    facet_wrap(~grupo, ncol = 2) +
    scale_x_continuous(breaks = 14:21) +
    scale_y_continuous(labels = function(x) paste0(x, "%"),
                        breaks = seq(0, 100, 20),
                        limits = c(0, 95)) +
    scale_color_manual(values = cores, name = "Ano da observação") +
    labs(x = "Idade",
          y = "% que já concluiu o ensino médio",
          caption = paste0(
              "Universo: jovens 14-21 anos em PNADC. ",
              "Numerador: VD3004 ≥ 5 (EM completo ou superior). ",
              "Renda dom. per capita classificada por: < R$ 230 (extrema pobreza, nominal) e > 1/2 SM nominal do ano. ",
              "SM por ano: R$ 788 (2015), R$ 937 (2017), R$ 998 (2019), R$ 1.100 (2021), R$ 1.320 (2023), R$ 1.518 (2025). ",
              "PdM anunciado em dez/2023; primeira parcela em mar/2024."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold", size = 10),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))

ggsave(OUTPUT_PDF, p, width = 11, height = 5.5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 11, height = 5.5, dpi = 150)
cat("Saved F22\n")
