"""Probe more symbols and FRED series."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import date, timedelta


def main() -> None:
    print("=== futures_spot symbols ===")
    import akshare as ak

    start = (date.today() - timedelta(days=14)).strftime("%Y%m%d")
    end = date.today().strftime("%Y%m%d")
    df = ak.futures_spot_price_daily(start_day=start, end_day=end)
    symbols = sorted({str(s) for s in df["symbol"].unique()})
    for s in symbols:
        print(s)
    latest = df["date"].max()
    day = df[df["date"] == latest]
    print("latest date", latest, "rows", len(day))

    print("\n=== FRED series ===")
    from app.config import settings
    from fredapi import Fred

    print("key set", bool(settings.fred_api_key))
    if settings.fred_api_key:
        fred = Fred(api_key=settings.fred_api_key)
        for sid in [
            "DCOILWTICO",
            "DCOILBRENTEU",
            "DHHNGSP",
            "PSILVERUSDM",
            "PALUMUSDM",
            "PSOILUSDM",
            "PCOPPUSDM",
            "PWHEAMTUSDM",
            "PMAIZMTUSDM",
            "PSOYBUSDM",
            "PCOTTINDUSDM",
            "IRONORE",
            "PIORECRUSDM",
        ]:
            try:
                s = fred.get_series(sid).dropna()
                print(sid, "latest", float(s.iloc[-1]), s.index[-1].date())
            except Exception as e:
                print(sid, "FAIL", e)

    print("\n=== currency_boc_safe sample ===")
    try:
        df2 = ak.currency_boc_safe()
        print(df2.tail(3))
        print("cols", list(df2.columns)[:20])
    except Exception as e:
        print("FAIL", e)

    print("\n=== spot_price_qh / other food ===")
    for name in [
        "spot_goods",
        "futures_main_sina",
        "index_hog_spot_price",
        "spot_hist_sge",
    ]:
        print(name, "has", hasattr(ak, name))

    if hasattr(ak, "index_hog_spot_price"):
        try:
            hog = ak.index_hog_spot_price()
            print("hog cols", list(hog.columns))
            print(hog.tail(2))
        except Exception as e:
            print("hog FAIL", e)


if __name__ == "__main__":
    main()
