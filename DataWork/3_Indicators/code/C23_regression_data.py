# -------------------------------------------------------------------------
# C23_regression_data.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-25
#
# Description:
#   Constroi dataset de regressao a partir das transicoes v5 (norot1).
#   Adiciona controles disponiveis:
#     - macroetapa, nivel
#     - idade, sexo, raca, defasagem idade-serie
#     - renda log, rede (publica/privada)
#     - capital/RM/RIDE/interior (V1023)
#
#   Variaveis nao disponiveis no parser atual mas que poderiam ser
#   adicionadas: gravidez (V2013, suplemento V5 anual), filhos tidos
#   (V2015, idem), perda de emprego de provedor.
#
# Outputs:
#   ../output/C23_regression_data.parquet
#   ../output/C23_regression_data.dta (para Stata)
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

# Load v5 transitions (norot1)
print("Loading C22 transitions...", flush=True)
t = pd.read_parquet(OUT_DIR / "C22_transitions_v5_norot1.parquet")
print(f"  {len(t):,} rows", flush=True)

# Need V1023 (capital/interior). Get from raw parquets via merge.
print("Extracting V1023 from raw lookup...", flush=True)
lookup = pd.read_parquet(OUT_DIR / "C19_v4_lookup.parquet",
                          columns=["UF", "UPA", "V1008", "V1014", "V2003",
                                   "Ano", "Trimestre"])
# Note: V1023 not in lookup. Re-extract from one parquet to get the values for our keys.

# Simpler: read V1023 from parquets and merge
import glob
PARSED_DIR = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
parquets = sorted(PARSED_DIR.glob("pnadc_*.parquet"))

v1023_frames = []
for p in parquets:
    try:
        d = pd.read_parquet(p, columns=["UF", "UPA", "V1008", "V1014", "V2003",
                                          "V1023", "Ano", "Trimestre"])
    except Exception:
        continue
    v1023_frames.append(d)
v1023 = pd.concat(v1023_frames, ignore_index=True)
v1023["V1023"] = pd.to_numeric(v1023["V1023"], errors="coerce")
print(f"  V1023 rows: {len(v1023):,}", flush=True)

# Take one V1023 per household (it should be constant within hh)
v1023["UF"] = v1023["UF"].astype(int)
v1023["UPA"] = v1023["UPA"].astype(str)
v1023["V1008"] = v1023["V1008"].astype(int)
v1023["V1014"] = v1023["V1014"].astype(int)
hh_v1023 = v1023.groupby(["UF", "UPA", "V1008", "V1014"])["V1023"].first().reset_index()
print(f"  Unique households: {len(hh_v1023):,}", flush=True)

# Get the hh_id components from link panel
print("Loading link to map person_id to household keys...", flush=True)
link, _ = pyreadstat.read_dta(
    str(LINK),
    usecols=["UF", "UPA", "V1008", "V1014", "V2003", "person_id", "link_ok", "Ano"]
)
link = link[link["link_ok"] == 1]
link["UF"] = link["UF"].astype(int)
link["UPA"] = link["UPA"].astype(int).astype(str)
link["V1008"] = link["V1008"].astype(int)
link["V1014"] = link["V1014"].astype(int)
person_to_hh = link.drop_duplicates(subset=["person_id", "Ano"])[
    ["person_id", "Ano", "UF", "UPA", "V1008", "V1014"]
].rename(columns={"Ano": "ano_t"})

# Merge person -> hh -> V1023
person_v1023 = person_to_hh.merge(hh_v1023, on=["UF", "UPA", "V1008", "V1014"], how="left")
print(f"  person_v1023 rows: {len(person_v1023):,}", flush=True)

# Merge to transitions
t = t.merge(person_v1023[["person_id", "ano_t", "V1023", "UF"]],
              on=["person_id", "ano_t"], how="left")
t = t.rename(columns={"V1023": "v1023_t", "UF": "uf_t"})

# Idade-padrao + defasagem
def idade_padrao(n):
    if pd.isna(n): return np.nan
    n = float(n)
    if 1 <= n <= 9: return 5 + n
    if n == 10: return 15
    if n == 11: return 16
    if n == 12: return 17
    if n == 13: return 18
    return np.nan
t["idade_padrao"] = t["nivel_t"].map(idade_padrao)
t["defasagem"] = t["idade_t"] - t["idade_padrao"]
t["defasagem_2plus"] = (t["defasagem"] >= 2).astype(int)
t["defasagem_1"] = ((t["defasagem"] >= 1) & (t["defasagem"] < 2)).astype(int)

# Rede dummy: rede 1,2,3 = publica (federal, estadual, municipal); rede 5 = privada
t["rede_publica"] = (t["rede_t"].isin([1, 2, 3])).astype(int)
t["rede_privada"] = (t["rede_t"] == 5).astype(int)

# Sexo
t["feminino"] = (t["sexo_t"] == 2).astype(int)

# Raca dummies (1=branca, 2=preta, 3=amarela, 4=parda, 5=indigena)
t["branca"] = (t["raca_t"] == 1).astype(int)
t["preta"] = (t["raca_t"] == 2).astype(int)
t["parda"] = (t["raca_t"] == 4).astype(int)
t["amarela"] = (t["raca_t"] == 3).astype(int)
t["indigena"] = (t["raca_t"] == 5).astype(int)

# Renda log
t["log_renda"] = np.log(t["renda_t"].clip(lower=1))

# Capital/RM/RIDE/Interior
t["capital"] = (t["v1023_t"] == 1).astype(int)
t["resto_rm"] = (t["v1023_t"] == 2).astype(int)
t["ride"] = (t["v1023_t"] == 3).astype(int)
t["interior"] = (t["v1023_t"] == 4).astype(int)

# Macroetapa dummies
t["me_efi"] = (t["macroetapa_t"] == "EF iniciais").astype(int)
t["me_eff"] = (t["macroetapa_t"] == "EF finais").astype(int)
t["me_em"]  = (t["macroetapa_t"] == "EM").astype(int)

# Save
keep = ["person_id", "ano_t", "ano_t1", "uf_t",
         "flag_evasao", "flag_repetencia", "flag_promocao", "flag_migracao_eja",
         "idade_t", "feminino", "branca", "preta", "parda", "amarela", "indigena",
         "defasagem", "defasagem_1", "defasagem_2plus",
         "nivel_t", "me_efi", "me_eff", "me_em",
         "rede_publica", "rede_privada",
         "log_renda", "renda_t",
         "capital", "resto_rm", "ride", "interior",
         "wt", "v1023_t"]

t_out = t[keep].copy()
print(f"\nFinal regression dataset: {len(t_out):,}", flush=True)
print(t_out.describe().to_string(), flush=True)

t_out.to_parquet(OUT_DIR / "C23_regression_data.parquet", index=False)
# Also save as .dta for Stata
import pyreadstat
pyreadstat.write_dta(t_out, str(OUT_DIR / "C23_regression_data.dta"))
print(f"\nSaved C23_regression_data.parquet and .dta", flush=True)
