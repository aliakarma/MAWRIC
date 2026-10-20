# MAWRIC-X experiment design (fixed before the full runs)

Written 16 October 2026, before any full-run result existed. The smoke test may change implementation details (solver tolerances, run counts), and every such change is logged at the end of this file. The research questions, policies, metrics and statistical tests below do not change after the full runs start.

## Why the original evaluation was replaced

The as-received `simulation.py` reproduces its own summary table (checked in a scratch copy, identical to 15 significant digits). Its headline results are inputs, not findings:

1. The MAWRIC-X arm applies sector efficiency coefficients `MX_EFF` that are set about twice `SILO_EFF`, and a loss-recovery fraction drawn from 38 to 55% against 10 to 20% for the siloed arm. The 35.6% potable saving follows from those settings.
2. The NPV subtracts the capital cost twice: `annual_cost` already contains the annuity of `capex`, and `npv` subtracts `capex` again.
3. The carbon value uses 0.00005 MUSD per thousand tonnes, which is 0.05 USD/tCO2e, about 1,000 times below the stated intent.
4. The benefit adds avoided energy to a water value that already embeds energy, which the manuscript text itself warns against.
5. The targeting result depends only on the assumed exponent theta = 2.1.

The new evaluation computes every outcome from mechanisms (storage, quality constraints, decision rights, information, hydraulics), so no result is assumed.

## Research questions and hypotheses

- **RQ1 / E1.** How much potable water, energy and cost does coordinated fit-for-purpose allocation of reclaimed water and captured stormwater save beyond siloed departmental operation of the same assets, and which mechanism produces the premium?
  - H1a: the premium is positive in all four climates.
  - H1b: the premium is largest when alternative supply is comparable to connected eligible demand.
- **RQ2 / E2.** Can sector agents that keep their demand private reach the centralized optimum by price-based negotiation (ADMM), how many messages does it take, and how far can one misreporting agent shift the outcome?
- **RQ3 / E3.** Does a deterministic assurance layer stop unsafe agent proposals on a hydraulic network, how many safe proposals does it reject, and how do autonomy level and human approval latency change leak losses and service?
- **RQ4 / E4.** Under declared uncertainty, what is the net present value of the coordination layer, and which parameters drive it?

## Data

| Input | Source | Use |
|---|---|---|
| Daily PRCP, TMAX, TMIN | NOAA GHCN-Daily via the NCEI access service: Phoenix AP USW00023183 (hot desert), Los Angeles Intl AP USW00023174 (Mediterranean), London Heathrow UKM00003772 (temperate oceanic), Singapore Changi SNM00048698 (tropical) | rainfall-runoff, irrigation and cooling demand |
| Years | 18 complete rainfall years per city: 2006 to 2023 for Phoenix, Los Angeles and London, 2003 to 2020 for Singapore | weather-years as replicates |
| Temperature gaps | London and Singapore temperature gaps filled with the station day-of-year climatology (31-day smoothing), share filled reported | ET0 |
| Reference ET0 | Hargreaves and Samani (1985) with FAO extraterrestrial radiation | irrigation demand |
| Networks | Net6 (3,323 junctions, 32 tanks, 61 pumps, 2 PRVs) and Net3 (92 junctions, 3 tanks, 2 pumps) bundled with WNTR 1.5.0 | E3 |
| Saudi stations | Riyadh SA000040438 and Al-Madinah SA000040430 were downloaded but report almost no daily precipitation in GHCN, so they are not used. Phoenix serves as the hot-desert analogue. | |

Raw files and SHA-256 checksums: `data/raw/ghcn/`.

## E1. Coordination premium (city scale, daily, 18 weather-years x 4 climates)

**Reference city.** One million residents and ten sectors (residential, hospitality, healthcare, education, commerce, industry, data centres, public landscape, construction, public services). Each sector's daily demand has an indoor component (weekly and calendar patterns), an outdoor irrigation component driven by a soil-moisture bucket with Kc x ET0 and effective rainfall, and a cooling component driven by daily maximum temperature. Each component is split into potable-only and non-potable-eligible end uses. All values and ranges are declared in `mawricx/config.py` and Table 2 of the paper.

**Sources.** Potable (unconstrained, marginal cost and energy), reclaimed water (tertiary capacity on wastewater inflow equal to a return factor times indoor use, storage, distribution capacity, sector connection fractions), captured stormwater (runoff from a contributing catchment, intake capacity, storage, sector reach). Reclaimed water may serve indoor non-potable and outdoor uses. Treated stormwater may serve outdoor uses, construction and public services.

**Policies (same assets in every policy).**
- P0 Baseline: potable only.
- S Siloed: the reuse department splits each day's available reclaimed water among connected users by fixed contract shares (proportional to expected connected eligible demand), unused shares return to storage or spill. The stormwater department serves only municipal users (public landscape, public services). No forecasts.
- Factorial over three coordination mechanisms: **pooling** (daily reassignment across users), **integration** (stormwater serves every compatible sector and both sources are dispatched jointly), **forecast** (7-day model predictive control with imperfect forecasts). Eight combinations. S has none, MAWRIC-X has all three.
- O Oracle: one-year LP with perfect foresight and all mechanisms (upper bound).

**Solver.** Linear programs in `scipy.optimize.linprog` (HiGHS). Objective: minimize marginal operating cost (potable > reclaimed > stormwater).

**Forecasts.** Rainfall forecast at lead h: multiplicative lognormal error with sigma 0.4 + 0.1h on wet days, miss probability 0.10 + 0.05h, false-alarm probability 0.05 + 0.02h with amounts drawn from the station's wet-day distribution. Demand forecast error 5% + 1% per day of lead.

**Replicates.** 18 weather-years x 4 climates x 8 Latin-hypercube parameter draws over the declared ranges (576 city-years per policy). Supply-ratio sweep for H1b: tertiary capacity at 10 levels, nominal parameters.

**Metrics.** Annual potable use, coordination premium (siloed minus coordinated potable use), premium as share of baseline potable use, reclaimed and stormwater utilization, spill, energy, emissions, operating cost, gap to oracle. Shapley attribution of the premium across the three mechanisms.

**Statistics.** Paired differences per city-year, 95% bootstrap confidence intervals (10,000 resamples), Wilcoxon signed-rank tests with Holm correction across climates.

## E2. Negotiation fidelity and robustness

Sector agents hold their own demand and eligibility data. Two source agents hold supply and storage. They solve the same 7-day MPC problem as E1 by ADMM in sharing form (Boyd et al. 2011): sectors solve closed-form box-and-simplex projections, source agents solve storage-feasible quadratic projections, and only proposed volumes and prices are exchanged. Instances: random days from E1 in each climate. Metrics: relative objective gap to the centralized LP, primal residual, iterations, messages per decision. Misreporting test: one sector inflates its declared eligible demand by 30, 60 and 100%, with and without a cap equal to 1.1 times the 90th percentile of its metered eligible use over the previous 28 days. Metrics: water allocated beyond true need, honest sectors' loss.

## E3a. Assurance layer under fault injection (Net6 primary, Net3 replication)

Operational contexts: random demand multipliers and initial tank levels. A nominal optimizer agent proposes 24-hour plans (pump schedule changes, tank-trigger changes, PRV settings). Fault models generate unsafe or invalid proposals: random corruption, stale state, adversarial pressure or tank drawdown, unit error (feet versus metres), hallucinated asset IDs, and false data injection into tank-level telemetry.

Ground truth: simulate each proposal on the true state with WNTR (EPANET) and flag a violation if a protected node drops below 20 m, any normally positive node drops below 0 m, or a tank falls below its fire reserve (30% of its range), for at least one hour.

Assurance configurations: A0 none, A1 schema and bound rules, A2 A1 plus twin simulation on the believed state, A3 A2 plus telemetry plausibility (mass-balance) check. Metrics: unsafe executions, false rejections, retained energy-cost saving of safe proposals.

## E3b. Leak response under autonomy levels

Leak events are drawn on Net6 pipes (Poisson arrivals, lognormal sizes). Detection delay and confidence follow a declared detector model (no new detector is built). Precomputed hydraulics give each leak's flow at normal and reduced pressure (pressure-leakage exponent N1 sampled from 0.5 to 1.5) and the demand and protected users cut by isolating its valve segment. Governance policies: human-only (every action needs approval), full autonomy without verification, and MAWRIC-X (automatic bounded pressure reduction, human-approved isolation, robot or crew verification of low-confidence alarms). Approval latency follows a lognormal distribution with a night-time penalty. Metrics: leak volume, customer-hours interrupted, false isolations, protected-user interruptions, operator approvals per week.

## E4. Economics

Benefits come from E1 (premium in potable, energy and emissions) and E3b (avoided leak volume). Costs: coordination platform (software, integration, staff), sensors, robots. Discount rate 6%, horizon 15 years. Monte Carlo over declared distributions. Sobol indices with SALib (Saltelli sampling). Capital is counted once. Energy embedded in the potable value is not added twice. Report the break-even annual cost of the coordination layer.

## Reproducibility

`python run_smoke.py` (minutes) and `python run_full.py` (hours) write `results/*.csv`, `results/numbers.tex` (LaTeX macros used by the manuscript) and `figures/*.pdf`. Seeds are fixed in `mawricx/config.py`.

## Change log after the smoke test

(entries added below as they occur)

1. **Spill tie-breaking (bug fix, smoke test).** With free spills and no value on end-of-horizon storage, the LP was indifferent between storing and spilling water it could not use inside the horizon and often spilled it. Fix: spill penalty of 0.01 USD/m3, terminal storage value of 0.5 times the delivery value in receding-horizon policies, 1.0 in the oracle, and a per-day delivery discount of 0.5% (1e-6 in the oracle). All policies are now compared on storage-adjusted potable use (net drawdown of the initial storage counts as potable-equivalent use).
2. **Forecast agent uses an ensemble mean (smoke test).** A single noisy forecast realization lowered the premium below the myopic policy on 6 test city-years (2.58 against 2.90 million m3). A 10-member ensemble mean, the usual operational product, gave 2.87 million m3 and perfect forecasts 3.04 million m3. The full runs use the 10-member ensemble mean for policies with the forecast mechanism and add a perfect-forecast variant (MAWRICX_PF) to bound the value of better forecasts.
3. **E3a attribution and configurations (smoke test).** Replacing a pump's level controls with an explicit schedule changes its operation outside the outage window, so each plan is now compared with the same pumps on their explicit baseline schedules. A minimum service pressure of 14 m for normally pressurized nodes (nominal minimum at least 20 m) was added, because a PRV set to 10 m violated none of the original constraints. Static rules rejected almost every non-nominal plan, safe ones included, so the configurations are now A0 none, A1 schema and static rules, A2 schema and twin, A3 schema, plausibility filter and twin, and A1 with A3. EPANET failures count as violations. FDI-induced plans stay inside the static window bound and target the pumps that feed the attacked tank.
4. **E3b re-alarms (smoke test).** A true burst whose alarm is dismissed or missed by a robot alarms again after 24 h with confidence raised by 0.25, for every policy. Without this, a single robot miss let a burst run for 14 days, which no operating detector would allow.
5. **E3a twin decision rule (full-run diagnosis).** Comparing sets of margin-tightened violations hid unsafe plans whenever default operation already sat inside the 2 m margin, because the element appeared in both sets. The twin now rejects a plan that leaves any constrained element inside the margin and more than 0.1 m worse than default operation. Ground truth is unchanged (a new hard violation relative to default operation). Transient EPANET file-access failures under parallel runs were removed by retrying each simulation up to three times. Failures that persist are reported.
6. **EPANET scratch-file isolation, E3a margin sweep and severity (full-run diagnosis).** EPANET 2.2 names its scratch hydraulics file with `_tempnam`, which produces the same names (en2, en5, ...) in every process and reads TMP only when the library loads. Parallel workers that shared TMP could therefore overwrite each other's hydraulics, sometimes with an error (Errors 106 and 307 in five Net6 contexts) and sometimes silently: two parallel runs of E3a disagreed on the ground truth of 43 of 1,800 proposals. Every worker of E3a and E3b now gets its own TMP before its first simulation (`hydraulics.isolate_tmp`), contexts with any EPANET file error are re-run serially, and `analysis/verify_e3a_serial.py` checks a sample of contexts against a serial run. E3a, E3b and E4 were re-run. E1 and E2 do not call EPANET and are unaffected. E3a now also records, for every proposal, the smallest twin slack among elements the plan makes worse than default operation (the twin rejects at margin m exactly when this value is below m) and the depth of the deepest new hard violation in the ground truth. The pre-declared 2 m margin stays the reported setting, and a post hoc sweep from 0 to 5 m shows the trade-off. Rates now exclude schema-invalid proposals (hallucinated assets), which every configuration except A0 rejects, because they inflated the unsafe denominator. The single entry point is `python run_all.py --smoke` or `--full`, outputs go to `results/`, `manuscript/numbers.tex`, `manuscript/tabledefs.tex` and `manuscript/figures/`.
7. **Post hoc analyses after the full runs (labelled post hoc in the paper).** (a) `analysis/e3a_twin_misses.py` re-simulates every unsafe proposal that A3 accepted on the true and the twin state and records the violated constraint types, the depth and hour of the deepest violation, whether any link changed status at a different hour, and whether a tank emptied. (b) `analysis/e3a_robust_twin.py` tests an ensemble twin (A3e) that also applies the 2 m slack rule on four perturbed states (believed demand times 1.05 and 0.95, all tank estimates plus and minus 0.10 m). It was designed after (a) and is tested on the same contexts, so its rates are optimistic. (c) In E1, negative premiums are attributed by checking whether the perfect-forecast variant is also negative for the same city-year. None of these analyses changes a pre-declared result.
8. **Pre-submission review round 1 (2026-10-17).** (a) E3a rates now carry 95% intervals from 2,000 bootstrap resamples of contexts, and the A1 minus A3 differences carry intervals from the same resamples. (b) E3b gained a post hoc burst-size sensitivity (median burst flow 1, 2, 4 and 8 L/s on the same 50 simulated years as the other sweeps); the rows of all earlier cases are unchanged, so E4 is unchanged. The latency curves carry 95% bootstrap bands over simulated years. (c) Appendix A now cites the published data behind three parameter groups (hospital use per bed, reclaimed-water cost and energy, crop coefficient and readily available water); all other values remain declared planning assumptions. No experiment or parameter value was changed to obtain a result.
9. **London weather station (pre-submission review round 2, 2026-10-17).** The synoptic Heathrow record (UKM00003772) lacked 47% of daily maxima and 50% of daily minima in 2006 to 2023, which had been filled with climatology. GHCN-Daily also carries the European Climate Assessment & Dataset series of Heathrow (UKE00107650, longitude stored with the wrong sign), which is complete for precipitation, maxima and minima in every year. London now uses UKE00107650 (same years), so no London value is filled; 86 days with the maximum below the minimum are swapped. E1, E2 and E4 were re-run; E3a and E3b do not use weather. Only London-dependent numbers changed (for example the nominal London premium moved from 0.338 to 0.456 Mm3 per year). Singapore keeps climatology filling for 41% of maxima because no other station exists; observed Singapore maxima deviate from climatology with a standard deviation of 1.4 C, against 3.4 to 3.7 C in the other cities.
