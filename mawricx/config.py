"""Declared parameters for every MAWRIC-X experiment.

Each parameter carries a nominal value, a range used for Latin-hypercube and
Sobol sampling, and a short provenance note. "declared" means a planning
assumption chosen for the reference city, not a measured value. Values with a
literature anchor name the source key used in the manuscript bibliography.
"""
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

MASTER_SEED = 20261016


@dataclass(frozen=True)
class Param:
    nominal: float
    low: float
    high: float
    unit: str
    note: str


# ----------------------------------------------------------------------------- climates
CITIES = {
    # key: (GHCN station, label, Koppen class, latitude deg, years used)
    "PHX": ("USW00023183", "Phoenix", "BWh hot desert", 33.4278, tuple(range(2006, 2024))),
    "LAX": ("USW00023174", "Los Angeles", "Csb Mediterranean", 33.9381, tuple(range(2006, 2024))),
    "LHR": ("UKE00107650", "London", "Cfb temperate oceanic", 51.4789, tuple(range(2006, 2024))),  # ECA&D Heathrow series in GHCN-Daily, complete Tmax/Tmin
    "SIN": ("SNM00048698", "Singapore", "Af tropical rainforest", 1.3500, tuple(range(2003, 2021))),
}

# ----------------------------------------------------------------------------- city
SECTORS = ["RES", "HOS", "HEA", "EDU", "COM", "IND", "DCT", "LAN", "CON", "PUB"]
SECTOR_LABEL = {
    "RES": "Residential", "HOS": "Hospitality", "HEA": "Healthcare", "EDU": "Education",
    "COM": "Commerce", "IND": "Industry", "DCT": "Data centers", "LAN": "Public landscape",
    "CON": "Construction", "PUB": "Public services",
}
MUNICIPAL = ("LAN", "PUB")  # sectors served by the stormwater department under siloed operation

P = {
    # residential
    "pop": Param(1.0e6, 1.0e6, 1.0e6, "persons", "reference city size, declared"),
    "res_lpcd": Param(150.0, 120.0, 200.0, "L/cap/d", "indoor residential use, declared"),
    "res_np": Param(0.20, 0.15, 0.27, "-", "toilet-flushing share of indoor use, declared"),
    "res_area": Param(8.0, 3.0, 15.0, "km2", "irrigated private gardens, declared"),
    # hospitality, healthcare, education, commerce, industry, data centres
    "hos_in": Param(15000.0, 10000.0, 25000.0, "m3/d", "hotel indoor use, declared"),
    "hos_np": Param(0.25, 0.15, 0.35, "-", "non-potable share of hotel indoor use, declared"),
    "hea_beds": Param(3000.0, 2000.0, 4500.0, "beds", "hospital beds (3 per 1000 residents), declared"),
    "hea_m3_bed_yr": Param(103.0, 80.0, 130.0, "m3/bed/yr", "gonzalez2018 (German hospitals)"),
    "hea_np": Param(0.10, 0.05, 0.15, "-", "non-clinical toilet share, declared (cooling excluded)"),
    "edu_in": Param(8000.0, 5000.0, 12000.0, "m3/d", "school-day indoor use, declared"),
    "edu_np": Param(0.35, 0.25, 0.45, "-", "toilet share in schools, declared"),
    "com_in": Param(25000.0, 18000.0, 35000.0, "m3/d", "weekday commercial indoor use, declared"),
    "com_np": Param(0.35, 0.25, 0.45, "-", "toilet share in commercial buildings, declared"),
    "com_cool": Param(80.0, 40.0, 150.0, "m3/d/degC", "cooling-tower make-up above 22 degC, declared"),
    "hos_cool": Param(30.0, 15.0, 60.0, "m3/d/degC", "hotel cooling make-up above 24 degC, declared"),
    "ind_proc": Param(35000.0, 25000.0, 50000.0, "m3/d", "weekday industrial process use, declared"),
    "ind_np": Param(0.40, 0.25, 0.55, "-", "process uses fit for reclaimed water, declared"),
    "dct_base": Param(3000.0, 1500.0, 6000.0, "m3/d", "data-centre evaporative cooling base, declared (mytton2021)"),
    "dct_slope": Param(400.0, 200.0, 800.0, "m3/d/degC", "cooling increase above 15 degC, declared"),
    # landscape, construction, public services
    "lan_area": Param(12.0, 5.0, 20.0, "km2", "irrigated public landscape, declared"),
    "minor_area": Param(3.35, 3.35, 3.35, "km2", "irrigated grounds of hotels, hospitals, schools, commerce"),
    "con_use": Param(5000.0, 3000.0, 8000.0, "m3/d", "construction dust control on dry working days, declared"),
    "pub_in": Param(6000.0, 4000.0, 9000.0, "m3/d", "municipal buildings indoor use, declared"),
    "pub_clean": Param(3000.0, 1500.0, 5000.0, "m3/d", "street cleaning on dry days, declared"),
    # irrigation physics
    "kc": Param(0.80, 0.65, 0.95, "-", "crop coefficient for turf and mixed landscape, declared"),
    "irr_eff": Param(0.72, 0.60, 0.85, "-", "irrigation application efficiency, declared"),
    "raw_mm": Param(40.0, 25.0, 60.0, "mm", "readily available soil water, declared"),
    # connection and reach fractions
    "cR_res": Param(0.10, 0.05, 0.20, "-", "share of residential non-potable demand on dual reticulation, declared"),
    "cR_nonres_in": Param(0.30, 0.15, 0.50, "-", "share of non-residential indoor non-potable demand connected, declared"),
    "cR_cool": Param(0.40, 0.20, 0.60, "-", "share of cooling demand connected, declared"),
    "cR_ind": Param(0.50, 0.30, 0.70, "-", "share of industrial eligible demand connected, declared"),
    "cR_dct": Param(0.60, 0.40, 0.80, "-", "share of data-centre cooling connected, declared"),
    "cR_out": Param(0.45, 0.25, 0.65, "-", "share of non-residential irrigation connected, declared"),
    "cR_lan": Param(0.60, 0.30, 0.90, "-", "share of public landscape on reclaimed network, declared"),
    "cR_con": Param(0.70, 0.50, 0.90, "-", "construction trucks filled at reclaimed stations, declared"),
    "cR_pub": Param(0.40, 0.20, 0.60, "-", "public services connected to reclaimed water, declared"),
    "cS_res": Param(0.05, 0.02, 0.10, "-", "stormwater reach of residential irrigation, declared"),
    "cS_out": Param(0.20, 0.10, 0.35, "-", "stormwater reach of other irrigation, declared"),
    "cS_lan": Param(0.50, 0.20, 0.80, "-", "stormwater reach of public landscape, declared"),
    "cS_con": Param(0.30, 0.10, 0.50, "-", "stormwater reach of construction, declared"),
    "cS_pub": Param(0.40, 0.20, 0.60, "-", "stormwater reach of public services, declared"),
    # reclaimed supply
    "return_factor": Param(0.80, 0.70, 0.90, "-", "wastewater inflow per unit indoor use, declared"),
    "tert_frac": Param(0.25, 0.10, 0.60, "-", "tertiary capacity as share of mean dry-weather inflow, declared"),
    "tert_recovery": Param(0.95, 0.90, 0.98, "-", "tertiary product recovery, declared"),
    "R_store_days": Param(10.0, 2.0, 60.0, "d", "reclaimed storage in days of mean product, declared"),
    "R_dist_peak": Param(2.0, 1.5, 3.0, "-", "reclaimed delivery capacity over mean product, declared"),
    # stormwater supply
    "catch_km2": Param(20.0, 10.0, 40.0, "km2", "contributing urban catchment, declared"),
    "runoff_c": Param(0.50, 0.30, 0.70, "-", "runoff coefficient, declared"),
    "init_loss_mm": Param(2.0, 1.0, 4.0, "mm", "initial abstraction per day, declared"),
    "S_intake": Param(150000.0, 50000.0, 300000.0, "m3/d", "stormwater intake capacity, declared"),
    "S_store": Param(1.0e6, 0.25e6, 3.0e6, "m3", "stormwater storage, declared"),
    "S_dist": Param(60000.0, 30000.0, 100000.0, "m3/d", "treated stormwater delivery capacity, declared"),
    # costs and energy (marginal operating values)
    "c_pot": Param(0.80, 0.40, 1.60, "USD/m3", "marginal potable supply cost, declared"),
    "c_rec": Param(0.30, 0.15, 0.45, "USD/m3", "marginal reclaimed O&M, declared (giammar2021, exposito2024)"),
    "c_sto": Param(0.20, 0.10, 0.35, "USD/m3", "marginal stormwater treatment and pumping, declared"),
    "e_pot": Param(1.50, 0.50, 4.00, "kWh/m3", "potable marginal energy, declared (plappally2012 range)"),
    "e_rec": Param(0.80, 0.40, 1.20, "kWh/m3", "tertiary plus delivery energy, declared (giammar2021)"),
    "e_sto": Param(0.40, 0.20, 0.60, "kWh/m3", "stormwater treatment and pumping energy, declared"),
    "ef_grid": Param(0.40, 0.10, 0.80, "kgCO2e/kWh", "grid emission factor, declared"),
}

# Parameters sampled in the E1 Latin hypercube (the rest stay nominal).
E1_LHS_KEYS = ["res_lpcd", "res_np", "res_area", "lan_area", "kc", "irr_eff", "raw_mm", "cR_res", "cR_nonres_in",
               "cR_out", "cR_lan", "cS_lan", "tert_frac", "R_store_days", "catch_km2", "runoff_c", "S_store",
               "S_intake", "ind_np", "dct_slope"]


def nominal_params():
    return {k: v.nominal for k, v in P.items()}


# ----------------------------------------------------------------------------- forecasts
@dataclass(frozen=True)
class ForecastModel:
    horizon: int = 7
    rain_sigma0: float = 0.40
    rain_sigma_slope: float = 0.10
    miss0: float = 0.10
    miss_slope: float = 0.05
    fa0: float = 0.05
    fa_slope: float = 0.02
    wet_mm: float = 1.0
    demand_sigma0: float = 0.05
    demand_sigma_slope: float = 0.01
    members: int = 10


FORECAST = ForecastModel()
PERFECT_FORECAST = ForecastModel(rain_sigma0=0.0, rain_sigma_slope=0.0, miss0=0.0, miss_slope=0.0,
                                 fa0=0.0, fa_slope=0.0, demand_sigma0=0.0, demand_sigma_slope=0.0, members=1)

# ----------------------------------------------------------------------------- experiments
E1_DRAWS = 8              # Latin-hypercube parameter draws per climate
E1_SWEEP_LEVELS = (0.05, 0.10, 0.15, 0.25, 0.35, 0.50, 0.70, 1.00, 1.40, 2.00)  # tertiary capacity / mean inflow
BOOTSTRAP = 10000
DELIVERY_DISCOUNT = 0.005  # per-day preference for earlier delivery: breaks ties and discounts forecast-dependent deliveries
ORACLE_DISCOUNT = 1e-6     # perfect-foresight benchmark: no forecast risk to discount
TERMINAL_FRAC = 0.5        # end-of-horizon storage valued at half its delivery value (store rather than spill)
SPILL_PENALTY = 0.01       # USD/m3, spill only when storage is full


@dataclass
class RunScale:
    """Smoke and full run sizes."""
    name: str
    cities: tuple = ("PHX", "LAX", "LHR", "SIN")
    years_per_city: int = 18
    draws: int = E1_DRAWS
    sweep: bool = True
    e2_days_per_city: int = 60
    e3_contexts: int = 120
    e3b_years: int = 200
    e4_mc: int = 20000
    e4_sobol_n: int = 4096
    workers: int = 10
    extra: dict = field(default_factory=dict)


SMOKE = RunScale(name="smoke", cities=("PHX", "LHR"), years_per_city=1, draws=1, sweep=False,
                 e2_days_per_city=4, e3_contexts=6, e3b_years=5, e4_mc=500, e4_sobol_n=64, workers=2)
FULL = RunScale(name="full")
