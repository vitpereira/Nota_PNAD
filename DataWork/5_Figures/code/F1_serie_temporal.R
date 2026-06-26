# -------------------------------------------------------------------------
# F1_serie_temporal.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Serie temporal 2012-2024 dos 4 indicadores inter-anuais, por macroetapa.
#   Usa T1 v5 (Q2-Q3 + V3014 + tecnico).
#
# Outputs:
#   ../output/F1_serie_temporal_pnadc.pdf
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

INPUT <- "../../3_Indicators/output/T1_brasil_inter_v5_main.csv"

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    filter(macroetapa %in% c("EF iniciais", "EF finais", "EM")) %>%
    # Excluir 2020 e 2021 (paradoxo COVID auto-relato vs administrativo)
    filter(!ano_t %in% c(2020, 2021)) %>%
    select(ano_t, macroetapa, flag_promocao, flag_repetencia,
            flag_evasao, flag_migracao_eja) %>%
    pivot_longer(c(flag_promocao, flag_repetencia, flag_evasao,
                    flag_migracao_eja),
                  names_to = "indicador", values_to = "valor") %>%
    mutate(
        indicador = case_when(
            indicador == "flag_promocao"      ~ "Promoção",
            indicador == "flag_repetencia"    ~ "Repetência",
            indicador == "flag_evasao"        ~ "Evasão",
            indicador == "flag_migracao_eja"  ~ "Migração EJA",
        ),
        indicador = factor(indicador,
                            levels = c("Promoção", "Repetência",
                                       "Evasão", "Migração EJA")),
        macroetapa = factor(macroetapa,
                              levels = c("EF iniciais", "EF finais", "EM"))
    )

p <- ggplot(df, aes(x = ano_t, y = valor, color = macroetapa,
                       group = macroetapa)) +
    annotate("rect", xmin = 2019.5, xmax = 2021.5, ymin = -Inf, ymax = Inf,
              alpha = 0.18, fill = "grey50") +
    annotate("text", x = 2020.5, y = 0.05, label = "COVID\nexcluído",
              size = 2.8, family = "serif", color = "gray30") +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.3) +
    facet_wrap(~ indicador, scales = "free_y", ncol = 2) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = percent_format(accuracy = 1)) +
    scale_color_manual(values = c("EF iniciais" = "#1A5276",
                                     "EF finais"   = "#7D6608",
                                     "EM"          = "#922B21"),
                        name = NULL) +
    labs(x = NULL, y = NULL,
          caption = "Painel longitudinal PNADC v5 (Q2-Q3 + max(nivel) + V3014 + tecnico). Faixa cinza: COVID 2020-2021.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8.5, color = "gray25"))

ggsave("../output/F1_serie_temporal_pnadc.pdf", p,
        width = 9, height = 6.5, device = cairo_pdf)
ggsave("../output/F1_serie_temporal_pnadc.png", p,
        width = 9, height = 6.5, dpi = 200)
cat("Saved F1\n")
