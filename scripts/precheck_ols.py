#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import statsmodels.api as sm

DATA = Path("data/clean/tea_gravity_panel_2005_2024.csv")
OUT_CSV = Path("output/tables/python_ols_precheck.csv")
OUT_TXT = Path("output/logs/python_ols_precheck.txt")

df = pd.read_csv(DATA, encoding="utf-8-sig")

specs = {
    "M1_basic": ["ln_gdp_china","ln_gdp_partner","ln_distance"],
    "M2_fta": ["ln_gdp_china","ln_gdp_partner","ln_distance","fta"],
}

rows = []
txt = [
    "Python OLS pre-check (not a substitute for final Stata log)",
    "Robust covariance: HC1, matching Stata vce(robust) convention closely.",
    "",
]
for name, xs in specs.items():
    d = df[["ln_export"] + xs].dropna().copy()
    X = sm.add_constant(d[xs], has_constant="add")
    y = d["ln_export"]
    model = sm.OLS(y, X).fit(cov_type="HC1")
    txt.append("=" * 78)
    txt.append(name)
    txt.append(model.summary().as_text())
    txt.append("")
    for var in model.params.index:
        rows.append({
            "model": name,
            "variable": var,
            "coef": model.params[var],
            "std_err_hc1": model.bse[var],
            "t": model.tvalues[var],
            "p_value": model.pvalues[var],
            "n": int(model.nobs),
            "r2": model.rsquared,
            "adj_r2": model.rsquared_adj,
        })

out = pd.DataFrame(rows)
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
OUT_TXT.write_text("\n".join(txt), encoding="utf-8")

print(out.to_string(index=False))
