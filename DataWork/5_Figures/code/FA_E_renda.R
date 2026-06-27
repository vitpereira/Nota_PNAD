# -------------------------------------------------------------------------
# FA_E_renda.R
# -------------------------------------------------------------------------
# Description:
#   Conclusao EM por quintil de renda, idade e ano.
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"
d <- read_csv("../../3_Indicators/output/AP_E_conclusao_por_quintil.csv",
               show_col_types = FALSE) %>%
    mutate(quintil = factor(quintil,
                               levels = c("Q1 (mais pobre)","Q2","Q3","Q4",
                                           "Q5 (mais rico)")),
           ano = factor(ano,
                          levels = c("2015","2017","2019","2021","2023","2025")))

cores_ano <- c("2015"="#FDD0A2","2017"="#FDAE6B","2019"="#FD8D3C",
                "2021"="#E6550D","2023"="#A63603","2025"="#000000")

# FA_E1: EM por idade x quintil, todos anos
p <- ggplot(d %>% filter(idade <= 24),
              aes(x = idade, y = em*100,
                   color = ano, group = ano)) +
    geom_line(linewidth = 0.85) +
    geom_point(size = 1.6) +
    facet_wrap(~quintil, ncol = 5) +
    scale_x_continuous(breaks = c(14,17,20,23)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    scale_color_manual(values = cores_ano, name = "Ano") +
    labs(x = "Idade", y = "% concluiu EM",
          caption = "Quintis de renda dom. per capita calculados dentro de cada ano.") +
    theme_minimal(base_family = "serif", base_size = 9) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust=0, size=8, color="gray25"))
ggsave(file.path(OUT_DIR, "FA_E1_em_por_quintil_ano.pdf"), p,
        width = 13, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_E1_em_por_quintil_ano.png"), p,
        width = 13, height = 4.5, dpi = 150)

# FA_E2: % concluiu EM aos 21 por quintil ao longo do tempo
d21 <- d %>% filter(idade == 21) %>%
    mutate(ano_n = as.integer(as.character(ano)))
p <- ggplot(d21, aes(x = ano_n, y = em*100, color = quintil, group = quintil)) +
    geom_line(linewidth = 0.9) +
    geom_point(size = 2.4) +
    scale_x_continuous(breaks = c(2015,2017,2019,2021,2023,2025)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    scale_color_manual(values = c("Q1 (mais pobre)"="#922B21","Q2"="#C0392B",
                                      "Q3"="#7D6608","Q4"="#1F618D",
                                      "Q5 (mais rico)"="#1A5276"),
                          name = NULL) +
    labs(x = NULL, y = "% concluiu EM aos 21 anos",
          caption = "Quintis de renda dom. per capita por ano.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust=0, size=8, color="gray25"))
ggsave(file.path(OUT_DIR, "FA_E2_em_aos_21_por_quintil.pdf"), p,
        width = 9, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_E2_em_aos_21_por_quintil.png"), p,
        width = 9, height = 5, dpi = 150)

cat("Saved FA_E1, FA_E2\n")
