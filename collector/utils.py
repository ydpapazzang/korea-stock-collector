import os, datetime
import pandas as pd

def get_last_trading_day() -> str:
    candidate = datetime.date.today() - datetime.timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= datetime.timedelta(days=1)
    return candidate.strftime("%Y%m%d")

def save_csv(df, output_dir, date):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"korea_stocks_{date}.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path

COLUMN_ORDER = [
    "Code","Name","Market","Sector","Industry",
    "Price","MarketCap","PER","PBR","ROE","PSR",
    "Volume_today","Volume_month_avg","Volume_month_max","Volume_month_min",
    "ma20","ma60","ma120","GoldenAlign_YN",
]

def reorder_columns(df):
    existing = [c for c in COLUMN_ORDER if c in df.columns]
    extra    = [c for c in df.columns if c not in COLUMN_ORDER]
    return df[existing + extra]

def print_summary(df, date, filepath):
    total      = len(df)
    kospi_cnt  = len(df[df["Market"]=="KOSPI"])  if "Market" in df.columns else "-"
    kosdaq_cnt = len(df[df["Market"]=="KOSDAQ"]) if "Market" in df.columns else "-"
    golden_cnt = len(df[df["GoldenAlign_YN"]=="Y"]) if "GoldenAlign_YN" in df.columns else "-"
    print("\n" + "="*60)
    print(f"  ✅ 수집 완료 | 기준일: {date}")
    print(f"     총 종목수  : {total:,}개")
    print(f"     KOSPI      : {kospi_cnt:,}개")
    print(f"     KOSDAQ     : {kosdaq_cnt:,}개")
    print(f"     정배열 종목: {golden_cnt:,}개")
    print(f"     저장 경로  : {filepath}")
    print("="*60)
