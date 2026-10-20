"""Assemble the MDPI Water submission package in submission/.

    python analysis/make_submission.py

Writes three upload folders: 1_Manuscript (compiled PDF and LaTeX source archive), 2_Cover_Letter
(compiled one-page letter) and 3_Supplementary (one archive holding S1, the code, data, results and
design log, and S2, the literature review as PDF plus its source files). Run it after
`run_all.py --full` and a clean `latexmk -pdf` of the manuscript and of manuscript/cover_letter.tex.
"""
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
OUT = ROOT / "submission"
MAN, LET, SUP = OUT / "1_Manuscript", OUT / "2_Cover_Letter", OUT / "3_Supplementary"
WORK = OUT / "_build"   # S1/S2 parts before they are bundled into the single supplementary archive
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".venv-sys", ".venv"}
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
    path = MAN / "MAWRIC_X_Water_LaTeX_source.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ("MAWRIC_X_Water.tex", "MAWRIC_X_Water.bbl", "references.bib", "numbers.tex", "tabledefs.tex"):
            z.write(MS / f, f)
        for f in ("fig_style.tex", "fig_arch.tex", "fig_design.tex"):
            z.write(MS / "figures" / f, f"figures/{f}")
        for p in sorted((MS / "figures").glob("fig_*.pdf")):
            z.write(p, f"figures/{p.name}")
        add_tree(z, MS, "figures/icons", {".png"})   # pictograms drawn by fig_arch and fig_design
        add_tree(z, MS, "Definitions")
    return path


def supplement_s1():
    path = WORK / "S1_MAWRIC-X_code_and_data.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in ("README.md", "requirements.txt", "run_all.py", "EXPERIMENT_DESIGN.md", "mawricx", "experiments",
                    "analysis", "tests", "data", "results"):
            add_tree(z, ROOT, rel)
    return path


def supplement_s2():
    pdf = WORK / "S2_literature_review.pdf"
    subprocess.run(["pandoc", str(ROOT / "literature_review.md"), "-o", str(pdf), "--pdf-engine=xelatex",
                    "-V", "geometry:margin=2cm", "-V", "fontsize=10pt", "-V", "mainfont=Times New Roman",
                    "-V", "monofont=Consolas",
                    "-V", "colorlinks=true", "--toc", "-M", "title=MAWRIC-X literature review and research gaps"],
                   check=True, cwd=ROOT)
    path = WORK / "S2_literature_sources.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        add_tree(z, ROOT, "literature_review.md")
        add_tree(z, ROOT, "literature")
    return pdf, path


def supplementary(parts):
    path = SUP / "MAWRIC_X_Water_Supplementary_Materials.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as z:   # parts are already compressed
        for p in parts:
            z.write(p, p.name)
    return path


def main():
    for d in (MAN, LET, SUP, WORK):
        d.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MS / "MAWRIC_X_Water.pdf", MAN / "MAWRIC_X_Water.pdf")
    shutil.copy2(MS / "cover_letter.pdf", LET / "Cover_Letter.pdf")
    made = [MAN / "MAWRIC_X_Water.pdf", latex_source(), LET / "Cover_Letter.pdf",
            supplementary([supplement_s1(), *supplement_s2()])]
    shutil.rmtree(WORK)
    for p in made:
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
