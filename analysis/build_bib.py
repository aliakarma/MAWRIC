"""Build manuscript/references.bib from the verified literature ledger.

Only keys cited in manuscript/MAWRIC_X_Water.tex are written. Entries come from
publisher BibTeX fetched at doi.org (literature/references_lit.bib) plus a few
verified extras without a ledger row. Fails if any cited key is missing.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "manuscript" / "MAWRIC_X_Water.tex"
LIT = ROOT / "literature" / "references_lit.bib"
OUT = ROOT / "manuscript" / "references.bib"

EXTRA = {
    "huangfu2017": r"""@article{huangfu2017, title={Parallelizing the dual revised simplex method}, volume={10}, DOI={10.1007/s12532-017-0130-5}, number={1}, journal={Mathematical Programming Computation}, author={Huangfu, Q. and Hall, J. A. J.}, year={2018}, pages={119--142}}""",
    "virtanen2020": r"""@article{virtanen2020, title={{SciPy} 1.0: fundamental algorithms for scientific computing in {Python}}, volume={17}, DOI={10.1038/s41592-019-0686-2}, number={3}, journal={Nature Methods}, author={Virtanen, Pauli and Gommers, Ralf and Oliphant, Travis E. and Haberland, Matt and Reddy, Tyler and Cournapeau, David and Burovski, Evgeni and Peterson, Pearu and Weckesser, Warren and Bright, Jonathan and others}, year={2020}, pages={261--272}}""",
    "shapley1953": r"""@incollection{shapley1953, title={A Value for n-Person Games}, booktitle={Contributions to the Theory of Games, Volume {II}}, editor={Kuhn, H. W. and Tucker, A. W.}, publisher={Princeton University Press}, address={Princeton, NJ, USA}, author={Shapley, L. S.}, year={1953}, pages={307--318}, DOI={10.1515/9781400881970-018}}""",
    "rossman2020": r"""@techreport{rossman2020, title={{EPANET} 2.2 User Manual}, institution={U.S. Environmental Protection Agency}, address={Washington, DC, USA}, number={EPA/600/R-20/133}, author={Rossman, Lewis A. and Woo, Hyoungmin and Tryby, Michael and Shang, Feng and Janke, Robert and Haxton, Terranna}, year={2020}}""",
    "euaiact2024": r"""@misc{euaiact2024, title={Regulation ({EU}) 2024/1689 of the {European} {Parliament} and of the {Council} of 13 June 2024 Laying Down Harmonised Rules on Artificial Intelligence ({Artificial} {Intelligence} {Act})}, howpublished={Official Journal of the European Union, L series, 12 July 2024}, url={http://data.europa.eu/eli/reg/2024/1689/oj}, author={{European Parliament and Council of the European Union}}, year={2024}}""",
    # verified 2026-10-17 against Crossref; ECA&D asks users of its series to cite this paper
    "kleintank2002": r"""@article{kleintank2002, title={Daily Dataset of 20th-Century Surface Air Temperature and Precipitation Series for the {European} {Climate} {Assessment}}, volume={22}, DOI={10.1002/joc.773}, number={12}, journal={International Journal of Climatology}, author={Klein Tank, A. M. G. and Wijngaard, J. B. and K{\"o}nnen, G. P. and B{\"o}hm, R. and Demar{\'e}e, G. and Gocheva, A. and Mileta, M. and Pashiardis, S. and Hejkrlik, L. and Kern-Hansen, C. and others}, year={2002}, pages={1441--1453}}""",
    # verified 2026-10-17 against Crossref (metadata) and OpenAlex (abstract)
    "kerkez2016": r"""@article{kerkez2016, title={Smarter Stormwater Systems}, volume={50}, DOI={10.1021/acs.est.5b05870}, number={14}, journal={Environmental Science \& Technology}, author={Kerkez, Branko and Gruden, Cyndee and Lewis, Matthew and Montestruque, Luis and Quigley, Marcus and Wong, Brandon and Bedig, Alex and Kertesz, Ruben and Braun, Tim and Cadwalader, Owen and Poresky, Aaron and Pak, Carrie}, year={2016}, pages={7267--7273}}""",
    "malajetmarova2017": r"""@article{malajetmarova2017, title={Lost in Optimisation of Water Distribution Systems? {A} Literature Review of System Operation}, volume={93}, DOI={10.1016/j.envsoft.2017.02.009}, journal={Environmental Modelling \& Software}, author={Mala-Jetmarova, Helena and Sultanova, Nargiz and Savic, Dragan}, year={2017}, pages={209--254}}""",
    # verified 2026-10-16 against the FAO title page, https://www.fao.org/4/x0490e/x0490e00.htm
    "allen1998": r"""@book{allen1998, title={Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements}, series={FAO Irrigation and Drainage Paper}, number={56}, publisher={Food and Agriculture Organization of the United Nations}, address={Rome, Italy}, author={Allen, Richard G. and Pereira, Luis S. and Raes, Dirk and Smith, Martin}, year={1998}, isbn={92-5-104219-5}}""",
    "dwd2020": r"""@misc{dwd2020, title={Directive ({EU}) 2020/2184 of the {European} {Parliament} and of the {Council} of 16 December 2020 on the Quality of Water Intended for Human Consumption (Recast)}, howpublished={Official Journal of the European Union, L 435, 23 December 2020, pp. 1--62}, url={http://data.europa.eu/eli/dir/2020/2184/oj}, author={{European Parliament and Council of the European Union}}, year={2020}}""",
}


ACCENTS = {"\u0301": "'", "\u0300": "`", "\u0308": '"', "\u0302": "^", "\u0303": "~", "\u0304": "=",
           "\u0307": ".", "\u0306": "u", "\u030c": "v", "\u030b": "H", "\u0327": "c", "\u0328": "k",
           "\u030a": "r"}
SPECIAL = {"\u0131": r"{\i}", "\u0142": r"{\l}", "\u0141": r"{\L}", "\u00f8": r"{\o}", "\u00d8": r"{\O}",
           "\u00df": r"{\ss}", "\u00e6": r"{\ae}", "\u00c6": r"{\AE}", "\u0153": r"{\oe}", "\u0152": r"{\OE}",
           "\u00e5": r"{\aa}", "\u00c5": r"{\AA}", "\u2019": "'", "\u2018": "`", "\u201c": "``", "\u201d": "''",
           "\u2032": "'", "\u00a0": "~", "\u00ae": r"\textregistered{}", "\u00a9": r"\textcopyright{}",
           "\u2122": r"\texttrademark{}", "\u00d7": r"$\times$", "\u2212": "--", "\u2010": "-", "\u2011": "-"}


def to_latex(text):
    """Transliterate non-ASCII characters to LaTeX so BibTeX never splits a multi-byte character."""
    import unicodedata
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        elif ch in SPECIAL:
            out.append(SPECIAL[ch])
        else:
            d = unicodedata.normalize("NFD", ch)
            base, marks = d[0], d[1:]
            if len(marks) == 1 and marks in ACCENTS and ord(base) < 128:
                b = r"\i" if base == "i" else base
                cmd = ACCENTS[marks]
                out.append("{\\" + cmd + ("{" + b + "}" if cmd.isalpha() else b) + "}")
            else:
                raise ValueError(f"no LaTeX mapping for {ch!r} (U+{ord(ch):04X})")
    return "".join(out)


def clean(entry):
    e = html.unescape(entry)
    e = e.replace("\u2013", "--").replace("\u2014", "--")
    e = to_latex(e)
    e = re.sub(r",\s*ISSN=\{[^}]*\}", "", e)
    e = re.sub(r",\s*url=\{http://dx\.doi\.org/[^}]*\}", "", e)
    e = re.sub(r",\s*month=\w+", "", e)
    e = re.sub(r"\b(journal|publisher|booktitle)=\{([^}]*)&([^}]*)\}",
               lambda m: f"{m.group(1)}={{{m.group(2)}\\&{m.group(3)}}}", e)
    e = e.replace("PLOS One", "PLoS ONE").replace("Communications AI \\& Computing", "Communications AI \\& Computing")
    return e


def main():
    # cited keys come from the manuscript and from generated table bodies (Appendix A cites sources)
    tex = TEX.read_text(encoding="utf-8") + (TEX.parent / "tabledefs.tex").read_text(encoding="utf-8")
    keys = []
    for grp in re.findall(r"\\cite[pt]?\{([^}]*)\}", tex):
        for k in grp.split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
    lit = LIT.read_text(encoding="utf-8")
    ent = {}
    for e in re.split(r"\n(?=@)", lit.strip()):
        m = re.match(r"@\w+\{([^,]+),", e)
        if m:
            ent[m.group(1)] = e.strip()
    out, missing = [], []
    for k in keys:
        if k in EXTRA:
            out.append(EXTRA[k])
        elif k in ent:
            out.append(clean(ent[k]))
        else:
            missing.append(k)
    if missing:
        print("MISSING KEYS:", missing)
        sys.exit(1)
    OUT.write_text("\n\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(keys)} cited keys written to {OUT}")


if __name__ == "__main__":
    main()
