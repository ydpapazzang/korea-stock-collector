프로젝트 분석 보고서: korea-stock-collector
이 프로젝트는 한국 주식 시장의 데이터를 자동으로 수집, 저장 및 관리하고 그 결과를 사용자에게 알림으로 전송하는 자동화 시스템입니다. 
1. 주요 기능데이터 자동 수집: FinanceDataReader 라이브러리를 사용하여 한국 거래소의 전 종목 주식 데이터를 수집합니다.
  2. 스케줄링 자동화: GitHub Actions를 활용하여 매일 정해진 시간에 수집 프로세스를 실행합니다.
  3. 데이터 관리 및 정리: 수집된 데이터를 CSV 형식으로 저장하며, 오래된 데이터를 자동으로 정리하여 저장 공간을 최적화합니다.
  4. 알림 시스템: 데이터 수집 완료 및 시스템 상태를 사용자에게 즉시 알립니다.

2. 파일 구조 및 역할실행 및 설정main.py: 프로젝트의 메인 진입점으로, 수집기 호출 및 전체 실행 흐름을 제어합니다.
   3. requirements.txt: 프로젝트 실행에 필요한 라이브러리(pandas, FinanceDataReader 등)가 정의되어 있습니다.
   4. .github/workflows/: GitHub Actions 설정 파일들이 포함되어 있으며, daily_collect.yml과 cron.yml을 통해 주기적인 자동 실행을 관리합니다.
   5. 데이터 수집 모듈 (collector/)price_volume.py: 종목별 가격과 거래량 데이터를 상세하게 수집하는 로직을 담당합니다.
   6. fdr_bulk.py: 전체 종목에 대한 데이터를 일괄적으로(Bulk) 수집하여 효율성을 높입니다.
   7. utils.py: 날짜 처리 및 데이터 포맷팅 등 수집 과정에서 필요한 공통 유틸리티 함수를 제공합니다. 관리 및 기타
   8. notifier.py: 수집 결과나 오류 발생 시 알림을 전송하는 모듈입니다.
   9. cleanup.py: 임시 파일이나 오래된 데이터를 삭제하여 시스템 청결도를 유지합니다.
   10. data/: 수집된 한국 주식 데이터가 날짜별 CSV 파일로 저장되는 디렉토리입니다.

3. 기술 스택Language: Python Library: Pandas (데이터 처리), FinanceDataReader (주식 데이터 수집) Infrastructure: GitHub Actions (자동화 스케줄러) 
