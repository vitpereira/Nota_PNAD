# -------------------------------------------------------------------------
# AP_C_abandono.py
# -------------------------------------------------------------------------
# Description:
#   Abandono intra-ano por SERIE individual (nao soh macroetapa).
#   Universo: alunos observados em Q1 do ano em regular EF/EM, observados
#   na ultima visita do mesmo ano, com correcao V3014.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT = ROOT / "DataWork/3_Indicators/output"

print("Loading linked...")
df, _ = pyreadstat.read_dta(str(LINK),
    usecols=["person_id","Ano","Trimestre","idade","etapa_consolid","serie",
              "freq_escola","peso_v1028","link_ok"])
df = df[(df["link_ok"] == 1) & (df["person_id"].astype(str).str.strip() != "")].copy()
df = df.dropna(subset=["etapa_consolid","serie"])

# Identifica HHs com cobertura Q1-Q4
trims = df.groupby(["person_id","Ano"])["Trimestre"].nunique()
full4 = trims[trims == 4].reset_index()[["person_id","Ano"]]
df_full = df.merge(full4, on=["person_id","Ano"], how="inner")

# Q1 (primeira) e Q4 (ultima)
q1 = df_full[df_full["Trimestre"]==1].copy()
q1 = q1[q1["etapa_consolid"].isin([4,5,10,11,12])]
q1 = q1[q1["freq_escola"]==1]

q4 = df_full[df_full["Trimestre"]==4][
    ["person_id","Ano","freq_escola","etapa_consolid","serie"]].copy()
q4 = q4.rename(columns={"freq_escola":"freq_q4"})

# Serie normalizada
def serie_norm(row):
    e, s = row["etapa_consolid"], row["serie"]
    if e == 4:  return s if 1 <= s <= 5 else np.nan
    if e == 5:  return s if 6 <= s <= 9 else np.nan
    if e == 10: return 10
    if e == 11: return 11
    if e == 12: return 12
    return np.nan
q1["serie_norm"] = q1.apply(serie_norm, axis=1)
q1 = q1.dropna(subset=["serie_norm"])

ab = q1.merge(q4[["person_id","Ano","freq_q4"]], on=["person_id","Ano"], how="left")
ab["flag_abandono_raw"] = (ab["freq_q4"]==0).astype(int)

SERIE_LBL = {1:"1o EF",2:"2o EF",3:"3o EF",4:"4o EF",5:"5o EF",
              6:"6o EF",7:"7o EF",8:"8o EF",9:"9o EF",
              10:"1o EM",11:"2o EM",12:"3o EM"}
ab["serie_lbl"] = ab["serie_norm"].map(SERIE_LBL)
ab["wt"] = ab["peso_v1028"].fillna(0)

rows = []
for (ano, serie), sub in ab.groupby(["Ano","serie_lbl"]):
    if sub["wt"].sum() == 0: continue
    rate = np.average(sub.flag_abandono_raw, weights=sub.wt)
    rows.append({"ano":int(ano), "serie":serie,
                  "flag_abandono":rate, "n":len(sub)})

out = pd.DataFrame(rows).sort_values(["serie","ano"])
out.to_csv(OUT / "AP_C_abandono_por_serie.csv", index=False)
print(f"AP_C: {len(out)} rows")
