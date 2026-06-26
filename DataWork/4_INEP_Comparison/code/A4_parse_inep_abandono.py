# -------------------------------------------------------------------------
# A4_parse_inep_abandono.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Le os arquivos da Taxa de Rendimento Escolar do INEP por ano
#   (2012-2024) e extrai a taxa de ABANDONO para Brasil Total Total,
#   por macroetapa: EF_AI, EF_AF, EM.
#
#   Tres formatos de arquivo:
#     Strategy A (2020-2024): variable codes 1_/2_/3_CAT_FUN_AI etc.
#     Strategy B (2015-2019): variable codes tap_/tre_/tab_ prefix
#     Strategy C (2012-2014): no var codes, use positional offsets
#
# Inputs:  tmp/inep_raw/extracted/rendimento/*.xlsx
# Outputs: output/inep_abandono_long.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC  = ROOT / "DataWork/4_INEP_Comparison/tmp/inep_raw/extracted/rendimento"
OUT  = ROOT / "DataWork/4_INEP_Comparison/output"

YEAR_FILES = {
    2012: "tx_rendimento_brasil_2012.xlsx",
    2013: "TAXAS RENDIMENTOS BRASIL 2013.xlsx",
    2014: "TAXAS RENDIMENTOS BRASIL 2014.xlsx",
    2015: "TAXA_REND_2015_BRASIL_REGIOES_UFS/TX_REND_BRASIL_2015.xlsx",
    2016: "TAXA_REND_2016_BRASIL_REGIOES_UFS/TX_REND_BRASIL_2016.xlsx",
    2017: "TAXA_REND_2017_BRASIL_REGIOES_UFS/TX_REND_BRASIL_REGIOES_UFS_2017.xlsx",
    2018: "TX_REND_BRASIL_REGIOES_UFS_2018/TX_REND_BRASIL_REGIOES_UFS_2018.xlsx",
    2019: "tx_rend_brasil_regioes_ufs_2019/tx_rend_brasil_regioes_ufs_2019.xlsx",
    2020: "tx_rend_brasil_regioes_ufs_2020/tx_rend_brasil_regioes_ufs_2020.xlsx",
    2021: "tx_rend_brasil_regioes_ufs_2021/tx_rend_brasil_regioes_ufs_2021.xlsx",
    2022: "tx_rend_brasil_regioes_ufs_2022/tx_rend_brasil_regioes_ufs_2022.xlsx",
    2023: "tx_rend_brasil_regioes_ufs_2023/tx_rend_brasil_regioes_ufs_2023.xlsx",
    2024: "tx_rend_brasil_regioes_ufs_2024/tx_rend_brasil_regioes_ufs_2024.xlsx",
}

def to_float(x):
    if pd.isna(x): return None
    s = str(x).strip()
    if s in ('--', '-', '', 'nan', 'NaN'): return None
    s = s.replace(',', '.').replace('%','').strip()
    try: return float(s)
    except: return None

def get_var_row(d, patterns, max_rows=15):
    """Find row index where any of the patterns appear among the cells."""
    for i in range(min(max_rows, len(d))):
        cells = [str(x) for x in d.iloc[i].values if pd.notna(x)]
        for p in patterns:
            if any(p in c for c in cells):
                return i
    return None

def find_data_row(d, start, brasil_col, cat_col, dep_col):
    """Find first data row with UNIDGEO='Brasil', NO_CATEGORIA='Total', NO_DEPENDENCIA='Total'."""
    for i in range(start, len(d)):
        row = d.iloc[i]
        def cell(c): return str(row.iloc[c]).strip() if c<len(row) and pd.notna(row.iloc[c]) else ''
        ug = cell(brasil_col).lower()
        ca = cell(cat_col)
        dp = cell(dep_col)
        if ug == 'brasil' and ca == 'Total' and dp == 'Total':
            return row
    return None

def parse_modern(f):
    """Strategy A: 2020-2024 format with codes like 3_CAT_FUN_AI."""
    d = pd.read_excel(f, sheet_name=0, header=None)
    hdr = get_var_row(d, ['3_CAT_FUN_AI'])
    if hdr is None: return None
    cols = {str(v).strip(): j for j,v in enumerate(d.iloc[hdr].values) if pd.notna(v)}
    need = {'3_CAT_FUN_AI':'EF_AI', '3_CAT_FUN_AF':'EF_AF', '3_CAT_MED':'EM'}
    if not all(k in cols for k in need): return None
    ug_col = cols.get('UNIDGEO', 1)
    ca_col = cols.get('NO_CATEGORIA', 2)
    dp_col = cols.get('NO_DEPENDENCIA', 3)
    row = find_data_row(d, hdr+1, ug_col, ca_col, dp_col)
    if row is None: return None
    return {etapa: to_float(row.iloc[cols[code]]) for code, etapa in need.items()}

def parse_tab_prefix(f):
    """Strategy B: 2015-2019 format with tap_/tre_/tab_ prefix.
    Mapping fluctua entre anos por causa da transicao 8->9 anos EF:
      - 2014-2017: tab_F14=AI(1a-4a), tab_F58=AF(5a-8a)
      - 2018-2019: tab_F14=AI(1o-5o), tab_F04=AF(6o-9o), tab_F58=1o Ano
    Heuristica robusta: o codigo IMEDIATAMENTE APOS tab_F14 (em ordem de
    coluna) eh sempre o agregado AF, seja tab_F58 ou tab_F04."""
    d = pd.read_excel(f, sheet_name=0, header=None)
    hdr = get_var_row(d, ['tab_F14', 'tab_FUN'])
    if hdr is None: return None
    cols = {str(v).strip().lower(): j for j,v in enumerate(d.iloc[hdr].values) if pd.notna(v)}
    if 'tab_f14' not in cols or 'tab_med' not in cols:
        return None
    # AI is tab_F14
    ai_col = cols['tab_f14']
    em_col = cols['tab_med']
    # AF is the FIRST tab_ column after tab_F14 (likely tab_F04 or tab_F58)
    tab_cols_sorted = sorted([(j, c) for c, j in cols.items() if c.startswith('tab_')])
    af_col = None
    for j, c in tab_cols_sorted:
        if j > ai_col and c != 'tab_med':
            af_col = j
            af_code = c
            break
    if af_col is None: return None
    need = {ai_col: 'EF_AI', af_col: 'EF_AF', em_col: 'EM'}
    # Find label columns
    abrang_col = None; loc_col = None; rede_col = None
    for c, j in cols.items():
        if 'tipoloca' in c or c in ('no_cod', 'unidgeo', 'abrang�ncia', 'abrangencia'):
            if abrang_col is None: abrang_col = j
        if 'dependad' in c or 'depend' in c:
            rede_col = j
        if 'localiza' in c or c == 'tipoloca':
            loc_col = j
    # Standard ordering: 4 cols: ano, geo, loc, dep
    # Try col indices 1, 2, 3 with various role mappings
    # Read R5 header to determine structure
    row5 = [str(x).strip() if pd.notna(x) else '' for x in d.iloc[5].values]
    # Determine col positions of identifying cols (assume row 5 has them)
    name_to_idx = {}
    for j, n in enumerate(row5):
        name_to_idx[n.lower()] = j
    # Conventional positions
    # 2015: Ano(0), Abrangencia(1), Localizacao(2), Rede(3)
    # 2016+: Ano(0), Unidade Geog/no_cod(1), Localizacao(2), Dependencia(3)
    ug_col = 1
    ca_col = 2  # localizacao
    dp_col = 3  # rede / dependencia
    # In some years the order is Localizacao before Dependencia, in others reversed
    # We need: UG=Brasil, Cat=Total (localizacao), Dep=Total (rede)
    row = find_data_row(d, hdr+1, ug_col, ca_col, dp_col)
    if row is None:
        # Try swapped Cat/Dep
        row = find_data_row(d, hdr+1, ug_col, dp_col, ca_col)
    if row is None: return None
    return {etapa: to_float(row.iloc[col_idx]) for col_idx, etapa in need.items()}

def parse_positional(f, year):
    """Strategy C: 2012-2014 format. Total 58 cols.
    cols 0-3: ano, Abrangencia, Rede, Localizacao.
    Each indicator (Aprov, Reprov, Abandono) has 18 cols:
      EF: Total + AI + AF + 9 series = 12 cols
      EM: Total + 1o + 2o + 3o + 4o + NS = 6 cols
    Offsets:
      Aprov_EF (4-15), Aprov_EM (16-21),
      Reprov_EF (22-33), Reprov_EM (34-39),
      Aband_EF (40-51): 40=Total, 41=AI, 42=AF, 43-51 = series 1-9
      Aband_EM (52-57): 52=Total, 53=1o, 54=2o, 55=3o, 56=4o, 57=NS
    """
    d = pd.read_excel(f, sheet_name=0, header=None)
    row = None
    for i in range(5, min(20, len(d))):
        rvals = d.iloc[i].values
        if pd.notna(rvals[0]) and str(rvals[0]).strip() == str(year):
            joined = ' '.join(str(x).lower() for x in rvals[:5] if pd.notna(x))
            if 'brasil' in joined and 'total' in joined:
                row = rvals
                break
    if row is None: return None
    try:
        return {
            'EF_AI': to_float(row[41]),
            'EF_AF': to_float(row[42]),
            'EM':    to_float(row[52]),
        }
    except IndexError:
        return None

# Run
rows = []
for year, rel in YEAR_FILES.items():
    f = SRC / rel
    if not f.exists():
        print(f"MISSING: {f}")
        continue
    out = None
    for fn, label in [(parse_modern, 'modern'),
                      (parse_tab_prefix, 'tab-prefix'),
                      (lambda fp: parse_positional(fp, year), 'positional')]:
        try:
            out = fn(f)
            if out and all(v is not None for v in out.values()):
                print(f"{year}: [{label}] EF_AI={out.get('EF_AI')}, EF_AF={out.get('EF_AF')}, EM={out.get('EM')}")
                break
        except Exception as e:
            pass
    if not out:
        print(f"{year}: PARSE FAILED ALL STRATEGIES")
        continue
    for etapa, valor in out.items():
        if valor is not None:
            rows.append({'ano_t': year, 'etapa': etapa, 'valor': valor,
                         'unidade': 'Brasil', 'indicador': 'abandono'})

dfo = pd.DataFrame(rows)
dest = OUT / 'inep_abandono_long.csv'
dfo.to_csv(dest, index=False)
print(f"\nWrote {dest} ({len(dfo)} rows)")
