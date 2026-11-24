clear all
set more off

* TODO: 设置项目根目录
* cd ".../tea_fta_paper"

capture log close
log using "output/logs/master.log", replace text

do "do/01_clean_trade.do"
do "do/02_merge_data.do"
do "do/03_descriptive.do"
do "do/04_regression.do"

log close
