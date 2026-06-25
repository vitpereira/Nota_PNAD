# -------------------------------------------------------------------------
# _master.py - Pipeline completo do projeto Nota_PNAD
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-24
#
# Description:
#   Orquestra a execucao completa do pipeline:
#     1. Download e parsing PNADC trimestral (Python)       -- ~4-5h
#     2. Construcao do painel longitudinal (Stata)          -- ~45min
#     3. Calculo dos 5 indicadores (Stata)                  -- ~30min
#     4. Download INEP (Python, manual fallback)            -- ~30min
#     5. Comparacao PNADC x INEP + decomposicao (Stata)     -- ~20min
#     6. Figuras com ggplot2 (R)                            -- ~10min
#     7. Compilacao LaTeX (pdflatex + bibtex)               -- ~2min
#
#   Total: ~6-7h em primeira execucao; ~1h em re-execucao parcial.
#
# Como rodar:
#   cd Nota_PNAD/
#   python _master.py [--stages 1,2,3,4,5,6,7]
#
#   Exemplo: rodar so estagios 3-6 (assumindo 1-2 ja rodados):
#     python _master.py --stages 3,4,5,6
# -------------------------------------------------------------------------

import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

# Executaveis
STATA  = "C:/Program Files/StataNow19/StataMP-64.exe"
RSCRIPT = "C:/Program Files/R/R-4.5.0/bin/Rscript.exe"
PYTHON = sys.executable

# Stages do pipeline
STAGES = {
    "1": {
        "name": "Download e parsing PNADC trimestral",
        "cmd": [PYTHON, str(ROOT / "DataWork/1_DownloadPNADC/code/_master.py")],
        "time_est": "4-5h",
    },
    "2": {
        "name": "Construcao do painel longitudinal",
        "cmd": [STATA, "-e", "do", str(ROOT / "DataWork/2_PanelBuild/code/_master.do")],
        "time_est": "45min",
    },
    "3": {
        "name": "Calculo dos 5 indicadores",
        "cmd": [STATA, "-e", "do", str(ROOT / "DataWork/3_Indicators/code/_master.do")],
        "time_est": "30min",
    },
    "4": {
        "name": "Download INEP (manual fallback)",
        "cmd": [PYTHON, str(ROOT / "DataWork/4_INEP_Comparison/code/A1_download_inep.py")],
        "time_est": "30min",
    },
    "5": {
        "name": "Comparacao PNADC x INEP + decomposicao",
        "cmd": [STATA, "-e", "do", str(ROOT / "DataWork/4_INEP_Comparison/code/_master.do")],
        "time_est": "20min",
    },
    "6": {
        "name": "Figuras (ggplot2)",
        "cmd": [RSCRIPT, str(ROOT / "DataWork/5_Figures/code/_master.R")],
        "time_est": "10min",
    },
    "7": {
        "name": "Compilacao LaTeX",
        "cmd": None,  # custom, handled below
        "time_est": "2min",
    },
}


def run_stage(stage_key):
    stage = STAGES[stage_key]
    name = stage["name"]
    t0 = datetime.now()
    print(f"\n{'='*70}")
    print(f"[{t0.strftime('%H:%M:%S')}] STAGE {stage_key}: {name}")
    print(f"  Tempo estimado: {stage['time_est']}")
    print(f"{'='*70}")

    if stage_key == "7":
        # Compilacao LaTeX
        paper_dir = ROOT / "Paper"
        env = os.environ.copy()
        env["TEXINPUTS"] = str(ROOT / "Preambles") + ";" + env.get("TEXINPUTS", "")
        env["BIBINPUTS"] = str(ROOT) + ";" + env.get("BIBINPUTS", "")
        for _ in range(2):
            subprocess.call(["pdflatex", "-interaction=nonstopmode", "main.tex"],
                            cwd=paper_dir, env=env)
        subprocess.call(["bibtex", "main"], cwd=paper_dir, env=env)
        for _ in range(2):
            rc = subprocess.call(["pdflatex", "-interaction=nonstopmode", "main.tex"],
                                 cwd=paper_dir, env=env)
        if rc == 0:
            print(f"\n[STAGE 7 OK] PDF em {paper_dir / 'main.pdf'}")
        else:
            print(f"\n[STAGE 7 FAIL] pdflatex retornou {rc}")
        return rc

    rc = subprocess.call(stage["cmd"])
    dt = datetime.now() - t0
    if rc == 0:
        print(f"\n[STAGE {stage_key} OK] em {dt.total_seconds()/60:.1f} min")
    else:
        print(f"\n[STAGE {stage_key} FAIL] codigo {rc} apos {dt.total_seconds()/60:.1f} min")
    return rc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stages", default="1,2,3,4,5,6,7",
                        help="Stages a rodar (CSV). Default: todos.")
    args = parser.parse_args()

    stages = args.stages.split(",")
    print(f"\nPipeline Nota_PNAD - rodando stages: {stages}")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for s in stages:
        s = s.strip()
        if s not in STAGES:
            print(f"AVISO: stage '{s}' desconhecido")
            continue
        rc = run_stage(s)
        if rc != 0:
            print(f"\nERRO no stage {s}. Abortando.")
            sys.exit(rc)

    print(f"\n{'='*70}")
    print(f"PIPELINE COMPLETO em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
