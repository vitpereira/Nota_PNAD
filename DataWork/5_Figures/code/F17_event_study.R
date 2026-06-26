# -------------------------------------------------------------------------
# F17_event_study.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Plot event study TWFE: coeficientes por trimestre, baseline 2023Q3.
#   Dois paineis: (a) Matricula em EM regular; (b) Engajamento.
#   Para cada painel, duas linhas (low e extreme) com bandas de IC 95%.
#
# Inputs:
INPUT_EM <- "../../3_Indicators/output/C36_event_em.csv"
INPUT_EN <- "../../3_Indicators/output/C36_event_engage.csv"
#
# Outputs:
OUT_PDF_EM <- "../output/F17a_event_em.pdf"; OUT_PNG_EM <- "../output/F17a_event_em.png"
OUT_PDF_EN <- "../output/F17b_event_engage.pdf"; OUT_PNG_EN <- "../output/F17b_event_engage.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

make_event_plot <- function(input_path, ylab, ymin = NA, ymax = NA) {
    d <- read_csv(input_path, show_col_types = FALSE) %>%
        mutate(grupo = factor(grupo, levels = c("1/4 a 1/2 SM",
                                                  "Renda < 1/4 SM")))

    x_pdm_anuncio <- 2023.875
    x_pdm_implem  <- 2024.25
    x_pdm_expand  <- 2024.625
    x_baseline    <- 2023.625

    p <- ggplot(d, aes(x = x, y = estimate, color = grupo, fill = grupo,
                          group = grupo)) +
        # Banda de IC 95%
        geom_ribbon(aes(ymin = conf.low, ymax = conf.high),
                     alpha = 0.18, color = NA) +
        geom_hline(yintercept = 0, color = "gray40", linewidth = 0.4) +
        # Linhas verticais
        geom_vline(xintercept = x_baseline, color = "gray40",
                    linetype = "solid", linewidth = 0.4) +
        geom_vline(xintercept = x_pdm_anuncio, linetype = "dotted",
                    color = "gray30", linewidth = 0.5) +
        geom_vline(xintercept = x_pdm_implem, linetype = "dotted",
                    color = "gray30", linewidth = 0.5) +
        geom_vline(xintercept = x_pdm_expand, linetype = "dotted",
                    color = "gray30", linewidth = 0.5) +
        geom_line(linewidth = 0.6) +
        geom_point(size = 1.6) +
        # Labels nas linhas
        annotate("text", x = x_baseline, y = Inf,
                  label = "Baseline\n(2023Q3)",
                  size = 2.5, family = "serif", color = "gray25",
                  hjust = 1.05, vjust = 1.6) +
        annotate("text", x = x_pdm_anuncio, y = Inf,
                  label = "Aprovação\nCongresso\n(dez/2023)",
                  size = 2.5, family = "serif", color = "gray25",
                  hjust = -0.05, vjust = 1.6) +
        annotate("text", x = x_pdm_implem, y = Inf,
                  label = "Primeira\nparcela\n(mar/2024)",
                  size = 2.5, family = "serif", color = "gray25",
                  hjust = -0.05, vjust = 1.6) +
        annotate("text", x = x_pdm_expand, y = Inf,
                  label = "Expansão\nCadÚnico\n(ago/2024)",
                  size = 2.5, family = "serif", color = "gray25",
                  hjust = -0.05, vjust = 1.6) +
        scale_x_continuous(
            breaks = seq(2022.125, 2025.875, 0.25),
            labels = c("2022Q1","Q2","Q3","Q4",
                        "2023Q1","Q2","Q3","Q4",
                        "2024Q1","Q2","Q3","Q4",
                        "2025Q1","Q2","Q3","Q4")
        ) +
        scale_y_continuous(labels = function(x) paste0(x, " p.p.")) +
        scale_color_manual(values = c(
            "1/4 a 1/2 SM"   = "#7D6608",
            "Renda < 1/4 SM" = "#922B21"
        ), name = NULL) +
        scale_fill_manual(values = c(
            "1/4 a 1/2 SM"   = "#7D6608",
            "Renda < 1/4 SM" = "#922B21"
        ), name = NULL) +
        labs(x = NULL, y = ylab,
              caption = paste0(
                  "Coeficientes de event-study TWFE com baseline em 2023Q3. ",
                  "Cinza claro: IC 95% com SE clusterizados em domicílio. ",
                  "Grupo controle: jovens 15-19 com renda dom. per capita > 1/2 SM. ",
                  "Pesos: V1028. FE de UF e trimestre."
              )) +
        theme_minimal(base_family = "serif", base_size = 10) +
        theme(legend.position = "bottom",
              panel.grid.minor = element_blank(),
              axis.text.x = element_text(angle = 45, hjust = 1),
              plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))

    if (!is.na(ymin) && !is.na(ymax)) {
        p <- p + coord_cartesian(ylim = c(ymin, ymax))
    }
    p
}

p_em <- make_event_plot(INPUT_EM,
    ylab = "Δ matrícula EM regular (p.p. vs. baseline)",
    ymin = -6, ymax = 9)
p_en <- make_event_plot(INPUT_EN,
    ylab = "Δ engajamento escolar (p.p. vs. baseline)",
    ymin = -3, ymax = 5)

ggsave(OUT_PDF_EM, p_em, width = 12, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_EM, p_em, width = 12, height = 5, dpi = 200)
ggsave(OUT_PDF_EN, p_en, width = 12, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_EN, p_en, width = 12, height = 5, dpi = 200)
cat("Saved F17a (EM regular) and F17b (engajamento)\n")
