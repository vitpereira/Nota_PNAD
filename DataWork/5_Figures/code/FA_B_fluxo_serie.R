# -------------------------------------------------------------------------
# FA_B_fluxo_serie.R
# -------------------------------------------------------------------------
# Description:
#   Heatmaps de taxas de fluxo (promocao, repetencia, evasao, mig EJA)
#   por serie individual e ano.
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"
d <- read_csv("../../3_Indicators/output/AP_B_fluxo_por_serie_ano.csv",
               show_col_types = FALSE) %>%
    filter(!(ano_t %in% c(2020, 2021))) %>%
    mutate(serie = factor(serie,
                            levels = c("1o EF","2o EF","3o EF","4o EF","5o EF",
                                        "6o EF","7o EF","8o EF","9o EF",
                                        "1o EM","2o EM","3o EM","4o EM tec")))

mk_heat <- function(varname, label_str, palette, fname) {
    p <- ggplot(d, aes(x = ano_t, y = serie, fill = .data[[varname]]*100)) +
        geom_tile() +
        geom_text(aes(label = sprintf("%.0f", .data[[varname]]*100)),
                   size = 2.0, family = "serif", color = "white") +
        scale_x_continuous(breaks = sort(unique(d$ano_t))) +
        scale_fill_gradient(low = palette[1], high = palette[2],
                              name = paste0(label_str, " (%)"),
                              labels = function(x) paste0(x, "%")) +
        labs(x = NULL, y = NULL,
              caption = paste0("Taxa de ", label_str,
                                " por série e ano (PNADC v5, exclui 2020-2021 COVID).")) +
        theme_minimal(base_family = "serif", base_size = 9) +
        theme(panel.grid = element_blank(),
              axis.text.x = element_text(angle = 45, hjust = 1),
              plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
    ggsave(file.path(OUT_DIR, paste0(fname, ".pdf")), p,
            width = 10, height = 6, device = cairo_pdf)
    ggsave(file.path(OUT_DIR, paste0(fname, ".png")), p,
            width = 10, height = 6, dpi = 150)
}

mk_heat("flag_promocao",      "promoção",     c("#FCFDBF","#5C2A85"), "FA_B1_promocao_serie")
mk_heat("flag_repetencia",    "repetência",   c("#FFEEE5","#641E16"), "FA_B2_repetencia_serie")
mk_heat("flag_evasao",        "evasão",       c("#FFF5E6","#6E2C00"), "FA_B3_evasao_serie")
mk_heat("flag_migracao_eja",  "migração EJA", c("#F5F5F5","#1B2631"), "FA_B4_migeja_serie")

cat("Saved FA_B1 a FA_B4\n")
