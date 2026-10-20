"""Daily weather from NOAA GHCN-Daily and Hargreaves-Samani reference evapotranspiration."""
import json

import numpy as np
import pandas as pd

from .config import CITIES, DATA_PROC, DATA_RAW


def extraterrestrial_radiation(lat_deg, doy):
    """FAO-56 Eq. 21, MJ m-2 d-1."""
    phi = np.deg2rad(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365.0)
    delta = 0.409 * np.sin(2 * np.pi * doy / 365.0 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1.0, 1.0))
    return (24 * 60 / np.pi) * 0.0820 * dr * (ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws))


def hargreaves_et0(tmax, tmin, lat_deg, doy):
    """Hargreaves and Samani (1985), mm d-1."""
    tmean = (tmax + tmin) / 2.0
    ra_mm = 0.408 * extraterrestrial_radiation(lat_deg, doy)
    return np.maximum(0.0, 0.0023 * ra_mm * (tmean + 17.8) * np.sqrt(np.maximum(tmax - tmin, 0.0)))


def _climatology(series, doy):
    """Day-of-year mean with 31-day circular smoothing."""
    df = pd.DataFrame({"v": series.values, "doy": doy})
    m = df.groupby("doy")["v"].mean().reindex(range(1, 367))
    m = m.interpolate(limit_direction="both")
    ext = pd.concat([m.iloc[-15:], m, m.iloc[:15]])
    sm = ext.rolling(31, center=True, min_periods=1).mean().iloc[15:-15]
    sm.index = range(1, 367)
    return sm


def load_city(city):
    """Return a daily DataFrame for the city's study years and a QC report."""
    station, label, koppen, lat, years = CITIES[city]
    raw = pd.read_csv(DATA_RAW / "ghcn" / f"{station}_2000_2025.csv", parse_dates=["DATE"])
    raw = raw.set_index("DATE").sort_index()
    full = pd.date_range(f"{min(years)}-01-01", f"{max(years)}-12-31", freq="D")
    d = raw.reindex(full)
    doy_all = raw.index.dayofyear.values
    qc = {"city": city, "station": station, "years": [min(years), max(years)], "days": int(len(d))}
    for v in ("TMAX", "TMIN"):
        clim = _climatology(raw[v].dropna(), raw[v].dropna().index.dayofyear.values)
        miss = d[v].isna()
        qc[f"{v.lower()}_filled_share"] = float(miss.mean())
        d.loc[miss, v] = clim.reindex(d.index[miss].dayofyear).values
    miss_p = d["PRCP"].isna()
    qc["prcp_missing_days"] = int(miss_p.sum())
    d["PRCP"] = d["PRCP"].fillna(0.0)
    bad = d["TMAX"] < d["TMIN"]
    d.loc[bad, ["TMAX", "TMIN"]] = d.loc[bad, ["TMIN", "TMAX"]].values
    qc["tmax_lt_tmin_swapped"] = int(bad.sum())
    doy = d.index.dayofyear.values
    out = pd.DataFrame({
        "P": d["PRCP"].astype(float).values,
        "Tmax": d["TMAX"].astype(float).values,
        "Tmin": d["TMIN"].astype(float).values,
    }, index=d.index)
    out["Tmean"] = (out.Tmax + out.Tmin) / 2
    out["ET0"] = hargreaves_et0(out.Tmax.values, out.Tmin.values, lat, doy)
    ann = out.groupby(out.index.year).agg(P=("P", "sum"), ET0=("ET0", "sum"), Tmax=("Tmax", "mean"))
    qc["annual_P_mm_mean"] = float(ann.P.mean())
    qc["annual_ET0_mm_mean"] = float(ann.ET0.mean())
    qc["mean_Tmax_C"] = float(ann.Tmax.mean())
    qc["label"], qc["koppen"] = label, koppen
    return out, qc


def build_all(write=True):
    frames, qcs = {}, []
    for c in CITIES:
        df, qc = load_city(c)
        frames[c] = df
        qcs.append(qc)
        if write:
            DATA_PROC.mkdir(parents=True, exist_ok=True)
            df.to_csv(DATA_PROC / f"weather_{c}.csv", index_label="date")
    if write:
        (DATA_PROC / "weather_qc.json").write_text(json.dumps(qcs, indent=1))
    return frames, qcs


def get_city_weather(city):
    f = DATA_PROC / f"weather_{city}.csv"
    if not f.exists():
        build_all(write=True)
    return pd.read_csv(f, index_col="date", parse_dates=["date"])
