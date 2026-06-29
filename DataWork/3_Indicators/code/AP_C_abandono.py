# -------------------------------------------------------------------------
# AP_C_abandono.py (v3 - estrutura da Rodada 25 C30)
# -------------------------------------------------------------------------
# Description:
#   Abandono intra-ano por SERIE com correcao V3014.
#   Estrutura segue C30_abandono_v5_corrected.py (Rodada 25 validada).
#   IMPORTANTE: NAO dropar etapa_consolid/serie cedo — pessoas que
#   abandonam ficam com freq=0 em Q4 mas SEM etapa_consolid.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT = ROOT / "DataWork/3_Indicators/output"

# { 1. Lookup com V3014 + nivel
print("Loading lookup...")
lookup = pd.read_parquet(OUT / "C19_v4_lookup.parquet",
    columns=["UF","UPA","V1008","V1014","V2003","Ano","Trimestre",
              "V3002","V3014","V3003","V3003A","V3006","V2009"])
for c in ["V3002","V3014","V3003","V3003A","V3006","V2009"]:
    lookup[c] = pd.to_numeric(lookup[c], errors="coerce")
lookup = lookup[lookup["V2009"].between(4,24)].copy()
ano = lookup["Ano"].values; v3 = lookup["V3003"].values; v3a = lookup["V3003A"].values
curso = np.full(len(lookup), 900.0)
mp = ano <= 2015
curso[mp & (v3==3)] = 100;  curso[mp & (v3==4)] = 300
curso[mp & (v3==5)] = 200;  curso[mp & (v3==6)] = 310; curso[mp & (v3==7)] = 210
mo = ano >= 2016
curso[mo & (v3a==4)] = 100; curso[mo & (v3a==5)] = 300
curso[mo & (v3a==6)] = 200; curso[mo & (v3a==7)] = 210
lookup["curso"] = curso
serie_v = lookup["V3006"].values
nivel = np.full(len(lookup), np.nan)
nivel[(curso==100) & (serie_v>=1) & (serie_v<=9)] = serie_v[(curso==100) & (serie_v>=1) & (serie_v<=9)]
nivel[(curso==200) & (serie_v>=1) & (serie_v<=3)] = 9 + serie_v[(curso==200) & (serie_v>=1) & (serie_v<=3)]
nivel[(curso==210) & (serie_v>=1) & (serie_v<=4)] = 9 + serie_v[(curso==210) & (serie_v>=1) & (serie_v<=4)]
lookup["nivel"] = nivel
lookup["concluiu"] = (lookup["V3014"]==1).astype(int)
# } ----

# { 2. Painel linkado SEM dropar etapa_consolid
print("Loading panel...")
df, _ = pyreadstat.read_dta(str(LINK),
    usecols=["person_id","Ano","Trimestre","UF","UPA","V1008","V1014","V2003",
              "idade","etapa_consolid","serie","freq_escola","peso_v1028","link_ok"])
df = df[(df["link_ok"]==1) & (df["person_id"].astype(str).str.strip()!='')].copy()
for c in ["freq_escola","etapa_consolid","serie","idade","peso_v1028",
           "Trimestre","Ano","UF","UPA","V1008","V1014","V2003"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
# CRITICAL: NAO dropna(etapa_consolid, serie) aqui — preciso manter
# pessoas com freq=0 em Q4 (sem etapa)
# } ----

# { 3. Merge V3014/nivel onto panel
keys = ["Ano","Trimestre","UF","UPA","V1008","V1014","V2003"]
for c in keys:
    df[c] = df[c].astype("Int64")
    lookup[c] = lookup[c].astype("Int64")
panel = df.merge(lookup[keys + ["nivel","concluiu","curso"]],
                  on=keys, how="left")
print(f"merged: {len(panel):,}")
# } ----

# { 4. Cobertura Q1-Q4
trims = panel.groupby(["person_id","Ano"])["Trimestre"].nunique()
full4 = trims[trims==4].reset_index()[["person_id","Ano"]]
df_full = panel.merge(full4, on=["person_id","Ano"], how="inner")
print(f"full4 obs: {len(df_full):,}")
# } ----

# { 5. Q1 universe (regular + freq=1) e Q4 outcome
df_q1 = df_full[df_full["Trimestre"]==1].copy()
df_q1 = df_q1[df_q1["etapa_consolid"].isin([4,5,10,11,12])]
df_q1 = df_q1[df_q1["freq_escola"]==1]
print(f"Q1 universe: {len(df_q1):,}")

df_q4 = df_full[df_full["Trimestre"]==4][
    ["person_id","Ano","freq_escola","etapa_consolid","serie"]].copy()
df_q4 = df_q4.rename(columns={"freq_escola":"freq_q4",
                                "etapa_consolid":"etapa_q4",
                                "serie":"serie_q4"})

# Aggregar nivel max e concluiu_any ao longo do ano
year_agg = (df_full.groupby(["person_id","Ano"], as_index=False)
              .agg(concluiu_any=("concluiu","max"),
                   nivel_max=("nivel","max")))

ab = (df_q1.merge(df_q4, on=["person_id","Ano"], how="left")
            .merge(year_agg, on=["person_id","Ano"], how="left"))
# } ----

# { 6. Series normalizada e abandono
def serie_norm(row):
    e, s = row["etapa_consolid"], row["serie"]
    if e==4:  return s if 1<=s<=5 else np.nan
    if e==5:  return s if 6<=s<=9 else np.nan
    if e==10: return 10
    if e==11: return 11
    if e==12: return 12
    return np.nan
ab["serie_norm"] = ab.apply(serie_norm, axis=1)
ab = ab.dropna(subset=["serie_norm"]).copy()

ab["abandono_raw"] = (ab["freq_q4"]==0).astype(int)
is_concluinte = ab["nivel_max"].isin([12.0,13.0]) & (ab["concluiu_any"]==1)
ab["concluinte"] = is_concluinte.astype(int)
ab["abandono"] = ab["abandono_raw"].copy()
ab.loc[is_concluinte, "abandono"] = 0

SERIE_LBL = {1:"1o EF",2:"2o EF",3:"3o EF",4:"4o EF",5:"5o EF",
              6:"6o EF",7:"7o EF",8:"8o EF",9:"9o EF",
              10:"1o EM",11:"2o EM",12:"3o EM"}
ab["serie_lbl"] = ab["serie_norm"].map(SERIE_LBL)
ab["wt"] = ab["peso_v1028"].fillna(0)
ab.to_parquet(OUT / "AP_C_micro_abandono.parquet", index=False)

# Sanity: abandono geral
total = np.average(ab["abandono"], weights=ab["wt"])
print(f"\nAbandono medio geral (com correcao V3014): {total*100:.2f}%")

rows = []
for (ano, serie), sub in ab.groupby(["Ano","serie_lbl"]):
    if sub["wt"].sum() == 0: continue
    rate_raw  = np.average(sub.abandono_raw, weights=sub.wt)
    rate_corr = np.average(sub.abandono, weights=sub.wt)
    pct_conc  = np.average(sub.concluinte, weights=sub.wt)
    rows.append({"ano":int(ano), "serie":serie,
                  "flag_abandono_raw":rate_raw,
                  "flag_abandono":rate_corr,
                  "pct_concluinte":pct_conc,
                  "n":len(sub)})
out = pd.DataFrame(rows).sort_values(["serie","ano"])
out.to_csv(OUT / "AP_C_abandono_por_serie.csv", index=False)
print(f"\n2019 EM (3o):")
sub19 = out[(out["ano"]==2019) & (out["serie"]=="3o EM")]
print(sub19.to_string(index=False))
print(f"\nAP_C: {len(out)} rows")
# } ----
