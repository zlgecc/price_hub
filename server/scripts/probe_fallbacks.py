"""Probe no-key fallbacks for oil/commodities."""
from __future__ import annotations

import httpx


def main() -> None:
    print("=== FRED CSV no key ===")
    for sid in ["DCOILWTICO", "DCOILBRENTEU", "DHHNGSP", "PCOPPUSDM", "PSILVERUSDM", "PALUMUSDM", "PSOILUSDM", "PSOYBUSDM"]:
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
            r = httpx.get(url, timeout=30, follow_redirects=True)
            print(sid, r.status_code, "bytes", len(r.content))
            if r.is_success:
                lines = [ln for ln in r.text.strip().splitlines() if ln and not ln.startswith("DATE")]
                # last non-empty numeric
                for ln in reversed(lines):
                    parts = ln.split(",")
                    if len(parts) >= 2 and parts[1] not in (".", ""):
                        print("  latest", parts[0], parts[1])
                        break
        except Exception as e:
            print(sid, "FAIL", e)

    print("\n=== futures_spot useful codes ===")
    import akshare as ak
    from datetime import date, timedelta

    start = (date.today() - timedelta(days=7)).strftime("%Y%m%d")
    end = date.today().strftime("%Y%m%d")
    df = ak.futures_spot_price_daily(start_day=start, end_day=end)
    latest = df["date"].max()
    day = df[df["date"] == latest]
    wanted = {
        "CU": "铜",
        "AL": "铝",
        "ZN": "锌",
        "RB": "螺纹钢",
        "I": "铁矿石",
        "Y": "豆油",
        "P": "棕榈油",
        "OI": "菜籽油",
        "M": "豆粕",
        "C": "玉米",
        "A": "豆一",
        "SR": "白糖",
        "CF": "棉花",
        "JD": "鸡蛋",
        "LH": "生猪",
        "AU": "黄金",
        "AG": "白银",
    }
    for code, name in wanted.items():
        row = day[day["symbol"] == code]
        if row.empty:
            print(code, name, "MISSING")
        else:
            print(code, name, float(row.iloc[0]["spot_price"]))

    print("\n=== FreeGoldAPI silver? ===")
    # check metals-api free alternatives
    for url in [
        "https://api.metals.live/v1/spot/gold",
        "https://api.metals.live/v1/spot/silver",
        "https://data-asg.goldprice.org/dbXRates/USD",
    ]:
        try:
            r = httpx.get(url, timeout=20, follow_redirects=True)
            print(url, r.status_code, r.text[:180].replace("\n", " "))
        except Exception as e:
            print(url, "FAIL", e)


if __name__ == "__main__":
    main()
