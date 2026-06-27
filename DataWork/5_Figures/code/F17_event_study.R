# -------------------------------------------------------------------------
# F17_event_study.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Dois plots event study TWFE separados. Convencao da literatura:
#   omitir o trimestre IMEDIATAMENTE ANTERIOR ao choque como referencia.
#     F17a: Renda < 1/4 SM. Choque = 2023Q4 (anuncio). Omitido: 2023Q3.
#     F17b: 1/4 a 1/2 SM.   Choque = 2024Q3 (expansao). Omitido: 2024Q2.
#   Outcome: matricula em EM regular OU EJA EM OU ja concluiu EM.
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

make_event_plot <- function(input_path, base_yrq, shock_yrq,
                              label, color, shock_descr,
                              ymin = NA, ymax = NA, sub_caption = "") {
    d <- read_csv(input_path, show_col_types = FALSE)
    base_ano  <- as.integer(str_sub(base_yrq, 1, 4))
    base_trim <- as.integer(str_sub(base_yrq, 6, 6))
    x_baseline <- base_ano + (base_trim - 0.5) / 4
    shock_ano  <- as.integer(str_sub(shock_yrq, 1, 4))
    shock_trim <- as.integer(str_sub(shock_yrq, 6, 6))
    x_shock <- shock_ano + (shock_trim - 0.5) / 4

    p <- ggplot(d, aes(x = x, y = estimate)) +
        geom_ribbon(aes(ymin = conf.low, ymax = conf.high),
                     fill = color, alpha = 0.18) +
        geom_hline(yintercept = 0, color = "gray40", linewidth = 0.4) +
        # Linha do trimestre omitido (k = -1, referencia)
        geom_vline(xintercept = x_baseline, color = "gray50",
                    linetype = "dotted", linewidth = 0.4) +
        # Linha do choque (k = 0, momento do tratamento)
        geom_vline(xintercept = x_shock, color = "gray20",
                    linetype = "dashed", linewidth = 0.5) +
        geom_line(linewidth = 0.7, color = color) +
        geom_point(size = 1.8, color = color, shape = 16) +
        annotate("text", x = x_baseline, y = Inf,
                  label = sprintf("Referência\n(omitido)\n%s = k–1", base_yrq),
                  size = 2.5, family = "serif", color = "gray35",
                  hjust = 1.05, vjust = 1.6) +
        annotate("text", x = x_shock, y = Inf,
                  label = sprintf("Choque\n%s\n%s = k 0", shock_descr, shock_yrq),
                  size = 2.5, family = "serif", color = "gray25",
                  hjust = -0.05, vjust = 1.6) +
        scale_x_continuous(
            breaks = seq(2023.125, 2025.875, 0.25),
            labels = c("2023Q1","Q2","Q3","Q4",
                        "2024Q1","Q2","Q3","Q4",
                        "2025Q1","Q2","Q3","Q4")
        ) +
        scale_y_continuous(labels = function(x) paste0(x, " p.p.")) +
        labs(x = NULL,
              y = sprintf("Δ tratado (%s) − controle (>1/2 SM), p.p.", label),
              title = NULL,
              caption = paste0(
                  sub_caption,
                  " Convenção: omitido o trimestre k=–1 (referência, normalizado a zero). ",
                  "Choque em k=0. Banda colorida: IC 95% com SE clusterizados em domicílio. ",
                  "Outcome: matriculado em EM regular OU EJA EM OU já concluiu EM. ",
                  "Universo: jovens 15-19 anos. TWFE com FE de UF e trimestre. Pesos: V1028."
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

# F17a: extreme (< 1/4 SM), choque = 2023Q4, omitido = 2023Q3
p_A <- make_event_plot(
    INPUT_A, base_yrq = "2023Q3", shock_yrq = "2023Q4",
    label = "Renda < R$ 230", color = "#922B21",
    shock_descr = "Anúncio PdM (dez/2023)",
    ymin = -4, ymax = 7,
    sub_caption = paste0(
        "Renda dom. per capita < R$ 230 (linha de extrema pobreza / prioridade BFA)."
    ))

# F17b: low (1/4-1/2 SM), choque = 2024Q3, omitido = 2024Q2
p_B <- make_event_plot(
    INPUT_B, base_yrq = "2024Q2", shock_yrq = "2024Q3",
    label = "R$ 230 a 1/2 SM", color = "#7D6608",
    shock_descr = "Expansão CadÚnico (ago/2024)",
    ymin = -4, ymax = 7,
    sub_caption = paste0(
        "Renda dom. per capita entre R$ 230 e 1/2 SM (CadÚnico-elegível não-BFA)."
    ))

ggsave(OUT_PDF_A, p_A, width = 9, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_A, p_A, width = 9, height = 5, dpi = 150)
ggsave(OUT_PDF_B, p_B, width = 9, height = 5, device = cairo_pdf)
ggsave(OUT_PNG_B, p_B, width = 9, height = 5, dpi = 150)
cat("Saved F17a and F17b com convencao da literatura (k=-1 omitido).\n")
