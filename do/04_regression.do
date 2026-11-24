clear all
set more off

* TODO: 载入最终面板数据
* encode country, gen(country_id)
* xtset country_id year

* 注意：export=0 时不要直接 ln(export)
* gen ln_export = ln(export) if export>0
* gen ln_gdp_china = ln(gdp_china)
* gen ln_gdp_partner = ln(gdp_partner)
* gen ln_distance = ln(distance)

* 基础引力模型
* reg ln_export ln_gdp_china ln_gdp_partner ln_distance, vce(robust)

* 加入FTA
* reg ln_export ln_gdp_china ln_gdp_partner ln_distance fta, vce(robust)

* 随机效应稳健性检验（按数据情况使用）
* xtreg ln_export ln_gdp_china ln_gdp_partner ln_distance fta, re vce(cluster country_id)
