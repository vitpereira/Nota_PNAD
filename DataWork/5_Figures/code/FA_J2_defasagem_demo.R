if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"
d <- read_csv("../../3_Indicators/output/AP_J2_defasagem_demo.csv",
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

# FA_J3a: defasagem por sexo (media 2017-2024) - barras por serie
d_sex <- d %>%
    filter(categoria == "sexo", ano %in% 2017:2024) %>%
    group_by(serie, macroetapa, valor) %>%
    summarise(defasado = mean(defasado), .groups = "drop")
p <- ggplot(d_sex, aes(x = serie, y = defasado*100, fill = valor)) +
    geom_col(width = 0.7, position = position_dodge()) +
    facet_wrap(~macroetapa, scales = "free_x", nrow = 1) +
    scale_fill_manual(values = c("Homem"="#1A5276","Mulher"="#922B21"),
                         name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "% defasados (idade ≥ padrão + 2)",
          caption = "Por série e sexo. Média 2017-2024.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_J3a_defasagem_sexo.pdf"), p,
        width = 12, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_J3a_defasagem_sexo.png"), p,
        width = 12, height = 5, dpi = 150)

# FA_J3b: defasagem por raca
d_rac <- d %>%
    filter(categoria == "raca", valor %in% c("Branca","Preta","Parda"),
           ano %in% 2017:2024) %>%
    group_by(serie, macroetapa, valor) %>%
    summarise(defasado = mean(defasado), .groups = "drop")
p <- ggplot(d_rac, aes(x = serie, y = defasado*100, fill = valor)) +
    geom_col(width = 0.7, position = position_dodge()) +
    facet_wrap(~macroetapa, scales = "free_x", nrow = 1) +
    scale_fill_manual(values = c("Branca"="#1A5276","Preta"="#922B21",
                                     "Parda"="#7D6608"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "% defasados",
          caption = "Por série e raça/cor. Média 2017-2024.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_J3b_defasagem_raca.pdf"), p,
        width = 12, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_J3b_defasagem_raca.png"), p,
        width = 12, height = 5, dpi = 150)

# FA_J4: defasagem ao longo do tempo, total por serie
d_tot <- d %>%
    filter(categoria == "sexo") %>%
    group_by(serie, ano, macroetapa) %>%
    summarise(defasado = sum(defasado * n) / sum(n), .groups = "drop")
cores_serie <- c(
    "1o EF"="#B3E5FC","2o EF"="#81D4FA","3o EF"="#4FC3F7",
    "4o EF"="#29B6F6","5o EF"="#039BE5",
    "6o EF"="#FFE082","7o EF"="#FFCA28","8o EF"="#FFB300","9o EF"="#FF8F00",
    "1o EM"="#EF9A9A","2o EM"="#E57373","3o EM"="#EF5350"
)
p <- ggplot(d_tot, aes(x = ano, y = defasado*100,
                          color = serie, group = serie)) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.2) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_color_manual(values = cores_serie, name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "% defasados",
          caption = "Defasagem por série e ano (exclui 2020-2021).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          legend.text = element_text(size = 7),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25")) +
    guides(color = guide_legend(nrow = 2))
ggsave(file.path(OUT_DIR, "FA_J4_defasagem_evol.pdf"), p,
        width = 13, height = 5.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_J4_defasagem_evol.png"), p,
        width = 13, height = 5.5, dpi = 150)

cat("Saved FA_J3a, J3b, J4\n")
