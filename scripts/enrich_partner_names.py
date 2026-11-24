#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import requests

REF_URL = "https://comtradeapi.un.org/files/v1/app/reference/partnerAreas.json"
CLEAN = Path("data/clean/tea_exports_2005_2024.csv")
RAW = Path("data/raw/comtrade_china_hs0902_2005_2024_raw.csv")
RANK = Path("output/tables/partner_export_ranking.csv")
REPORT = Path("output/logs/comtrade_data_quality.md")

r = requests.get(REF_URL, timeout=60, headers={"User-Agent":"tea-fta-gravity-paper/1.0"})
r.raise_for_status()
refs = pd.DataFrame(r.json()["results"])
refs = refs.rename(columns={
    "PartnerCode":"partner_code",
    "PartnerDesc":"country",
    "PartnerCodeIsoAlpha3":"partner_iso",
    "isGroup":"is_group",
})
refs["partner_code"] = pd.to_numeric(refs["partner_code"], errors="coerce").astype("Int64")
refs["partner_iso"] = refs.get("partner_iso", "").fillna("").astype(str).str.strip()
refs["country"] = refs.get("country", "").fillna("").astype(str).str.strip()

clean = pd.read_csv(CLEAN, encoding="utf-8-sig")
clean["partner_code"] = pd.to_numeric(clean["partner_code"], errors="coerce").astype("Int64")
clean = clean.drop(columns=[c for c in ["partner_iso","country"] if c in clean.columns])
clean = clean.merge(
    refs[["partner_code","partner_iso","country","is_group"]],
    on="partner_code",
    how="left",
    validate="many_to_one",
)

missing_name = clean["country"].isna() | clean["country"].eq("")
missing_iso = clean["partner_iso"].isna() | clean["partner_iso"].eq("")
if missing_name.any():
    bad = sorted(clean.loc[missing_name, "partner_code"].dropna().unique().tolist())
    raise RuntimeError(f"Missing partner names for codes: {bad}")

clean["partner_iso"] = clean["partner_iso"].fillna("")
clean["country"] = clean["country"].fillna("")
clean["is_group"] = clean["is_group"].fillna(False).astype(bool)

clean = clean[[
    "year","partner_code","partner_iso","country","export",
    "cmd_code","reporter_code","flow_code","is_group"
]].sort_values(["country","year"]).reset_index(drop=True)
clean.to_csv(CLEAN, index=False, encoding="utf-8-sig")

ranking = (
    clean.groupby(["partner_code","partner_iso","country","is_group"], dropna=False, as_index=False)
    .agg(
        cumulative_export=("export","sum"),
        years_observed=("year","nunique"),
        zero_years=("export", lambda s: int((s == 0).sum())),
        first_year=("year","min"),
        last_year=("year","max"),
    )
    .sort_values("cumulative_export", ascending=False)
)
ranking.to_csv(RANK, index=False, encoding="utf-8-sig")

raw = pd.read_csv(RAW, encoding="utf-8-sig")
raw_year_col = "refYear" if "refYear" in raw.columns else ("period" if "period" in raw.columns else "_query_year")
annual_counts = raw.groupby(raw_year_col).size().to_dict()

dup_rows = clean[clean.duplicated(["partner_code","year"], keep=False)]
top40 = ranking.head(40)

lines = [
    "# UN Comtrade 数据质量报告",
    "",
    "## 查询设定",
    "",
    "- Reporter: China (156)",
    "- Flow: Exports (X)",
    "- Commodity: HS 0902 (Tea)",
    "- Period: 2005–2024",
    "- Source: UN Comtrade public preview API",
    "- Partner names/ISO3: UN Comtrade official Partners reference table",
    "",
    "## API 年度返回行数",
    "",
    "| Year | Rows |",
    "|---:|---:|",
]
for y in range(2005, 2025):
    lines.append(f"| {y} | {int(annual_counts.get(y, 0))} |")

lines += [
    "",
    "## 清洗后质量检查",
    "",
    f"- Partner-year observations: **{len(clean)}**",
    f"- Unique partners: **{clean['partner_code'].nunique()}**",
    f"- Missing partner names: **{int((clean['country']=='').sum())}**",
    f"- Missing ISO3 codes: **{int((clean['partner_iso']=='').sum())}**",
    f"- Missing export values: **{int(clean['export'].isna().sum())}**",
    f"- Zero export values: **{int((clean['export']==0).sum())}**",
    f"- Negative export values: **{int((clean['export']<0).sum())}**",
    f"- Duplicate partner-year rows: **{len(dup_rows)}**",
    "",
    "## 累计出口额前40个贸易伙伴（候选样本）",
    "",
    "| Rank | Partner | ISO3 | Years | Cumulative export (USD) |",
    "|---:|---|---|---:|---:|",
]
for i,row in enumerate(top40.itertuples(index=False), start=1):
    val=f"{row.cumulative_export:,.0f}"
    lines.append(f"| {i} | {row.country} | {row.partner_iso} | {row.years_observed} | {val} |")

lines += [
    "",
    "## 说明",
    "",
    "最终30–40国样本还需结合GDP可得性、CEPII距离匹配情况、FTA/非FTA组别构成，",
    "并排除非标准经济体/区域汇总项后确定。",
]
REPORT.write_text("\n".join(lines), encoding="utf-8")
print("Partner names/ISO3 enriched and ranking/report regenerated.")
