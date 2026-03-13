🇰🇷 Korea Stock Data Collector
KOSPI / KOSDAQ 전종목 일별 데이터를 자동 수집하여 CSV로 저장합니다.
GitHub Actions로 매일 오후 5:30 KST 자동 실행되며, 7일 지난 파일은 자동 삭제됩니다.

수집 데이터
컬럼	설명	소스
Code	종목코드	FDR
Name	종목명	FDR
Market	KOSPI / KOSDAQ	FDR
Sector / Industry	섹터/업종	FDR
Price	당일 종가	FDR
MarketCap	시가총액	FDR
PER	주가수익비율	네이버
PBR	주가순자산비율	네이버
ROE	자기자본이익률	네이버
PSR	주가매출비율	네이버
Volume_today	당일 거래량	FDR
Volume_month_avg/max/min	최근 1개월 거래량 통계	FDR
ma20 / ma60 / ma120	이동평균	계산
GoldenAlign_YN	정배열 여부 (ma20>ma60>ma120)	계산
GitHub Actions 배포 방법
Step 1. 레포 생성
github.com 로그인 → 우측 상단 + → New repository
이름: korea-stock-collector
Create repository 클릭
Step 2. 파일 업로드 (폴더 구조 그대로 유지)
korea-stock-collector/
├── .github/workflows/daily_collect.yml  ← 핵심!
├── collector/
│   ├── __init__.py
│   ├── fdr_bulk.py
│   ├── price_volume.py
│   └── utils.py
├── data/.gitkeep
├── cleanup.py
├── main.py
└── requirements.txt
Step 3. Actions 쓰기 권한 설정
레포 → Settings → Actions → General
→ Workflow permissions → Read and write permissions → Save

Step 4. 완료!
수동 실행: Actions 탭 → Daily Korea Stock Collector → Run workflow
자동 실행: 매 평일 오후 5:30 KST (cron: 30 8 * * 1-5)
파일 보관 정책
최근 7일치 CSV만 유지 (자동 삭제)
파일 크기: 약 1MB/일
1주일치 = 약 5~7MB (레포 용량 부담 없음)
로컬 실행
pip install finance-datareader pykrx pandas numpy requests tqdm beautifulsoup4
python main.py          # 전 영업일 기준
python cleanup.py       # 오래된 파일 수동 정리
