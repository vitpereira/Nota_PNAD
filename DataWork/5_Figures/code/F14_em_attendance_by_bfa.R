# -------------------------------------------------------------------------
# F14_em_attendance_by_bfa.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Figura trimestral 2022Q1-2024Q4 de matricula em EM regular entre
#   adolescentes 15-17 anos, 3 grupos:
#     - Bolsa Familia
#     - CadUnico sem BFA (proxy: renda_dom_pc <= 1/2 SM)
#     - Fora do CadUnico
#   Linhas verticais:
#     - Marco/2024: implementacao PdM (primeira parcela BFA)
#     - Agosto/2024: expansao PdM para CadUnico (Portaria 792)
#
# Inputs:
INPUT <- "../../3_Indicators/output/C31_em_attendance_by_bfa.csv"
#
# Outputs:
OUTPUT_PDF  <- "../output/F14_em_attendance_by_bfa.pdf"
OUTPUT_PNG  <- "../output/F14_em_attendance_by_bfa.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

df <- read_csv(INPUT, show_col_types = FALSE) %>%
    mutate(
        # x numerico continuo: ano + (trim-1)/4 (centra trim em meio do trimestre)
        x = Ano + (Trim - 0.5) / 4,
        grupo = factor(grupo, levels = c(
            "Bolsa Familia",
            "CadUnico (sem BFA)",
            "Fora do CadUnico"
        ))
    )

# Datas-chave PdM convertidas a x continuo
# PdM lei 14.818 sancionada 16/01/2024, primeira parcela BFA Marco/2024
x_pdm_start <- 2024 + (3 - 0.5) / 12   # ~Marco 2024 (em escala mensal/decimal)
# Convertendo para escala trimestral: trim 1 cobre Jan-Mar, fim de trim 1 = inicio trim 2
# Marco esta no final de trim 1: x = 2024 + 1 = 2025... wait, our scale uses (Trim-0.5)/4
# Trim 1 (Jan-Mar): x = 2024 + 0.5/4 = 2024.125
# Trim 2 (Apr-Jun): x = 2024 + 1.5/4 = 2024.375
# Marco eh final de Trim 1 -> entre x=2024.125 e x=2024.375 -> x ~ 2024.25
x_pdm_implem <- 2024.25   # fim de Marco/inicio de Abril 2024
# Expansao CadUnico: Portaria 792 em 15/08/2024, primeiro pagamento 26/08-02/09
# 15 Agosto = meio do Trim 3 (Jul-Set): x ~ 2024.625
x_pdm_expand <- 2024.625

p <- ggplot(df, aes(x = x, y = em_rate * 100,
                       color = grupo, linetype = grupo, shape = grupo)) +
    # Linhas verticais e anotacoes
    geom_vline(xintercept = x_pdm_implem, linetype = "dotted",
                color = "gray30", linewidth = 0.5) +
    geom_vline(xintercept = x_pdm_expand, linetype = "dotted",
                color = "gray30", linewidth = 0.5) +
    annotate("text", x = x_pdm_implem, y = 84,
              label = "Pé-de-Meia\nimplementação\n(mar/2024)",
              size = 2.6, family = "serif", color = "gray25",
              hjust = 1.05, vjust = 1) +
    annotate("text", x = x_pdm_expand, y = 84,
              label = "Expansão\nCadÚnico\n(ago/2024)",
              size = 2.6, family = "serif", color = "gray25",
              hjust = -0.05, vjust = 1) +
    geom_line(linewidth = 0.7) +
    geom_point(size = 1.6) +
    scale_x_continuous(
        breaks = seq(2022.125, 2024.875, 0.25),
        labels = c("2022Q1","Q2","Q3","Q4",
                    "2023Q1","Q2","Q3","Q4",
                    "2024Q1","Q2","Q3","Q4")
    ) +
    scale_y_continuous(labels = function(x) paste0(x, "%"),
                        limits = c(50, 86), breaks = seq(50, 85, 5)) +
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
              "Universo: adolescentes 15-17 anos. Numerador: matriculados em EM regular (V3002=1, V3003A=6). ",
              "BFA = qualquer membro do domicílio com V5002A=1 em V5. ",
              "CadÚnico sem BFA proxy: renda domiciliar per capita ≤ ½ salário mínimo do ano."
          )) +
    theme_minimal(base_family = "serif", base_size = 10) +
    theme(legend.position = "bottom",
          panel.grid.minor = element_blank(),
          axis.text.x = element_text(angle = 45, hjust = 1),
          plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))

ggsave(OUTPUT_PDF, p, width = 10, height = 5, device = cairo_pdf)
ggsave(OUTPUT_PNG, p, width = 10, height = 5, dpi = 200)
cat("Saved F14\n")
