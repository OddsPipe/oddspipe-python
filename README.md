# OddsPipe Python SDK

Python client for the [OddsPipe](https://oddspipe.com) prediction market API.

## Install

```bash
pip install oddspipe
```

## Quick start

```python
from oddspipe import OddsPipe

client = OddsPipe(api_key="your-api-key")

# List top markets by volume
markets = client.markets(limit=10)
for m in markets["items"]:
    print(m["title"], m["spread"])

# Search for a market
results = client.search("Trump", platform="polymarket")

# Get OHLCV candlesticks
candles = client.candlesticks(market_id=123, interval="1h", limit=100)
for c in candles["candles"]:
    print(c["timestamp"], c["close"], c["volume"])

# Find cross-platform price divergences
spreads = client.spreads(min_spread=0.03)
for item in spreads["items"]:
    print(item["polymarket"]["title"], item["spread"]["yes_diff"])

# Most-traded matched pairs first (default sort="spread": largest divergence first)
liquid = client.spreads(sort="volume", min_score=95, limit=5)

# Cross-platform spread for a single market
spread = client.spread(market_id=123)
print(spread["sources"])
print(spread["spread"])
```

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `markets()` | `GET /v1/markets` | List markets with latest prices |
| `market(id)` | `GET /v1/markets/{id}` | Single market detail |
| `search(q)` | `GET /v1/markets/search` | Full-text search |
| `history(id)` | `GET /v1/markets/{id}/history` | Raw price snapshots |
| `candlesticks(id)` | `GET /v1/markets/{id}/candlesticks` | OHLCV candles (1m/5m/1h/1d) |
| `spread(id)` | `GET /v1/markets/{id}/spread` | Cross-platform spread |
| `spreads()` | `GET /v1/spreads` | Cross-platform price spreads |

## Error handling

```python
from oddspipe import OddsPipe, OddsPipeError

client = OddsPipe(api_key="your-key")
try:
    client.market(999999)
except OddsPipeError as e:
    print(e.status_code)  # 404
    print(e.body)         # {"detail": "Market not found"}
```
