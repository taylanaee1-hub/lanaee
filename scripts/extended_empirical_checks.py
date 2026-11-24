#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import numpy as np
from linearmodels.panel import RandomEffects
import statsmodels.api as sm

DATA = Path("data/clean/tea_gravity_panel_2005_2024.csv")
OUT_DESC = Path("output/tables/descriptive_statistics.csv")
OUT_CORR = Path("output/tables/correlation_matrix.csv")
OUT_RE = Path("output/tables/random_effects_robustness.csv")
OUT_TXT = Path("output/logs/extended_empirical_checks.txt")

df = pd.read_csv(DATA, encoding="utf-8-sig")

# Descriptive statistics on regression variables, using available observations.
vars_desc = ["export","gdp_china","gdp_partner","distance","fta",
             "ln_export","ln_gdp_china","ln_gdp_partner","ln_distance"]
desc = df[vars_desc].agg(["count","mean","std","min","max"]).T.reset_index()
desc = desc.rename(columns={"index":"variable"})
OUT_DESC.parent.mkdir(parents=True, exist_ok=True)
desc.to_csv(OUT_DESC, index=False, encoding="utf-8-sig")

# Correlation matrix for core regressors + dependent variable.
corr_vars = ["ln_export","ln_gdp_china","ln_gdp_partner","ln_distance","fta"]
corr = df[corr_vars].corr()
corr.to_csv(OUT_CORR, encoding="utf-8-sig")

# Random-effects panel robustness check.
re_df = df[["partner_iso","year","ln_export","ln_gdp_china","ln_gdp_partner","ln_distance","fta"]].dropna().copy()
re_df = re_df.set_index(["partner_iso","year"])
X = sm.add_constant(re_df[["ln_gdp_china","ln_gdp_partner","ln_distance","fta"]], has_constant="add")
re_mod = RandomEffects(re_df["ln_export"], X)
re_res = re_mod.fit(cov_type="clustered", cluster_entity=True)

rows = []
for var in re_res.params.index:
    rows.append({
        "variable": var,
        "coef": re_res.params[var],
        "std_err_cluster": re_res.std_errors[var],
        "t": re_res.tstats[var],
        "p_value": re_res.pvalues[var],
        "n": int(re_res.nobs),
        "r2_overall": re_res.rsquared_overall,
        "r2_between": re_res.rsquared_between,
        "r2_within": re_res.rsquared_within,
    })
pd.DataFrame(rows).to_csv(OUT_RE, index=False, encoding="utf-8-sig")

text = []
text.append("DESCRIPTIVE STATISTICS")
text.append(desc.to_string(index=False))
text.append("\nCORRELATION MATRIX")
text.append(corr.to_string())
text.append("\nRANDOM EFFECTS ROBUSTNESS")
text.append(str(re_res.summary))
OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
OUT_TXT.write_text("\n".join(text), encoding="utf-8")

print(desc.to_string(index=False))
print("\nRandom effects:")
print(pd.DataFrame(rows).to_string(index=False))
