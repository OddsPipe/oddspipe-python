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

# Latest price for a single market
market = client.market(market_id=123)

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
| `spread(id)` | `GET /v1/markets/{id}/spread` | Cross-platform spread |
| `spreads()` | `GET /v1/spreads` | Cross-platform price spreads |

## Price history retired

Price history was retired on 2026-09-27. `GET /v1/markets/{id}/history` and
`GET /v1/markets/{id}/candlesticks` now return **410 Gone**. `history()` and
`candlesticks()` still exist so old code fails clearly: they emit a
`DeprecationWarning` and raise `OddsPipeError` with `status_code == 410`. They
will be removed in a future release. Use `market()` for a market's latest
price, and `spread()` / `spreads()` for cross-platform comparisons.

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

A few older markets hold more than one contract on the same venue. For those,
`spread()` raises `OddsPipeError` with status
409 instead of mixing contracts; pick one with `source_id=`:

```python
try:
    spread = client.spread(market_id=123)
except OddsPipeError as e:
    if e.status_code != 409:
        raise
    first = e.body["detail"]["sources"][0]["source_id"]
    spread = client.spread(market_id=123, source_id=first)
```
