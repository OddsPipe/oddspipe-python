"""Synchronous Python client for the OddsPipe prediction market API."""

from __future__ import annotations

import warnings

import httpx

_HISTORY_RETIRED = (
    "OddsPipe.{name}() is deprecated: price history was retired on 2026-09-27 and "
    "the API now returns HTTP 410 Gone for {path}. Use market() for a market's "
    "latest price, or spread() / spreads() for cross-platform comparisons."
)


def _warn_history_retired(name: str, path: str) -> None:
    warnings.warn(
        _HISTORY_RETIRED.format(name=name, path=path),
        DeprecationWarning,
        stacklevel=3,
    )


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

    def market(self, market_id: int, source_id: int | None = None) -> dict:
        """Get a single market with its primary source (or ``source_id``) and all source ids."""
        return self._request("GET", f"/markets/{market_id}", self._clean({
            "source_id": source_id,
        }))

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
        source_id: int | None = None,
    ) -> dict:
        """Deprecated: price history was retired on 2026-09-27.

        The API returns 410 Gone, raised as ``OddsPipeError``. Use ``market()``
        for the latest price, or ``spread()`` / ``spreads()``.
        """
        _warn_history_retired("history", "/v1/markets/{id}/history")
        return self._request("GET", f"/markets/{market_id}/history", self._clean({
            "source": source,
            "source_id": source_id,
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
        source_id: int | None = None,
    ) -> dict:
        """Deprecated: price history was retired on 2026-09-27.

        The API returns 410 Gone, raised as ``OddsPipeError``. Use ``market()``
        for the latest price, or ``spread()`` / ``spreads()``.
        """
        _warn_history_retired("candlesticks", "/v1/markets/{id}/candlesticks")
        return self._request("GET", f"/markets/{market_id}/candlesticks", self._clean({
            "interval": interval,
            "source": source,
            "source_id": source_id,
            "start": start,
            "end": end,
            "limit": limit,
        }))

    def spread(self, market_id: int, source_id: int | None = None) -> dict:
        """Get cross-platform spread for a single market (409 -> pass ``source_id``)."""
        return self._request("GET", f"/markets/{market_id}/spread", self._clean({
            "source_id": source_id,
        }))

    def spreads(
        self,
        limit: int = 50,
        offset: int = 0,
        min_spread: float | None = None,
        min_score: float | None = None,
        top_n: int | None = None,
        sort: str | None = None,
    ) -> dict:
        """List all markets with cross-platform spreads.

        sort: "spread" (server default, largest spread first) or "volume"
        (most-traded pairs first).
        """
        return self._request("GET", "/spreads", self._clean({
            "limit": limit,
            "offset": offset,
            "min_spread": min_spread,
            "min_score": min_score,
            "top_n": top_n,
            "sort": sort,
        }))

    def close(self):
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
