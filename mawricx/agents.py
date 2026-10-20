"""Price-based negotiation among sector and source agents (ADMM in sharing form).

Sector agents keep their demand and eligibility private. In each round they
receive one broadcast vector from the coordinator and return a proposed
delivery schedule. Source agents (reclaimed, stormwater) project the aggregate
request onto their storage-feasible set. The fixed point is the optimum of the
same horizon LP that `allocation.AllocLP` solves centrally (Boyd et al. 2011,
Section 7.3). Volumes are scaled to units of 1e4 m3 and money to 1e4 USD.
"""
import numpy as np
from scipy.optimize import minimize

from .config import DELIVERY_DISCOUNT, SPILL_PENALTY, TERMINAL_FRAC

SCALE = 1e4


def project_pairs(tr, ts, ER, ES, EA):
    """Euclidean projection of (tr, ts) onto {0<=r<=ER, 0<=s<=ES, r+s<=EA}, elementwise."""
    r = np.clip(tr, 0.0, ER)
    s = np.clip(ts, 0.0, ES)
    viol = r + s > EA + 1e-12
    if np.any(viol):
        lo = np.maximum(0.0, EA - ES)
        hi = np.minimum(ER, EA)
        rl = np.clip((tr + EA - ts) / 2.0, lo, hi)
        r = np.where(viol, rl, r)
        s = np.where(viol, EA - rl, s)
    return r, s


class SourceAgent:
    """Storage-feasible projection for one source over the horizon."""

    def __init__(self, inflow, s0, smax, qmax, value, discount=DELIVERY_DISCOUNT,
                 terminal_frac=TERMINAL_FRAC, spill_penalty=SPILL_PENALTY):
        self.inflow, self.s0, self.smax, self.qmax = inflow, s0, smax, qmax
        self.H = len(inflow)
        self.tv = terminal_frac * value * (1 - discount) ** (self.H - 1)
        self.sp = spill_penalty  # USD per m3 equals 1e4 USD per 1e4 m3 (scaled units)
        L = np.tril(np.ones((self.H, self.H)))
        self.L = L
        self.cum_in = np.cumsum(inflow)
        self._x0 = None

    def storage(self, y, z):
        return self.s0 + self.cum_in - self.L @ (y + z)

    def project(self, target, rho_eff):
        """min (rho_eff/2)||y - target||^2 + tv*sum(y) + (sp+tv)*sum(z) s.t. storage bounds."""
        H = self.H
        x0 = self._x0 if self._x0 is not None else np.concatenate([np.clip(target, 0, self.qmax), np.zeros(H)])

        def f(x):
            y, z = x[:H], x[H:]
            d = y - target
            return 0.5 * rho_eff * d @ d + self.tv * y.sum() + (self.sp + self.tv) * z.sum()

        def g(x):
            y = x[:H]
            return np.concatenate([rho_eff * (y - target) + self.tv, np.full(H, self.sp + self.tv)])

        cons = [{"type": "ineq", "fun": lambda x: self.storage(x[:H], x[H:]),
                 "jac": lambda x: np.hstack([-self.L, -self.L])},
                {"type": "ineq", "fun": lambda x: self.smax - self.storage(x[:H], x[H:]),
                 "jac": lambda x: np.hstack([self.L, self.L])}]
        bounds = [(0.0, self.qmax)] * H + [(0.0, None)] * H
        res = minimize(f, x0, jac=g, constraints=cons, bounds=bounds, method="SLSQP",
                       options={"maxiter": 200, "ftol": 1e-10})
        x = res.x
        self._x0 = x
        return np.clip(x[:H], 0.0, self.qmax)


def admm_negotiate(data, s0R, s0S, SRmax, SSmax, QR, QS, prm, declared=None, caps=None,
                   rho=1.0, max_iter=3000, eps_abs=1e-4, eps_rel=1e-4, relax=1.6, adapt=True):
    """Negotiate the horizon allocation. data holds true ER, ES, EA (H x N) and prodR, capS (H).
    declared: optional dict with declared ER, ES, EA (misreporting). caps: optional (N,) cap on
    each sector's requested total per day (coordinator-side verification).
    Returns dict with allocations (H x N) per source, iterations, residual history, messages."""
    ER = (declared or data)["ER"] / SCALE
    ES = (declared or data)["ES"] / SCALE
    EA = (declared or data)["EA"] / SCALE
    H, N = ER.shape
    if caps is not None:
        capv = np.asarray(caps)[None, :] / SCALE
        EA = np.minimum(EA, capv)
        ER = np.minimum(ER, capv)
        ES = np.minimum(ES, capv)
    disc = (1.0 - DELIVERY_DISCOUNT) ** np.arange(H)
    vR = (prm["c_pot"] - prm["c_rec"])
    vS = (prm["c_pot"] - prm["c_sto"])
    cR = -vR * disc[:, None] * np.ones((H, N))   # cost per unit (1e4 USD per 1e4 m3 = USD/m3)
    cS = -vS * disc[:, None] * np.ones((H, N))
    srcR = SourceAgent(data["prodR"] / SCALE, s0R / SCALE, SRmax / SCALE, QR / SCALE, vR)
    srcS = SourceAgent(data["capS"] / SCALE, s0S / SCALE, SSmax / SCALE, QS / SCALE, vS)
    xR = np.zeros((H, N)); xS = np.zeros((H, N))
    zR = np.zeros(H); zS = np.zeros(H)       # z-bar (average shared variable) per source
    uR = np.zeros(H); uS = np.zeros(H)
    hist = []
    msgs = 0
    k = 0
    for k in range(1, max_iter + 1):
        xbarR_old, xbarS_old = xR.mean(axis=1), xS.mean(axis=1)
        # sector agents: local proximal step (private bounds)
        aR = xR - xbarR_old[:, None] + zR[:, None] - uR[:, None]
        aS = xS - xbarS_old[:, None] + zS[:, None] - uS[:, None]
        xR, xS = project_pairs(aR - cR / rho, aS - cS / rho, ER, ES, EA)
        msgs += 2 * N
        xbarR, xbarS = xR.mean(axis=1), xS.mean(axis=1)
        # over-relaxation
        hR = relax * xbarR + (1 - relax) * zR
        hS = relax * xbarS + (1 - relax) * zS
        # source agents: storage-feasible projection of N*(hbar + u)
        zR_old, zS_old = zR, zS
        yR = srcR.project(N * (hR + uR), rho / N)
        yS = srcS.project(N * (hS + uS), rho / N)
        zR, zS = yR / N, yS / N
        msgs += 4
        uR = uR + hR - zR
        uS = uS + hS - zS
        r = np.sqrt(N) * np.sqrt(np.sum((xbarR - zR) ** 2) + np.sum((xbarS - zS) ** 2))
        s = rho * np.sqrt(N) * np.sqrt(np.sum((zR - zR_old) ** 2) + np.sum((zS - zS_old) ** 2))
        eps_pri = np.sqrt(2 * H * N) * eps_abs + eps_rel * max(np.sqrt(N) * np.linalg.norm(np.r_[xbarR, xbarS]),
                                                               np.sqrt(N) * np.linalg.norm(np.r_[zR, zS]))
        eps_dual = np.sqrt(2 * H * N) * eps_abs + eps_rel * rho * np.sqrt(N) * np.linalg.norm(np.r_[uR, uS])
        hist.append((k, r, s, rho))
        if r < eps_pri and s < eps_dual:
            break
        if adapt and k % 10 == 0:
            if r > 10 * s:
                rho *= 2.0; uR /= 2.0; uS /= 2.0
            elif s > 10 * r:
                rho /= 2.0; uR *= 2.0; uS *= 2.0
    # ration requests to source-feasible totals (pro rata)
    reqR, reqS = xR.sum(axis=1), xS.sum(axis=1)
    fR = np.where(reqR > 1e-12, np.minimum(1.0, (zR * N) / np.maximum(reqR, 1e-12)), 0.0)
    fS = np.where(reqS > 1e-12, np.minimum(1.0, (zS * N) / np.maximum(reqS, 1e-12)), 0.0)
    xR = xR * fR[:, None] * SCALE
    xS = xS * fS[:, None] * SCALE
    return {"xR": xR, "xS": xS, "iters": k, "hist": hist, "messages": msgs,
            "floats": msgs * 2 * H, "final_rho": rho}


def horizon_value(xR, xS, data, s0R, s0S, SRmax, SSmax, prm, true_EA=None):
    """Objective (USD, lower is better) of a delivery plan, simulating storage and spill.
    Deliveries beyond a sector's true eligible demand are wasted (no value)."""
    H, N = xR.shape
    disc = (1.0 - DELIVERY_DISCOUNT) ** np.arange(H)
    vR, vS = prm["c_pot"] - prm["c_rec"], prm["c_pot"] - prm["c_sto"]
    useful_R, useful_S = xR.copy(), xS.copy()
    if true_EA is not None:
        tot = xR + xS
        scale = np.where(tot > true_EA, true_EA / np.maximum(tot, 1e-9), 1.0)
        useful_R, useful_S = xR * scale, xS * scale
    obj = -(vR * disc[:, None] * useful_R).sum() - (vS * disc[:, None] * useful_S).sum()
    for x, inflow, s0, smax, v in ((xR, data["prodR"], s0R, SRmax, vR), (xS, data["capS"], s0S, SSmax, vS)):
        s = s0
        spill = 0.0
        for h in range(H):
            s = s + inflow[h] - x[h].sum()
            if s < -1e-6:
                raise ValueError("infeasible plan: storage below zero")
            if s > smax:
                spill += s - smax
                s = smax
        obj += SPILL_PENALTY * spill - TERMINAL_FRAC * v * disc[-1] * s
    wasted = float((xR + xS - useful_R - useful_S).sum())
    return obj, wasted, useful_R, useful_S
