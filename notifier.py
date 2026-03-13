"""
notifier.py
───────────
수집 완료된 CSV를 이메일로 발송합니다.
"""
import os
import glob
import smtplib
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
import datetime


def send_email(output_dir: str, gmail_user: str, gmail_pw: str, to_email: str):
    # 최신 CSV 파일 찾기
    files = sorted(glob.glob(os.path.join(output_dir, "korea_stocks_*.csv")))
    if not files:
        print("⚠️  발송할 CSV 파일 없음")
        return

    latest_file = files[-1]
    filename    = os.path.basename(latest_file)
    date_str    = datetime.date.today().strftime("%Y-%m-%d")
    file_size   = os.path.getsize(latest_file) / 1024  # KB

    # 메일 구성
    msg = MIMEMultipart()
    msg["From"]    = gmail_user
    msg["To"]      = to_email
    msg["Subject"] = f"📊 [{date_str}] KOSPI/KOSDAQ 일별 데이터 수집 완료"

    # 본문
    body = f"""
안녕하세요!

오늘의 KOSPI/KOSDAQ 주식 데이터 수집이 완료되었습니다.

📅 기준일  : {date_str}
📁 파일명  : {filename}
📦 파일크기: {file_size:.1f} KB
📊 수집항목: 종목코드, 종목명, 시가총액, PER, PBR, ROE, PSR,
            이동평균(ma20/60/120), 정배열 신호 등

첨부 파일을 확인해주세요.

---
자동 발송 by Korea Stock Collector
GitHub: https://github.com/ydpapazzang/korea-stock-collector
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # CSV 첨부
    with open(latest_file, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    # 발송
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pw)
            server.sendmail(gmail_user, to_email, msg.as_string())
        print(f"✅ 이메일 발송 완료 → {to_email} ({filename})")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",   type=str, default="data")
    parser.add_argument("--from_email", type=str, default=os.environ.get("GMAIL_USER", ""))
    parser.add_argument("--password",   type=str, default=os.environ.get("GMAIL_PASSWORD", ""))
    parser.add_argument("--to_email",   type=str, default=os.environ.get("NOTIFY_EMAIL", ""))
    args = parser.parse_args()

    if not all([args.from_email, args.password, args.to_email]):
        print("❌ 환경변수 GMAIL_USER, GMAIL_PASSWORD, NOTIFY_EMAIL 필요")
    else:
        send_email(args.output, args.from_email, args.password, args.to_email)
