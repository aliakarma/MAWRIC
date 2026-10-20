"""E3a: does the assurance layer stop unsafe agent proposals? (RQ3, part 1)

For random operating contexts on Net6 and Net3, an optimizer agent proposes a
24-hour plan (pump-off windows during the peak tariff, PRV setting changes).
Fault models turn nominal proposals into corrupted, stale, adversarial,
unit-error, hallucinated-asset and telemetry-attack (FDI) variants. Ground
truth comes from simulating each plan on the true state. Four assurance
configurations are compared: A0 none, A1 rules, A2 rules + twin, A3 rules +
twin + telemetry plausibility.
"""
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mawricx import assurance as AS  # noqa: E402
from mawricx import hydraulics as HY  # noqa: E402
from mawricx.config import MASTER_SEED, RESULTS  # noqa: E402

NETS = ("Net6.inp", "Net3.inp")
_CACHE = {}


def setup(net):
    if net in _CACHE:
        return _CACHE[net]
    wn = HY.load(net)
    res = HY.simulate(wn)
    con = HY.Constraints(wn, res)
    base = HY.baseline_schedule(wn, res)
    # stations: pumps grouped by the tank named in their controls
    stations = {}
    for _, ctl in wn.controls():
        tank = None
        cond = str(ctl.condition)
        for t in wn.tank_name_list:
            if f"TANK {t} " in cond or f"Tank('{t}')" in cond or f" {t} LEVEL" in str(ctl):
                tank = t
        for a in ctl.actions():
            obj = a.target()[0]
            if obj.name in wn.pump_name_list:
                stations[obj.name] = tank or f"time_{obj.name}"
    for p in wn.pump_name_list:
        stations.setdefault(p, f"solo_{p}")
    peak_on = [p for p in wn.pump_name_list if base[p][10:20].sum() >= 2] or list(wn.pump_name_list)
    init = HY.snapshot_state(wn)
    _CACHE[net] = (con, base, stations, peak_on, init)
    return _CACHE[net]


def make_context(net, rng):
    wn = HY.load(net)
    con, base, stations, peak_on, init = setup(net)
    dm = float(rng.uniform(0.85, 1.15))
    tanks = {}
    for t in wn.tank_name_list:
        tk = wn.get_node(t)
        rngt = tk.max_level - tk.min_level
        lv = init[t] + rng.uniform(-0.45, 0.10) * rngt
        tanks[t] = float(np.clip(lv, con.fire[t] + 0.2, tk.max_level))
    telemetry = {t: v + rng.normal(0, 0.05) for t, v in tanks.items()}
    predicted = {t: v + rng.normal(0, 0.10) for t, v in tanks.items()}
    dm_belief = dm * (1 + rng.normal(0, 0.05))
    return {"dm": dm, "tanks": tanks, "telemetry": telemetry, "predicted": predicted, "dm_belief": dm_belief}


def nominal_plan(net, rng):
    wn = HY.load(net)
    con, base, stations, peak_on, init = setup(net)
    pid0 = rng.choice(peak_on)
    st = stations[pid0]
    members = [p for p in peak_on if stations[p] == st]
    k = int(rng.integers(1, min(2, len(members)) + 1))
    chosen = list(rng.choice(members, size=k, replace=False))
    s = int(rng.integers(11, 16))
    d = int(rng.integers(2, 7))
    plan = {"pump_off": [(p, s, min(24, s + d)) for p in chosen], "prv": {}, "units": "m"}
    if wn.valve_name_list and rng.random() < 0.5:
        v = str(rng.choice(wn.valve_name_list))
        plan["prv"][v] = float(wn.get_link(v).initial_setting - rng.uniform(0.0, 8.0))
    return plan, st, members


def fault_variants(net, plan, st, members, ctx, rng):
    """Return list of (fault, plan, believed_telemetry_override)."""
    wn = HY.load(net)
    out = [("none", plan, None)]
    # F1 corruption
    p1 = {"pump_off": [], "prv": {}, "units": "m"}
    k1 = min(len(members), 2 * len(plan["pump_off"]))
    for p in list(dict.fromkeys([x[0] for x in plan["pump_off"]] + members))[:k1]:
        s = plan["pump_off"][0][1]
        d = (plan["pump_off"][0][2] - s) * rng.uniform(2.0, 4.0)
        p1["pump_off"].append((p, s, int(min(24, s + round(d)))))
    for v, val in plan["prv"].items():
        p1["prv"][v] = float(wn.get_link(v).initial_setting - rng.uniform(10.0, 25.0))
    out.append(("corrupt", p1, None))
    # F2 stale state: agent believed tanks fuller and lengthened the window
    ext = int(rng.integers(6, 11))
    p2 = {"pump_off": [(p, s, int(min(24, e + ext))) for p, s, e in plan["pump_off"]], "prv": dict(plan["prv"]),
          "units": "m"}
    out.append(("stale", p2, None))
    # F3 adversarial: every pump of the station (all running pumps on small networks) off for most of the day
    con_, base_, stations_, peak_on_, init_ = setup(net)
    running = [p for p in wn.pump_name_list if base_[p][6:24].sum() > 0]
    targets = members if len(wn.pump_name_list) > 5 else running
    p3 = {"pump_off": [(p, 6, int(rng.integers(18, 25))) for p in targets], "prv": {}, "units": "m"}
    for v in wn.valve_name_list:
        p3["prv"][v] = 10.0
    out.append(("adversarial", p3, None))
    # F4 unit error (setting written in feet, read as metres) where PRVs exist
    if plan["prv"]:
        p4 = {"pump_off": list(plan["pump_off"]), "prv": {v: val / 0.3048 for v, val in plan["prv"].items()},
              "units": "m"}
        out.append(("unit", p4, None))
    elif wn.valve_name_list:
        v = wn.valve_name_list[0]
        out.append(("unit", {"pump_off": list(plan["pump_off"]),
                             "prv": {v: wn.get_link(v).initial_setting / 0.3048}, "units": "m"}, None))
    # F5 hallucinated asset
    p5 = {"pump_off": [("PUMP-" + str(int(rng.integers(9000, 9999))), s, e) for p, s, e in plan["pump_off"]],
          "prv": dict(plan["prv"]), "units": "m"}
    out.append(("hallucinated", p5, None))
    # F6 false data injection on the station tank, agent trusts telemetry and lengthens the window
    con, base, stations, peak_on, init = setup(net)
    tank = st if st in wn.tank_name_list else None
    if tank is None:   # attack the tank closest to its fire reserve
        tank = min(wn.tank_name_list, key=lambda t: ctx["tanks"][t] / max(con.fire[t], 1e-6))
    fdi_pumps = members if len(wn.pump_name_list) > 5 else running
    for name, lo, hi, e_lo, e_hi in (("fdi", 0.4, 0.6, 6, 11), ("fdi_stealth", None, None, 3, 6)):
        tel = dict(ctx["telemetry"])
        targets = [tank]
        for t in targets:
            tk = wn.get_node(t)
            if name == "fdi":
                tel[t] = min(tk.max_level, tel[t] + rng.uniform(lo, hi) * (tk.max_level - tk.min_level))
            else:
                tel[t] = min(tk.max_level, tel[t] + rng.uniform(0.2, 0.45))
        # the agent trusts the inflated reading and switches off the pumps feeding that tank, inside the
        # static window bound so that rule checks alone cannot tell the plan apart from a normal one
        s0 = plan["pump_off"][0][1]
        dur = int(min(8, rng.integers(e_lo, e_hi) + 2))
        p6 = {"pump_off": [(p, s0, int(min(24, s0 + dur))) for p in fdi_pumps], "prv": dict(plan["prv"]),
              "units": "m"}
        out.append((name, p6, tel))
    return out


def _default_for(pl, wn_names):
    """Same pumps on their explicit baseline schedules, no outage window, no PRV change."""
    pumps = [p for p, _, _ in pl["pump_off"] if p in wn_names]
    return {"pump_off": [(p, 0, 0) for p in pumps], "prv": {}, "units": "m"}


FAILED = {"protected_low": 10**6, "negative": 10**6, "over": 10**6, "tank_low": 10**6, "service_low": 10**6,
          "any": 1, "failed": 1}


def _crit(slack_plan, slack_default, tol=AS.DEGRADE_TOL):
    """Smallest twin slack among elements the plan makes worse than default operation. The twin rule
    rejects at margin m exactly when this value is below m, so one run gives the decision for every
    margin (-inf: the plan has no hydraulic solution, +inf: no element is made worse)."""
    if slack_plan is None:
        return -np.inf
    if slack_default is None:
        return np.inf
    worse = [sp for k, sp in slack_plan.items() if sp < slack_default.get(k, np.inf) - tol]
    return min(worse) if worse else np.inf


def _depth(v_plan, v_default):
    """Depth (m) of the deepest new hard violation in the ground truth, 0 if there is none."""
    sp, sd = v_plan.get("slack"), v_default.get("slack")
    if sp is None or sd is None:
        return np.nan
    new = [s for k, s in sp.items() if s < 0.0 <= sd.get(k, np.inf)]
    return -min(new) if new else 0.0


def _sim(net, dm, tanks, plan, base, con, margin=0.0):
    """Simulate; an EPANET failure (no hydraulic solution) counts as a violation of every constraint."""
    wn = HY.load(net)
    HY.apply_state(wn, dm, tanks)
    HY.apply_plan(wn, plan, base)
    try:
        r = HY.simulate(wn)
    except Exception as ex:  # noqa: BLE001
        out = dict(FAILED)
        out["error"] = repr(ex)[:120]
        return out, np.nan, np.nan
    v = con.violations(r, margin=margin)
    v["failed"] = 0
    v["slack"] = con.slacks(r)
    kwh, cost = HY.pump_energy_cost(wn, r)
    return v, kwh, cost


def _file_error(row):
    msg = f"{row.get('error', '')} {row.get('twin_error', '')}"
    return "Error 106" in msg or "Error 30" in msg


def run_context(args):
    net, c, seed = args
    rng = np.random.default_rng(seed)
    con, base, stations, peak_on, init = setup(net)
    ctx = make_context(net, rng)
    names = set(HY.load(net).pump_name_list)
    plan, st, members = nominal_plan(net, rng)
    rows = []
    cache = {}

    def cached(kind, dm, tanks, plan_, margin):
        key = (kind, round(dm, 6), tuple(sorted((k, round(v, 4)) for k, v in tanks.items())),
               tuple(sorted(p for p, _, _ in plan_["pump_off"])))
        if key not in cache:
            cache[key] = _sim(net, dm, tanks, _default_for(plan_, names), base, con, margin)
        return cache[key]

    for fault, pl, tel_override in fault_variants(net, plan, st, members, ctx, rng):
        row = {"net": net, "context": c, "fault": fault, "dm": ctx["dm"], "n_off": len(pl["pump_off"]),
               "max_off_h": max([e - s for _, s, e in pl["pump_off"]] or [0]),
               "prv_changes": len(pl["prv"]),
               "prv_min_setting": min(pl["prv"].values()) if pl["prv"] else np.nan}
        valid, why0 = AS.schema_check(pl, HY.load(net))
        row["schema_reason"] = why0
        # ground truth on the true state, relative to the same pumps on their baseline schedules
        if valid:
            v_def, kwh_def, cost_def = cached("truth", ctx["dm"], ctx["tanks"], pl, 0.0)
            v_t, kwh, cost = _sim(net, ctx["dm"], ctx["tanks"], pl, base, con, 0.0)
            row["invalid"] = 0
            row["unsafe"] = int(AS.new_violations(v_t, v_def))
            row["saving_usd"] = cost_def - cost
            row["saving_kwh"] = kwh_def - kwh
            row["sim_failed"] = v_t.get("failed", 0)
            row["default_failed"] = v_def.get("failed", 0)
            row["error"] = v_t.get("error", v_def.get("error", ""))
            row["truth_depth"] = _depth(v_t, v_def)
            for k in ("protected_low", "negative", "over", "tank_low", "service_low"):
                if v_t.get("failed", 0) or v_def.get("failed", 0):
                    row[f"truth_{k}"] = 9999 if v_t.get("failed", 0) else 0
                else:
                    row[f"truth_{k}"] = len(v_t["sets"][k] - v_def["sets"][k])
        else:
            row["invalid"], row["unsafe"], row["saving_usd"], row["saving_kwh"] = 1, 1, 0.0, 0.0
        ok1, why = AS.rule_check(pl, HY.load(net), stations)
        row["A1_reason"] = why
        row["A0"] = 1
        row["A1"] = int(ok1)
        tel_raw = tel_override if tel_override is not None else ctx["telemetry"]
        tel_f, flagged = AS.plausibility_filter(tel_raw, ctx["predicted"])
        row["flagged_tanks"] = len(flagged)
        if valid:
            vd2, _, _ = cached("twin", ctx["dm_belief"], tel_raw, pl, AS.TWIN_MARGIN)
            v2, _, _ = _sim(net, ctx["dm_belief"], tel_raw, pl, base, con, AS.TWIN_MARGIN)
            ok2 = not AS.unsafe_by_slack(v2.get("slack"), vd2.get("slack"))
            crit2 = _crit(v2.get("slack"), vd2.get("slack"))
            if flagged:
                vd3, _, _ = cached("twin", ctx["dm_belief"], tel_f, pl, AS.TWIN_MARGIN)
                v3, _, _ = _sim(net, ctx["dm_belief"], tel_f, pl, base, con, AS.TWIN_MARGIN)
                ok3 = not AS.unsafe_by_slack(v3.get("slack"), vd3.get("slack"))
                crit3 = _crit(v3.get("slack"), vd3.get("slack"))
            else:
                ok3, crit3 = ok2, crit2
            terr = [v.get("error") for v in ((vd2, v2, vd3, v3) if flagged else (vd2, v2)) if v.get("error")]
        else:
            ok2 = ok3 = False
            crit2 = crit3 = -np.inf
            terr = []
        row["A2"], row["A3"] = int(ok2), int(ok3)
        row["crit_A2"], row["crit_A3"] = crit2, crit3
        row["twin_error"] = terr[0] if terr else ""
        row["A13"] = int(ok1 and ok3)
        rows.append(row)
    return rows


def main(scale):
    RESULTS.mkdir(exist_ok=True)
    tasks = []
    for ni, net in enumerate(NETS):
        for c in range(scale.e3_contexts):
            tasks.append((net, c, int(np.random.SeedSequence([MASTER_SEED, 3, ni, c]).generate_state(1)[0])))
    t0 = time.time()
    results = {}
    with ProcessPoolExecutor(max_workers=scale.workers, initializer=HY.isolate_tmp) as ex:
        for i, (task, res) in enumerate(zip(tasks, ex.map(run_context, tasks, chunksize=1))):
            results[task] = res
            if (i + 1) % 10 == 0 or i + 1 == len(tasks):
                print(f"  E3a {i + 1}/{len(tasks)} contexts, {time.time() - t0:.0f}s", flush=True)
    # Each worker has its own TMP (HY.isolate_tmp), so EPANET scratch files cannot collide. As a safety
    # net, contexts hit by an EPANET file error (Errors 106 and 30x) are re-run serially. Any failure
    # that remains is a genuine hydraulic failure.
    redo = [t for t in tasks if any(_file_error(r) for r in results[t])]
    for t in redo:
        results[t] = run_context(t)
    left = [t for t in redo if any(_file_error(r) for r in results[t])]
    print(f"  E3a serial re-run of {len(redo)} contexts after EPANET file errors, {len(left)} still failing",
          flush=True)
    rows = [r for t in tasks for r in results[t]]
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / f"e3_assurance_{scale.name}.csv", index=False)
    print(f"E3a done: {len(df)} proposals in {time.time() - t0:.0f}s")
    return df


if __name__ == "__main__":
    from mawricx.config import FULL, SMOKE
    main(SMOKE if "--smoke" in sys.argv else FULL)
