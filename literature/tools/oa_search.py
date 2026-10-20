"""OpenAlex search helper for the MAWRIC-X literature review.

Every query is appended to literature/search_log.csv and the raw response is
cached in literature/raw/. Screening output prints one compact line per hit.

Usage:
    python oa_search.py PASS "query text" [--n 15] [--from 2015] [--to 2026]
    python oa_search.py --batch queries.tsv      (columns: pass<TAB>query<TAB>from<TAB>to<TAB>n)
    python oa_search.py --doi 10.3390/w17202957 [10.xxxx ...]   (metadata + abstract)
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
RAW.mkdir(exist_ok=True)
LOG = ROOT / "search_log.csv"
MAILTO = "aliakarma974@gmail.com"
API = "https://api.openalex.org/works"


def abstract(w):
    inv = w.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def authors(w, k=4):
    names = [a["author"]["display_name"] for a in w.get("authorships", [])]
    s = "; ".join(names[:k])
    return s + ("; et al." if len(names) > k else "")


def venue(w):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    return src.get("display_name") or "unknown"


def log_row(pass_, query, filters, n_ret):
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        if new:
            wr.writerow(["no", "date", "pass", "tool", "query", "filters", "results_returned", "new_relevant", "notes"])
        no = sum(1 for _ in LOG.open(encoding="utf-8")) if not new else 1
        wr.writerow([no, dt.date.today().isoformat(), pass_, "OpenAlex API", query, filters, n_ret, "", ""])


def search(pass_, query, n=15, y0=None, y1=None, sort=None):
    params = {"search": query, "per-page": n, "mailto": MAILTO}
    filt = []
    if y0 or y1:
        filt.append(f"publication_year:{y0 or 1900}-{y1 or 2026}")
    filt.append("type:article|review|preprint|book-chapter|proceedings-article")
    params["filter"] = ",".join(filt)
    if sort:
        params["sort"] = sort
    for attempt in range(4):
        try:
            r = requests.get(API, params=params, timeout=40)
            if r.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(2 + attempt * 2)
    else:
        print("FAILED", query)
        return []
    res = r.json().get("results", [])
    h = hashlib.md5((pass_ + query + str(y0) + str(y1)).encode()).hexdigest()[:10]
    (RAW / f"{pass_}_{h}.json").write_text(json.dumps({"query": query, "pass": pass_, "y0": y0, "y1": y1,
                                                        "results": res}, indent=1), encoding="utf-8")
    log_row(pass_, query, f"years {y0 or ''}-{y1 or ''}; n={n}", len(res))
    print(f"\n### [{pass_}] {query}  ({y0 or ''}-{y1 or ''}) -> {len(res)}")
    for i, w in enumerate(res):
        doi = (w.get("doi") or "").replace("https://doi.org/", "")
        print(f"{i:02d} {w.get('publication_year')} c{w.get('cited_by_count'):<5} {doi:<38} "
              f"{(w.get('display_name') or '')[:105]} | {venue(w)[:40]}")
    return res


def by_doi(dois, show_abs=True):
    out = []
    for d in dois:
        d = d.strip().replace("https://doi.org/", "")
        try:
            r = requests.get(f"{API}/https://doi.org/{d}", params={"mailto": MAILTO}, timeout=40)
        except requests.RequestException as e:
            print("ERR", d, e)
            continue
        if r.status_code != 200:
            print("NOTFOUND", d, r.status_code)
            continue
        w = r.json()
        out.append(w)
        print(f"\n== {d}\n   {w.get('display_name')}\n   {authors(w, 8)}\n   {w.get('publication_year')} | "
              f"{venue(w)} | cites {w.get('cited_by_count')} | type {w.get('type')}")
        if show_abs:
            a = abstract(w)
            print("   ABS:", (a[:1400] + ("..." if len(a) > 1400 else "")) if a else "(no abstract in OpenAlex)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pass_", nargs="?")
    ap.add_argument("query", nargs="?")
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--from", dest="y0", type=int)
    ap.add_argument("--to", dest="y1", type=int)
    ap.add_argument("--sort")
    ap.add_argument("--batch")
    ap.add_argument("--doi", nargs="+")
    ap.add_argument("--noabs", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.doi:
        by_doi(a.doi, not a.noabs)
    elif a.batch:
        for line in Path(a.batch).read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            p, q = parts[0], parts[1]
            y0 = int(parts[2]) if len(parts) > 2 and parts[2] else None
            y1 = int(parts[3]) if len(parts) > 3 and parts[3] else None
            n = int(parts[4]) if len(parts) > 4 and parts[4] else a.n
            search(p, q, n, y0, y1, a.sort)
            time.sleep(0.3)
    else:
        search(a.pass_, a.query, a.n, a.y0, a.y1, a.sort)
