"""Fit-for-purpose allocation of reclaimed water and captured stormwater.

One linear-programming formulation serves every policy. Three switches turn
coordination mechanisms on or off while assets stay identical:

* pooling      - daily reassignment of each source across users. When off, each
                 user is limited to a fixed contract share of the department's
                 daily release and unused shares return to storage.
* integration  - treated stormwater may serve every compatible sector and both
                 sources are dispatched jointly. When off, the stormwater
                 department serves only municipal sectors.
* forecast     - receding-horizon control over `horizon` days with imperfect
                 forecasts. When off, decisions are myopic (one day).

Variables per day h (sector index i):
  xR[i,h], xS[i,h]  deliveries, sR[h], sS[h] end-of-day storage,
  zR[h], zS[h] spills, relR[h], relS[h] departmental releases.
"""
from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.optimize import linprog

from .config import DELIVERY_DISCOUNT, MUNICIPAL, ORACLE_DISCOUNT, SECTORS, SPILL_PENALTY, TERMINAL_FRAC

NS = len(SECTORS)
MUNI_MASK = np.array([s in MUNICIPAL for s in SECTORS])


@dataclass(frozen=True)
class Policy:
    name: str
    pooling: bool
    integration: bool
    forecast: bool
    oracle: bool = False
    horizon: int = 7

    @property
    def H(self):
        return 1 if not self.forecast else self.horizon


def factorial_policies(horizon=7):
    out = []
    for pool in (False, True):
        for integ in (False, True):
            for fc in (False, True):
                name = "P" + str(int(pool)) + "I" + str(int(integ)) + "F" + str(int(fc))
                out.append(Policy(name, pool, integ, fc, horizon=horizon))
    return out


SILOED = Policy("SILOED", False, False, False)
MAWRICX = Policy("MAWRICX", True, True, True)
ORACLE = Policy("ORACLE", True, True, True, oracle=True)


class AllocLP:
    """Builds and solves the horizon-H allocation LP for one policy."""

    def __init__(self, H, pooling, integration, c_pot, c_rec, c_sto, alphaR=None, alphaS=None,
                 discount=DELIVERY_DISCOUNT, terminal_frac=TERMINAL_FRAC, spill_penalty=SPILL_PENALTY):
        """terminal_frac values end-of-horizon storage at a share of its delivery value, so the
        LP stores rather than spills water it cannot use inside the horizon. spill_penalty makes
        spills happen only when storage is full."""
        self.H, self.pool, self.integ = H, pooling, integration
        self.nv_day = 2 * NS + 6
        self.nv = self.nv_day * H
        self.alphaR, self.alphaS = alphaR, alphaS
        disc = (1.0 - discount) ** np.arange(H)
        c = np.zeros(self.nv)
        for h in range(H):
            b = h * self.nv_day
            c[b:b + NS] = -(c_pot - c_rec) * disc[h]
            c[b + NS:b + 2 * NS] = -(c_pot - c_sto) * disc[h]
            c[self.ix(h, "zR")] = spill_penalty
            c[self.ix(h, "zS")] = spill_penalty
        c[self.ix(H - 1, "sR")] = -terminal_frac * (c_pot - c_rec) * disc[H - 1]
        c[self.ix(H - 1, "sS")] = -terminal_frac * (c_pot - c_sto) * disc[H - 1]
        self.c = c
        self._build_pattern()

    # index helpers
    def ix(self, h, name, i=None):
        b = h * self.nv_day
        if name == "xR":
            return b + i
        if name == "xS":
            return b + NS + i
        return b + 2 * NS + {"sR": 0, "sS": 1, "zR": 2, "zS": 3, "relR": 4, "relS": 5}[name]

    def _build_pattern(self):
        H = self.H
        rows_ub, cols_ub, vals_ub = [], [], []
        r = 0
        self.ub_kind = []
        for h in range(H):
            # capacity rows
            for src in ("xR", "xS"):
                for i in range(NS):
                    rows_ub.append(r); cols_ub.append(self.ix(h, src, i)); vals_ub.append(1.0)
                self.ub_kind.append(("cap" + src[-1], h, None)); r += 1
            # joint eligibility rows
            for i in range(NS):
                rows_ub += [r, r]; cols_ub += [self.ix(h, "xR", i), self.ix(h, "xS", i)]; vals_ub += [1.0, 1.0]
                self.ub_kind.append(("EA", h, i)); r += 1
            if not self.pool:
                for src, rel, alpha, sto, inflow in (("xR", "relR", self.alphaR, "sR", "prodR"),
                                                     ("xS", "relS", self.alphaS, "sS", "capS")):
                    for i in range(NS):
                        rows_ub += [r, r]; cols_ub += [self.ix(h, src, i), self.ix(h, rel)]
                        vals_ub += [1.0, -float(alpha[i])]
                        self.ub_kind.append(("share", h, i)); r += 1
                    for i in range(NS):
                        rows_ub.append(r); cols_ub.append(self.ix(h, src, i)); vals_ub.append(1.0)
                    rows_ub.append(r); cols_ub.append(self.ix(h, rel)); vals_ub.append(-1.0)
                    self.ub_kind.append(("sumrel", h, None)); r += 1
                    rows_ub.append(r); cols_ub.append(self.ix(h, rel)); vals_ub.append(1.0)
                    if h > 0:
                        rows_ub.append(r); cols_ub.append(self.ix(h - 1, sto)); vals_ub.append(-1.0)
                    self.ub_kind.append(("avail" + src[-1], h, None)); r += 1
        self.A_ub = sparse.csr_matrix((vals_ub, (rows_ub, cols_ub)), shape=(r, self.nv))
        rows_eq, cols_eq, vals_eq = [], [], []
        q = 0
        for h in range(H):
            for src, sto, z in (("xR", "sR", "zR"), ("xS", "sS", "zS")):
                rows_eq.append(q); cols_eq.append(self.ix(h, sto)); vals_eq.append(1.0)
                if h > 0:
                    rows_eq.append(q); cols_eq.append(self.ix(h - 1, sto)); vals_eq.append(-1.0)
                for i in range(NS):
                    rows_eq.append(q); cols_eq.append(self.ix(h, src, i)); vals_eq.append(1.0)
                rows_eq.append(q); cols_eq.append(self.ix(h, z)); vals_eq.append(1.0)
                q += 1
        self.A_eq = sparse.csr_matrix((vals_eq, (rows_eq, cols_eq)), shape=(q, self.nv))

    def solve(self, data, s0R, s0S, SRmax, SSmax, QR, QS):
        """data: dict of arrays with H rows: ER, ES, EA (H x NS), prodR, capS (H)."""
        H = self.H
        lb = np.zeros(self.nv)
        ub = np.full(self.nv, np.inf)
        ES = data["ES"].copy()
        if not self.integ:
            ES[:, ~MUNI_MASK] = 0.0
        for h in range(H):
            b = h * self.nv_day
            ub[b:b + NS] = data["ER"][h]
            ub[b + NS:b + 2 * NS] = ES[h]
            ub[self.ix(h, "sR")] = SRmax
            ub[self.ix(h, "sS")] = SSmax
            ub[self.ix(h, "relR")] = QR
            ub[self.ix(h, "relS")] = QS
        b_ub = np.zeros(self.A_ub.shape[0])
        for k, (kind, h, i) in enumerate(self.ub_kind):
            if kind == "capR":
                b_ub[k] = QR
            elif kind == "capS":
                b_ub[k] = QS
            elif kind == "EA":
                b_ub[k] = data["EA"][h, i]
            elif kind == "availR":
                b_ub[k] = data["prodR"][h] + (s0R if h == 0 else 0.0)
            elif kind == "availS":
                b_ub[k] = data["capS"][h] + (s0S if h == 0 else 0.0)
        b_eq = np.zeros(self.A_eq.shape[0])
        for h in range(H):
            b_eq[2 * h] = data["prodR"][h] + (s0R if h == 0 else 0.0)
            b_eq[2 * h + 1] = data["capS"][h] + (s0S if h == 0 else 0.0)
        res = linprog(self.c, A_ub=self.A_ub, b_ub=b_ub, A_eq=self.A_eq, b_eq=b_eq,
                      bounds=np.column_stack([lb, ub]), method="highs")
        if res.status != 0:
            raise RuntimeError(f"LP failed: {res.message}")
        x = res.x
        xR = np.array([[x[self.ix(h, 'xR', i)] for i in range(NS)] for h in range(H)])
        xS = np.array([[x[self.ix(h, 'xS', i)] for i in range(NS)] for h in range(H)])
        sR = np.array([x[self.ix(h, 'sR')] for h in range(H)])
        sS = np.array([x[self.ix(h, 'sS')] for h in range(H)])
        zR = np.array([x[self.ix(h, 'zR')] for h in range(H)])
        zS = np.array([x[self.ix(h, 'zS')] for h in range(H)])
        return {"xR": xR, "xS": xS, "sR": sR, "sS": sS, "zR": zR, "zS": zS, "obj": res.fun}


def contract_shares(cy, integration):
    mR = cy.ER.mean(axis=0)
    aR = mR / mR.sum() if mR.sum() > 0 else np.full(NS, 1.0 / NS)
    ES = cy.ES.copy()
    if not integration:
        ES[:, ~MUNI_MASK] = 0.0
    mS = ES.mean(axis=0)
    aS = mS / mS.sum() if mS.sum() > 0 else np.full(NS, 1.0 / NS)
    return aR, aS


def make_forecaster(cy, weather_year, fm, rng, wet_amounts):
    """Ensemble-mean forecaster: averages fm.members independent noisy members (operational
    ensemble practice). With fm.members == 1 it returns a single noisy realization."""
    k = max(1, int(getattr(fm, "members", 1)))
    if k == 1:
        return _make_member(cy, weather_year, fm, rng, wet_amounts)
    members = [_make_member(cy, weather_year, fm, np.random.default_rng(rng.integers(1 << 31)), wet_amounts)
               for _ in range(k)]

    def fc(t, H):
        outs = [m(t, H) for m in members]
        res = {key: np.mean([o[key] for o in outs], axis=0) for key in ("ER", "ES", "EA", "prodR", "capS")}
        res["h"] = outs[0]["h"]
        return res

    return fc


def _make_member(cy, weather_year, fm, rng, wet_amounts):
    """Return f(t, H) -> dict of forecast arrays for days t..t+H-1 (day t is a nowcast)."""
    n = len(cy.prodR)
    prm = cy.params
    P = weather_year.P.values

    def fc(t, H):
        idx = np.arange(t, min(n, t + H))
        h = idx - t
        ER, ES, EA = cy.ER[idx].copy(), cy.ES[idx].copy(), cy.EA[idx].copy()
        capS = cy.capS[idx].copy()
        prodR = cy.prodR[idx].copy()
        for k in range(1, len(idx)):
            sd = fm.demand_sigma0 + fm.demand_sigma_slope * k
            common = rng.normal(0.0, sd)
            mult = np.maximum(0.0, 1.0 + common + rng.normal(0.0, sd / 2.0, NS))
            ER[k] *= mult; ES[k] *= mult; EA[k] *= mult
            prodR[k] *= max(0.0, 1.0 + rng.normal(0.0, sd / 2.0))
            p = P[idx[k]]
            if p >= fm.wet_mm:
                if rng.random() < fm.miss0 + fm.miss_slope * k:
                    pf = 0.0
                else:
                    s = fm.rain_sigma0 + fm.rain_sigma_slope * k
                    pf = p * np.exp(rng.normal(-s * s / 2.0, s))
            else:
                pf = rng.choice(wet_amounts) if rng.random() < fm.fa0 + fm.fa_slope * k else p
            ro = prm["catch_km2"] * 1e6 * prm["runoff_c"] * max(0.0, pf - prm["init_loss_mm"]) / 1000.0
            capS[k] = min(ro, prm["S_intake"])
        return {"ER": ER, "ES": ES, "EA": EA, "prodR": prodR, "capS": capS, "h": h}

    return fc


def simulate_policy(cy, policy, weather_year=None, fm=None, rng=None, wet_amounts=None, s0R=None, s0S=None):
    """Run one policy over the city-year. Returns annual totals and daily series."""
    prm = cy.params
    n = len(cy.prodR)
    aR, aS = contract_shares(cy, policy.integration)
    s0R = 0.5 * cy.SRmax if s0R is None else s0R
    s0S = 0.5 * cy.SSmax if s0S is None else s0S
    xR = np.zeros((n, NS)); xS = np.zeros((n, NS))
    sR = np.zeros(n); sS = np.zeros(n); zR = np.zeros(n); zS = np.zeros(n)
    if policy.oracle:
        lp = AllocLP(n, True, True, prm["c_pot"], prm["c_rec"], prm["c_sto"], discount=ORACLE_DISCOUNT,
                     terminal_frac=1.0)
        data = {"ER": cy.ER, "ES": cy.ES, "EA": cy.EA, "prodR": cy.prodR, "capS": cy.capS}
        out = lp.solve(data, s0R, s0S, cy.SRmax, cy.SSmax, cy.QR, cy.QS)
        xR, xS, sR, sS, zR, zS = out["xR"], out["xS"], out["sR"], out["sS"], out["zR"], out["zS"]
    else:
        H = policy.H
        lps = {}
        fc = make_forecaster(cy, weather_year, fm, rng, wet_amounts) if policy.forecast else None
        cur_R, cur_S = s0R, s0S
        for t in range(n):
            Ht = min(H, n - t)
            if Ht not in lps:
                lps[Ht] = AllocLP(Ht, policy.pooling, policy.integration, prm["c_pot"], prm["c_rec"], prm["c_sto"],
                                  aR, aS)
            if policy.forecast:
                data = fc(t, Ht)
            else:
                data = {"ER": cy.ER[t:t + 1], "ES": cy.ES[t:t + 1], "EA": cy.EA[t:t + 1],
                        "prodR": cy.prodR[t:t + 1], "capS": cy.capS[t:t + 1]}
            out = lps[Ht].solve(data, cur_R, cur_S, cy.SRmax, cy.SSmax, cy.QR, cy.QS)
            xR[t], xS[t] = out["xR"][0], out["xS"][0]
            sR[t], sS[t], zR[t], zS[t] = out["sR"][0], out["sS"][0], out["zR"][0], out["zS"][0]
            cur_R, cur_S = sR[t], sS[t]
    return summarize(cy, xR, xS, sR, sS, zR, zS, policy.name, s0R, s0S)


def summarize(cy, xR, xS, sR, sS, zR, zS, name, s0R=None, s0S=None):
    prm = cy.params
    D = cy.D
    pot = D - xR - xS
    tot = {
        "policy": name,
        "demand": D.sum(), "potable": pot.sum(), "rec_used": xR.sum(), "sto_used": xS.sum(),
        "rec_prod": cy.prodR.sum(), "sto_captured": cy.capS.sum(), "runoff": cy.runoff.sum(),
        "rec_spill": zR.sum(), "sto_spill": zS.sum(),
        "elig": cy.Elig.sum(), "elig_reach": cy.EA.sum(), "rec_reach": cy.ER.sum(), "sto_reach": cy.ES.sum(),
        "end_sR": sR[-1], "end_sS": sS[-1],
    }
    s0R = 0.5 * cy.SRmax if s0R is None else s0R
    s0S = 0.5 * cy.SSmax if s0S is None else s0S
    # storage-adjusted potable: net drawdown of the initial storage counts as potable-equivalent use
    tot["dstore"] = (sR[-1] - s0R) + (sS[-1] - s0S)
    tot["potable_adj"] = tot["potable"] - tot["dstore"]
    tot["energy_kwh"] = prm["e_pot"] * tot["potable"] + prm["e_rec"] * tot["rec_used"] + prm["e_sto"] * tot["sto_used"]
    tot["co2_t"] = tot["energy_kwh"] * prm["ef_grid"] / 1000.0
    tot["cost_usd"] = prm["c_pot"] * tot["potable"] + prm["c_rec"] * tot["rec_used"] + prm["c_sto"] * tot["sto_used"]
    for j, s in enumerate(SECTORS):
        tot[f"pot_{s}"] = pot[:, j].sum()
        tot[f"rec_{s}"] = xR[:, j].sum()
        tot[f"sto_{s}"] = xS[:, j].sum()
        tot[f"dem_{s}"] = D[:, j].sum()
    return tot


def baseline_summary(cy):
    z = np.zeros_like(cy.D)
    zero = np.zeros(len(cy.prodR))
    out = summarize(cy, z, z, zero + 0.5 * cy.SRmax, zero + 0.5 * cy.SSmax, cy.prodR.copy(), cy.capS.copy(),
                    "BASELINE")
    return out
