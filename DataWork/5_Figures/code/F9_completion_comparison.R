# -------------------------------------------------------------------------
# F9_completion_comparison.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Figura comparando taxas de conclusao do EM:
#     - INEP projetada (linha horizontal)
#     - PNADC projetada (linha horizontal)
#     - PNADC observada (linha ao longo dos anos) via VD3004
#
# Inputs:
INPUT_OBS  <- "../../3_Indicators/output/F9_completion_by_year.csv"
INPUT_COMP <- "../../3_Indicators/output/T7_iterative_completion.csv"
#
# Outputs:
OUTPUT_PDF <- "../output/F9_completion_comparison.pdf"
OUTPUT_PNG <- "../output/F9_completion_comparison.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, patchwork)

obs <- read_csv(INPUT_OBS, show_col_types = FALSE)
comp <- read_csv(INPUT_COMP, show_col_types = FALSE)

# Pull projected rates
inep_em_proj  <- comp$completion_em[comp$source == "INEP (projetada)"] / 100
pnadc_em_proj <- comp$completion_em[comp$source == "PNADC (projetada)"] / 100
inep_ef_proj  <- comp$completion_ef[comp$source == "INEP (projetada)"] / 100
pnadc_ef_proj <- comp$completion_ef[comp$source == "PNADC (projetada)"] / 100

# Plot 1: EM completion
p_em <- ggplot(obs, aes(x = Ano, y = completed_em)) +
    geom_line(linewidth = 0.8, color = "#1A5276") +
    geom_point(size = 2, color = "#1A5276") +
    geom_hline(yintercept = inep_em_proj, linetype = "dashed",
               color = "#922B21", linewidth = 0.7) +
    geom_hline(yintercept = pnadc_em_proj, linetype = "dotted",
               color = "#B7950B", linewidth = 0.8) +
    annotate("text", x = 2014, y = inep_em_proj + 0.02,
             label = sprintf("INEP projetada (%.1f%%)", inep_em_proj * 100),
             color = "#922B21", size = 3, hjust = 0, family = "serif") +
    annotate("text", x = 2014, y = pnadc_em_proj + 0.02,
             label = sprintf("PNADC projetada (%.1f%%)", pnadc_em_proj * 100),
             color = "#B7950B", size = 3, hjust = 0, family = "serif") +
    annotate("rect", xmin = 2020, xmax = 2021,
             ymin = -Inf, ymax = Inf,
             alpha = 0.10, fill = "gray50") +
    scale_y_continuous(labels = percent_format(accuracy = 1),
                       limits = c(0, 1)) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    labs(x = NULL, y = "% jovens 19-24 com EM completo",
         title = "Painel A: Conclusão do EM") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(panel.grid.minor = element_blank(),
          plot.title = element_text(size = 11, hjust = 0))

# Plot 2: EF completion
p_ef <- ggplot(obs, aes(x = Ano, y = completed_ef)) +
    geom_line(linewidth = 0.8, color = "#1A5276") +
    geom_point(size = 2, color = "#1A5276") +
    geom_hline(yintercept = inep_ef_proj, linetype = "dashed",
               color = "#922B21", linewidth = 0.7) +
    geom_hline(yintercept = pnadc_ef_proj, linetype = "dotted",
               color = "#B7950B", linewidth = 0.8) +
    annotate("text", x = 2014, y = inep_ef_proj + 0.02,
             label = sprintf("INEP projetada (%.1f%%)", inep_ef_proj * 100),
             color = "#922B21", size = 3, hjust = 0, family = "serif") +
    annotate("text", x = 2014, y = pnadc_ef_proj - 0.04,
             label = sprintf("PNADC projetada (%.1f%%)", pnadc_ef_proj * 100),
             color = "#B7950B", size = 3, hjust = 0, family = "serif") +
    annotate("rect", xmin = 2020, xmax = 2021,
             ymin = -Inf, ymax = Inf,
             alpha = 0.10, fill = "gray50") +
    scale_y_continuous(labels = percent_format(accuracy = 1),
                       limits = c(0, 1)) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    labs(x = NULL, y = "% jovens 19-24 com EF completo",
         title = "Painel B: Conclusão do EF",
         caption = "Linha sólida azul: conclusão observada na PNADC (VD3004) por ano. Linhas tracejadas: projeções iterativas de coorte aplicando as taxas do INEP e da PNADC. Faixa cinza: COVID 2020-2021.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(panel.grid.minor = element_blank(),
          plot.title = element_text(size = 11, hjust = 0),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray35"))

combined <- p_em / p_ef
ggsave(OUTPUT_PDF, combined, width = 8, height = 8, device = cairo_pdf)
ggsave(OUTPUT_PNG, combined, width = 8, height = 8, dpi = 200)
cat("Saved", OUTPUT_PDF, "\n")
