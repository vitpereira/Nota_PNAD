if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"

# FA_BR1: identidade contabil + residuo por macroetapa
d <- read_csv("../../3_Indicators/output/AP_BR_identidade_contabil.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021))) %>%
    mutate(macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")))

# Stacked area dos 4 destinos
d_long <- d %>%
    select(ano, macroetapa, prom, rep, evas, eja, residuo) %>%
    pivot_longer(c(prom, rep, evas, eja, residuo),
                  names_to = "destino", values_to = "share") %>%
    mutate(destino = factor(case_when(
                destino == "prom" ~ "Promoção",
                destino == "rep"  ~ "Repetência",
                destino == "evas" ~ "Evasão",
                destino == "eja"  ~ "Mig EJA",
                destino == "residuo" ~ "Resíduo"),
              levels = c("Promoção","Repetência","Mig EJA","Evasão","Resíduo")))
p <- ggplot(d_long, aes(x = ano, y = share*100, fill = destino)) +
    geom_area(alpha = 0.85) +
    facet_wrap(~macroetapa) +
    scale_fill_manual(values = c("Promoção"="#27AE60",
                                     "Repetência"="#F39C12",
                                     "Mig EJA"="#3498DB",
                                     "Evasão"="#922B21",
                                     "Resíduo"="gray70"), name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%"),
                        expand = expansion(0)) +
    labs(x = NULL, y = "% dos alunos",
          caption = "Decomposição da transição t -> t+1 com resíduo (não promovido/repetente/EJA/evasão).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_BR1_identidade_area.pdf"), p,
        width = 12, height = 5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_BR1_identidade_area.png"), p,
        width = 12, height = 5, dpi = 150)

# FA_BR2: residuo por ano e macroetapa - linha
p <- ggplot(d, aes(x = ano, y = residuo*100, color = macroetapa,
                       group = macroetapa)) +
    geom_line(linewidth = 0.9) +
    geom_point(size = 1.8) +
    scale_color_manual(values = c("EF iniciais"="#1A5276",
                                      "EF finais"="#7D6608",
                                      "EM"="#922B21"), name = NULL) +
    scale_x_continuous(breaks = seq(2012, 2024, 2)) +
    scale_y_continuous(labels = function(x) paste0(x,"%")) +
    labs(x = NULL, y = "Resíduo da identidade (%)",
          caption = "1 - (promoção + repetência + mig EJA + evasão).") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
ggsave(file.path(OUT_DIR, "FA_BR2_residuo.pdf"), p,
        width = 9, height = 4.5, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "FA_BR2_residuo.png"), p,
        width = 9, height = 4.5, dpi = 150)

# FA_E3: fluxos por quintil e ano
d <- read_csv("../../3_Indicators/output/AP_E_fluxos_por_quintil.csv",
               show_col_types = FALSE) %>%
    filter(!(ano %in% c(2020, 2021)),
            macroetapa %in% c("EF iniciais","EF finais","EM")) %>%
    mutate(macroetapa = factor(macroetapa,
              levels = c("EF iniciais","EF finais","EM")),
           quintil = factor(quintil, levels = c("Q1","Q2","Q3","Q4","Q5")))

cores_q <- c("Q1"="#922B21","Q2"="#C0392B","Q3"="#7D6608",
              "Q4"="#1F618D","Q5"="#1A5276")

mk_quintil <- function(varname, ylab, fname) {
    p <- ggplot(d, aes(x = ano, y = .data[[varname]]*100,
                          color = quintil, group = quintil)) +
        geom_line(linewidth = 0.8) +
        geom_point(size = 1.4) +
        facet_wrap(~macroetapa, scales = "free_y") +
        scale_color_manual(values = cores_q, name = "Quintil") +
        scale_x_continuous(breaks = seq(2012, 2024, 2)) +
        scale_y_continuous(labels = function(x) paste0(x,"%")) +
        labs(x = NULL, y = ylab,
              caption = "Quintis de renda dom. per capita dentro do ano. Exclui 2020-2021.") +
        theme_minimal(base_family = "serif", base_size = 10) +
        theme(legend.position = "bottom",
              panel.grid.minor = element_blank(),
              strip.text = element_text(face = "bold"),
              axis.text.x = element_text(angle = 45, hjust = 1),
              plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
    ggsave(file.path(OUT_DIR, paste0(fname, ".pdf")), p,
            width = 12, height = 4.5, device = cairo_pdf)
    ggsave(file.path(OUT_DIR, paste0(fname, ".png")), p,
            width = 12, height = 4.5, dpi = 150)
}

mk_quintil("prom",  "Promoção (%)",     "FA_E3_promocao_quintil")
mk_quintil("rep",   "Repetência (%)",   "FA_E4_repetencia_quintil")
mk_quintil("evas",  "Evasão (%)",       "FA_E5_evasao_quintil")

cat("Saved FA_BR1, BR2 + FA_E3-E5\n")
