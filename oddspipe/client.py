"""Synchronous Python client for the OddsPipe prediction market API."""

from __future__ import annotations

import httpx


class OddsPipeError(Exception):
    """Raised when the API returns a non-200 response."""

    def __init__(self, status_code: int, body: dict | str):
        self.status_code = status_code
        self.body = body
        detail = body.get("detail", body) if isinstance(body, dict) else body
        super().__init__(f"HTTP {status_code}: {detail}")


class OddsPipe:
    """Synchronous client for the OddsPipe API.

    Usage::

        client = OddsPipe(api_key="your-key")
        markets = client.markets(limit=10)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://oddspipe.com",
        timeout: float = 30.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=f"{self._base_url}/v1",
            headers={"X-API-Key": api_key},
            timeout=timeout,
        )

    def _request(self, method: str, path: str, params: dict | None = None) -> dict:
        resp = self._client.request(method, path, params=params)
        if resp.status_code != 200:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise OddsPipeError(resp.status_code, body)
        return resp.json()

    def _clean(self, params: dict) -> dict:
        return {k: v for k, v in params.items() if v is not None}

    # ----- endpoints -----

    def markets(
        self,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
    ) -> dict:
        """List markets with sources and latest prices.

        status: one of 'active', 'paused', 'closed', 'resolved'
        ('paused' is Kalshi-only). Defaults to 'active' server-side.
        """
        return self._request("GET", "/markets", self._clean({
            "limit": limit,
            "offset": offset,
            "search": search,
            "status": status,
        }))

    def market(self, market_id: int) -> dict:
        """Get a single market with all sources and latest snapshot per source."""
        return self._request("GET", f"/markets/{market_id}")

    def search(
        self,
        q: str,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """Full-text search across market titles.

        status: one of 'active', 'paused', 'closed', 'resolved'
        ('paused' is Kalshi-only).
        """
        return self._request("GET", "/markets/search", self._clean({
            "q": q,
            "platform": platform,
            "status": status,
            "limit": limit,
            "offset": offset,
        }))

    def history(
        self,
        market_id: int,
        source: str | None = None,
        since: str | None = None,
    ) -> dict:
        """Get all price snapshots for a market."""
        return self._request("GET", f"/markets/{market_id}/history", self._clean({
            "source": source,
            "since": since,
        }))

    def candlesticks(
        self,
        market_id: int,
        interval: str = "1h",
        source: str | None = None,
        start: str | None = None,
        end: str | None = None,
        limit: int = 500,
    ) -> dict:
        """Get OHLCV candlestick data for a market."""
        return self._request("GET", f"/markets/{market_id}/candlesticks", self._clean({
            "interval": interval,
            "source": source,
            "start": start,
            "end": end,
            "limit": limit,
        }))

    def spread(self, market_id: int) -> dict:
        """Get cross-platform spread for a single market."""
        return self._request("GET", f"/markets/{market_id}/spread")

    def spreads(
        self,
        limit: int = 50,
        offset: int = 0,
        min_spread: float | None = None,
        min_score: float | None = None,
        top_n: int | None = None,
    ) -> dict:
        """List all markets with cross-platform spreads, sorted by largest spread."""
        return self._request("GET", "/spreads", self._clean({
            "limit": limit,
            "offset": offset,
            "min_spread": min_spread,
            "min_score": min_score,
            "top_n": top_n,
        }))

    def close(self):
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
