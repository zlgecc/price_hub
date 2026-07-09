"""Probe external price data sources for availability."""
from __future__ import annotations

import traceback
from datetime import date, timedelta


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    section("FreeGoldAPI")
    try:
        import httpx

        r = httpx.get("https://freegoldapi.com/data/latest.json", timeout=30)
        print("status", r.status_code)
        if r.is_success:
            data = r.json()
            print("len", len(data), "latest", data[-1] if data else None)
        else:
            print(r.text[:200])
    except Exception as exc:
        print("FAIL", exc)

    section("SGE Au99.99")
    try:
        import akshare as ak

        df = ak.spot_hist_sge(symbol="Au99.99")
        print(df.tail(2))
    except Exception as exc:
        print("FAIL", exc)

    section("SGE Ag99.99")
    try:
        import akshare as ak

        df = ak.spot_hist_sge(symbol="Ag99.99")
        print(df.tail(2))
    except Exception as exc:
        print("FAIL", exc)

    section("SGE Pt99.95")
    try:
        import akshare as ak

        df = ak.spot_hist_sge(symbol="Pt99.95")
        print(df.tail(2))
    except Exception as exc:
        print("FAIL", exc)

    section("basket indices")
    try:
        import akshare as ak

        for name in ["macro_china_vegetable_basket", "macro_china_agricultural_product"]:
            df = getattr(ak, name)()
            print(name, df.tail(1).to_dict("records"))
    except Exception as exc:
        print("FAIL", exc)

    section("futures_spot_price_daily")
    try:
        import akshare as ak

        start = (date.today() - timedelta(days=14)).strftime("%Y%m%d")
        end = date.today().strftime("%Y%m%d")
        df = ak.futures_spot_price_daily(start_day=start, end_day=end)
        print("cols", list(df.columns))
        print("rows", len(df))
        if "symbol" in df.columns:
            symbols = sorted({str(s) for s in df["symbol"].unique()})
            print("symbol count", len(symbols))
            for kw in ["晚籼米", "花生油", "猪肉", "大豆", "鸡蛋", "白糖", "豆油", "菜籽油", "棉花", "螺纹钢"]:
                hits = [s for s in symbols if kw in s]
                print(kw, hits[:5] if hits else "NONE")
    except Exception as exc:
        print("FAIL", exc)
        traceback.print_exc()

    section("energy oil_price / energy_oil_hist")
    try:
        import akshare as ak

        candidates = [
            "energy_oil_hist",
            "energy_oil_detail",
            "oil_price_ajx",
            "energy_carbon_domestic",
        ]
        for name in candidates:
            if hasattr(ak, name):
                print("has", name)
                try:
                    fn = getattr(ak, name)
                    df = fn() if name != "energy_oil_hist" else fn()
                    print(name, "shape", getattr(df, "shape", None), "cols", list(df.columns)[:12])
                    print(df.head(2))
                except TypeError as te:
                    print(name, "TypeError", te)
                except Exception as e:
                    print(name, "FAIL", e)
            else:
                print("missing", name)
    except Exception as exc:
        print("FAIL", exc)

    section("FX / USD_CNY via akshare")
    try:
        import akshare as ak

        for name in ["fx_spot_quote", "currency_boc_safe", "macro_china_fx_reserves"]:
            if hasattr(ak, name):
                print("has", name)
            else:
                print("missing", name)
        if hasattr(ak, "fx_spot_quote"):
            df = ak.fx_spot_quote()
            print("fx_spot_quote cols", list(df.columns))
            print(df.head(5))
            # look for USD
            text = df.astype(str).to_string()
            print("contains 美元", "美元" in text or "USD" in text)
    except Exception as exc:
        print("FAIL", exc)
        traceback.print_exc()

    section("FRED sample without key")
    try:
        from app.config import settings
        from fredapi import Fred

        print("key set", bool(settings.fred_api_key))
        if settings.fred_api_key:
            fred = Fred(api_key=settings.fred_api_key)
            for sid in ["DCOILWTICO", "DCOILBRENTEU", "DHHNGSP", "PSILVERUSDM", "PALUMUSDM", "PSOILUSDM"]:
                try:
                    s = fred.get_series(sid)
                    print(sid, "len", len(s), "latest", s.dropna().iloc[-1], s.dropna().index[-1].date())
                except Exception as e:
                    print(sid, "FAIL", e)
    except Exception as exc:
        print("FAIL", exc)


if __name__ == "__main__":
    main()
