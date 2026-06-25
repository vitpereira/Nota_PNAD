# -------------------------------------------------------------------------
# F1_serie_temporal.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Figura 1 - serie temporal 2012-2024 dos 5 indicadores, por macroetapa.
#
# Inputs:
#   3_Indicators/output/F1_serie_temporal_indicadores.csv
#   3_Indicators/output/T1_brasil_inter_por_macroetapa_ano.csv
#   3_Indicators/output/T1_brasil_intra_por_macroetapa_ano.csv
#
# Outputs:
#   output/F1_serie_temporal_pnadc.pdf
# -------------------------------------------------------------------------

INTER_INPUT <- file.path(INDIC_OUT, "T1_brasil_inter_por_macroetapa_ano.csv")
INTRA_INPUT <- file.path(INDIC_OUT, "T1_brasil_intra_por_macroetapa_ano.csv")

if (!file.exists(INTER_INPUT)) {
    cat("F1 SKIP: input nao encontrado em", INTER_INPUT, "\n")
} else {
    df_inter <- read_csv(INTER_INPUT, show_col_types = FALSE)
    # macroetapa eh string com label
    df_inter <- df_inter %>%
        rename(year = ano_t) %>%
        select(year, macroetapa,
               flag_promocao, flag_repetencia, flag_evasao, flag_naoprog)

    # Abandono separado
    if (file.exists(INTRA_INPUT)) {
        df_intra <- read_csv(INTRA_INPUT, show_col_types = FALSE) %>%
            rename(year = ano_cal) %>%
            select(year, macroetapa, flag_abandono)
        df_all <- df_inter %>% left_join(df_intra, by = c("year", "macroetapa"))
    } else {
        df_all <- df_inter
    }

    df_long <- df_all %>%
        pivot_longer(
            cols = starts_with("flag_"),
            names_to = "indicador_raw",
            values_to = "taxa"
        ) %>%
        mutate(
            indicador = case_when(
                indicador_raw == "flag_promocao"   ~ "Promoção",
                indicador_raw == "flag_repetencia" ~ "Repetência",
                indicador_raw == "flag_evasao"     ~ "Evasão",
                indicador_raw == "flag_naoprog"    ~ "Não-progressão",
                indicador_raw == "flag_abandono"   ~ "Abandono",
                TRUE ~ indicador_raw
            )
        ) %>%
        filter(!is.na(taxa) & macroetapa %in% c("EF iniciais", "EF finais", "EM"))
        # Etapa codes harmonizados: V3003 (pre-2016) com codigos 3=EF, 5=EM mapeados
        # para V3003A pos-2016 onde 4=EF, 6=EM. Agora consistente 2012-2024.

    indicadores_main <- c("Promoção", "Repetência", "Evasão", "Abandono")

    p1 <- df_long %>%
        filter(indicador %in% indicadores_main) %>%
        mutate(
            indicador = factor(indicador, levels = indicadores_main),
            macroetapa = factor(macroetapa,
                                levels = c("EF iniciais", "EF finais", "EM"))
        ) %>%
        ggplot(aes(x = year, y = taxa, color = macroetapa)) +
        annotate("rect", xmin = 2020, xmax = 2021, ymin = -Inf, ymax = Inf,
                 alpha = 0.15, fill = "grey50") +
        geom_line(linewidth = 1) +
        geom_point(size = 1.5) +
        facet_wrap(~indicador, scales = "free_y", ncol = 2) +
        scale_x_continuous(breaks = 2012:2024) +
        scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
        scale_color_brewer(palette = "Dark2") +
        labs(x = NULL, y = NULL, color = NULL, title = NULL, subtitle = NULL) +
        theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 8))

    ggsave(file.path(OUTDIR, "F1_serie_temporal_pnadc.pdf"),
           plot = p1, width = 10, height = 7)
    ggsave(file.path(OUTDIR, "F1_serie_temporal_pnadc.png"),
           plot = p1, width = 10, height = 7, dpi = 300)

    cat("F1 OK: figura salva em", file.path(OUTDIR, "F1_serie_temporal_pnadc.pdf"), "\n")
}
