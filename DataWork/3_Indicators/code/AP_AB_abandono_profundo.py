# -------------------------------------------------------------------------
# AP_AB_abandono_profundo.py (v2 - usa AP_C micro com V3014)
# -------------------------------------------------------------------------
# Description:
#   Exploracoes profundas do abandono usando AP_C_micro_abandono.parquet
#   (que ja tem correcao V3014). Adiciona demografia (sexo, raca) ao micro.
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT = ROOT / "DataWork/3_Indicators/output"

# Carregar AP_C micro
ab = pd.read_parquet(OUT / "AP_C_micro_abandono.parquet")
print(f"AP_C micro: {len(ab):,}")

# Adicionar sexo e raca do painel
print("Loading demo do panel...")
demo, _ = pyreadstat.read_dta(str(LINK),
    usecols=["person_id","Ano","Trimestre","sexo","raca"])
demo = demo[demo["Trimestre"]==1].drop(columns="Trimestre")
demo["sexo"] = pd.to_numeric(demo["sexo"], errors="coerce")
demo["raca"] = pd.to_numeric(demo["raca"], errors="coerce")
demo["sexo_lbl"] = demo["sexo"].map({1:"Homem",2:"Mulher"})
demo["raca_lbl"] = demo["raca"].map({1:"Branca",2:"Preta",4:"Parda"})

ab = ab.merge(demo[["person_id","Ano","sexo_lbl","raca_lbl"]],
                on=["person_id","Ano"], how="left")
print(f"after merge demo: {len(ab):,}")

# Macroetapa
ab["macroetapa"] = ab["etapa_consolid"].map({4:"EF iniciais",5:"EF finais",
                                                  10:"EM",11:"EM",12:"EM"})

# AB1: abandono (corrigido) por idade x macroetapa, pooled
print("\nAB1: por idade...")
rows = []
for (macro, idade), sub in ab.groupby(["macroetapa","idade"]):
    if sub["wt"].sum() == 0: continue
    rate = np.average(sub.abandono, weights=sub.wt)
    rows.append({"macroetapa":macro, "idade":int(idade),
                  "abandono":rate, "n":len(sub)})
pd.DataFrame(rows).to_csv(OUT / "AP_AB1_abandono_por_idade.csv", index=False)

# AB2: por sexo e raca, ano
print("AB2: por sexo e raca, ano...")
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

# AB4: idade media abandonados vs retidos
print("AB4: idade media...")
rows = []
for (macro, ano), sub in ab.groupby(["macroetapa","Ano"]):
    abandon = sub[sub.abandono == 1]
    retido  = sub[sub.abandono == 0]
    idade_ab = np.average(abandon.idade, weights=abandon.wt) if abandon["wt"].sum() > 0 else np.nan
    idade_rt = np.average(retido.idade,  weights=retido.wt)  if retido["wt"].sum() > 0 else np.nan
    rows.append({"macroetapa":macro,"ano":int(ano),
                  "idade_media_abandonados":idade_ab,
                  "idade_media_retidos":idade_rt,
                  "diff": idade_ab - idade_rt if not np.isnan(idade_ab) else np.nan,
                  "n_ab":len(abandon), "n_rt":len(retido)})
pd.DataFrame(rows).to_csv(OUT / "AP_AB4_idade_abandono.csv", index=False)

print("Done.")
