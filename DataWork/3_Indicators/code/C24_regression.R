# -------------------------------------------------------------------------
# C24_regression.R
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Regressao linear de probabilidade (LPM) para evasao escolar usando
#   o painel longitudinal da PNADC (v5, sem rotacao 1).
#
#   Estrutura em blocos progressivos de controles:
#     (1) Demográficos: idade, sexo, raça
#     (2) Educacionais: defasagem, macroetapa
#     (3) Família: log renda PC, rede
#     (4) Localização: capital/RM/interior, UF FE
#     (5) Tempo: ano FE
#
#   Cluster SE: hh_id (idealmente)
#
# Inputs:
INPUT_PARQUET <- "../../3_Indicators/output/C20_transitions_v5.parquet"
#
# Outputs:
OUTPUT_TEX <- "../../3_Indicators/output/T_regressao_evasao.tex"
# -------------------------------------------------------------------------

if (!require("pacman")) install.packages("pacman")
pacman::p_load(arrow, dplyr, fixest, modelsummary, tidyr)

cat("Loading data...\n")
df <- read_parquet(INPUT_PARQUET)
cat("Rows:", nrow(df), "\n")

# Extract UF from person_id (first underscore-separated component)
df <- df %>%
    mutate(uf_t = as.integer(substr(person_id, 1, regexpr("_", person_id) - 1)),
           hh_id = sub("_[^_]+$", "", person_id))

# Build variables
df <- df %>%
    mutate(
        # Idade-padrao + defasagem
        idade_padrao = case_when(
            nivel_t %in% 1:9 ~ 5 + nivel_t,
            nivel_t == 10 ~ 15,
            nivel_t == 11 ~ 16,
            nivel_t == 12 ~ 17,
            nivel_t == 13 ~ 18,
            TRUE ~ NA_real_
        ),
        defasagem = idade_t - idade_padrao,
        defasagem_2plus = as.integer(defasagem >= 2),
        defasagem_1 = as.integer(defasagem >= 1 & defasagem < 2),
        # Sexo (V2007: 1=M, 2=F)
        feminino = as.integer(sexo_t == 2),
        # Raça
        preta_parda = as.integer(raca_t %in% c(2, 4)),
        amarela_indigena = as.integer(raca_t %in% c(3, 5)),
        # Reference: branca
        # Renda log
        log_renda = log(pmax(renda_t, 1)),
        # Macroetapa
        me_ef_finais = as.integer(macroetapa_t == "EF finais"),
        me_em        = as.integer(macroetapa_t == "EM"),
        # Reference: EF iniciais
        # Outcome and weights
        evasao = flag_evasao,
        wt = wt_t
    ) %>%
    # Drop NA controls
    filter(!is.na(defasagem), !is.na(feminino), !is.na(raca_t),
            !is.na(log_renda), !is.na(macroetapa_t))

cat("After filter:", nrow(df), "\n")
cat("Mean evasion:", mean(df$evasao, na.rm = TRUE), "\n")
cat("Mean evasion by macroetapa:\n")
print(df %>% group_by(macroetapa_t) %>%
        summarise(evasao = mean(evasao, na.rm = TRUE), n = n()))

# === Regressions: progressive controls ===
# All weighted by wt

# Block 1: demographic only
m1 <- feols(evasao ~ idade_t + feminino + preta_parda + amarela_indigena,
             data = df, weights = ~wt, cluster = ~hh_id)

# Block 2: + educational (defasagem, macroetapa)
m2 <- feols(evasao ~ idade_t + feminino + preta_parda + amarela_indigena
              + defasagem_1 + defasagem_2plus + me_ef_finais + me_em,
             data = df, weights = ~wt, cluster = ~hh_id)

# Block 3: + family (log renda)
m3 <- feols(evasao ~ idade_t + feminino + preta_parda + amarela_indigena
              + defasagem_1 + defasagem_2plus + me_ef_finais + me_em
              + log_renda,
             data = df, weights = ~wt, cluster = ~hh_id)

# Block 4: + school + ano FE
m4 <- feols(evasao ~ idade_t + feminino + preta_parda + amarela_indigena
              + defasagem_1 + defasagem_2plus + me_ef_finais + me_em
              + log_renda
              | ano_t,
             data = df, weights = ~wt, cluster = ~hh_id)

# Block 5: + UF FE
m5 <- feols(evasao ~ idade_t + feminino + preta_parda + amarela_indigena
              + defasagem_1 + defasagem_2plus + me_ef_finais + me_em
              + log_renda
              | ano_t + uf_t,
             data = df, weights = ~wt, cluster = ~hh_id)

# Summary table
cat("\n=== Block 1 ===\n"); print(summary(m1))
cat("\n=== Block 2 ===\n"); print(summary(m2))
cat("\n=== Block 3 ===\n"); print(summary(m3))
cat("\n=== Block 4 ===\n"); print(summary(m4))
cat("\n=== Block 5 ===\n"); print(summary(m5))

# Build LaTeX table with modelsummary
cm <- c(
    "idade_t"           = "Idade",
    "feminino"           = "Feminino",
    "preta_parda"        = "Preta/parda",
    "amarela_indigena"   = "Amarela/indígena",
    "defasagem_1"        = "Defasagem 1 ano",
    "defasagem_2plus"    = "Defasagem $\\geq$ 2 anos",
    "me_ef_finais"       = "EF finais",
    "me_em"              = "EM",
    "log_renda"          = "log(renda PC)"
)

ms_out <- modelsummary(
    list("(1)" = m1, "(2)" = m2, "(3)" = m3, "(4)" = m4, "(5)" = m5),
    coef_map = cm,
    gof_map = c("nobs", "r.squared"),
    stars = c("*" = 0.10, "**" = 0.05, "***" = 0.01),
    fmt = 4,
    escape = FALSE,
    output = "latex_tabular"
)

# Manual wrap with caption/threeparttable
tex_str <- paste(c(
    "% C24 regressao evasao",
    "\\begin{table}[htbp]\\centering",
    "\\caption{Regress\\~oes lineares de probabilidade para evas\\~ao escolar entre $t$ e $t+1$, painel longitudinal PNADC v5 (sem rota\\c{c}\\~ao 1), 2012--2023.}",
    "\\label{tab:reg_evasao}",
    "\\begin{threeparttable}",
    "\\footnotesize",
    as.character(ms_out),
    "\\begin{tablenotes}\\footnotesize",
    "\\item \\textit{Notas:} Modelos lineares de probabilidade ponderados pelo peso amostral $w_i^{P1}$, com erros padr\\~ao agrupados por indiv\\'iduo. Vari\\'avel dependente: \\texttt{flag\\_evasao}, igual a um se o aluno n\\~ao est\\'a matriculado em $t+1$ e n\\~ao migrou para EJA. Categorias de refer\\^encia: ra\\c{c}a branca, EF iniciais. As colunas (4) e (5) incluem efeitos fixos de ano e UF, respectivamente. $* p < 0.10$, $** p < 0.05$, $*** p < 0.01$.",
    "\\end{tablenotes}",
    "\\end{threeparttable}",
    "\\end{table}"
), collapse = "\n")

writeLines(tex_str, OUTPUT_TEX)
cat("\nSaved", OUTPUT_TEX, "\n")
