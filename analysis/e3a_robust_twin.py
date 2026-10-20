"""Post hoc exploratory variant of the E3a twin check: an ensemble twin (A3e).

A3e accepts a proposal only if the twin rule (2 m margin) passes on the filtered state used by A3 and
on four perturbed states: believed demand times 1.05 and 0.95, and every tank estimate raised and
lowered by 0.10 m (the spread of the twin's demand belief and level prediction errors). A3e can only
reject more than A3, so only the schema-valid proposals that A3 accepted are re-simulated.
Writes results/e3a_robust_<tag>.csv. Usage: python analysis/e3a_robust_twin.py [--tag full]
"""
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import e3_assurance as E  # noqa: E402
from mawricx import assurance as AS  # noqa: E402
from mawricx import hydraulics as HY  # noqa: E402
from mawricx.config import MASTER_SEED, RESULTS  # noqa: E402

TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "full"
WORKERS = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
MEMBERS = ((1.05, 0.0), (0.95, 0.0), (1.0, 0.10), (1.0, -0.10))   # (demand factor, tank offset in m)


def run_context(args):
    net, c, seed, faults = args
    rng = np.random.default_rng(seed)
    con, base, stations, peak_on, init = E.setup(net)
    ctx = E.make_context(net, rng)          # same random stream as experiments/e3_assurance.py
    plan, st, members = E.nominal_plan(net, rng)
    names = set(HY.load(net).pump_name_list)
    cache, rows = {}, []
    for fault, pl, tel in E.fault_variants(net, plan, st, members, ctx, rng):
        if fault not in faults:
            continue
        tel_f, _ = AS.plausibility_filter(tel if tel is not None else ctx["telemetry"], ctx["predicted"])
        crit, errs = [], []
        for i, (fd, ft) in enumerate(MEMBERS):
            tanks = {t: v + ft for t, v in tel_f.items()}
            dm = ctx["dm_belief"] * fd
            key = (i, tuple(sorted(tanks.items())), tuple(sorted(p for p, _, _ in pl["pump_off"])))
            if key not in cache:
                cache[key] = E._sim(net, dm, tanks, E._default_for(pl, names), base, con)[0]
            vd = cache[key]
            vp = E._sim(net, dm, tanks, pl, base, con)[0]
            crit.append(E._crit(vp.get("slack"), vd.get("slack")))
            errs += [v.get("error") for v in (vd, vp) if v.get("error")]
        rows.append({"net": net, "context": c, "fault": fault, "crit_ens_min": min(crit),
                     **{f"crit_m{i}": v for i, v in enumerate(crit)}, "error": errs[0] if errs else ""})
    return rows


def main():
    e = pd.read_csv(RESULTS / f"e3_assurance_{TAG}.csv")
    acc = e[(e.invalid == 0) & (e.A3 == 1)]
    tasks = []
    for (net, c), g in acc.groupby(["net", "context"], sort=False):
        ni = E.NETS.index(net)
        seed = int(np.random.SeedSequence([MASTER_SEED, 3, ni, c]).generate_state(1)[0])
        tasks.append((net, int(c), seed, set(g.fault)))
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=HY.isolate_tmp) as ex:
        for i, res in enumerate(ex.map(run_context, tasks, chunksize=1)):
            rows.extend(res)
            if (i + 1) % 20 == 0 or i + 1 == len(tasks):
                print(f"  A3e {i + 1}/{len(tasks)} contexts, {time.time() - t0:.0f}s", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / f"e3a_robust_{TAG}.csv", index=False)
    print(f"A3e done: {len(out)} proposals re-checked in {time.time() - t0:.0f}s, "
          f"{int((out.error != '').sum())} with EPANET errors")


if __name__ == "__main__":
    main()
