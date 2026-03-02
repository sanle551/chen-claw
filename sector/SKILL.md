---
name: sector
description: A股板块分析工具。查看国内A股行业板块和概念板块的实时行情，获取热门板块推荐。
---

# A股板块分析

查看国内A股行业板块和概念板块的实时行情，获取热门板块推荐。

## Usage

```bash
# 查看板块列表
/sector list --type industry               # 行业板块
/sector list --type concept --limit 10     # 概念板块

# 查看热门板块
/sector hot --limit 5                      # 涨跌幅前5的板块
/sector hot --sort amount --limit 10       # 成交额前10的板块

# 查看板块内个股
/sector stocks --name 光伏设备 --limit 15   # 光伏设备板块个股

# 查看资金流向
/sector flow --type industry --limit 10    # 行业板块资金流向

# 查看技术指标
/sector tech --name 光伏设备               # 板块技术指标分析
```

## Commands

### list - 获取板块列表

获取行业板块或概念板块的实时行情列表。

```bash
sector list [--type industry|concept] [--limit 20]
```

**参数:**
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--type, -t` | `industry` | 板块类型: `industry`(行业), `concept`(概念) |
| `--limit, -l` | `20` | 返回数量限制 |

**输出示例:**
```json
{
  "type": "industry",
  "count": 5,
  "sectors": [
    {
      "code": "BK0420",
      "name": "电力设备",
      "price": 1234.56,
      "change": 12.34,
      "change_rate": 2.15,
      "volume": 123456789,
      "amount": 45.67,
      "leader_stock": "宁德时代",
      "leader_rate": 5.23,
      "rise_count": 45,
      "fall_count": 12,
      "timestamp": "2026-01-25 10:30:00"
    }
  ],
  "timestamp": "2026-01-25 10:30:00",
  "summary": "行业板块共5个，上涨3个，下跌2个，平盘0个。涨幅最大: 电力设备(2.15%)"
}
```

---

### hot - 获取热门板块

获取热门板块，支持按涨跌幅或成交额排序。

```bash
sector hot [--sort change|amount] [--limit 10]
```

**参数:**
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--sort, -s` | `change` | 排序方式: `change`(涨跌幅), `amount`(成交额) |
| `--limit, -l` | `10` | 返回数量限制 |

---

### stocks - 获取板块内个股

获取指定板块内的个股列表，按涨跌幅排序。

```bash
sector stocks --name <板块名称> [--limit 20]
```

**参数:**
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--name, -n` | 必填 | 板块名称，如: 光伏设备、新能源汽车 |
| `--limit, -l` | `20` | 返回数量限制 |

---

### flow - 获取资金流向

获取行业或概念板块的资金流向数据，包含主力/散户资金净流入。

```bash
sector flow [--type industry|concept] [--limit 20]
```

---

### tech - 获取技术指标

获取指定板块的技术指标分析(MA/RSI/MACD等)。

```bash
sector tech --name <板块名称>
```

## Data Source

数据来源: 东方财富行情中心
- 行业板块: https://quote.eastmoney.com/center/boardlist.html#industry_board
- 概念板块: https://quote.eastmoney.com/center/boardlist.html#concept_board
- 资金流向: https://data.eastmoney.com/bkzj/hy.html

## Notes

- 数据为实时行情，交易时段内会持续更新
- 使用 Playwright 抓取，首次运行可能需要较长时间
- 非交易时段数据为上一交易日收盘数据
