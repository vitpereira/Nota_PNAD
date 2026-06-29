# -------------------------------------------------------------------------
# AP_J2_defasagem_demo.py
# -------------------------------------------------------------------------
# Description:
#   Defasagem por serie x sexo x raca.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT = ROOT / "DataWork/3_Indicators/output"

print("Loading...")
df, _ = pyreadstat.read_dta(str(LINK),
    usecols=["Ano","Trimestre","idade","sexo","raca",
              "etapa_consolid","serie","peso_v1028","link_ok"])
df = df[(df["link_ok"]==1) & (df["Trimestre"]==2)].copy()

SERIE_LBL = {1:"1o EF",2:"2o EF",3:"3o EF",4:"4o EF",5:"5o EF",
              6:"6o EF",7:"7o EF",8:"8o EF",9:"9o EF",
              10:"1o EM",11:"2o EM",12:"3o EM"}

def serie_norm(row):
    e, s = row["etapa_consolid"], row["serie"]
    if e == 4:  return s if 1 <= s <= 5 else np.nan
    if e == 5:  return s if 6 <= s <= 9 else np.nan
    if e == 10: return 10
    if e == 11: return 11
    if e == 12: return 12
    return np.nan
df["serie_norm"] = df.apply(serie_norm, axis=1)
df = df.dropna(subset=["serie_norm"]).copy()
df["serie_lbl"] = df["serie_norm"].map(SERIE_LBL)
IDADE_PADRAO = {"1o EF":6,"2o EF":7,"3o EF":8,"4o EF":9,"5o EF":10,
                 "6o EF":11,"7o EF":12,"8o EF":13,"9o EF":14,
                 "1o EM":15,"2o EM":16,"3o EM":17}
df["idade_padrao"] = df["serie_lbl"].map(IDADE_PADRAO)
df["defasado"] = (df["idade"] >= df["idade_padrao"] + 2).astype(int)
df["wt"] = df["peso_v1028"].fillna(0)
df["sexo_lbl"] = df["sexo"].map({1:"Homem",2:"Mulher"})
df["raca_lbl"] = df["raca"].map({1:"Branca",2:"Preta",4:"Parda"})

# Por sexo
rows = []
for (ano, serie, sx), sub in df.groupby(["Ano","serie_lbl","sexo_lbl"]):
    if pd.isna(sx) or sub["wt"].sum() == 0: continue
    rate = np.average(sub.defasado, weights=sub.wt)
    rows.append({"ano":int(ano), "serie":serie,
                  "categoria":"sexo","valor":sx,
                  "defasado":rate, "n":len(sub)})

# Por raca
for (ano, serie, rc), sub in df.groupby(["Ano","serie_lbl","raca_lbl"]):
    if pd.isna(rc) or sub["wt"].sum() == 0: continue
    rate = np.average(sub.defasado, weights=sub.wt)
    rows.append({"ano":int(ano), "serie":serie,
                  "categoria":"raca","valor":rc,
                  "defasado":rate, "n":len(sub)})

out = pd.DataFrame(rows).sort_values(["serie","ano","categoria","valor"])
out.to_csv(OUT / "AP_J2_defasagem_demo.csv", index=False)
print(f"J2: {len(out)} rows")
