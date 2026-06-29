# -------------------------------------------------------------------------
# AP_extras.py
# -------------------------------------------------------------------------
# Description:
#   Analises extras para o apendice:
#   X1. Composicao de quem abandona: % por sexo, % por raca, % por idade,
#       % com renda <R$230, etc. (qual eh o perfil do abandonado?)
#   X2. Taxa de evasao por quintil x macroetapa x ano (heterogeneidade
#       socioeconomica de evasao)
#   X3. Distribuicao de defasagem por quintil de renda (defasagem é mais
#       comum em pobres?)
#   X4. Probabilidade de promocao por raca e renda combinados (2x2)
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "DataWork/3_Indicators/output"

# Usar AP_C micro (abandono) e C20 transitions (fluxo) que ja temos
ab = pd.read_parquet(OUT / "AP_C_micro_abandono.parquet")
t  = pd.read_parquet(OUT / "C20_transitions_v5.parquet")

# X1. Perfil de quem abandona: % do TOTAL de abandonos que vem de cada grupo
print("X1: perfil de quem abandona...")
# Need sexo, raca do AB micro - they were added in AP_AB but not saved to micro
# Re-merge
import pyreadstat
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
demo, _ = pyreadstat.read_dta(str(LINK),
    usecols=["person_id","Ano","Trimestre","sexo","raca","idade"])
demo = demo[demo.Trimestre==1].drop(columns=["Trimestre","idade"])
demo["sexo"] = pd.to_numeric(demo["sexo"], errors="coerce")
demo["raca"] = pd.to_numeric(demo["raca"], errors="coerce")
demo["sexo_lbl"] = demo["sexo"].map({1:"Homem",2:"Mulher"})
demo["raca_lbl"] = demo["raca"].map({1:"Branca",2:"Preta",4:"Parda",
                                          3:"Amarela",5:"Indigena"})
ab = ab.merge(demo[["person_id","Ano","sexo_lbl","raca_lbl"]],
                on=["person_id","Ano"], how="left")

# Macroetapa
ab["macroetapa"] = ab["etapa_consolid"].map({4:"EF iniciais",5:"EF finais",
                                                  10:"EM",11:"EM",12:"EM"})

# Pop total e pop abandonados
rows = []
for macro in ["EF iniciais","EF finais","EM"]:
    sub = ab[ab.macroetapa==macro]
    abandon = sub[sub.abandono==1]
    wt_all = sub.wt.sum()
    wt_ab = abandon.wt.sum()
    # Idade media
    rows.append({"macroetapa":macro, "metric":"idade_media",
                  "pop_geral": np.average(sub.idade, weights=sub.wt),
                  "abandonados": np.average(abandon.idade, weights=abandon.wt) if wt_ab > 0 else np.nan})
    # Sexo
    for sx in ["Homem","Mulher"]:
        rows.append({"macroetapa":macro, "metric":f"share_{sx}",
                      "pop_geral": sub[sub.sexo_lbl==sx].wt.sum() / wt_all,
                      "abandonados": abandon[abandon.sexo_lbl==sx].wt.sum() / wt_ab if wt_ab > 0 else np.nan})
    # Raca
    for rc in ["Branca","Preta","Parda"]:
        rows.append({"macroetapa":macro, "metric":f"share_{rc}",
                      "pop_geral": sub[sub.raca_lbl==rc].wt.sum() / wt_all,
                      "abandonados": abandon[abandon.raca_lbl==rc].wt.sum() / wt_ab if wt_ab > 0 else np.nan})
pd.DataFrame(rows).to_csv(OUT / "AP_X1_perfil_abandono.csv", index=False)

# X2. Evasao por quintil x macroetapa x ano (ja temos AP_E)
print("X2: ja em AP_E_fluxos_por_quintil")

# X4. Probabilidade de promocao por raca + renda combinados (matrix)
print("X4: prom por raca + quintil...")
t["sexo_lbl"] = t["sexo_t"].map({1:"Homem",2:"Mulher"})
t["raca_lbl"] = t["raca_t"].map({1:"Branca",2:"Preta",4:"Parda"})
# Quintil dentro do ano
rows = []
for ano, sub in t.groupby("ano_t"):
    sub = sub.dropna(subset=["renda_t","raca_lbl"]).copy()
    if len(sub) == 0: continue
    qtl = sub["renda_t"].quantile([0.2,0.4,0.6,0.8]).values
    def to_q(r):
        if r < qtl[0]: return "Q1 (pobre)"
        if r < qtl[3]: return "Q2-Q4"
        return "Q5 (rico)"
    sub["q3"] = sub["renda_t"].apply(to_q)
    for (macro, rc, q), s in sub.groupby(["macroetapa_t","raca_lbl","q3"]):
        if s["wt"].sum() == 0: continue
        rows.append({"ano":int(ano), "macroetapa":macro,
                      "raca":rc, "quintil":q,
                      "prom": np.average(s.flag_promocao,    weights=s.wt),
                      "evas": np.average(s.flag_evasao,      weights=s.wt),
                      "n":   len(s)})
pd.DataFrame(rows).to_csv(OUT / "AP_X4_prom_raca_quintil.csv", index=False)
print("Done X1, X4")
