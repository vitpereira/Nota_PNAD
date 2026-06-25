# -------------------------------------------------------------------------
# _master.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-24
#
# Description:
#   Pipeline do modulo 1_DownloadPNADC:
#     A1: download PNADC trimestral 2012Q1-2024Q4 (FTP IBGE)
#     A2: parse fixed-width -> parquet (1 por trim) + consolidado .dta
#
# Como rodar:
#   cd 1_DownloadPNADC/code
#   python _master.py
#
# Tempo esperado: ~4-6h (gargalo: download)
# -------------------------------------------------------------------------

import sys
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

SCRIPTS = [
    "A1_download_pnadc_trimestral.py",
    "A2_parse_pnadc_trimestral.py",
]


def main():
    for s in SCRIPTS:
        script_path = HERE / s
        print(f"\n{'='*70}")
        print(f"RUNNING: {s}")
        print(f"{'='*70}")
        rc = subprocess.call([sys.executable, str(script_path)])
        if rc != 0:
            print(f"\nERRO: {s} terminou com codigo {rc}")
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
