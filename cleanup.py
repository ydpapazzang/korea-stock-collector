import os, glob, argparse, datetime

def cleanup_old_files(output_dir, keep_days):
    pattern = os.path.join(output_dir, "korea_stocks_*.csv")
    files   = sorted(glob.glob(pattern))
    if not files:
        print(f"📂 {output_dir}/ 에 CSV 파일 없음")
        return
    cutoff = datetime.date.today() - datetime.timedelta(days=keep_days)
    print(f"🗑️  {keep_days}일 기준 (cutoff: {cutoff}) | 전체 {len(files)}개 확인")
    deleted, kept = [], []
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            date_str  = filename.replace("korea_stocks_","").replace(".csv","")
            file_date = datetime.datetime.strptime(date_str, "%Y%m%d").date()
        except: continue
        if file_date < cutoff:
            os.remove(filepath)
            deleted.append(filename)
            print(f"  🗑️  삭제: {filename}")
        else:
            kept.append(filename)
            print(f"  ✅ 보관: {filename}")
    print(f"\n완료 | 삭제 {len(deleted)}개 / 보관 {len(kept)}개")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",   type=int, default=7)
    parser.add_argument("--output", type=str, default="data")
    args = parser.parse_args()
    cleanup_old_files(args.output, args.days)
