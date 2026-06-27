# -------------------------------------------------------------------------
# FA_D_conclusao.R
# -------------------------------------------------------------------------
# Description:
#   Figuras de conclusao de etapa por idade, ano, sexo, raca
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

OUT_DIR <- "../output"
d <- read_csv("../../3_Indicators/output/AP_D_conclusao_por_etapa.csv",
               show_col_types = FALSE)

cores_ano <- c("2015"="#FDD0A2","2017"="#FDAE6B","2019"="#FD8D3C",
                "2021"="#E6550D","2023"="#A63603","2025"="#000000")

mk_curve <- function(d_sub, outcome, title_str, fname,
                       facet_var = NULL, age_max = 24) {
    d_sub <- d_sub %>%
        filter(idade <= age_max) %>%
        mutate(ano = factor(ano,
                              levels = c("2015","2017","2019","2021","2023","2025")))
    p <- ggplot(d_sub, aes(x = idade, y = .data[[outcome]]*100,
                              color = ano, group = ano)) +
        geom_line(linewidth = 0.85) +
        geom_point(size = 1.8) +
        scale_x_continuous(breaks = seq(14, age_max, 2)) +
        scale_y_continuous(labels = function(x) paste0(x,"%")) +
        scale_color_manual(values = cores_ano, name = "Ano") +
        labs(x = "Idade", y = paste0("% que concluiu ", title_str),
              caption = "PNADC, Q1-Q4 do ano. Pesos: V1028.") +
        theme_minimal(base_family = "serif", base_size = 10) +
        theme(legend.position = "bottom",
              panel.grid.minor = element_blank(),
              plot.caption = element_text(hjust=0, size=8, color="gray25"))
    if (!is.null(facet_var)) p <- p + facet_wrap(reformulate(facet_var))
    ggsave(file.path(OUT_DIR, paste0(fname, ".pdf")), p,
            width = 11, height = 5.5, device = cairo_pdf)
    ggsave(file.path(OUT_DIR, paste0(fname, ".png")), p,
            width = 11, height = 5.5, dpi = 150)
}

# D.1 EF completo total
d_tot <- d %>% filter(categoria == "total")
mk_curve(d_tot, "ef",  "Ensino Fundamental",     "FA_D1_ef_completo_idade",      age_max = 24)
mk_curve(d_tot, "em",  "Ensino Médio",           "FA_D2_em_completo_idade",      age_max = 24)
mk_curve(d_tot, "sup", "Ensino Superior",        "FA_D3_sup_completo_idade",     age_max = 29)

# D.4 Por sexo
d_sex <- d %>% filter(categoria == "sexo")
mk_curve(d_sex, "em",  "Ensino Médio",           "FA_D4_em_por_sexo",             facet_var = "valor", age_max = 24)

# D.5 Por raca
d_rac <- d %>% filter(categoria == "raca", valor %in% c("Branca","Preta","Parda"))
mk_curve(d_rac, "em",  "Ensino Médio",           "FA_D5_em_por_raca",             facet_var = "valor", age_max = 24)
mk_curve(d_rac, "sup", "Ensino Superior",        "FA_D6_sup_por_raca",            facet_var = "valor", age_max = 29)

cat("Saved FA_D1..D6\n")
