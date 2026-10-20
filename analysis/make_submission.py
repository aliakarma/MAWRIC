"""Assemble the MDPI Water submission package in submission/.

    python analysis/make_submission.py

Writes the compiled manuscript, a LaTeX source archive, Supplementary Material S1 (code, data,
results, design log) and S2 (literature review as PDF plus its source files). Run it after
`run_all.py --full` and a clean `latexmk -pdf` of the manuscript.
"""
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
OUT = ROOT / "submission"
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".venv-sys", ".venv"}
SKIP_FILES = {"ghcnd-inventory.txt", "ghcnd-stations.txt"}   # NOAA station metadata, not needed to rerun


def add_tree(z, base, rel, suffixes=None):
    src = base / rel
    files = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
    for p in files:
        if SKIP_DIRS & set(p.relative_to(base).parts) or p.name in SKIP_FILES:
            continue
        if suffixes and p.suffix.lower() not in suffixes:
            continue
        z.write(p, p.relative_to(base).as_posix())


def latex_source():
    path = OUT / "MAWRIC_X_Water_LaTeX_source.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ("MAWRIC_X_Water.tex", "MAWRIC_X_Water.bbl", "references.bib", "numbers.tex", "tabledefs.tex"):
            z.write(MS / f, f)
        add_tree(z, MS, "figures", {".tex", ".pdf"})
        add_tree(z, MS, "Definitions")
    return path


def supplement_s1():
    path = OUT / "S1_MAWRIC-X_code_and_data.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in ("README.md", "requirements.txt", "run_all.py", "EXPERIMENT_DESIGN.md", "mawricx", "experiments",
                    "analysis", "tests", "data", "results"):
            add_tree(z, ROOT, rel)
    return path


def supplement_s2():
    pdf = OUT / "S2_literature_review.pdf"
    subprocess.run(["pandoc", str(ROOT / "literature_review.md"), "-o", str(pdf), "--pdf-engine=xelatex",
                    "-V", "geometry:margin=2cm", "-V", "fontsize=10pt", "-V", "mainfont=Times New Roman",
                    "-V", "monofont=Consolas",
                    "-V", "colorlinks=true", "--toc", "-M", "title=MAWRIC-X literature review and research gaps"],
                   check=True, cwd=ROOT)
    path = OUT / "S2_literature_sources.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        add_tree(z, ROOT, "literature_review.md")
        add_tree(z, ROOT, "literature")
    return pdf, path


def main():
    OUT.mkdir(exist_ok=True)
    shutil.copy2(MS / "MAWRIC_X_Water.pdf", OUT / "MAWRIC_X_Water.pdf")
    made = [OUT / "MAWRIC_X_Water.pdf", latex_source(), supplement_s1(), *supplement_s2()]
    for p in made:
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
