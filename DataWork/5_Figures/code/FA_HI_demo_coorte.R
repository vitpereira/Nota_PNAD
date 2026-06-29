if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"

# H.2: freq trim por sexo e raca
d <- read_csv("../../3_Indicators/output/AP_H2_freq_demo.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")),
           x = ano + (trim-0.5)/4)

# Por sexo
d_sex <- d %>% filter(categoria == "sexo")
p <- ggplot(d_sex, aes(x = x, y = freq*100,
                          color = valor, group = interaction(valor, macroetapa))) +
    geom_line(linewidth = 0.55) +
    facet_wrap(~macroetapa) +
    scale_color_manual(values = c("Homem"="#1A5276","Mulher"="#922B21"),
                          name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "% frequenta escola",
          caption = "Por trimestre, sexo e macroetapa. Exclui 2020-2021.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_H2a_freq_trim_sexo.pdf"), p,
        width = 12, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_H2a_freq_trim_sexo.png"), p,
        width = 12, height = 4.5, dpi = 150)

# Por raca
d_rac <- d %>% filter(categoria == "raca", valor %in% c("Branca","Preta","Parda"))
p <- ggplot(d_rac, aes(x = x, y = freq*100,
                          color = valor, group = interaction(valor, macroetapa))) +
    geom_line(linewidth = 0.55) +
    facet_wrap(~macroetapa) +
    scale_color_manual(values = c("Branca"="#1A5276","Preta"="#922B21",
                                      "Parda"="#7D6608"), name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "% frequenta escola",
          caption = "Por trimestre, raça/cor e macroetapa. Exclui 2020-2021.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_H2b_freq_trim_raca.pdf"), p,
        width = 12, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_H2b_freq_trim_raca.png"), p,
        width = 12, height = 4.5, dpi = 150)

# I.1: matricula em EM por idade e coorte (ano de nascimento)
d <- read_csv("../../3_Indicators/output/AP_I_em_por_coorte_idade.csv",
               show_col_types = FALSE)
# Plotar para cada idade (15-19), a evolucao por coorte (ano de nascimento)
p <- ggplot(d %>% filter(idade %in% 15:19),
              aes(x = coorte_nascimento, y = em_matr*100,
                   color = factor(idade), group = factor(idade))) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.4) +
    scale_color_brewer(palette = "Set1", name = "Idade na observação") +
    scale_x_continuous(breaks = seq(1994, 2010, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = "Ano de nascimento (coorte)",
          y = "% matriculados em EM regular",
          caption = "Observado em Q2 de 2015, 2017, 2019, 2021, 2023, 2025.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_I1_em_por_coorte.pdf"), p,
        width = 10, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_I1_em_por_coorte.png"), p,
        width = 10, height = 5, dpi = 150)

cat("Saved H2a, H2b, I1\n")
