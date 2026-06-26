# -------------------------------------------------------------------------
# C28_diagnostic_intra_year.py
# -------------------------------------------------------------------------
# Author: Vitor
# Last update: 2026-06-26
#
# Description:
#   Diagnostico da queda abrupta na inconsistencia intra-ano de V3006
#   pos-2020. Mede % de pessoas que reportam etapa/serie diferente entre
#   trimestres consecutivos do mesmo ano civil. Hipotese: mudanca CAPI->CATI
#   em marco de 2020 introduziu carry-over de respostas anteriores.
#
# Outputs:
#   ../output/C28_within_year_consistency.csv
#   ../output/C28_visit_pair_changes.csv
# -------------------------------------------------------------------------

from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LINK = ROOT / "DataWork/2_PanelBuild/tmp/pnadc_linked.dta"
OUT_DIR = ROOT / "DataWork/3_Indicators/output"

print("Loading linked panel...", flush=True)
df, _ = pyreadstat.read_dta(str(LINK),
    usecols=['person_id','Ano','Trimestre','idade','etapa_consolid',
             'serie','visita','link_ok'])
df = df[(df['person_id'].astype(str).str.strip() != '') & (df['link_ok']==1)]
df = df.dropna(subset=['etapa_consolid','serie','visita'])
df['es'] = df['etapa_consolid'].astype(int).astype(str) + '_' + df['serie'].astype(int).astype(str)
print(f"Rows after cleaning: {len(df):,}", flush=True)

# Within (person, ano), how many distinct (etapa, serie) values?
g = df.groupby(['person_id','Ano'], sort=False).agg(
    n_obs=('Trimestre','count'),
    n_unique=('es','nunique')
).reset_index()
multi = g[g['n_obs']>=2].copy()
multi['changed'] = (multi['n_unique']>1).astype(int)
within = (multi.groupby('Ano')
          .agg(pct_changed=('changed','mean'),
               n_persons=('person_id','count')))
within['pct_changed'] = (within['pct_changed']*100).round(2)
within.to_csv(OUT_DIR / 'C28_within_year_consistency.csv')
print("\n==== % WITHIN-PERSON com SERIE/ETAPA inconsistente intra-ano ====")
print(within.to_string())

# Visit-pair changes
gp = df.groupby(['person_id','Ano','visita'], as_index=False).first()
gp = gp.sort_values(['person_id','Ano','visita'])
gp['prev_es']     = gp.groupby(['person_id','Ano'])['es'].shift(1)
gp['prev_visita'] = gp.groupby(['person_id','Ano'])['visita'].shift(1)
gp['change']      = ((gp['es']!=gp['prev_es']) & gp['prev_es'].notna()).astype(int)
gp['is_consec']   = (gp['visita']-gp['prev_visita']).eq(1)

sub = gp[gp['is_consec'] & gp['prev_es'].notna()].copy()
sub['pair'] = sub['prev_visita'].astype(int).astype(str)+'->'+sub['visita'].astype(int).astype(str)
pivot = sub.groupby(['Ano','pair'])['change'].mean().unstack()
pivot = (pivot*100).round(1)
pivot.to_csv(OUT_DIR / 'C28_visit_pair_changes.csv')

print("\n==== % MUDANCA between consecutive visitas, by Ano x visit-pair ====")
print(pivot.to_string())

print("\nSaved C28_within_year_consistency.csv")
print("Saved C28_visit_pair_changes.csv")
