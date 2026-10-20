"""Reference-city demand and alternative-water supply for one weather-year.

Every sector demand is split into end-use components. Each component has a
potable-only part and a non-potable-eligible part, and the eligible part has a
reach fraction for reclaimed water (cR) and for treated stormwater (cS).
Reclaimed water may serve indoor non-potable, cooling and outdoor uses.
Stormwater may serve outdoor irrigation, construction and street cleaning only.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import SECTORS


@dataclass
class CityYear:
    dates: pd.DatetimeIndex
    D: np.ndarray        # total demand (days x sectors), m3/d
    ER: np.ndarray       # reclaimed-reachable eligible demand
    ES: np.ndarray       # stormwater-reachable eligible demand
    EA: np.ndarray       # eligible demand reachable by at least one source
    Elig: np.ndarray     # eligible demand regardless of connection
    indoor: np.ndarray   # indoor (sewered) use per day, m3/d
    prodR: np.ndarray    # reclaimed product available per day, m3/d
    capS: np.ndarray     # stormwater captured per day, m3/d
    runoff: np.ndarray   # stormwater runoff generated per day, m3/d
    SRmax: float
    SSmax: float
    QR: float
    QS: float
    params: dict


def irrigation(et0, p, area_km2, kc, eff, raw_mm, d0=None):
    """Aggregate deficit irrigation that keeps root-zone depletion at or below RAW (m3/d)."""
    n = len(et0)
    out = np.zeros(n)
    dep = raw_mm / 2.0 if d0 is None else d0
    peff = 0.8 * np.maximum(0.0, p - 1.0)
    for t in range(n):
        dep = max(0.0, dep + kc * et0[t] - peff[t])
        if dep > raw_mm:
            out[t] = (dep - raw_mm) / eff
            dep = raw_mm
    return out * area_km2 * 1000.0


def school_factor(dates, southern_or_tropical=False):
    m, d, wd = dates.month.values, dates.day.values, dates.dayofweek.values
    f = np.ones(len(dates))
    if southern_or_tropical:
        hol = (m == 6) | ((m == 11) & (d >= 20)) | (m == 12)
    else:
        hol = (m == 7) | (m == 8) | ((m == 12) & (d >= 20)) | ((m == 1) & (d <= 5)) | ((m == 4) & (d <= 7))
    f[hol] = 0.3
    f[wd >= 5] = 0.1
    return f


def build_city_year(weather, year, prm, tropical=False):
    w = weather[weather.index.year == year]
    dates = w.index
    n = len(w)
    et0, p, tmax, tmean = w.ET0.values, w.P.values, w.Tmax.values, w.Tmean.values
    wd = dates.dayofweek.values
    weekend = wd >= 5
    dry = p < 1.0
    irr = lambda area: irrigation(et0, p, area, prm["kc"], prm["irr_eff"], prm["raw_mm"])  # noqa: E731

    S = {s: i for i, s in enumerate(SECTORS)}
    D = np.zeros((n, len(SECTORS)))
    ER = np.zeros_like(D)
    ES = np.zeros_like(D)
    EA = np.zeros_like(D)
    EL = np.zeros_like(D)
    indoor = np.zeros(n)

    def add(sector, total, elig, cR, cS):
        i = S[sector]
        D[:, i] += total
        EL[:, i] += elig
        ER[:, i] += cR * elig
        ES[:, i] += cS * elig
        EA[:, i] += min(1.0, cR + cS) * elig

    # residential
    res_in = prm["pop"] * prm["res_lpcd"] / 1000.0 * (1 + 0.004 * (tmean - tmean.mean())) * np.where(weekend, 1.03, 1.0)
    add("RES", res_in * (1 - prm["res_np"]), 0, 0, 0)
    add("RES", res_in * prm["res_np"], res_in * prm["res_np"], prm["cR_res"], 0.0)
    res_out = irr(prm["res_area"])
    add("RES", res_out, res_out, prm["cR_res"], prm["cS_res"])
    indoor += res_in
    # hospitality
    hos_in = np.full(n, prm["hos_in"])
    add("HOS", hos_in, hos_in * prm["hos_np"], prm["cR_nonres_in"], 0.0)
    hos_cool = prm["hos_cool"] * np.maximum(0.0, tmax - 24.0)
    add("HOS", hos_cool, hos_cool, prm["cR_cool"], 0.0)
    minor = prm["minor_area"] / 3.35
    hos_out = irr(0.60 * minor)
    add("HOS", hos_out, hos_out, prm["cR_out"], prm["cS_out"])
    indoor += hos_in
    # healthcare (cooling towers excluded from reuse for Legionella control)
    hea_in = np.full(n, prm["hea_beds"] * prm["hea_m3_bed_yr"] / 365.0)
    add("HEA", hea_in, hea_in * prm["hea_np"], prm["cR_nonres_in"], 0.0)
    hea_out = irr(0.25 * minor)
    add("HEA", hea_out, hea_out, prm["cR_out"], prm["cS_out"])
    indoor += hea_in
    # education
    edu_in = prm["edu_in"] * school_factor(dates, tropical)
    add("EDU", edu_in, edu_in * prm["edu_np"], prm["cR_nonres_in"], 0.0)
    edu_out = irr(1.50 * minor)
    add("EDU", edu_out, edu_out, prm["cR_out"], prm["cS_out"])
    indoor += edu_in
    # commerce
    com_in = prm["com_in"] * np.where(weekend, 0.6, 1.0)
    add("COM", com_in, com_in * prm["com_np"], prm["cR_nonres_in"], 0.0)
    com_cool = prm["com_cool"] * np.maximum(0.0, tmax - 22.0)
    add("COM", com_cool, com_cool, prm["cR_cool"], 0.0)
    com_out = irr(1.00 * minor)
    add("COM", com_out, com_out, prm["cR_out"], prm["cS_out"])
    indoor += com_in
    # industry
    ind = prm["ind_proc"] * np.where(weekend, 0.5, 1.0)
    add("IND", ind, ind * prm["ind_np"], prm["cR_ind"], 0.0)
    indoor += ind
    # data centres (90% of evaporative make-up eligible after treatment)
    dct = prm["dct_base"] + prm["dct_slope"] * np.maximum(0.0, tmax - 15.0)
    add("DCT", dct, 0.9 * dct, prm["cR_dct"], 0.0)
    # public landscape
    lan = irr(prm["lan_area"])
    add("LAN", lan, lan, prm["cR_lan"], prm["cS_lan"])
    # construction
    con = prm["con_use"] * np.where(wd == 6, 0.0, 1.0) * np.where(dry, 1.0, 0.2)
    add("CON", con, 0.9 * con, prm["cR_con"], prm["cS_con"])
    # public services
    pub_in = prm["pub_in"] * np.where(weekend, 0.5, 1.0)
    add("PUB", pub_in, 0.30 * pub_in, prm["cR_nonres_in"], 0.0)
    pub_clean = prm["pub_clean"] * np.where(dry, 1.0, 0.0)
    add("PUB", pub_clean, pub_clean, prm["cR_pub"], prm["cS_pub"])
    indoor += pub_in

    # reclaimed supply
    inflow = prm["return_factor"] * indoor
    cap = prm["tert_frac"] * inflow.mean()
    prodR = np.minimum(inflow, cap) * prm["tert_recovery"]
    SRmax = prm["R_store_days"] * prodR.mean()
    QR = prm["R_dist_peak"] * prodR.mean()
    # stormwater supply
    runoff = prm["catch_km2"] * 1e6 * prm["runoff_c"] * np.maximum(0.0, p - prm["init_loss_mm"]) / 1000.0
    capS = np.minimum(runoff, prm["S_intake"])
    return CityYear(dates, D, ER, ES, EA, EL, indoor, prodR, capS, runoff, SRmax, prm["S_store"], QR,
                    prm["S_dist"], dict(prm))
