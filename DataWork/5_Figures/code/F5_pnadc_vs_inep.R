# -------------------------------------------------------------------------
# F5_pnadc_vs_inep.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Figura comparando PNADC vs INEP para os indicadores de fluxo escolar
#   (promocao, repetencia, evasao). Brasil, 2012-2021.
#
# Inputs:
#   3_Indicators/output/T1_brasil_inter_por_macroetapa_ano.csv
#   4_INEP_Comparison/output/inep_transicao_long.csv
# -------------------------------------------------------------------------

PNADC_PATH <- file.path(INDIC_OUT, "T1_brasil_inter_por_macroetapa_ano.csv")
INEP_PATH  <- file.path(ROOT, "DataWork", "4_INEP_Comparison", "output",
                        "inep_transicao_long.csv")

if (!file.exists(INEP_PATH)) {
    cat("F5 SKIP: INEP nao parseado\n")
} else if (!file.exists(PNADC_PATH)) {
    cat("F5 SKIP: PNADC nao computado\n")
} else {

    # Carregar PNADC
    df_pnadc <- read_csv(PNADC_PATH, show_col_types = FALSE) %>%
        filter(macroetapa %in% c("EF iniciais", "EF finais", "EM")) %>%
        pivot_longer(cols = c("flag_promocao", "flag_repetencia", "flag_evasao"),
                     names_to = "indicador_raw", values_to = "valor") %>%
        mutate(
            indicador = case_when(
                indicador_raw == "flag_promocao"   ~ "promocao",
                indicador_raw == "flag_repetencia" ~ "repetencia",
                indicador_raw == "flag_evasao"     ~ "evasao"
            ),
            fonte = "PNADC",
            ano = ano_t,
            etapa_pnadc = macroetapa,
            # Converter para % (INEP esta em %, PNADC em fracao)
            valor = valor * 100
        ) %>%
        select(ano, etapa_pnadc, indicador, valor, fonte)
    # Etapa codes ja harmonizados V3003 (pre-2016) <-> V3003A (pos-2016)

    # Carregar INEP (Brasil, indicadores comparaveis)
    df_inep <- read_csv(INEP_PATH, show_col_types = FALSE) %>%
        filter(unidade == "Brasil") %>%
        filter(indicador %in% c("promocao", "repetencia", "evasao")) %>%
        # Mapear etapa INEP para macroetapa PNADC
        mutate(
            etapa_pnadc = case_when(
                etapa == "EF_AI"     ~ "EF iniciais",
                etapa == "EF_AF"     ~ "EF finais",
                etapa == "Total_EM"  ~ "EM",
                TRUE ~ NA_character_
            )
        ) %>%
        filter(!is.na(etapa_pnadc)) %>%
        mutate(fonte = "INEP", ano = ano_t) %>%
        select(ano, etapa_pnadc, indicador, valor, fonte)

    df_all <- bind_rows(df_pnadc, df_inep) %>%
        mutate(
            indicador_lbl = case_when(
                indicador == "promocao"   ~ "Promoção",
                indicador == "repetencia" ~ "Repetência",
                indicador == "evasao"     ~ "Evasão"
            ),
            indicador_lbl = factor(indicador_lbl,
                                  levels = c("Promoção", "Repetência", "Evasão")),
            etapa_pnadc = factor(etapa_pnadc,
                                 levels = c("EF iniciais", "EF finais", "EM"))
        )

    p <- ggplot(df_all, aes(x = ano, y = valor, color = etapa_pnadc, linetype = fonte)) +
        annotate("rect", xmin = 2020, xmax = 2021, ymin = -Inf, ymax = Inf,
                 alpha = 0.15, fill = "grey50") +
        geom_line(linewidth = 0.9) +
        geom_point(size = 1.3) +
        facet_wrap(~indicador_lbl, scales = "free_y", ncol = 3) +
        scale_x_continuous(breaks = seq(2007, 2024, by = 2)) +
        scale_y_continuous(labels = function(x) paste0(x, "%")) +
        scale_color_brewer(palette = "Dark2", name = "Etapa") +
        scale_linetype_manual(values = c("INEP" = "solid", "PNADC" = "dashed"),
                              name = "Fonte") +
        labs(x = NULL, y = NULL, title = NULL) +
        theme(legend.position = "bottom",
              axis.text.x = element_text(angle = 45, hjust = 1))

    ggsave(file.path(OUTDIR, "F5_pnadc_vs_inep.pdf"),
           plot = p, width = 11, height = 5, device = cairo_pdf)
    ggsave(file.path(OUTDIR, "F5_pnadc_vs_inep.png"),
           plot = p, width = 11, height = 5, dpi = 300)

    cat("F5 OK\n")
}
