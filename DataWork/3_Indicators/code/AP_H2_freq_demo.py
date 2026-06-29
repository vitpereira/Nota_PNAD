# -------------------------------------------------------------------------
# AP_H2_freq_demo.py
# -------------------------------------------------------------------------
# Description:
#   H.2: Frequencia trimestral por demografico (sexo, raca, macroetapa)
#   I:   Curvas de retencao por coorte (sobrevivencia em EM por idade)
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
    usecols=["Ano","Trimestre","idade","sexo","raca",
              "etapa_consolid","freq_escola","peso_v1028","link_ok"])
df = df[df["link_ok"] == 1].copy()
df["sexo_lbl"] = df["sexo"].map({1:"Homem",2:"Mulher"})
df["raca_lbl"] = df["raca"].map({1:"Branca",2:"Preta",4:"Parda"})
df["macroetapa"] = df["etapa_consolid"].map({4:"EF iniciais",5:"EF finais",
                                                  10:"EM",11:"EM",12:"EM"})
df["wt"] = df["peso_v1028"].fillna(0)

# H.2a: freq por sexo x trim
rows = []
for (ano, trim, macro, sx), sub in df.groupby(["Ano","Trimestre","macroetapa","sexo_lbl"]):
    if pd.isna(sx) or pd.isna(macro) or sub["wt"].sum() == 0: continue
    rate = np.average(sub.freq_escola.fillna(0), weights=sub.wt)
    rows.append({"ano":int(ano), "trim":int(trim), "macroetapa":macro,
                  "categoria":"sexo","valor":sx,
                  "freq":rate, "n":len(sub)})
# H.2b: freq por raca x trim
for (ano, trim, macro, rc), sub in df.groupby(["Ano","Trimestre","macroetapa","raca_lbl"]):
    if pd.isna(rc) or pd.isna(macro) or sub["wt"].sum() == 0: continue
    rate = np.average(sub.freq_escola.fillna(0), weights=sub.wt)
    rows.append({"ano":int(ano), "trim":int(trim), "macroetapa":macro,
                  "categoria":"raca","valor":rc,
                  "freq":rate, "n":len(sub)})
pd.DataFrame(rows).to_csv(OUT / "AP_H2_freq_demo.csv", index=False)
print(f"H2 done")

# I.1: % matriculados em EM por idade x ano de nascimento
# Foco: idade 14-21, ano 2015-2025 (das parsed parquets)
PD_TRI = ROOT / "DataWork/1_DownloadPNADC/tmp/pnad_parsed"
rows = []
for ano in [2015,2017,2019,2021,2023,2025]:
    for q in [2]:
        p = PD_TRI / f"pnadc_0{q}{ano}.parquet"
        if not p.exists(): continue
        d = pd.read_parquet(p, columns=["V2009","V3002","V3003A","V1028","V2010","V2007"])
        for c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
        d = d[d["V2009"].between(14, 21)].copy()
        d["wt"] = d["V1028"].fillna(0)
        d["nascimento"] = ano - d["V2009"]
        d["em_matriculado"] = ((d["V3002"]==1) & (d["V3003A"]==6)).astype(int)
        for (idade, nasc), sub in d.groupby(["V2009","nascimento"]):
            if sub["wt"].sum() == 0: continue
            rate = np.average(sub.em_matriculado, weights=sub.wt)
            rows.append({"obs_ano":ano, "idade":int(idade),
                          "coorte_nascimento":int(nasc),
                          "em_matr":rate, "n":len(sub)})
pd.DataFrame(rows).to_csv(OUT / "AP_I_em_por_coorte_idade.csv", index=False)
print("I1 done")
