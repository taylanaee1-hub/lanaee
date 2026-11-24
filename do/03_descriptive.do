clear all
set more off

* ------------------------------------------------------------
* Descriptive statistics for:
* 自由贸易协定对中国茶叶出口的影响——基于引力模型的实证研究
* Final panel: 35 partners x 2005-2024
* ------------------------------------------------------------

use "data/clean/tea_gravity_panel_2005_2024.dta", clear

* Country panel identifier
egen country_id = group(partner_iso), label
xtset country_id year

* Basic structure and data-quality checks
describe
xtdescribe
duplicates report country_id year
misstable summarize export gdp_partner gdp_china distance fta

* Confirm the single missing trade observation is not silently coded as zero
list country partner_iso year export if missing(export), noobs

* Descriptive statistics
summarize export gdp_partner gdp_china distance fta
summarize ln_export ln_gdp_partner ln_gdp_china ln_distance fta

* FTA distribution
tabulate fta
tabulate country if fta==1

* Correlation matrix for regression variables
pwcorr ln_export ln_gdp_china ln_gdp_partner ln_distance fta, sig obs

* Panel summary by country
bysort country_id: egen years_trade = count(export)
bysort country_id: egen mean_export = mean(export)

preserve
collapse (first) country partner_iso years_trade mean_export distance, by(country_id)
gsort -mean_export
list country partner_iso years_trade mean_export distance in 1/35, noobs
restore
