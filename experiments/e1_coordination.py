"""E1: coordination premium of fit-for-purpose allocation (RQ1).

Tasks are (city, year, parameter draw). Draw 0 is the nominal reference city,
draws 1..n are a Latin hypercube over E1_LHS_KEYS. Each task runs the potable-only
baseline, the eight factorial policies (pooling x integration x forecast) and the
perfect-foresight oracle on identical assets and weather.
"""
import itertools
import math
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import qmc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mawricx import allocation as A  # noqa: E402
from mawricx.city import build_city_year  # noqa: E402
from mawricx.config import (CITIES, E1_LHS_KEYS, E1_SWEEP_LEVELS, FORECAST, MASTER_SEED, P,  # noqa: E402
                            PERFECT_FORECAST, RESULTS, nominal_params)
from mawricx.weather import get_city_weather  # noqa: E402

CITY_LIST = list(CITIES)


def lhs_draws(n, seed=MASTER_SEED):
    """Draw 0 = nominal; draws 1..n from a scrambled Latin hypercube."""
    out = [nominal_params()]
    if n <= 0:
        return out
    sampler = qmc.LatinHypercube(d=len(E1_LHS_KEYS), seed=seed)
    u = sampler.random(n)
    for row in u:
        prm = nominal_params()
        for k, x in zip(E1_LHS_KEYS, row):
            prm[k] = P[k].low + x * (P[k].high - P[k].low)
        out.append(prm)
    return out


def task_seed(city, year, draw, salt=0):
    return np.random.SeedSequence([MASTER_SEED, CITY_LIST.index(city), year, draw, salt])


def run_task(args):
    city, year, draw, prm, mode = args
    w = get_city_weather(city)
    wy = w[w.index.year == year]
    wet = wy.P.values[wy.P.values >= FORECAST.wet_mm]
    if len(wet) == 0:
        wet = np.array([5.0])
    cy = build_city_year(w, year, prm, tropical=(city == "SIN"))
    rows = []
    base = A.baseline_summary(cy)
    base.update({"city": city, "year": year, "draw": draw, "mode": mode})
    rows.append(base)
    if mode == "factorial":
        policies = A.factorial_policies() + [A.Policy("MAWRICX_PF", True, True, True), A.ORACLE]
    else:  # sweep
        policies = [A.SILOED, A.Policy("P1I1F0", True, True, False), A.MAWRICX, A.ORACLE]
    for pol in policies:
        rng = np.random.default_rng(task_seed(city, year, draw, salt=zlib.crc32(pol.name.encode()) % 100003))
        t0 = time.time()
        fm = PERFECT_FORECAST if pol.name == "MAWRICX_PF" else FORECAST
        r = A.simulate_policy(cy, pol, wy, fm, rng, wet)
        r.update({"city": city, "year": year, "draw": draw, "mode": mode, "secs": time.time() - t0})
        if pol.name == "P0I0F0":
            r["policy"] = "SILOED"
        if pol.name == "P1I1F1":
            r["policy"] = "MAWRICX"
        rows.append(r)
    for r in rows:
        r["tert_frac"] = prm["tert_frac"]
        for k in E1_LHS_KEYS:
            r[f"prm_{k}"] = prm[k]
    return rows


def shapley(df):
    """Shapley attribution of the premium (SILOED minus policy) across P, I, F per task."""
    out = []
    mech = ["P", "I", "F"]
    for (city, year, draw), g in df[df["mode"] == "factorial"].groupby(["city", "year", "draw"]):
        pa = g.set_index("policy")["potable_adj"]
        name = lambda s: "P%dI%dF%d" % tuple(int(m in s) for m in mech)  # noqa: E731
        lookup = {"P0I0F0": pa["SILOED"], "P1I1F1": pa["MAWRICX"]}
        for k in pa.index:
            if k.startswith("P") and len(k) == 6:
                lookup[k] = pa[k]
        v = lambda s: lookup["P0I0F0"] - lookup[name(s)]  # noqa: E731
        row = {"city": city, "year": year, "draw": draw, "total": v(set(mech))}
        n = len(mech)
        for m in mech:
            phi = 0.0
            others = [x for x in mech if x != m]
            for r in range(len(others) + 1):
                for S in itertools.combinations(others, r):
                    wgt = math.factorial(len(S)) * math.factorial(n - len(S) - 1) / math.factorial(n)
                    phi += wgt * (v(set(S) | {m}) - v(set(S)))
            row[m] = phi
        out.append(row)
    return pd.DataFrame(out)


def main(scale):
    RESULTS.mkdir(exist_ok=True)
    draws = lhs_draws(scale.draws)
    tasks = []
    for city in scale.cities:
        years = CITIES[city][4][: scale.years_per_city]
        for year in years:
            for d, prm in enumerate(draws):
                tasks.append((city, year, d, prm, "factorial"))
            if scale.sweep:
                for lvl in E1_SWEEP_LEVELS:
                    prm = nominal_params()
                    prm["tert_frac"] = lvl
                    tasks.append((city, year, 100 + E1_SWEEP_LEVELS.index(lvl), prm, "sweep"))
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=scale.workers) as ex:
        for i, res in enumerate(ex.map(run_task, tasks, chunksize=2)):
            rows.extend(res)
            if (i + 1) % 25 == 0 or i + 1 == len(tasks):
                print(f"  E1 {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    tag = scale.name
    df.to_csv(RESULTS / f"e1_runs_{tag}.csv", index=False)
    sh = shapley(df)
    sh.to_csv(RESULTS / f"e1_shapley_{tag}.csv", index=False)
    print(f"E1 done: {len(tasks)} tasks, {len(df)} rows in {time.time() - t0:.0f}s")
    return df, sh


if __name__ == "__main__":
    from mawricx.config import FULL, SMOKE
    main(SMOKE if "--smoke" in sys.argv else FULL)
