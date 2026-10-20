"""Download the GHCN-Daily station records used in the study and check them against SHA256SUMS.txt.

NOAA occasionally revises historical records, so a checksum mismatch means the station file changed
after 16 to 17 October 2026 (the retrieval dates of the files used in the paper), not that the download failed.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent / "raw" / "ghcn"
STATIONS = ["USW00023183", "USW00023174", "UKE00107650", "UKM00003772", "SNM00048698", "SA000040438", "SA000040430"]
URL = ("https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations={s}"
       "&startDate=2000-01-01&endDate=2025-12-31&dataTypes=PRCP,TMAX,TMIN&format=csv&units=metric"
       "&includeAttributes=false")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sums = {}
    sum_file = OUT / "SHA256SUMS.txt"
    if sum_file.exists():
        for line in sum_file.read_text().splitlines():
            h, name = line.split(maxsplit=1)
            sums[name.lstrip("*")] = h
    ok = True
    for s in STATIONS:
        name = f"{s}_2000_2025.csv"
        if "--force" in sys.argv or not (OUT / name).exists():
            with urllib.request.urlopen(URL.format(s=s), timeout=120) as r:
                (OUT / name).write_bytes(r.read())
        h = hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        match = sums.get(name) == h
        ok &= match
        print(f"{name}: {'checksum ok' if match else 'CHECKSUM DIFFERS'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
