if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"

# X1: perfil dos abandonados (composicao)
d <- read_csv("../../3_Indicators/output/AP_X1_perfil_abandono.csv",
               show_col_types = FALSE) %>%
    filter(str_detect(metric, "share_")) %>%
    mutate(grupo = str_remove(metric, "share_"),
           macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM"))) %>%
    pivot_longer(c(pop_geral, abandonados),
                  names_to = "tipo", values_to = "share") %>%
    mutate(tipo = ifelse(tipo == "pop_geral", "População Q1", "Abandonados Q4"))

# Filtrar so sexo
d_sex <- d %>% filter(grupo %in% c("Homem","Mulher"))
p <- ggplot(d_sex, aes(x = grupo, y = share*100, fill = tipo)) +
    geom_col(width = 0.7, position = position_dodge()) +
    facet_wrap(~macroetapa) +
    scale_fill_manual(values = c("População Q1"="gray70",
                                     "Abandonados Q4"="#922B21"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%"),
                        expand = expansion(0)) +
    labs(x = NULL, y = "% da população",
          caption = "Composição da pop. enrolada (Q1) vs. dos abandonados (Q4) por sexo.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_X1a_perfil_sexo.pdf"), p,
        width = 10, height = 4, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_X1a_perfil_sexo.png"), p,
        width = 10, height = 4, dpi = 150)

# Por raca
d_rac <- d %>% filter(grupo %in% c("Branca","Preta","Parda"))
p <- ggplot(d_rac, aes(x = grupo, y = share*100, fill = tipo)) +
    geom_col(width = 0.7, position = position_dodge()) +
    facet_wrap(~macroetapa) +
    scale_fill_manual(values = c("População Q1"="gray70",
                                     "Abandonados Q4"="#922B21"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%"),
                        expand = expansion(0)) +
    labs(x = NULL, y = "% da população",
          caption = "Composição da pop. enrolada (Q1) vs. dos abandonados (Q4) por raça/cor.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_X1b_perfil_raca.pdf"), p,
        width = 10, height = 4, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_X1b_perfil_raca.png"), p,
        width = 10, height = 4, dpi = 150)

# X4: promocao por raca x quintil (interacao)
d <- read_csv("../../3_Indicators/output/AP_X4_prom_raca_quintil.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021)),
            macroetapa %in% c("EF iniciais","EF finais","EM")) %>%
    mutate(macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")),
           quintil = factor(quintil,
              levels = c("Q1 (pobre)","Q2-Q4","Q5 (rico)")),
           raca = factor(raca, levels = c("Branca","Preta","Parda")))

# Promocao media 2017-2024 por raca x quintil x macroetapa
d_avg <- d %>%
    filter(ano %in% 2017:2024) %>%
    group_by(macroetapa, raca, quintil) %>%
    summarise(prom = mean(prom), evas = mean(evas), .groups = "drop")

p <- ggplot(d_avg, aes(x = quintil, y = prom*100, fill = raca)) +
    geom_col(width = 0.7, position = position_dodge()) +
    facet_wrap(~macroetapa) +
    scale_fill_manual(values = c("Branca"="#1A5276","Preta"="#922B21",
                                     "Parda"="#7D6608"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "Promoção (%)",
          caption = "Interação raça x quintil de renda na taxa de promoção. Média 2017-2024.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 25, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_X4_prom_raca_quintil.pdf"), p,
        width = 11, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_X4_prom_raca_quintil.png"), p,
        width = 11, height = 4.5, dpi = 150)

# X4b: evasao por raca x quintil
p <- ggplot(d_avg, aes(x = quintil, y = evas*100, fill = raca)) +
    geom_col(width = 0.7, position = position_dodge()) +
    facet_wrap(~macroetapa) +
    scale_fill_manual(values = c("Branca"="#1A5276","Preta"="#922B21",
                                     "Parda"="#7D6608"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "Evasão (%)",
          caption = "Interação raça x quintil de renda na taxa de evasão. Média 2017-2024.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 25, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_X4b_evas_raca_quintil.pdf"), p,
        width = 11, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_X4b_evas_raca_quintil.png"), p,
        width = 11, height = 4.5, dpi = 150)

cat("Saved FA_X1a, X1b, X4, X4b\n")
