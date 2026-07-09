"""Unit tests for FRED CSV parsing helpers (no network in pure parse tests)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.fetchers.fred_util import calc_change_pct, fetch_fred_latest


def test_calc_change_pct() -> None:
    assert calc_change_pct(Decimal("110"), Decimal("100")) == Decimal("10.0000")
    assert calc_change_pct(Decimal("100"), None) is None
    assert calc_change_pct(Decimal("100"), Decimal("0")) is None


def test_fetch_fred_latest_csv_fallback() -> None:
    csv_body = (
        "observation_date,DCOILWTICO\n"
        "2026-07-01,70.10\n"
        "2026-07-02,.\n"
        "2026-07-03,71.25\n"
    )
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.text = csv_body

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_client.get.return_value = mock_resp

    with (
        patch("app.fetchers.fred_util.settings") as settings,
        patch("app.fetchers.fred_util.httpx.Client", return_value=mock_client),
    ):
        settings.fred_api_key = ""
        result = fetch_fred_latest("DCOILWTICO")

    assert result == (date(2026, 7, 3), Decimal("71.2500"))


def test_seed_item_codes_unique() -> None:
    from app.seed_data import SEED_ITEMS

    codes = [item["code"] for item in SEED_ITEMS]
    assert len(codes) == len(set(codes))
    assert len(codes) >= 30
