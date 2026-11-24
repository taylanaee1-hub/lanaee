#!/usr/bin/env python3
"""
Download China HS0902 (tea) annual exports by partner from the UN Comtrade
public preview API for 2005-2024, validate the returned data, and create
raw/clean CSV files plus a data-quality report.

The public preview API is limited to 500 rows per request. We request one
year and one HS4 commodity at a time; the script aborts if any annual
response hits the cap so truncated data are never silently accepted.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
YEARS = range(2005, 2025)
REPORTER = 156  # China
CMD = "0902"
FLOW = "X"
OUT_RAW = Path("data/raw/comtrade_china_hs0902_2005_2024_raw.csv")
OUT_CLEAN = Path("data/clean/tea_exports_2005_2024.csv")
OUT_RANK = Path("output/tables/partner_export_ranking.csv")
OUT_REPORT = Path("output/logs/comtrade_data_quality.md")

for p in [OUT_RAW.parent, OUT_CLEAN.parent, OUT_RANK.parent, OUT_REPORT.parent]:
    p.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "tea-fta-gravity-paper/1.0"})

all_rows = []
annual_counts = {}
annual_errors = []

for year in YEARS:
    params = {
        "reporterCode": REPORTER,
        "period": year,
        "cmdCode": CMD,
        "flowCode": FLOW,
    }
    last_exc = None
    for attempt in range(4):
        try:
            r = session.get(BASE, params=params, timeout=60)
            r.raise_for_status()
            payload = r.json()
            rows = payload.get("data", [])
            count = int(payload.get("count", len(rows)))
            annual_counts[year] = count
            if count >= 500:
                raise RuntimeError(
                    f"{year}: API returned {count} rows, reaching preview cap; "
                    "refusing to continue because data may be truncated."
                )
            if not rows:
                raise RuntimeError(f"{year}: API returned zero rows.")
            for row in rows:
                row["_query_year"] = year
            all_rows.extend(rows)
            print(f"{year}: {count} rows")
            last_exc = None
            break
        except Exception as exc:
            last_exc = exc
            if attempt == 3:
                annual_errors.append(f"{year}: {exc}")
            else:
                time.sleep(2 ** attempt)
    if last_exc is not None:
        raise SystemExit("\n".join(annual_errors))

raw = pd.DataFrame(all_rows)
raw.to_csv(OUT_RAW, index=False, encoding="utf-8-sig")

# Flexible field extraction because API schemas can evolve.
def pick(df, names, required=True):
    for n in names:
        if n in df.columns:
            return n
    if required:
        raise KeyError(f"None of these columns found: {names}")
    return None

year_col = pick(raw, ["refYear", "period", "_query_year"])
partner_code_col = pick(raw, ["partnerCode"])
partner_iso_col = pick(raw, ["partnerISO"], required=False)
partner_desc_col = pick(raw, ["partnerDesc"], required=False)
value_col = pick(raw, ["primaryValue", "tradeValue", "netWgt"], required=False)
cmd_col = pick(raw, ["cmdCode"])
reporter_col = pick(raw, ["reporterCode"])
flow_col = pick(raw, ["flowCode"])
partner2_col = pick(raw, ["partner2Code"], required=False)
customs_col = pick(raw, ["customsCode"], required=False)
mot_col = pick(raw, ["motCode", "mosCode"], required=False)

if value_col is None:
    raise KeyError("No trade-value field found (expected primaryValue or tradeValue).")

clean = pd.DataFrame({
    "year": pd.to_numeric(raw[year_col], errors="coerce"),
    "partner_code": pd.to_numeric(raw[partner_code_col], errors="coerce"),
    "partner_iso": raw[partner_iso_col] if partner_iso_col else "",
    "country": raw[partner_desc_col] if partner_desc_col else "",
    "export": pd.to_numeric(raw[value_col], errors="coerce"),
    "cmd_code": raw[cmd_col].astype(str),
    "reporter_code": pd.to_numeric(raw[reporter_col], errors="coerce"),
    "flow_code": raw[flow_col].astype(str),
})

# Keep only partner-level bilateral records. World aggregate uses partnerCode=0.
clean = clean[clean["partner_code"].notna()].copy()
clean = clean[clean["partner_code"] != 0].copy()

# If dimensions are present, keep aggregate partner2/customs/mode records.
if partner2_col:
    p2 = pd.to_numeric(raw.loc[clean.index, partner2_col], errors="coerce")
    clean = clean[p2.fillna(0).eq(0)]
if customs_col:
    cc = raw.loc[clean.index, customs_col].astype(str)
    clean = clean[cc.isin(["C00", "nan", "None", ""])]
if mot_col:
    mc = raw.loc[clean.index, mot_col].astype(str)
    clean = clean[mc.isin(["0", "0.0", "nan", "None", ""])]

clean["year"] = clean["year"].astype("Int64")
clean["partner_code"] = clean["partner_code"].astype("Int64")
clean["reporter_code"] = clean["reporter_code"].astype("Int64")
clean["cmd_code"] = clean["cmd_code"].str.replace(r"\.0$", "", regex=True).str.zfill(4)

# Quality checks
wrong_year = clean[~clean["year"].isin(list(YEARS))]
wrong_reporter = clean[clean["reporter_code"] != REPORTER]
wrong_cmd = clean[clean["cmd_code"] != CMD]
wrong_flow = clean[~clean["flow_code"].str.upper().eq(FLOW)]
missing_export = int(clean["export"].isna().sum())
zero_export = int(clean["export"].eq(0).sum())
negative_export = int(clean["export"].lt(0).sum())
dup_mask = clean.duplicated(["partner_code", "year"], keep=False)
dup_rows = clean[dup_mask].sort_values(["partner_code", "year"])

# Do not silently aggregate true duplicates: abort if they exist.
if len(dup_rows):
    dup_rows.to_csv("output/logs/comtrade_duplicates.csv", index=False, encoding="utf-8-sig")
    raise RuntimeError(
        f"Found {len(dup_rows)} duplicate partner-year rows after filtering. "
        "Saved them to output/logs/comtrade_duplicates.csv for inspection."
    )

clean = clean.sort_values(["country", "year"]).reset_index(drop=True)
clean.to_csv(OUT_CLEAN, index=False, encoding="utf-8-sig")

ranking = (
    clean.groupby(["partner_code", "partner_iso", "country"], dropna=False, as_index=False)
    .agg(
        cumulative_export=("export", "sum"),
        years_observed=("year", "nunique"),
        zero_years=("export", lambda s: int((s == 0).sum())),
        first_year=("year", "min"),
        last_year=("year", "max"),
    )
    .sort_values("cumulative_export", ascending=False)
)
ranking.to_csv(OUT_RANK, index=False, encoding="utf-8-sig")

top40 = ranking.head(40).copy()

report = []
report.append("# UN Comtrade 数据质量报告\n")
report.append("## 查询设定\n")
report.append(f"- Reporter: China ({REPORTER})")
report.append(f"- Flow: Exports ({FLOW})")
report.append(f"- Commodity: HS {CMD} (Tea)")
report.append("- Period: 2005–2024")
report.append("- Source: UN Comtrade public preview API")
report.append("\n## API 年度返回行数\n")
report.append("| Year | Rows |")
report.append("|---:|---:|")
for y in YEARS:
    report.append(f"| {y} | {annual_counts.get(y, 0)} |")

report.append("\n## 清洗后质量检查\n")
report.append(f"- Partner-year observations: **{len(clean)}**")
report.append(f"- Unique partners: **{clean['partner_code'].nunique()}**")
report.append(f"- Missing export values: **{missing_export}**")
report.append(f"- Zero export values: **{zero_export}**")
report.append(f"- Negative export values: **{negative_export}**")
report.append(f"- Wrong reporter rows: **{len(wrong_reporter)}**")
report.append(f"- Wrong HS0902 rows: **{len(wrong_cmd)}**")
report.append(f"- Wrong export-flow rows: **{len(wrong_flow)}**")
report.append(f"- Out-of-range year rows: **{len(wrong_year)}**")
report.append("- Duplicate partner-year rows: **0**")

report.append("\n## 累计出口额前40个贸易伙伴（候选样本）\n")
report.append("| Rank | Partner | ISO3 | Years | Cumulative export (USD) |")
report.append("|---:|---|---|---:|---:|")
for i, row in enumerate(top40.itertuples(index=False), start=1):
    val = "" if pd.isna(row.cumulative_export) else f"{row.cumulative_export:,.0f}"
    report.append(
        f"| {i} | {row.country} | {row.partner_iso} | "
        f"{row.years_observed} | {val} |"
    )

report.append("\n## 说明\n")
report.append(
    "本报告只完成贸易数据层面的初筛。最终30–40国样本还需结合GDP可得性、"
    "CEPII距离匹配情况以及FTA/非FTA组别构成后确定。"
)
OUT_REPORT.write_text("\n".join(report), encoding="utf-8")

print(f"Saved raw: {OUT_RAW}")
print(f"Saved clean: {OUT_CLEAN}")
print(f"Saved ranking: {OUT_RANK}")
print(f"Saved report: {OUT_REPORT}")
