"""Shared helpers for FRED series (API key or public CSV fallback)."""

from __future__ import annotations

import csv
import io
import logging
from datetime import date
from decimal import Decimal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def fetch_fred_latest(series_id: str) -> tuple[date, Decimal] | None:
    """Return (record_date, price) for the latest non-null observation."""
    if settings.fred_api_key:
        result = _via_fredapi(series_id)
        if result is not None:
            return result
        logger.info("FRED API failed for %s, trying CSV fallback", series_id)
    return _via_csv(series_id)


def fetch_fred_series_tail(series_id: str, limit: int = 5) -> list[tuple[date, Decimal]]:
    """Return up to `limit` latest non-null points, oldest first."""
    points = _csv_points(series_id)
    if not points and settings.fred_api_key:
        points = _fredapi_points(series_id)
    return points[-limit:]


def _via_fredapi(series_id: str) -> tuple[date, Decimal] | None:
    try:
        from fredapi import Fred

        fred = Fred(api_key=settings.fred_api_key)
        series = fred.get_series(series_id)
        if series is None or series.empty:
            return None
        clean = series.dropna()
        if clean.empty:
            return None
        latest_val = clean.iloc[-1]
        record_date = clean.index[-1].date()
        return record_date, Decimal(str(latest_val)).quantize(Decimal("0.0001"))
    except Exception as exc:
        logger.warning("fredapi fetch failed for %s: %s", series_id, exc)
        return None


def _via_csv(series_id: str) -> tuple[date, Decimal] | None:
    points = _csv_points(series_id)
    return points[-1] if points else None


def _csv_points(series_id: str) -> list[tuple[date, Decimal]]:
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        with httpx.Client(timeout=45, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
        reader = csv.DictReader(io.StringIO(resp.text))
        points: list[tuple[date, Decimal]] = []
        for row in reader:
            raw = (row.get(series_id) or row.get("VALUE") or "").strip()
            if not raw or raw == ".":
                continue
            date_raw = (
                row.get("observation_date")
                or row.get("DATE")
                or row.get("date")
                or ""
            ).strip()
            if not date_raw:
                continue
            day = date.fromisoformat(date_raw[:10])
            points.append((day, Decimal(raw).quantize(Decimal("0.0001"))))
        return points
    except Exception as exc:
        logger.warning("FRED CSV fetch failed for %s: %s", series_id, exc)
        return []


def _fredapi_points(series_id: str) -> list[tuple[date, Decimal]]:
    try:
        from fredapi import Fred

        fred = Fred(api_key=settings.fred_api_key)
        series = fred.get_series(series_id).dropna()
        return [
            (idx.date(), Decimal(str(val)).quantize(Decimal("0.0001")))
            for idx, val in series.items()
        ]
    except Exception as exc:
        logger.warning("fredapi points failed for %s: %s", series_id, exc)
        return []


def calc_change_pct(current: Decimal, previous: Decimal | None) -> Decimal | None:
    if previous is None or not previous:
        return None
    return ((current - previous) / previous * 100).quantize(Decimal("0.0001"))
