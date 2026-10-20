# MAWRIC-X: A Governed Multi-Agent Framework for Urban Water Allocation and Leak Response

[![Python 3.10 | 3.11](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 6 Passing](https://img.shields.io/badge/tests-6%20passed-brightgreen.svg)](tests/)
[![Hydraulics: WNTR 1.5.0](https://img.shields.io/badge/hydraulics-WNTR%201.5.0-navy.svg)](https://wntr.readthedocs.io/)
[![Optimization: SciPy HiGHS](https://img.shields.io/badge/solver-SciPy%20HiGHS-orange.svg)](https://highs.dev/)
[![Pre-Registration: Locked](https://img.shields.io/badge/study-pre--registered-success.svg)](EXPERIMENT_DESIGN.md)
[![Publication: MDPI Water](https://img.shields.io/badge/journal-MDPI%20Water%20(2026)-blue.svg)](https://www.mdpi.com/journal/water)

> **Official Research Codebase & Artifact Repository**  
> Accompanying the paper: *“MAWRIC-X: A Governed Multi-Agent Framework for Urban Water Allocation and Leak Response, with Evidence on the Size of the Coordination Premium”* (MDPI *Water*, 2026).

---

## Table of Contents

- [Overview & Research Motivation](#overview--research-motivation)
- [Key Capabilities & Features](#key-capabilities--features)
- [Architecture & Governance Model](#architecture--governance-model)
- [Repository Structure](#repository-structure)
- [Installation & Environment Setup](#installation--environment-setup)
  - [Prerequisites](#prerequisites)
  - [Linux / macOS Setup](#linux--macos-setup)
  - [Windows Setup (PowerShell)](#windows-setup-powershell)
- [Quick Start & Minimal Reproducible Examples](#quick-start--minimal-reproducible-examples)
  - [1. Invariant Unit Test Suite (< 5 seconds)](#1-invariant-unit-test-suite--5-seconds)
  - [2. End-to-End Smoke Test (~2–3 minutes)](#2-end-to-end-smoke-test-23-minutes)
  - [3. Full Empirical Replication (~30–60 minutes)](#3-full-empirical-replication-3060-minutes)
  - [4. Standalone Experiment Runs](#4-standalone-experiment-runs)
  - [5. Manuscript & Figure Compilation](#5-manuscript--figure-compilation)
- [Experimental Protocols (E1–E4)](#experimental-protocols-e1e4)
  - [E1: Coordination Premium & Factorial Shapley Attribution](#e1-coordination-premium--factorial-shapley-attribution)
  - [E2: Decentralized ADMM Negotiation & Privacy Resilience](#e2-decentralized-admm-negotiation--privacy-resilience)
  - [E3a: Deterministic Hydraulic Assurance & Twin Fault Injection](#e3a-deterministic-hydraulic-assurance--twin-fault-injection)
  - [E3b: Dynamic Burst Response & Human Approval Latency](#e3b-dynamic-burst-response--human-approval-latency)
  - [E4: Life-Cycle Techno-Economics & Global Sobol Sensitivity](#e4-life-cycle-techno-economics--global-sobol-sensitivity)
- [Empirical Results & Key Findings](#empirical-results--key-findings)
- [Meteorological Data & Quality Control](#meteorological-data--quality-control)
- [Scientific Integrity & Reproducibility Guarantees](#scientific-integrity--reproducibility-guarantees)
- [Configuration & Parameter Bounds](#configuration--parameter-bounds)
- [Troubleshooting & Platform Notes](#troubleshooting--platform-notes)
- [Limitations & Operational Scope](#limitations--operational-scope)
- [Development & Contributing](#development--contributing)
- [Authors, Citation & License](#authors-citation--license)

---

## Overview & Research Motivation

Municipal water systems are historically fragmented into operational and institutional silos:

- **Potable drinking distribution networks** operate under strict pressure and quality mandates.
- **Wastewater reclamation plants** discharge or distribute secondary/tertiary effluent with static contracts.
- **Stormwater management systems** treat runoff as a flood hazard rather than an alternative supply asset.

This fragmentation leaves municipal utilities vulnerable to climate extremes and induces severe non-revenue water (NRW) losses worldwide.

**MAWRIC-X** (*Multi-Agent Water Resource Integrated Coordination with Runtime Hydraulic Assurance*) is an open-source, reproducible cyber-physical research framework that bridges autonomous multi-agent optimization with deterministic hydraulic safety filters:

1. **Fit-for-Purpose Resource Allocation:** Allocates potable water, tertiary-treated reclaimed water, and harvested stormwater across 10 distinct urban and commercial sectors according to strict end-use quality compatibility.
2. **Decentralized Negotiation (ADMM):** Employs the Alternating Direction Method of Multipliers in sharing form, enabling sector agents to negotiate shadow prices and delivery schedules without disclosing local private utility functions or demand curves.
3. **Deterministic Hydraulic Assurance Filter:** Interposes an EPANET / WNTR digital twin barrier between optimization proposals and the physical network. Control schedules (pump dispatch, valve adjustments) are screened against pressure deficits, tank drainage, and velocity limits before actuation.
4. **Automated Leak Response:** Coordinates rapid pressure reduction and valve isolation during pipe burst transients, substantially cutting physical water losses while respecting operator-in-the-loop oversight latency.

> [!NOTE]
> All empirical conclusions are derived from first-principles physical and economic mechanisms (mass-balance storage, hydraulic head equations, and optimization duality). No metrics or savings ratios are hardcoded.

---

## Key Capabilities & Features

- **10 Municipal & Commercial Sectors:** Residential, Hospitality, Healthcare, Education, Commerce, Industry, Data Centers, Public Landscape, Construction, and Public Services.
- **4 Contrasting Köppen Climate Archetypes:** Evaluated over 18 complete weather-years per city (72 city-years; 26,280 simulated operational days) based on NOAA GHCN-Daily records:
  - **Phoenix (PHX), USA:** Hot Desert (*BWh*) — high reference evapotranspiration ($\text{ET}_0$), acute baseline scarcity.
  - **Los Angeles (LAX), USA:** Mediterranean (*Csb*) — winter-wet, dry summer peaks.
  - **London (LHR), UK:** Temperate Oceanic (*Cfb*) — steady indoor baseline demand, moderate distributed rainfall.
  - **Singapore (SIN), Singapore:** Tropical Rainforest (*Af*) — high humidity, persistent equatorial rainfall.
- **Benchmark Hydraulic Networks:**
  - **Net3:** 92 junctions, 3 storage tanks, 2 pumps. Used for dynamic transient leak isolation and fast validation.
  - **Net6:** 3,323 junctions, 32 storage tanks, 61 pumps, 2 pressure reducing valves (PRVs). Used for large-scale runtime safety assurance.
- **Factorial Mechanism Attribution:** Uses cooperative game-theoretic Shapley values to isolate the exact marginal contribution of three distinct coordination mechanisms:
  - **Resource Pooling ($P$):** Daily cross-sector sharing of reclaimed water.
  - **Cross-Sector Integration ($I$):** Opening stormwater assets to non-potable commercial and municipal users.
  - **Forecast Horizon ($F$):** 7-day Model Predictive Control (MPC) with ensemble forecast uncertainty.
- **Fault-Tolerant Stress Testing:** Evaluated under sensor calibration drift, telemetry packet loss, state-estimation errors, and adversarial demand over-reporting (30% to 100% inflation).
- **Comprehensive Life-Cycle Economics:** Net Present Value (NPV), Levelized Cost of Water (LCOW), and Saltelli global Sobol variance decomposition across capital expenditure and tariff uncertainty.

---

## Architecture & Governance Model

The framework executes a three-tier cyber-physical pipeline separating information gathering, agent bidding, hydraulic screening, and physical execution:

```
                      ┌──────────────────────────────────────────────┐
                      │    Meteorological Data & Quality Control     │
                      │  NOAA GHCN-Daily: P, Tmin, Tmax (72 City-Yrs)│
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Reference ET0 & Sector Demand Engine      │
                      │  Hargreaves-Samani & Soil-Moisture Dynamics  │
                      │             (mawricx/city.py)                │
                      └──────────────────────┬───────────────────────┘
                                             │
                      ┌──────────────────────┴───────────────────────┐
                      ▼                                              ▼
        ┌────────────────────────────┐               ┌───────────────────────────────┐
        │  Centralized Benchmark LP  │               │   Decentralized Negotiation   │
        │   8 Factorial MPC Modes    │  Shadow Price │    Autonomous Sector Agents   │
        │   (mawricx/allocation.py)  │  ◄──────────► │     ADMM Consensus Protocol   │
        │                            │   Allocations │      (mawricx/agents.py)      │
        └─────────────┬──────────────┘               └───────────────┬───────────────┘
                      │                                              │
                      └──────────────────────┬───────────────────────┘
                                             │ Candidate Control Proposals
                                             │ (Pump schedules, PRV settings)
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │   Deterministic Hydraulic Assurance Layer    │
                      │       WNTR / EPANET Digital Twin Filter      │
                      │      Pressure, Slack & Tank Bounds (Net6)    │
                      │           (mawricx/assurance.py)             │
                      └──────────────────────┬───────────────────────┘
                                             │ Safe Filtered Actions
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │          Physical Network Execution          │
                      │   Pressure Bounds Validation & Leak Control  │
                      │          (mawricx/hydraulics.py)             │
                      └──────────────────────────────────────────────┘
```

### Governance Layers (E3a)

- **A0 (Unchecked):** Unchecked optimization execution (zero assurance).
- **A1 (Static Schema & Bound Rules):** Rejects syntactically malformed commands, out-of-range pressures, and unauthorized asset IDs.
- **A2 (Digital Twin Simulation):** Runs proposed schedules on the believed network state in EPANET 2.2 before physical deployment. Rejects plans yielding negative node pressure or tank storage depletion.
- **A3 (Plausibility + Twin):** Pre-screens state telemetry for mass-balance violations before running the digital twin (full MAWRIC-X governance).

---

## Repository Structure

```
MAWRIC/
├── mawricx/                    # Core simulation, optimization, and hydraulic engine
│   ├── __init__.py             # Package version and metadata
│   ├── agents.py               # Decentralized ADMM consensus negotiation and privacy caps
│   ├── allocation.py           # Linear programming (SciPy HiGHS) and 7-day MPC allocation
│   ├── assurance.py            # Runtime hydraulic safety verification and critical slack rules
│   ├── city.py                 # 10-sector reference city demand and dual-storage models
│   ├── config.py               # Master seed (20261016) and Latin Hypercube distributions
│   ├── hydraulics.py           # WNTR / EPANET wrapper and isolated scratch-file management
│   └── weather.py              # NOAA GHCN ingestion and Hargreaves-Samani ET0 model
│
├── experiments/                # Pre-registered empirical benchmark protocols (E1–E4)
│   ├── e1_coordination.py      # E1: Coordination premium and factorial Shapley decomposition
│   ├── e2_negotiation.py       # E2: ADMM negotiation, consensus convergence, and privacy tests
│   ├── e3_assurance.py         # E3a: Hydraulic fault injection and digital twin safety filters
│   ├── e3b_leak_response.py    # E3b: Automated pipe burst response and human approval latency
│   └── e4_economics.py         # E4: 25-year lifecycle NPV, LCOW, and SALib Sobol sensitivity
│
├── analysis/                   # Statistical validation, macro synthesis, and plot generation
│   ├── make_results.py         # Primary synthesis: builds manuscript numbers.tex and figures
│   ├── build_bib.py            # Automated bibliography verification and bib extraction
│   ├── e3a_robust_twin.py      # Post-hoc ensemble digital twin robustness analysis
│   ├── e3a_twin_misses.py      # Deep hydraulic failure and margin-sweep investigation
│   ├── verify_e3a_serial.py    # Deterministic serial audit for parallel EPANET executions
│   └── make_submission.py      # Archive generation pipeline for publication supplementary
│
├── data/                       # Meteorological datasets and provenance verification
│   ├── download_ghcn.py        # Automated NOAA NCEI daily record fetcher with SHA-256 checks
│   ├── raw/ghcn/               # Station CSV files and SHA256SUMS.txt integrity ledger
│   └── processed/              # Verified climatology-filled weather inputs (PHX, LAX, LHR, SIN)
│
├── results/                    # Validated experimental simulation outputs
│   ├── *_full.csv              # Full multi-decade simulation runs (72 city-years)
│   ├── *_smoke.csv             # Lightweight verification runs for CI/testing
│   └── logs/                   # Execution logs for all pipeline stages
│
├── manuscript/                 # LaTeX publication artifacts (MDPI Water submission)
│   ├── MAWRIC_X_Water.tex      # Full camera-ready manuscript source
│   ├── numbers.tex             # Auto-generated LaTeX macros derived from results/*.csv
│   ├── tabledefs.tex           # Auto-generated publication table definitions
│   ├── references.bib          # Verified BibTeX literature database
│   └── figures/                # High-resolution vector (PDF) and raster (PNG) publication figures
│
├── literature/                 # Systematic PRISMA evidence base and comparative matrix
│   ├── review_body.md          # Comprehensive literature review narrative
│   ├── source_ledger.csv       # Curated corpus ledger across 150+ research sources
│   ├── extraction_sheet.csv    # Dimensional comparative extraction matrix
│   └── references_lit.bib      # Raw BibTeX database for literature synthesis
│
├── tests/                      # Automated regression and invariant verification suite
│   └── test_core.py            # Pytest test cases (ADMM, Shapley, hydraulics, ET0, macros)
│
├── EXPERIMENT_DESIGN.md        # Pre-registered experimental protocol, design rationale & changelog
├── literature_review.md        # Monolithic literature review and gap analysis report
├── requirements.txt            # Pinned dependencies for bit-exact reproducibility
├── run_all.py                  # Master CLI pipeline orchestrator (--smoke and --full modes)
├── LICENSE                     # MIT Open Source License
└── .gitignore                  # Git repository exclusion rules
```

---

## Installation & Environment Setup

### Prerequisites

- **Python:** `3.10.x` or `3.11.x` (64-bit recommended; verified on `3.10.11`).
- **C/C++ Build Tools:** Standard C compiler (for building/linking WNTR EPANET extensions if installing from source).
- **RAM / Storage:** 8 GB RAM minimum (16 GB recommended for parallel Net6 simulations). ~2 GB disk space for full experimental logs and outputs.

### Linux / macOS Setup

```bash
# 1. Clone repository
git clone https://github.com/aliakarma/MAWRIC.git
cd MAWRIC

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Upgrade pip and install pinned dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows Setup (PowerShell)

```powershell
# 1. Clone repository
git clone https://github.com/aliakarma/MAWRIC.git
cd MAWRIC

# 2. Configure execution policy (if script activation is restricted)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 4. Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Quick Start & Minimal Reproducible Examples

### 1. Invariant Unit Test Suite (< 5 seconds)

Execute the invariant test suite to verify solver integration, mathematical theorems, and hydraulic calculations:

```bash
python -m pytest tests -q
```

*Expected output:*

```text
......                                                                   [100%]
6 passed in 3.51s
```

*Validated checks:*

- `test_twin_rule_matches_critical_slack`: Confirms the stored critical slack reproduces the digital twin decision at all safety margins ($m \in [0.0, 3.5]$ m).
- `test_shapley_values_sum_to_premium`: Verifies the additive efficiency axiom ($\sum \phi_i = \text{Total Premium}$) across factorial runs.
- `test_admm_reaches_central_optimum`: Validates ADMM convergence within 0.1% of the centralized SciPy HiGHS LP optimum.
- `test_hargreaves_summer_value_is_plausible`: Confirms extraterrestrial solar radiation and $\text{ET}_0$ physically bound summer demand ($5.0 < \text{ET}_0 < 9.0$ mm/day).
- `test_result_macros_have_backslash` & `test_used_result_macros_are_defined`: Verifies LaTeX macro alignment with the manuscript.

### 2. End-to-End Smoke Test (~2–3 minutes)

Runs the entire pipeline at a reduced sample scale to verify end-to-end execution integrity across weather, allocation, negotiation, assurance, leak response, and economics:

```bash
python run_all.py --smoke
```

Outputs are written to `results/*_smoke.csv` and execution logs to `results/logs/*_smoke.log`.

### 3. Full Empirical Replication (~30–60 minutes)

Reproduces the complete multi-decade empirical study across all 72 city-years, Net6 hydraulic networks, and Monte Carlo draws, then compiles LaTeX macros and publication figures:

```bash
python run_all.py --full
```

### 4. Standalone Experiment Runs

Individual experiments can be executed independently in either `--smoke` or full mode:

```bash
# E1: Coordination Premium & Factorial Shapley Attribution
python experiments/e1_coordination.py --smoke

# E2: Decentralized ADMM Negotiation Protocol
python experiments/e2_negotiation.py --smoke

# E3a: Deterministic Hydraulic Assurance on Net6 / Net3
python experiments/e3_assurance.py --smoke

# E3b: Automated Pipe Burst Isolation
python experiments/e3b_leak_response.py --smoke

# E4: Life-Cycle Techno-Economics & Sobol Sensitivity
python experiments/e4_economics.py --smoke
```

### 5. Manuscript & Figure Compilation

Regenerate publication numbers, tables, and figures from raw simulation data, and compile the camera-ready PDF:

```bash
# Regenerate manuscript macros and figures
python analysis/make_results.py --tag full

# Compile LaTeX manuscript (requires TeX Live / MikTeX with latexmk)
cd manuscript
latexmk -pdf MAWRIC_X_Water.tex
```

---

## Experimental Protocols (E1–E4)

| Protocol | Scope & Objective | Mathematical / Algorithmic Formulation | Benchmark Networks & Data | Output Files |
| --- | --- | --- | --- | --- |
| **E1** | **Coordination Premium** | 8-policy factorial optimization (LP/MPC) with Latin Hypercube draws | 72 city-years (PHX, LAX, LHR, SIN); 10 sectors | `results/e1_runs_full.csv`<br>`results/e1_shapley_full.csv` |
| **E2** | **Negotiation Fidelity** | ADMM sharing consensus; quadratic source projections; eligibility caps | 10 economic sectors; 240 diurnal profile instances | `results/e2_negotiation_full.csv` |
| **E3a** | **Hydraulic Assurance** | WNTR/EPANET digital twin; critical slack rule; fault injection | Net6 (3,323 nodes, 32 tanks); Net3 (92 nodes) | `results/e3_assurance_full.csv`<br>`results/e3a_by_fault_full.csv` |
| **E3b** | **Dynamic Leak Response** | Pressure-dependent leakage ($Q = C P^{N_1}$); valve segment cut | EPANET Net3 benchmark network; 64 bursts | `results/e3b_leak_full.csv`<br>`results/e3b_network_full.csv` |
| **E4** | **Economic Feasibility** | 15/25-year NPV, LCOW, and Saltelli/Sobol variance decomposition | 10,000 Monte Carlo draws; SALib sampling | `results/e4_economics_full.csv`<br>`results/e4_sobol_full.csv` |

### E1: Coordination Premium & Factorial Shapley Attribution

Compares eight operational policies on identical physical storage and treatment assets:

1. `P0`: Baseline potable-only supply.
2. `Siloed`: Departments operate independently with fixed contract quotas; stormwater serves only municipal parks.
3. Factorial policies: Combining **Pooling** ($P$), **Integration** ($I$), and **Forecast** ($F$):
   - $P_1I_0F_0$, $P_0I_1F_0$, $P_0I_0F_1$, $P_1I_1F_0$, $P_1I_0F_1$, $P_0I_1F_1$.
4. `MAWRIC-X`: All three mechanisms enabled simultaneously ($P_1I_1F_1$).
5. `Oracle`: Full-year upper-bound LP with perfect foresight.

Shapley values allocate the coordination premium across mechanisms:
$$\phi_i = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N| - |S| - 1)!}{|N|!} \left[ v(S \cup \{i\}) - v(S) \right]$$

### E2: Decentralized ADMM Negotiation & Privacy Resilience

Sector agents solve private local projections while source agents manage storage constraints. The coordinator updates non-potable clearing prices:
$$\lambda^{k+1} = \lambda^k + \rho \sum_{i=1}^{M} \left( x_i^{k+1} - s_i^{k+1} \right)$$
Tested against strategic manipulation: a rogue sector over-reports demand by 30%, 60%, and 100%. A local verification cap ($1.1 \times 90\text{th}$ percentile of 28-day metered use) eliminates gaming with minimal welfare penalty.

### E3a: Deterministic Hydraulic Assurance & Twin Fault Injection

Evaluates runtime digital twin screening under six synthetic failure and cyber-attack modes:

- Sensor calibration drift ($\pm 15\%$).
- White-noise telemetry error ($\sigma = 2.0$ m).
- Sensor dropouts and stale state.
- False Data Injection (FDI) on storage telemetry.
- Unit conversion errors (feet vs. meters).
- Hallucinated asset IDs.

The digital twin decision evaluates critical slack relative to default operation:
$$\text{Critical Slack} = \min_{j \in \mathcal{V}_{\text{active}}} \left[ H_j^{\text{plan}} - H_j^{\text{min}} \right]$$

### E3b: Dynamic Burst Response & Human Approval Latency

Models dynamic pipe bursts under three autonomy configurations:

- **Human-in-the-Loop:** Every action (pressure modulation and valve isolation) requires dispatcher approval.
- **Full Autonomous Unchecked:** Automatic pressure reduction and instant isolation upon sensor trigger.
- **MAWRIC-X Governed Autonomy:** Automatic bounded pressure reduction, human-confirmed isolation, and mobile verification dispatch for low-confidence triggers.

### E4: Life-Cycle Techno-Economics & Global Sobol Sensitivity

Integrates water savings, avoided leak losses, energy consumption, and infrastructure costs (sensors, compute platform, and mobile verification units). Evaluates first-order ($S_i$) and total-order ($S_{Ti}$) Sobol variance indices via `SALib`.

---

## Empirical Results & Key Findings

All figures, metrics, and summary tables below reflect verified values from the full multi-decade simulation runs (`results/*_full.csv`):

| Evaluation Dimension | Primary Metric | Observed Value | Physical / Operational Interpretation |
| --- | --- | --- | --- |
| **Siloed Replacement** | Alternative water share | **19.3% – 34.9%** | Siloed reuse/stormwater assets replace substantial potable water before coordination. |
| **Coordination Premium** | Extra potable saved | **0.21 – 2.87 Mm³/yr** | Marginal gain from coordination. Largest in tropical Singapore (2.87 Mm³/yr; 2.9% demand). |
| **Mechanism Attribution** | Shapley dominance | **Integration ($I$) > 65%** | Cross-sector stormwater integration provides the majority of the coordination premium. |
| **Negotiation Fidelity** | ADMM optimality gap | **$\le$ 0.20%** | Decentralized private negotiation matches the central LP optimum in 95% of instances. |
| **Assurance on Net6** | Severe violation intercept | **100% prevented** | The digital twin stopped every command causing hydraulic head violations $> 10$ m. |
| **Safe Plan Preservation** | Twin false rejections | **0.4% (Net6)** | The digital twin rejected only 0.4% of safe commands, compared to 3.1% for static rules. |
| **Twin Failure on Net3** | Unsafe executions | **3.8% (Net3)** | State errors at pump switches caused misses, demonstrating the necessity of safety margins. |
| **Operator Overhead** | Human approvals | **96% reduction** | Bounded autonomy cut human approval bottlenecks from 105.2 down to 4.5 actions per week. |
| **Crew Dispatch** | Field verification | **79% reduction** | Targeted automated pressure modulation cut emergency field dispatches from 84 to 17 per year. |
| **Latency Robustness** | Leak volume growth | **+11% vs. +33%** | Under 4h approval delays, MAWRIC-X losses rose 11% vs. 33% under manual operations. |
| **Economic Payback** | Break-even status | **Unfavorable without co-benefits** | Under declared hardware/software costs, coordination did not pay on water/leak savings alone. |

> [!IMPORTANT]
> **Key Scientific Takeaway:** The coordination premium is physically bounded by alternative supply relative to connected eligible demand. In dry climates (Phoenix), scarcity limits alternative volumes. In temperate climates (London), steady baseline supply leaves modest room for coordination. The largest gains occur where heavy precipitation coincides with uncoordinated storage (Singapore).

---

## Meteorological Data & Quality Control

Daily precipitation (`PRCP`), maximum temperature (`TMAX`), and minimum temperature (`TMIN`) are retrieved directly from the **NOAA Global Historical Climatology Network (GHCN-Daily)** via [`data/download_ghcn.py`](data/download_ghcn.py):

| City Archetype | Station ID | Network Series | Years Analyzed | Preprocessing & Quality Notes |
| --- | --- | --- | --- | --- |
| **Phoenix (PHX)** | `USW00023183` | NOAA GHCN | 2006–2023 (18 yrs) | Sky Harbor Airport. Complete daily records; hot-desert climate (*BWh*). |
| **Los Angeles (LAX)** | `USW00023174` | NOAA GHCN | 2006–2023 (18 yrs) | LAX Airport. Mediterranean rainfall patterns (*Csb*). |
| **London (LHR)** | `UKE00107650` | ECA&D Series | 2006–2023 (18 yrs) | Heathrow Airport. 100% complete records; zero climatology filling. |
| **Singapore (SIN)** | `SNM00048698` | NOAA GHCN | 2003–2020 (18 yrs) | Changi Airport. Climatology-filled for missing TMAX (low variance: $\sigma = 1.4^\circ\text{C}$). |
| **Saudi Reference** | `SA000040438` | NOAA GHCN | 2000–2025 | Riyadh. Archived in `data/raw/ghcn/`; excluded from main runs due to sparse rainfall records. |

### Cryptographic Verification

Verify the SHA-256 hashes of all raw meteorological inputs:

```bash
python data/download_ghcn.py
```

Station CSV records in `data/raw/ghcn/` are cryptographically verified against [`data/raw/ghcn/SHA256SUMS.txt`](data/raw/ghcn/SHA256SUMS.txt).

---

## Scientific Integrity & Reproducibility Guarantees

1. **Deterministic Master Seed:** All stochastic draws (Latin Hypercube parameter sets, forecast error noise, sensor drift, and burst arrivals) are derived deterministically from a single master seed defined in [`mawricx/config.py`](mawricx/config.py):

   ```python
   MASTER_SEED = 20261016
   ```

2. **Elimination of Hardcoded Constants:** All reported figures, LaTeX tables, and macros are compiled directly from `results/*.csv` by [`analysis/make_results.py`](analysis/make_results.py). No metrics are hardcoded into the manuscript.
3. **EPANET Parallel Scratch-File Isolation:** EPANET 2.2 names temporary hydraulic scratch files with standard library routines (`_tempnam`), which can trigger silent race conditions when multiple worker processes execute concurrently. [`mawricx/hydraulics.py`](mawricx/hydraulics.py) forces process-isolated temporary directories via `isolate_tmp()`. Serial reproducibility is verified by [`analysis/verify_e3a_serial.py`](analysis/verify_e3a_serial.py).
4. **Pre-Registered Study Protocol:** All research questions, hypothesis criteria, policy formulations, and statistical tests were locked in [`EXPERIMENT_DESIGN.md`](EXPERIMENT_DESIGN.md) prior to conducting the full multi-decade simulation runs.

---

## Configuration & Parameter Bounds

System configuration parameters are defined in [`mawricx/config.py`](mawricx/config.py):

```python
# Extract nominal parameters
from mawricx.config import nominal_params, sample_params

params = nominal_params()
print(f"Master Seed: {params['master_seed']}")
print(f"Potable Cost: ${params['c_pot']}/m3 | Reclaimed Cost: ${params['c_rec']}/m3")
```

Key nominal parameters include:

- **Reference Population:** 1,000,000 residents across 10 economic sectors.
- **Economic Tariff Weights:** Potable (\$1.50/m³), Reclaimed (\$0.80/m³), Stormwater (\$0.30/m³).
- **Assurance Pressure Bounds:** Minimum service pressure = 20.0 m (14.0 m absolute floor during outages); Minimum tank reserve = 30% capacity.
- **Optimization Horizon:** 7 days receding horizon (MPC); 24-hour time-step for allocation; 1-hour time-step for hydraulic simulation.

---

## Troubleshooting & Platform Notes

### 1. Windows PowerShell Execution Policy

If virtual environment activation fails with `Execution_Policies`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 2. Missing C/C++ Compiler during WNTR Installation

WNTR and SciPy provide pre-compiled wheels for x86_64 architectures on Python 3.10 and 3.11. If pip attempts to build from source:

```bash
pip install --only-binary :all: numpy scipy matplotlib
pip install wntr==1.5.0
```

### 3. Parallel Worker Memory Limits

During full replication (`python run_all.py --full`), E3a spawns parallel workers to simulate Net6 (3,323 nodes). If executing on a system with limited RAM (< 8 GB), restrict worker count:

```bash
python experiments/e3_assurance.py --workers 2
```

---

## Limitations & Operational Scope

- **Synthetic Urban Topology:** The 10-sector demand series reflects calibrated micro-component models and real weather, but is mapped onto standardized EPANET benchmark networks (Net3, Net6) rather than a specific municipal GIS topology.
- **Water Quality Dynamics:** Water quality is governed via strict categorical end-use eligibility (potable, non-potable tertiary, outdoor stormwater). Solute transport, chlorine decay, and pathogen dynamics are not modeled dynamically.
- **Economic Accounting Boundaries:** Economic analysis accounts strictly for direct water and energy savings. Wider societal externalities (carbon offsets, avoided stormwater flood damage, environmental discharge credits) are excluded from the core financial balance.

---

## Development & Contributing

Contributions, issue reports, and research extensions are welcome.

### Code Style & Quality Standards

- Format code following PEP 8 conventions.
- Maintain deterministic seeding using `np.random.default_rng(seed)`.
- Ensure all pull requests pass the invariant test suite:

  ```bash
  python -m pytest tests -q
  ```

---

## Authors, Citation & License

### Authors

- **Toqeer Ali Syed** — *Islamic University of Madinah, Saudi Arabia*
- **Ali Akarma** — *Islamic University of Madinah, Saudi Arabia*
- **Raghda M. Alqurashi** (*Corresponding Author*) — *Umm Al-Qura University, Saudi Arabia*
- **Muhammad Tayyab Naqash** — *Islamic University of Madinah, Saudi Arabia*
- **Qazi U. Farooq** — *Islamic University of Madinah, Saudi Arabia*

### Citation

```bibtex
@article{syed2026mawricx,
  title     = {MAWRIC-X: A Governed Multi-Agent Framework for Urban Water Allocation and Leak Response, with Evidence on the Size of the Coordination Premium},
  author    = {Syed, Toqeer Ali and Akarma, Ali and Alqurashi, Raghda M. and Naqash, Muhammad Tayyab and Farooq, Qazi U.},
  journal   = {Water},
  url       = {https://github.com/aliakarma/MAWRIC}
}
```

### License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for complete terms.
