# -------------------------------------------------------------------------
# F4_cohort_fluxo.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Replica Figuras 2 e 3 do IMDS A002 / Fernandes (2011) usando PNADC
#   trimestral. Versao DUAL:
#
#   Painel A (versao Fernandes "estilo IMDS"): indice por SERIE
#     Cada serie normalizada a 100 no inicio. Mostra abandono intra-ano
#     limpamente. Renormalizacao "esconde" transicoes entre series.
#
#   Painel B (NOVO): indice de COORTE (100 no inicio do 8o EF)
#     Cada coorte normalizada a 100 no Q1 do 8o EF. Mostra TODAS as quedas:
#     intra-ano (abandono) + entre-series (evasao + repetencia + migracao EJA).
#     Esta versao responde a critica do strategist-critic 4.1.
#
# Inputs:
#   3_Indicators/output/F4_cohort_normalized.csv
# -------------------------------------------------------------------------

F4_TOTAL <- file.path(INDIC_OUT, "F4_cohort_normalized.csv")

if (!file.exists(F4_TOTAL)) {
    cat("F4_cohort SKIP\n")
} else {
    library(patchwork)

    df <- read_csv(F4_TOTAL, show_col_types = FALSE) %>%
        mutate(
            serie_lbl = factor(serie_lbl,
                               levels = c("8o EF", "1o EM", "2o EM", "3o EM")),
            cohort_year = factor(cohort_year)
        )

    # Painel A: normalizado por serie (mostra apenas abandono intra-ano)
    pA <- df %>%
        ggplot(aes(x = tempo_rel, y = indice_serie,
                   color = cohort_year,
                   group = interaction(cohort_year, serie_lbl))) +
        geom_line(linewidth = 0.8, alpha = 0.85) +
        geom_point(size = 1.5, alpha = 0.85) +
        geom_vline(xintercept = c(3.5, 7.5, 11.5),
                   linetype = "dashed", color = "grey60") +
        annotate("text", x = 1.5, y = 105, label = "8º EF", size = 3.5, family = "serif") +
        annotate("text", x = 5.5, y = 105, label = "1º EM", size = 3.5, family = "serif") +
        annotate("text", x = 9.5, y = 105, label = "2º EM", size = 3.5, family = "serif") +
        annotate("text", x = 13.5, y = 105, label = "3º EM", size = 3.5, family = "serif") +
        scale_x_continuous(breaks = 0:15,
                           labels = rep(c("Q1", "Q2", "Q3", "Q4"), 4)) +
        scale_y_continuous(limits = c(NA, 108)) +
        scale_color_brewer(palette = "Dark2", name = "Coorte\n8º EF") +
        labs(x = NULL, y = "Índice por série (Q1 = 100)",
             title = NULL, subtitle = NULL) +
        theme(legend.position = "right",
              panel.grid.minor = element_blank())

    # Painel B: normalizado por COORTE (mostra abandono + entre-series drops)
    pB <- df %>%
        ggplot(aes(x = tempo_rel, y = indice,
                   color = cohort_year,
                   group = interaction(cohort_year, serie_lbl))) +
        geom_line(linewidth = 0.8, alpha = 0.85) +
        geom_point(size = 1.5, alpha = 0.85) +
        geom_vline(xintercept = c(3.5, 7.5, 11.5),
                   linetype = "dashed", color = "grey60") +
        annotate("text", x = 1.5, y = max(df$indice, na.rm = TRUE) * 1.05,
                 label = "8º EF", size = 3.5, family = "serif") +
        annotate("text", x = 5.5, y = max(df$indice, na.rm = TRUE) * 1.05,
                 label = "1º EM", size = 3.5, family = "serif") +
        annotate("text", x = 9.5, y = max(df$indice, na.rm = TRUE) * 1.05,
                 label = "2º EM", size = 3.5, family = "serif") +
        annotate("text", x = 13.5, y = max(df$indice, na.rm = TRUE) * 1.05,
                 label = "3º EM", size = 3.5, family = "serif") +
        scale_x_continuous(breaks = 0:15,
                           labels = rep(c("Q1", "Q2", "Q3", "Q4"), 4)) +
        scale_color_brewer(palette = "Dark2", name = "Coorte\n8º EF") +
        labs(x = NULL, y = "Índice da coorte (Q1 8º EF = 100)",
             title = NULL, subtitle = NULL) +
        theme(legend.position = "right",
              panel.grid.minor = element_blank())

    pcombined <- pA / pB +
        plot_annotation(
            tag_levels = list(c(
                "Painel A — Índice normalizado por série (mostra abandono intra-ano)",
                "Painel B — Índice de coorte: cada cohort = 100 no início (mostra todas as quedas)"
            ))
        ) &
        theme(plot.tag = element_text(family = "serif", size = 9, face = "bold", hjust = 0))

    ggsave(file.path(OUTDIR, "F4_cohort_fluxo.pdf"),
           plot = pcombined, width = 11, height = 9, device = cairo_pdf)
    ggsave(file.path(OUTDIR, "F4_cohort_fluxo.png"),
           plot = pcombined, width = 11, height = 9, dpi = 300)

    cat("F4 cohort OK (dual panel)\n")
}
