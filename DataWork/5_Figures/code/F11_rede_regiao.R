# -------------------------------------------------------------------------
# F11_rede_regiao.R
# -------------------------------------------------------------------------
# Author: Vitor (auto-generated)
# Last update: 2026-06-25
#
# Description:
#   Gera duas figuras adicionais de heterogeneidade:
#     F8e: taxas de fluxo por rede (publica/privada) e macroetapa
#     F11: taxas de fluxo por macrorregiao e macroetapa
#
#   Universo: media 2018-2023 ex-COVID, painel v5 (C22_transitions ou C20).
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales, arrow, haven)

OUT_DIR <- "../output"
DATA_DIR <- "../../3_Indicators/output"

cat("Loading v5 transitions...\n")
t <- read_parquet(file.path(DATA_DIR, "C20_transitions_v5.parquet"))
cat("Rows:", nrow(t), "\n")

# Need rede and UF from link panel
cat("Loading extras (rede, UF, raca)...\n")
extras <- read_dta("../../2_PanelBuild/tmp/pnadc_linked.dta",
                    col_select = c("person_id", "Ano", "Trimestre",
                                   "UF", "rede")) %>%
    filter(Trimestre %in% c(2, 3)) %>%
    arrange(person_id, Ano, Trimestre) %>%
    distinct(person_id, Ano, .keep_all = TRUE) %>%
    rename(ano_t = Ano)

t <- t %>% left_join(extras, by = c("person_id", "ano_t"))
cat("After merge:", nrow(t), "\n")

# Macrorregião do UF
t <- t %>%
    mutate(regiao = case_when(
        UF %in% c(11, 12, 13, 14, 15, 16, 17) ~ "Norte",
        UF %in% c(21, 22, 23, 24, 25, 26, 27, 28, 29) ~ "Nordeste",
        UF %in% c(31, 32, 33, 35) ~ "Sudeste",
        UF %in% c(41, 42, 43) ~ "Sul",
        UF %in% c(50, 51, 52, 53) ~ "Centro-Oeste",
        TRUE ~ NA_character_
    ))

# Rede dummy
t <- t %>%
    mutate(rede_label = case_when(
        rede %in% 1:3 ~ "Pública",
        rede == 5 ~ "Privada",
        TRUE ~ NA_character_
    ))

# Filter to 2018-2023 ex-COVID
sub <- t %>%
    filter(ano_t %in% c(2018, 2019, 2022, 2023)) %>%
    filter(!is.na(regiao))

cat("Sample 2018-2023 ex-COVID:", nrow(sub), "\n")

# Helper plot
plot_by_dim <- function(d, dim_var, dim_label) {
    sym_dim <- sym(dim_var)
    d_sum <- d %>%
        filter(!is.na(!!sym_dim)) %>%
        group_by(macroetapa_t, !!sym_dim) %>%
        summarise(
            Promocao = weighted.mean(flag_promocao, w = wt_t, na.rm = TRUE),
            Repetencia = weighted.mean(flag_repetencia, w = wt_t, na.rm = TRUE),
            Evasao = weighted.mean(flag_evasao, w = wt_t, na.rm = TRUE),
            `Migração EJA` = weighted.mean(flag_migracao_eja, w = wt_t, na.rm = TRUE),
            n = n(),
            .groups = "drop"
        ) %>%
        filter(n >= 50) %>%
        pivot_longer(c(Promocao, Repetencia, Evasao, `Migração EJA`),
                     names_to = "indicador", values_to = "valor") %>%
        mutate(macroetapa = factor(macroetapa_t,
                                    levels = c("EF iniciais",
                                               "EF finais", "EM")),
               indicador = factor(indicador,
                                  levels = c("Promocao", "Repetencia",
                                             "Evasao", "Migração EJA")))

    ggplot(d_sum, aes(x = !!sym_dim, y = valor, fill = indicador)) +
        geom_col(position = position_dodge(width = 0.85), width = 0.8) +
        facet_wrap(~ macroetapa, nrow = 1) +
        scale_y_continuous(labels = percent_format(accuracy = 1)) +
        scale_fill_manual(values = c(
            "Promocao" = "#1A5276",
            "Repetencia" = "#B7950B",
            "Evasao" = "#922B21",
            "Migração EJA" = "#6C3483"
        )) +
        labs(x = dim_label, y = NULL, fill = NULL) +
        theme_minimal(base_family = "serif", base_size = 9) +
        theme(legend.position = "bottom",
              panel.grid.minor = element_blank(),
              axis.text.x = element_text(angle = 30, hjust = 1),
              strip.text = element_text(face = "bold"))
}

# F8e: rede
p_rede <- plot_by_dim(sub %>% filter(!is.na(rede_label)),
                       "rede_label", "Rede")
ggsave(file.path(OUT_DIR, "F8e_heterog_rede.pdf"),
        p_rede, width = 8.5, height = 4, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "F8e_heterog_rede.png"),
        p_rede, width = 8.5, height = 4, dpi = 200)

# F11: macrorregião
sub <- sub %>%
    mutate(regiao = factor(regiao,
                            levels = c("Norte", "Nordeste",
                                       "Sudeste", "Sul",
                                       "Centro-Oeste")))
p_reg <- plot_by_dim(sub, "regiao", "Macrorregião")
ggsave(file.path(OUT_DIR, "F11_heterog_regiao.pdf"),
        p_reg, width = 9, height = 4, device = cairo_pdf)
ggsave(file.path(OUT_DIR, "F11_heterog_regiao.png"),
        p_reg, width = 9, height = 4, dpi = 200)

cat("Saved F8e and F11\n")
