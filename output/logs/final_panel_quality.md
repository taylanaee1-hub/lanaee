# 最终引力模型面板数据质量报告

## 样本

- 时间：2005–2024（20年）
- 国家：35个
- 理论平衡面板行数：700
- 实际面板行数：**700**
- 有出口额记录的country-year：**699**
- 出口额缺失的country-year：**1**
- 伙伴国GDP缺失：**0**
- 中国GDP缺失：**0**
- 距离缺失：**0**
- FTA=1 的country-year数量：**141**

## FTA伙伴及生效年份

| Partner | ISO3 | Effective year | Arrangement |
|---|---|---:|---|
| Malaysia | MYS | 2005 | China-ASEAN FTA |
| Myanmar | MMR | 2005 | China-ASEAN FTA |
| Singapore | SGP | 2005 | China-ASEAN FTA |
| Thailand | THA | 2005 | China-ASEAN FTA |
| Viet Nam | VNM | 2005 | China-ASEAN FTA |
| Pakistan | PAK | 2007 | China-Pakistan FTA |
| Australia | AUS | 2015 | China-Australia FTA |
| Rep. of Korea | KOR | 2015 | China-Korea FTA |
| Japan | JPN | 2022 | RCEP |

## 出口额缺失观察

| Partner | ISO3 | Year |
|---|---|---:|
| Viet Nam | VNM | 2008 |

## 回归使用提醒

- 主回归的因变量为 ln_export；出口额缺失的观察将由Stata自动剔除。
- 本项目没有把Comtrade未返回的观察擅自改成0。
- fta按协定生效/开始实施优惠安排的当年起记为1。
- distance为时间不变变量，因此国家固定效应模型会吸收distance；主模型不采用国家FE来估计距离系数。