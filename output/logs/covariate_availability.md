# GDP与CEPII距离可得性检查

## 数据来源

- GDP: World Bank WDI, indicator NY.GDP.MKTP.CD (current US$), 2005–2024
- Distance: CEPII GeoDist dyadic file dist_cepii.xls, variable dist
- 初始候选：按2005–2024累计茶叶出口额前45个市场
- 特殊排除：中国香港（HKG），因其CEPA安排和经济体性质与主权国家样本可比性较弱

## 候选市场检查

| Rank | Partner | ISO3 | GDP years | Distance km | Eligible | Final sample |
|---:|---|---|---:|---:|---|---|
| 1 | Morocco | MAR | 20 | 9951.1 | Yes | Yes |
| 2 | China, Hong Kong SAR | HKG | 0 |  | No |  |
| 3 | Malaysia | MYS | 20 | 4355.0 | Yes | Yes |
| 4 | USA | USA | 20 | 10993.7 | Yes | Yes |
| 5 | Japan | JPN | 20 | 2098.1 | Yes | Yes |
| 6 | Ghana | GHA | 20 | 11831.6 | Yes | Yes |
| 7 | Viet Nam | VNM | 20 | 2330.8 | Yes | Yes |
| 8 | Mauritania | MRT | 20 | 11903.6 | Yes | Yes |
| 9 | Senegal | SEN | 20 | 12312.9 | Yes | Yes |
| 10 | Algeria | DZA | 20 | 9117.7 | Yes | Yes |
| 11 | Russian Federation | RUS | 20 | 5795.0 | Yes | Yes |
| 12 | Togo | TGO | 20 | 11656.9 | Yes | Yes |
| 13 | Uzbekistan | UZB | 20 | 3943.6 | Yes | Yes |
| 14 | Germany | DEU | 20 | 7785.3 | Yes | Yes |
| 15 | Mali | MLI | 20 | 11841.6 | Yes | Yes |
| 16 | Thailand | THA | 20 | 3303.9 | Yes | Yes |
| 17 | France | FRA | 20 | 8225.2 | Yes | Yes |
| 18 | Myanmar | MMR | 20 | 3234.1 | Yes | Yes |
| 19 | Gambia | GMB | 20 | 12365.8 | Yes | Yes |
| 20 | Benin | BEN | 20 | 11545.9 | Yes | Yes |
| 21 | Libya | LBY | 20 | 8743.5 | Yes | Yes |
| 22 | Niger | NER | 20 | 11024.2 | Yes | Yes |
| 23 | Pakistan | PAK | 20 | 3882.9 | Yes | Yes |
| 24 | United Kingdom | GBR | 20 | 8151.4 | Yes | Yes |
| 25 | Guinea | GIN | 20 | 12651.8 | Yes | Yes |
| 26 | Australia | AUS | 20 | 8956.4 | Yes | Yes |
| 27 | Canada | CAN | 20 | 10598.3 | Yes | Yes |
| 28 | Cameroon | CMR | 20 | 11002.3 | Yes | Yes |
| 29 | Spain | ESP | 20 | 9232.3 | Yes | Yes |
| 30 | Singapore | SGP | 20 | 4484.7 | Yes | Yes |
| 31 | Poland | POL | 20 | 6947.9 | Yes | Yes |
| 32 | Rep. of Korea | KOR | 20 | 955.7 | Yes | Yes |
| 33 | Netherlands | NLD | 20 | 7831.1 | Yes | Yes |
| 34 | Afghanistan | AFG | 20 | 4180.4 | Yes | Yes |
| 35 | Iran | IRN | 20 | 5609.0 | Yes | Yes |
| 36 | Belgium | BEL | 20 | 7970.8 | Yes | Yes |
| 37 | Côte d'Ivoire | CIV | 20 | 12145.1 | Yes |  |
| 38 | Sri Lanka | LKA | 20 | 5171.5 | Yes |  |
| 39 | Ukraine | UKR | 20 | 6460.8 | Yes |  |
| 40 | United Arab Emirates | ARE | 20 | 5966.4 | Yes |  |
| 41 | Tajikistan | TJK | 20 | 4052.9 | Yes |  |
| 42 | Other Asia, nes | S19 | 0 |  | No |  |
| 43 | Saudi Arabia | SAU | 20 | 6605.2 | Yes |  |
| 44 | Tunisia | TUN | 20 | 8646.6 | Yes |  |
| 45 | Turkmenistan | TKM | 20 | 4940.0 | Yes |  |

## 最终样本原则

在贸易规模靠前的候选市场中，排除中国香港，并要求2005–2024年GDP至少有18年可得、CEPII距离可匹配。
在符合条件的经济体中按累计茶叶出口额排序选取前35个，兼顾样本规模与数据可操作性。

- 最终样本国家数：**35**
- FTA变量将在下一步按正式生效年份逐国编码。