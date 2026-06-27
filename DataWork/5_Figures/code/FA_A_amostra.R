# -------------------------------------------------------------------------
# FA_A_amostra.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-27
#
# Description:
#   Figuras para a secao A do apendice (caracterizacao da amostra):
#     FA_A1: tamanho amostral por ano
#     FA_A2: distribuicao de idade por ano (heatmap)
#     FA_A3: composicao por sexo e raca por ano
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"
IN_DIR  <- "../../3_Indicators/output"

# { FA_A1: tamanho amostral ----
d <- read_csv(file.path(IN_DIR, "AP_A1_amostra_por_ano.csv"),
              show_col_types = FALSE)
p <- ggplot(d, aes(x = ano)) +
    geom_col(aes(y = n_obs/1000), fill = "#2874A6", alpha = 0.75) +
    geom_text(aes(y = n_obs/1000,
                    label = sprintf("%.0fk", n_obs/1000)),
              vjust = -0.4, size = 2.8, family = "serif") +
    scale_x_continuous(breaks = 2012:2025) +
    scale_y_continuous(labels = function(x) paste0(x, "k")) +
    labs(x = NULL,
          y = "Observações pessoa-trimestre (mil)",
          caption = "Universo: 4-24 anos, todos os trimestres do ano (PNADC).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_A1_amostra_por_ano.pdf"), p,
        width = 9, height = 4, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_A1_amostra_por_ano.png"), p,
        width = 9, height = 4, dpi = 150)
# } ----

# { FA_A2: distribuicao de idade por ano (heatmap) ----
d <- read_csv(file.path(IN_DIR, "AP_A2_idade_por_ano.csv"),
              show_col_types = FALSE)
p <- ggplot(d, aes(x = ano, y = idade, fill = share * 100)) +
    geom_tile() +
    geom_text(aes(label = sprintf("%.1f", share*100)),
              size = 2.0, family = "serif",
              color = "white") +
    scale_x_continuous(breaks = 2012:2025) +
    scale_y_continuous(breaks = 4:24) +
    scale_fill_viridis_c(option = "magma", name = "% pop.",
                          labels = function(x) paste0(x, "%")) +
    labs(x = NULL, y = "Idade",
          caption = "Share da população 4-24 anos por idade e ano (PNADC Q2).") +
    theme_minimal(base_family = "serif", base_size = 9) +
    theme(panel.grid = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_A2_idade_por_ano.pdf"), p,
        width = 11, height = 6, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_A2_idade_por_ano.png"), p,
        width = 11, height = 6, dpi = 150)
# } ----

# { FA_A3: composicao racial por ano ----
d <- read_csv(file.path(IN_DIR, "AP_A3_sexo_raca_por_ano.csv"),
              show_col_types = FALSE)
d_raca <- d %>%
    filter(categoria == "raca",
            valor %in% c("Branca","Preta","Amarela","Parda","Indigena")) %>%
    mutate(valor = factor(valor,
                            levels = c("Branca","Preta","Parda",
                                        "Amarela","Indigena")))
p <- ggplot(d_raca, aes(x = ano, y = share*100, fill = valor)) +
    geom_area(alpha = 0.85) +
    scale_x_continuous(breaks = 2012:2025) +
    scale_y_continuous(labels = function(x) paste0(x, "%"),
                        expand = expansion(0)) +
    scale_fill_brewer(palette = "Set2", name = "Raça/cor") +
    labs(x = NULL, y = "% da população 4-24 anos",
          caption = "Composição racial autodeclarada, PNADC Q2.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_A3_raca_por_ano.pdf"), p,
        width = 9, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_A3_raca_por_ano.png"), p,
        width = 9, height = 5, dpi = 150)
# } ----

cat("Saved FA_A1, FA_A2, FA_A3\n")
