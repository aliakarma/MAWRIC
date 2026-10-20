# MAWRIC-X: Governed Multi-Agent Coordination for Urban Water

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Pytest](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Hydraulics: WNTR](https://img.shields.io/badge/hydraulics-WNTR%201.5.0-navy.svg)](https://wntr.readthedocs.io/)
[![Optimization: HiGHS](https://img.shields.io/badge/solver-SciPy%20HiGHS-orange.svg)](https://highs.dev/)

A reproducible research codebase for **MAWRIC-X** (*Multi-Agent Water Resource Integrated Coordination*), a governed multi-agent optimization and hydraulic assurance framework for fit-for-purpose urban water allocation and automated leak response.

---

## Table of Contents

- [Overview](#overview)
- [Key Capabilities](#key-capabilities)
- [Architecture & Framework](#architecture--framework)
- [Repository Structure](#repository-structure)
- [Installation & Environment](#installation--environment)
- [Quick Start & Verification](#quick-start--verification)
- [Experimental Protocols (E1–E4)](#experimental-protocols-e1e4)
- [Data & Meteorological Sources](#data--meteorological-sources)
- [Reproducibility Guarantees](#reproducibility-guarantees)
- [Citation & License](#citation--license)

---

## Overview

Urban water networks face growing supply stress, demographic pressure, and climate volatility. Traditional municipal water management operates in organizational silos: potable distribution, wastewater reuse, and stormwater drainage operate independently with static allocations and uncoordinated buffers.

**MAWRIC-X** introduces a multi-tier cyber-physical coordination framework that connects decentralized agent negotiation with deterministic hydraulic governance:

1. **Fit-for-Purpose Resource Allocation:** Dynamically matches tiered water grades (potable, reclaimed wastewater, treated stormwater) across 10 municipal and commercial sectors.
2. **Decentralized Negotiation (ADMM):** Enables autonomous sector agents to negotiate delivery schedules and market-clearing shadow prices while keeping private demand curves confidential.
3. **Deterministic Assurance Layer:** A digital twin safety barrier executed via EPANET / WNTR that intercepts and checks agent control proposals against pressure, velocity, and tank bounds before physical execution.
4. **Automated Leak Response:** Fast pressure-transient detection and coordinated valve routing that drastically reduces physical water losses compared to human-in-the-loop dispatch.

---

## Key Capabilities

- **10 Economic Sectors:** Residential, Hospitality, Healthcare, Education, Commerce, Industry, Data Centers, Public Landscape, Construction, and Public Services.
- **4 Contrasting Climate Archetypes:** Evaluated over 18 observed weather years per city (72 city-years) using NOAA GHCN-Daily records:
  - **Phoenix (PHX):** Hot Desert (*BWh*) — high ET₀, constrained supply.
  - **Los Angeles (LAX):** Mediterranean (*Csb*) — winter-wet, dry summer peaks.
  - **London (LHR):** Temperate Oceanic (*Cfb*) — steady demand, moderate rainfall.
  - **Singapore (SIN):** Tropical Rainforest (*Af*) — high humidity, persistent precipitation.
- **Factorial Mechanism Attribution:** Quantifies the individual and cooperative contributions of **Resource Pooling**, **Cross-Sector Integration**, and **Model Predictive Control (MPC) Forecasting** using cooperative game-theoretic Shapley values.
- **Rigorous Fault Tolerance:** Stress-tested against sensor drift, calibration noise, telemetry dropouts, and adversarial demand over-reporting.
- **Life-Cycle Economics:** Net Present Value (NPV), Levelized Cost of Water (LCOW), and Sobol global variance decomposition across capital expenditure and utility tariff ranges.

---

## Architecture & Framework

```
                          ┌─────────────────────────────────────┐
                          │    External Meteorological Data     │
                          │   (NOAA GHCN-Daily: P, Tmin, Tmax)  │
                          └──────────────────┬──────────────────┘
                                             │
                                             ▼
                          ┌─────────────────────────────────────┐
                          │   Reference Evapotranspiration      │
                          │    & Sector Demand Generator        │
                          │        (mawricx/city.py)            │
                          └──────────────────┬──────────────────┘
                                             │
                   ┌─────────────────────────┴─────────────────────────┐
                   ▼                                                   ▼
       ┌───────────────────────┐                           ┌───────────────────────┐
       │ Centralized Baseline  │                           │   Decentralized ADMM  │
       │   & Factorial LP/MPC  │                           │  Autonomous Agents    │
       │ (mawricx/allocation)  │                           │   (mawricx/agents)    │
       └───────────┬───────────┘                           └───────────┬───────────┘
                   │                                                   │
                   └─────────────────────────┬─────────────────────────┘
                                             │ Control Proposals
                                             ▼
                          ┌─────────────────────────────────────┐
                          │     Deterministic Assurance Layer   │
                          │       (mawricx/assurance.py)        │
                          │   Hydraulic Twin Stress Filter      │
                          │    [Net3 / Net6 via WNTR/EPANET]    │
                          └──────────────────┬──────────────────┘
                                             │ Safe Actions
                                             ▼
                          ┌─────────────────────────────────────┐
                          │      Physical Network Execution     │
                          │      Pressure / Tank Validation     │
                          │        Leak Response (E3b)          │
                          └─────────────────────────────────────┘
```

---

## Repository Structure

```
MAWRIC/
├── mawricx/                    # Core simulation and algorithmic package
│   ├── __init__.py             # Package metadata and version definition
│   ├── agents.py               # Decentralized ADMM negotiation and bidding protocol
│   ├── allocation.py           # Linear Programming (LP) and MPC allocation models
│   ├── assurance.py            # Deterministic hydraulic safety rules and filters
│   ├── city.py                 # 10-sector reference city demand and storage models
│   ├── config.py               # Latin Hypercube parameter distributions and master seed
│   ├── hydraulics.py           # WNTR / EPANET simulation harness and network metrics
│   └── weather.py              # GHCN weather ingestion and Hargreaves ET₀ computation
│
├── experiments/                # Empirical experimental benchmarks (E1 - E4)
│   ├── e1_coordination.py      # E1: Coordination premium and factorial Shapley analysis
│   ├── e2_negotiation.py       # E2: Decentralized ADMM negotiation and privacy metrics
│   ├── e3_assurance.py         # E3a: Safety assurance and hydraulic fault injection
│   ├── e3b_leak_response.py    # E3b: Automated valve routing and leak isolation
│   └── e4_economics.py         # E4: Life-cycle NPV, LCOW, and Sobol sensitivity analysis
│
├── analysis/                   # Statistical analysis and figure generation
│   ├── make_results.py         # Synthesis script for publication tables, numbers, and figures
│   ├── build_bib.py            # Verification and bibliography assembly tool
│   ├── e3a_robust_twin.py      # Post-hoc robustness checks for hydraulic digital twins
│   ├── e3a_twin_misses.py      # Hydraulic margin sweep and miss-classification analysis
│   ├── verify_e3a_serial.py    # Deterministic serial audit for assurance simulations
│   └── make_submission.py      # Supplementary package archiving pipeline
│
├── data/                       # Meteorological datasets and station retrieval
│   ├── download_ghcn.py        # Automated NOAA NCEI daily record download & SHA-256 check
│   ├── raw/ghcn/               # Station CSV records with SHA256SUMS.txt integrity ledger
│   └── processed/              # Climatology-filled weather inputs for PHX, LAX, LHR, SIN
│
├── results/                    # Validated experimental simulation outputs
│   ├── *_full.csv              # Full multi-decade simulation runs
│   ├── *_smoke.csv             # Fast-check smoke run outputs
│   └── logs/                   # Execution logs for full benchmark evaluations
│
├── literature/                 # Systematic literature review and PRISMA evidence base
│   ├── review_body.md          # Comprehensive literature review synthesis
│   ├── source_ledger.csv       # Curated corpus ledger across 150+ research sources
│   ├── extraction_sheet.csv    # Dimensional comparative extraction matrix
│   ├── references_lit.bib      # BibTeX literature database
│   └── tools/                  # Automated search and extraction utilities (Crossref, OpenAlex)
│
├── tests/                      # Verification and unit test suite
│   └── test_core.py            # Core tests (ADMM convergence, Shapley, hydraulics, ET₀)
│
├── EXPERIMENT_DESIGN.md        # Pre-registered experimental design and change log
├── literature_review.md        # Monolithic literature review and gap analysis report
├── requirements.txt            # Pinned dependencies for reproducible execution
├── run_all.py                  # Top-level unified orchestrator (smoke / full modes)
└── .gitignore                  # Exclusion rules (caches, manuscript, raw metadata)
```

---

## Installation & Environment

### Prerequisites
- **Python**: `3.10.x` or `3.11.x` (64-bit recommended)
- **C/C++ Compiler**: Standard system build tools for SciPy / WNTR wheel support.

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aliakarma/MAWRIC.git
   cd MAWRIC
   ```

2. **Create and activate a virtual environment:**

   *On Linux / macOS:*
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   *On Windows (PowerShell):*
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Quick Start & Verification

### 1. Run Core Test Suite (< 15 seconds)
Run the automated test suite to confirm mathematical, algorithmic, and physical invariants:
```bash
python -m pytest tests -q
```
*Expected output: All 6 test suites passing (ADMM optimality, Shapley summation, Hargreaves bounds, critical slack equivalence).*

### 2. Fast Smoke Test (2–3 minutes)
Run every experiment at reduced sample scale to verify end-to-end execution:
```bash
python run_all.py --smoke
```
This produces `results/*_smoke.csv` and populates `results/logs/*_smoke.log`.

### 3. Full Benchmark Replication (~30–60 minutes)
Recreate the full empirical study across all 72 city-years, hydraulic networks, and Monte Carlo draws:
```bash
python run_all.py --full
```

---

## Experimental Protocols (E1–E4)

| Experiment | Focus | Methodology | Networks / Datasets | Key Metrics |
|---|---|---|---|---|
| **E1** | Coordination Premium | 8-policy factorial optimization (LP/MPC) with Latin Hypercube draws | 72 city-years across 4 climates (PHX, LAX, LHR, SIN) | Potable reduction (%), spill volumes, Shapley values, oracle gap |
| **E2** | Decentralized Negotiation | ADMM consensus protocol with local privacy bounds & verification caps | 10 economic sectors, 240 randomized diurnal profiles | Iterations to convergence, shadow price error, misreporting resilience |
| **E3a** | Hydraulic Safety Assurance | WNTR hydraulic stress filter under fault injection (drift, noise, drops) | Net6 (3,323 nodes, 32 tanks), Net3 (92 nodes) | Pressure violations prevented, false-rejection rate, critical slack |
| **E3b** | Dynamic Leak Isolation | Dynamic burst modeling & valve routing under varying approval latencies | EPANET Net3 benchmark network | Non-revenue water loss ($m^3$), isolation time, customer pressure deficit |
| **E4** | Economic Feasibility | Life-cycle cost-benefit analysis under climate & tariff uncertainty | 25-year lifecycle, Latin Hypercube Sobol sampling | NPV ($M), LCOW ($/m^3$), first-order & total Sobol indices |

---

## Data & Meteorological Sources

All precipitation and temperature data are derived from the **NOAA Global Historical Climatology Network (GHCN-Daily)** access service:

- **USW00023183**: Phoenix Sky Harbor International Airport, AZ, USA
- **USW00023174**: Los Angeles International Airport, CA, USA
- **UKE00107650**: London Heathrow Airport, United Kingdom (ECA&D series)
- **SNM00048698**: Singapore Changi International Airport, Singapore
- **SA000040438 & SA000040430**: Riyadh and Al-Madinah, Saudi Arabia (reference stations)

Integrity can be validated at any time using:
```bash
python data/download_ghcn.py
```
Station files in `data/raw/ghcn/` are verified against cryptographic hashes recorded in `SHA256SUMS.txt`.

---

## Reproducibility Guarantees

- **Deterministic Seeds:** All stochastic sampling (Latin Hypercube samples, forecast error generators, sensor noise) derives deterministically from a single master seed defined in [`mawricx/config.py`](mawricx/config.py) (`MASTER_SEED = 20261016`).
- **No Hardcoded Metrics:** All figures, macro variables, and statistical values are computed dynamically from simulation output files via [`analysis/make_results.py`](analysis/make_results.py).
- **Self-Contained EPANET Models:** EPANET benchmarks (Net3 and Net6) are executed via `wntr==1.5.0` without external proprietary solver requirements.

---

## Citation & License

This project is licensed under the [MIT License](LICENSE).

```bibtex
@article{mawricx2026water,
  title     = {MAWRIC-X: A Governed Multi-Agent Framework for Urban Water Allocation and Leak Response, with Evidence on When Coordination Pays},
  journal   = {Water},
  year      = {2026},
  note      = {Code and empirical data available at https://github.com/aliakarma/MAWRIC}
}
```
