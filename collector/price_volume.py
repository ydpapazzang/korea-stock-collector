
import time, datetime
import numpy as np
import pandas as pd
import FinanceDataReader as fdr
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def _date_str(days_back):
    return (datetime.date.today() - datetime.timedelta(days=days_back)).strftime("%Y%m%d")

def fetch_ticker(args):
    ticker, end_date = args
    result = {
        "Code": ticker,
        "ma20": np.nan, "ma60": np.nan, "ma120": np.nan,
        "GoldenAlign_YN": "N",
        "Volume_month_avg": np.nan,
        "Volume_month_max": np.nan,
        "Volume_month_min": np.nan,
    }
    try:
        df = fdr.DataReader(ticker, _date_str(200), end_date)
        if df is None or df.empty: return result
        close, vol = df["Close"], df["Volume"]
        if len(close) >= 20:  result["ma20"]  = round(float(close.rolling(20).mean().iloc[-1]),  0)
        if len(close) >= 60:  result["ma60"]  = round(float(close.rolling(60).mean().iloc[-1]),  0)
        if len(close) >= 120: result["ma120"] = round(float(close.rolling(120).mean().iloc[-1]), 0)
        m20, m60, m120 = result["ma20"], result["ma60"], result["ma120"]
        if not any(np.isnan(x) for x in [m20, m60, m120]):
            result["GoldenAlign_YN"] = "Y" if (m20 > m60 > m120) else "N"
        vol_1m = vol.iloc[-22:]
        result["Volume_month_avg"] = int(vol_1m.mean())
        result["Volume_month_max"] = int(vol_1m.max())
        result["Volume_month_min"] = int(vol_1m.min())
    except: pass
    return result

def fetch_all_price_volume(tickers, end_date, delay=0, max_workers=16):
    print(f"  [FDR] 병렬 수집 (workers={max_workers}) | {len(tickers):,}개 종목")
    records = []
    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        futures = {exe.submit(fetch_ticker, (t, end_date)): t for t in tickers}
        for f in tqdm(as_completed(futures), total=len(tickers), desc="이동평균 계산"):
            try: records.append(f.result(timeout=15))
            except: records.append({"Code": futures[f]})
    df = pd.DataFrame(records)
    df["Code"] = df["Code"].astype(str).str.zfill(6)
    return df
