"""E3b: leak response under autonomy levels, approval latency and robot verification (RQ3, part 2).

Hydraulic grounding (Net6, WNTR): pipe lengths, nodal pressures (burst flow scales
with pressure through an N1 exponent), isolation-valve segments (strategic N-2
valve layer), the demand cut by isolating each segment, and segments that serve
protected customers. A discrete-event model then simulates one year of burst and
false alarms for each governance policy with the same random event stream.

Policies
  HUMAN    every dispatch and isolation waits for operator approval (L1/L2).
  AUTO     immediate crew dispatch and isolation for every alarm above 0.3, no approval, no robots.
  MAWRICX  automatic crew dispatch for alarms >= 0.6 ranked by expected loss, robot verification for
           0.3-0.6, operator approval only before isolating a segment that serves protected customers.
Detector, latency, crew and robot parameters are declared and varied in a sensitivity sweep.
"""
import heapq
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import wntr

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mawricx import hydraulics as HY  # noqa: E402
from mawricx.config import MASTER_SEED, RESULTS  # noqa: E402

NOMINAL = dict(
    burst_rate_km=0.10,      # bursts per km per year (declared)
    q_median_ls=2.0,         # burst flow at 50 m (L/s), lognormal median (declared)
    q_sigma=0.9,
    n1_low=0.5, n1_high=1.5,  # pressure-leakage exponent range (van Zyl and Clayton 2007, van Zyl and Cassa 2014)
    detect_median_h=4.0,     # awareness delay median for a 2 L/s burst (declared)
    false_per_week=1.5,      # false alarms per week (declared)
    loc_correct=0.75,        # alarm points to the right segment (declared)
    approve_day_h=0.5, approve_night_h=2.0, approve_sigma=0.6,   # operator approval latency (declared)
    robot_h=1.5, robot_sigma=0.4, robots=2, robot_acc=0.95,     # robot verification (declared)
    crews=3, travel_h=1.0, valve_h=0.5, repair_h=6.0, repair_sigma=0.5, search_h=2.0, inspect_h=1.0,
    conf_dispatch=0.3, conf_auto=0.6,
)
SWEEP = {
    "approve_day_h": [0.25, 0.5, 1.0, 2.0, 4.0],
    "false_per_week": [0.5, 1.5, 3.0, 5.0],
    "crews": [2, 3, 5],
    "robots": [0, 1, 2, 4],
    "q_median_ls": [1.0, 2.0, 4.0, 8.0],   # added at revision: does the envelope advantage hold for large bursts?
}
POLICIES = ("HUMAN", "AUTO", "MAWRICX")
REALARM_H = 24.0      # an unresolved true burst raises a new alarm after this many hours
REALARM_STEP = 0.25   # confidence gain of each repeated alarm
_NET = {}


def network():
    if _NET:
        return _NET
    wn = HY.load("Net6.inp")
    res = HY.simulate(wn)
    con = HY.Constraints(wn, res)
    pipes = wn.pipe_name_list
    length = np.array([wn.get_link(p).length for p in pipes]) / 1000.0
    pmean = res.node["pressure"].mean()
    p_pipe = np.array([max(1.0, 0.5 * (pmean.get(wn.get_link(p).start_node_name, 30.0) +
                                       pmean.get(wn.get_link(p).end_node_name, 30.0))) for p in pipes])
    vl = wntr.network.generate_valve_layer(wn, "strategic", 2, seed=MASTER_SEED % 100000)
    G = wn.to_graph()
    node_seg, link_seg, _ = wntr.metrics.valve_segments(G, vl)
    seg_of_pipe = np.array([int(link_seg[p]) for p in pipes])
    # demand cut by isolating each segment: nodes of the segment plus nodes cut off from all sources
    uG = G.to_undirected()
    sources = set(wn.reservoir_name_list) | set(wn.tank_name_list)
    base_dem = {j: (wn.get_node(j).demand_timeseries_list[0].base_value
                    if wn.get_node(j).demand_timeseries_list else 0.0) for j in wn.junction_name_list}
    protected = set(con.protected)
    seg_nodes = {}
    for n, s in node_seg.items():
        seg_nodes.setdefault(int(s), []).append(n)
    seg_links = {}
    for l, s in link_seg.items():
        seg_links.setdefault(int(s), []).append(l)
    cut_dem, cut_prot = {}, {}
    for s in np.unique(seg_of_pipe):
        H = uG.copy()
        H.remove_nodes_from([n for n in seg_nodes.get(s, []) if n not in sources])
        reach = set()
        for comp in nx.connected_components(H):
            if comp & sources:
                reach |= comp
        lost = [j for j in wn.junction_name_list if j not in reach]
        cut_dem[s] = float(sum(base_dem[j] for j in lost))          # m3/s
        cut_prot[s] = int(any(j in protected for j in lost))
    # adjacency of segments (for wrong-location alarms)
    seg_adj = {}
    for l, s in link_seg.items():
        lk = wn.get_link(l)
        for nd in (lk.start_node_name, lk.end_node_name):
            if nd in node_seg:
                seg_adj.setdefault(int(s), set()).add(int(node_seg[nd]))
    _NET.update(dict(pipes=pipes, length=length, p_pipe=p_pipe, seg=seg_of_pipe, cut_dem=cut_dem,
                     cut_prot=cut_prot, seg_adj=seg_adj, total_km=float(length.sum()),
                     n_valves=len(vl), n_segments=len(cut_dem)))
    return _NET


def make_events(prm, rng):
    net = network()
    n_b = rng.poisson(prm["burst_rate_km"] * net["total_km"])
    idx = rng.choice(len(net["pipes"]), size=n_b, p=net["length"] / net["length"].sum())
    t0 = rng.uniform(0, 8760, n_b)
    n1 = rng.uniform(prm["n1_low"], prm["n1_high"], n_b)
    q = prm["q_median_ls"] * np.exp(rng.normal(0, prm["q_sigma"], n_b)) * (net["p_pipe"][idx] / 50.0) ** n1
    delay = prm["detect_median_h"] * np.sqrt(2.0 / np.maximum(q, 0.05)) * np.exp(rng.normal(0, 0.7, n_b))
    delay = np.minimum(delay, 24 * 14)
    conf = rng.beta(4, 2, n_b)
    seg_true = net["seg"][idx]
    correct = rng.random(n_b) < prm["loc_correct"]
    seg_alarm = np.array([s if c else int(rng.choice(sorted(net["seg_adj"].get(s, {s})))) for s, c in zip(seg_true, correct)])
    ev = [dict(kind="burst", t_start=t0[k], t_alarm=t0[k] + delay[k], q=q[k], conf=conf[k], seg=int(seg_alarm[k]),
               seg_true=int(seg_true[k]), correct=bool(correct[k] or seg_alarm[k] == seg_true[k])) for k in range(n_b)]
    n_f = rng.poisson(prm["false_per_week"] * 52.14)
    fidx = rng.choice(len(net["pipes"]), size=n_f, p=net["length"] / net["length"].sum())
    for k in range(n_f):
        ev.append(dict(kind="false", t_start=np.nan, t_alarm=rng.uniform(0, 8760), q=0.0, conf=rng.beta(2, 4),
                       seg=int(net["seg"][fidx[k]]), seg_true=-1, correct=False))
    ev.sort(key=lambda e: e["t_alarm"])
    # pre-draw stochastic durations so every policy sees the same ones
    for e in ev:
        e["u_approve"] = rng.normal(0, prm["approve_sigma"])
        e["d_robot"] = prm["robot_h"] * np.exp(rng.normal(0, prm["robot_sigma"]))
        e["robot_ok"] = rng.random() < prm["robot_acc"]
        e["d_travel"] = prm["travel_h"] * np.exp(rng.normal(0, 0.3))
        e["d_repair"] = prm["repair_h"] * np.exp(rng.normal(0, prm["repair_sigma"]))
    return ev


def approval_delay(prm, t, u):
    hour = t % 24
    med = prm["approve_night_h"] if (hour >= 22 or hour < 7) else prm["approve_day_h"]
    return med * np.exp(u)


def simulate(policy, prm, events):
    """Discrete-event simulation with limited crews and robots. Returns yearly metrics."""
    net = network()
    crews = [0.0] * int(prm["crews"])     # time each crew becomes free
    robots = [0.0] * int(prm["robots"])
    approvals = 0
    lost_m3 = 0.0
    t_isolate = []
    crew_false_h = 0.0
    prot_unapproved = 0
    cust_hours = 0.0                     # demand-weighted hours of supply interruption (m3 not delivered)
    jobs = []                            # (ready_time, priority, k, verified)
    alarms = [(e["t_alarm"], k, e["conf"]) for k, e in enumerate(events)]
    heapq.heapify(alarms)
    while alarms:
        t_al, k, conf = heapq.heappop(alarms)
        e = events[k]
        if conf < prm["conf_dispatch"]:
            if e["kind"] == "burst":     # dismissed: a persistent anomaly alarms again a day later
                heapq.heappush(alarms, (t_al + REALARM_H, k, min(1.0, conf + REALARM_STEP)))
            continue
        ready = t_al
        verified = None
        if policy == "HUMAN":
            approvals += 1
            ready += approval_delay(prm, t_al, e["u_approve"])
        elif policy == "MAWRICX" and conf < prm["conf_auto"] and robots:
            i = int(np.argmin(robots))
            start = max(ready, robots[i])
            robots[i] = start + e["d_robot"]
            ready = robots[i]
            verified = (e["kind"] == "burst") if e["robot_ok"] else (e["kind"] != "burst")
            if not verified:
                if e["kind"] == "burst":   # missed by the robot: the anomaly persists and alarms again
                    heapq.heappush(alarms, (ready + REALARM_H, k, min(1.0, conf + REALARM_STEP)))
                continue
        prio = -(e["q"] if e["kind"] == "burst" else 0.0) * conf
        heapq.heappush(jobs, (ready, prio if policy == "MAWRICX" else ready, k, verified))
    # crews serve jobs in order of readiness (and priority for MAWRICX among ready jobs)
    pending = sorted(jobs, key=lambda j: j[0])
    queue = []
    i = 0
    while i < len(pending) or queue:
        tfree = min(crews)
        while i < len(pending) and (pending[i][0] <= tfree or not queue):
            heapq.heappush(queue, (pending[i][1], pending[i][0], pending[i][2], pending[i][3]))
            i += 1
        prio, ready, k, verified = heapq.heappop(queue)
        e = events[k]
        c = int(np.argmin(crews))
        start = max(crews[c], ready)
        arrive = start + e["d_travel"]
        if e["kind"] == "false":
            crews[c] = arrive + prm["inspect_h"]
            crew_false_h += crews[c] - start
            continue
        found = arrive + (0.0 if e["correct"] or verified else prm["search_h"])
        iso = found + prm["valve_h"]
        seg = e["seg_true"]
        if net["cut_prot"].get(seg, 0):
            if policy == "MAWRICX":
                approvals += 1
                iso += approval_delay(prm, found, e["u_approve"])
            elif policy == "AUTO":
                prot_unapproved += 1
        lost_m3 += e["q"] * 3.6 * (iso - e["t_start"])
        t_isolate.append(iso - e["t_start"])
        done = iso + e["d_repair"]
        cust_hours += net["cut_dem"].get(seg, 0.0) * 3600 * (done - iso)
        crews[c] = done
    return {"lost_m3": lost_m3, "mean_t_isolate_h": float(np.mean(t_isolate)) if t_isolate else 0.0,
            "p90_t_isolate_h": float(np.percentile(t_isolate, 90)) if t_isolate else 0.0,
            "approvals": approvals, "crew_false_h": crew_false_h, "prot_unapproved": prot_unapproved,
            "undelivered_m3": cust_hours, "n_bursts": sum(e["kind"] == "burst" for e in events),
            "n_false": sum(e["kind"] == "false" for e in events)}


def run_year(args):
    case, val, prm, year, seed = args
    rng = np.random.default_rng(seed)
    events = make_events(prm, rng)
    rows = []
    for pol in POLICIES:
        r = simulate(pol, prm, events)
        r.update({"case": case, "value": val, "year": year, "policy": pol})
        rows.append(r)
    return rows


def main(scale):
    RESULTS.mkdir(exist_ok=True)
    net = network()
    print(f"Net6: {net['total_km']:.1f} km, {net['n_valves']} valves, {net['n_segments']} segments")
    tasks = []
    for y in range(scale.e3b_years):
        tasks.append(("nominal", 0, dict(NOMINAL), y, int(np.random.SeedSequence([MASTER_SEED, 31, y]).generate_state(1)[0])))
    n_sweep = max(2, scale.e3b_years // 4)
    for key, vals in SWEEP.items():
        for v in vals:
            prm = dict(NOMINAL)
            prm[key] = v
            if key == "approve_day_h":
                prm["approve_night_h"] = 4 * v
            for y in range(n_sweep):
                tasks.append((key, v, prm, y, int(np.random.SeedSequence([MASTER_SEED, 32, y]).generate_state(1)[0])))
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=scale.workers, initializer=HY.isolate_tmp) as ex:
        for res in ex.map(run_year, tasks, chunksize=4):
            rows.extend(res)
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / f"e3b_leak_{scale.name}.csv", index=False)
    meta = pd.DataFrame([{k: v for k, v in net.items() if k in ("total_km", "n_valves", "n_segments")}])
    meta["protected_segments"] = sum(net["cut_prot"].values())
    meta.to_csv(RESULTS / f"e3b_network_{scale.name}.csv", index=False)
    print(f"E3b done: {len(df)} rows in {time.time() - t0:.0f}s")
    return df


if __name__ == "__main__":
    from mawricx.config import FULL, SMOKE
    main(SMOKE if "--smoke" in sys.argv else FULL)
