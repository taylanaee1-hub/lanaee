#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import pandas as pd

TRADE = Path("data/clean/tea_exports_2005_2024.csv")
GDP = Path("data/clean/worldbank_gdp_2005_2024.csv")
DIST = Path("data/clean/cepii_distance_china.csv")
CAND = Path("output/tables/sample_candidates_covariates.csv")
FTA = Path("data/manual/fta_effective_years.csv")

OUT_CSV = Path("data/clean/tea_gravity_panel_2005_2024.csv")
OUT_DTA = Path("data/clean/tea_gravity_panel_2005_2024.dta")
OUT_SAMPLE = Path("output/tables/final_sample_35.csv")
OUT_REPORT = Path("output/logs/final_panel_quality.md")

YEARS = list(range(2005, 2025))

trade = pd.read_csv(TRADE, encoding="utf-8-sig")
gdp = pd.read_csv(GDP, encoding="utf-8-sig")
dist = pd.read_csv(DIST, encoding="utf-8-sig")
cand = pd.read_csv(CAND, encoding="utf-8-sig")
fta_map = pd.read_csv(FTA)

sample = cand[cand["final_sample"].astype(str).str.lower().isin(["true","1"])].copy()
if len(sample) != 35:
    raise RuntimeError(f"Expected 35 final sample countries, found {len(sample)}")

sample = sample[["partner_iso","country","cumulative_export"]].drop_duplicates("partner_iso")
sample.to_csv(OUT_SAMPLE, index=False, encoding="utf-8-sig")

# Balanced country-year skeleton: missing trade observations stay missing, never silently set to zero.
grid = (
    sample[["partner_iso","country"]]
    .assign(key=1)
    .merge(pd.DataFrame({"year":YEARS, "key":1}), on="key")
    .drop(columns="key")
)

t = trade[trade["partner_iso"].isin(sample["partner_iso"])][["partner_iso","year","export"]].copy()
panel = grid.merge(t, on=["partner_iso","year"], how="left", validate="one_to_one")
panel["trade_observed"] = panel["export"].notna().astype(int)

# Partner GDP
gp = gdp[gdp["iso3"].isin(sample["partner_iso"])][["iso3","year","gdp"]].rename(
    columns={"iso3":"partner_iso","gdp":"gdp_partner"}
)
panel = panel.merge(gp, on=["partner_iso","year"], how="left", validate="one_to_one")

# China GDP
gc = gdp[gdp["iso3"]=="CHN"][["year","gdp"]].rename(columns={"gdp":"gdp_china"})
panel = panel.merge(gc, on="year", how="left", validate="many_to_one")

# Distance
d = dist[["iso_d","dist"]].rename(columns={"iso_d":"partner_iso","dist":"distance"})
panel = panel.merge(d, on="partner_iso", how="left", validate="many_to_one")

# FTA metadata and dummy
fm = fta_map[["iso3","fta_effective_year","fta_arrangement"]].rename(columns={"iso3":"partner_iso"})
panel = panel.merge(fm, on="partner_iso", how="left", validate="many_to_one")
panel["fta_effective_year"] = pd.to_numeric(panel["fta_effective_year"], errors="coerce")
panel["fta"] = (
    panel["fta_effective_year"].notna()
    & (panel["year"] >= panel["fta_effective_year"])
).astype(int)
panel["fta_arrangement"] = panel["fta_arrangement"].fillna("None")

# Logs for main OLS. Do not log missing trade.
panel["ln_export"] = np.where(panel["export"] > 0, np.log(panel["export"]), np.nan)
panel["ln_gdp_partner"] = np.where(panel["gdp_partner"] > 0, np.log(panel["gdp_partner"]), np.nan)
panel["ln_gdp_china"] = np.where(panel["gdp_china"] > 0, np.log(panel["gdp_china"]), np.nan)
panel["ln_distance"] = np.where(panel["distance"] > 0, np.log(panel["distance"]), np.nan)

panel = panel.sort_values(["partner_iso","year"]).reset_index(drop=True)

# Quality assertions
if len(panel) != 35 * 20:
    raise RuntimeError(f"Expected 700 balanced rows, got {len(panel)}")
if panel[["gdp_partner","gdp_china","distance"]].isna().any().any():
    raise RuntimeError("Missing GDP/distance in final sample panel")
if panel.duplicated(["partner_iso","year"]).any():
    raise RuntimeError("Duplicate partner-year observations in final panel")

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
panel.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

# Stata-compatible names/types
stata = panel.copy()
stata["country"] = stata["country"].astype(str)
stata["partner_iso"] = stata["partner_iso"].astype(str)
stata["fta_arrangement"] = stata["fta_arrangement"].astype(str)
stata.to_stata(OUT_DTA, write_index=False, version=118)

missing_trade = panel[panel["export"].isna()][["country","partner_iso","year"]]
fta_countries = (
    panel[panel["fta_effective_year"].notna()]
    [["country","partner_iso","fta_effective_year","fta_arrangement"]]
    .drop_duplicates()
    .sort_values(["fta_effective_year","country"])
)

lines = [
    "# 最终引力模型面板数据质量报告",
    "",
    "## 样本",
    "",
    "- 时间：2005–2024（20年）",
    "- 国家：35个",
    "- 理论平衡面板行数：700",
    f"- 实际面板行数：**{len(panel)}**",
    f"- 有出口额记录的country-year：**{int(panel['trade_observed'].sum())}**",
    f"- 出口额缺失的country-year：**{int(panel['export'].isna().sum())}**",
    f"- 伙伴国GDP缺失：**{int(panel['gdp_partner'].isna().sum())}**",
    f"- 中国GDP缺失：**{int(panel['gdp_china'].isna().sum())}**",
    f"- 距离缺失：**{int(panel['distance'].isna().sum())}**",
    f"- FTA=1 的country-year数量：**{int(panel['fta'].sum())}**",
    "",
    "## FTA伙伴及生效年份",
    "",
    "| Partner | ISO3 | Effective year | Arrangement |",
    "|---|---|---:|---|",
]
for r in fta_countries.itertuples(index=False):
    lines.append(f"| {r.country} | {r.partner_iso} | {int(r.fta_effective_year)} | {r.fta_arrangement} |")

lines += ["", "## 出口额缺失观察"]
if len(missing_trade):
    lines += ["", "| Partner | ISO3 | Year |", "|---|---|---:|"]
    for r in missing_trade.itertuples(index=False):
        lines.append(f"| {r.country} | {r.partner_iso} | {r.year} |")
else:
    lines.append("")
    lines.append("- 无")

lines += [
    "",
    "## 回归使用提醒",
    "",
    "- 主回归的因变量为 ln_export；出口额缺失的观察将由Stata自动剔除。",
    "- 本项目没有把Comtrade未返回的观察擅自改成0。",
    "- fta按协定生效/开始实施优惠安排的当年起记为1。",
    "- distance为时间不变变量，因此国家固定效应模型会吸收distance；主模型不采用国家FE来估计距离系数。",
]
OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

print(panel.head())
print(f"Saved final CSV: {OUT_CSV}")
print(f"Saved final DTA: {OUT_DTA}")
print(f"Missing trade observations: {len(missing_trade)}")
print(f"FTA country-years: {int(panel['fta'].sum())}")
