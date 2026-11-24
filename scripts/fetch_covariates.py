#!/usr/bin/env python3
from pathlib import Path
import io, zipfile
import pandas as pd
import requests

RANK = Path("output/tables/partner_export_ranking.csv")
OUT_GDP = Path("data/clean/worldbank_gdp_2005_2024.csv")
OUT_DIST = Path("data/clean/cepii_distance_china.csv")
OUT_CAND = Path("output/tables/sample_candidates_covariates.csv")
OUT_REPORT = Path("output/logs/covariate_availability.md")

YEARS = list(range(2005, 2025))
GDP_IND = "NY.GDP.MKTP.CD"

rank = pd.read_csv(RANK, encoding="utf-8-sig")
rank["partner_iso"] = rank["partner_iso"].astype(str).str.strip()

# Start from the top 45 trade partners so there is room to exclude special cases/missing data.
cand = rank.head(45).copy()
# Mainland-Hong Kong CEPA is a special institutional arrangement and Hong Kong is not a sovereign state.
cand["excluded_special"] = cand["partner_iso"].eq("HKG")
isos = cand.loc[~cand["excluded_special"], "partner_iso"].dropna().unique().tolist()

# ---------- World Bank GDP ----------
wb_codes = sorted(set(isos + ["CHN"]))
url = f"https://api.worldbank.org/v2/country/all/indicator/{GDP_IND}"
params = {"format":"json", "date":"2005:2024", "per_page":20000}
r = requests.get(url, params=params, timeout=90, headers={"User-Agent":"tea-fta-gravity-paper/1.0"})
r.raise_for_status()
payload = r.json()
if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
    raise RuntimeError(f"Unexpected World Bank API response: {str(payload)[:500]}")

rows = []
for rec in payload[1]:
    rows.append({
        "iso3": rec.get("countryiso3code"),
        "year": int(rec["date"]) if rec.get("date") else None,
        "gdp": rec.get("value"),
        "country_wb": (rec.get("country") or {}).get("value"),
    })
gdp = pd.DataFrame(rows)
gdp = gdp[gdp["iso3"].isin(wb_codes) & gdp["year"].isin(YEARS)].copy()
gdp["gdp"] = pd.to_numeric(gdp["gdp"], errors="coerce")
gdp = gdp.sort_values(["iso3","year"]).reset_index(drop=True)
OUT_GDP.parent.mkdir(parents=True, exist_ok=True)
gdp.to_csv(OUT_GDP, index=False, encoding="utf-8-sig")

# ---------- CEPII GeoDist ----------
urls = [
    "https://www.cepii.fr/distance/dist_cepii.zip",
    "http://www.cepii.fr/distance/dist_cepii.zip",
]
content = None
last = None
for u in urls:
    try:
        rr = requests.get(u, timeout=120, headers={"User-Agent":"tea-fta-gravity-paper/1.0"})
        rr.raise_for_status()
        content = rr.content
        break
    except Exception as exc:
        last = exc
if content is None:
    raise RuntimeError(f"Could not download CEPII GeoDist: {last}")

with zipfile.ZipFile(io.BytesIO(content)) as z:
    names = z.namelist()
    target = next((n for n in names if n.lower().endswith("dist_cepii.xls")), None)
    if target is None:
        raise RuntimeError(f"dist_cepii.xls not found in CEPII zip: {names[:10]}")
    with z.open(target) as fh:
        dist_all = pd.read_excel(fh, engine="xlrd")

required = {"iso_o","iso_d","dist"}
missing = required - set(dist_all.columns)
if missing:
    raise RuntimeError(f"CEPII columns missing: {missing}; found={dist_all.columns.tolist()}")

dist = dist_all[(dist_all["iso_o"]=="CHN") & (dist_all["iso_d"].isin(isos))].copy()
keep = [c for c in ["iso_o","iso_d","dist","distcap","distw","distwces","contig","comlang_off"] if c in dist.columns]
dist = dist[keep].drop_duplicates(["iso_o","iso_d"]).sort_values("iso_d")
dist.to_csv(OUT_DIST, index=False, encoding="utf-8-sig")

# ---------- Availability report ----------
gdp_av = (
    gdp[gdp["iso3"].isin(isos)]
    .groupby("iso3", as_index=False)
    .agg(
        gdp_years=("gdp", lambda s: int(s.notna().sum())),
        gdp_missing=("gdp", lambda s: int(s.isna().sum())),
    )
)
dist_av = dist[["iso_d","dist"]].rename(columns={"iso_d":"partner_iso","dist":"distance"})

out = cand.merge(gdp_av, left_on="partner_iso", right_on="iso3", how="left").drop(columns=["iso3"], errors="ignore")
out = out.merge(dist_av, on="partner_iso", how="left")
out["gdp_years"] = out["gdp_years"].fillna(0).astype(int)
out["gdp_missing"] = 20 - out["gdp_years"]
out["distance_missing"] = out["distance"].isna()
out["eligible"] = (~out["excluded_special"]) & (out["gdp_years"] >= 18) & (~out["distance_missing"])
out.to_csv(OUT_CAND, index=False, encoding="utf-8-sig")

eligible = out[out["eligible"]].copy()
# Keep a clean, manageable sample of 35 highest-ranked eligible sovereign partners.
final35 = eligible.head(35).copy()
final35["final_sample"] = True
out["final_sample"] = out["partner_iso"].isin(final35["partner_iso"])
out.to_csv(OUT_CAND, index=False, encoding="utf-8-sig")

lines = [
    "# GDP与CEPII距离可得性检查",
    "",
    "## 数据来源",
    "",
    "- GDP: World Bank WDI, indicator NY.GDP.MKTP.CD (current US$), 2005–2024",
    "- Distance: CEPII GeoDist dyadic file dist_cepii.xls, variable dist",
    "- 初始候选：按2005–2024累计茶叶出口额前45个市场",
    "- 特殊排除：中国香港（HKG），因其CEPA安排和经济体性质与主权国家样本可比性较弱",
    "",
    "## 候选市场检查",
    "",
    "| Rank | Partner | ISO3 | GDP years | Distance km | Eligible | Final sample |",
    "|---:|---|---|---:|---:|---|---|",
]
for idx,row in out.reset_index(drop=True).iterrows():
    ranknum = idx + 1
    d = "" if pd.isna(row["distance"]) else f'{row["distance"]:.1f}'
    lines.append(
        f'| {ranknum} | {row["country"]} | {row["partner_iso"]} | '
        f'{row["gdp_years"]} | {d} | {"Yes" if row["eligible"] else "No"} | '
        f'{"Yes" if row["final_sample"] else ""} |'
    )

lines += [
    "",
    "## 最终样本原则",
    "",
    "在贸易规模靠前的候选市场中，排除中国香港，并要求2005–2024年GDP至少有18年可得、CEPII距离可匹配。",
    "在符合条件的经济体中按累计茶叶出口额排序选取前35个，兼顾样本规模与数据可操作性。",
    "",
    f"- 最终样本国家数：**{len(final35)}**",
    f"- FTA变量将在下一步按正式生效年份逐国编码。",
]
OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"Eligible: {len(eligible)}; final sample: {len(final35)}")
print(final35[["country","partner_iso","gdp_years","distance"]].to_string(index=False))
