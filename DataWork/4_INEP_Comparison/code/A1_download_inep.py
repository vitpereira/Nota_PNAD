# -------------------------------------------------------------------------
# A1_download_inep.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Baixa os indicadores educacionais do INEP nos dois grupos relevantes:
#     A. TAXAS DE RENDIMENTO (Censo, anual): aprovacao, reprovacao, abandono
#     B. TAXAS DE TRANSICAO/FLUXO (longitudinal CPF): promocao, repetencia,
#        migracao EJA, evasao
#
#   URLs descobertas via playwright (clique nas abas dinamicas do INEP).
#   Os padroes mudam entre eras de divulgacao:
#     2007-2011: subdir "informacoes_estatisticas/2011/..."
#     2012:      subdir "taxas_rendimento" (plural)
#     2013-2015: subdir "taxa_rendimento" (singular)
#     2016-2017: UPPER, sem subdir, ordem REND_<ANO>_<TIPO>
#     2018:      UPPER, sem subdir, ordem REND_<TIPO>_<ANO>
#     2019-2024: lowercase, sem subdir, ordem rend_<TIPO>_<ANO>
#
#   Ultima divulgacao INEP (junho 2026):
#     - Rendimento: 2024 (publicado ago/2025)
#     - Transicao:  2021-2022 (publicado jul/2025)
# -------------------------------------------------------------------------

import os
import sys
import csv
import time
import requests
from pathlib import Path

# { Paths ----
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "tmp" / "inep_raw"
REND_DIR = RAW_DIR / "rendimento"
TRANS_DIR = RAW_DIR / "transicao"
DOCS_DIR = RAW_DIR / "docs"
OUT_DIR = ROOT / "output"
for d in (REND_DIR, TRANS_DIR, DOCS_DIR, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)
# } ----

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = 120


# { URLs descobertas via playwright ----
def rendimento_urls():
    """Padroes especificos por era de divulgacao."""
    base = "https://download.inep.gov.br/informacoes_estatisticas"
    urls = []
    # Era 1: 2007-2011 (batch publicado em 2011)
    for ano in range(2007, 2012):
        for sufix in ["brasil_regioes_UFs", "municipios", "escolas"]:
            urls.append((
                f"{base}/2011/indicadores_educacionais/taxa_rendimento/{ano}/tx_rendimento_{sufix}_{ano}.zip",
                REND_DIR / f"tx_rendimento_{sufix}_{ano}.zip"
            ))
    # Era 2: 2012 (taxas_rendimento PLURAL)
    for sufix in ["brasil_regioes_UFs", "municipios", "escolas"]:
        urls.append((
            f"{base}/indicadores_educacionais/2012/taxas_rendimento/tx_rendimento_{sufix}_2012.zip",
            REND_DIR / f"tx_rendimento_{sufix}_2012.zip"
        ))
    # Era 3: 2013-2015 (taxa_rendimento SINGULAR)
    for ano in range(2013, 2016):
        for sufix in ["brasil_regioes_UFs", "municipios", "escolas"]:
            urls.append((
                f"{base}/indicadores_educacionais/{ano}/taxa_rendimento/tx_rendimento_{sufix}_{ano}.zip",
                REND_DIR / f"tx_rendimento_{sufix}_{ano}.zip"
            ))
    # Era 4: 2016-2017 (UPPER, ordem REND_<ANO>_<TIPO>)
    for ano in (2016, 2017):
        for sufix in ["BRASIL_REGIOES_UFS", "MUNICIPIOS", "ESCOLAS"]:
            urls.append((
                f"{base}/indicadores_educacionais/{ano}/TAXA_REND_{ano}_{sufix}.zip",
                REND_DIR / f"TAXA_REND_{ano}_{sufix}.zip"
            ))
    # Era 5: 2018 (UPPER, ordem REND_<TIPO>_<ANO>)
    for sufix in ["BRASIL_REGIOES_UFS", "MUNICIPIOS", "ESCOLAS"]:
        urls.append((
            f"{base}/indicadores_educacionais/2018/TX_REND_{sufix}_2018.zip",
            REND_DIR / f"TX_REND_{sufix}_2018.zip"
        ))
    # Era 6: 2019-2024 (lowercase, sem subdir)
    for ano in range(2019, 2025):
        for sufix in ["brasil_regioes_ufs", "municipios", "escolas"]:
            urls.append((
                f"{base}/indicadores_educacionais/{ano}/tx_rend_{sufix}_{ano}.zip",
                REND_DIR / f"tx_rend_{sufix}_{ano}.zip"
            ))
    return urls


def transicao_urls():
    """Padrao unificado para Taxa de Transicao 2007-2022."""
    base = "https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/taxa_transicao"
    urls = []
    for ano1 in range(2007, 2022):
        ano2 = ano1 + 1
        for sufix in ["brasil_regioes_ufs", "municipios"]:
            urls.append((
                f"{base}/tx_transicao_{sufix}_{ano1}_{ano2}.zip",
                TRANS_DIR / f"tx_transicao_{sufix}_{ano1}_{ano2}.zip"
            ))
    return urls


def docs_urls():
    base = "https://download.inep.gov.br"
    return [
        (f"{base}/informacoes_estatisticas/indicadores_educacionais/2007_2016/nota_tecnica_taxas_transicao_2007_2016.pdf",
         DOCS_DIR / "nota_tecnica_taxas_transicao_2007_2016.pdf"),
        (f"{base}/informacoes_estatisticas/indicadores_educacionais/2017/metodologia_indicadores_trajetoria_curso.pdf",
         DOCS_DIR / "metodologia_indicadores_trajetoria_curso.pdf"),
        (f"{base}/publicacoes/institucionais/estatisticas_e_indicadores/dicionario_de_indicadores_educacionais_formulas_de_calculo.pdf",
         DOCS_DIR / "dicionario_de_indicadores_educacionais_formulas_de_calculo.pdf"),
        (f"{base}/publicacoes/institucionais/estatisticas_e_indicadores/notas_estatisticas_censo_da_educacao_basica_2024.pdf",
         DOCS_DIR / "notas_estatisticas_censo_da_educacao_basica_2024.pdf"),
    ]
# } ----


def download(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest.stat().st_size, "skipped"
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS, stream=True, verify=False)
        if r.status_code == 404:
            return 0, "http_404"
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)
        sz = dest.stat().st_size
        if sz < 500:
            with open(dest, "rb") as fh:
                head = fh.read(500)
            if b"<html" in head.lower():
                dest.unlink()
                return 0, "html_error_page"
        return sz, "downloaded"
    except Exception as e:
        return 0, f"err:{str(e)[:60]}"


def main():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    log = []

    for grupo, urls_fn in [("rendimento", rendimento_urls), ("transicao", transicao_urls), ("docs", docs_urls)]:
        print(f"\n{'='*70}\n{grupo.upper()}\n{'='*70}")
        for url, dest in urls_fn():
            sz, status = download(url, dest)
            log.append({"grupo": grupo, "url": url, "file": dest.name, "size_mb": sz/1e6, "status": status})
            emoji = "OK" if status in ("downloaded", "skipped") else "X "
            print(f"  [{emoji}] {dest.name}: {status} ({sz/1e6:.1f} MB)")

    log_path = OUT_DIR / "inep_download_log.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["grupo", "url", "file", "size_mb", "status"])
        writer.writeheader()
        writer.writerows(log)

    n_ok = sum(1 for r in log if r["status"] in ("downloaded", "skipped"))
    print(f"\n{'='*70}")
    print(f"OK:    {n_ok}/{len(log)}")
    print(f"FAIL:  {len(log)-n_ok}/{len(log)}")
    print(f"Log:   {log_path}")


if __name__ == "__main__":
    main()
