"""Check that the parallel E3a run reproduces a serial run exactly.

Re-runs every k-th context of each network in a single process and compares every decision and
ground-truth column with results/e3_assurance_<tag>.csv. Writes results/e3a_serial_check_<tag>.csv.
Usage: python analysis/verify_e3a_serial.py [--tag full] [--every 6]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import e3_assurance as E  # noqa: E402
from mawricx import hydraulics as HY  # noqa: E402
from mawricx.config import MASTER_SEED, RESULTS  # noqa: E402

TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "full"
EVERY = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 6
# extra contexts to check on every network, e.g. those where two earlier parallel runs disagreed
EXTRA = ([int(c) for c in sys.argv[sys.argv.index("--contexts") + 1].split(",")]
         if "--contexts" in sys.argv else [])
EXACT = ["invalid", "unsafe", "A0", "A1", "A2", "A3", "A13", "flagged_tanks"]
CLOSE = ["saving_usd", "crit_A2", "crit_A3", "truth_depth"]


def main():
    HY.isolate_tmp()
    par = pd.read_csv(RESULTS / f"e3_assurance_{TAG}.csv")
    n_ctx = int(par.context.max()) + 1
    rows = []
    for ni, net in enumerate(E.NETS):
        for c in sorted(set(range(0, n_ctx, EVERY)) | {c for c in EXTRA if c < n_ctx}):
            seed = int(np.random.SeedSequence([MASTER_SEED, 3, ni, c]).generate_state(1)[0])
            rows.extend(E.run_context((net, c, seed)))
    ser = pd.DataFrame(rows)
    m = ser.merge(par, on=["net", "context", "fault"], suffixes=("_ser", "_par"))
    out = []
    for col in EXACT:
        diff = int((m[f"{col}_ser"] != m[f"{col}_par"]).sum())
        out.append({"column": col, "rows": len(m), "mismatches": diff})
    for col in CLOSE:
        a, b = m[f"{col}_ser"].to_numpy(float), m[f"{col}_par"].to_numpy(float)
        same = np.isclose(a, b, rtol=1e-9, atol=1e-9, equal_nan=True) | (np.isinf(a) & (a == b))
        out.append({"column": col, "rows": len(m), "mismatches": int((~same).sum())})
    res = pd.DataFrame(out)
    res.to_csv(RESULTS / f"e3a_serial_check_{TAG}.csv", index=False)
    print(res.to_string(index=False))
    print(f"contexts checked: {m.groupby('net').context.nunique().to_dict()}")
    sys.exit(0 if res.mismatches.sum() == 0 else 1)


if __name__ == "__main__":
    main()
