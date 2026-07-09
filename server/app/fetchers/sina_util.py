"""Parse Sina finance HQ quotes (no API key required)."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import httpx

logger = logging.getLogger(__name__)

_HQ_RE = re.compile(r'hq_str_([^=]+)="([^"]*)"')


@dataclass(frozen=True)
class SinaQuote:
    symbol: str
    name: str
    price: Decimal
    change_pct: Decimal | None
    record_date: date


def fetch_sina_quotes(symbols: list[str]) -> dict[str, SinaQuote]:
    """Fetch multiple Sina HQ symbols; keys are the request symbols."""
    if not symbols:
        return {}
    url = "https://hq.sinajs.cn/list=" + ",".join(symbols)
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://finance.sina.com.cn",
                },
            )
            resp.raise_for_status()
            # Sina often returns GBK
            text = resp.content.decode("gbk", errors="ignore")
    except Exception as exc:
        logger.warning("Sina HQ fetch failed: %s", exc)
        return {}

    results: dict[str, SinaQuote] = {}
    for match in _HQ_RE.finditer(text):
        symbol = match.group(1)
        payload = match.group(2).strip()
        if not payload:
            continue
        quote = _parse_payload(symbol, payload)
        if quote is not None:
            results[symbol] = quote
    return results


def _parse_payload(symbol: str, payload: str) -> SinaQuote | None:
    fields = payload.split(",")
    try:
        if symbol.startswith("s_"):
            # 名称,现价,涨跌额,涨跌幅,...
            name = fields[0]
            price = _dec(fields[1])
            change_pct = _dec(fields[3]) if len(fields) > 3 else None
            return SinaQuote(symbol, name, price, change_pct, date.today())
        if symbol.startswith("gb_"):
            # 名称,现价,涨跌幅(%),时间,涨跌额,...
            name = fields[0]
            price = _dec(fields[1])
            change_pct = _dec(fields[2]) if len(fields) > 2 else None
            record_date = _parse_gb_date(fields[3] if len(fields) > 3 else "")
            return SinaQuote(symbol, name, price, change_pct, record_date)
        # A-share full quote: 名称,今开,昨收,现价,...
        name = fields[0]
        price = _dec(fields[3])
        prev = _dec(fields[2]) if len(fields) > 2 else None
        change_pct = None
        if prev and prev != 0:
            change_pct = ((price - prev) / prev * 100).quantize(Decimal("0.0001"))
        record_date = date.today()
        if len(fields) > 30:
            try:
                record_date = date.fromisoformat(fields[30][:10])
            except ValueError:
                pass
        return SinaQuote(symbol, name, price, change_pct, record_date)
    except (InvalidOperation, IndexError, ValueError) as exc:
        logger.warning("Failed to parse Sina quote %s: %s", symbol, exc)
        return None


def _dec(raw: str) -> Decimal:
    return Decimal(str(raw).strip()).quantize(Decimal("0.0001"))


def _parse_gb_date(raw: str) -> date:
    text = (raw or "").strip()
    if not text:
        return date.today()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:19], fmt).date()
        except ValueError:
            continue
    return date.today()
