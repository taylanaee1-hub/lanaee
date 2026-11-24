clear all
set more off

* ------------------------------------------------------------
* Main regressions
* Dependent variable: ln_export
* Main policy variable: fta
* ------------------------------------------------------------

use "data/clean/tea_gravity_panel_2005_2024.dta", clear

egen country_id = group(partner_iso), label
xtset country_id year

* Verify usable regression observations
count
count if !missing(ln_export, ln_gdp_china, ln_gdp_partner, ln_distance)
count if !missing(ln_export, ln_gdp_china, ln_gdp_partner, ln_distance, fta)

* Model (1): basic gravity model
reg ln_export ln_gdp_china ln_gdp_partner ln_distance, vce(robust)
estimates store M1

* Model (2): add FTA dummy -- core specification
reg ln_export ln_gdp_china ln_gdp_partner ln_distance fta, vce(robust)
estimates store M2

* Direct test of the policy variable
test fta

* Model (3): random-effects robustness check
* Distance is time-invariant, so a country fixed-effects model would absorb it.
xtreg ln_export ln_gdp_china ln_gdp_partner ln_distance fta, re vce(cluster country_id)
estimates store M3_RE

* Display stored estimates
estimates table M1 M2 M3_RE, b(%9.4f) se(%9.4f) stats(N)

* Residual diagnostic for the core OLS model
estimates restore M2
predict resid_m2, residuals
summarize resid_m2, detail

* NOTE:
* 1. Viet Nam 2008 has missing export and is automatically excluded from ln_export regressions.
* 2. No missing Comtrade record has been manually changed to zero.
* 3. FTA=1 begins in the calendar year the agreement/preferential arrangement became effective.
