# -------------------------------------------------------------------------
# FA_T_transicao.R
# -------------------------------------------------------------------------
# Description:
#   Figuras alternativas para transicao e abandono.
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"

# FA_T1: matriz de transicao - stacked bar por serie
d <- read_csv("../../3_Indicators/output/AP_T1_matriz_transicao.csv",
               show_col_types = FALSE) %>%
    mutate(serie = factor(serie,
                            levels = c("1o EF","2o EF","3o EF","4o EF","5o EF",
                                        "6o EF","7o EF","8o EF","9o EF",
                                        "1o EM","2o EM","3o EM","4o EM tec")),
           destino = factor(destino,
                              levels = c("Promoção","Repetência",
                                          "Migração EJA","Evasão","Outro")))

p <- ggplot(d, aes(x = serie, y = share*100, fill = destino)) +
    geom_col(width = 0.7) +
    scale_fill_manual(values = c("Promoção"="#27AE60",
                                     "Repetência"="#F39C12",
                                     "Migração EJA"="#3498DB",
                                     "Evasão"="#922B21",
                                     "Outro"="gray70"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%"),
                        expand = expansion(0)) +
    labs(x = NULL, y = "% dos alunos em cada destino em t+1",
          caption = "Média 2012-2024 da transição entre-anos por série inicial. Painel PNADC v5.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_T1_matriz_transicao_stacked.pdf"), p,
        width = 11, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_T1_matriz_transicao_stacked.png"), p,
        width = 11, height = 5, dpi = 150)

# FA_T2: probabilidade de destino por sexo e raca, por macroetapa
d <- read_csv("../../3_Indicators/output/AP_T2_destino_por_demo.csv",
               show_col_types = FALSE) %>%
    pivot_longer(cols = c(prom, rep, evas, eja),
                  names_to = "destino", values_to = "share") %>%
    mutate(destino = factor(case_when(
                destino == "prom" ~ "Promoção",
                destino == "rep"  ~ "Repetência",
                destino == "evas" ~ "Evasão",
                destino == "eja"  ~ "Migração EJA"),
              levels = c("Promoção","Repetência","Migração EJA","Evasão")),
           macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")))

# Por raca
d_rac <- d %>% filter(categoria == "raca")
p <- ggplot(d_rac, aes(x = valor, y = share*100, fill = destino)) +
    geom_col(width = 0.7, position = position_stack()) +
    facet_wrap(~macroetapa, ncol = 3) +
    scale_fill_manual(values = c("Promoção"="#27AE60",
                                     "Repetência"="#F39C12",
                                     "Migração EJA"="#3498DB",
                                     "Evasão"="#922B21"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%"),
                        expand = expansion(0)) +
    labs(x = NULL, y = "% em cada destino",
          caption = "Destino na transição t -> t+1 por raça/cor (média do período PNADC v5).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_T2a_destino_por_raca.pdf"), p,
        width = 10, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_T2a_destino_por_raca.png"), p,
        width = 10, height = 5, dpi = 150)

# Por sexo
d_sex <- d %>% filter(categoria == "sexo")
p <- ggplot(d_sex, aes(x = valor, y = share*100, fill = destino)) +
    geom_col(width = 0.7, position = position_stack()) +
    facet_wrap(~macroetapa, ncol = 3) +
    scale_fill_manual(values = c("Promoção"="#27AE60",
                                     "Repetência"="#F39C12",
                                     "Migração EJA"="#3498DB",
                                     "Evasão"="#922B21"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%"),
                        expand = expansion(0)) +
    labs(x = NULL, y = "% em cada destino",
          caption = "Destino na transição t -> t+1 por sexo.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_T2b_destino_por_sexo.pdf"), p,
        width = 10, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_T2b_destino_por_sexo.png"), p,
        width = 10, height = 5, dpi = 150)

# FA_T3: probabilidade de cada destino por idade, no EM
d <- read_csv("../../3_Indicators/output/AP_T3_destino_por_idade.csv",
               show_col_types = FALSE) %>%
    pivot_longer(cols = c(prom, rep, evas),
                  names_to = "destino", values_to = "share") %>%
    mutate(destino = factor(case_when(
                destino == "prom" ~ "Promoção",
                destino == "rep"  ~ "Repetência",
                destino == "evas" ~ "Evasão"),
              levels = c("Promoção","Repetência","Evasão")),
           macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM"))) %>%
    filter(idade <= 24)
p <- ggplot(d, aes(x = idade, y = share*100, color = destino)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.4) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_color_manual(values = c("Promoção"="#27AE60",
                                      "Repetência"="#F39C12",
                                      "Evasão"="#922B21"), name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    scale_x_continuous(breaks = seq(6, 24, 3)) +
    labs(x = "Idade no início da transição", y = "% em cada destino",
          caption = "Probabilidade de cada destino (t -> t+1) por idade no inicio da transicao.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_T3_destino_por_idade.pdf"), p,
        width = 12, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_T3_destino_por_idade.png"), p,
        width = 12, height = 4.5, dpi = 150)

# FA_T4: trajetoria temporal de cada destino por macroetapa
d <- read_csv("../../3_Indicators/output/AP_T4_trajetoria_temporal.csv",
               show_col_types = FALSE) %>%
    pivot_longer(cols = c(prom, rep, evas, eja),
                  names_to = "destino", values_to = "share") %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(destino = factor(case_when(
                destino == "prom" ~ "Promoção",
                destino == "rep"  ~ "Repetência",
                destino == "evas" ~ "Evasão",
                destino == "eja"  ~ "Migração EJA"),
              levels = c("Promoção","Repetência","Evasão","Migração EJA")),
           macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")))
p <- ggplot(d, aes(x = ano, y = share*100, color = destino)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.4) +
    facet_wrap(~macroetapa, scales = "free_y") +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_color_manual(values = c("Promoção"="#27AE60",
                                      "Repetência"="#F39C12",
                                      "Evasão"="#922B21",
                                      "Migração EJA"="#3498DB"),
                          name = NULL) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "% em cada destino",
          caption = "Probabilidade de cada destino (t -> t+1) ao longo dos anos. Exclui 2020-2021.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_T4_trajetoria_temporal.pdf"), p,
        width = 12, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_T4_trajetoria_temporal.png"), p,
        width = 12, height = 5, dpi = 150)

cat("Saved FA_T1 a T4\n")
