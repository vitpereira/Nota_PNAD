"""Strip \num{X} -> X from regression table."""
import re
from pathlib import Path

path = Path("C:/Users/vitpe/Dropbox/MEC_Pe_de_Meia/Nota_PNAD/DataWork/3_Indicators/output/T_regressao_evasao.tex")
text = path.read_text(encoding="utf-8")
# \num{X} → X
text = re.sub(r"\\num\{([^}]*)\}", r"\1", text)
path.write_text(text, encoding="utf-8")
print("Patched, len:", len(text))
print(text[:800])
