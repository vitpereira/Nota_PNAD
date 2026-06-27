# -------------------------------------------------------------------------
# AP_HJ_freq_defasagem.py
# -------------------------------------------------------------------------
# Description:
#   H. Frequencia trimestral por serie/etapa
#   J. Defasagem idade-serie (idade media por serie e ano)
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT = ROOT / "DataWork/3_Indicators/output"

print("Loading linked panel...")
df, _ = pyreadstat.read_dta(str(LINK),
    usecols=["Ano","Trimestre","idade","serie","etapa_consolid",
              "freq_escola","peso_v1028","link_ok"])
df = df[df["link_ok"] == 1].copy()

ETAPA_LBL = {4:"EF iniciais", 5:"EF finais", 10:"1o EM", 11:"2o EM", 12:"3o EM",
              20:"EJA EF", 21:"EJA EM", 30:"Pre-escola"}
df["etapa_lbl"] = df["etapa_consolid"].map(ETAPA_LBL)

# H.1 Frequencia por trimestre x etapa x ano
rows = []
for (ano, trim, etapa), sub in df.groupby(["Ano","Trimestre","etapa_lbl"]):
    if pd.isna(etapa): continue
    if sub["peso_v1028"].sum() == 0: continue
    freq = np.average(sub["freq_escola"].fillna(0),
                       weights=sub["peso_v1028"].fillna(0))
    rows.append({"ano":int(ano), "trim":int(trim), "etapa":etapa,
                  "freq_rate":freq, "n":len(sub)})
out_h = pd.DataFrame(rows).sort_values(["etapa","ano","trim"])
out_h.to_csv(OUT / "AP_H_freq_trim_etapa.csv", index=False)
print(f"AP_H: {len(out_h)} rows")

# J.1 Idade media por serie x ano (Q2 para representatividade)
sub = df[df["Trimestre"] == 2].copy()
SERIE_LBL = {1:"1o EF",2:"2o EF",3:"3o EF",4:"4o EF",5:"5o EF",
              6:"6o EF",7:"7o EF",8:"8o EF",9:"9o EF",
              10:"1o EM",11:"2o EM",12:"3o EM"}
# Combine etapa_consolid + serie para identificar serie unica
sub["serie_norm"] = np.where(
    sub["etapa_consolid"].isin([4,5]),
    sub["serie"],
    np.where(sub["etapa_consolid"] == 10, 10,
    np.where(sub["etapa_consolid"] == 11, 11,
    np.where(sub["etapa_consolid"] == 12, 12, np.nan))))
sub = sub.dropna(subset=["serie_norm"]).copy()
sub["serie_lbl"] = sub["serie_norm"].map(SERIE_LBL)

rows = []
for (ano, serie), s in sub.groupby(["Ano","serie_lbl"]):
    if pd.isna(serie): continue
    if s["peso_v1028"].sum() == 0: continue
    idade_media = np.average(s["idade"].fillna(0),
                              weights=s["peso_v1028"].fillna(0))
    rows.append({"ano":int(ano), "serie":serie,
                  "idade_media":idade_media, "n":len(s)})
out_j = pd.DataFrame(rows).sort_values(["serie","ano"])
out_j.to_csv(OUT / "AP_J_idade_media_serie.csv", index=False)
print(f"AP_J: {len(out_j)} rows")
