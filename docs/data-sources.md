# 数据源文档

## 贵金属

| 品种 | 数据源 | 说明 |
|------|--------|------|
| 上海金 Au99.99 | AKShare → SGE | 国内现货金价，元/克 |
| 上海银 Ag99.99 | AKShare → SGE | 国内现货银价，元/千克 |
| 上海铂 Pt99.95 | AKShare → SGE | 国内现货铂价，元/克 |
| 国际金价 | FreeGoldAPI | 美元/盎司，无需 API Key |

## 能源

| 品种 | 数据源 | 说明 |
|------|--------|------|
| WTI 原油 | FRED (`DCOILWTICO`) | 美元/桶；无 Key 时走公开 CSV |
| Brent 原油 | FRED (`DCOILBRENTEU`) | 美元/桶；无 Key 时走公开 CSV |
| Henry Hub 天然气 | FRED (`DHHNGSP`) | 美元/百万英热 |
| 国内汽油/柴油指导价 | AKShare `energy_oil_hist` | 元/吨，无需 API Key |
| 92#汽油（各省） | TianAPI / 东方财富 / QiYouJiaGe | 有 Key 优先 TianAPI；否则东方财富公开接口，再降级 HTML |

## 生活必需品

| 品种 | 数据源 | 说明 |
|------|--------|------|
| 菜篮子批发价格指数 | AKShare | 日度指数 |
| 农产品批发价格总指数 | AKShare | 日度指数 |
| 猪肉（生猪成交均价） | AKShare `index_hog_spot_price` | 元/公斤 |
| 鸡蛋/白糖/豆油/棕榈油/菜籽油/豆粕/玉米 | AKShare `futures_spot_price_daily` | 国内期货对应现货价 |

## 大宗商品

| 品种 | 数据源 | 说明 |
|------|--------|------|
| 铜/铝/小麦/玉米/大豆/棕榈油（国际） | FRED | 美元/吨，月度；无 Key 走 CSV |
| 铜/铝/锌/螺纹钢/铁矿石/棉花（国内） | AKShare 现货 | 元/吨 |

## 汇率

| 品种 | 数据源 | 说明 |
|------|--------|------|
| 美元/欧元/日元/港元/英镑兑人民币 | AKShare `currency_boc_safe` | 中行中间价口径，人民币/100外币 |

## 股票指数

| 品种 | 数据源 | 说明 |
|------|--------|------|
| 上证/深成/创业板/沪深300/上证50/科创50 | 新浪财经 HQ | 无需 API Key |
| 标普500 / 纳斯达克100 / 道琼斯 | FRED | 无 Key 走公开 CSV |

## 科技芯片

| 品种 | 数据源 | 说明 |
|------|--------|------|
| 科创芯片指数 | 新浪财经 HQ | 半导体相关指数 |
| SOXX 半导体 ETF | 新浪美股 | DRAM/芯片板块代理指标 |
| 中芯国际 / 北方华创 / 海康威视 | 新浪 A 股 | 国内芯片/设备/科技代表 |
| NVDA / AAPL / AMD / MU / TSM / INTC | 新浪美股 | 芯片/内存/代工代表股；MU 作 DRAM 代理 |
| 美国半导体 PPI / 工业生产指数 | FRED | 月度宏观指标，无现货 DRAM/NAND 公开价时的兜底 |

## API Key 申请

| 服务 | 注册地址 | 用途 |
|------|----------|------|
| FRED | https://fred.stlouisfed.org/docs/api/api_key.html | 国际能源/大宗/美股指数（可选，有公开 CSV 兜底） |
| TianAPI | https://www.tianapi.com/ | 国内各省油价（可选，无 Key 走 QiYouJiaGe） |

## 降级策略

- 无 `FRED_API_KEY`：通过 FRED 公开 CSV 抓取 WTI/Brent/天然气、国际大宗与美股指数
- 无 `TIANAPI_KEY`：各省 92# 汽油走东方财富公开接口（QiYouJiaGe 作次级兜底）；全国汽柴油指导价仍可用
- 新浪 HQ / AKShare 接口失败：记录日志，不影响其他抓取器
- 单个抓取器异常：FetcherManager 继续执行下一个
- Dashboard 样本优先展示已有最新价的品种，避免空价占位

## 维护注意

- AKShare 接口可能随数据源改版失效，需关注 [AKShare Issues](https://github.com/akfamily/akshare/issues)
- `futures_spot_price_daily` 返回的是期货品种代码（如 `Y`/`JD`），不是中文品名
- TianAPI 免费额度有限；QiYouJiaGe 为 HTML 抓取，站点改版时需更新解析
- DRAM/NAND 现货价缺少稳定免费源，当前用 MU/SOXX/半导体 PPI 等公开代理指标
- 旧种子项 `rice_late_indica` / `peanut_oil` 已分别切换为玉米/豆油现货（保留 code 兼容）
- 本地开发若 8000 被占用，后端建议使用 `8001`，前端 Vite 代理已指向该端口
