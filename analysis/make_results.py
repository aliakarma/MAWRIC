"""Statistics, figures, LaTeX tables and macros for the manuscript.

Every number quoted in manuscript/MAWRIC_X_Water.tex comes from
manuscript/numbers.tex, which this script writes from results/*.csv.
Usage: python analysis/make_results.py [--tag full|smoke]
"""
import json
import re
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
MS = ROOT / "manuscript"
FIG = MS / "figures"
TAB = MS / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "full"
RNG = np.random.default_rng(20261016)

# reference palette (dataviz skill, light mode), fixed order, validated for 4 adjacent slots
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100", "magenta": "#e87ba4",
     "green": "#008300", "violet": "#6250d6", "red": "#e34948"}
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
NEUTRAL = "#9a9893"
CITY_ORDER = ["PHX", "LAX", "LHR", "SIN"]
CITY_NAME = {"PHX": "Phoenix", "LAX": "Los Angeles", "LHR": "London", "SIN": "Singapore"}
CITY_COL = {"PHX": C["blue"], "LAX": C["orange"], "LHR": C["aqua"], "SIN": C["yellow"]}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "grid.linestyle": "-", "axes.axisbelow": True, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300, "pdf.fonttype": 42,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left",
})

MAC = {}


def mac(name, value, fmt="{:.2f}"):
    """Register a LaTeX macro \\name{} with a formatted value."""
    if isinstance(value, str):
        MAC[name] = value
    else:
        MAC[name] = fmt.format(value)


def minus(text):
    """Typeset a hyphen that starts a negative number as a minus sign (works in text and math mode)."""
    return re.sub(r"(?<![-\w\\{])-(?=\d)", r"\\ensuremath{-}", text)


def boot_ci(x, n=10000, stat=np.mean):
    x = np.asarray(x, float)
    idx = RNG.integers(0, len(x), (n, len(x)))
    s = stat(x[idx], axis=1)
    return np.percentile(s, 2.5), np.percentile(s, 97.5)


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    m = len(p)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, (m - r) * p[i])
        adj[i] = min(1.0, run)
    return adj


def fmt_p(p):
    return r"$<$0.001" if p < 0.001 else f"{p:.3f}"


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)


# ============================================================================ climate
def climate():
    qc = json.loads((ROOT / "data" / "processed" / "weather_qc.json").read_text())
    rows = []
    fig, axes = plt.subplots(1, 4, figsize=(6.6, 1.9), sharey=True)
    for ax, c in zip(axes, CITY_ORDER):
        w = pd.read_csv(ROOT / "data" / "processed" / f"weather_{c}.csv", parse_dates=["date"], index_col="date")
        m = w.groupby(w.index.month).agg(P=("P", "sum"), ET0=("ET0", "sum")) / (w.index.year.nunique())
        x = np.arange(1, 13)
        ax.bar(x - 0.2, m.P, width=0.38, color=C["blue"], label="Rainfall")
        ax.bar(x + 0.2, m.ET0, width=0.38, color=C["orange"], label="Reference ET$_0$")
        ax.set_xticks([1, 4, 7, 10], ["Jan", "Apr", "Jul", "Oct"])
        ax.set_title(CITY_NAME[c])
        ax.grid(axis="x", visible=False)
        q = next(d for d in qc if d["city"] == c)
        rows.append(q)
        mac(f"P{c}", q["annual_P_mm_mean"], "{:,.0f}")
        mac(f"ETo{c}", q["annual_ET0_mm_mean"], "{:,.0f}")
        mac(f"Tx{c}", q["mean_Tmax_C"], "{:.1f}")
        mac(f"TxFill{c}", 100 * q["tmax_filled_share"], "{:.0f}")
        mac(f"TnFill{c}", 100 * q["tmin_filled_share"], "{:.0f}")
        mac(f"PMiss{c}", q["prcp_missing_days"], "{:d}")
        mac(f"TSwap{c}", q["tmax_lt_tmin_swapped"], "{:d}")
        mac(f"Yr{c}", f"{q['years'][0]}--{q['years'][1]}")
        # day-to-day variability that climatology filling removes: SD of observed daily Tmax anomalies
        sys.path.insert(0, str(ROOT))
        from mawricx.config import CITIES
        from mawricx.weather import _climatology
        station, _, _, _, yrs = CITIES[c]
        raw = pd.read_csv(ROOT / "data" / "raw" / "ghcn" / f"{station}_2000_2025.csv", parse_dates=["DATE"])
        tx = raw.set_index("DATE").sort_index().TMAX.dropna()
        clim = _climatology(tx, tx.index.dayofyear.values)
        tx = tx[(tx.index.year >= min(yrs)) & (tx.index.year <= max(yrs))]
        mac(f"TxAnomSd{c}", float(np.std(tx.values - clim.reindex(tx.index.dayofyear).values)), "{:.1f}")
    axes[0].set_ylabel("mm per month")
    axes[0].legend(loc="upper left", fontsize=7)
    fig.tight_layout(w_pad=0.6)
    save(fig, "fig_climate")
    return rows


# ============================================================================ E1
def e1():
    df = pd.read_csv(RES / f"e1_runs_{TAG}.csv")
    f = df[df["mode"] == "factorial"]
    piv = f.pivot_table(index=["city", "year", "draw"], columns="policy", values="potable_adj")
    base = piv["BASELINE"]
    sav = (1 - piv.div(base, axis=0)) * 100
    prem = piv.rsub(piv["SILOED"], axis=0)       # m3, positive means better than siloed
    nom = prem.xs(0, level="draw")
    savn = sav.xs(0, level="draw")
    rows, pvals = [], []
    for c in CITY_ORDER:
        g = nom.loc[c]
        gs = savn.loc[c]
        b = base.xs(0, level="draw").loc[c]
        pm = g["MAWRICX"].values
        lo, hi = boot_ci(pm)
        stat = wilcoxon(pm, zero_method="wilcox") if np.any(pm != 0) else None
        p = stat.pvalue if stat is not None else 1.0
        pvals.append(p)
        dfc = (g["MAWRICX"] - g["P1I1F0"]).values
        rows.append({"city": c, "base": b.mean() / 1e6, "s_sil": gs["SILOED"].mean(), "s_mx": gs["MAWRICX"].mean(),
                     "s_or": gs["ORACLE"].mean(), "prem": pm.mean() / 1e6, "lo": lo / 1e6, "hi": hi / 1e6,
                     "prem_pct": (pm / b.values).mean() * 100, "prem_or": g["ORACLE"].mean() / 1e6,
                     "prem_pf": g["MAWRICX_PF"].mean() / 1e6, "prem_my": g["P1I1F0"].mean() / 1e6,
                     "fc_value": dfc.mean() / 1e6, "p": p,
                     "share_or": pm.mean() / g["ORACLE"].mean() * 100 if g["ORACLE"].mean() > 0 else np.nan})
    padj = holm(pvals)
    for r, pa in zip(rows, padj):
        r["p_holm"] = pa
    best = max(rows, key=lambda r: r["prem_pf"] - r["prem_my"])
    mac("PFGainMax", best["prem_pf"] - best["prem_my"], "{:.3f}")
    mac("PFGainMaxCity", CITY_NAME[best["city"]])
    t = pd.DataFrame(rows)
    for r in rows:
        c = r["city"]
        mac(f"Base{c}", r["base"], "{:.1f}")
        mac(f"SavSil{c}", r["s_sil"], "{:.2f}")
        mac(f"SavMx{c}", r["s_mx"], "{:.2f}")
        mac(f"SavOr{c}", r["s_or"], "{:.2f}")
        mac(f"Prem{c}", r["prem"], "{:.3f}")
        mac(f"PremK{c}", r["prem"] * 1000, "{:,.0f}")
        mac(f"PremLo{c}", r["lo"], "{:.3f}")
        mac(f"PremHi{c}", r["hi"], "{:.3f}")
        mac(f"PremPct{c}", r["prem_pct"], "{:.2f}")
        mac(f"PremOr{c}", r["prem_or"], "{:.3f}")
        mac(f"PremPF{c}", r["prem_pf"], "{:.3f}")
        mac(f"PremMy{c}", r["prem_my"], "{:.3f}")
        mac(f"FcVal{c}", r["fc_value"] * 1000, "{:,.0f}")
        mac(f"FcLoss{c}", -r["fc_value"] * 1000, "{:,.0f}")   # positive when forecasts lowered the premium
        mac(f"PFGain{c}", r["prem_pf"] - r["prem_my"], "{:.3f}")
        mac(f"MyShareOr{c}", r["prem_my"] / r["prem_or"] * 100, "{:.0f}")
        mac(f"ShareOr{c}", r["share_or"], "{:.0f}")
        mac(f"PHolm{c}", fmt_p(r["p_holm"]))
    allp = prem["MAWRICX"]
    allpct = allp / base * 100
    for c in CITY_ORDER:
        mac(f"PremAllMin{c}", allp.loc[c].min() / 1e6, "{:.3f}")
        mac(f"PremAllMax{c}", allp.loc[c].max() / 1e6, "{:.3f}")
        mac(f"PremAllMean{c}", allp.loc[c].mean() / 1e6, "{:.3f}")
        mac(f"PremAllPctMax{c}", allpct.loc[c].max(), "{:.2f}")
        mac(f"NegShare{c}", (allp.loc[c] < 0).mean() * 100, "{:.0f}")
        neg = (allp.loc[c] < 0).to_numpy()
        mac(f"NegN{c}", int(neg.sum()), "{:d}")
        mac(f"NegPF{c}", int((prem["MAWRICX_PF"].loc[c].to_numpy()[neg] < 0).sum()), "{:d}")
    mac("SavSilMin", t.s_sil.min(), "{:.1f}")
    mac("SavSilMax", t.s_sil.max(), "{:.1f}")
    mac("EOneTasks", f"{len(f[['city', 'year', 'draw']].drop_duplicates()):,}")
    mac("EOneCityYears", f"{len(f[['city', 'year', 'draw']].drop_duplicates()):,}")
    mac("EOneRuns", f"{len(df):,}")
    # energy, emissions, utilization (nominal)
    en = f.pivot_table(index=["city", "year", "draw"], columns="policy", values="energy_kwh").xs(0, level="draw")
    co = f.pivot_table(index=["city", "year", "draw"], columns="policy", values="co2_t").xs(0, level="draw")
    ru = f.pivot_table(index=["city", "year", "draw"], columns="policy", values="rec_used").xs(0, level="draw")
    rp = f.pivot_table(index=["city", "year", "draw"], columns="policy", values="rec_prod").xs(0, level="draw")
    su = f.pivot_table(index=["city", "year", "draw"], columns="policy", values="sto_used").xs(0, level="draw")
    sc = f.pivot_table(index=["city", "year", "draw"], columns="policy", values="sto_captured").xs(0, level="draw")
    for c in CITY_ORDER:
        mac(f"DEn{c}", (en.loc[c, "SILOED"] - en.loc[c, "MAWRICX"]).mean() / 1e6, "{:.3f}")
        mac(f"DCo{c}", (co.loc[c, "SILOED"] - co.loc[c, "MAWRICX"]).mean(), "{:,.0f}")
        mac(f"RecUtilSil{c}", (ru.loc[c, "SILOED"] / rp.loc[c, "SILOED"]).mean() * 100, "{:.0f}")
        mac(f"RecUtilMx{c}", (ru.loc[c, "MAWRICX"] / rp.loc[c, "MAWRICX"]).mean() * 100, "{:.0f}")
        mac(f"StoUtilSil{c}", (su.loc[c, "SILOED"] / sc.loc[c, "SILOED"]).mean() * 100, "{:.0f}")
        mac(f"StoUtilMx{c}", (su.loc[c, "MAWRICX"] / sc.loc[c, "MAWRICX"]).mean() * 100, "{:.0f}")
        mac(f"EnBase{c}", en.loc[c, "SILOED"].mean() / 1e6, "{:.1f}")
    # Shapley
    sh = pd.read_csv(RES / f"e1_shapley_{TAG}.csv")
    shn = sh[sh.draw == 0].groupby("city")[["total", "P", "I", "F"]].mean() / 1e6
    sha = sh.groupby("city")[["total", "P", "I", "F"]].mean() / 1e6
    for c in CITY_ORDER:
        for m in ("P", "I", "F"):
            mac(f"Sh{m}{c}", shn.loc[c, m], "{:.3f}")
            mac(f"ShAll{m}{c}", sha.loc[c, m], "{:.3f}")
        tot = shn.loc[c, ["P", "I"]].clip(lower=0).sum()
        mac(f"ShIShare{c}", 100 * max(shn.loc[c, "I"], 0) / tot if tot > 0 else 0, "{:.0f}")
    # sweep
    s = df[df["mode"] == "sweep"]
    sp = s.pivot_table(index=["city", "year", "tert_frac"], columns="policy", values="potable_adj")
    spp = sp.rsub(sp["SILOED"], axis=0).groupby(level=["city", "tert_frac"]).mean() / 1e6
    for c in CITY_ORDER:
        g = spp.loc[c]
        k = g["MAWRICX"].idxmax()
        mac(f"SweepPeak{c}", k, "{:.2f}")
        mac(f"SweepPeakVal{c}", g["MAWRICX"].max(), "{:.3f}")
        mac(f"SweepLow{c}", g["MAWRICX"].iloc[0], "{:.3f}")
        mac(f"SweepHigh{c}", g["MAWRICX"].iloc[-1], "{:.3f}")
    # ---------------- figures
    fig, ax = plt.subplots(figsize=(6.3, 2.5))
    xs = np.arange(len(CITY_ORDER))
    series = [("MAWRICX", "MAWRIC-X (ensemble forecasts)", C["blue"], -0.22),
              ("MAWRICX_PF", "MAWRIC-X (perfect forecasts)", C["violet"], 0.0),
              ("ORACLE", "Oracle (perfect foresight)", NEUTRAL, 0.22)]
    for key, lab, col, off in series:
        for i, c in enumerate(CITY_ORDER):
            v = nom.loc[c][key].values / 1e6
            jitter = RNG.uniform(-0.05, 0.05, len(v))
            ax.scatter(np.full(len(v), i + off) + jitter, v, s=9, color=col, alpha=0.45, linewidths=0)
            ax.plot([i + off - 0.08, i + off + 0.08], [v.mean(), v.mean()], color=col, lw=2.2,
                    solid_capstyle="round", label=lab if i == 0 else None)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xticks(xs, [CITY_NAME[c] for c in CITY_ORDER])
    ax.set_ylabel("Potable water saved beyond\nsiloed operation (Mm$^3$/yr)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", ncol=1)
    save(fig, "fig_e1_premium")

    fig, ax = plt.subplots(figsize=(6.3, 2.3))
    w = 0.22
    for j, (m, lab, col) in enumerate((("P", "Pooling across users", C["blue"]),
                                        ("I", "Stormwater integration", C["orange"]),
                                        ("F", "Forecast-based storage", C["aqua"]))):
        vals = [shn.loc[c, m] for c in CITY_ORDER]
        ax.bar(xs + (j - 1) * w, vals, width=w * 0.9, color=col, label=lab)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xticks(xs, [CITY_NAME[c] for c in CITY_ORDER])
    ax.set_ylabel("Shapley share of the\npremium (Mm$^3$/yr)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left")
    save(fig, "fig_e1_shapley")

    fig, axes = plt.subplots(1, 4, figsize=(6.6, 1.95), sharey=True)
    for ax, c in zip(axes, CITY_ORDER):
        g = spp.loc[c]
        x = g.index.values
        ax.plot(x, g["ORACLE"], color=NEUTRAL, lw=1.6, label="Oracle (perfect foresight)")
        ax.plot(x, g["MAWRICX"], color=C["blue"], lw=2.0, marker="o", ms=3.2, label="MAWRIC-X")
        ax.set_xscale("log")
        ax.set_xticks([0.05, 0.2, 1.0, 2.0], ["0.05", "0.2", "1", "2"])
        ax.minorticks_off()
        ax.set_title(CITY_NAME[c])
        ax.axhline(0, color=MUTED, lw=0.6)
    axes[0].set_ylabel("Premium (Mm$^3$/yr)")
    fig.supxlabel("Tertiary capacity as a multiple of mean wastewater inflow", fontsize=8, color=INK2, y=0.02)
    axes[0].legend(loc="upper left", fontsize=6.5)
    fig.tight_layout(w_pad=0.5)
    save(fig, "fig_e1_sweep")

    # table body
    lines = []
    for r in rows:
        lines.append(f"{CITY_NAME[r['city']]} & {r['base']:.1f} & {r['s_sil']:.2f} & {r['s_mx']:.2f} & "
                     f"{r['prem']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}] & {r['prem_pf']:.3f} & {r['prem_or']:.3f} & "
                     f"{fmt_p(r['p_holm'])} \\\\")
    (TAB / "tab_e1.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return t


# ============================================================================ E2
def e2():
    d = pd.read_csv(RES / f"e2_negotiation_{TAG}.csv")
    h = d[d.case == "honest"]
    mac("ETwoN", len(h), "{:d}")
    mac("GapMed", h.gap.median() * 100, "{:.4f}")
    mac("GapPninetyfive", h.gap.quantile(0.95) * 100, "{:.3f}")
    mac("GapMax", h.gap.max() * 100, "{:.3f}")
    mac("ItMed", h.iters.median(), "{:.0f}")
    mac("ItPninetyfive", h.iters.quantile(0.95), "{:.0f}")
    mac("MsgMed", h.messages.median(), "{:,.0f}")
    mac("TAdmm", h.t.median(), "{:.2f}")
    mac("TLp", h.t_lp.median() * 1000, "{:.0f}")
    hh = h.set_index(["city", "year", "day"])
    out = []
    for case in ("mis30", "mis60", "mis100"):
        for capped in ("", "_cap"):
            g = d[d.case == case + capped].set_index(["city", "year", "day"])
            sc = g.supply_ratio < 1
            gain = (g.liar_useful - hh.liar_useful)[sc].mean()
            loss = -(g.others_useful - hh.others_useful)[sc].mean()
            waste = g.wasted[sc].mean()
            out.append({"case": case, "cap": bool(capped), "gain": gain, "loss": loss, "waste": waste,
                        "n": int(sc.sum())})
            tag = {"mis30": "Thirty", "mis60": "Sixty", "mis100": "Hundred"}[case] + ("Cap" if capped else "")
            mac(f"Gain{tag}", gain, "{:,.0f}")
            mac(f"Loss{tag}", loss, "{:,.0f}")
            mac(f"Waste{tag}", waste, "{:,.0f}")
    o = pd.DataFrame(out)
    mac("ScarceN", o.n.iloc[0], "{:d}")
    red = 1 - o[o.cap].loss.values / o[~o.cap].loss.values
    mac("CapRedMin", red.min() * 100, "{:.0f}")
    mac("CapRedMax", red.max() * 100, "{:.0f}")
    hc = d[d.case == "honest_cap"].set_index(["city", "year", "day"])
    sc = hc.supply_ratio < 1
    mac("CapCostScarce", -(hc.others_useful - hh.others_useful)[sc].mean(), "{:,.0f}")
    mac("CapCostSurplus", -(hc.others_useful - hh.others_useful)[~sc].mean(), "{:,.0f}")
    mac("CapCostScarceLiar", -(hc.liar_useful - hh.liar_useful)[sc].mean(), "{:,.0f}")
    for c in CITY_ORDER:
        mac(f"ScarceShare{c}", (h[h.city == c].supply_ratio < 1).mean() * 100, "{:.0f}")
    # figure: gap distribution and misreport effects
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.3), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    vals = np.maximum(h.gap.values * 100, 1e-6)
    ax.hist(np.log10(vals), bins=24, color=C["blue"], edgecolor="white", linewidth=0.8)
    ax.set_xlabel("Gap to centralized optimum (%)")
    ax.set_xticks([-5, -4, -3, -2, -1], [r"$10^{-5}$", r"$10^{-4}$", r"$10^{-3}$", r"$10^{-2}$", r"$10^{-1}$"])
    ax.set_ylabel("Instances")
    ax.set_title("a  Negotiation fidelity")
    ax.grid(axis="x", visible=False)
    ax = axes[1]
    labels = ["+30%", "+60%", "+100%"]
    x = np.arange(3)
    no = o[~o.cap].loss.values / 1e3
    yes = o[o.cap].loss.values / 1e3
    ax.bar(x - 0.17, no, width=0.32, color=C["orange"], label="No verification cap")
    ax.bar(x + 0.17, yes, width=0.32, color=C["blue"], label="Cap from metered history")
    ax.set_xticks(x, labels)
    ax.set_xlabel("Over-declared eligible demand (one sector)")
    ax.set_ylabel("Honest sectors' loss\n(thousand m$^3$ per 7 days)")
    ax.set_title("b  Misreporting under scarcity")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left")
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_e2")
    return o


# ============================================================================ E3a
TWIN_MARGIN = 2.0   # m, the margin declared in mawricx/assurance.py
MARGINS = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)
SEVERE_M = 10.0    # m below a limit: the node has effectively lost supply
BOOT_E3A = 2000    # context-level bootstrap resamples for E3a intervals
FAULT_NAME = {"none": "None (nominal plan)", "corrupt": "Corrupted values", "stale": "Stale state",
              "adversarial": "Adversarial", "unit": "Unit error", "fdi": "False data injection",
              "fdi_stealth": "Stealthy injection"}


def e3a():
    e = pd.read_csv(RES / f"e3_assurance_{TAG}.csv")
    chk_f = RES / f"e3a_serial_check_{TAG}.csv"
    if chk_f.exists():
        chk = pd.read_csv(chk_f)
        assert chk.mismatches.sum() == 0, "serial re-run disagrees with the parallel E3a run"
        mac("SerialRows", int(chk.rows.iloc[0]), "{:d}")
    e["twin_error"] = e["twin_error"].fillna("") if "twin_error" in e else ""
    rows, sweep, fault_rows = [], [], []
    cfg = [("A0", "A0 none"), ("A1", "A1 rules"), ("A2", "A2 twin"), ("A3", "A3 twin + plausibility"),
           ("A13", "A1 + A3")]
    for net in ("Net6.inp", "Net3.inp"):
        xa = e[e.net == net]
        nm = net.replace(".inp", "")
        mn = {"Net6": "NetSix", "Net3": "NetThree"}[nm]
        mac(f"Props{mn}", len(xa), "{:,d}")
        mac(f"Invalid{mn}", int(xa.invalid.sum()), "{:d}")
        # schema-invalid proposals name assets that do not exist; every configuration except A0 rejects
        # them at the schema check, so rates are reported over schema-valid proposals
        x = xa[xa.invalid == 0]
        unsafe = x.unsafe == 1
        safe = ~unsafe
        ben = safe & (x.saving_usd > 0)
        mac(f"Valid{mn}", len(x), "{:,d}")
        mac(f"Unsafe{mn}", int(unsafe.sum()), "{:d}")
        mac(f"Fail{mn}", int((x.sim_failed == 1).sum() + (x.default_failed == 1).sum()), "{:d}")
        mac(f"TwinErr{mn}", int((x.twin_error != "").sum()), "{:d}")
        assert ((x.crit_A2 >= TWIN_MARGIN) == (x.A2 == 1)).all(), "stored critical slack disagrees with A2"
        assert ((x.crit_A3 >= TWIN_MARGIN) == (x.A3 == 1)).all(), "stored critical slack disagrees with A3"

        def rates(acc, sub=None):
            sub = np.ones(len(x), bool) if sub is None else sub
            u, s, b = unsafe & sub, safe & sub, ben & sub
            ue = (acc & u).sum() / max(1, u.sum()) * 100
            fr = (~acc & s).sum() / max(1, s.sum()) * 100
            sk = x.saving_usd[acc & b].sum() / max(1e-9, x.saving_usd[b].sum()) * 100
            return ue, fr, sk

        # 95% intervals by resampling contexts, because the proposals of one context share its state
        ids, inv = np.unique(x.context.to_numpy(), return_inverse=True)
        brng = np.random.default_rng([20261016, 31, {"Net6": 6, "Net3": 3}[nm]])
        W = brng.multinomial(len(ids), np.full(len(ids), 1.0 / len(ids)), size=BOOT_E3A)
        u_np, s_np, b_np, sav_np = unsafe.to_numpy(), safe.to_numpy(), ben.to_numpy(), x.saving_usd.to_numpy()

        def per_ctx(v):
            return np.bincount(inv, weights=np.asarray(v, float), minlength=len(ids))

        den_u, den_s, den_b = W @ per_ctx(u_np), W @ per_ctx(s_np), W @ per_ctx(b_np * sav_np)

        def boot(acc):
            acc = np.asarray(acc, bool)
            return (W @ per_ctx(acc & u_np) / np.maximum(den_u, 1) * 100,
                    W @ per_ctx(~acc & s_np) / np.maximum(den_s, 1) * 100,
                    W @ per_ctx((acc & b_np) * sav_np) / np.maximum(den_b, 1e-9) * 100)

        def add_row(code, lab, acc, an=None):
            ue, fr, sk = rates(pd.Series(np.asarray(acc, bool), index=x.index))
            bu, bs, bk = boot(acc)
            (ul, uh), (sl, sh), (kl, kh) = (np.percentile(v, [2.5, 97.5]) for v in (bu, bs, bk))
            rows.append({"net": nm, "cfg": code, "label": lab, "unsafe_exec": ue, "safe_rej": fr, "saving_kept": sk,
                         "ue_lo": ul, "ue_hi": uh, "sr_lo": sl, "sr_hi": sh, "sk_lo": kl, "sk_hi": kh})
            if an:
                mac(f"UE{an}{mn}", ue, "{:.1f}")
                mac(f"SR{an}{mn}", fr, "{:.1f}")
                mac(f"SK{an}{mn}", sk, "{:.0f}")
                for key, lo, hi, fmt in (("UE", ul, uh, "{:.1f}"), ("SR", sl, sh, "{:.1f}"), ("SK", kl, kh, "{:.0f}")):
                    mac(f"{key}{an}Lo{mn}", lo, fmt)
                    mac(f"{key}{an}Hi{mn}", hi, fmt)

        for a, lab in cfg:
            add_row(a, lab, (x[a] == 1).to_numpy(),
                    {"A0": "None", "A1": "Rules", "A2": "Twin", "A3": "Plaus", "A13": "Full"}[a])
        # rules minus twin with plausibility, on the same resampled contexts
        (u1, s1, _), (u3, s3, _) = boot((x.A1 == 1).to_numpy()), boot((x.A3 == 1).to_numpy())
        r1, r3 = rates(x.A1 == 1), rates(x.A3 == 1)
        for key, diff, point in (("UE", u1 - u3, r1[0] - r3[0]), ("SR", s1 - s3, r1[1] - r3[1])):
            lo, hi = np.percentile(diff, [2.5, 97.5])
            mac(f"Diff{key}{mn}", point, "{:.1f}")
            mac(f"Diff{key}Lo{mn}", lo, "{:.1f}")
            mac(f"Diff{key}Hi{mn}", hi, "{:.1f}")
        # value of nominal (fault-free) proposals and the source of the saving pool
        nom = (x.fault == "none").values
        for a, an in (("A1", "Rules"), ("A3", "Plaus")):
            mac(f"SKNom{an}{mn}", rates(x[a] == 1, nom)[2], "{:.0f}")
        longp = x.fault.isin(["adversarial", "fdi", "fdi_stealth"])
        mac(f"SavShareLong{mn}", x.saving_usd[ben & longp].sum() / x.saving_usd[ben].sum() * 100, "{:.0f}")
        # margin sweep: the twin decision at margin m is (critical slack >= m)
        for m in MARGINS:
            for a in ("A2", "A3", "A13"):
                acc = (x.crit_A2 >= m) if a == "A2" else (x.crit_A3 >= m)
                if a == "A13":
                    acc = acc & (x.A1 == 1)
                ue, fr, sk = rates(acc)
                sweep.append({"net": nm, "cfg": a, "margin": m, "unsafe_exec": ue, "safe_rej": fr, "saving_kept": sk})
        for m, mm in ((1.0, "One"), (3.0, "Three")):
            ue, fr, sk = rates(x.crit_A3 >= m)
            mac(f"UEPlaus{mm}m{mn}", ue, "{:.1f}")
            mac(f"SRPlaus{mm}m{mn}", fr, "{:.1f}")
            mac(f"SKPlaus{mm}m{mn}", sk, "{:.0f}")
        # severity of the unsafe proposals each configuration let through (ground truth). Depths beyond
        # SEVERE_M are nodes that the network can no longer supply: EPANET's demand-driven solution then
        # reports pressures thousands of metres below zero, so counts are reported instead of depths.
        for a, an in (("A1", "Rules"), ("A3", "Plaus"), ("A13", "Full")):
            d = x.truth_depth[(x[a] == 1) & unsafe].dropna()
            mac(f"UECount{an}{mn}", int(((x[a] == 1) & unsafe).sum()), "{:d}")
            mac(f"Severe{an}{mn}", int((d > SEVERE_M).sum()), "{:d}")
            mild = d[d <= SEVERE_M]
            mac(f"DepthMax{an}{mn}", mild.max() if len(mild) else 0.0, "{:.1f}")
        # FDI-specific: unsafe injected plans accepted by the twin with raw (A2) and filtered (A3) telemetry
        fd = x[(x.fault == "fdi") & unsafe]
        mac(f"FdiUnsafe{mn}", len(fd), "{:d}")
        mac(f"FdiAtwo{mn}", fd.A2.mean() * 100 if len(fd) else 0, "{:.0f}")
        mac(f"FdiAthree{mn}", fd.A3.mean() * 100 if len(fd) else 0, "{:.0f}")
        mac(f"FdiAtwoCount{mn}", int(fd.A2.sum()), "{:d}")
        mac(f"FdiAthreeCount{mn}", int(fd.A3.sum()), "{:d}")
        # stealthy injection: unsafe plans accepted by the twin with raw (A2) and filtered (A3) telemetry
        st = x[(x.fault == "fdi_stealth") & unsafe]
        mac(f"StealthUnsafe{mn}", len(st), "{:d}")
        mac(f"StealthAtwo{mn}", st.A2.mean() * 100 if len(st) else 0, "{:.0f}")
        mac(f"StealthAthree{mn}", st.A3.mean() * 100 if len(st) else 0, "{:.0f}")
        mac(f"StealthAthreeCount{mn}", int(st.A3.sum()), "{:d}")
        # post hoc ensemble twin (A3e): A3 plus four perturbed twin states (analysis/e3a_robust_twin.py)
        rob_f = RES / f"e3a_robust_{TAG}.csv"
        if rob_f.exists():
            rob = pd.read_csv(rob_f)
            xr = x.merge(rob[["net", "context", "fault", "crit_ens_min"]], on=["net", "context", "fault"], how="left")
            assert xr.crit_ens_min[xr.A3 == 1].notna().all(), "A3-accepted proposal missing from the A3e re-check"
            a3e = ((xr.A3 == 1) & (xr.crit_ens_min >= TWIN_MARGIN)).to_numpy()
            add_row("A3e", r"A3e ensemble twin$^{\dagger}$", a3e, "Ens")
            add_row("A1+A3e", r"A1 + A3e$^{\dagger}$", a3e & (x.A1 == 1).to_numpy(), "EnsFull")
            mac(f"UECountEns{mn}", int((a3e & unsafe.to_numpy()).sum()), "{:d}")
            mac(f"SKNomEns{mn}", rates(pd.Series(a3e, index=x.index), nom)[2], "{:.0f}")
        mac(f"FdiFlag{mn}", (x[x.fault == "fdi"].flagged_tanks > 0).mean() * 100, "{:.0f}")
        mac(f"StealthFlag{mn}", (x[x.fault == "fdi_stealth"].flagged_tanks > 0).mean() * 100, "{:.0f}")
        fs = x[(x.fault == "fdi") & safe]
        mac(f"FdiSafeRejAtwo{mn}", (fs.A2 == 0).mean() * 100 if len(fs) else 0, "{:.0f}")
        mac(f"FdiSafeRejAthree{mn}", (fs.A3 == 0).mean() * 100 if len(fs) else 0, "{:.0f}")
        for fault in FAULT_NAME:
            g = x[x.fault == fault]
            if not len(g):
                continue
            u, s = g[g.unsafe == 1], g[g.unsafe == 0]
            fault_rows.append({"net": nm, "fault": fault, "n": len(g), "unsafe": len(u),
                               "A1_exec_unsafe": u.A1.mean() * 100 if len(u) else np.nan,
                               "A3_exec_unsafe": u.A3.mean() * 100 if len(u) else np.nan,
                               "A1_rej_safe": (1 - s.A1.mean()) * 100 if len(s) else np.nan,
                               "A3_rej_safe": (1 - s.A3.mean()) * 100 if len(s) else np.nan})
    t = pd.DataFrame(rows)
    sw = pd.DataFrame(sweep)
    sw.to_csv(RES / f"e3a_margin_sweep_{TAG}.csv", index=False)
    fr_df = pd.DataFrame(fault_rows)
    fr_df.to_csv(RES / f"e3a_by_fault_{TAG}.csv", index=False)
    # diagnosis of the unsafe proposals that A3 accepted (analysis/e3a_twin_misses.py)
    miss_f = RES / f"e3a_twin_misses_{TAG}.csv"
    if miss_f.exists():
        ms = pd.read_csv(miss_f)
        n6, n3 = ms[ms.net == "Net6"], ms[ms.net == "Net3"]
        mac("MissAll", len(ms), "{:d}")
        mac("SwitchDiffAll", int(ms.switch_differs.sum()), "{:d}")
        mac("SwitchDiffNetSix", int(n6.switch_differs.sum()), "{:d}")
        mac("SwitchDiffNetThree", int(n3.switch_differs.sum()), "{:d}")
        nosw = ms[ms.switch_differs == 0]
        mac("MissNoSwitch", len(nosw), "{:d}")
        mac("MissNoSwitchMaxDepth", nosw.depth.max() if len(nosw) else 0.0, "{:.2f}")
        mac("MissNoSwitchDmErr", -nosw.dm_error.max() * 100 if len(nosw) else 0.0, "{:.0f}")
        mac("TankEmptyNetThree", int(n3.tank_emptied.sum()), "{:d}")
        mac("MissOverNetSix", int((n6.types == "over").sum()), "{:d}")
        mac("MissMaxDepthNetSix", n6.depth.max(), "{:.1f}")
        mac("MissLateNetThree", int((n3.worst_hour >= 22).sum()), "{:d}")
        rob_f = RES / f"e3a_robust_{TAG}.csv"
        if rob_f.exists():
            rob = pd.read_csv(rob_f)
            rob["net"] = rob.net.str.replace(".inp", "", regex=False)
            mr = ms.merge(rob, on=["net", "context", "fault"], how="left")
            caught = mr.crit_ens_min < TWIN_MARGIN
            left = mr[~caught]
            mac("EnsCaught", int(caught.sum()), "{:d}")
            mac("EnsCaughtEmpty", int((caught & (mr.tank_emptied == 1)).sum()), "{:d}")
            mac("EnsCaughtHighDemand", int((caught & (mr.crit_m0 < TWIN_MARGIN)).sum()), "{:d}")
            mac("EnsLeft", len(left), "{:d}")
            mac("EnsLeftLastHour", int((left.worst_hour == 24).sum()), "{:d}")
    # figure: trade-off curves over the twin margin, with the fixed configurations as points.
    # A0 (no assurance) sits at 100% unsafe executed and 0% safe rejected on both networks.
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.9))
    series = (("A2", "A2 twin", C["blue"]), ("A3", "A3 twin + plausibility", C["orange"]),
              ("A13", "A1 + A3", C["aqua"]))
    for ax, nm in zip(axes, ("Net6", "Net3")):
        g = sw[sw.net == nm]
        for a, lab, col in series:
            s = g[g.cfg == a].sort_values("margin")
            ax.plot(s.safe_rej, s.unsafe_exec, color=col, lw=2, zorder=2, label=lab)
            ax.scatter(s.safe_rej, s.unsafe_exec, s=10, color=col, zorder=3)
            m2 = s[s.margin == TWIN_MARGIN]
            ax.scatter(m2.safe_rej, m2.unsafe_exec, s=46, color=col, edgecolor="white", linewidth=1.5, zorder=4)
        pts = [("A1", "A1 rules", "D", 48)] + ([("A3e", "A3e ensemble twin", "^", 80)] if (t.cfg == "A3e").any() else [])
        for a, lab, mk, size in pts:
            r = t[(t.net == nm) & (t.cfg == a)].iloc[0]
            ax.scatter([r.safe_rej], [r.unsafe_exec], s=size, marker=mk, color=INK, edgecolor="white",
                       linewidth=1.2, zorder=5, label=lab)
        s3 = g[g.cfg == "A3"].sort_values("margin")
        for m, dx, dy in ((0.0, -4, 6), (5.0, 2, 6)):
            r = s3[s3.margin == m].iloc[0]
            ax.annotate(f"{m:.0f} m", (r.safe_rej, r.unsafe_exec), xytext=(dx, dy), textcoords="offset points",
                        fontsize=7, color=INK2)
        ymax = max(g.unsafe_exec.max(), t[t.net == nm].query("cfg != 'A0'").unsafe_exec.max())
        ax.set_title(f"{nm} ({'3,323' if nm == 'Net6' else '92'} junctions)")
        ax.set_xlabel("Safe proposals rejected (%)")
        ax.set_xlim(-2, 72)
        ax.set_ylim(-1, ymax * 1.15 + 1)
    axes[0].set_ylabel("Unsafe proposals executed (%)")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1.02), handlelength=1.6,
               columnspacing=1.2)
    fig.tight_layout(w_pad=1.2, rect=(0, 0, 1, 0.9))
    save(fig, "fig_e3a")
    def with_ci(v, lo, hi, fmt):
        s = fmt.format(v)
        return s if abs(hi - lo) < 1e-9 else f"{s} [{fmt.format(lo)}, {fmt.format(hi)}]"

    lines = []
    for nm in ("Net6", "Net3"):
        for _, r in t[t.net == nm].iterrows():
            lines.append(f"{nm} & {r.label} & {with_ci(r.unsafe_exec, r.ue_lo, r.ue_hi, '{:.1f}')} & "
                         f"{with_ci(r.safe_rej, r.sr_lo, r.sr_hi, '{:.1f}')} & "
                         f"{with_ci(r.saving_kept, r.sk_lo, r.sk_hi, '{:.0f}')} \\\\")
        if nm == "Net6":
            lines.append(r"\midrule")
    (TAB / "tab_e3a.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def cell(v):
        return "--" if pd.isna(v) else f"{v:.0f}"

    fl = []
    for nm in ("Net6", "Net3"):
        for _, r in fr_df[fr_df.net == nm].iterrows():
            fl.append(f"{nm} & {FAULT_NAME[r.fault]} & {r.unsafe}/{r.n} & {cell(r.A1_exec_unsafe)} & "
                      f"{cell(r.A3_exec_unsafe)} & {cell(r.A1_rej_safe)} & {cell(r.A3_rej_safe)} \\\\")
        if nm == "Net6":
            fl.append(r"\midrule")
    (TAB / "tab_e3a_fault.tex").write_text("\n".join(fl) + "\n", encoding="utf-8")
    return t


# ============================================================================ E3b
def e3b():
    d = pd.read_csv(RES / f"e3b_leak_{TAG}.csv")
    meta = pd.read_csv(RES / f"e3b_network_{TAG}.csv").iloc[0]
    mac("NetKm", meta.total_km, "{:.0f}")
    mac("NetValves", meta.n_valves, "{:,.0f}")
    mac("NetSegments", meta.n_segments, "{:,.0f}")
    mac("NetProtSeg", meta.protected_segments, "{:,.0f}")
    nom = d[d.case == "nominal"]
    mac("EThreeBYears", nom.year.nunique(), "{:d}")
    rows = []
    for pol in ("HUMAN", "AUTO", "MAWRICX"):
        g = nom[nom.policy == pol]
        lo, hi = boot_ci(g.lost_m3)
        rows.append({"policy": pol, "lost": g.lost_m3.mean(), "lo": lo, "hi": hi, "tiso": g.mean_t_isolate_h.mean(),
                     "approvals": g.approvals.mean(), "crew": g.crew_false_h.mean(), "prot": g.prot_unapproved.mean(),
                     "undel": g.undelivered_m3.mean()})
        p = pol.title() if pol != "MAWRICX" else "Mx"
        mac(f"Lost{p}", g.lost_m3.mean(), "{:,.0f}")
        mac(f"LostLo{p}", lo, "{:,.0f}")
        mac(f"LostHi{p}", hi, "{:,.0f}")
        mac(f"Tiso{p}", g.mean_t_isolate_h.mean(), "{:.1f}")
        mac(f"Appr{p}", g.approvals.mean(), "{:.1f}")
        mac(f"Crew{p}", g.crew_false_h.mean(), "{:.0f}")
        mac(f"Prot{p}", g.prot_unapproved.mean(), "{:.1f}")
    mac("Bursts", nom.n_bursts.mean(), "{:.0f}")
    mac("Falses", nom.n_false.mean(), "{:.0f}")
    pv = nom.pivot_table(index="year", columns="policy", values="lost_m3")
    st = wilcoxon(pv.HUMAN, pv.MAWRICX)
    mac("PLeakHM", fmt_p(st.pvalue))
    mac("ApprRed", (1 - nom[nom.policy == "MAWRICX"].approvals.mean() /
                    nom[nom.policy == "HUMAN"].approvals.mean()) * 100, "{:.0f}")
    mac("CrewRed", (1 - nom[nom.policy == "MAWRICX"].crew_false_h.mean() /
                    nom[nom.policy == "HUMAN"].crew_false_h.mean()) * 100, "{:.0f}")
    lat = d[d.case == "approve_day_h"].groupby(["value", "policy"]).lost_m3.mean().unstack()
    # loss rise across the sweep range (0.25 h to 4 h daytime latency), in percent
    mac("LatRiseMx", (lat.loc[4.0, "MAWRICX"] / lat.loc[0.25, "MAWRICX"] - 1) * 100, "{:.0f}")
    mac("LatRiseHuman", (lat.loc[4.0, "HUMAN"] / lat.loc[0.25, "HUMAN"] - 1) * 100, "{:.0f}")
    # sweep points use the same simulated years (common random numbers); 95% bands by bootstrap over years
    latd = d[d.case == "approve_day_h"]
    mac("SweepYears", latd.year.nunique(), "{:d}")
    srng = np.random.default_rng([20261016, 32])

    def band(x, n=10000):
        x = np.asarray(x, float)
        s = x[srng.integers(0, len(x), (n, len(x)))].mean(axis=1)
        return np.percentile(s, 2.5), np.percentile(s, 97.5)

    lat_band = {k: band(g.lost_m3) for k, g in latd.groupby(["value", "policy"])}
    if (d.case == "q_median_ls").any():
        qd = d[d.case == "q_median_ls"]
        qs = qd.groupby(["value", "policy"]).lost_m3.mean().unstack()
        for v, tag in zip(sorted(qs.index), "ABCD"):
            mac(f"BurstQ{tag}", v, "{:g}")
            for pol, p in (("HUMAN", "Human"), ("MAWRICX", "Mx"), ("AUTO", "Auto")):
                mac(f"BurstLost{p}{tag}", qs.loc[v, pol], "{:,.0f}")
            mac(f"BurstGap{tag}", (qs.loc[v, "HUMAN"] - qs.loc[v, "MAWRICX"]) / qs.loc[v, "HUMAN"] * 100, "{:.0f}")
        pv_q = qd[qd.value == max(qs.index)].pivot_table(index="year", columns="policy", values="lost_m3")
        pb = wilcoxon(pv_q.HUMAN, pv_q.MAWRICX).pvalue
        mac("PBurstHM", fmt_p(pb) if pb < 0.001 else f"$= {pb:.3f}$")
    for v in lat.index:
        tag = {0.25: "A", 0.5: "B", 1.0: "C", 2.0: "D", 4.0: "E"}[v]
        mac(f"LatHuman{tag}", lat.loc[v, "HUMAN"], "{:,.0f}")
        mac(f"LatMx{tag}", lat.loc[v, "MAWRICX"], "{:,.0f}")
        mac(f"LatAuto{tag}", lat.loc[v, "AUTO"], "{:,.0f}")
    rob = d[d.case == "robots"].groupby(["value", "policy"])[["lost_m3", "crew_false_h"]].mean().unstack()
    mac("RobZeroCrew", rob.loc[0, ("crew_false_h", "MAWRICX")], "{:.0f}")
    mac("RobTwoCrew", rob.loc[2, ("crew_false_h", "MAWRICX")], "{:.0f}")
    # crew and robot sensitivities (50-year sweeps); intervals are bootstrap over simulated years
    for v, tag in ((2.0, "Two"), (3.0, "Three"), (5.0, "Five")):
        for pol, p in (("MAWRICX", "Mx"), ("HUMAN", "Human")):
            g = d[(d.case == "crews") & (d.value == v) & (d.policy == pol)]
            lo, hi = boot_ci(g.lost_m3)
            mac(f"CrewSweepLost{tag}{p}", g.lost_m3.mean(), "{:,.0f}")
            mac(f"CrewSweepLo{tag}{p}", lo, "{:,.0f}")
            mac(f"CrewSweepHi{tag}{p}", hi, "{:,.0f}")
    for v, tag in ((0.0, "Zero"), (1.0, "One"), (2.0, "Two"), (4.0, "Four")):
        g = d[(d.case == "robots") & (d.value == v) & (d.policy == "MAWRICX")]
        lo, hi = boot_ci(g.lost_m3)
        mac(f"RobSweepLost{tag}", g.lost_m3.mean(), "{:,.0f}")
        mac(f"RobSweepLo{tag}", lo, "{:,.0f}")
        mac(f"RobSweepHi{tag}", hi, "{:,.0f}")
    fal = d[d.case == "false_per_week"].groupby(["value", "policy"]).crew_false_h.mean().unstack()
    mac("FalseFiveCrewHuman", fal.loc[5.0, "HUMAN"], "{:.0f}")
    mac("FalseFiveCrewMx", fal.loc[5.0, "MAWRICX"], "{:.0f}")
    # figure
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.4), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    for pol, lab, col in (("HUMAN", "Human approval for every action", C["orange"]),
                          ("MAWRICX", "MAWRIC-X autonomy envelope", C["blue"]),
                          ("AUTO", "Full autonomy", C["aqua"])):
        lo = [lat_band[(v, pol)][0] / 1e3 for v in lat.index]
        hi = [lat_band[(v, pol)][1] / 1e3 for v in lat.index]
        ax.fill_between(lat.index, lo, hi, color=col, alpha=0.18, lw=0)
        ax.plot(lat.index, lat[pol] / 1e3, marker="o", ms=3.5, lw=2.0, color=col, label=lab)
    ax.set_xscale("log", base=2)
    ax.set_xticks([0.25, 0.5, 1, 2, 4], ["0.25", "0.5", "1", "2", "4"])
    ax.minorticks_off()
    ax.set_xlabel("Median daytime approval latency (h)")
    ax.set_ylabel("Real losses from bursts\n(thousand m$^3$/yr)")
    ax.set_title("a  Latency of human approval")
    ax.legend(loc="upper left", fontsize=6.8)
    ax = axes[1]
    pols = ["HUMAN", "MAWRICX", "AUTO"]
    r = pd.DataFrame(rows).set_index("policy")
    x = np.arange(3)
    ax.bar(x - 0.17, [r.loc[p, "approvals"] for p in pols], width=0.32, color=C["violet"], label="Operator approvals")
    ax.bar(x + 0.17, [r.loc[p, "crew"] for p in pols], width=0.32, color=C["magenta"], label="Crew hours on false alarms")
    ax.set_xticks(x, ["Human", "MAWRIC-X", "Full\nautonomy"])
    ax.set_ylabel("Per year")
    ax.set_title("b  Workload")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", fontsize=6.8)
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_e3b")
    lines = []
    for p, lab in (("HUMAN", "Human approval for every action"), ("MAWRICX", "MAWRIC-X envelope"),
                   ("AUTO", "Full autonomy")):
        q = r.loc[p]
        lines.append(f"{lab} & {q.lost:,.0f} [{q.lo:,.0f}, {q.hi:,.0f}] & {q.tiso:.1f} & {q.approvals:.1f} & "
                     f"{q.crew:.0f} & {q.prot:.1f} \\\\")
    (TAB / "tab_e3b.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return r


# ============================================================================ E4
def e4():
    r = pd.read_csv(RES / f"e4_economics_{TAG}.csv").set_index("city")
    s = pd.read_csv(RES / f"e4_sobol_{TAG}.csv")
    for c in CITY_ORDER:
        q = r.loc[c]
        mac(f"Ben{c}", q.benefit_mean / 1e3, "{:,.0f}")
        mac(f"Eac{c}", q.eac_mean / 1e6, "{:.2f}")
        mac(f"Npv{c}", q.npv_mean / 1e6, "{:.1f}")
        mac(f"NpvLo{c}", q.npv_p05 / 1e6, "{:.1f}")
        mac(f"NpvHi{c}", q.npv_p95 / 1e6, "{:.1f}")
        mac(f"PPos{c}", q.p_npv_pos * 100, "{:.1f}")
        mac(f"PPosSoc{c}", q.p_npv_soc_pos * 100, "{:.1f}")
        mac(f"BeEac{c}", q.breakeven_eac_p50 / 1e3, "{:,.0f}")
        mac(f"BeEacTen{c}", q.breakeven_eac_p10 / 1e3, "{:,.0f}")
        mac(f"Dco{c}", q.dco2_mean, "{:,.0f}")
        g = s[s.city == c].sort_values("ST", ascending=False)
        mac(f"TopOne{c}", g.param.iloc[0].replace("_", r"\_"))
        mac(f"TopOneST{c}", g.ST.iloc[0], "{:.2f}")
        mac(f"STopex{c}", g.set_index("param").loc["opex_platform", "ST"], "{:.2f}")
        mac(f"STprem{c}", g.set_index("param").loc["u_prem", "ST"], "{:.2f}")
        mac(f"STcpot{c}", g.set_index("param").loc["c_pot", "ST"], "{:.2f}")
    mac("EacMean", r.eac_mean.mean() / 1e6, "{:.2f}")
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.5), gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axes[0]
    for i, c in enumerate(CITY_ORDER):
        m = pd.read_csv(RES / f"e4_mc_sample_{c}_{TAG}.csv")
        v = m.npv.values / 1e6
        parts = ax.violinplot([v], positions=[i], widths=0.7, showextrema=False)
        for b in parts["bodies"]:
            b.set_facecolor(CITY_COL[c])
            b.set_alpha(0.35)
            b.set_edgecolor("none")
        ax.plot([i - 0.18, i + 0.18], [np.median(v)] * 2, color=INK, lw=1.6)
    ax.axhline(0, color=C["red"], lw=1.0)
    ax.set_xticks(range(4), [CITY_NAME[c] for c in CITY_ORDER], fontsize=7)
    ax.set_ylabel("15-year NPV (million USD)")
    ax.set_title("a  Coordination layer NPV")
    ax.grid(axis="x", visible=False)
    ax = axes[1]
    keys = ["opex_platform", "u_prem", "c_pot", "capex_platform", "discount"]
    labs = ["Platform O&M", "Coordination premium", "Potable marginal cost", "Platform capital", "Discount rate"]
    y = np.arange(len(keys))
    for j, c in enumerate(CITY_ORDER):
        g = s[s.city == c].set_index("param")
        ax.barh(y + (j - 1.5) * 0.19, [g.loc[k, "ST"] for k in keys], height=0.17, color=CITY_COL[c],
                label=CITY_NAME[c])
    ax.set_yticks(y, labs)
    ax.invert_yaxis()
    ax.set_xlabel("Sobol total-effect index")
    ax.set_title("b  What drives NPV")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=6.5)
    fig.tight_layout(w_pad=1.0)
    save(fig, "fig_e4")
    lines = []
    for c in CITY_ORDER:
        q = r.loc[c]
        lines.append(f"{CITY_NAME[c]} & {q.benefit_mean / 1e3:,.0f} & {q.breakeven_eac_p50 / 1e3:,.0f} & "
                     f"{q.eac_mean / 1e6:.2f} & {q.npv_mean / 1e6:.1f} [{q.npv_p05 / 1e6:.1f}, {q.npv_p95 / 1e6:.1f}] & "
                     f"{q.p_npv_pos * 100:.1f} \\\\")
    (TAB / "tab_e4.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return r


def write_macros():
    out = ["% Auto-generated by analysis/make_results.py from results/*.csv. Do not edit by hand."]
    for k in sorted(MAC):
        name = "".join(ch for ch in k if ch.isalpha())
        if name != k:
            raise ValueError(f"macro name must be letters only: {k}")
        out.append(f"\\newcommand{{\\{k}}}{{{minus(MAC[k])}}}")
    (MS / "numbers.tex").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {len(MAC)} macros to manuscript/numbers.tex")


# ============================================================================ parameter table (Appendix A)
def params_table():
    sys.path.insert(0, str(ROOT))
    from mawricx.config import E1_LHS_KEYS, P
    desc = {
        "pop": "Residents", "res_lpcd": "Residential indoor use", "res_np": "Toilet share of residential indoor use",
        "res_area": "Irrigated private gardens", "hos_in": "Hotel indoor use", "hos_np": "Non-potable share, hotels",
        "hea_beds": "Hospital beds", "hea_m3_bed_yr": r"Hospital use per bed~\cite{gonzalez2018}",
        "hea_np": "Non-clinical toilet share, hospitals", "edu_in": "School-day indoor use",
        "edu_np": "Toilet share, schools", "com_in": "Weekday commercial indoor use",
        "com_np": "Toilet share, commercial", "com_cool": r"Commercial cooling above 22 $^\circ$C",
        "hos_cool": r"Hotel cooling above 24 $^\circ$C", "ind_proc": "Weekday industrial process use",
        "ind_np": "Industrial use fit for reclaimed water", "dct_base": "Data-center cooling, base",
        "dct_slope": r"Data-center cooling above 15 $^\circ$C", "lan_area": "Irrigated public landscape",
        "minor_area": "Irrigated grounds of other sectors", "con_use": "Construction dust control, dry days",
        "pub_in": "Municipal buildings indoor use", "pub_clean": "Street cleaning, dry days",
        "kc": r"Crop coefficient~\cite{allen1998}", "irr_eff": "Irrigation efficiency",
        "raw_mm": r"Readily available water~\cite{allen1998}",
        "cR_res": "Reclaimed reach, residential", "cR_nonres_in": "Reclaimed reach, other indoor",
        "cR_cool": "Reclaimed reach, cooling", "cR_ind": "Reclaimed reach, industry",
        "cR_dct": "Reclaimed reach, data centers", "cR_out": "Reclaimed reach, other irrigation",
        "cR_lan": "Reclaimed reach, public landscape", "cR_con": "Reclaimed reach, construction",
        "cR_pub": "Reclaimed reach, public services", "cS_res": "Stormwater reach, residential irrigation",
        "cS_out": "Stormwater reach, other irrigation", "cS_lan": "Stormwater reach, public landscape",
        "cS_con": "Stormwater reach, construction", "cS_pub": "Stormwater reach, public services",
        "return_factor": "Wastewater return factor", "tert_frac": "Tertiary capacity / mean inflow",
        "tert_recovery": "Tertiary recovery", "R_store_days": "Reclaimed storage",
        "R_dist_peak": "Reclaimed delivery peak factor", "catch_km2": "Contributing catchment",
        "runoff_c": "Runoff coefficient", "init_loss_mm": "Initial abstraction", "S_intake": "Stormwater intake",
        "S_store": "Stormwater storage", "S_dist": "Stormwater delivery capacity",
        "c_pot": "Potable marginal cost", "c_rec": r"Reclaimed marginal cost~\cite{giammar2021}",
        "c_sto": "Stormwater marginal cost",
        "e_pot": "Potable energy intensity", "e_rec": r"Reclaimed energy intensity~\cite{giammar2021}",
        "e_sto": "Stormwater energy intensity", "ef_grid": "Grid emission factor",
    }
    unit_tex = {"km2": "km$^2$", "m3/d": "m$^3$/d", "m3": "m$^3$", "m3/bed/yr": "m$^3$/bed/yr",
                "m3/d/degC": r"m$^3$/d/$^\circ$C", "USD/m3": "USD/m$^3$", "kWh/m3": "kWh/m$^3$",
                "kgCO2e/kWh": "kgCO$_2$e/kWh", "L/cap/d": "L/cap/d", "-": "--"}

    def num(v):
        if abs(v) >= 1e5:
            return f"{v:,.0f}"
        if abs(v) >= 100:
            return f"{v:,.0f}"
        return f"{v:g}"

    lines = []
    for k, prm in P.items():
        rng = f"{num(prm.low)}--{num(prm.high)}" if prm.low != prm.high else "fixed"
        star = r"$^{\ast}$" if k in E1_LHS_KEYS else ""
        lines.append(f"{desc[k]}{star} & {num(prm.nominal)} & {rng} & {unit_tex.get(prm.unit, prm.unit)} \\\\")
    half = (len(lines) + 1) // 2
    (TAB / "tab_params_a.tex").write_text("\n".join(lines[:half]) + "\n", encoding="utf-8")
    (TAB / "tab_params_b.tex").write_text("\n".join(lines[half:]) + "\n", encoding="utf-8")
    mac("NParams", len(lines), "{:d}")
    mac("NLhs", len(E1_LHS_KEYS), "{:d}")



def write_table_macros():
    """Wrap each generated table body in a macro (expands safely inside tabularx)."""
    names = {"tab_e1": "TabEOne", "tab_e3a": "TabEThreeA", "tab_e3b": "TabEThreeB", "tab_e4": "TabEFour",
             "tab_params_a": "TabParamsA", "tab_params_b": "TabParamsB", "tab_e3a_fault": "TabEThreeAFault"}
    out = ["% Auto-generated by analysis/make_results.py from results/*.csv. Do not edit by hand."]
    for stem, mac_name in names.items():
        f = TAB / f"{stem}.tex"
        if f.exists():
            body = minus(f.read_text(encoding="utf-8").strip())
            out.append("\\newcommand{\\" + mac_name + "}{%\n" + body + "%\n}")
    (MS / "tabledefs.tex").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote table macros to manuscript/tabledefs.tex")


if __name__ == "__main__":
    climate()
    e1()
    e2()
    e3a()
    e3b()
    e4()
    params_table()
    write_macros()
    write_table_macros()
