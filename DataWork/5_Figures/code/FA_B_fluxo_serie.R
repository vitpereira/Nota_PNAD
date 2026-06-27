# -------------------------------------------------------------------------
# FA_B_fluxo_serie.R (versao 2 - sem heatmaps)
# -------------------------------------------------------------------------
# Description:
#   Visualizacoes alternativas das taxas de fluxo por serie x ano.
#   Substitui heatmaps por:
#   - Slope graphs (2019 vs 2024) por serie
#   - Faceted line plots por macroetapa
#   - Cleveland dot plots ordenados
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, ggrepel)

OUT_DIR <- "../output"
d <- read_csv("../../3_Indicators/output/AP_B_fluxo_por_serie_ano.csv",
               show_col_types = FALSE) %>%
    filter(!(ano_t %in% c(2020, 2021))) %>%
    mutate(serie = factor(serie,
                            levels = c("1o EF","2o EF","3o EF","4o EF","5o EF",
                                        "6o EF","7o EF","8o EF","9o EF",
                                        "1o EM","2o EM","3o EM","4o EM tec")),
           macroetapa = case_when(
                str_detect(as.character(serie), "EF") &
                  !str_detect(as.character(serie), "EM") &
                  as.integer(serie) <= 5 ~ "EF iniciais (1o-5o)",
                str_detect(as.character(serie), "EF") &
                  as.integer(serie) >= 6 ~ "EF finais (6o-9o)",
                TRUE ~ "Ensino Médio"
           ))

# Cores por serie (escalonando por nivel)
cores_serie <- c(
    "1o EF"="#B3E5FC","2o EF"="#81D4FA","3o EF"="#4FC3F7",
    "4o EF"="#29B6F6","5o EF"="#039BE5",
    "6o EF"="#FFE082","7o EF"="#FFCA28","8o EF"="#FFB300","9o EF"="#FF8F00",
    "1o EM"="#EF9A9A","2o EM"="#E57373","3o EM"="#EF5350","4o EM tec"="#C62828"
)

# {{ Helper: faceted lineplot por macroetapa
mk_facet_line <- function(varname, label_str, fname,
                            ymin = 0, ymax = NA) {
    p <- ggplot(d, aes(x = ano_t, y = .data[[varname]]*100,
                          color = serie, group = serie)) +
        geom_line(linewidth = 0.8) +
        geom_point(size = 1.5) +
        facet_wrap(~macroetapa, scales = "free_y") +
        scale_color_manual(values = cores_serie, name = NULL) +
        scale_x_continuous(breaks = seq(2012, 2024, 2)) +
        scale_y_continuous(labels = function(x) paste0(x,"%")) +
        labs(x = NULL, y = paste0(label_str, " (%)"),
              caption = "Por série e ano (PNADC v5). Exclui 2020-2021 (COVID).") +
        theme_minimal(base_family = "serif", base_size = 10) +
        theme(legend.position = "bottom",
              legend.text = element_text(size = 7),
              panel.grid.minor = element_blank(),
              strip.text = element_text(face = "bold"),
              axis.text.x = element_text(angle = 45, hjust = 1),
              plot.caption = element_text(hjust = 0, size = 8, color = "gray25")) +
        guides(color = guide_legend(nrow = 2))
    if (!is.na(ymax)) p <- p + coord_cartesian(ylim = c(ymin, ymax))
    ggsave(file.path(OUT_DIR, paste0(fname, ".pdf")), p,
            width = 13, height = 5.5, device = cairo_pdf)
    ggsave(file.path(OUT_DIR, paste0(fname, ".png")), p,
            width = 13, height = 5.5, dpi = 150)
}

# }}

mk_facet_line("flag_promocao",      "Promoção",     "FA_B1_promocao_serie")
mk_facet_line("flag_repetencia",    "Repetência",   "FA_B2_repetencia_serie")
mk_facet_line("flag_evasao",        "Evasão",       "FA_B3_evasao_serie")
mk_facet_line("flag_migracao_eja",  "Migração EJA", "FA_B4_migeja_serie")

# {{ Slope graph: comparar 2019 (pre-COVID) com 2023 (recente)
mk_slope <- function(varname, label_str, fname) {
    ds <- d %>%
        filter(ano_t %in% c(2019, 2023)) %>%
        select(serie, ano_t, valor = all_of(varname), macroetapa) %>%
        mutate(valor = valor * 100,
                ano_t = factor(ano_t, levels = c("2019","2023")))
    p <- ggplot(ds, aes(x = ano_t, y = valor, group = serie, color = serie)) +
        geom_line(linewidth = 0.9) +
        geom_point(size = 2.5) +
        geom_text_repel(data = filter(ds, ano_t == "2019"),
                          aes(label = serie), hjust = 1.1, size = 2.6,
                          family = "serif", direction = "y",
                          segment.size = 0.2, nudge_x = -0.05) +
        geom_text_repel(data = filter(ds, ano_t == "2023"),
                          aes(label = sprintf("%.1f%%", valor)), hjust = -0.3,
                          size = 2.5, family = "serif",
                          segment.size = 0.2, nudge_x = 0.05) +
        facet_wrap(~macroetapa, ncol = 3, scales = "free_y") +
        scale_color_manual(values = cores_serie, guide = "none") +
        scale_y_continuous(labels = function(x) paste0(x,"%")) +
        labs(x = NULL, y = paste0(label_str, " (%)"),
              caption = "Comparação 2019 (pré-COVID) vs 2023.") +
        theme_minimal(base_family = "serif", base_size = 10) +
        theme(panel.grid.minor = element_blank(),
              strip.text = element_text(face = "bold"),
              plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
    ggsave(file.path(OUT_DIR, paste0(fname, ".pdf")), p,
            width = 13, height = 5.5, device = cairo_pdf)
    ggsave(file.path(OUT_DIR, paste0(fname, ".png")), p,
            width = 13, height = 5.5, dpi = 150)
}

mk_slope("flag_promocao",      "Promoção",     "FA_B1b_promocao_slope")
mk_slope("flag_repetencia",    "Repetência",   "FA_B2b_repetencia_slope")
mk_slope("flag_evasao",        "Evasão",       "FA_B3b_evasao_slope")
mk_slope("flag_migracao_eja",  "Migração EJA", "FA_B4b_migeja_slope")

cat("Saved FA_B (lines + slopes)\n")
