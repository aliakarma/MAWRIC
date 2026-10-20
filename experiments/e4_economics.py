"""E4: economics of the coordination layer (RQ4).

Benefits are drawn from the measured E1 and E3b distributions:
  * net operating saving from the coordination premium: potable volume saved times the potable
    marginal cost, minus the marginal cost of the extra reclaimed and storm water delivered;
  * avoided real losses and crew hours from E3b (MAWRICX against HUMAN), scaled to the
    reference city by system demand;
  * carbon, valued separately (societal view) and never added to the utility NPV.
Costs are declared planning ranges for the coordination platform, telemetry and robots.
Capital is counted once (t = 0). The energy embedded in the potable marginal cost is not
counted again as an energy benefit.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from SALib.analyze import sobol
from SALib.sample import saltelli

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mawricx.config import MASTER_SEED, P, RESULTS  # noqa: E402

HORIZON = 15
COSTS = {   # declared planning ranges (USD)
    "capex_platform": (1.0e6, 4.0e6),     # agents, digital twin integration, assurance software
    "capex_telemetry": (0.5e6, 2.0e6),    # meters, sensors, communications for alternative-water assets
    "capex_robots": (0.2e6, 0.8e6),       # two in-pipe or acoustic inspection robots
    "opex_platform": (0.3e6, 1.0e6),      # licences, cloud, 2 to 4 staff, cyber assurance per year
    "robot_om_share": (0.10, 0.20),       # robot O&M as a share of robot capex per year
}
OTHER = {
    "discount": (0.03, 0.09),
    "carbon_usd_t": (0.0, 150.0),
    "crew_usd_h": (80.0, 200.0),
    "loss_value_share": (0.3, 1.0),       # share of the potable marginal cost recovered per m3 of real loss avoided
}
REF_DEMAND_SCALE = None  # set from E1 baseline demand / Net6 demand


def annuity_factor(r, n=HORIZON):
    return (1 - (1 + r) ** -n) / r


def load_inputs(tag):
    e1 = pd.read_csv(RESULTS / f"e1_runs_{tag}.csv")
    f = e1[e1["mode"] == "factorial"]
    piv = {k: f.pivot_table(index=["city", "year", "draw"], columns="policy", values=k)
           for k in ("potable_adj", "rec_used", "sto_used", "demand")}
    d = pd.DataFrame({
        "dpot": piv["potable_adj"]["SILOED"] - piv["potable_adj"]["MAWRICX"],
        "drec": piv["rec_used"]["MAWRICX"] - piv["rec_used"]["SILOED"],
        "dsto": piv["sto_used"]["MAWRICX"] - piv["sto_used"]["SILOED"],
        "demand": piv["demand"]["BASELINE"],
    }).reset_index()
    e3b = pd.read_csv(RESULTS / f"e3b_leak_{tag}.csv")
    nom = e3b[e3b.case == "nominal"].pivot_table(index="year", columns="policy",
                                                 values=["lost_m3", "crew_false_h"])
    leak = pd.DataFrame({"dloss": nom["lost_m3"]["HUMAN"] - nom["lost_m3"]["MAWRICX"],
                         "dcrew": nom["crew_false_h"]["HUMAN"] - nom["crew_false_h"]["MAWRICX"]})
    return d, leak


def npv_model(x, prem, leak, scale):
    """Vectorized NPV. x: dict of arrays. prem/leak: arrays of empirical draws (indices chosen by u)."""
    n = len(x["c_pot"])
    i = np.minimum((x["u_prem"] * len(prem)).astype(int), len(prem) - 1)
    j = np.minimum((x["u_leak"] * len(leak)).astype(int), len(leak) - 1)
    dpot, drec, dsto = prem[i, 0], prem[i, 1], prem[i, 2]
    dloss, dcrew = leak[j, 0] * scale, leak[j, 1] * scale
    b_alloc = dpot * x["c_pot"] - drec * x["c_rec"] - dsto * x["c_sto"]
    b_leak = dloss * x["c_pot"] * x["loss_value_share"] + dcrew * x["crew_usd_h"]
    capex = x["capex_platform"] + x["capex_telemetry"] + x["capex_robots"]
    opex = x["opex_platform"] + x["robot_om_share"] * x["capex_robots"]
    af = annuity_factor(x["discount"])
    npv = -capex + af * (b_alloc + b_leak - opex)
    dco2 = (x["e_pot"] * dpot - x["e_rec"] * drec - x["e_sto"] * dsto) * x["ef_grid"] / 1000.0
    npv_soc = npv + af * dco2 * x["carbon_usd_t"]
    eac = capex / af + opex
    return {"npv": npv, "npv_soc": npv_soc, "b_alloc": b_alloc, "b_leak": b_leak, "opex": opex, "capex": capex,
            "eac": eac, "dco2": dco2, "benefit": b_alloc + b_leak}


def ranges():
    r = {"u_prem": (0.0, 1.0), "u_leak": (0.0, 1.0),
         "c_pot": (P["c_pot"].low, P["c_pot"].high), "c_rec": (P["c_rec"].low, P["c_rec"].high),
         "c_sto": (P["c_sto"].low, P["c_sto"].high), "e_pot": (P["e_pot"].low, P["e_pot"].high),
         "e_rec": (P["e_rec"].low, P["e_rec"].high), "e_sto": (P["e_sto"].low, P["e_sto"].high),
         "ef_grid": (P["ef_grid"].low, P["ef_grid"].high)}
    r.update(COSTS)
    r.update(OTHER)
    return r


def main(scale):
    tag = scale.name
    prem_df, leak_df = load_inputs(tag)
    net6_daily = 119451.0   # Net6 mean daily demand from the nominal EPANET run, m3/d
    rng = np.random.default_rng(MASTER_SEED + 4)
    R = ranges()
    keys = list(R)
    rows, sob = [], []
    leak = leak_df[["dloss", "dcrew"]].to_numpy()
    t0 = time.time()
    for city, g in prem_df.groupby("city"):
        prem = g[["dpot", "drec", "dsto"]].to_numpy()
        scale_c = float(g["demand"].mean() / (net6_daily * 365))
        n = scale.e4_mc
        x = {k: rng.uniform(lo, hi, n) for k, (lo, hi) in R.items()}
        out = npv_model(x, prem, leak, scale_c)
        rows.append({
            "city": city, "n": n, "scale_to_ref": scale_c,
            "dpot_mean": prem[:, 0].mean(), "benefit_mean": out["benefit"].mean(),
            "b_alloc_mean": out["b_alloc"].mean(), "b_leak_mean": out["b_leak"].mean(),
            "eac_mean": out["eac"].mean(), "npv_mean": out["npv"].mean(), "npv_p05": np.percentile(out["npv"], 5),
            "npv_p50": np.percentile(out["npv"], 50), "npv_p95": np.percentile(out["npv"], 95),
            "p_npv_pos": (out["npv"] > 0).mean(), "npv_soc_mean": out["npv_soc"].mean(),
            "p_npv_soc_pos": (out["npv_soc"] > 0).mean(), "dco2_mean": out["dco2"].mean(),
            # break-even equivalent annual cost: benefits supported at the median and 90th percentile
            "breakeven_eac_p50": np.percentile(out["benefit"], 50), "breakeven_eac_p10": np.percentile(out["benefit"], 10),
        })
        pd.DataFrame({k: v for k, v in out.items()}).assign(city=city).sample(
            n=min(5000, n), random_state=1).to_csv(RESULTS / f"e4_mc_sample_{city}_{tag}.csv", index=False)
        problem = {"num_vars": len(keys), "names": keys, "bounds": [list(R[k]) for k in keys]}
        np.random.seed(MASTER_SEED % 2**31)
        X = saltelli.sample(problem, scale.e4_sobol_n, calc_second_order=False)
        xx = {k: X[:, i] for i, k in enumerate(keys)}
        Y = npv_model(xx, prem, leak, scale_c)["npv"]
        Si = sobol.analyze(problem, Y, calc_second_order=False, seed=MASTER_SEED % 2**31)
        for k, s1, st, st_conf in zip(keys, Si["S1"], Si["ST"], Si["ST_conf"]):
            sob.append({"city": city, "param": k, "S1": s1, "ST": st, "ST_conf": st_conf})
    pd.DataFrame(rows).to_csv(RESULTS / f"e4_economics_{tag}.csv", index=False)
    pd.DataFrame(sob).to_csv(RESULTS / f"e4_sobol_{tag}.csv", index=False)
    print(f"E4 done in {time.time() - t0:.0f}s")
    return pd.DataFrame(rows), pd.DataFrame(sob)


if __name__ == "__main__":
    from mawricx.config import FULL, SMOKE
    main(SMOKE if "--smoke" in sys.argv else FULL)
