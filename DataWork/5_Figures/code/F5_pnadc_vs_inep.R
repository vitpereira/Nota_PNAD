# -------------------------------------------------------------------------
# F5_pnadc_vs_inep.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Figura comparando PNADC v5 vs INEP para indicadores de fluxo escolar
#   (promocao, repetencia, evasao). Brasil, 2007-2024.
#
# Inputs:
INPUT_PNADC <- "../../3_Indicators/output/T1_brasil_inter_v5_main.csv"
INPUT_INEP  <- "../../4_INEP_Comparison/output/inep_transicao_long.csv"
#
# Outputs:
OUTPUT_PDF  <- "../output/F5_pnadc_vs_inep.pdf"
OUTPUT_PNG  <- "../output/F5_pnadc_vs_inep.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

# Carregar PNADC v5
df_pnadc <- read_csv(INPUT_PNADC, show_col_types = FALSE) %>%
    filter(macroetapa %in% c("EF iniciais", "EF finais", "EM")) %>%
    pivot_longer(cols = c("flag_promocao", "flag_repetencia", "flag_evasao"),
                  names_to = "indicador_raw", values_to = "valor") %>%
    mutate(
        indicador = case_when(
            indicador_raw == "flag_promocao"   ~ "promocao",
            indicador_raw == "flag_repetencia" ~ "repetencia",
            indicador_raw == "flag_evasao"     ~ "evasao"
        ),
        fonte = "PNADC v5",
        ano = ano_t,
        etapa_pnadc = macroetapa,
        valor = valor * 100
    ) %>%
    select(ano, etapa_pnadc, indicador, valor, fonte)

# Carregar INEP
df_inep <- read_csv(INPUT_INEP, show_col_types = FALSE) %>%
    filter(unidade == "Brasil") %>%
    filter(indicador %in% c("promocao", "repetencia", "evasao")) %>%
    mutate(
        etapa_pnadc = case_when(
            etapa == "EF_AI"    ~ "EF iniciais",
            etapa == "EF_AF"    ~ "EF finais",
            etapa == "Total_EM" ~ "EM",
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
                              levels = c("EF iniciais", "EF finais", "EM")),
        fonte = factor(fonte, levels = c("INEP", "PNADC v5"))
    )

p <- ggplot(df_all, aes(x = ano, y = valor, color = etapa_pnadc,
                            linetype = fonte)) +
    annotate("rect", xmin = 2020, xmax = 2021, ymin = -Inf, ymax = Inf,
              alpha = 0.15, fill = "grey50") +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.3) +
    facet_wrap(~indicador_lbl, scales = "free_y", ncol = 3) +
    scale_x_continuous(breaks = seq(2008, 2024, by = 4)) +
    scale_y_continuous(labels = function(x) paste0(x, "%")) +
    scale_color_manual(values = c("EF iniciais" = "#1A5276",
                                     "EF finais"   = "#7D6608",
                                     "EM"          = "#922B21"),
                        name = "Macroetapa") +
    scale_linetype_manual(values = c("INEP" = "solid", "PNADC v5" = "dashed"),
                            name = "Fonte") +
    labs(x = NULL, y = NULL,
          caption = paste0(
              "Comparação PNADC v5 (Q2-Q3 + max(nivel) + V3014) vs INEP. ",
              "Faixa cinza: anos COVID 2020-2021."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8.5, color = "gray25"))

ggsave(OUTPUT_PDF, p, width = 11, height = 5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 11, height = 5, dpi = 200)
cat("Saved F5\n")
