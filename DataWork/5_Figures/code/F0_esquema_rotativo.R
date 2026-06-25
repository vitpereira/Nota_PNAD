# -------------------------------------------------------------------------
# F0_esquema_rotativo.R
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Figura ilustrativa do esquema rotativo 1-2(5) da PNADC. Mostra como
#   cada rotacao (1 a 4) gera uma cadeia de 5 visitas atravessando dois
#   anos calendario. Destaca a janela de medicao Q2-Q3 (v5) e o periodo
#   de ferias Q1.
#
# Outputs:
#   ../output/F0_esquema_rotativo.pdf
#   ../output/F0_esquema_rotativo.png
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

# Construir grade ano-trimestre (de y a y+1, 8 trimestres total)
# Rotacoes 1 a 4: cada rotacao tem 5 visitas (V1 a V5)
# Trimestres em ordem cronologica: y-Q1, y-Q2, y-Q3, y-Q4, (y+1)-Q1, (y+1)-Q2, (y+1)-Q3, (y+1)-Q4

# Rotacao 1: entra em Q1 do ano y -> visitas em y-Q1, y-Q2, y-Q3, y-Q4, (y+1)-Q1
# Rotacao 2: entra em Q2 do ano y -> visitas em y-Q2, y-Q3, y-Q4, (y+1)-Q1, (y+1)-Q2
# Rotacao 3: entra em Q3 do ano y -> visitas em y-Q3, y-Q4, (y+1)-Q1, (y+1)-Q2, (y+1)-Q3
# Rotacao 4: entra em Q4 do ano y -> visitas em y-Q4, (y+1)-Q1, (y+1)-Q2, (y+1)-Q3, (y+1)-Q4

# Construir um data frame para o ggplot
trimestres <- c("y-Q1", "y-Q2", "y-Q3", "y-Q4",
                 "y+1-Q1", "y+1-Q2", "y+1-Q3", "y+1-Q4")
trim_idx <- 1:8

# Cada rotacao: trimestres ocupados
rot1 <- c(1, 2, 3, 4, 5)
rot2 <- c(2, 3, 4, 5, 6)
rot3 <- c(3, 4, 5, 6, 7)
rot4 <- c(4, 5, 6, 7, 8)

df <- bind_rows(
    tibble(rotacao = 1, visita = 1:5, trim = rot1),
    tibble(rotacao = 2, visita = 1:5, trim = rot2),
    tibble(rotacao = 3, visita = 1:5, trim = rot3),
    tibble(rotacao = 4, visita = 1:5, trim = rot4)
) %>%
    mutate(rot_label = paste0("Rotação ", rotacao),
            ano = ifelse(trim <= 4, "Ano y", "Ano y+1"),
            trim_in_year = ifelse(trim <= 4, trim, trim - 4),
            tri_label = paste0("Q", trim_in_year),
            in_v5 = trim_in_year %in% c(2, 3),  # janela v5
            in_q1 = trim_in_year == 1,
            in_q4 = trim_in_year == 4)

# Plot:
# - x: trimestre (cronologico, 1-8)
# - y: rotacao
# - cada celula: visita (V1-V5)
# - cor de fundo: V5 highlight Q2-Q3, Q1 outlined férias
p <- ggplot(df, aes(x = trim, y = rotacao)) +
    geom_tile(aes(fill = in_v5), color = "gray70", linewidth = 0.3,
              height = 0.7, width = 0.85) +
    geom_text(aes(label = paste0("V", visita)),
              color = "black", size = 3.2, family = "serif") +
    scale_fill_manual(values = c("TRUE" = "#BFE2A0",   # green: in v5 window
                                   "FALSE" = "white"),
                       guide = "none") +
    # Background bands for Q1 (ferias) and Q4 (fim ano)
    annotate("rect", xmin = 0.5, xmax = 1.5, ymin = -Inf, ymax = Inf,
             fill = "gray", alpha = 0.18) +
    annotate("rect", xmin = 4.5, xmax = 5.5, ymin = -Inf, ymax = Inf,
             fill = "gray", alpha = 0.18) +
    # Divider between Ano y and Ano y+1
    geom_vline(xintercept = 4.5, color = "gray40", linetype = "dashed",
                linewidth = 0.4) +
    scale_x_continuous(breaks = 1:8,
                        labels = c("Q1", "Q2", "Q3", "Q4",
                                   "Q1", "Q2", "Q3", "Q4"),
                        sec.axis = sec_axis(~., breaks = c(2.5, 6.5),
                                              labels = c("Ano y",
                                                         "Ano y+1"))) +
    scale_y_continuous(breaks = 1:4,
                        labels = paste0("Rotação ", 1:4),
                        trans = "reverse") +
    labs(x = NULL, y = NULL,
          caption = paste0(
              "Cada linha mostra uma rotação; cada célula uma das cinco visitas (V1-V5) ",
              "ao mesmo domicílio.\n",
              "Sombreado cinza: trimestres Q1 (jan-mar, férias e início do ano letivo).\n",
              "Sombreado verde: trimestres Q2 e Q3, janela de mensuração v5 usada nesta nota.")) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "none",
          panel.grid.major.x = element_blank(),
          panel.grid.minor = element_blank(),
          axis.text.x.top = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8.5,
                                       color = "gray25"))

ggsave("../output/F0_esquema_rotativo.pdf", p,
        width = 8.5, height = 4, device = cairo_pdf)
ggsave("../output/F0_esquema_rotativo.png", p,
        width = 8.5, height = 4, dpi = 200)

cat("Saved F0_esquema_rotativo.pdf\n")
