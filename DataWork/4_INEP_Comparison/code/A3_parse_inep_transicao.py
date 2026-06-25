# -------------------------------------------------------------------------
# A3_parse_inep_transicao.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Parseia xlsx INEP Taxas de Transicao (Brasil/Regiao/UF) para formato
#   longo. Trata 2 formatos:
#     - "Antigo" (2007/08 a 2016/17): 4 cols ID + 64 cols indicadores = 68 total
#     - "Novo" (2017/18 a 2021/22): 7 cols ID + 64 cols indicadores = 71 total
#
#   64 cols indicador = 4 indicadores x 16 etapa-subcolunas
#     Indicadores: promocao, repetencia, evasao, migracao_eja
#     Etapa: Total_EF, EF anos iniciais, EF anos finais, EF 1-9 (12 cols)
#            Total_EM, EM 1a-3a (4 cols) = 16 cols
#
# Inputs:
#   tmp/inep_raw/extracted/transicao/**/TX_TRANSICAO_BRASIL_REGIOES_UFS_*.xlsx
#
# Outputs:
#   output/inep_transicao_long.csv
# -------------------------------------------------------------------------

import os
import re
import sys
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACT_DIR = ROOT / "tmp" / "inep_raw" / "extracted" / "transicao"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ETAPA_COLS = ['Total_EF', 'EF_AI', 'EF_AF',
              'EF_1', 'EF_2', 'EF_3', 'EF_4', 'EF_5',
              'EF_6', 'EF_7', 'EF_8', 'EF_9',
              'Total_EM', 'EM_1', 'EM_2', 'EM_3']

INDICADORES = ['promocao', 'repetencia', 'evasao', 'migracao_eja']


def parse_one_xlsx(path):
    try:
        df = pd.read_excel(path, sheet_name=0, header=None, skiprows=9)
    except Exception as e:
        print(f"  ERR: {path.name}: {e}")
        return None

    n_cols = df.shape[1]
    n_data_cols = 64

    if n_cols == 68:
        # Old format: 4 ID + 64 data
        id_cols = ['ANO', 'NO_CODIGO', 'TIPOLOCA', 'DEPENDAD']
    elif n_cols == 71:
        # New format: 7 ID + 64 data
        id_cols = ['NU_ANO_CENSO', 'NO_REGIAO', 'NO_UF', 'CO_MUNICIPIO',
                   'NO_MUNICIPIO', 'NO_LOCALIZACAO', 'NO_DEPENDENCIA']
    else:
        print(f"  SKIP {path.name}: {n_cols} colunas (esperado 68 ou 71)")
        return None

    # Build data column names
    data_cols = []
    for ind in INDICADORES:
        for etapa in ETAPA_COLS:
            data_cols.append(f"{ind}__{etapa}")

    df.columns = id_cols + data_cols

    # Filtrar Total/Total (sem dependencia/localizacao filter)
    if n_cols == 68:
        df = df[(df['TIPOLOCA'].astype(str).str.strip() == 'Total') &
                (df['DEPENDAD'].astype(str).str.strip() == 'Total')]
        df = df.rename(columns={'NO_CODIGO': 'unidade', 'ANO': 'ano_str'})
    else:
        df = df[(df['NO_LOCALIZACAO'].astype(str).str.strip() == 'Total') &
                (df['NO_DEPENDENCIA'].astype(str).str.strip() == 'Total')]
        df = df[df['CO_MUNICIPIO'].isna() | (df['CO_MUNICIPIO'].astype(str).str.strip() == '')]
        df['unidade'] = df['NO_REGIAO'].fillna('Brasil')
        df.loc[df['NO_UF'].notna(), 'unidade'] = df.loc[df['NO_UF'].notna(), 'NO_UF']
        df['ano_str'] = df['NU_ANO_CENSO']

    df = df[['ano_str', 'unidade'] + data_cols]

    if len(df) == 0:
        return None

    # Reshape
    df_long = df.melt(id_vars=['ano_str', 'unidade'], var_name='ind_etapa',
                     value_name='valor')
    df_long[['indicador', 'etapa']] = df_long['ind_etapa'].str.split('__', expand=True)
    df_long = df_long.drop(columns=['ind_etapa'])
    df_long['valor'] = pd.to_numeric(df_long['valor'], errors='coerce')
    df_long = df_long[df_long['valor'].notna()]

    return df_long


def main():
    files_all = list(EXTRACT_DIR.rglob("*BRASIL_REGIOES*UFS*.xlsx"))
    files_all += list(EXTRACT_DIR.rglob("*brasil_regioes*ufs*.xlsx"))
    files_all = list(set([str(f) for f in files_all if "~$" not in f.name]))
    files_all = sorted([Path(f) for f in files_all])
    print(f"Arquivos unicos: {len(files_all)}")

    all_dfs = []
    for f in files_all:
        print(f"  {f.name}...")
        df = parse_one_xlsx(f)
        if df is not None:
            m = re.search(r'(\d{4})_(\d{4})', f.name)
            if m:
                df['ano_t'] = int(m.group(1))
                df['ano_t1'] = int(m.group(2))
            all_dfs.append(df)
            print(f"    {len(df):,} obs")

    if all_dfs:
        big = pd.concat(all_dfs, ignore_index=True)
        out = OUT_DIR / "inep_transicao_long.csv"
        big.to_csv(out, index=False, encoding='utf-8')
        print(f"\nSalvo: {out} ({len(big):,} obs)")
        print(f"\nIndicadores: {sorted(big['indicador'].unique())}")
        print(f"Etapas: {sorted(big['etapa'].unique())}")
        print(f"Anos t: {sorted(big['ano_t'].unique())}")
        print(f"\nPreview Brasil 1o EM evasao:")
        bras = big[(big['unidade'] == 'Brasil') &
                   (big['etapa'] == 'EM_1') &
                   (big['indicador'] == 'evasao')]
        print(bras[['ano_t', 'valor']].sort_values('ano_t').to_string(index=False))
    else:
        print("Nenhum parseado")


if __name__ == "__main__":
    main()
