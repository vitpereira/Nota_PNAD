# -------------------------------------------------------------------------
# A1_download_pnadc_trimestral.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-24
#
# Description:
#   Baixa todos os microdados PNADC TRIMESTRAL (não Anual!) do FTP do IBGE
#   de 2012Q1 a 2024Q4 (52 trimestres). Para cada trimestre baixa:
#     - PNADC_<TT><AAAA>.zip  (microdados em txt fixed-width)
#   Também baixa documentação (dicionario .xls + input SAS .txt) que dá
#   as posições das colunas no arquivo fixed-width.
#
#   Total esperado: ~52 arquivos zip, ~3-4 GB.
#
# Inputs:
#   FTP IBGE (HTTPS):
#     /Trimestral/Microdados/AAAA/PNADC_TTAAAA.zip
#     /Trimestral/Microdados/Documentacao/input_PNADC_trimestral.txt
#     /Trimestral/Microdados/Documentacao/dicionario_PNADC_microdados_trimestral.xls
#
# Outputs:
#   tmp/pnad_raw/PNADC_<TTAAAA>.zip      (microdados, 52 arquivos)
#   tmp/pnad_raw/docs/input_PNADC_trimestral.txt
#   tmp/pnad_raw/docs/dicionario_PNADC_microdados_trimestral.xls
#   output/download_log.csv              (manifest com tamanho e timestamp)
# -------------------------------------------------------------------------

import os
import re
import sys
import time
import csv
import requests
from pathlib import Path
from datetime import datetime

# { Paths ----
ROOT = Path(__file__).resolve().parent.parent  # 1_DownloadPNADC
TMPDIR = ROOT / "tmp" / "pnad_raw"
DOCSDIR = TMPDIR / "docs"
OUTDIR = ROOT / "output"
TMPDIR.mkdir(parents=True, exist_ok=True)
DOCSDIR.mkdir(parents=True, exist_ok=True)
OUTDIR.mkdir(parents=True, exist_ok=True)
# } ----

# { Config ----
BASE = "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados"
DOCS_URL = f"{BASE}/Documentacao/"

YEARS = list(range(2012, 2025))  # 2012-2024
QUARTERS = [1, 2, 3, 4]

HEADERS = {"User-Agent": "Mozilla/5.0 (research; vitpereira@gmail.com)"}
TIMEOUT = 180
CHUNK = 1024 * 1024  # 1 MB
RETRIES = 3
# } ----


def list_files(url):
    """Lista arquivos de um diretório do FTP via HTML (apache index)."""
    r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    r.raise_for_status()
    links = re.findall(r'href="([^"]+)"', r.text)
    return [l for l in links if not l.startswith("/") and not l.startswith("?")]


def download(url, dest, label=""):
    """Baixa arquivo com retry e skip-if-exists."""
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [SKIP] {label}: ja existe ({dest.stat().st_size/1e6:.1f} MB)")
        return dest.stat().st_size, "skipped"

    for attempt in range(1, RETRIES + 1):
        try:
            print(f"  [GET ] {label} (tentativa {attempt}): {url}")
            t0 = time.time()
            with requests.get(url, timeout=TIMEOUT, headers=HEADERS, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(dest, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=CHUNK):
                        if chunk:
                            fh.write(chunk)
                            downloaded += len(chunk)
            dt = time.time() - t0
            size = dest.stat().st_size
            print(f"  [DONE] {label}: {size/1e6:.1f} MB em {dt:.1f}s")
            return size, "downloaded"
        except Exception as e:
            print(f"  [ERR ] {label}: {e}")
            if dest.exists():
                dest.unlink()
            if attempt == RETRIES:
                return 0, f"failed: {e}"
            time.sleep(5 * attempt)
    return 0, "failed"


def main():
    log_rows = []

    # { 1. Documentacao ----
    print("=" * 70)
    print("Baixando documentacao (dicionario + input SAS)")
    print("=" * 70)
    try:
        doc_files = list_files(DOCS_URL)
    except Exception as e:
        print(f"ERRO ao listar Documentacao: {e}")
        doc_files = []

    # Pegar o input mais recente
    inputs = [f for f in doc_files if f.startswith("input_PNADC_trimestral") and f.endswith(".txt")]
    dicts = [f for f in doc_files if f.startswith("dicionario_PNADC_microdados_trimestral") and f.endswith(".xls")]

    if inputs:
        fname = sorted(inputs)[-1]
        url = DOCS_URL + fname
        dest = DOCSDIR / "input_PNADC_trimestral.txt"
        sz, status = download(url, dest, label=f"input {fname}")
        log_rows.append({"file": fname, "size_mb": sz/1e6, "status": status, "type": "input"})
    else:
        print("  AVISO: nenhum input_PNADC_trimestral encontrado")

    if dicts:
        fname = sorted(dicts)[-1]
        url = DOCS_URL + fname
        dest = DOCSDIR / "dicionario_PNADC_microdados_trimestral.xls"
        sz, status = download(url, dest, label=f"dict {fname}")
        log_rows.append({"file": fname, "size_mb": sz/1e6, "status": status, "type": "dict"})
    else:
        print("  AVISO: nenhum dicionario encontrado")
    # } ----

    # { 2. Microdados por ano-trimestre ----
    print("\n" + "=" * 70)
    print(f"Baixando microdados trimestrais ({YEARS[0]}-{YEARS[-1]})")
    print("=" * 70)

    total_size = 0
    n_ok = 0
    n_fail = 0
    n_skip = 0

    for year in YEARS:
        year_url = f"{BASE}/{year}/"
        try:
            year_files = list_files(year_url)
        except Exception as e:
            print(f"[{year}] ERRO ao listar: {e}")
            continue

        zips_in_year = [f for f in year_files if f.endswith(".zip") and "PNADC_" in f]

        for q in QUARTERS:
            # Padrao: PNADC_TTAAAA.zip - ex.: PNADC_012023.zip
            pattern = f"PNADC_{q:02d}{year}"
            candidates = [f for f in zips_in_year if pattern in f]

            if not candidates:
                print(f"[{year}Q{q}] NAO ENCONTRADO no FTP")
                log_rows.append({"file": f"PNADC_{q:02d}{year}.zip", "size_mb": 0, "status": "not_found", "type": "data"})
                n_fail += 1
                continue

            # Pegar o mais recente (maior sufixo se houver revisao)
            fname = sorted(candidates)[-1]
            url = year_url + fname
            dest = TMPDIR / f"PNADC_{q:02d}{year}.zip"

            sz, status = download(url, dest, label=f"data {year}Q{q}")
            log_rows.append({"file": fname, "size_mb": sz/1e6, "status": status, "type": "data"})

            if "downloaded" in status:
                n_ok += 1
                total_size += sz
            elif status == "skipped":
                n_skip += 1
                total_size += sz
            else:
                n_fail += 1
    # } ----

    # { 3. Salvar log ----
    log_path = OUTDIR / "download_log.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["file", "size_mb", "status", "type"])
        writer.writeheader()
        writer.writerows(log_rows)
    print(f"\nLog salvo em: {log_path}")
    # } ----

    # { 4. Resumo ----
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"  Trimestres baixados (novos):    {n_ok}")
    print(f"  Trimestres ja em disco (skip):  {n_skip}")
    print(f"  Falhas / nao encontrados:       {n_fail}")
    print(f"  Tamanho total:                  {total_size/1e9:.2f} GB")
    print(f"  Concluido em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # } ----

    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
