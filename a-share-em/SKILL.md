---
name: a-share-em
description: 基于东方财富API的A股数据获取工具。无需安装额外库，直接使用urllib获取实时行情、历史数据、板块资金等。当AKShare/Tushare不可用时作为备用方案。
---

# A股数据工具 (东方财富API版)

基于东方财富网页API的A股数据获取工具，无需额外依赖，纯Python标准库实现。

## 特点

- ✅ 无需安装额外Python包
- ✅ 使用标准库 urllib
- ✅ 实时行情数据
- ✅ 历史K线数据
- ✅ 板块资金流向

## 使用方法

### 1. 获取实时行情

```python
import urllib.request
import json

def get_realtime_quote(stock_code):
    \"\"\"获取股票实时行情
    
    Args:
        stock_code: 股票代码，如 '600000' (浦发)、'000001' (平安银行)
    
    Returns:
        dict: 包含最新价格、涨跌、成交量等
    \"\"\"
    # 判断是上海还是深圳
    if stock_code.startswith('6'):
        secid = f\"1.{stock_code}\"  # 上海
    else:
        secid = f\"0.{stock_code}\"  # 深圳
    
    url = f\"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}\u0026fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170\"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://quote.eastmoney.com/',
    }
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    
    if data.get('data'):
        d = data['data']
        return {
            'code': d.get('f57'),
            'name': d.get('f58'),
            'price': d.get('f43') / 100 if d.get('f43') else None,
            'open': d.get('f44') / 100 if d.get('f44') else None,
            'high': d.get('f45') / 100 if d.get('f45') else None,
            'low': d.get('f46') / 100 if d.get('f46') else None,
            'volume': d.get('f47'),
            'amount': d.get('f48'),
            'pre_close': d.get('f60') / 100 if d.get('f60') else None,
            'change_pct': d.get('f170') / 100 if d.get('f170') else None,
        }
    return None

# 示例
quote = get_realtime_quote('000001')
print(f\"{quote['name']}({quote['code']}): ¥{quote['price']}, 涨跌幅: {quote['change_pct']}%\")
```

### 2. 获取历史K线数据

```python
def get_kline(stock_code, period='daily', days=30):
    \"\"\"获取历史K线数据\"\"\"
    if stock_code.startswith('6'):
        secid = f\"1.{stock_code}\"
    else:
        secid = f\"0.{stock_code}\"
    
    klt = {'daily': 101, 'weekly': 102, 'monthly': 103}.get(period, 101)
    
    url = f\"http://push2.eastmoney.com/api/qt/stock/kline/get?secid={secid}\u0026klt={klt}\u0026lmt={days}\"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://quote.eastmoney.com/',
    }
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    
    result = []
    if data.get('data') and data['data'].get('klines'):
        for line in data['data']['klines']:
            parts = line.split(',')
            result.append({
                'date': parts[0],
                'open': float(parts[1]),
                'close': float(parts[2]),
                'high': float(parts[3]),
                'low': float(parts[4]),
                'volume': int(parts[5]),
                'amount': float(parts[6]),
                'change_pct': float(parts[8]),
            })
    return result
```

## 字段说明

| 字段 | 说明 | 单位 |
|------|------|------|
| f43 | 最新价 | 分（需除以100） |
| f44 | 开盘价 | 分 |
| f45 | 最高价 | 分 |
| f46 | 最低价 | 分 |
| f47 | 成交量 | 手 |
| f48 | 成交额 | 元 |
| f57 | 股票代码 | - |
| f58 | 股票名称 | - |
| f60 | 昨收价 | 分 |
| f170 | 涨跌幅 | % |
| f62 | 主力净流入 | 万元 |
