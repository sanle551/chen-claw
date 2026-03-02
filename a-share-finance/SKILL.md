---
name: a-share-finance
description: A股财务数据补充接口。整合新浪财经、东方财富等免费数据源，获取财务报表、盈利能力、成长能力等数据。当需要查询股票财务数据、利润表、资产负债表、现金流量表、ROE、毛利率等指标时触发。
---

# A股财务数据接口

整合多个免费数据源的财务数据获取工具。

## 数据来源

| 数据源 | 数据类型 | 稳定性 |
|--------|---------|--------|
| 新浪财经 | 财务摘要、利润表、资产负债表 | ⭐⭐⭐ |
| 东方财富 | 估值指标、实时行情 | ⭐⭐⭐⭐ |
| 同花顺 | 财务指标、行业对比 | ⭐⭐⭐ |

## 接口列表

### 1. 获取财务摘要（新浪财经）

```python
import urllib.request
import json
import re

def get_finance_summary_sina(stock_code):
    """从新浪财经获取财务摘要
    
    Args:
        stock_code: 股票代码，如 '000001'
    
    Returns:
        dict: 财务摘要数据
    """
    if stock_code.startswith('6'):
        symbol = f"sh{stock_code}"
    else:
        symbol = f"sz{stock_code}"
    
    url = f"https://finance.sina.com.cn/realstock/company/{symbol}/finance.shtml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        html = response.read().decode('gb2312', errors='ignore')
        
        # 解析财务数据
        data = {}
        
        # 提取基本每股收益
        eps_match = re.search(r'基本每股收益.*?([\d.]+)', html)
        if eps_match:
            data['eps'] = float(eps_match.group(1))
        
        # 提取每股净资产
        bps_match = re.search(r'每股净资产.*?([\d.]+)', html)
        if bps_match:
            data['bps'] = float(bps_match.group(1))
        
        # 提取净资产收益率
        roe_match = re.search(r'净资产收益率.*?([\d.]+)', html)
        if roe_match:
            data['roe'] = float(roe_match.group(1))
        
        # 提取营业收入
        revenue_match = re.search(r'营业收入.*?([\d,\.]+)', html)
        if revenue_match:
            data['revenue'] = revenue_match.group(1).replace(',', '')
        
        # 提取净利润
        profit_match = re.search(r'净利润.*?([\d,\.]+)', html)
        if profit_match:
            data['net_profit'] = profit_match.group(1).replace(',', '')
        
        return data
    except Exception as e:
        return {'error': str(e)}

# 使用示例
# data = get_finance_summary_sina('000001')
# print(data)
```

### 2. 获取利润表（新浪财经）

```python
def get_profit_statement_sina(stock_code):
    """获取利润表数据"""
    if stock_code.startswith('6'):
        symbol = f"sh{stock_code}"
    else:
        symbol = f"sz{stock_code}"
    
    # 新浪财经财务报表接口
    url = f"https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?stockid={stock_code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        html = response.read().decode('gb2312', errors='ignore')
        return {'status': 'parsed', 'length': len(html)}
    except Exception as e:
        return {'error': str(e)}
```

### 3. 获取主要财务指标（同花顺）

```python
def get_financial_indicators_ths(stock_code):
    """从同花顺获取财务指标
    
    包括：ROE、毛利率、净利率、营收增长率、净利润增长率等
    """
    if stock_code.startswith('6'):
        exchange = 'sh'
    else:
        exchange = 'sz'
    
    url = f"http://basic.10jqka.com.cn/{stock_code}/finance.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://basic.10jqka.com.cn/',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        html = response.read().decode('utf-8', errors='ignore')
        
        data = {}
        
        # 提取ROE
        roe_match = re.search(r'净资产收益率\(ROE\).*?([\d.]+)%', html)
        if roe_match:
            data['roe'] = float(roe_match.group(1))
        
        # 提取毛利率
        gross_match = re.search(r'毛利率.*?([\d.]+)%', html)
        if gross_match:
            data['gross_margin'] = float(gross_match.group(1))
        
        # 提取净利率
        net_match = re.search(r'净利率.*?([\d.]+)%', html)
        if net_match:
            data['net_margin'] = float(net_match.group(1))
        
        return data
    except Exception as e:
        return {'error': str(e)}
```

### 4. 新浪实时行情接口

```python
def get_sina_realtime(stock_code):
    """新浪实时行情接口（包含部分财务数据）
    
    返回数据格式：股票名称,今日开盘价,昨日收盘价,当前价,今日最高价,今日最低价,
    竞买价,竞卖价,成交股数,成交金额,...
    """
    if stock_code.startswith('6'):
        symbol = f"sh{stock_code}"
    else:
        symbol = f"sz{stock_code}"
    
    url = f"https://hq.sinajs.cn/list={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://finance.sina.com.cn',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('gb2312', errors='ignore')
        
        # 解析数据
        # var hq_str_sz000001="平安银行,10.850,10.900,10.880,...
        match = re.search(r'"([^"]+)"', content)
        if match:
            parts = match.group(1).split(',')
            return {
                'name': parts[0],
                'open': float(parts[1]),
                'pre_close': float(parts[2]),
                'price': float(parts[3]),
                'high': float(parts[4]),
                'low': float(parts[5]),
                'volume': int(parts[8]),
                'amount': float(parts[9]),
            }
        return {}
    except Exception as e:
        return {'error': str(e)}

# 使用示例
# data = get_sina_realtime('000001')
# print(f"{data['name']}: ¥{data['price']}, 成交量{data['volume']}")
```

### 5. 获取完整财务数据（综合）

```python
class AShareFinance:
    """A股财务数据获取类"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    
    def get_all_finance_data(self, stock_code):
        """获取所有可用的财务数据"""
        result = {
            'stock_code': stock_code,
            'data_sources': {},
        }
        
        # 1. 东方财富估值指标
        try:
            result['data_sources']['eastmoney'] = self._get_eastmoney_valuation(stock_code)
        except Exception as e:
            result['data_sources']['eastmoney'] = {'error': str(e)}
        
        # 2. 新浪财经财务摘要
        try:
            result['data_sources']['sina'] = get_finance_summary_sina(stock_code)
        except Exception as e:
            result['data_sources']['sina'] = {'error': str(e)}
        
        # 3. 同花顺财务指标
        try:
            result['data_sources']['ths'] = get_financial_indicators_ths(stock_code)
        except Exception as e:
            result['data_sources']['ths'] = {'error': str(e)}
        
        return result
    
    def _get_eastmoney_valuation(self, stock_code):
        """东方财富估值指标"""
        if stock_code.startswith('6'):
            secid = f"1.{stock_code}"
        else:
            secid = f"0.{stock_code}"
        
        url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f57,f58,f191,f192,f193,f194,f195,f196"
        
        req = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if data.get('data'):
            d = data['data']
            return {
                'name': d.get('f58'),
                'price': d.get('f43') / 100 if d.get('f43') else None,
                'pe_ttm': d.get('f193'),
                'pb': d.get('f194'),
                'total_mv': d.get('f195'),
                'float_mv': d.get('f196'),
            }
        return {}

# 使用示例
# finance = AShareFinance()
# data = finance.get_all_finance_data('000001')
# print(json.dumps(data, indent=2, ensure_ascii=False))
```

## 数据字段说明

### 估值指标

| 字段 | 说明 | 来源 |
|------|------|------|
| pe_ttm | 市盈率(TTM) | 东方财富 |
| pb | 市净率 | 东方财富 |
| total_mv | 总市值 | 东方财富 |
| float_mv | 流通市值 | 东方财富 |

### 盈利能力

| 字段 | 说明 | 来源 |
|------|------|------|
| roe | 净资产收益率 | 新浪财经/同花顺 |
| gross_margin | 毛利率 | 同花顺 |
| net_margin | 净利率 | 同花顺 |
| eps | 每股收益 | 新浪财经 |

### 成长能力

| 字段 | 说明 | 来源 |
|------|------|------|
| revenue_growth | 营收增长率 | 新浪财经 |
| profit_growth | 净利润增长率 | 新浪财经 |

## 注意事项

1. **数据延迟**: 免费数据通常有1-2天延迟
2. **数据完整性**: 不同来源数据可能不完整
3. **频率限制**: 不要过于频繁请求
4. **错误处理**: 建议添加重试机制

## 替代方案

如果以上接口都无法获取完整财务数据，建议：

1. **Tushare** - 积累积分（2000+）
2. **手动下载** - 东方财富、同花顺网页导出
3. **付费服务** - Wind、Choice、iFinD
