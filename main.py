import argparse, sys

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--date",   type=str,   default=None)
    p.add_argument("--delay",  type=float, default=0.1)
    p.add_argument("--output", type=str,   default="data")
    return p.parse_args()

def main():
    args = parse_args()
    from collector import (fetch_all_bulk, fetch_all_price_volume,
                           get_last_trading_day, save_csv,
                           reorder_columns, print_summary)

    date = args.date or get_last_trading_day()
    print(f"\n🚀 Korea Stock Collector 시작")
    print(f"   기준일  : {date}")
    print(f"   저장위치: {args.output}/\n")

    print("[1/3] 기본정보 + 시세 + 펀더멘털 수집...")
    df_bulk = fetch_all_bulk(date)

    print(f"\n[2/3] 이동평균 / 거래량 수집...")
    df_pv = fetch_all_price_volume(df_bulk["Code"].tolist(), end_date=date)

    print("\n[3/3] 병합 및 저장...")
    import pandas as pd
    df = df_bulk.merge(df_pv, on="Code", how="left")
    df = reorder_columns(df)
    filepath = save_csv(df, args.output, date)
    print_summary(df, date, filepath)

if __name__ == "__main__":
    main()
