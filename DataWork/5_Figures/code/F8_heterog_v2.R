# -------------------------------------------------------------------------
# F8_heterog_v2.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Figuras desagregadas a partir de C14_transitions_v2.parquet:
#     F8a: prom/rep/evas/eja por macroetapa x sexo
#     F8b: prom/rep/evas/eja por macroetapa x raca (branca/parda/preta)
#     F8c: prom/rep/evas/eja por macroetapa x quintil de renda (Q1-Q5)
#     F8d: prom/rep/evas/eja por macroetapa x defasagem (em dia vs >=2 anos)
#
#   Universo: media 2018-2023 ex-COVID.
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, haven, scales, arrow, patchwork)

OUT_DIR <- "../output"
DATA_DIR <- "../../3_Indicators/output"

cat("Loading transitions...\n")
t <- read_parquet(file.path(DATA_DIR, "C14_transitions_v2.parquet"))
cat("Rows:", nrow(t), "\n")

# Load extra demographics from raw panel (need sexo, raca, renda_dom_pc)
cat("Loading demographics from linked panel...\n")
extras <- read_dta("../../2_PanelBuild/tmp/pnadc_linked.dta",
                    col_select = c("person_id", "Ano", "Trimestre",
                                   "sexo", "raca", "renda_dom_pc")) %>%
    filter(Trimestre %in% c(2, 3)) %>%
    arrange(person_id, Ano, Trimestre) %>%
    distinct(person_id, Ano, .keep_all = TRUE) %>%
    rename(ano_t = Ano)

t <- t %>% left_join(extras, by = c("person_id", "ano_t"))
cat("After merge:", nrow(t), "rows, sexo non-NA:", sum(!is.na(t$sexo)), "\n")

# Drop NA flags (attrition)
t <- t %>% filter(!is.na(freq_t1))

# Compute idade-padrao, defasagem
t <- t %>%
    mutate(
        idade_padrao = case_when(
            nivel_t %in% 1:9 ~ 5 + nivel_t,
            nivel_t == 10 ~ 15,
            nivel_t == 11 ~ 16,
            nivel_t == 12 ~ 17,
            TRUE ~ NA_real_
        ),
        defasagem = idade_t - idade_padrao,
        em_dia = case_when(
            is.na(defasagem) ~ NA_character_,
            defasagem >= 2 ~ "Defasados (>= 2 anos)",
            TRUE ~ "Em dia"
        )
    )

# Compute flags (also already in parquet, ensure)
t <- t %>%
    mutate(
        any_eja_t1 = as.logical(any_eja_t1),
        flag_migracao_eja = as.integer(any_eja_t1),
        flag_evasao = as.integer((freq_t1 == 0) & !any_eja_t1),
        flag_promocao = as.integer((freq_t1 == 1) & !any_eja_t1 &
                                    !is.na(nivel_t1) & (nivel_t1 > nivel_t)),
        flag_repetencia = as.integer((freq_t1 == 1) & !any_eja_t1 &
                                      !is.na(nivel_t1) & (nivel_t1 == nivel_t))
    )

# Sample: 2018-2023, ex-COVID
sub <- t %>% filter(ano_t %in% c(2018, 2019, 2022, 2023))
cat("Sample 2018-2023 ex-COVID:", nrow(sub), "rows\n")

# Helper function
plot_by_dim <- function(d, dim_var, dim_label, title) {
    dimsym <- sym(dim_var)
    d_sum <- d %>%
        filter(!is.na(!!dimsym)) %>%
        group_by(macroetapa_t, !!dimsym) %>%
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

    ggplot(d_sum, aes(x = !!dimsym, y = valor, fill = indicador)) +
        geom_col(position = position_dodge(width = 0.85), width = 0.8) +
        facet_wrap(~ macroetapa, nrow = 1) +
        scale_y_continuous(labels = percent_format(accuracy = 1)) +
        scale_fill_manual(values = c(
            "Promocao" = "#1A5276",
            "Repetencia" = "#B7950B",
            "Evasao" = "#922B21",
            "Migração EJA" = "#6C3483"
        )) +
        labs(x = dim_label, y = NULL, fill = NULL, title = title) +
        theme_minimal(base_family = "serif", base_size = 9) +
        theme(legend.position = "bottom",
              panel.grid.minor = element_blank(),
              axis.text.x = element_text(angle = 30, hjust = 1),
              strip.text = element_text(face = "bold"),
              plot.title = element_text(size = 10, hjust = 0))
}

# ---- F8a: sexo ----
sub <- sub %>% mutate(sexo_label = case_when(
    sexo == 1 ~ "Masculino", sexo == 2 ~ "Feminino", TRUE ~ NA_character_))
p_sex <- plot_by_dim(sub, "sexo_label", "Sexo",
                     "Painel A: Por sexo")
ggsave(file.path(OUT_DIR, "F8a_heterog_sexo.pdf"),
       p_sex, width = 8.5, height = 4, device = cairo_pdf)

# ---- F8b: raca ----
sub <- sub %>% mutate(raca_label = case_when(
    raca == 1 ~ "Branca", raca == 2 ~ "Preta",
    raca == 3 ~ "Amarela", raca == 4 ~ "Parda",
    raca == 5 ~ "Indígena", TRUE ~ NA_character_)) %>%
    mutate(raca_label = factor(raca_label,
                                levels = c("Branca", "Preta", "Parda",
                                           "Amarela", "Indígena")))
p_raca <- plot_by_dim(sub %>% filter(raca_label %in% c("Branca", "Preta", "Parda")),
                      "raca_label", "Raça/cor",
                      "Painel B: Por raça/cor (branca, preta, parda)")
ggsave(file.path(OUT_DIR, "F8b_heterog_raca.pdf"),
       p_raca, width = 8.5, height = 4, device = cairo_pdf)

# ---- F8c: quintil de renda ----
# Compute quintile from renda_dom_pc nationally per year
sub <- sub %>% group_by(ano_t) %>%
    mutate(quintil = case_when(
        is.na(renda_dom_pc) ~ NA_real_,
        TRUE ~ as.numeric(cut(renda_dom_pc,
                              breaks = quantile(renda_dom_pc,
                                                probs = seq(0, 1, 0.2),
                                                na.rm = TRUE),
                              include.lowest = TRUE,
                              labels = FALSE))
    )) %>%
    ungroup() %>%
    mutate(quintil_label = case_when(
        quintil == 1 ~ "Q1 (mais pobre)",
        quintil == 2 ~ "Q2",
        quintil == 3 ~ "Q3",
        quintil == 4 ~ "Q4",
        quintil == 5 ~ "Q5 (mais rico)",
        TRUE ~ NA_character_)) %>%
    mutate(quintil_label = factor(quintil_label,
                                   levels = c("Q1 (mais pobre)", "Q2",
                                              "Q3", "Q4", "Q5 (mais rico)")))
p_renda <- plot_by_dim(sub, "quintil_label", "Quintil de renda dom. per capita",
                       "Painel C: Por quintil de renda")
ggsave(file.path(OUT_DIR, "F8c_heterog_renda.pdf"),
       p_renda, width = 9, height = 4, device = cairo_pdf)

# ---- F8d: defasagem ----
p_def <- plot_by_dim(sub, "em_dia", "Defasagem idade-série",
                     "Painel D: Por defasagem idade-série")
ggsave(file.path(OUT_DIR, "F8d_heterog_defasagem.pdf"),
       p_def, width = 8.5, height = 4, device = cairo_pdf)

# ---- Combined F8: 4 panels (a, b, c, d) stacked ----
combined <- p_sex / p_raca / p_renda / p_def
ggsave(file.path(OUT_DIR, "F8_heterog_combined.pdf"),
       combined, width = 10, height = 16, device = cairo_pdf)

cat("Saved F8a-d and F8_heterog_combined\n")
