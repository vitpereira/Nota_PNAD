# -------------------------------------------------------------------------
# FA_HJ_freq_defasagem.R (v2 - sem heatmap)
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, ggrepel)

OUT_DIR <- "../output"

# H.1 Frequencia trimestral por etapa - mantido
d <- read_csv("../../3_Indicators/output/AP_H_freq_trim_etapa.csv",
               show_col_types = FALSE) %>%
    filter(etapa %in% c("EF iniciais","EF finais","1o EM","2o EM","3o EM")) %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(x = ano + (trim-0.5)/4,
           etapa = factor(etapa, levels=c("EF iniciais","EF finais",
                                            "1o EM","2o EM","3o EM")))
p <- ggplot(d, aes(x = x, y = freq_rate*100, color = etapa)) +
    geom_line(linewidth = 0.65) +
    geom_point(size = 1.1) +
    scale_x_continuous(breaks = seq(2012, 2025, 1)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    scale_color_brewer(palette = "Set1", name = NULL) +
    labs(x = NULL, y = "% frequenta escola",
          caption = "Por trimestre. Exclui 2020-2021 (COVID).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust=0, size=8, color="gray25"))
ggsave(file.path(OUT_DIR, "FA_H1_freq_trim_etapa.pdf"), p,
        width = 11, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_H1_freq_trim_etapa.png"), p,
        width = 11, height = 5, dpi = 150)

# J.1 (substitui heatmap): line plot com faceting por macroetapa
d <- read_csv("../../3_Indicators/output/AP_J_idade_media_serie.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(serie = factor(serie,
                            levels = c("1o EF","2o EF","3o EF","4o EF","5o EF",
                                        "6o EF","7o EF","8o EF","9o EF",
                                        "1o EM","2o EM","3o EM")),
           nivel = as.integer(serie),
           macroetapa = case_when(
                nivel <= 5 ~ "EF iniciais (1o-5o)",
                nivel <= 9 ~ "EF finais (6o-9o)",
                TRUE ~ "Ensino Médio"
           ),
           idade_padrao = case_when(
                serie == "1o EF" ~ 6,  serie == "2o EF" ~ 7,
                serie == "3o EF" ~ 8,  serie == "4o EF" ~ 9,
                serie == "5o EF" ~ 10, serie == "6o EF" ~ 11,
                serie == "7o EF" ~ 12, serie == "8o EF" ~ 13,
                serie == "9o EF" ~ 14, serie == "1o EM" ~ 15,
                serie == "2o EM" ~ 16, serie == "3o EM" ~ 17),
           defasagem = idade_media - idade_padrao)

cores_serie <- c(
    "1o EF"="#B3E5FC","2o EF"="#81D4FA","3o EF"="#4FC3F7",
    "4o EF"="#29B6F6","5o EF"="#039BE5",
    "6o EF"="#FFE082","7o EF"="#FFCA28","8o EF"="#FFB300","9o EF"="#FF8F00",
    "1o EM"="#EF9A9A","2o EM"="#E57373","3o EM"="#EF5350"
)

# Defasagem (idade - idade padrao) ao longo do tempo
p <- ggplot(d, aes(x = ano, y = defasagem, color = serie, group = serie)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.5) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_color_manual(values = cores_serie, name = NULL) +
    labs(x = NULL,
          y = "Defasagem média (anos acima da idade-padrão)",
          caption = "Diferença entre idade média na série e idade-padrão (e.g., 6 anos para 1o EF). Exclui 2020-2021.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          legend.text = element_text(size = 7),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25")) +
    guides(color = guide_legend(nrow = 2))
ggsave(file.path(OUT_DIR, "FA_J1_defasagem_serie.pdf"), p,
        width = 13, height = 5.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_J1_defasagem_serie.png"), p,
        width = 13, height = 5.5, dpi = 150)

# J.2 ja era line plot, mantido
p <- ggplot(d, aes(x = ano, y = idade_media, color = serie, group = serie)) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.3) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_color_manual(values = cores_serie, name = NULL) +
    labs(x = NULL, y = "Idade média (anos)",
          caption = "Por série e ano (Q2). Maior idade média = mais defasagem.") +
    theme_minimal(base_family = "serif", base_size = 9) +
    theme(legend.position = "bottom",
          legend.text = element_text(size = 7),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust=0, size=8, color="gray25")) +
    guides(color = guide_legend(nrow = 2))
ggsave(file.path(OUT_DIR, "FA_J2_idade_media_serie_linhas.pdf"), p,
        width = 13, height = 5.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_J2_idade_media_serie_linhas.png"), p,
        width = 13, height = 5.5, dpi = 150)

cat("Saved FA_H1, FA_J1 (defasagem), FA_J2 (lines)\n")
