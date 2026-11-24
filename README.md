# Tea FTA Gravity Paper

课程论文项目：**《自由贸易协定对中国茶叶出口的影响——基于引力模型的实证研究》**

## 研究问题

在控制经济规模和地理距离等传统引力因素后，自由贸易协定（FTA）是否显著影响中国茶叶出口？

## 样本设计

- 出口国：中国
- 商品：HS 0902（Tea, whether or not flavoured）
- 暂定样本期：2005–2024
- 贸易伙伴：先从中国茶叶主要出口市场中筛选约 30–40 个国家，同时保留 FTA 与非 FTA 伙伴
- 结论必须以真实数据和真实回归结果为依据，不预设 FTA 一定显著为正

## 基础模型

```text
ln(Export_jt)
= β0
+ β1 ln(GDP_China,t)
+ β2 ln(GDP_jt)
+ β3 ln(Distance_j)
+ β4 FTA_jt
+ ε_jt
```

核心关注 `β4`。

## 变量与数据来源

| 变量 | 定义 | 计划来源 |
|---|---|---|
| export | 中国对贸易伙伴 j 的 HS0902 年度出口额 | UN Comtrade |
| gdp_china | 中国年度 GDP | World Bank WDI |
| gdp_partner | 贸易伙伴年度 GDP | World Bank WDI |
| distance | 中国与贸易伙伴双边距离 | CEPII GeoDist |
| fta | 当年中国与该伙伴已生效 FTA=1，否则=0 | 商务部自由贸易区服务网 / WTO RTA Database |

## 项目结构

```text
data/
  raw/
  clean/

do/
  01_clean_trade.do
  02_merge_data.do
  03_descriptive.do
  04_regression.do
  master.do

output/
  tables/
  figures/
  logs/

paper/
  literature_notes.md
  empirical_results.md
  paper_outline.md

AGENTS.md
README.md
```

## 分析流程

1. 导入并检查 UN Comtrade 原始数据。
2. 核验年份、HS0902、伙伴国、重复值、缺失值和零贸易值。
3. 按 2005–2024 累计出口额筛选样本国家。
4. 合并 GDP、距离和 FTA 生效年份。
5. 形成 `country × year` 长面板。
6. 描述性统计和相关性分析。
7. 运行基础引力模型。
8. 加入 FTA 变量。
9. 根据数据特征进行随机效应或 PPML 等稳健性检查。
10. 依据真实回归结果完成实证章节和结论。

## 数据与实证原则

- 永远保留 raw 数据，不覆盖原始文件。
- 所有删除或修正样本的步骤必须可追溯。
- 不人为修改数据以追求显著性。
- 若 `export=0`，不得直接计算 `ln(export)`。
- 主模型保持适合本科课程论文的复杂度。
- 若使用时间不变的 `distance`，需谨慎解释国家固定效应模型。

## 当前第一任务

将 UN Comtrade 下载的中国 HS0902 茶叶出口原始 CSV / Excel 放入 `data/raw/` 后：

- 检查字段、年份、HS 编码、国家
- 检查重复值、缺失值、零贸易值
- 汇总各国累计出口额
- 给出 30–40 个候选样本国家
- 输出数据质量报告

然后再进入 GDP、距离、FTA 数据合并阶段。
