# -------------------------------------------------------------------------
# F12_evasao_pnadc_vs_inep.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Figura exclusiva comparando EVASÃO PNADC v5 vs INEP, por macroetapa,
#   Brasil 2007-2024. Excluindo 2020-2021 (paradoxo COVID).
#
#   Motivação: evasão é o indicador que melhor concorda entre as duas
#   fontes (em contraste com promoção e repetência onde há divergência
#   pós-2020). Esse gráfico documenta a concordância.
#
# Inputs:
INPUT_PNADC <- "../../3_Indicators/output/T1_brasil_inter_v5_main.csv"
INPUT_INEP  <- "../../4_INEP_Comparison/output/inep_transicao_long.csv"
#
# Outputs:
OUTPUT_PDF  <- "../output/F12_evasao_pnadc_vs_inep.pdf"
OUTPUT_PNG  <- "../output/F12_evasao_pnadc_vs_inep.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

# { Carregar PNADC v5 ----
df_pnadc <- read_csv(INPUT_PNADC, show_col_types = FALSE) %>%
    filter(macroetapa %in% c("EF iniciais", "EF finais", "EM")) %>%
    filter(!ano_t %in% c(2020, 2021)) %>%
    mutate(
        fonte = "PNADC v5",
        ano = ano_t,
        etapa_pnadc = macroetapa,
        valor = flag_evasao * 100
    ) %>%
    select(ano, etapa_pnadc, valor, fonte)
# } ----

# { Carregar INEP ----
df_inep <- read_csv(INPUT_INEP, show_col_types = FALSE) %>%
    filter(unidade == "Brasil") %>%
    filter(indicador == "evasao") %>%
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
    select(ano, etapa_pnadc, valor, fonte)
# } ----

# { Combinar e plotar ----
df_all <- bind_rows(df_pnadc, df_inep) %>%
    mutate(
        etapa_pnadc = factor(etapa_pnadc,
                              levels = c("EF iniciais", "EF finais", "EM")),
        fonte = factor(fonte, levels = c("INEP", "PNADC v5"))
    )

p <- ggplot(df_all, aes(x = ano, y = valor, color = fonte,
                            linetype = fonte, shape = fonte)) +
    annotate("rect", xmin = 2019.5, xmax = 2021.5, ymin = -Inf, ymax = Inf,
              alpha = 0.15, fill = "grey50") +
    annotate("text", x = 2020.5, y = Inf, label = "COVID",
              vjust = 1.6, size = 2.7, family = "serif", color = "gray35") +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.6) +
    facet_wrap(~etapa_pnadc, scales = "free_y", ncol = 3) +
    scale_x_continuous(breaks = seq(2008, 2024, by = 4)) +
    scale_y_continuous(labels = function(x) paste0(x, "%")) +
    scale_color_manual(values = c("INEP" = "#1A5276", "PNADC v5" = "#922B21"),
                        name = NULL) +
    scale_linetype_manual(values = c("INEP" = "solid", "PNADC v5" = "dashed"),
                            name = NULL) +
    scale_shape_manual(values = c("INEP" = 16, "PNADC v5" = 17),
                        name = NULL) +
    labs(x = NULL, y = NULL,
          caption = paste0(
              "Evasão entre-anos: aluno matriculado em t e não-matriculado em t+1. ",
              "Faixa cinza: anos COVID 2020-2021 (omitidos da PNADC v5)."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8.5, color = "gray25"))

ggsave(OUTPUT_PDF, p, width = 10, height = 4.5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 10, height = 4.5, dpi = 200)
cat("Saved F12\n")
# } ----
