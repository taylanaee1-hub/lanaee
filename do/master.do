clear all
set more off

* Run this file from the repository root folder.
* Example:
* cd "C:/.../lanaee"

capture log close
log using "output/logs/stata_master.log", replace text

display "=== Descriptive statistics ==="
do "do/03_descriptive.do"

display "=== Gravity regressions ==="
do "do/04_regression.do"

log close
display "Finished. See output/logs/stata_master.log"
