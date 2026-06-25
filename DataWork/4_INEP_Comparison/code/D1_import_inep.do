* -------------------------------------------------------------------------
* D1_import_inep.do
* -------------------------------------------------------------------------
* Author: Vitor
* Last update: 2026-06-24
*
* Description:
*   Importa os arquivos baixados do INEP (xlsx ou csv) e padroniza em um
*   .dta longo com colunas: ano, uf, etapa, rede, indicador, valor.
*
*   ATENCAO: as estruturas dos xlsx do INEP variam por ano. Este script
*   tenta os formatos mais comuns. Pode precisar de ajuste manual.
*
* Inputs:
*   tmp/inep_raw/*.xlsx
*   tmp/inep_raw/*.zip   (unzipped first)
*
* Outputs:
local INEP_LONG  "$OUTDIR/inep_indicadores_long.dta"
* -------------------------------------------------------------------------

* PLACEHOLDER: este script depende de quais arquivos do INEP foram baixados
* com sucesso. Sera completado apos validar o download.

* Estrutura tipica do INEP .xlsx (Taxas de Rendimento):
*   Aba "Brasil_Regiao_UF": colunas com NU_ANO_CENSO, NO_REGIAO, NO_UF,
*                          CO_UF, CO_LOCALIZACAO_FISICA (urbano/rural),
*                          CO_REDE (federal/estadual/municipal/privada),
*                          taxas por etapa (1_EF, 2_EF, ..., 1_EM, 2_EM, 3_EM)

* Por enquanto, criar um placeholder vazio para que o pipeline rode
clear
set obs 1
gen ano = .
gen uf = ""
gen etapa = ""
gen rede = ""
gen indicador = ""
gen valor = .

drop in 1   // tira a linha placeholder
save "`INEP_LONG'", replace
di "D1 OK (placeholder - aguardar download dos arquivos INEP)"
