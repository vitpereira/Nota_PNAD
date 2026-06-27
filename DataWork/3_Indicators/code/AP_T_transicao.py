# -------------------------------------------------------------------------
# AP_T_transicao.py
# -------------------------------------------------------------------------
# Description:
#   Exploracoes mais profundas dos dados de transicao e abandono:
#   T1. Matriz de transicao serie_t -> destino em t+1 (Brasil, media)
#   T2. Trajetorias por demografico: probabilidade de cada destino
#       (promovido/repetente/evadido/EJA) por sexo, raca, quintil
#   T3. Probabilidade de retorno apos abandono (mesmo HH em t+1)
#   T4. Heterogeneidade do abandono por demografico
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

t = pd.read_parquet(OUT / "C20_transitions_v5.parquet")

SERIE_LBL = {1:"1o EF",2:"2o EF",3:"3o EF",4:"4o EF",5:"5o EF",
              6:"6o EF",7:"7o EF",8:"8o EF",9:"9o EF",
              10:"1o EM",11:"2o EM",12:"3o EM",13:"4o EM tec"}

# T1. Matriz de transicao: para cada nivel_t, distribuicao em t+1
print("T1: matriz de transicao...")
rows = []
for nivel in range(1, 14):
    sub = t[t["nivel_t"] == nivel].copy()
    if sub["wt"].sum() == 0: continue
    # Destino:
    sub["destino"] = "Outro"
    sub.loc[sub["flag_promocao"] == 1, "destino"] = "Promoção"
    sub.loc[sub["flag_repetencia"] == 1, "destino"] = "Repetência"
    sub.loc[sub["flag_evasao"] == 1, "destino"] = "Evasão"
    sub.loc[sub["flag_migracao_eja"] == 1, "destino"] = "Migração EJA"
    for d, s in sub.groupby("destino"):
        rows.append({"serie": SERIE_LBL[nivel],
                      "nivel": nivel,
                      "destino": d,
                      "share": s["wt"].sum() / sub["wt"].sum(),
                      "n": len(s)})
matriz = pd.DataFrame(rows)
matriz.to_csv(OUT / "AP_T1_matriz_transicao.csv", index=False)
print(f"  {len(matriz)} rows")

# T2. Probabilidade de cada destino por sexo e raca
print("T2: por sexo e raca...")
t["sexo_lbl"] = t["sexo_t"].map({1:"Homem",2:"Mulher"})
t["raca_lbl"] = t["raca_t"].map({1:"Branca",2:"Preta",4:"Parda"})

rows = []
for macroetapa in ["EF iniciais","EF finais","EM"]:
    sub = t[t["macroetapa_t"] == macroetapa].copy()
    # Total
    for cat in ["sexo_lbl","raca_lbl"]:
        for valor, sub2 in sub.groupby(cat):
            if pd.isna(valor) or sub2["wt"].sum() == 0: continue
            wt = sub2["wt"].sum()
            rows.append({"macroetapa":macroetapa,
                          "categoria":cat.replace("_lbl",""),
                          "valor":valor,
                          "prom":  np.average(sub2.flag_promocao,    weights=sub2.wt),
                          "rep":   np.average(sub2.flag_repetencia,  weights=sub2.wt),
                          "evas":  np.average(sub2.flag_evasao,      weights=sub2.wt),
                          "eja":   np.average(sub2.flag_migracao_eja,weights=sub2.wt),
                          "n":     len(sub2)})
out2 = pd.DataFrame(rows)
out2.to_csv(OUT / "AP_T2_destino_por_demo.csv", index=False)
print(f"  {len(out2)} rows")

# T3. Heterogeneidade por idade
print("T3: por idade...")
rows = []
for macroetapa in ["EF iniciais","EF finais","EM"]:
    sub = t[t["macroetapa_t"] == macroetapa].copy()
    for idade, sub2 in sub.groupby("idade_t"):
        if sub2["wt"].sum() == 0: continue
        rows.append({"macroetapa":macroetapa,
                      "idade":int(idade),
                      "prom":  np.average(sub2.flag_promocao,    weights=sub2.wt),
                      "rep":   np.average(sub2.flag_repetencia,  weights=sub2.wt),
                      "evas":  np.average(sub2.flag_evasao,      weights=sub2.wt),
                      "n":     len(sub2)})
out3 = pd.DataFrame(rows)
out3.to_csv(OUT / "AP_T3_destino_por_idade.csv", index=False)
print(f"  {len(out3)} rows")

# T4. Trajetoria ao longo do tempo (Brasil, todos anos)
print("T4: trajetoria temporal por macroetapa...")
rows = []
for (ano, macro), sub in t.groupby(["ano_t","macroetapa_t"]):
    if sub["wt"].sum() == 0: continue
    rows.append({"ano":int(ano), "macroetapa":macro,
                  "prom":  np.average(sub.flag_promocao,    weights=sub.wt),
                  "rep":   np.average(sub.flag_repetencia,  weights=sub.wt),
                  "evas":  np.average(sub.flag_evasao,      weights=sub.wt),
                  "eja":   np.average(sub.flag_migracao_eja,weights=sub.wt),
                  "n":     len(sub)})
out4 = pd.DataFrame(rows)
out4.to_csv(OUT / "AP_T4_trajetoria_temporal.csv", index=False)
print(f"  {len(out4)} rows")

print("\nAll AP_T saved.")
