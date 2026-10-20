"""Diagnose the unsafe E3a proposals that the twin (A3, 2 m margin) accepted.

For each such proposal the plan is simulated on the true state and on the twin's filtered state.
The script records the violated constraint types, the depth of the deepest new violation, the
hour it occurs, and whether any link (pipe, pump or valve) switched status at a different hour in
the twin than in the truth. Writes results/e3a_twin_misses_<tag>.csv.
Usage: python analysis/e3a_twin_misses.py [--tag full]
"""
import sys
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


def _run(net, dm, tanks, plan, base):
    wn = HY.load(net)
    HY.apply_state(wn, dm, tanks)
    HY.apply_plan(wn, plan, base)
    return HY.simulate(wn)


def main():
    HY.isolate_tmp()
    d = pd.read_csv(RESULTS / f"e3_assurance_{TAG}.csv")
    miss = d[(d.invalid == 0) & (d.unsafe == 1) & (d.A3 == 1)]
    rows = []
    for (net, c), g in miss.groupby(["net", "context"]):
        ni = E.NETS.index(net)
        seed = int(np.random.SeedSequence([MASTER_SEED, 3, ni, c]).generate_state(1)[0])
        rng = np.random.default_rng(seed)
        con, base, stations, peak_on, init = E.setup(net)
        ctx = E.make_context(net, rng)
        plan, st, members = E.nominal_plan(net, rng)
        names = set(HY.load(net).pump_name_list)
        for fault, pl, tel in E.fault_variants(net, plan, st, members, ctx, rng):
            if fault not in set(g.fault):
                continue
            tel_f, _ = AS.plausibility_filter(tel if tel is not None else ctx["telemetry"], ctx["predicted"])
            vt, _, _ = E._sim(net, ctx["dm"], ctx["tanks"], pl, base, con)
            vd, _, _ = E._sim(net, ctx["dm"], ctx["tanks"], E._default_for(pl, names), base, con)
            new = {k: s for k, s in vt["slack"].items() if s < 0.0 <= vd["slack"].get(k, np.inf)}
            r_true = _run(net, ctx["dm"], ctx["tanks"], pl, base)
            r_twin = _run(net, ctx["dm_belief"], tel_f, pl, base)
            s_true = r_true.link["status"].iloc[:25].astype(int)
            s_twin = r_twin.link["status"].iloc[:25].astype(int)
            switch_diff = int((s_true.values != s_twin.values).any())
            # hour of the deepest new violation in the truth
            k_worst = min(new, key=new.get) if new else None
            hour = np.nan
            if k_worst is not None:
                kind, elem = k_worst
                series = r_true.node["pressure"][elem].iloc[:25]
                hour = int(np.argmax(series.values) if kind == "over" else np.argmin(series.values))
            wn = HY.load(net)
            # a tank that the plan (not default operation) drives below its fire reserve and down to empty
            emptied = int(any(kind == "tank" and float(r_true.node["pressure"][t].iloc[:25].min())
                              <= wn.get_node(t).min_level + 0.05 for kind, t in new))
            rows.append({"net": net.replace(".inp", ""), "context": c, "fault": fault,
                         "types": ",".join(sorted({k[0] for k in new})), "depth": -min(new.values()) if new else 0.0,
                         "worst_hour": hour, "switch_differs": switch_diff, "tank_emptied": emptied,
                         "dm_error": ctx["dm_belief"] / ctx["dm"] - 1.0})
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / f"e3a_twin_misses_{TAG}.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
