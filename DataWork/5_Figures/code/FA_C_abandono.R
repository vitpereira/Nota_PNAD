# -------------------------------------------------------------------------
# FA_C_abandono.R (v2 - sem heatmap)
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, ggrepel)

OUT_DIR <- "../output"
d <- read_csv("../../3_Indicators/output/AP_C_abandono_por_serie.csv",
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
           ))

cores_serie <- c(
    "1o EF"="#B3E5FC","2o EF"="#81D4FA","3o EF"="#4FC3F7",
    "4o EF"="#29B6F6","5o EF"="#039BE5",
    "6o EF"="#FFE082","7o EF"="#FFCA28","8o EF"="#FFB300","9o EF"="#FF8F00",
    "1o EM"="#EF9A9A","2o EM"="#E57373","3o EM"="#EF5350"
)

# FA_C1: faceted lineplot por macroetapa
p <- ggplot(d, aes(x = ano, y = flag_abandono*100,
                      color = serie, group = serie)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.5) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_color_manual(values = cores_serie, name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "Abandono intra-ano (%)",
          caption = "Por série e ano (PNADC). Exclui 2020-2021 (COVID).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          legend.text = element_text(size = 7),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25")) +
    guides(color = guide_legend(nrow = 2))
ggsave(file.path(OUT_DIR, "FA_C1_abandono_serie.pdf"), p,
        width = 13, height = 5.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_C1_abandono_serie.png"), p,
        width = 13, height = 5.5, dpi = 150)

# FA_C2: dot plot ordenado (media 2017-2019 e media 2022-2024)
d_avg <- d %>%
    mutate(periodo = case_when(
                ano %in% c(2017, 2018, 2019) ~ "2017-2019",
                ano %in% c(2022, 2023, 2024) ~ "2022-2024",
                TRUE ~ NA_character_)) %>%
    filter(!is.na(periodo)) %>%
    group_by(serie, macroetapa, periodo) %>%
    summarise(abandono = mean(flag_abandono)*100, .groups = "drop")

p <- ggplot(d_avg, aes(x = abandono, y = fct_rev(serie),
                          color = periodo, shape = periodo)) +
    geom_line(aes(group = serie), color = "gray60",
                linewidth = 0.6) +
    geom_point(size = 3) +
    scale_color_manual(values = c("2017-2019" = "#5DADE2",
                                      "2022-2024" = "#922B21"),
                          name = NULL) +
    scale_shape_manual(values = c("2017-2019" = 16, "2022-2024" = 17),
                          name = NULL) +
    scale_x_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = "Abandono intra-ano médio (%)", y = NULL,
          caption = "Comparação média 2017-2019 (pré-pandemia) vs 2022-2024 (pós).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_C2_abandono_dot_periodo.pdf"), p,
        width = 9, height = 6, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_C2_abandono_dot_periodo.png"), p,
        width = 9, height = 6, dpi = 150)

cat("Saved FA_C1 (facet lines), FA_C2 (dot)\n")
