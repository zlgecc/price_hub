import logging
import re
from datetime import date
from decimal import Decimal, InvalidOperation

import httpx

from app.config import settings
from app.fetchers.base import BaseFetcher
from app.fetchers.fred_util import calc_change_pct, fetch_fred_series_tail
from app.schemas.price import PriceRecordCreate
from app.seed_data import FRED_SERIES, OIL_QIYOU_PAGES, OIL_REGION_MAP

logger = logging.getLogger(__name__)

ENERGY_FRED_ITEMS = ("oil_wti", "oil_brent", "gas_henry_hub")
_QIYOU_92_RE = re.compile(r"<dt>[^<]*92#汽油</dt>\s*<dd>([0-9]+(?:\.[0-9]+)?)</dd>")
_EASTMONEY_OIL_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"


class OilFetcher(BaseFetcher):
    def source_name(self) -> str:
        return "oil"

    def fetch(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        records.extend(self._fetch_fred_energy())
        records.extend(self._fetch_national_guidance())
        records.extend(self._fetch_domestic())
        return records

    def _fetch_fred_energy(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        for item_code in ENERGY_FRED_ITEMS:
            series_id = FRED_SERIES[item_code]
            try:
                points = fetch_fred_series_tail(series_id, limit=2)
                if not points:
                    logger.info("No FRED data for %s (%s)", item_code, series_id)
                    continue
                record_date, price = points[-1]
                prev = points[-2][1] if len(points) >= 2 else None
                records.append(
                    PriceRecordCreate(
                        item_code=item_code,
                        record_date=record_date,
                        price=price,
                        change_pct=calc_change_pct(price, prev),
                    )
                )
            except Exception as exc:
                logger.warning("Energy FRED fetch failed for %s: %s", item_code, exc)
        return records

    def _fetch_national_guidance(self) -> list[PriceRecordCreate]:
        """National gasoline/diesel guidance prices — no API key required."""
        try:
            import akshare as ak

            df = ak.energy_oil_hist()
            if df is None or df.empty:
                return []
            latest = df.iloc[-1]
            record_date = _parse_date(latest["调整日期"])
            records: list[PriceRecordCreate] = []

            gas = Decimal(str(latest["汽油价格"])).quantize(Decimal("0.0001"))
            diesel = Decimal(str(latest["柴油价格"])).quantize(Decimal("0.0001"))
            gas_chg = _optional_decimal(latest.get("汽油涨跌"), gas)
            diesel_chg = _optional_decimal(latest.get("柴油涨跌"), diesel)

            records.append(
                PriceRecordCreate(
                    item_code="oil_gasoline_national",
                    record_date=record_date,
                    price=gas,
                    change_pct=gas_chg,
                )
            )
            records.append(
                PriceRecordCreate(
                    item_code="oil_diesel_national",
                    record_date=record_date,
                    price=diesel,
                    change_pct=diesel_chg,
                )
            )
            return records
        except Exception as exc:
            logger.warning("National oil guidance fetch failed: %s", exc)
            return []

    def _fetch_domestic(self) -> list[PriceRecordCreate]:
        if settings.tianapi_key:
            records = self._fetch_tianapi()
            if records:
                return records
            logger.info("TianAPI returned no oil rows, falling back to public sources")
        else:
            logger.info("TIANAPI_KEY not set, using public provincial oil fallbacks")

        records = self._fetch_eastmoney()
        if records:
            return records
        logger.info("Eastmoney oil empty, trying QiYouJiaGe")
        return self._fetch_qiyoujiage()

    def _fetch_tianapi(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        today = date.today()
        with httpx.Client(timeout=30) as client:
            for region, item_code in OIL_REGION_MAP.items():
                try:
                    resp = client.get(
                        "https://apis.tianapi.com/oilprice/index",
                        params={"key": settings.tianapi_key, "prov": region},
                    )
                    resp.raise_for_status()
                    payload = resp.json()
                    if payload.get("code") != 200:
                        logger.warning("TianAPI error for %s: %s", region, payload.get("msg"))
                        continue
                    result = payload.get("result") or {}
                    price_val = result.get("p92")
                    if price_val is None:
                        continue
                    records.append(
                        PriceRecordCreate(
                            item_code=item_code,
                            record_date=today,
                            price=Decimal(str(price_val)),
                            change_pct=None,
                        )
                    )
                except Exception as exc:
                    logger.warning("Domestic oil fetch failed for %s: %s", region, exc)
        return records

    def _fetch_eastmoney(self) -> list[PriceRecordCreate]:
        """Provincial 92# pump prices via Eastmoney open datacenter (no key)."""
        try:
            with httpx.Client(timeout=30, follow_redirects=True) as client:
                resp = client.get(
                    _EASTMONEY_OIL_URL,
                    params={
                        "reportName": "RPTA_WEB_YJ_JH",
                        "columns": "ALL",
                        "pageNumber": 1,
                        "pageSize": 50,
                        "sortColumns": "DIM_DATE",
                        "sortTypes": -1,
                    },
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                resp.raise_for_status()
                rows = ((resp.json() or {}).get("result") or {}).get("data") or []
            return parse_eastmoney_oil_rows(rows, OIL_REGION_MAP)
        except Exception as exc:
            logger.warning("Eastmoney provincial oil fetch failed: %s", exc)
            return []

    def _fetch_qiyoujiage(self) -> list[PriceRecordCreate]:
        """Public provincial pump prices from qiyoujiage.com (no API key)."""
        records: list[PriceRecordCreate] = []
        today = date.today()
        headers = {"User-Agent": "Mozilla/5.0"}
        with httpx.Client(timeout=20, follow_redirects=True, headers=headers) as client:
            for item_code, slug in OIL_QIYOU_PAGES.items():
                try:
                    resp = client.get(f"http://www.qiyoujiage.com/{slug}.shtml")
                    resp.raise_for_status()
                    price = parse_qiyou_92(resp.text)
                    if price is None:
                        logger.warning("QiYouJiaGe missing 92# price for %s", slug)
                        continue
                    records.append(
                        PriceRecordCreate(
                            item_code=item_code,
                            record_date=today,
                            price=price,
                            change_pct=None,
                        )
                    )
                except Exception as exc:
                    logger.warning("QiYouJiaGe fetch failed for %s: %s", slug, exc)
        return records


def parse_eastmoney_oil_rows(
    rows: list[dict],
    region_map: dict[str, str],
) -> list[PriceRecordCreate]:
    if not rows:
        return []
    latest_date = max(str(row.get("DIM_DATE", ""))[:10] for row in rows if row.get("DIM_DATE"))
    if not latest_date:
        return []
    by_city = {
        str(row.get("CITYNAME", "")).strip(): row
        for row in rows
        if str(row.get("DIM_DATE", ""))[:10] == latest_date
    }
    record_date = date.fromisoformat(latest_date)
    records: list[PriceRecordCreate] = []
    for region, item_code in region_map.items():
        row = by_city.get(region)
        if not row or row.get("V92") is None:
            continue
        try:
            price = Decimal(str(row["V92"])).quantize(Decimal("0.0001"))
        except (InvalidOperation, ValueError):
            continue
        change_pct = None
        try:
            zde = row.get("ZDE92")
            if zde is not None and price:
                prev = price - Decimal(str(zde))
                if prev:
                    change_pct = (Decimal(str(zde)) / prev * 100).quantize(Decimal("0.0001"))
        except (InvalidOperation, ValueError, TypeError):
            change_pct = None
        records.append(
            PriceRecordCreate(
                item_code=item_code,
                record_date=record_date,
                price=price,
                change_pct=change_pct,
            )
        )
    return records


def parse_qiyou_92(html: str) -> Decimal | None:
    match = _QIYOU_92_RE.search(html)
    if not match:
        return None
    return Decimal(match.group(1)).quantize(Decimal("0.0001"))


def _parse_date(value) -> date:
    if hasattr(value, "date"):
        return value.date()
    return date.fromisoformat(str(value)[:10])


def _optional_decimal(raw, base: Decimal) -> Decimal | None:
    if raw is None:
        return None
    try:
        import math

        if isinstance(raw, float) and math.isnan(raw):
            return None
        delta = Decimal(str(raw))
        if not base:
            return None
        # 涨跌列为绝对价差（元/吨），换算为百分比
        return (delta / base * 100).quantize(Decimal("0.0001"))
    except Exception:
        return None
