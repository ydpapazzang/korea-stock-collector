
import time, re
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer":    "https://finance.naver.com/sise/sise_market_sum.naver",
}

def _parse_num(s):
    s = s.strip().replace(",", "").replace("-", "")
    try: return float(s) if s else None
    except: return None

def _fetch_naver_page(sosok, page):
    url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
    try:
        soup = BeautifulSoup(requests.get(url, headers=_HEADERS, timeout=10).text, "html.parser")
        results = []
        for row in soup.select("table.type_2 tr"):
            cols = row.select("td")
            if len(cols) < 12: continue
            a_tag = cols[1].select_one("a")
            if not a_tag: continue
            m = re.search(r"code=(\d+)", a_tag.get("href", ""))
            if not m: continue
            results.append({
                "Code": m.group(1).zfill(6),
                "PER":  _parse_num(cols[10].get_text()),
                "ROE":  _parse_num(cols[11].get_text()),
            })
        return results
    except: return []

def _fetch_last_page(sosok):
    url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page=1"
    try:
        soup = BeautifulSoup(requests.get(url, headers=_HEADERS, timeout=10).text, "html.parser")
        last = soup.select("td.pgRR a")
        if last:
            m = re.search(r"page=(\d+)", last[0]["href"])
            if m: return int(m.group(1))
    except: pass
    return 50

def _fetch_naver_bulk():
    all_records = []
    for sosok, market in [(0,"KOSPI"),(1,"KOSDAQ")]:
        last_page = _fetch_last_page(sosok)
        print(f"  [네이버] {market} {last_page}페이지 수집 중...")
        with ThreadPoolExecutor(max_workers=8) as exe:
            futures = {exe.submit(_fetch_naver_page, sosok, p): p for p in range(1, last_page+1)}
            for f in tqdm(as_completed(futures), total=last_page, desc=market):
                try: all_records.extend(f.result())
                except: pass
        time.sleep(0.3)
    if not all_records:
        return pd.DataFrame(columns=["Code","PER","ROE"])
    df = pd.DataFrame(all_records)
    df["Code"] = df["Code"].astype(str).str.zfill(6)
    return df.drop_duplicates("Code")

def _get_naver_fundamental(code):
    result = {"Code": code, "PBR": None, "PSR": None}
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        soup = BeautifulSoup(requests.get(url, headers=_HEADERS, timeout=5).text, "html.parser")
        table = soup.select_one("table.per_table")
        if table:
            parts = table.get_text("|", strip=True).split("|")
            try: result["PBR"] = float(parts[28].replace(",",""))
            except: pass
        sales_th = soup.select_one("th.th_cop_anal8")
        if sales_th:
            sales_td = sales_th.parent.select_one("td.t_line.cell_strong")
            if sales_td:
                try: result["_sales"] = float(sales_td.get_text(strip=True).replace(",",""))
                except: pass
    except: pass
    return result

def _fetch_pbr_psr_parallel(codes, marcap_map, max_workers=20):
    print(f"  [네이버] PBR/PSR 수집 중... ({len(codes):,}개, workers={max_workers})")
    results = []
    def _fetch(code):
        r = _get_naver_fundamental(code)
        sales = r.pop("_sales", None)
        marcap = marcap_map.get(code)
        if sales and marcap and sales > 0:
            r["PSR"] = round(marcap / 1_000_000 / sales, 2)
        return r
    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        futures = {exe.submit(_fetch, c): c for c in codes}
        for f in tqdm(as_completed(futures), total=len(codes), desc="PBR/PSR"):
            try: results.append(f.result(timeout=10))
            except: results.append({"Code": futures[f], "PBR": None, "PSR": None})
    df = pd.DataFrame(results)
    df["Code"] = df["Code"].astype(str).str.zfill(6)
    return df.drop_duplicates("Code")

def fetch_all_bulk(date):
    print(f"  [FDR] 전종목 시세 수집 중... (기준일: {date})")
    kospi  = fdr.StockListing("KOSPI")
    kosdaq = fdr.StockListing("KOSDAQ")
    df = pd.concat([kospi, kosdaq], ignore_index=True)
    df = df.rename(columns={"Close":"Price","Marcap":"MarketCap","Volume":"Volume_today","Dept":"Industry"})
    df["Sector"]   = df["Industry"].fillna("Unknown")
    df["Industry"] = df["Sector"]
    df["Market"]   = df["Market"].str.strip()
    keep = ["Code","Name","Market","Sector","Industry","Price","MarketCap","Volume_today"]
    df = df[[c for c in keep if c in df.columns]].copy()
    df["Code"] = df["Code"].astype(str).str.zfill(6)
    print(f"        → {len(df):,}개 종목")
    bulk_fund = _fetch_naver_bulk()
    marcap_map = dict(zip(df["Code"], df["MarketCap"]))
    pbr_psr = _fetch_pbr_psr_parallel(df["Code"].tolist(), marcap_map, max_workers=20)
    pbr_psr = pbr_psr[["Code","PBR","PSR"]]
    df = df.merge(bulk_fund, on="Code", how="left")
    df = df.merge(pbr_psr,  on="Code", how="left")
    return df
