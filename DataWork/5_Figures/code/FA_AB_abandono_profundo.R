if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"

# FA_AB1: abandono por idade x macroetapa
d <- read_csv("../../3_Indicators/output/AP_AB1_abandono_por_idade.csv",
               show_col_types = FALSE) %>%
    filter(idade <= 24) %>%
    mutate(macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")))
p <- ggplot(d, aes(x = idade, y = abandono*100, color = macroetapa,
                       group = macroetapa)) +
    geom_line(linewidth = 0.85) +
    geom_point(size = 1.8) +
    scale_color_manual(values = c("EF iniciais"="#1A5276",
                                      "EF finais"="#7D6608",
                                      "EM"="#922B21"), name = NULL) +
    scale_x_continuous(breaks = seq(6, 24, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = "Idade", y = "Probabilidade de abandono intra-ano",
          caption = "Idade no Q1 do ano. Pooled 2012-2024 (exclui 2020-2021).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_AB1_abandono_por_idade.pdf"), p,
        width = 10, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_AB1_abandono_por_idade.png"), p,
        width = 10, height = 5, dpi = 150)

# FA_AB2: abandono por raca e sexo, ao longo dos anos
d <- read_csv("../../3_Indicators/output/AP_AB2_abandono_por_demo.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")))

# Por raca
d_rac <- d %>% filter(categoria == "raca",
                       valor %in% c("Branca","Preta","Parda"))
p <- ggplot(d_rac, aes(x = ano, y = abandono*100,
                          color = valor, group = valor)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.6) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_color_manual(values = c("Branca"="#1A5276","Preta"="#922B21",
                                      "Parda"="#7D6608"), name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "Abandono intra-ano",
          caption = "Por raça/cor e macroetapa.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_AB2a_abandono_por_raca.pdf"), p,
        width = 12, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_AB2a_abandono_por_raca.png"), p,
        width = 12, height = 4.5, dpi = 150)

# Por sexo
d_sex <- d %>% filter(categoria == "sexo")
p <- ggplot(d_sex, aes(x = ano, y = abandono*100,
                          color = valor, group = valor)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.6) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_color_manual(values = c("Homem"="#1A5276","Mulher"="#922B21"),
                          name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "Abandono intra-ano",
          caption = "Por sexo e macroetapa.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_AB2b_abandono_por_sexo.pdf"), p,
        width = 12, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_AB2b_abandono_por_sexo.png"), p,
        width = 12, height = 4.5, dpi = 150)

# FA_AB4: idade media abandonados vs retidos
d <- read_csv("../../3_Indicators/output/AP_AB4_idade_abandono.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM"))) %>%
    pivot_longer(c(idade_media_abandonados, idade_media_retidos),
                  names_to = "tipo", values_to = "idade") %>%
    mutate(tipo = ifelse(tipo == "idade_media_abandonados",
                            "Abandonaram", "Retidos"))
p <- ggplot(d, aes(x = ano, y = idade, color = tipo, group = tipo)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.6) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_color_manual(values = c("Abandonaram"="#922B21",
                                      "Retidos"="#1A5276"), name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    labs(x = NULL, y = "Idade média (anos)",
          caption = "Idade média dos que abandonaram intra-ano vs dos que persistiram, por macroetapa.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_AB4_idade_ab_vs_retidos.pdf"), p,
        width = 12, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_AB4_idade_ab_vs_retidos.png"), p,
        width = 12, height = 4.5, dpi = 150)

cat("Saved FA_AB1, AB2a, AB2b, AB4\n")
