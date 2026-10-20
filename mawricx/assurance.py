"""Deterministic assurance layer that screens agent proposals before execution.

A1 rules  : schema (known assets, unit = metres) and static bounds
            (pump-off window, share of a station off at once, PRV range and step).
A2 twin   : A1 plus a 24-hour EPANET simulation of the proposal on the twin's
            believed state, with safety margins. Rejects a proposal that creates a
            violation the default operation would not create.
A3 plaus. : A2 plus a telemetry plausibility check. Reported tank levels are
            compared with the level the twin predicts from the last trusted state;
            readings that jump by more than the threshold are replaced by the
            prediction before the twin check.
No component uses a language model, and every decision is reproducible.
"""
import numpy as np

from . import hydraulics as HY

MAX_OFF_H = 8
MAX_STATION_OFF_SHARE = 0.5
PRV_RANGE = (20.0, 60.0)
PRV_MAX_STEP = 10.0
TWIN_MARGIN = 2.0          # m on pressures, also used on tank levels
PLAUS_THRESHOLD = 0.5      # m jump in a tank reading relative to the twin prediction


def schema_check(plan, wn):
    """Known assets and metre units only (no operational bounds). Returns (ok, reason)."""
    if plan.get("units", "m") != "m":
        return False, "unit"
    for pid, s, e in plan.get("pump_off", []):
        if pid not in set(wn.pump_name_list):
            return False, "unknown_asset"
    for vid in plan.get("prv", {}):
        if vid not in set(wn.valve_name_list):
            return False, "unknown_asset"
    return True, "ok"


def rule_check(plan, wn, stations):
    """Schema plus static operational bounds. Returns (ok, reason)."""
    if plan.get("units", "m") != "m":
        return False, "unit"
    pumps = set(wn.pump_name_list)
    valves = set(wn.valve_name_list)
    off_by_station = {}
    for pid, s, e in plan.get("pump_off", []):
        if pid not in pumps:
            return False, "unknown_asset"
        if e - s > MAX_OFF_H or s < 0 or e > 24:
            return False, "window_bound"
        st = stations.get(pid, pid)
        off_by_station[st] = off_by_station.get(st, 0) + 1
    for st, k in off_by_station.items():
        members = [p for p, s in stations.items() if s == st]
        if len(members) > 1 and k / len(members) > MAX_STATION_OFF_SHARE:
            return False, "station_share"
    for vid, setting in plan.get("prv", {}).items():
        if vid not in valves:
            return False, "unknown_asset"
        cur = wn.get_link(vid).initial_setting
        if not (PRV_RANGE[0] <= setting <= PRV_RANGE[1]) or abs(setting - cur) > PRV_MAX_STEP:
            return False, "prv_bound"
    return True, "ok"


def new_violations(v_plan, v_default):
    """True if the plan violates a constraint at a node or tank that is not violated under default
    operation. A failed simulation counts as a violation unless the default also failed."""
    keys = ("protected_low", "negative", "over", "tank_low", "service_low")
    if v_plan.get("failed", 0):
        return not v_default.get("failed", 0)
    if v_default.get("failed", 0):
        return False
    sp, sd = v_plan.get("sets"), v_default.get("sets")
    if sp is None or sd is None:
        return any(v_plan[k] > v_default[k] for k in keys)
    return any(len(sp[k] - sd[k]) > 0 for k in keys)


def twin_check(net, plan, believed_state, base_sched, con, default_viol=None):
    """Simulate plan and default operation on the believed state. Returns (ok, details)."""
    dm, tanks = believed_state
    if default_viol is None:
        wn_d = HY.load(net)
        HY.apply_state(wn_d, dm, tanks)
        default_viol = con.violations(HY.simulate(wn_d), margin=TWIN_MARGIN)
    wn_p = HY.load(net)
    HY.apply_state(wn_p, dm, tanks)
    try:
        HY.apply_plan(wn_p, plan, base_sched)
    except KeyError:
        return False, {"reason": "unknown_asset"}
    v = con.violations(HY.simulate(wn_p), margin=TWIN_MARGIN)
    return (not new_violations(v, default_viol)), {"pred": v, "pred_default": default_viol}


def plausibility_filter(reported, predicted, threshold=PLAUS_THRESHOLD):
    """Replace implausible tank readings with the twin prediction. Returns (filtered, flagged tanks)."""
    flagged = [t for t in reported if abs(reported[t] - predicted[t]) > threshold]
    out = dict(reported)
    for t in flagged:
        out[t] = predicted[t]
    return out, flagged


DEGRADE_TOL = 0.1   # m, numerical tolerance when comparing a plan with default operation


def unsafe_by_slack(slack_plan, slack_default, margin=TWIN_MARGIN, tol=DEGRADE_TOL):
    """Twin decision rule. A plan is rejected if it leaves any constrained element inside the safety
    margin and worse than under default operation. This closes the blind spot of comparing violation
    sets when default operation already sits inside the margin."""
    if slack_plan is None:
        return True
    if slack_default is None:
        return False
    for k, sp in slack_plan.items():
        sd = slack_default.get(k, np.inf)
        if sp < margin and sp < sd - tol:
            return True
    return False

