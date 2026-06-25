# -------------------------------------------------------------------------
# A2_parse_inep.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Parseia os arquivos XLSX do INEP (Rendimento + Transicao) baixados em
#   A1, extraindo as taxas por etapa em formato longo:
#     ano, uf, etapa, rede, indicador, valor
#
# Inputs:
#   tmp/inep_raw/rendimento/*.zip
#   tmp/inep_raw/transicao/*.zip
#
# Outputs:
#   output/inep_rendimento_long.csv
#   output/inep_transicao_long.csv
# -------------------------------------------------------------------------

import os
import sys
import zipfile
import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "tmp" / "inep_raw"
REND_DIR = RAW_DIR / "rendimento"
TRANS_DIR = RAW_DIR / "transicao"
EXTRACT_DIR = RAW_DIR / "extracted"
OUT_DIR = ROOT / "output"
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


def unzip_all(src_dir, target_dir):
    """Extrai todos os zips de src_dir para target_dir."""
    extracted = []
    for zf_path in sorted(src_dir.glob("*.zip")):
        try:
            with zipfile.ZipFile(zf_path) as zf:
                zf.extractall(target_dir)
                xlsx_files = [n for n in zf.namelist() if n.endswith(".xlsx") and "~$" not in n]
                for x in xlsx_files:
                    extracted.append((zf_path.stem, target_dir / x))
        except Exception as e:
            print(f"  ERR unzip {zf_path.name}: {e}")
    return extracted


def parse_transicao_xlsx(path, ano1, ano2):
    """Le um XLSX de Taxa de Transicao do INEP e retorna df longo."""
    try:
        # As tabelas do INEP tem header em multiple rows. Tentar ler com varias estrategias
        df = pd.read_excel(path, sheet_name=0, skiprows=8, header=[0, 1])
    except Exception as e:
        print(f"  ERR parse {path}: {e}")
        return None

    # Estrutura tipica do INEP:
    # NU_ANO_CENSO, UF (or NO_REGIAO), CO_REGIAO/UF, NO_UF (or aggregate),
    # CO_LOCALIZACAO_FISICA, ...
    # Taxas: 1o EF, 2o EF, ..., 9o EF, 1o EM, 2o EM, 3o EM
    # Com 4 colunas para cada etapa: promocao, repetencia, migracao_EJA, evasao

    df.columns = ['_'.join([str(c) for c in col]).strip() if isinstance(col, tuple) else str(col)
                  for col in df.columns]
    df.columns = [c.strip().replace('Unnamed: ', 'col_').replace('\n', '_') for c in df.columns]
    return df


def main():
    print("=" * 70)
    print("Extraindo zips...")
    print("=" * 70)

    extracted_rend = unzip_all(REND_DIR, EXTRACT_DIR / "rendimento")
    extracted_trans = unzip_all(TRANS_DIR, EXTRACT_DIR / "transicao")
    print(f"  Rendimento: {len(extracted_rend)} xlsx extraidos")
    print(f"  Transicao:  {len(extracted_trans)} xlsx extraidos")

    # Por enquanto: salvar lista de arquivos extraidos como log
    log = []
    for tag, path in extracted_trans:
        # Parse ano-ano do nome
        m = re.search(r'(\d{4})_(\d{4})', tag)
        if not m:
            continue
        ano1, ano2 = m.group(1), m.group(2)
        log.append({"tipo": "transicao", "ano1": ano1, "ano2": ano2,
                    "path": str(path), "tag": tag})

    for tag, path in extracted_rend:
        m = re.search(r'(\d{4})', tag)
        if not m:
            continue
        ano = m.group(1)
        log.append({"tipo": "rendimento", "ano1": ano, "ano2": ano,
                    "path": str(path), "tag": tag})

    df_log = pd.DataFrame(log)
    log_path = OUT_DIR / "inep_extracted_files.csv"
    df_log.to_csv(log_path, index=False)
    print(f"\n  Log salvo em: {log_path}")
    print(f"  Total: {len(df_log)} arquivos")

    # Para parse detalhado, ler 1 arquivo e mostrar estrutura
    if len(extracted_trans) > 0:
        sample_path = extracted_trans[-1][1]
        print(f"\nExemplo de parse: {sample_path.name}")
        try:
            df = pd.read_excel(sample_path, sheet_name=0, nrows=20, header=None)
            print(df.head(15).to_string(max_colwidth=20))
        except Exception as e:
            print(f"Erro: {e}")


if __name__ == "__main__":
    main()
