"""Unit tests for oil / sina helpers (no live network)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.fetchers.oil import parse_eastmoney_oil_rows, parse_qiyou_92
from app.fetchers.sina_util import fetch_sina_quotes


def test_parse_qiyou_92() -> None:
    html = """
    <div id="youjia">
      <dl><dt>北京92#汽油</dt><dd>7.18</dd></dl>
      <dl><dt>北京95#汽油</dt><dd>7.64</dd></dl>
    </div>
    """
    assert parse_qiyou_92(html) == Decimal("7.1800")
    assert parse_qiyou_92("<div>no price</div>") is None


def test_parse_eastmoney_oil_rows() -> None:
    rows = [
        {
            "DIM_DATE": "2026-07-04 00:00:00",
            "CITYNAME": "北京",
            "V92": 7.18,
            "ZDE92": -0.75,
        },
        {
            "DIM_DATE": "2026-07-04 00:00:00",
            "CITYNAME": "上海",
            "V92": 7.14,
            "ZDE92": -0.74,
        },
        {
            "DIM_DATE": "2026-06-19 00:00:00",
            "CITYNAME": "北京",
            "V92": 7.93,
            "ZDE92": 0.1,
        },
    ]
    records = parse_eastmoney_oil_rows(
        rows,
        {"北京": "oil_gasoline_92", "上海": "oil_gasoline_92_sh", "广东": "oil_gasoline_92_gd"},
    )
    assert len(records) == 2
    by_code = {r.item_code: r for r in records}
    assert by_code["oil_gasoline_92"].price == Decimal("7.1800")
    assert by_code["oil_gasoline_92"].record_date == date(2026, 7, 4)
    assert by_code["oil_gasoline_92"].change_pct == Decimal("-9.4578")
    assert by_code["oil_gasoline_92_sh"].price == Decimal("7.1400")


def test_fetch_sina_quotes_index_and_us() -> None:
    body = (
        'var hq_str_s_sh000001="上证指数,3969.7506,-1.1291,-0.03,1,1";\n'
        'var hq_str_gb_nvda="英伟达,204.1200,3.65,2026-07-09 09:49:42,7.1900";\n'
        'var hq_str_sh688981="中芯国际,153.680,152.100,164.890,166.580,152.100,'
        "164.890,164.900,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"
        '2026-07-09,13:31:47,00,";\n'
    ).encode("gbk")

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.content = body

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_client.get.return_value = mock_resp

    with patch("app.fetchers.sina_util.httpx.Client", return_value=mock_client):
        quotes = fetch_sina_quotes(["s_sh000001", "gb_nvda", "sh688981"])

    assert quotes["s_sh000001"].price == Decimal("3969.7506")
    assert quotes["s_sh000001"].change_pct == Decimal("-0.0300")
    assert quotes["gb_nvda"].price == Decimal("204.1200")
    assert quotes["gb_nvda"].change_pct == Decimal("3.6500")
    assert quotes["gb_nvda"].record_date == date(2026, 7, 9)
    assert quotes["sh688981"].price == Decimal("164.8900")
    assert quotes["sh688981"].change_pct == Decimal("8.4089")
