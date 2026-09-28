import httpx
import pytest

from oddspipe import OddsPipe, OddsPipeError

RETIRED_DETAIL = "Price history has been retired."


def _client(status_code: int, body: dict) -> tuple[OddsPipe, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(status_code, json=body)

    client = OddsPipe(api_key="test-key")
    client._client = httpx.Client(
        base_url="https://oddspipe.test/v1",
        headers={"X-API-Key": "test-key"},
        transport=httpx.MockTransport(handler),
    )
    return client, seen


@pytest.mark.parametrize(
    "method, path",
    [("history", "/v1/markets/123/history"), ("candlesticks", "/v1/markets/123/candlesticks")],
)
def test_retired_methods_warn_and_raise_410(method, path):
    client, seen = _client(410, {"detail": RETIRED_DETAIL})

    with pytest.warns(DeprecationWarning, match=r"retired on 2026-09-27") as record:
        with pytest.raises(OddsPipeError) as exc:
            getattr(client, method)(123)

    assert exc.value.status_code == 410
    assert exc.value.body == {"detail": RETIRED_DETAIL}
    assert seen[0].url.path == path

    message = str(record[0].message)
    assert "410" in message
    for alternative in ("market()", "spread()", "spreads()"):
        assert alternative in message
    # stacklevel points the warning at the caller, not at the SDK.
    assert record[0].filename == __file__


def test_live_methods_do_not_warn(recwarn):
    client, _ = _client(200, {"id": 123})

    assert client.market(123) == {"id": 123}
    assert not [w for w in recwarn if issubclass(w.category, DeprecationWarning)]
