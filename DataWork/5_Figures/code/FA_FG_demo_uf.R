# -------------------------------------------------------------------------
# FA_FG_demo_uf.R
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, ggrepel)

OUT_DIR <- "../output"

cores_ano <- c("2015"="#FDD0A2","2017"="#FDAE6B","2019"="#FD8D3C",
                "2021"="#E6550D","2023"="#A63603","2025"="#000000")

# F. EM por raca x sexo x idade x ano
d <- read_csv("../../3_Indicators/output/AP_F_em_por_raca_sexo.csv",
               show_col_types = FALSE) %>%
    mutate(ano = factor(ano,
                          levels = c("2015","2017","2019","2021","2023","2025")),
           raca = factor(raca, levels = c("Branca","Preta","Parda")),
           sexo = factor(sexo, levels = c("Homem","Mulher")))

# FA_F1: EM por idade x raca x sexo, todos anos
p <- ggplot(d, aes(x = idade, y = em*100, color = ano, group = ano)) +
    geom_line(linewidth = 0.75) +
    geom_point(size = 1.4) +
    facet_grid(sexo ~ raca) +
    scale_x_continuous(breaks = seq(14, 24, 3)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    scale_color_manual(values = cores_ano, name = NULL) +
    labs(x = "Idade", y = "% concluiu EM",
          caption = "Por idade, raça e sexo. Linhas escuras = anos recentes.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_F1_em_raca_sexo_idade.pdf"), p,
        width = 11, height = 7, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_F1_em_raca_sexo_idade.png"), p,
        width = 11, height = 7, dpi = 150)

# FA_F2: EM aos 21 por raca, evolucao ano
d21 <- d %>% filter(idade == 21) %>%
    mutate(ano_n = as.integer(as.character(ano)))
p <- ggplot(d21, aes(x = ano_n, y = em*100, color = raca,
                       linetype = sexo, shape = sexo)) +
    geom_line(linewidth = 0.85) +
    geom_point(size = 2.2) +
    scale_x_continuous(breaks = c(2015,2017,2019,2021,2023,2025)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    scale_color_manual(values = c("Branca"="#1A5276","Preta"="#922B21",
                                      "Parda"="#7D6608"), name = NULL) +
    labs(x = NULL, y = "% concluiu EM aos 21 anos",
          caption = "Evolução por raça/cor e sexo.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_F2_em_aos_21_raca_sexo.pdf"), p,
        width = 9, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_F2_em_aos_21_raca_sexo.png"), p,
        width = 9, height = 5, dpi = 150)

# G. EM por UF
d <- read_csv("../../3_Indicators/output/AP_G_em_aos_19_21_por_uf.csv",
               show_col_types = FALSE) %>%
    mutate(ano = factor(ano,
                          levels = c("2015","2017","2019","2021","2023","2025")),
           regiao = factor(regiao, levels = c("N","NE","CO","SE","S")))

# FA_G1: dot plot UF ordenado pelo valor mais recente
d_latest <- d %>% filter(ano == "2025") %>% arrange(em)
ordem_uf <- d_latest$uf
d <- d %>% mutate(uf = factor(uf, levels = ordem_uf))

# Comparacao 2019 vs 2025
d_comp <- d %>%
    filter(ano %in% c("2019","2025")) %>%
    pivot_wider(names_from = ano, values_from = em, names_prefix = "y_") %>%
    mutate(delta = y_2025 - y_2019,
            delta_pos = delta > 0)
p <- ggplot(d_comp, aes(y = uf)) +
    geom_segment(aes(x = y_2019*100, xend = y_2025*100,
                       yend = uf),
                  arrow = arrow(length = unit(2, "mm")),
                  linewidth = 0.5,
                  color = "gray50") +
    geom_point(aes(x = y_2019*100), shape = 1, size = 2.5, color = "#1A5276") +
    geom_point(aes(x = y_2025*100), shape = 16, size = 2.8, color = "#000000") +
    facet_wrap(~regiao, scales = "free_y", ncol = 5) +
    scale_x_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = "% concluiu EM aos 19-21 anos", y = NULL,
          caption = "Setas: variação 2019 (○ azul) → 2025 (● preto), por UF, agrupado por região.") +
    theme_minimal(base_family = "serif", base_size = 9) +
    theme(strip.text = element_text(face = "bold"),
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_G1_em_uf_2019_2025.pdf"), p,
        width = 13, height = 7, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_G1_em_uf_2019_2025.png"), p,
        width = 13, height = 7, dpi = 150)

# FA_G2: serie temporal de UFs selecionadas (top, mid, bottom) por regiao
ufs_destaque <- c("RJ","SP","MG","BA","CE","MA","PI","AL","SC","RS","DF")
p <- ggplot(d %>% filter(uf %in% ufs_destaque) %>%
              mutate(ano_n = as.integer(as.character(ano))),
              aes(x = ano_n, y = em*100, color = uf, group = uf)) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.4) +
    scale_x_continuous(breaks = c(2015,2017,2019,2021,2023,2025)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "% concluiu EM aos 19-21 anos",
          caption = "Estados selecionados.", color = NULL) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_G2_em_uf_selecao.pdf"), p,
        width = 11, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_G2_em_uf_selecao.png"), p,
        width = 11, height = 5, dpi = 150)

# FA_G3: regiao agregada
d_reg <- d %>%
    group_by(ano, regiao) %>%
    summarise(em = sum(em * n) / sum(n), .groups = "drop") %>%
    mutate(ano_n = as.integer(as.character(ano)))
p <- ggplot(d_reg, aes(x = ano_n, y = em*100, color = regiao, group = regiao)) +
    geom_line(linewidth = 0.85) +
    geom_point(size = 2.0) +
    scale_x_continuous(breaks = c(2015,2017,2019,2021,2023,2025)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    scale_color_manual(values = c("N"="#922B21","NE"="#E67E22",
                                      "CO"="#F1C40F","SE"="#1A5276",
                                      "S"="#0E6655"), name = NULL) +
    labs(x = NULL, y = "% concluiu EM aos 19-21 anos",
          caption = "Por região (ponderada por n).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_G3_em_regiao.pdf"), p,
        width = 9, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_G3_em_regiao.png"), p,
        width = 9, height = 5, dpi = 150)

cat("Saved FA_F1, F2 + FA_G1, G2, G3\n")
