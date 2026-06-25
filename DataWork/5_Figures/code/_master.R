# -------------------------------------------------------------------------
# _master.R - Modulo 5: Figuras (ggplot2)
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-24
#
# Description:
#   Pipeline de figuras. Le os CSVs gerados pelo modulo 3_Indicators e
#   4_INEP_Comparison e produz as figuras finais em PDF.
#
#   Figuras canonicas:
#     F1: Series temporais 2012-2024, 4 paineis (aprov/repro/aband/evasao)
#     F2: Gradientes por renda e raca (1o EM)
#     F3: Captura de retorno por subgrupo
#     F4: Caracteristicas dos retidos vs. perdidos no painel (robustez)
#
# Padroes (per rules/figures.md):
#   - Sem titulo embedido (labs(title=NULL))
#   - Serif font (theme_minimal(base_family="serif"))
#   - Anos completos no eixo x quando < 20 ticks
#   - Output: PDF e PNG (este ultimo p/ slides)
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")

# { Paths ----
ROOT       <- "C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD"
MOD_ROOT   <- file.path(ROOT, "DataWork", "5_Figures")
INDIC_OUT  <- file.path(ROOT, "DataWork", "3_Indicators", "output")
COMP_OUT   <- file.path(ROOT, "DataWork", "4_INEP_Comparison", "output")
CODDIR     <- file.path(MOD_ROOT, "code")
OUTDIR     <- file.path(MOD_ROOT, "output")
TMPDIR     <- file.path(MOD_ROOT, "tmp")
dir.create(OUTDIR, recursive = TRUE, showWarnings = FALSE)
dir.create(TMPDIR, recursive = TRUE, showWarnings = FALSE)

setwd(CODDIR)
# } ----

# { Packages ----
pacman::p_load(tidyverse, scales, ggrepel, patchwork, ggthemes, RColorBrewer)
# } ----

# { Theme global ----
theme_paper <- theme_minimal(base_family = "serif", base_size = 11) +
    theme(
        panel.grid.minor = element_blank(),
        legend.position  = "bottom",
        legend.title     = element_blank(),
        plot.title       = element_blank(),
        plot.subtitle    = element_blank()
    )
theme_set(theme_paper)
# } ----

# { Pipeline ----
source(file.path(CODDIR, "F1_serie_temporal.R"))
source(file.path(CODDIR, "F2_gradientes_renda_raca.R"))
source(file.path(CODDIR, "F3_captura_retorno.R"))
source(file.path(CODDIR, "F4_atrito_robustez.R"))
source(file.path(CODDIR, "F4_cohort_fluxo.R"))
source(file.path(CODDIR, "F5_pnadc_vs_inep.R"))
# } ----

cat("\nFiguras geradas em:", OUTDIR, "\n")
