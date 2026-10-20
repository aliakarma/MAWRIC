"""Crossref search helper (used after the OpenAlex free daily budget ran out).

Logs every query to literature/search_log.csv like oa_search.py does.
Usage:  python cr_search.py --batch file.tsv   (pass<TAB>query<TAB>from<TAB>to<TAB>n)
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
LOG = ROOT / "search_log.csv"
MAILTO = "aliakarma974@gmail.com"
sys.stdout.reconfigure(encoding="utf-8")


def log_row(pass_, query, filters, n_ret):
    no = sum(1 for _ in LOG.open(encoding="utf-8"))
    with LOG.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([no, dt.date.today().isoformat(), pass_, "Crossref API", query, filters, n_ret, "", ""])


def search(pass_, query, n=10, y0=None, y1=None):
    params = {"query.bibliographic": query, "rows": n, "mailto": MAILTO,
              "select": "DOI,title,issued,container-title,author,is-referenced-by-count,type"}
    filt = []
    if y0:
        filt.append(f"from-pub-date:{y0}")
    if y1:
        filt.append(f"until-pub-date:{y1}")
    if filt:
        params["filter"] = ",".join(filt)
    for k in range(4):
        try:
            r = requests.get("https://api.crossref.org/works", params=params, timeout=60)
            if r.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(2 + 2 * k)
    else:
        print("FAILED", query)
        return []
    items = r.json()["message"]["items"]
    h = hashlib.md5((pass_ + query).encode()).hexdigest()[:10]
    (RAW / f"cr_{pass_}_{h}.json").write_text(json.dumps({"query": query, "items": items}, indent=1), encoding="utf-8")
    log_row(pass_, query, f"years {y0 or ''}-{y1 or ''}; n={n}", len(items))
    print(f"\n### [{pass_}] {query} ({y0 or ''}-{y1 or ''}) -> {len(items)}")
    for i, it in enumerate(items):
        yr = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        t = (it.get("title") or [""])[0][:105]
        v = (it.get("container-title") or [""])
        v = v[0][:38] if v else ""
        print(f"{i:02d} {yr} c{it.get('is-referenced-by-count', 0):<5} {it.get('DOI', ''):<38} {t} | {v}")
    return items


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    for line in Path(a.batch).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        p = line.split("\t")
        y0 = int(p[2]) if len(p) > 2 and p[2] else None
        y1 = int(p[3]) if len(p) > 3 and p[3] else None
        n = int(p[4]) if len(p) > 4 and p[4] else a.n
        search(p[0], p[1], n, y0, y1)
        time.sleep(1.0)
