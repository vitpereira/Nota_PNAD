# -------------------------------------------------------------------------
# FA_HJ_freq_defasagem.R
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"

# H.1 Frequencia trimestral por etapa (Brasil, todos anos)
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
          caption = "Por trimestre, exclui 2020-2021 (COVID). Painel linkado.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust=0, size=8, color="gray25"))
ggsave(file.path(OUT_DIR, "FA_H1_freq_trim_etapa.pdf"), p,
        width = 11, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_H1_freq_trim_etapa.png"), p,
        width = 11, height = 5, dpi = 150)

# J.1 Idade media por serie e ano (heatmap)
d <- read_csv("../../3_Indicators/output/AP_J_idade_media_serie.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(serie = factor(serie,
                            levels = c("1o EF","2o EF","3o EF","4o EF","5o EF",
                                        "6o EF","7o EF","8o EF","9o EF",
                                        "1o EM","2o EM","3o EM")))
p <- ggplot(d, aes(x = ano, y = serie, fill = idade_media)) +
    geom_tile() +
    geom_text(aes(label = sprintf("%.1f", idade_media)),
               size = 2.1, family = "serif", color = "white") +
    scale_x_continuous(breaks = sort(unique(d$ano))) +
    scale_fill_viridis_c(option = "magma", name = "Idade média",
                          direction = -1) +
    labs(x = NULL, y = NULL,
          caption = "Idade média (anos) por série e ano civil (PNADC Q2).") +
    theme_minimal(base_family = "serif", base_size = 9) +
    theme(panel.grid = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust=0, size=8, color="gray25"))
ggsave(file.path(OUT_DIR, "FA_J1_idade_media_serie.pdf"), p,
        width = 10, height = 6, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_J1_idade_media_serie.png"), p,
        width = 10, height = 6, dpi = 150)

# J.2 Idade media por serie — series temporais (linhas)
p <- ggplot(d, aes(x = ano, y = idade_media, color = serie, group = serie)) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.3) +
    scale_x_continuous(breaks = seq(2012, 2025, 1)) +
    labs(x = NULL, y = "Idade média (anos)", color = NULL,
          caption = "Por série e ano. Maior idade média = mais defasagem.") +
    theme_minimal(base_family = "serif", base_size = 9) +
    theme(legend.position = "bottom",
          legend.text = element_text(size = 7),
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust=0, size=8, color="gray25"))
ggsave(file.path(OUT_DIR, "FA_J2_idade_media_serie_linhas.pdf"), p,
        width = 11, height = 5.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_J2_idade_media_serie_linhas.png"), p,
        width = 11, height = 5.5, dpi = 150)

cat("Saved FA_H1, FA_J1, FA_J2\n")
