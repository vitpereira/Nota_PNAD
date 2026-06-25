import re

renames_block = """* Renomear _first vars para nome unificado (apos load do PANEL_INTRA)
cap rename raca_first raca
cap rename etapa_consolid_first etapa_consolid
cap rename serie_first serie
cap rename rede_first rede
cap rename idade_first idade

"""

pattern = r'use "`PANEL_INTRA\'", clear\n'

for f in ['C2_heterogeneity_socio.do', 'C3_heterogeneity_age_rede.do', 'C4_by_uf.do']:
    fpath = r'C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD/DataWork/3_Indicators/code/' + f
    with open(fpath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    new = re.sub(pattern, r'\g<0>' + renames_block, content)
    with open(fpath, 'w', encoding='utf-8') as fh:
        fh.write(new)
    print(f'{f}: done')
