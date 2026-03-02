---
name: a-share-tushare
description: A股数据分析工具，基于Tushare Pro API。获取股票行情、财务数据、板块资金流向、技术指标等。当用户询问A股、股票代码、行情数据、财务报表、资金流向、技术指标、板块分析等话题时触发。
---

# A股数据分析 (Tushare版)

基于 Tushare Pro API 的 A 股数据分析工具。

## 前置要求

需要 Tushare Pro 账号和 Token：
1. 注册 https://tushare.pro/register
2. 获取 Token：https://tushare.pro/user/token
3. 设置环境变量：`export TUSHARE_TOKEN="your_token"`

## 功能模块

### 1. 股票基础数据

**获取股票列表**
```python
import tushare as ts
pro = ts.pro_api()

# 获取所有A股列表
df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
```

**获取日线行情**
```python
# 获取某股票日线数据
df = pro.daily(ts_code='000001.SZ', start_date='20260101', end_date='20260301')

# 获取实时行情（当日）
df = pro.daily(ts_code='000001.SZ')
```

### 2. 财务数据

**获取财务报表**
```python
# 利润表
df = pro.income(ts_code='000001.SZ', period='20241231')

# 资产负债表
df = pro.balancesheet(ts_code='000001.SZ', period='20241231')

# 现金流量表
df = pro.cashflow(ts_code='000001.SZ', period='20241231')

# 主要财务指标
df = pro.fina_indicator(ts_code='000001.SZ', period='20241231')
```

### 3. 板块资金流向

**行业板块资金流向**
```python
# 获取当日行业板块资金流向
df = pro.moneyflow_ind_ths(trade_date='20260302')

# 获取概念板块资金流向
df = pro.moneyflow_con_ths(trade_date='20260302')
```

**个股资金流向**
```python
# 获取个股资金流向
df = pro.moneyflow(ts_code='000001.SZ', start_date='20260101', end_date='20260301')
```

### 4. 技术指标

**获取每日指标**
```python
# 获取每日技术指标（包含换手率、量比、PE、PB等）
df = pro.daily_basic(ts_code='000001.SZ', trade_date='20260301')
```

### 5. 板块数据

**获取行业板块成分股**
```python
# 获取行业板块列表
df = pro.ths_industry()

# 获取概念板块列表
df = pro.ths_concept()

# 获取板块成分股
df = pro.ths_member(ts_code='885952.TI')
```

## 常用分析场景

### 场景1：查看某股票基本信息
```python
import tushare as ts
pro = ts.pro_api()

# 股票基础信息
df = pro.stock_basic(ts_code='000001.SZ')
print(df[['ts_code', 'name', 'industry', 'list_date']])

# 最新行情
df = pro.daily(ts_code='000001.SZ')
print(df[['trade_date', 'open', 'high', 'low', 'close', 'vol']].head())

# 技术指标
df = pro.daily_basic(ts_code='000001.SZ')
print(df[['trade_date', 'turnover_rate', 'pe', 'pb']].head())
```

### 场景2：热门板块资金流向
```python
# 获取行业板块资金流向（按主力净流入排序）
df = pro.moneyflow_ind_ths(trade_date='20260302')
df = df.sort_values('net_mf_amount', ascending=False)
print(df[['industry_name', 'change_pct', 'net_mf_amount']].head(10))
```

### 场景3：财务健康度检查
```python
# 获取主要财务指标
df = pro.fina_indicator(ts_code='000001.SZ', period='20241231')
print(df[['eps', 'roe', 'grossprofit_margin', 'netprofit_margin']])
```

## 数据说明

| 数据类型 | 接口 | 积分要求 |
|---------|------|---------|
| 股票基础信息 | stock_basic | 免费 |
| 日线行情 | daily | 免费 |
| 财务报表 | income/balancesheet/cashflow | 2000积分 |
| 资金流向 | moneyflow | 2000积分 |
| 板块数据 | ths_industry/ths_concept | 2000积分 |
| 技术指标 | daily_basic | 免费 |

## 与 sector skill 的对比

| 功能 | sector skill | tushare skill |
|------|-------------|---------------|
| 数据来源 | 东方财富(爬虫) | Tushare Pro(API) |
| 实时性 | 实时 | 延迟15分钟 |
| 稳定性 | 依赖页面结构 | API稳定 |
| 历史数据 | 有限 | 完整历史 |
| 财务数据 | 无 | 完整财报 |
| 积分要求 | 无 | 需要积分 |

## 建议用法

- **日常使用**: sector skill（实时、免费）
- **深度分析**: tushare skill（历史数据、财务数据）
- **量化研究**: tushare skill（完整API、稳定）

## 安装依赖

```bash
pip install tushare
```

## 配置Token

```bash
export TUSHARE_TOKEN="your_token_here"
```

或在 Python 中设置：
```python
import tushare as ts
ts.set_token('your_token_here')
pro = ts.pro_api()
```
