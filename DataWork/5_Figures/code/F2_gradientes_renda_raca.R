# -------------------------------------------------------------------------
# F2_gradientes_renda_raca.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-24
#
# Description:
#   Figura 2 - gradientes dos 5 indicadores por:
#     Painel A: quintil de renda dom. PC (Q1 ao Q5)
#     Painel B: raca/cor (branca, parda, preta)
#   Recorte: 1o EM (macroetapa = 3), media 2018-2023.
#
# Inputs:
#   3_Indicators/output/T2_heterog_quintil_renda.csv
#   3_Indicators/output/T2_heterog_raca.csv
#
# Outputs:
#   output/F2_gradientes_renda_raca.pdf
# -------------------------------------------------------------------------

F2_RENDA <- file.path(INDIC_OUT, "T2_heterog_quintil_renda.csv")
F2_RACA  <- file.path(INDIC_OUT, "T2_heterog_raca.csv")

if (!file.exists(F2_RENDA) | !file.exists(F2_RACA)) {
    cat("F2 SKIP: inputs nao encontrados\n")
} else {
    # { Renda ----
    df_renda <- read_csv(F2_RENDA, show_col_types = FALSE) %>%
        filter(macroetapa == 3) %>%   # EM
        pivot_longer(
            cols = matches("flag_"),
            names_to = "indicador_raw",
            values_to = "taxa"
        ) %>%
        mutate(
            indicador = case_when(
                str_detect(indicador_raw, "promocao")    ~ "Promoção",
                str_detect(indicador_raw, "repetencia")  ~ "Repetência",
                str_detect(indicador_raw, "evasao")      ~ "Evasão",
                str_detect(indicador_raw, "naoprog")     ~ "Não-progressão",
                TRUE ~ NA_character_
            )
        ) %>%
        filter(!is.na(indicador))

    pA <- df_renda %>%
        ggplot(aes(x = quintil_renda, y = taxa, fill = indicador)) +
        geom_col(position = "dodge") +
        scale_x_continuous(breaks = 1:5, labels = c("Q1\n(mais pobre)", "Q2", "Q3", "Q4", "Q5\n(mais rico)")) +
        scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
        scale_fill_brewer(palette = "Dark2") +
        labs(x = NULL, y = NULL, title = NULL, subtitle = NULL, fill = NULL)
    # } ----

    # { Raca ----
    df_raca <- read_csv(F2_RACA, show_col_types = FALSE) %>%
        filter(macroetapa == 3) %>%
        pivot_longer(
            cols = matches("flag_"),
            names_to = "indicador_raw",
            values_to = "taxa"
        ) %>%
        mutate(
            indicador = case_when(
                str_detect(indicador_raw, "promocao")    ~ "Promoção",
                str_detect(indicador_raw, "repetencia")  ~ "Repetência",
                str_detect(indicador_raw, "evasao")      ~ "Evasão",
                str_detect(indicador_raw, "naoprog")     ~ "Não-progressão",
                TRUE ~ NA_character_
            ),
            raca_lbl = case_when(
                raca == 1 ~ "Branca",
                raca == 2 ~ "Preta",
                raca == 3 ~ "Amarela",
                raca == 4 ~ "Parda",
                raca == 5 ~ "Indigena"
            )
        ) %>%
        filter(!is.na(indicador), raca %in% c(1, 2, 4))  # branca, preta, parda

    pB <- df_raca %>%
        ggplot(aes(x = raca_lbl, y = taxa, fill = indicador)) +
        geom_col(position = "dodge") +
        scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
        scale_fill_brewer(palette = "Dark2") +
        labs(x = NULL, y = NULL, title = NULL, subtitle = NULL, fill = NULL)
    # } ----

    # { Combinar ----
    library(patchwork)
    pcombined <- (pA / pB) +
        plot_annotation(tag_levels = "A", tag_prefix = "Painel ") &
        theme(plot.tag = element_text(family = "serif", size = 10, face = "bold"))

    ggsave(file.path(OUTDIR, "F2_gradientes_renda_raca.pdf"),
           plot = pcombined, width = 8, height = 7, device = cairo_pdf)
    ggsave(file.path(OUTDIR, "F2_gradientes_renda_raca.png"),
           plot = pcombined, width = 8, height = 7, dpi = 300)

    cat("F2 OK: figura salva em", file.path(OUTDIR, "F2_gradientes_renda_raca.pdf"), "\n")
    # } ----
}
