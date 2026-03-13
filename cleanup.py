"""
cleanup.py
──────────
data/ 폴더에서 N일 이상 지난 CSV 파일을 삭제합니다.
GitHub Actions에서 매일 자동 실행됩니다.

사용법:
    python cleanup.py --days 7 --output data
"""

import os
import glob
import argparse
import datetime


def cleanup_old_files(output_dir: str, keep_days: int):
    pattern = os.path.join(output_dir, "korea_stocks_*.csv")
    files   = sorted(glob.glob(pattern))

    if not files:
        print(f"📂 {output_dir}/ 에 CSV 파일 없음")
        return

    cutoff = datetime.date.today() - datetime.timedelta(days=keep_days)
    print(f"🗑️  {keep_days}일 기준 (cutoff: {cutoff}) | 전체 {len(files)}개 파일 확인")

    deleted = []
    kept    = []

    for filepath in files:
        filename = os.path.basename(filepath)
        # 파일명에서 날짜 파싱: korea_stocks_YYYYMMDD.csv
        try:
            date_str = filename.replace("korea_stocks_", "").replace(".csv", "")
            file_date = datetime.datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            print(f"  ⚠️  날짜 파싱 실패 (스킵): {filename}")
            continue

        if file_date < cutoff:
            os.remove(filepath)
            deleted.append(filename)
            print(f"  🗑️  삭제: {filename} ({file_date})")
        else:
            kept.append(filename)
            print(f"  ✅ 보관: {filename} ({file_date})")

    print(f"\n완료 | 삭제 {len(deleted)}개 / 보관 {len(kept)}개")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="오래된 CSV 파일 정리")
    parser.add_argument("--days",   type=int, default=7,      help="보관 기간 (일)")
    parser.add_argument("--output", type=str, default="data", help="CSV 폴더 경로")
    args = parser.parse_args()

    cleanup_old_files(args.output, args.days)
