# -------------------------------------------------------------------------
# F17_event_study.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Dois plots event study TWFE separados:
#     F17a: Renda < 1/4 SM vs control, T0 = 2023Q4 (anuncio PdM)
#     F17b: 1/4 a 1/2 SM   vs control, T0 = 2024Q3 (expansao CadUnico)
#   Outcome: matricula em EM regular OU EJA EM OU ja concluiu EM (V3002=1 &
#            V3003A in (6,7) OR VD3004>=5).
#
# Inputs:
INPUT_A <- "../../3_Indicators/output/C36_event_extreme_em.csv"
INPUT_B <- "../../3_Indicators/output/C36_event_low_em.csv"
#
# Outputs:
OUT_PDF_A <- "../output/F17a_event_extreme.pdf"
OUT_PNG_A <- "../output/F17a_event_extreme.png"
OUT_PDF_B <- "../output/F17b_event_low.pdf"
OUT_PNG_B <- "../output/F17b_event_low.png"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, scales)

make_event_plot <- function(input_path, base_yrq, label, color,
                              ymin = NA, ymax = NA, sub_caption = "") {
    d <- read_csv(input_path, show_col_types = FALSE)
    base_ano <- as.integer(str_sub(base_yrq, 1, 4))
    base_trim <- as.integer(str_sub(base_yrq, 6, 6))
    x_baseline <- base_ano + (base_trim - 0.5) / 4

    p <- ggplot(d, aes(x = x, y = estimate)) +
        # IC 95%
        geom_ribbon(aes(ymin = conf.low, ymax = conf.high),
                     fill = color, alpha = 0.18) +
        geom_hline(yintercept = 0, color = "gray40", linewidth = 0.4) +
        # Linha do baseline T0
        geom_vline(xintercept = x_baseline, color = "gray20",
                    linetype = "dashed", linewidth = 0.5) +
        geom_line(linewidth = 0.7, color = color) +
        geom_point(size = 1.8, color = color, shape = 16) +
        annotate("text", x = x_baseline, y = Inf,
                  label = sprintf("T0 = %s", base_yrq),
                  size = 2.7, family = "serif", color = "gray25",
                  hjust = -0.05, vjust = 1.6) +
        scale_x_continuous(
            breaks = seq(2022.125, 2025.875, 0.25),
            labels = c("2022Q1","Q2","Q3","Q4",
                        "2023Q1","Q2","Q3","Q4",
                        "2024Q1","Q2","Q3","Q4",
                        "2025Q1","Q2","Q3","Q4")
        ) +
        scale_y_continuous(labels = function(x) paste0(x, " p.p.")) +
        labs(x = NULL,
              y = sprintf("Δ tratado (%s) − controle (>1/2 SM), p.p.", label),
              title = NULL,
              caption = paste0(
                  sub_caption,
                  " Banda colorida: IC 95% com SE clusterizados em domicílio. ",
                  "Outcome: matriculado em EM regular OU EJA EM OU já concluiu EM. ",
                  "Universo: jovens 15-19 anos. ",
                  "Modelo TWFE com FE de UF e trimestre. Pesos: V1028."
              )) +
        theme_minimal(base_family = "serif", base_size = 10) +
        theme(panel.grid.minor = element_blank(),
              axis.text.x = element_text(angle = 45, hjust = 1),
              plot.caption = element_text(hjust = 0, size = 8, color = "gray25"))

    if (!is.na(ymin) && !is.na(ymax)) {
        p <- p + coord_cartesian(ylim = c(ymin, ymax))
    }
    p
}

# F17a: extreme (< 1/4 SM), T0 = 2023Q4
p_A <- make_event_plot(
    INPUT_A, "2023Q4", "Renda < 1/4 SM", "#922B21",
    ymin = -4, ymax = 5,
    sub_caption = paste0(
        "Renda dom. per capita < 1/4 SM (extrema pobreza / prioridade BFA). ",
        "T0 = 2023Q4: aprovação do PdM no Congresso (dez/2023)."
    ))

# F17b: low (1/4-1/2 SM), T0 = 2024Q3
p_B <- make_event_plot(
    INPUT_B, "2024Q3", "1/4 a 1/2 SM", "#7D6608",
    ymin = -4, ymax = 5,
    sub_caption = paste0(
        "Renda dom. per capita entre 1/4 e 1/2 SM (CadÚnico-elegível não-BFA). ",
        "T0 = 2024Q3: expansão CadÚnico via Portaria 792 (ago/2024)."
    ))

ggsave(OUT_PDF_A, p_A, width = 11, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_A, p_A, width = 11, height = 5, dpi = 200)
ggsave(OUT_PDF_B, p_B, width = 11, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_B, p_B, width = 11, height = 5, dpi = 200)
cat("Saved F17a (extreme, T0=2023Q4) and F17b (low, T0=2024Q3)\n")
