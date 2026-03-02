---
name: eastmoney-api
description: 东方财富网页API接入指南。无需注册，直接调用获取A股实时行情、历史K线、财务数据、资金流向等。
---

# 东方财富网页API接入指南

东方财富提供了丰富的网页API，无需注册即可使用。这些API被AKShare等库封装，也可以直接调用。

## 基础接口

### 1. 实时行情接口

**URL**: `http://push2.eastmoney.com/api/qt/stock/get`

**参数**:
- `secid`: 股票代码标识 `0.{code}`(深圳) 或 `1.{code}`(上海)
- `fields`: 需要返回的字段

**示例**:
```python
import urllib.request
import json

def get_realtime_quote(stock_code):
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
    else:
        secid = f"0.{stock_code}"
    
    url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170"
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

# 使用
quote = get_realtime_quote('000001')
print(f"{quote['name']}: ¥{quote['price']}, 涨跌幅: {quote['change_pct']}%")
```

**字段说明**:

| 字段 | 说明 | 单位 |
|------|------|------|
| f43 | 最新价 | 分 |
| f44 | 开盘价 | 分 |
| f45 | 最高价 | 分 |
| f46 | 最低价 | 分 |
| f47 | 成交量 | 手 |
| f48 | 成交额 | 元 |
| f57 | 股票代码 | - |
| f58 | 股票名称 | - |
| f60 | 昨收价 | 分 |
| f170 | 涨跌幅 | % |
| f169 | 涨跌额 | 分 |
| f50 | 量比 | - |
| f51 | 委比 | % |
| f52 | 换手率 | % |
| f191 | 市盈率(动) | - |
| f192 | 市盈率(静) | - |
| f193 | 市盈率(TTM) | - |
| f194 | 市净率 | - |
| f195 | 总市值 | 元 |
| f196 | 流通市值 | 元 |

---

### 2. 历史K线接口

**URL**: `http://push2.eastmoney.com/api/qt/stock/kline/get`

**参数**:
- `secid`: 股票代码标识
- `klt`: K线类型 101(日线), 102(周线), 103(月线)
- `lmt`: 获取条数
- `fields1`: 字段1
- `fields2`: 字段2

**示例**:
```python
def get_kline(stock_code, days=30):
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
    else:
        secid = f"0.{stock_code}"
    
    url = f"http://push2.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=0&end=20500101&lmt={days}"
    
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
            # 格式: 日期,开盘价,收盘价,最高价,最低价,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
            parts = line.split(',')
            result.append({
                'date': parts[0],
                'open': float(parts[1]),
                'close': float(parts[2]),
                'high': float(parts[3]),
                'low': float(parts[4]),
                'volume': int(parts[5]),
                'amount': float(parts[6]),
                'amplitude': float(parts[7]),
                'change_pct': float(parts[8]),
                'change': float(parts[9]),
                'turnover': float(parts[10]),
            })
    return result

# 使用
kline = get_kline('000001', days=5)
for k in kline:
    print(f"{k['date']}: 开{k['open']} 收{k['close']} 涨跌幅{k['change_pct']}%")
```

---

### 3. 板块资金流向接口

**URL**: `http://push2.eastmoney.com/api/qt/clist/get`

**示例**:
```python
def get_sector_flow():
    url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&fltt=2&invt=2&fid=f62&fs=m:90+t:2&fields=f12,f13,f14,f20,f21,f22,f62,f66,f69,f72,f75,f78,f81,f84,f87"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://quote.eastmoney.com/',
    }
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    
    result = []
    if data.get('data') and data['data'].get('diff'):
        for item in data['data']['diff'].values():
            result.append({
                'code': item.get('f12'),
                'name': item.get('f14'),
                'main_inflow': item.get('f62'),  # 主力净流入
                'change_pct': item.get('f3'),    # 涨跌幅
            })
    return result
```

---

### 4. 个股资金流向接口

**URL**: `http://push2.eastmoney.com/api/qt/stock/fflow/kline/get`

**示例**:
```python
def get_stock_flow(stock_code):
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
    else:
        secid = f"0.{stock_code}"
    
    url = f"http://push2.eastmoney.com/api/qt/stock/fflow/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://quote.eastmoney.com/',
    }
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    return data
```

---

### 5. 财务数据接口

**利润表**:
```python
def get_income(stock_code):
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
    else:
        secid = f"0.{stock_code}"
    
    url = f"http://f10.eastmoney.com/NewFinanceAnalysis/lrbAjax?companyType=4&reportDateType=0&code={stock_code}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://f10.eastmoney.com/',
    }
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    # 注意：返回数据可能有BOM头，需要处理
    content = response.read()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
    data = json.loads(content.decode('utf-8'))
    return data
```

---

## 完整示例代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富API完整示例
"""

import urllib.request
import json
import ssl

# 禁用SSL验证（如有需要）
ssl._create_default_https_context = ssl._create_unverified_context

class EastMoneyAPI:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://quote.eastmoney.com/',
        }
    
    def _get_secid(self, stock_code):
        """获取secid"""
        if stock_code.startswith('6'):
            return f"1.{stock_code}"
        return f"0.{stock_code}"
    
    def get_realtime(self, stock_code):
        """获取实时行情"""
        secid = self._get_secid(stock_code)
        url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170,f169,f50,f52,f191,f192,f193,f194,f195,f196"
        
        req = urllib.request.Request(url, headers=self.headers)
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
                'pe_ttm': d.get('f193'),
                'pb': d.get('f194'),
                'total_mv': d.get('f195'),
                'float_mv': d.get('f196'),
            }
        return None
    
    def get_kline(self, stock_code, days=30):
        """获取历史K线"""
        secid = self._get_secid(stock_code)
        url = f"http://push2.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=0&end=20500101&lmt={days}"
        
        req = urllib.request.Request(url, headers=self.headers)
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

# 使用示例
if __name__ == '__main__':
    api = EastMoneyAPI()
    
    # 获取实时行情
    quote = api.get_realtime('000001')
    print(f"{quote['name']}({quote['code']}): ¥{quote['price']}, PE_TTM: {quote['pe_ttm']}")
    
    # 获取K线
    kline = api.get_kline('000001', days=5)
    for k in kline:
        print(f"{k['date']}: 收{k['close']}, 涨跌幅{k['change_pct']}%")
```

---

## 注意事项

1. **Headers 必须设置**: `User-Agent` 和 `Referer` 必须设置，否则会被拒绝
2. **频率限制**: 不要过于频繁请求，建议间隔 1 秒以上
3. **HTTP 协议**: 使用 HTTP 而不是 HTTPS，避免 SSL 问题
4. **数据单位**: 价格字段通常是"分"，需要除以 100
5. **错误处理**: 建议添加 try-except 处理网络异常

---

## 与 AKShare 的关系

AKShare 就是封装了这些东方财富 API。如果 AKShare 有网络问题，可以直接使用这些 API。
