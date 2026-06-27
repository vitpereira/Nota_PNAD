# -------------------------------------------------------------------------
# AP_AB_abandono_profundo.py
# -------------------------------------------------------------------------
# Description:
#   Exploracoes profundas do abandono:
#   AB1. Abandono por idade na serie (cada serie tem distribuicao etaria)
#   AB2. Abandono por raca, sexo, dentro de cada macroetapa
#   AB3. Probabilidade de "retorno" - abandonou em t e voltou em t+1
#   AB4. Idade media dos abandonados vs idade media dos retidos
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
    usecols=["person_id","Ano","Trimestre","idade","sexo","raca",
              "etapa_consolid","serie","freq_escola","peso_v1028","link_ok"])
df = df[(df["link_ok"] == 1) & (df["person_id"].astype(str).str.strip() != "")].copy()
df = df.dropna(subset=["etapa_consolid","serie"])

# Cobertura Q1-Q4
trims = df.groupby(["person_id","Ano"])["Trimestre"].nunique()
full4 = trims[trims == 4].reset_index()[["person_id","Ano"]]
df_full = df.merge(full4, on=["person_id","Ano"], how="inner")

q1 = df_full[df_full["Trimestre"]==1].copy()
q1 = q1[q1["etapa_consolid"].isin([4,5,10,11,12])]
q1 = q1[q1["freq_escola"]==1]
q4 = df_full[df_full["Trimestre"]==4][
    ["person_id","Ano","freq_escola"]].rename(columns={"freq_escola":"freq_q4"})

ab = q1.merge(q4, on=["person_id","Ano"], how="left")
ab["abandono"] = (ab["freq_q4"]==0).astype(int)
ab["macroetapa"] = ab["etapa_consolid"].map({4:"EF iniciais",5:"EF finais",
                                                10:"EM",11:"EM",12:"EM"})
ab["sexo_lbl"] = ab["sexo"].map({1:"Homem",2:"Mulher"})
ab["raca_lbl"] = ab["raca"].map({1:"Branca",2:"Preta",4:"Parda"})
ab["wt"] = ab["peso_v1028"].fillna(0)

# AB1: abandono por idade na serie
print("AB1: por idade...")
rows = []
for (macro, idade), sub in ab.groupby(["macroetapa","idade"]):
    if sub["wt"].sum() == 0: continue
    rate = np.average(sub.abandono, weights=sub.wt)
    rows.append({"macroetapa":macro, "idade":int(idade),
                  "abandono":rate, "n":len(sub)})
pd.DataFrame(rows).to_csv(OUT / "AP_AB1_abandono_por_idade.csv", index=False)

# AB2: abandono por raca e sexo
print("AB2: por raca e sexo...")
rows = []
for (macro, ano), sub in ab.groupby(["macroetapa","Ano"]):
    for sx, sub2 in sub.groupby("sexo_lbl"):
        if pd.isna(sx) or sub2["wt"].sum() == 0: continue
        rate = np.average(sub2.abandono, weights=sub2.wt)
        rows.append({"macroetapa":macro,"ano":int(ano),
                      "categoria":"sexo","valor":sx,
                      "abandono":rate, "n":len(sub2)})
    for rc, sub2 in sub.groupby("raca_lbl"):
        if pd.isna(rc) or sub2["wt"].sum() == 0: continue
        rate = np.average(sub2.abandono, weights=sub2.wt)
        rows.append({"macroetapa":macro,"ano":int(ano),
                      "categoria":"raca","valor":rc,
                      "abandono":rate, "n":len(sub2)})
pd.DataFrame(rows).to_csv(OUT / "AP_AB2_abandono_por_demo.csv", index=False)

# AB4: idade media dos abandonados vs retidos (por macroetapa, ano)
print("AB4: idade media abandonados vs retidos...")
rows = []
for (macro, ano), sub in ab.groupby(["macroetapa","Ano"]):
    abandon = sub[sub.abandono == 1]
    retido  = sub[sub.abandono == 0]
    if abandon["wt"].sum() > 0:
        idade_ab = np.average(abandon.idade, weights=abandon.wt)
    else:
        idade_ab = np.nan
    if retido["wt"].sum() > 0:
        idade_rt = np.average(retido.idade, weights=retido.wt)
    else:
        idade_rt = np.nan
    rows.append({"macroetapa":macro,"ano":int(ano),
                  "idade_media_abandonados":idade_ab,
                  "idade_media_retidos":idade_rt,
                  "diff": idade_ab - idade_rt if not np.isnan(idade_ab) else np.nan,
                  "n_ab":len(abandon), "n_rt":len(retido)})
pd.DataFrame(rows).to_csv(OUT / "AP_AB4_idade_abandono.csv", index=False)

print("Done.")
