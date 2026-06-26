# -------------------------------------------------------------------------
# A2_parse_pnadc_trimestral.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-24
#
# Description:
#   Parseia o microdado PNADC trimestral (fixed-width text dentro do ZIP)
#   usando o input SAS .txt como layout. Extrai apenas as variaveis
#   necessarias para a construcao do painel longitudinal e para o calculo
#   dos 5 indicadores de fluxo (abandono, evasao, promocao, repetencia,
#   nao-progressao).
#
#   Salva como parquet (1 arquivo por trimestre) em tmp/pnad_parsed/.
#   Tambem salva uma versao consolidada (long format) em output/pnadc_long.dta
#   para uso direto em Stata no proximo modulo.
#
# Inputs:
#   tmp/pnad_raw/PNADC_<TTAAAA>.zip                  (52 trimestres)
#   tmp/pnad_raw/docs/input_PNADC_trimestral.txt     (layout SAS)
#
# Outputs:
#   tmp/pnad_parsed/pnadc_<TTAAAA>.parquet           (52 arquivos pequenos)
#   output/pnadc_long_2012_2024.dta                  (long format consolidado)
#   output/parse_manifest.json                       (resumo do parsing)
#   output/parse_log.csv                             (log detalhado)
#
# Variaveis extraidas (focadas no objetivo da nota):
#   IDs/painel:   Ano, Trimestre, UF, UPA, V1008, V1014, V1016, V1032
#   Pessoa:       V2001, V2003, V2005, V2007, V2009, V2010
#   Educacao:     V3001, V3002, V3002A, V3003, V3003A, V3005, V3005A,
#                 V3006, V3014, V3013, V3013A, VD3004, VD3005
#   Renda:        VD5002, VD5007, VD5008
# -------------------------------------------------------------------------

import os
import re
import sys
import json
import csv
import zipfile
from pathlib import Path
import pandas as pd

# { Paths ----
ROOT = Path(__file__).resolve().parent.parent
TMPDIR = ROOT / "tmp" / "pnad_raw"
DOCSDIR = TMPDIR / "docs"
PARSEDDIR = ROOT / "tmp" / "pnad_parsed"
OUTDIR = ROOT / "output"
PARSEDDIR.mkdir(parents=True, exist_ok=True)
OUTDIR.mkdir(parents=True, exist_ok=True)
# } ----

# { Config: variaveis desejadas ----
# NOTA: PNADC Trimestral NAO tem V1032 (peso calibrado) nem VD5xxx (renda PC
# derivada). Essas existem so em PNADC Anual / Visita 5.
# Usamos V1028 (peso da pessoa sem calibracao a totais conhecidos).
# Renda dom PC sera calculada em Stata a partir de V403312.
WANTED_VARS = [
    # IDs e painel
    "Ano", "Trimestre", "UF", "UPA", "Estrato",
    "V1008", "V1014", "V1016", "V1022", "V1023", "V1027", "V1028",
    # Pessoa
    "V2001", "V2003", "V2005", "V2007", "V2008", "V2009", "V2010",
    # Educacao (versoes diferentes em anos diferentes - extrair todas as que existirem)
    "V3001", "V3001A",        # le e escreve
    "V3002", "V3002A",        # frequenta + rede
    "V3003", "V3003A",        # curso/etapa (V3003 ate 2015; V3003A a partir de 2016)
    "V3005", "V3005A",        # curso anterior
    "V3006", "V3014",         # serie (V3006 ate 2018; V3014 a partir de 2019)
    "V3013", "V3013A",        # ultima serie concluida
    "VD3004", "VD3005",       # nivel/anos de estudo (derivadas)
    # Renda (do trabalho - sera somada em Stata por dom para gerar renda dom PC)
    "V403312",                # rendimento habitual trab principal
    "VD4019",                 # rendimento habitual de todos os trabalhos
    # Condicao no trabalho (util para filtros)
    "VD4001", "VD4002",
]
# } ----


def parse_input_layout(input_txt_path):
    """Le input SAS-style. Retorna {varname: (pos_1indexed, width)}."""
    with open(input_txt_path, "r", encoding="latin-1", errors="replace") as f:
        txt = f.read()
    pat = re.compile(r"@(\d+)\s+(\w+)\s+\$?(\d+)\.", re.M)
    layout = {}
    for pos, name, width in pat.findall(txt):
        layout[name] = (int(pos), int(width))
    return layout


def build_colspecs(layout, wanted):
    """Para variaveis em wanted que existem no layout, retorna colspecs."""
    cols = []
    names = []
    missing = []
    for v in wanted:
        if v not in layout:
            missing.append(v)
            continue
        pos, width = layout[v]
        start = pos - 1
        end = start + width
        cols.append((start, end))
        names.append(v)
    return names, cols, missing


def find_microdata_in_zip(zf):
    """Retorna o nome do .txt de microdados (maior arquivo) dentro do zip."""
    candidates = [n for n in zf.namelist() if n.lower().endswith(".txt")]
    if not candidates:
        raise RuntimeError(f"Nenhum .txt no zip. Files: {zf.namelist()}")
    sized = [(zf.getinfo(n).file_size, n) for n in candidates]
    sized.sort(reverse=True)
    return sized[0][1]


def parse_quarter(year, quarter, layout):
    """Parseia um trimestre. Retorna info dict ou None se falhou."""
    zip_name = f"PNADC_{quarter:02d}{year}.zip"
    zip_path = TMPDIR / zip_name
    if not zip_path.exists():
        return {"year": year, "quarter": quarter, "status": "zip_missing", "rows": 0}

    out_path = PARSEDDIR / f"pnadc_{quarter:02d}{year}.parquet"
    if out_path.exists() and out_path.stat().st_size > 0:
        try:
            df = pd.read_parquet(out_path)
            return {"year": year, "quarter": quarter, "status": "skip_existing",
                    "rows": int(len(df)), "cols": int(df.shape[1])}
        except Exception:
            out_path.unlink()  # corrupt, reparse

    names, colspecs, missing = build_colspecs(layout, WANTED_VARS)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            micro = find_microdata_in_zip(zf)
            with zf.open(micro) as fh:
                df = pd.read_fwf(
                    fh, colspecs=colspecs, names=names,
                    dtype=str, encoding="latin-1",
                )
    except Exception as e:
        return {"year": year, "quarter": quarter, "status": f"parse_fail: {e}", "rows": 0}

    # { Type coercion ----
    int_vars = ["Ano", "Trimestre", "UF", "V1008", "V1014", "V1016",
                "V2001", "V2003", "V2005", "V2009", "VD3004"]
    float_vars = ["V1028", "V1027", "V403312", "VD4019"]
    for v in int_vars:
        if v in df.columns:
            df[v] = pd.to_numeric(df[v], errors="coerce").astype("Int64")
    for v in float_vars:
        if v in df.columns:
            df[v] = pd.to_numeric(df[v], errors="coerce")
    for v in df.columns:
        if df[v].dtype == object:
            df[v] = df[v].str.strip()
            df.loc[df[v] == "", v] = pd.NA
    # } ----

    df.to_parquet(out_path, index=False)

    return {
        "year": year, "quarter": quarter, "status": "parsed",
        "rows": int(len(df)), "cols": int(df.shape[1]),
        "missing": missing, "vars": names,
    }


def consolidate_long():
    """Junta todos os parquet trimestrais em um .dta long para Stata."""
    files = sorted(PARSEDDIR.glob("pnadc_??20*.parquet"))
    if not files:
        print("Nenhum parquet para consolidar.")
        return None

    print(f"\nConsolidando {len(files)} arquivos em formato long...")
    dfs = []
    for f in files:
        df = pd.read_parquet(f)
        dfs.append(df)
    big = pd.concat(dfs, ignore_index=True)
    print(f"  Total: {len(big):,} obs x {big.shape[1]} cols")

    # Salvar em .dta para Stata (precisa de pyreadstat)
    try:
        import pyreadstat
        out_dta = OUTDIR / "pnadc_long_2012_2024.dta"
        # Converter Int64 nullable para float (pyreadstat nao suporta nullable int)
        for c in big.columns:
            if str(big[c].dtype) == "Int64":
                big[c] = big[c].astype(float)
        pyreadstat.write_dta(big, str(out_dta))
        print(f"  Salvo: {out_dta} ({out_dta.stat().st_size/1e6:.1f} MB)")
    except ImportError:
        print("  pyreadstat nao disponivel; salvando em parquet")
        out_par = OUTDIR / "pnadc_long_2012_2024.parquet"
        big.to_parquet(out_par, index=False)
        print(f"  Salvo: {out_par} ({out_par.stat().st_size/1e6:.1f} MB)")

    return big


def main():
    # { 1. Layout ----
    layout_path = DOCSDIR / "input_PNADC_trimestral.txt"
    if not layout_path.exists():
        print(f"ERRO: layout nao encontrado em {layout_path}")
        print("Rode A1_download_pnadc_trimestral.py primeiro.")
        return 1

    layout = parse_input_layout(layout_path)
    print(f"Layout carregado: {len(layout)} variaveis")

    # Verificar quais das desejadas estao no layout
    found = [v for v in WANTED_VARS if v in layout]
    missing = [v for v in WANTED_VARS if v not in layout]
    print(f"  Desejadas encontradas no layout: {len(found)}/{len(WANTED_VARS)}")
    if missing:
        print(f"  AVISO - nao encontradas no layout (podem nao existir em todos os anos):")
        for v in missing:
            print(f"    - {v}")
    # } ----

    # { 2. Loop sobre trimestres ----
    YEARS = list(range(2012, 2026))
    summary = []
    for year in YEARS:
        for q in [1, 2, 3, 4]:
            info = parse_quarter(year, q, layout)
            status = info["status"]
            rows = info.get("rows", 0)
            print(f"  {year}Q{q}: {status:>20s} | {rows:>9,} rows")
            summary.append(info)
    # } ----

    # { 3. Log e manifest ----
    log_path = OUTDIR / "parse_log.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["year", "quarter", "status", "rows", "cols"])
        writer.writeheader()
        for s in summary:
            writer.writerow({k: s.get(k, "") for k in ["year", "quarter", "status", "rows", "cols"]})
    print(f"\nLog: {log_path}")

    manifest_path = OUTDIR / "parse_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    # } ----

    # { 4. Consolidacao long format ----
    consolidate_long()
    # } ----

    return 0


if __name__ == "__main__":
    sys.exit(main())
