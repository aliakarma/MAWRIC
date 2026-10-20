"""E2: fidelity, cost and robustness of the agent negotiation (RQ2).

For random days of the nominal reference city in each climate, the 7-day
allocation problem is solved (a) centrally by LP and (b) by ADMM negotiation in
which sectors keep their bounds private. A misreporting test inflates one
sector's declared eligible demand, with and without coordinator-side caps
derived from the sector's metered history.
"""
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mawricx import allocation as A  # noqa: E402
from mawricx.agents import admm_negotiate, horizon_value  # noqa: E402
from mawricx.city import build_city_year  # noqa: E402
from mawricx.config import CITIES, MASTER_SEED, RESULTS, SECTORS, nominal_params  # noqa: E402
from mawricx.weather import get_city_weather  # noqa: E402

H = 7
LIAR = "IND"
MISREPORT = (0.3, 0.6, 1.0)
CAP_MULT, CAP_Q, CAP_WIN = 1.1, 90, 28


def instance(cy, t, s0R, s0S):
    sl = slice(t, t + H)
    return {"ER": cy.ER[sl], "ES": cy.ES[sl], "EA": cy.EA[sl], "prodR": cy.prodR[sl], "capS": cy.capS[sl]}


def caps_for(cy, t):
    past = cy.EA[t - CAP_WIN:t]
    return CAP_MULT * np.percentile(past, CAP_Q, axis=0)


def run_city(args):
    city, year, ndays, seed = args
    w = get_city_weather(city)
    prm = nominal_params()
    cy = build_city_year(w, year, prm, tropical=(city == "SIN"))
    # storage states from the myopic coordinated trajectory
    n = len(cy.prodR)
    lp1 = A.AllocLP(1, True, True, prm["c_pot"], prm["c_rec"], prm["c_sto"])
    sR = np.zeros(n); sS = np.zeros(n)
    cR, cS = 0.5 * cy.SRmax, 0.5 * cy.SSmax
    for t in range(n):
        o = lp1.solve({"ER": cy.ER[t:t + 1], "ES": cy.ES[t:t + 1], "EA": cy.EA[t:t + 1],
                       "prodR": cy.prodR[t:t + 1], "capS": cy.capS[t:t + 1]}, cR, cS, cy.SRmax, cy.SSmax, cy.QR, cy.QS)
        cR, cS = o["sR"][0], o["sS"][0]
        sR[t], sS[t] = cR, cS
    rng = np.random.default_rng(seed)
    days = np.sort(rng.choice(np.arange(CAP_WIN + 1, n - H), size=ndays, replace=False))
    li = SECTORS.index(LIAR)
    lpH = A.AllocLP(H, True, True, prm["c_pot"], prm["c_rec"], prm["c_sto"])
    rows = []
    for t in days:
        s0R, s0S = sR[t - 1], sS[t - 1]
        data = instance(cy, t, s0R, s0S)
        t0 = time.time()
        lp = lpH.solve(data, s0R, s0S, cy.SRmax, cy.SSmax, cy.QR, cy.QS)
        t_lp = time.time() - t0
        obj_lp, _, uR_lp, uS_lp = horizon_value(lp["xR"], lp["xS"], data, s0R, s0S, cy.SRmax, cy.SSmax, prm, data["EA"])
        base = {"city": city, "year": year, "day": int(t), "obj_lp": obj_lp, "t_lp": t_lp,
                "supply_ratio": float((data["prodR"].sum() + data["capS"].sum() + s0R + s0S) / max(data["EA"].sum(), 1.0))}
        t0 = time.time()
        ad = admm_negotiate(data, s0R, s0S, cy.SRmax, cy.SSmax, cy.QR, cy.QS, prm)
        t_ad = time.time() - t0
        obj_ad, wasted, uR, uS = horizon_value(ad["xR"], ad["xS"], data, s0R, s0S, cy.SRmax, cy.SSmax, prm, data["EA"])
        honest_useful = (uR + uS).sum(axis=0)
        rows.append({**base, "case": "honest", "obj": obj_ad, "gap": (obj_ad - obj_lp) / abs(obj_lp) if obj_lp else 0.0,
                     "iters": ad["iters"], "messages": ad["messages"], "floats": ad["floats"], "t": t_ad,
                     "wasted": wasted, "liar_useful": honest_useful[li],
                     "others_useful": honest_useful.sum() - honest_useful[li],
                     "lp_useful": float((uR_lp + uS_lp).sum())})
        caps = caps_for(cy, t)
        for m in MISREPORT:
            dec = {"ER": data["ER"].copy(), "ES": data["ES"].copy(), "EA": data["EA"].copy()}
            for key in dec:
                dec[key][:, li] *= (1.0 + m)
            for capped in (False, True):
                t0 = time.time()
                adm = admm_negotiate(data, s0R, s0S, cy.SRmax, cy.SSmax, cy.QR, cy.QS, prm, declared=dec,
                                     caps=caps if capped else None)
                tm = time.time() - t0
                obj_m, wasted_m, uRm, uSm = horizon_value(adm["xR"], adm["xS"], data, s0R, s0S, cy.SRmax, cy.SSmax,
                                                          prm, data["EA"])
                useful = (uRm + uSm).sum(axis=0)
                delivered_liar = float((adm["xR"][:, li] + adm["xS"][:, li]).sum())
                rows.append({**base, "case": f"mis{int(m * 100)}{'_cap' if capped else ''}", "obj": obj_m,
                             "gap": (obj_m - obj_lp) / abs(obj_lp) if obj_lp else 0.0, "iters": adm["iters"],
                             "messages": adm["messages"], "floats": adm["floats"], "t": tm, "wasted": wasted_m,
                             "liar_useful": useful[li], "liar_delivered": delivered_liar,
                             "others_useful": useful.sum() - useful[li],
                             "lp_useful": float((uR_lp + uS_lp).sum())})
        # honest agents under caps only (cost of verification caps)
        adc = admm_negotiate(data, s0R, s0S, cy.SRmax, cy.SSmax, cy.QR, cy.QS, prm, caps=caps)
        obj_c, wasted_c, uRc, uSc = horizon_value(adc["xR"], adc["xS"], data, s0R, s0S, cy.SRmax, cy.SSmax, prm, data["EA"])
        usec = (uRc + uSc).sum(axis=0)
        rows.append({**base, "case": "honest_cap", "obj": obj_c, "gap": (obj_c - obj_lp) / abs(obj_lp) if obj_lp else 0.0,
                     "iters": adc["iters"], "messages": adc["messages"], "floats": adc["floats"], "t": 0.0,
                     "wasted": wasted_c, "liar_useful": usec[li], "others_useful": usec.sum() - usec[li],
                     "lp_useful": float((uR_lp + uS_lp).sum())})
    return rows


def main(scale):
    RESULTS.mkdir(exist_ok=True)
    tasks = []
    for ci, city in enumerate(scale.cities):
        years = CITIES[city][4]
        # spread the sampled days over three weather-years per city
        for yi, year in enumerate(years[:: max(1, len(years) // 3)][:3] if scale.name == "full" else years[:1]):
            nd = scale.e2_days_per_city // (3 if scale.name == "full" else 1)
            tasks.append((city, year, nd, int(np.random.SeedSequence([MASTER_SEED, 2, ci, yi]).generate_state(1)[0])))
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=scale.workers) as ex:
        for res in ex.map(run_city, tasks):
            rows.extend(res)
            print(f"  E2 {len(rows)} rows, {time.time() - t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / f"e2_negotiation_{scale.name}.csv", index=False)
    print(f"E2 done: {len(df)} rows in {time.time() - t0:.0f}s")
    return df


if __name__ == "__main__":
    from mawricx.config import FULL, SMOKE
    main(SMOKE if "--smoke" in sys.argv else FULL)
