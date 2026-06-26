# -------------------------------------------------------------------------
# F14_em_attendance_by_bfa.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Tres figuras separadas (15-17, 18-20, 21-24): matricula em EM regular,
#   por trimestre, com 3 grupos (BFA, CadUnico sem BFA, Fora) e linhas
#   verticais nas datas-chave do Pe-de-Meia.
#
# Inputs:
INPUT <- "../../3_Indicators/output/C31_em_attendance_by_bfa.csv"
#
# Outputs:
OUT_PDF_15 <- "../output/F14a_em_15_17.pdf";  OUT_PNG_15 <- "../output/F14a_em_15_17.png"
OUT_PDF_18 <- "../output/F14b_em_18_20.pdf";  OUT_PNG_18 <- "../output/F14b_em_18_20.png"
OUT_PDF_21 <- "../output/F14c_em_21_24.pdf";  OUT_PNG_21 <- "../output/F14c_em_21_24.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    mutate(
        x = Ano + (Trim - 0.5) / 4,
        grupo = factor(grupo, levels = c(
            "Bolsa Familia",
            "CadUnico (sem BFA)",
            "Fora do CadUnico"
        ))
    )

# Datas-chave (formato continuous)
x_pdm_implem <- 2024.25   # ~Marco 2024 (fim Q1)
x_pdm_expand <- 2024.625  # ~Agosto 2024 (meio Q3)

make_plot <- function(faixa_label, y_min, y_max, y_step, label_y) {
    sub <- df %>% filter(faixa == faixa_label)
    p <- ggplot(sub, aes(x = x, y = em_rate * 100,
                            color = grupo, linetype = grupo, shape = grupo)) +
        geom_vline(xintercept = x_pdm_implem, linetype = "dotted",
                    color = "gray30", linewidth = 0.5) +
        geom_vline(xintercept = x_pdm_expand, linetype = "dotted",
                    color = "gray30", linewidth = 0.5) +
        annotate("text", x = x_pdm_implem, y = label_y,
                  label = "Pé-de-Meia\nimplementação\n(mar/2024)",
                  size = 2.6, family = "serif", color = "gray25",
                  hjust = 1.05, vjust = 1) +
        annotate("text", x = x_pdm_expand, y = label_y,
                  label = "Expansão\nCadÚnico\n(ago/2024)",
                  size = 2.6, family = "serif", color = "gray25",
                  hjust = -0.05, vjust = 1) +
        geom_line(linewidth = 0.7) +
        geom_point(size = 1.6) +
        scale_x_continuous(
            breaks = seq(2022.125, 2025.875, 0.25),
            labels = c("2022Q1","Q2","Q3","Q4",
                        "2023Q1","Q2","Q3","Q4",
                        "2024Q1","Q2","Q3","Q4",
                        "2025Q1","Q2","Q3","Q4")
        ) +
        scale_y_continuous(labels = function(x) paste0(x, "%"),
                            limits = c(y_min, y_max),
                            breaks = seq(y_min, y_max, y_step)) +
        scale_color_manual(values = c(
            "Bolsa Familia"      = "#922B21",
            "CadUnico (sem BFA)" = "#7D6608",
            "Fora do CadUnico"   = "#1A5276"
        ), name = NULL) +
        scale_linetype_manual(values = c(
            "Bolsa Familia"      = "solid",
            "CadUnico (sem BFA)" = "dashed",
            "Fora do CadUnico"   = "dotdash"
        ), name = NULL) +
        scale_shape_manual(values = c(
            "Bolsa Familia"      = 16,
            "CadUnico (sem BFA)" = 17,
            "Fora do CadUnico"   = 15
        ), name = NULL) +
        labs(x = NULL, y = NULL,
              caption = paste0(
                  "Universo: jovens ", faixa_label, " anos. ",
                  "Numerador: matriculados em EM regular (V3002=1, V3003A=6). ",
                  "BFA = qualquer membro do domicílio com V5002A=1 em V5 (Anual). ",
                  "CadÚnico sem BFA: renda domiciliar per capita ≤ ½ SM (proxy). ",
                  "Em 2025 não há V5 disponível, BFA não classificado."
              )) +
        theme_minimal(base_family = "serif", base_size = 10) +
        theme(legend.position = "bottom",
              panel.grid.minor = element_blank(),
              axis.text.x = element_text(angle = 45, hjust = 1),
              plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))
    p
}

p15 <- make_plot("15-17", y_min = 50, y_max = 86, y_step = 5, label_y = 84)
p18 <- make_plot("18-20", y_min = 12, y_max = 34, y_step = 4, label_y = 33)
p21 <- make_plot("21-24", y_min = 0,  y_max = 5,  y_step = 1, label_y = 4.7)

ggsave(OUT_PDF_15, p15, width = 12, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_15, p15, width = 12, height = 5, dpi = 200)
ggsave(OUT_PDF_18, p18, width = 12, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_18, p18, width = 12, height = 5, dpi = 200)
ggsave(OUT_PDF_21, p21, width = 12, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_21, p21, width = 12, height = 5, dpi = 200)
cat("Saved F14a (15-17), F14b (18-20), F14c (21-24)\n")
