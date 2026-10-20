"""WNTR (EPANET 2.2) utilities for the governance experiments.

A plan is a dict:
  {"pump_off": [(pump_id, start_h, end_h), ...], "prv": {valve_id: setting_m}, "units": "m"}
The same functions simulate a plan on the true state (ground truth) and on the
twin's believed state (assurance check).
"""
import os
import tempfile
import time
import uuid

import numpy as np
import wntr
from wntr.network.controls import Control, ControlAction

NET_DIR = os.path.join(os.path.dirname(wntr.__file__), "library", "networks")
TOU = np.array([0.08] * 12 + [0.20] * 8 + [0.08] * 4)   # USD/kWh by hour: peak 12:00-20:00
P_MIN_PROTECTED = 20.0   # m
P_MIN_SERVICE = 14.0     # m, minimum service pressure for normally pressurized nodes
P_MAX = 100.0            # m
FIRE_FRAC = 0.30         # fire reserve as share of tank max level
MIN_HOURS = 1            # violation must last at least this many hourly steps


def load(name):
    wn = wntr.network.WaterNetworkModel(os.path.join(NET_DIR, name))
    wn.options.time.duration = 24 * 3600
    wn.options.time.hydraulic_timestep = 3600
    wn.options.time.report_timestep = 3600
    wn.options.time.pattern_timestep = 3600
    wn.options.time.quality_timestep = 3600
    return wn


def snapshot_state(wn):
    return {t: wn.get_node(t).init_level for t in wn.tank_name_list}


def apply_state(wn, demand_mult, tank_levels):
    wn.options.hydraulic.demand_multiplier = float(demand_mult)
    for t, lv in tank_levels.items():
        tk = wn.get_node(t)
        tk.init_level = float(np.clip(lv, tk.min_level, tk.max_level))


def set_schedule(wn, pid, sched):
    """Replace every control acting on the pump with an explicit 24-hour on/off schedule."""
    pump = wn.get_link(pid)
    for cname, ctl in list(wn.controls()):
        if any(a.target()[0] is pump for a in ctl.actions()):
            wn.remove_control(cname)
    prev = None
    for h, on in enumerate(sched):
        if on == prev:
            continue
        st = wntr.network.LinkStatus.Open if on else wntr.network.LinkStatus.Closed
        act = ControlAction(pump, "status", st)
        wn.add_control(f"sched_{pid}_{h}", Control._time_control(wn, h * 3600, "SIM_TIME", False, act))
        prev = on
    pump.initial_status = wntr.network.LinkStatus.Open if sched[0] else wntr.network.LinkStatus.Closed


def apply_plan(wn, plan, base_sched):
    """Apply a plan. pump_off windows are applied to the pump's baseline schedule.
    Raises KeyError for unknown assets (the caller decides what that means)."""
    for pid, s, e in plan.get("pump_off", []):
        wn.get_link(pid)  # KeyError if unknown
        sched = np.array(base_sched[pid]).copy()
        sched[int(max(0, s)):int(min(24, e))] = 0
        set_schedule(wn, pid, sched)
    units = plan.get("units", "m")
    for vid, setting in plan.get("prv", {}).items():
        v = wn.get_link(vid)
        val = float(setting)
        if units == "ft":
            val = val * 0.3048
        elif units == "psi":
            val = val * 0.70307
        v.initial_setting = val


def isolate_tmp():
    """Give this process its own temporary directory. Call it before the first simulation of a parallel
    worker (ProcessPoolExecutor initializer). EPANET 2.2 names its scratch hydraulics file with _tempnam,
    which yields the same names (en2, en5, ...) in every process and reads TMP only when the library is
    loaded, so workers that share TMP can overwrite each other's file without raising an error."""
    import atexit
    import shutil
    d = tempfile.mkdtemp(prefix=f"mx_w{os.getpid()}_")
    os.environ["TMP"] = d
    os.environ["TEMP"] = d
    tempfile.tempdir = d
    atexit.register(shutil.rmtree, d, True)


def _simulate_once(wn):
    d = tempfile.mkdtemp(prefix="mx_")
    prefix = os.path.join(d, "s" + uuid.uuid4().hex[:8])
    try:
        return wntr.sim.EpanetSimulator(wn).run_sim(file_prefix=prefix)
    finally:
        for ext in (".inp", ".rpt", ".bin", ".out"):
            try:
                os.remove(prefix + ext)
            except OSError:
                pass
        try:
            os.rmdir(d)
        except OSError:
            pass


def simulate(wn, retries=5):
    """EPANET run with retries: parallel runs on Windows occasionally fail on file access, so only a
    failure that repeats with fresh temporary files is treated as a genuine hydraulic failure. The
    random wait keeps colliding processes from retrying in lockstep."""
    last = None
    rng = np.random.default_rng()
    for _ in range(retries):
        try:
            return _simulate_once(wn)
        except Exception as ex:  # noqa: BLE001
            last = ex
            time.sleep(float(rng.uniform(0.1, 0.6)))
    raise last


def pump_energy_cost(wn, res):
    """Pump energy (kWh) and time-of-use cost (USD) over the first 24 hours."""
    e = wntr.metrics.pump_energy(res.link["flowrate"], res.node["head"], wn)[wn.pump_name_list].astype(float)
    e = e[e.index < 24 * 3600]
    kwh = e.values.sum(axis=1) / 3.6e6
    hours = (e.index.values // 3600).astype(int) % 24
    return float(kwh.sum()), float((kwh * TOU[hours]).sum())


def baseline_schedule(wn, res):
    flows = res.link["flowrate"]
    return {p: (flows[p].values[:24] > 1e-6).astype(int) for p in wn.pump_name_list}


class Constraints:
    """Network-specific constraint set derived from a nominal run."""

    def __init__(self, wn, nominal_res, n_protected=20):
        jn = wn.junction_name_list
        pr = nominal_res.node["pressure"][jn]
        base_dem = np.array([wn.get_node(j).demand_timeseries_list[0].base_value
                             if wn.get_node(j).demand_timeseries_list else 0.0 for j in jn])
        ok = (pr.min(axis=0).values >= P_MIN_PROTECTED + 5) & (base_dem > 0)
        cand = np.array(jn)[ok]
        order = np.argsort(-base_dem[ok])
        self.protected = list(cand[order[:n_protected]])
        self.watch = list(np.array(jn)[pr.min(axis=0).values >= 10.0])   # nodes that never run near zero
        self.service = list(np.array(jn)[pr.min(axis=0).values >= 20.0])  # nodes with normal service pressure
        self.pmax_ok = list(np.array(jn)[pr.max(axis=0).values < P_MAX])
        self.tanks = list(wn.tank_name_list)
        lv = nominal_res.node["pressure"][self.tanks]
        # fire reserve: 30% of the tank range, never above 90% of the nominal daily minimum
        self.fire = {t: min(FIRE_FRAC * wn.get_node(t).max_level, 0.9 * float(lv[t].min())) for t in self.tanks}

    def violations(self, res, margin=0.0):
        """Counts per constraint type plus the sets of violating nodes and tanks."""
        pr = res.node["pressure"]
        out, sets = {}, {}

        def flag(df, mask):
            hit = mask.sum(axis=0) >= MIN_HOURS
            return set(df.columns[hit.values])

        sets["protected_low"] = flag(pr[self.protected], pr[self.protected] < P_MIN_PROTECTED + margin)
        sets["negative"] = flag(pr[self.watch], pr[self.watch] < 0.0 + margin)
        sets["service_low"] = flag(pr[self.service], pr[self.service] < P_MIN_SERVICE + margin)
        sets["over"] = flag(pr[self.pmax_ok], pr[self.pmax_ok] > P_MAX - margin)
        lv = pr[self.tanks]   # tank "pressure" equals water level in WNTR results
        fire = np.array([self.fire[t] for t in self.tanks])
        sets["tank_low"] = flag(lv, lv < fire + margin)
        for k, v in sets.items():
            out[k] = len(v)
        out["any"] = int(sum(out.values()) > 0)
        out["sets"] = sets
        return out

    def slacks(self, res):
        """Worst-hour slack (m) of every constrained element: value minus limit (or limit minus value)."""
        pr = res.node["pressure"]
        out = {}
        out.update({("protected", n): float(v) - P_MIN_PROTECTED for n, v in pr[self.protected].min().items()})
        out.update({("negative", n): float(v) for n, v in pr[self.watch].min().items()})
        out.update({("service", n): float(v) - P_MIN_SERVICE for n, v in pr[self.service].min().items()})
        out.update({("over", n): P_MAX - float(v) for n, v in pr[self.pmax_ok].max().items()})
        out.update({("tank", t): float(pr[t].min()) - self.fire[t] for t in self.tanks})
        return out

