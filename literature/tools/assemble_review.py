"""Assemble literature_review.md = review_body.md + ledger appendix built from publisher BibTeX."""
import csv
import html
import re
from pathlib import Path

LIT = Path(__file__).resolve().parents[1]
ROOT = LIT.parent

CLUSTERS = {
    "C1-DT": "C1. Urban water digital twins and hydroinformatics",
    "C2-MAS": "C2. Multi-agent control, decomposition and task allocation",
    "C3-LLM": "C3. LLM and agentic AI in water and smart cities",
    "C4-ALLOC": "C4. Fit-for-purpose allocation, alternative sources and reuse",
    "C5-LOSS": "C5. Loss recovery: leakage, pressure, detection, repair and robots",
    "C6-OPS": "C6. Operations and the water-energy nexus",
    "C7-DEM": "C7. Demand, metering, behaviour and sectors",
    "C8-GOV": "C8. Governance, safety, security and human factors",
    "C9-ECON": "C9. Economics, evaluation and sensitivity analysis",
    "C10-TOOL": "C10. Tools and data",
}


def field(entry, name):
    m = re.search(name + r"\s*=\s*\{(.*?)\}\s*(,\s*\w+\s*=|\}\s*$)", entry, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def short_authors(a):
    names = [x.strip() for x in a.split(" and ") if x.strip()]
    fam = [n.split(",")[0].strip() if "," in n else n.split()[-1] for n in names]
    if not fam:
        return ""
    if len(fam) == 1:
        return fam[0]
    if len(fam) == 2:
        return f"{fam[0]} and {fam[1]}"
    return f"{fam[0]} et al."


def main():
    bib = (LIT / "references_lit.bib").read_text(encoding="utf-8")
    ent = {}
    for e in re.split(r"\n(?=@)", bib.strip()):
        k = re.match(r"@\w+\{([^,]+),", e).group(1)
        ent[k] = e
    ledger = list(csv.DictReader((LIT / "source_ledger.csv").open(encoding="utf-8")))
    out = []
    for code, title in CLUSTERS.items():
        rows = [r for r in ledger if r["cluster"] == code]
        if not rows:
            continue
        out.append(f"\n### {title} ({len(rows)})\n")
        out.append("| Key | Authors | Year | Title | Venue | DOI |")
        out.append("|---|---|---|---|---|---|")
        for r in sorted(rows, key=lambda r: (field(ent[r['key']], 'year'), r["key"])):
            e = ent[r["key"]]
            au = short_authors(field(e, "author")) or r["authors"].split(";")[0]
            yr = field(e, "year") or r["year"]
            ti = (field(e, "title") or r["title"]).replace("|", "/").replace("\n", " ")
            ve = (field(e, "journal") or field(e, "booktitle") or field(e, "publisher") or r["venue"]).replace("|", "/")
            doi = r["doi_or_url"].replace("https://doi.org/", "")
            out.append(f"| `{r['key']}` | {au} | {yr} | {ti} | {ve} | [{doi}](https://doi.org/{doi}) |")
    body = (LIT / "review_body.md").read_text(encoding="utf-8")
    text = body.rstrip() + "\n" + "\n".join(out) + "\n"
    text = text.replace(" — ", ", ").replace("—", ", ").replace(" – ", ": ").replace("–", "-")
    text = text.replace("; ", ", ")  # house style: no semicolons, also inside reproduced titles
    (ROOT / "literature_review.md").write_text(text, encoding="utf-8")
    print("written", ROOT / "literature_review.md", len(text.split()), "words")


if __name__ == "__main__":
    main()
