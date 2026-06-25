# -------------------------------------------------------------------------
# F7_freq_by_quarter.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Grafico do percentual de alunos frequentando a escola ao longo dos
#   trimestres Q1-Q4, separado por serie. Constroi a serie a partir do
#   raw panel.
#
# Inputs:
INPUT  <- "../../2_PanelBuild/tmp/pnadc_linked.dta"
#
# Outputs:
OUTPUT_PDF <- "../output/F7_freq_por_trimestre.pdf"
OUTPUT_PNG <- "../output/F7_freq_por_trimestre.png"
OUTPUT_CSV <- "../../3_Indicators/output/F7_freq_por_trimestre.csv"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, haven, scales)

cat("Reading panel...\n")
df <- read_dta(INPUT,
               col_select = c("Ano", "Trimestre", "etapa_consolid",
                              "serie", "freq_escola", "peso_v1028",
                              "link_ok", "idade"))

df <- df %>% filter(link_ok == 1)
cat("After link_ok:", nrow(df), "rows\n")

# Macroetapa
df <- df %>%
    mutate(macroetapa = case_when(
        etapa_consolid == 4 ~ "EF iniciais",
        etapa_consolid == 5 ~ "EF finais",
        etapa_consolid %in% c(10, 11, 12) ~ "EM",
        TRUE ~ NA_character_
    ))

# Nivel
df <- df %>%
    mutate(nivel = case_when(
        etapa_consolid == 4 & between(serie, 1, 5) ~ as.numeric(serie),
        etapa_consolid == 5 & between(serie, 6, 9) ~ as.numeric(serie),
        etapa_consolid == 10 ~ 10,
        etapa_consolid == 11 ~ 11,
        etapa_consolid == 12 ~ 12,
        TRUE ~ NA_real_
    ))

# Filter to EF + EM only
df <- df %>% filter(!is.na(macroetapa))
cat("After macroetapa filter:", nrow(df), "rows\n")

# For Figure 7: compute % freq_escola=1 by (Ano, Trimestre, nivel)
# Note: we want to capture WHICH SERIE the kid started in (at Q1 or first obs)
# and follow that kid through quarters.
# For simplicity, use the nivel at the first quarter the kid appears in that year.

df_first <- df %>%
    arrange(person_q_id <- NULL, Ano, Trimestre) %>%
    group_by(Ano) %>%
    mutate(rownum_year = row_number()) %>%
    ungroup()

# Better: use the EARLIEST nivel observed for that person in that year
# Use idade range 4-24
df <- df %>% filter(between(idade, 4, 24))

# Aggregate: % freq=1 by (Ano, Trimestre, macroetapa)
agg <- df %>%
    filter(!is.na(macroetapa)) %>%
    group_by(Ano, Trimestre, macroetapa) %>%
    summarise(
        pct_freq = weighted.mean(freq_escola == 1, w = peso_v1028, na.rm = TRUE),
        n = n(),
        .groups = "drop"
    )

# Save CSV
write_csv(agg, OUTPUT_CSV)
cat("Saved", OUTPUT_CSV, "\n")

# Plot: x = Trimestre, y = pct_freq, color = macroetapa, facet = Ano (selected years)
years_plot <- c(2013, 2015, 2017, 2019, 2022, 2023)
agg_plot <- agg %>% filter(Ano %in% years_plot) %>%
    mutate(macroetapa = factor(macroetapa,
                                levels = c("EF iniciais", "EF finais", "EM")),
           Ano = factor(Ano))

p <- ggplot(agg_plot,
            aes(x = Trimestre, y = pct_freq,
                color = macroetapa, group = macroetapa)) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.5) +
    facet_wrap(~ Ano, nrow = 2) +
    scale_x_continuous(breaks = 1:4, labels = c("Q1", "Q2", "Q3", "Q4")) +
    scale_y_continuous(labels = percent_format(accuracy = 1),
                       limits = c(NA, 1.0)) +
    scale_color_manual(values = c(
        "EF iniciais" = "#1A5276",
        "EF finais"   = "#7D6608",
        "EM"          = "#922B21"
    )) +
    labs(x = NULL, y = "% frequentando escola",
         color = NULL,
         caption = "Painel longitudinal da PNADC. Universo: idade 4-24, EF regular ou EM regular.") +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray35"))

ggsave(OUTPUT_PDF, p, width = 8.5, height = 5.5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 8.5, height = 5.5, dpi = 200)

cat("Saved", OUTPUT_PDF, "and", OUTPUT_PNG, "\n")
