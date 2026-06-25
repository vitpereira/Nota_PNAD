# -------------------------------------------------------------------------
# F3_captura_retorno.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
# -------------------------------------------------------------------------

F3_ETAPA  <- file.path(INDIC_OUT, "F3_captura_retorno_por_macroetapa.csv")
F3_QUINT  <- file.path(INDIC_OUT, "F3_captura_retorno_por_quintil.csv")

if (!file.exists(F3_ETAPA)) {
    cat("F3 SKIP: input principal nao encontrado\n")
} else {
    df_a <- read_csv(F3_ETAPA, show_col_types = FALSE) %>%
        filter(macroetapa %in% c("EF iniciais", "EF finais", "EM")) %>%
        pivot_longer(cols = c(mudou_rede, mudou_modalidade),
                     names_to = "tipo", values_to = "fracao") %>%
        mutate(
            tipo = case_when(
                tipo == "mudou_rede"       ~ "Mudou de rede",
                tipo == "mudou_modalidade" ~ "Mudou de modalidade"
            ),
            macroetapa = factor(macroetapa,
                                levels = c("EF iniciais", "EF finais", "EM"))
        )

    pA <- df_a %>%
        ggplot(aes(x = macroetapa, y = fracao, fill = tipo)) +
        geom_col(position = "dodge") +
        scale_y_continuous(labels = scales::percent_format(accuracy = 0.1)) +
        scale_fill_brewer(palette = "Set1") +
        labs(x = NULL, y = NULL, fill = NULL, title = NULL)

    pB <- NULL
    if (file.exists(F3_QUINT)) {
        df_b <- read_csv(F3_QUINT, show_col_types = FALSE) %>%
            filter(macroetapa == "EM" & !is.na(quintil_renda))
        pB <- df_b %>%
            ggplot(aes(x = quintil_renda, y = mudou_rede)) +
            geom_col(fill = "#4d4d4d") +
            scale_y_continuous(labels = scales::percent_format(accuracy = 0.1)) +
            labs(x = NULL, y = "% mudou de rede", title = NULL) +
            theme(axis.text.x = element_text(angle = 30, hjust = 1))
    }

    if (!is.null(pB)) {
        library(patchwork)
        pcombined <- pA / pB +
            plot_annotation(tag_levels = "A", tag_prefix = "Painel ") &
            theme(plot.tag = element_text(family = "serif", size = 10, face = "bold"))
    } else {
        pcombined <- pA
    }

    ggsave(file.path(OUTDIR, "F3_captura_retorno.pdf"),
           plot = pcombined, width = 8, height = 7)
    ggsave(file.path(OUTDIR, "F3_captura_retorno.png"),
           plot = pcombined, width = 8, height = 7, dpi = 300)

    cat("F3 OK: figura salva\n")
}
