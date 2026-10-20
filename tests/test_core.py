"""Fast checks of the core components and of the manuscript macros.

Run from the project root:  python -m pytest tests -q
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
MS = ROOT / "manuscript"


def test_twin_rule_matches_critical_slack():
    """The stored critical slack reproduces the twin decision at every margin (basis of the margin sweep)."""
    import e3_assurance as E
    from mawricx import assurance as AS
    rng = np.random.default_rng(1)
    keys = [("node", i) for i in range(6)]
    for _ in range(3000):
        sd = {k: float(rng.uniform(-1.0, 6.0)) for k in keys}
        sp = {k: sd[k] + float(rng.normal(0.0, 1.5)) for k in keys}
        for m in (0.0, 0.5, 2.0, 3.5):
            assert AS.unsafe_by_slack(sp, sd, margin=m) == (E._crit(sp, sd) < m)
    assert AS.unsafe_by_slack(None, {}) and E._crit(None, {}) == -np.inf
    assert not AS.unsafe_by_slack({}, None) and E._crit({}, None) == np.inf


def test_shapley_values_sum_to_premium():
    import e1_coordination as E1
    rng = np.random.default_rng(2)
    rows = []
    names = ["SILOED", "MAWRICX", "P1I0F0", "P0I1F0", "P0I0F1", "P1I1F0", "P1I0F1", "P0I1F1"]
    for year in range(3):
        for pol in names:
            rows.append({"mode": "factorial", "city": "X", "year": year, "draw": 0, "policy": pol,
                         "potable_adj": float(rng.uniform(80.0, 100.0))})
    sh = E1.shapley(pd.DataFrame(rows))
    assert np.allclose(sh[["P", "I", "F"]].sum(axis=1), sh["total"])


def test_admm_reaches_central_optimum():
    from mawricx import allocation as A
    from mawricx.agents import admm_negotiate, horizon_value
    from mawricx.city import build_city_year
    from mawricx.config import nominal_params
    from mawricx.weather import get_city_weather
    prm = nominal_params()
    cy = build_city_year(get_city_weather("LHR"), 2010, prm, tropical=False)
    t, H = 150, 7
    sl = slice(t, t + H)
    data = {"ER": cy.ER[sl], "ES": cy.ES[sl], "EA": cy.EA[sl], "prodR": cy.prodR[sl], "capS": cy.capS[sl]}
    s0R, s0S = 0.5 * cy.SRmax, 0.5 * cy.SSmax
    lp = A.AllocLP(H, True, True, prm["c_pot"], prm["c_rec"], prm["c_sto"]).solve(
        data, s0R, s0S, cy.SRmax, cy.SSmax, cy.QR, cy.QS)
    ad = admm_negotiate(data, s0R, s0S, cy.SRmax, cy.SSmax, cy.QR, cy.QS, prm)
    v_lp = horizon_value(lp["xR"], lp["xS"], data, s0R, s0S, cy.SRmax, cy.SSmax, prm, data["EA"])[0]
    v_ad = horizon_value(ad["xR"], ad["xS"], data, s0R, s0S, cy.SRmax, cy.SSmax, prm, data["EA"])[0]
    assert abs(v_ad - v_lp) <= 1e-3 * abs(v_lp)


def test_hargreaves_summer_value_is_plausible():
    from mawricx.weather import hargreaves_et0
    et0 = hargreaves_et0(np.array([35.0]), np.array([20.0]), 33.4, np.array([180]))
    assert 5.0 < float(et0[0]) < 9.0


def _defined_macros():
    n_file, t_file = MS / "numbers.tex", MS / "tabledefs.tex"
    text = ""
    if n_file.exists():
        text += n_file.read_text(encoding="utf-8")
    if t_file.exists():
        text += t_file.read_text(encoding="utf-8")
    return set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", text))


@pytest.mark.skipif(not (MS / "MAWRIC_X_Water.tex").exists(), reason="Manuscript files not present")
def test_result_macros_have_backslash():
    """A generated macro name typed without its backslash would print as plain text."""
    tex = (MS / "MAWRIC_X_Water.tex").read_text(encoding="utf-8")
    for name in _defined_macros():
        assert not re.search(r"(?<![\\A-Za-z])" + name + r"\{\}", tex), name


@pytest.mark.skipif(not (MS / "MAWRIC_X_Water.tex").exists(), reason="Manuscript files not present")
def test_used_result_macros_are_defined():
    tex = (MS / "MAWRIC_X_Water.tex").read_text(encoding="utf-8")
    used = set(re.findall(r"\\([A-Z][A-Za-z]+)", tex))
    latex = {"Title", "Author", "AuthorNames", "abstract", "PublishersNote", "Phi", "Delta", "Pi", "Sigma",
             "Huge", "LARGE", "Large", "TeX", "LaTeX"}
    missing = sorted(n for n in used - latex - _defined_macros() if not n.startswith(("Tab", "Mx")))
    assert not missing, missing
