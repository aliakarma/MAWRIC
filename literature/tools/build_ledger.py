"""Fetch OpenAlex metadata + abstract and Crossref BibTeX for every candidate.

Input : literature/candidates.tsv  (key<TAB>doi<TAB>cluster<TAB>used_for)
Output: literature/ledger_raw.json, literature/source_ledger.csv,
        literature/references_lit.bib, literature/abstracts.md
Verification levels follow the finding-gap protocol:
  V1 = metadata + abstract from OpenAlex, V2 = DOI resolved at doi.org with
  publisher (Crossref) metadata. Nothing here is V3 (full text).
"""
import csv
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MAILTO = "aliakarma974@gmail.com"
TODAY = dt.date.today().isoformat()
sys.stdout.reconfigure(encoding="utf-8")


_LOCAL = None


def _local_index():
    """Index every OpenAlex work object cached by oa_search.py (search results)."""
    global _LOCAL
    if _LOCAL is None:
        _LOCAL = {}
        for f in (ROOT / "raw").glob("*.json"):
            if f.name.startswith("cr_"):
                continue
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            for w in d.get("results", []):
                doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
                if doi:
                    _LOCAL[doi] = w
    return _LOCAL


def s2(doi):
    for k in range(4):
        try:
            r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
                             params={"fields": "title,year,venue,abstract,citationCount,authors,publicationTypes"},
                             timeout=40)
            if r.status_code == 200:
                j = r.json()
                return {"display_name": j.get("title"), "publication_year": j.get("year"),
                        "authorships": [{"author": {"display_name": a.get("name")}} for a in j.get("authors", [])],
                        "primary_location": {"source": {"display_name": j.get("venue")}},
                        "type": ",".join(j.get("publicationTypes") or []), "cited_by_count": j.get("citationCount"),
                        "_abstract_text": j.get("abstract") or ""}
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(3 * (k + 1))
    return None


def oa(doi):
    w = _local_index().get(doi.lower())
    if w:
        return w
    return s2(doi)


def crossref_bib(doi):
    for k in range(3):
        try:
            r = requests.get(f"https://doi.org/{doi}", headers={"Accept": "application/x-bibtex; charset=utf-8"},
                             timeout=40, allow_redirects=True)
            if r.status_code == 200 and r.text.strip().startswith("@"):
                return r.content.decode("utf-8", errors="replace").strip()
            if r.status_code in (404, 406):
                return None
        except requests.RequestException:
            pass
        time.sleep(1.5 * (k + 1))
    return None


def abstract(w):
    if (w or {}).get("_abstract_text"):
        return w["_abstract_text"]
    inv = (w or {}).get("abstract_inverted_index") or {}
    pos = {i: word for word, idxs in inv.items() for i in idxs}
    return " ".join(pos[i] for i in sorted(pos))


def rekey(bib, key):
    return re.sub(r"^@(\w+)\{[^,]*,", lambda m: f"@{m.group(1)}{{{key},", bib, count=1)


def main():
    rows = []
    for line in (ROOT / "candidates.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        p = [x.strip() for x in line.split("|")]
        rows.append({"key": p[0].strip(), "doi": p[1].strip(), "cluster": p[2].strip() if len(p) > 2 else "",
                     "used_for": p[3].strip() if len(p) > 3 else ""})
    cache_p = ROOT / "ledger_raw.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    for r in rows:
        if r["key"] in cache and cache[r["key"]].get("doi") == r["doi"]:
            continue
        w = oa(r["doi"])
        bib = crossref_bib(r["doi"])
        cache[r["key"]] = {"doi": r["doi"], "openalex": w and {
            "title": w.get("display_name"), "year": w.get("publication_year"),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "type": w.get("type"), "cited_by": w.get("cited_by_count"), "abstract": abstract(w)},
            "bibtex": bib}
        print(("OK " if w else "NO-OA ") + ("BIB " if bib else "NO-BIB ") + r["key"], flush=True)
        time.sleep(1.1)
    cache_p.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")

    with (ROOT / "source_ledger.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["key", "title", "authors", "year", "venue", "doi_or_url", "retrieved_via", "retrieved_on",
                     "verification_level", "used_for", "preprint", "cluster", "cited_by"])
        for r in rows:
            c = cache[r["key"]]
            o = c["openalex"] or {}
            lvl = "V2" if c["bibtex"] else ("V1" if o else "unverified")
            pre = "yes" if (o.get("type") == "preprint" or "arxiv" in r["doi"].lower()
                            or "ssrn" in r["doi"].lower() or "preprints" in r["doi"].lower()) else "no"
            wr.writerow([r["key"], o.get("title", ""), "; ".join(o.get("authors", [])[:6]) +
                         ("; et al." if len(o.get("authors", [])) > 6 else ""), o.get("year", ""),
                         o.get("venue", ""), "https://doi.org/" + r["doi"], "OpenAlex API; doi.org (Crossref)",
                         TODAY, lvl, r["used_for"], pre, r["cluster"], o.get("cited_by", "")])
    with (ROOT / "references_lit.bib").open("w", encoding="utf-8") as f:
        for r in rows:
            b = cache[r["key"]]["bibtex"]
            if b:
                f.write(rekey(b, r["key"]) + "\n\n")
    with (ROOT / "abstracts.md").open("w", encoding="utf-8") as f:
        for r in rows:
            o = cache[r["key"]]["openalex"] or {}
            f.write(f"### {r['key']} ({o.get('year')}) {o.get('title')}\n{o.get('venue')} | doi:{r['doi']}\n\n"
                    f"{o.get('abstract') or '(no abstract in OpenAlex)'}\n\n")
    print("ledger rows:", len(rows))


if __name__ == "__main__":
    main()
