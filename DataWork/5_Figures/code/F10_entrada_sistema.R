# -------------------------------------------------------------------------
# F10_entrada_sistema.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Figura da taxa de entrada no sistema escolar regular por faixa
#   etária e por ano. Painel A: média 2012-2023 por faixa etária.
#   Painel B: série temporal por ano para algumas faixas.
#
# Inputs:
INPUT_AVG  <- "../../3_Indicators/output/T_entrada_no_sistema.csv"
INPUT_YEAR <- "../../3_Indicators/output/T_entrada_por_ano.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F10_entrada_sistema.pdf"
OUTPUT_PNG <- "../output/F10_entrada_sistema.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, patchwork)

avg <- read_csv(INPUT_AVG, show_col_types = FALSE)
yr  <- read_csv(INPUT_YEAR, show_col_types = FALSE)

# Painel A: barras por faixa etária (média 2012-2023)
avg <- avg %>%
    mutate(idade_bin = factor(idade_bin,
                                levels = c("4-6 anos", "7-10 anos",
                                           "11-14 anos", "15-17 anos",
                                           "18-24 anos")))

p_a <- ggplot(avg, aes(x = idade_bin, y = taxa_entrada,
                          label = scales::percent(taxa_entrada, accuracy = 0.1))) +
    geom_col(fill = "#1A5276", width = 0.7) +
    geom_text(vjust = -0.4, size = 3.2, family = "serif") +
    scale_y_continuous(labels = percent_format(accuracy = 1),
                        limits = c(0, 1.0)) +
    labs(x = NULL, y = "Taxa de entrada no sistema",
          title = "Painel A: Por faixa etária (média 2012--2023)") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(panel.grid.minor = element_blank(),
          plot.title = element_text(size = 11, hjust = 0))

# Painel B: série temporal por ano, para 3 faixas selecionadas
yr <- yr %>%
    mutate(idade_bin = factor(idade_bin,
                                levels = c("4-6 anos", "7-10 anos",
                                           "11-14 anos", "15-17 anos",
                                           "18-24 anos")))

yr_select <- yr %>%
    filter(idade_bin %in% c("4-6 anos", "15-17 anos", "18-24 anos"))

p_b <- ggplot(yr_select, aes(x = ano_t, y = taxa_entrada,
                                  color = idade_bin, group = idade_bin)) +
    geom_line(linewidth = 0.6) +
    geom_point(size = 1.5) +
    annotate("rect", xmin = 2020, xmax = 2021,
              ymin = -Inf, ymax = Inf,
              alpha = 0.10, fill = "gray50") +
    scale_color_manual(values = c("4-6 anos"     = "#1A5276",
                                     "15-17 anos"   = "#922B21",
                                     "18-24 anos"   = "#7D6608")) +
    scale_y_continuous(labels = percent_format(accuracy = 1),
                        limits = c(0, NA)) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    labs(x = NULL, y = "Taxa de entrada no sistema",
          color = NULL,
          title = "Painel B: Série temporal por faixa etária") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.title = element_text(size = 11, hjust = 0))

p <- p_a / p_b +
    plot_annotation(
        caption = paste0(
            "Universo: indivíduos 4-24 anos não observados em EF/EM regular ou técnico em t. ",
            "Numerador: matriculados em t+1.\n",
            "Painel longitudinal PNADC, janela Q2-Q3. Faixa cinza em B: anos COVID 2020-2021."
        ),
        theme = theme(plot.caption = element_text(hjust = 0, size = 8.5,
                                                    color = "gray25",
                                                    family = "serif"))
    )

ggsave(OUTPUT_PDF, p, width = 8.5, height = 7, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 8.5, height = 7, dpi = 200)

cat("Saved F10_entrada_sistema\n")
