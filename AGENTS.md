# AGENTS.md

## 项目目标
协助完成课程论文《自由贸易协定对中国茶叶出口的影响——基于引力模型的实证研究》。

## 工作原则
1. 所有数据、文献和回归结果必须真实可核验。
2. 不得伪造参考文献、数据或显著性结果。
3. 任何数据清洗、删除和重编码步骤都应可复现。
4. 原始数据只读保留在 data/raw/。
5. 不要在未检查数据质量前直接跑最终回归。
6. 不预设 FTA 系数方向或显著性。
7. 主模型保持本科课程论文所需的清晰与可解释性，避免不必要的复杂化。
8. 若发现零贸易值、严重缺失、异常国家名、HS 版本不一致等问题，先报告再处理。
9. 写作必须与实际实证结果一致。

## 当前模型
基础：
ln(export) = β0 + β1 ln(gdp_china) + β2 ln(gdp_partner) + β3 ln(distance) + ε

加入政策变量：
ln(export) = β0 + β1 ln(gdp_china) + β2 ln(gdp_partner) + β3 ln(distance) + β4 fta + ε

## 当前数据目标
country, iso3, year, export, gdp_china, gdp_partner, distance, fta

## 推荐执行顺序
01_clean_trade.do → 02_merge_data.do → 03_descriptive.do → 04_regression.do → master.do
