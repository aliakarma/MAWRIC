"""Code the core corpus into the finding-gap extraction sheet.

Coding is by one analyst (Claude) from titles and abstracts (V1/V2), so every
count derived from it describes this coded corpus only.

Controlled vocabulary
  study_type : review | simulation | field | system-demo | conceptual | empirical-stats | experiment | lab
  method     : LLM-MAS; MARL; DRL; MPC; LP/MILP; network-flow; metaheuristic; fuzzy; hydraulic-model;
               ML-detection; statistical; survey/interview; field-experiment; QMRA; game-theory;
               POMDP/VoI; robotics-hardware; formal-shield; CBA/DCF; system-dynamics; rule-based
  setting    : benchmark-WDN; real-utility; city-scale; building; basin; lab; none
  outcomes   : task-success; detection-accuracy; energy-cost; potable-offset; real-losses;
               pressure-service; resilience; safety-violations; NPV-cost; emissions; equity;
               latency; adoption; health-risk; trade-offs
  moderators : water-cycle functions covered: F-alloc; F-ops; F-loss; F-demand; F-reuse; F-gov;
               F-econ; F-robot; F-quality
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# key: (study_type, method, setting, outcomes, functions, limitations_tags, future_work_tags, country, key_finding)
C = {
 # C1 digital twins
 "bam2025": ("review", "review", "none", "trade-offs", "F-ops;F-loss;F-reuse;F-quality", "interoperability;field-validation", "integration;field-validation", "", "DT use in water is emerging; gaps in validation and integration"),
 "ramos2023": ("simulation", "hydraulic-model", "real-utility", "real-losses;NPV-cost", "F-ops;F-loss", "", "", "PT", "DT + DMA sectorization: ~80% potential real-loss reduction (Gaula)"),
 "ramos2022": ("simulation", "hydraulic-model;metaheuristic", "real-utility", "real-losses", "F-ops;F-loss", "", "", "PT", "DT + PRV optimization up to 28% water savings in a DMA"),
 "pesantez2022": ("simulation", "hydraulic-model", "real-utility", "pressure-service;energy-cost", "F-ops;F-demand", "", "", "US", "AMI-coupled DT shows COVID demand shifts change water age, pressure, energy"),
 "ciliberti2023": ("conceptual", "hydraulic-model", "none", "adoption", "F-ops", "", "integration", "", "DT to standardized digital water services in QGIS"),
 "altindas2026": ("review", "review", "none", "trade-offs", "F-reuse;F-ops", "field-validation;interoperability;governance", "field-validation;governance;benchmarking", "", "48 DT-WSUD studies mostly conceptual/prototype; governance and interoperability gaps"),
 "fu2022": ("review", "review", "none", "detection-accuracy", "F-demand;F-loss;F-quality", "field-validation;data-availability;explainability", "multi-agent;explainability;field-validation", "", "DL in UWM mostly benchmark/synthetic tests; MAS and DT named as challenges"),
 "eggimann2017": ("review", "review", "none", "NPV-cost", "F-ops;F-demand", "data-availability;cost-benefit", "cost-benefit", "", "data-driven UWM promising; cost-benefit hard to assess"),
 # C3 LLM / agentic
 "choi2025": ("system-demo", "LLM-MAS", "city-scale", "task-success", "F-ops", "", "field-validation", "KR", "GPT agent in urban DT for building energy (not water)"),
 "restuccia2026": ("system-demo", "LLM-MAS", "benchmark-WDN", "task-success;energy-cost", "F-ops", "", "", "IT", "edge agentic RAG raises full-task success 30-40% over zero-shot"),
 "khadam2026": ("review", "review", "none", "trade-offs", "F-ops", "field-validation;uncertainty;benchmarking", "real-world-validation;benchmarking;interoperability", "", "82 agent-based UDT studies: low TRL, simulation validation, little uncertainty handling"),
 "wang2026agentic": ("system-demo", "LLM-MAS", "benchmark-WDN", "task-success", "F-ops", "", "", "UK", "EPANET-Agentic 100% task success with human-in-the-loop oversight"),
 "wang2027control": ("simulation", "LLM-MAS", "benchmark-WDN", "task-success;energy-cost", "F-ops", "", "selective-autonomy", "UK", "delegating pipeline nodes changes reliability and cost far more than solution quality"),
 "wang2026llm": ("system-demo", "LLM-MAS", "benchmark-WDN", "task-success;energy-cost", "F-ops", "numerical-constraints", "", "UK", "LLM agents calibrate and optimize pumps; constraint enforcement in NL is hard"),
 "hosseini2026": ("conceptual", "LLM-MAS", "none", "trade-offs", "F-ops;F-loss;F-gov", "", "negotiation;field-validation", "", "LLM-MA framework incl. negotiating agents; conceptual"),
 "mu2026leak": ("simulation", "LLM-MAS;ML-detection", "benchmark-WDN", "detection-accuracy", "F-loss", "", "", "CN", "LeakAgent ~96% detection+partition accuracy across five networks"),
 "syed2026agentic": ("simulation", "LLM-MAS", "city-scale", "latency;task-success", "F-gov;F-ops", "field-validation", "field-validation", "SA", "agentic DT cuts detection latency vs rule-based in 18,000 synthetic incidents (authors' prior work)"),
 "syed2026climate": ("review", "review", "none", "trade-offs", "F-gov", "field-validation", "integration", "SA", "agentic AI for cities clustered, almost no validated cross-domain deployment (authors' prior work)"),
 "kalyuzhnaya2025": ("system-demo", "LLM-MAS", "city-scale", "task-success", "F-gov", "", "", "RU", "LLM agents route urban queries with 94-99% pipeline accuracy"),
 "he2025iwms": ("system-demo", "LLM-MAS", "basin", "task-success", "F-alloc", "", "", "CN", "LLM workflow orchestration for water resources management"),
 "arslan2026": ("review", "review", "none", "trade-offs", "F-gov", "field-validation;reproducibility", "empirical-rigor;human-in-the-loop", "", "34 LLM-SWM studies mostly conceptual or observational"),
 "xu2025": ("conceptual", "LLM-MAS", "none", "task-success", "F-quality", "reliability", "benchmarking", "", "foundation models not yet reliable; need water benchmarks"),
 "tamuka2026": ("review", "review", "none", "safety-violations", "F-gov", "field-validation;data-availability", "human-in-the-loop;safety-constraints", "", "agentic AI should recommend while humans approve; validation insufficient"),
 "alevizos2025": ("simulation", "MARL;ML-detection;robotics-hardware", "basin", "detection-accuracy;energy-cost", "F-quality;F-robot", "", "", "", "robot+IoT multi-agent water quality surveillance"),
 # C2 MAS / control
 "hu2023": ("simulation", "MARL", "benchmark-WDN", "energy-cost;real-losses", "F-ops;F-loss", "", "", "CN", "MADDPG pump+valve scheduling; water loss dominates cost"),
 "jia2025": ("review", "review", "none", "trade-offs", "F-ops", "scalability;communication", "robustness;generalization", "", "MARL in water systems faces heterogeneity and communication limits"),
 "negm2024": ("review", "review", "none", "trade-offs", "F-ops;F-loss", "", "", "", "DRL applications in WDN and stormwater reviewed"),
 "kage2025": ("review", "review", "none", "trade-offs", "F-alloc;F-ops", "field-validation;explainability", "sim-to-real;explainability", "", "RL agents trained in simulation; safety-critical explainability needed"),
 "javed2025": ("review", "review", "none", "detection-accuracy", "F-loss", "", "leak-prevention", "", "DRL for leakage management still evolving"),
 "grosso2016": ("simulation", "MPC", "real-utility", "energy-cost;pressure-service", "F-ops", "", "", "ES", "stochastic MPC variants for Barcelona DWN"),
 "castelletti2023": ("review", "review", "none", "trade-offs", "F-ops;F-alloc", "benchmarking;uncertainty;multi-objective", "benchmarking;forecast-value;multi-objective", "", "149 MPC water papers lack benchmarking, uncertainty and forecast-value analysis"),
 "han2018": ("simulation", "game-theory", "basin", "equity;trade-offs", "F-alloc", "", "", "CN", "bi-level game raises cooperation willingness 20% to 80%"),
 "gerkey2004": ("conceptual", "LP/MILP", "none", "trade-offs", "F-robot", "", "", "", "MRTA taxonomy maps task allocation to OR problems"),
 "korsah2013": ("conceptual", "LP/MILP", "none", "trade-offs", "F-robot", "", "", "", "iTax extends MRTA taxonomy to interrelated utilities"),
 # C4 allocation / reuse
 "porse2017": ("simulation", "network-flow", "city-scale", "potable-offset;trade-offs", "F-alloc;F-reuse;F-demand", "fragmentation", "governance", "US", "LA imports cut 30% with stormwater, reuse and conservation; fragmented agencies matter"),
 "matrosov2015": ("simulation", "metaheuristic", "city-scale", "NPV-cost;energy-cost;resilience;trade-offs", "F-alloc;F-reuse;F-loss;F-demand", "", "", "UK", "many-objective portfolios for London reveal masked trade-offs"),
 "padula2013": ("simulation", "LP/MILP", "city-scale", "NPV-cost", "F-alloc;F-demand;F-loss", "", "", "UK", "including demand management cut discounted cost 10%"),
 "hsieh2025": ("simulation", "fuzzy", "city-scale", "resilience;health-risk", "F-alloc;F-reuse;F-quality", "", "", "TW", "quality-weighted dynamic multi-source allocation raises resilience 9.6%"),
 "garridobaserba2024": ("simulation", "hydraulic-model;CBA/DCF", "building", "energy-cost;NPV-cost", "F-reuse;F-econ", "", "", "US", "block-scale decentralization recovers water, energy, nutrients"),
 "seguela2026": ("empirical-stats", "CBA/DCF", "building", "emissions;NPV-cost;potable-offset", "F-reuse;F-econ", "asset-scale-only", "", "AE", "NPW gains depend on source substitution and configuration, not reuse volume"),
 "sapkota2015": ("review", "review", "none", "trade-offs", "F-reuse;F-alloc", "integration", "interaction-centralized-decentralized", "", "hybrid systems' effect on centralized operations unknown"),
 "mosleh2021": ("review", "review", "none", "trade-offs", "F-alloc;F-reuse;F-ops", "socio-economic;water-energy", "water-energy;socio-economic", "", "IUWM models rarely include water-energy, social and policy factors"),
 "ndeketeya2022": ("simulation", "hydraulic-model", "city-scale", "potable-offset", "F-reuse;F-alloc", "", "storage", "ZA", "Johannesburg harvestable runoff twice non-potable need; storage limits reliability"),
 "zhong2025": ("simulation", "LP/MILP", "city-scale", "NPV-cost;potable-offset", "F-reuse;F-alloc;F-econ", "", "", "US", "reclaimed network more cost-effective than rain tanks for urban food"),
 "exposito2024": ("empirical-stats", "CBA/DCF", "real-utility", "NPV-cost", "F-reuse;F-econ", "", "", "ES", "reclaimed water production cost from Andalusian WWTP finances"),
 "schoen2018": ("simulation", "QMRA", "building", "health-risk", "F-reuse;F-quality", "", "", "US", "wastewater intrusion into non-potable systems gives unacceptable risk"),
 "jahne2024": ("simulation", "QMRA", "none", "health-risk", "F-reuse;F-quality", "", "", "US", "harmonized fit-for-purpose microbial treatment targets"),
 "jeffrey2026": ("review", "review", "none", "health-risk", "F-reuse;F-quality;F-gov", "", "", "", "dual-pipe incidents dominated by cross-connections and misuse"),
 "giammar2021": ("simulation", "CBA/DCF", "real-utility", "NPV-cost;energy-cost", "F-reuse;F-econ", "", "", "US", "reuse LCOW 0.40-0.54 USD/m3, 0.30-0.84 kWh/m3"),
 "rohrer2017": ("simulation", "rule-based", "city-scale", "potable-offset;NPV-cost", "F-reuse;F-ops", "", "", "ZA", "rudimentary RTC of ponds raises stormwater yield cost-effectively"),
 "lopezzavala2016": ("field", "CBA/DCF", "building", "potable-offset;NPV-cost", "F-reuse;F-econ", "", "", "MX", "RWH + greywater cut campus potable use 48%"),
 "ferreira2023": ("simulation", "rule-based", "building", "potable-offset", "F-reuse", "", "", "PT", "hybrid rain/greywater effectiveness set by end uses and storage"),
 "badruzzaman2022": ("field", "QMRA;CBA/DCF", "real-utility", "potable-offset;health-risk", "F-reuse;F-quality", "", "", "SA", "reclaimed cooling makeup viable, 27% less water"),
 "mytton2021": ("review", "review", "none", "potable-offset", "F-demand", "data-availability", "measurement", "", "data-centre water use poorly measured"),
 "lunstad2024": ("review", "review", "none", "potable-offset", "F-demand;F-ops", "coordination", "coordinated-networks", "US", "smart controllers cut demand 15%; coordinated control is future work"),
 "porse2023": ("simulation", "network-flow", "city-scale", "potable-offset;energy-cost", "F-reuse;F-alloc;F-demand", "", "", "US", "reuse up to 30% of LA supply; energy intensity rises without conservation"),
 "maldonado2025": ("review", "review", "none", "trade-offs", "F-reuse;F-gov", "governance", "governance", "", "AI for water harvesting reviewed; governance gaps"),
 "radcliffe2020": ("review", "review", "none", "trade-offs", "F-reuse;F-gov", "", "", "AU", "Australian reuse history; economics drove plant mothballing"),
 # C5 loss
 "liemberger2019": ("empirical-stats", "statistical", "none", "real-losses;NPV-cost", "F-loss", "", "", "", "global NRW 126 bn m3/yr, USD 39 bn/yr"),
 "vicente2016": ("review", "review", "none", "real-losses", "F-loss;F-ops", "practice-gap", "", "", "PM progress not reflected in practice"),
 "romeroben2023": ("review", "review", "benchmark-WDN", "detection-accuracy", "F-loss", "", "", "", "model-based to data-based leak methods"),
 "vrachimis2022": ("simulation", "ML-detection;statistical", "benchmark-WDN", "detection-accuracy;NPV-cost", "F-loss", "benchmarking", "benchmarks", "CY", "BattLeDIM: need better methods and more open benchmarks"),
 "vanzyl2007": ("lab", "hydraulic-model", "lab", "real-losses", "F-loss", "", "", "ZA", "leakage exponents above 0.5 explained by pipe material behaviour"),
 "vanzyl2014": ("lab", "hydraulic-model", "lab", "real-losses", "F-loss", "", "", "ZA", "N1 ranges 0.5 to 1.5 for deforming leaks"),
 "gonelas2015": ("simulation", "CBA/DCF;hydraulic-model", "real-utility", "NPV-cost;real-losses", "F-loss;F-econ", "", "", "GR", "PM reaches economic leakage level, Kozani"),
 "islam2013": ("simulation", "hydraulic-model;CBA/DCF", "real-utility", "NPV-cost;real-losses", "F-loss;F-econ", "", "", "TH", "ELL nomographs for Bangkok DMA"),
 "lambert2005": ("conceptual", "CBA/DCF", "none", "NPV-cost;real-losses", "F-loss;F-econ", "", "", "", "economic intervention frequency for ALC"),
 "moslehi2020": ("field", "CBA/DCF;statistical", "real-utility", "NPV-cost;real-losses", "F-loss;F-econ", "", "", "IR", "SR-ELL 27 m3/connection/yr in Mashhad"),
 "ahopelto2020": ("simulation", "CBA/DCF", "real-utility", "NPV-cost", "F-loss;F-econ", "", "", "FI", "leakage reduction not always cost-beneficial at moderate loss levels"),
 "aboelnga2018": ("field", "statistical", "real-utility", "real-losses;NPV-cost", "F-loss", "", "", "JO", "BABE: reported bursts 37% of real losses, response time matters"),
 "brentan2018": ("simulation", "metaheuristic;hydraulic-model", "benchmark-WDN", "energy-cost;real-losses", "F-ops;F-loss", "", "", "BR", "joint PRV+pump control ~50% energy saving and leakage reduction"),
 "shao2019": ("simulation", "metaheuristic;hydraulic-model", "benchmark-WDN", "energy-cost;real-losses", "F-ops;F-loss", "", "", "CN", "joint pump+PRV beats separate scheduling: 33% leakage, 25% energy"),
 "ferrarese2024": ("review", "review", "benchmark-WDN", "energy-cost;real-losses", "F-ops;F-loss", "benchmarking", "comparability", "", "36 metaheuristic studies hard to compare"),
 "balut2019": ("simulation", "statistical", "benchmark-WDN", "resilience", "F-loss;F-robot", "", "", "PL", "repair ranking for post-disaster scheduling"),
 "assad2020": ("simulation", "metaheuristic", "real-utility", "resilience;NPV-cost", "F-loss;F-robot", "", "", "CA", "crew-constrained restoration plan cuts duration 48%"),
 "jeon2024": ("field", "robotics-hardware", "real-utility", "detection-accuracy", "F-robot;F-loss", "", "", "KR", "MFL in-pipe robot validated on 1 km test bed"),
 "aitken2021": ("review", "review", "none", "trade-offs", "F-robot", "robustness", "multi-robot;long-term-operation", "", "pipe robots need SLAM robustness for long operations"),
 "memarzadeh2016insp": ("simulation", "POMDP/VoI", "none", "NPV-cost", "F-robot;F-loss", "", "", "US", "VoI-based inspection scheduling within POMDP maintenance"),
 "marzola2021": ("field", "statistical", "real-utility", "real-losses", "F-loss;F-demand", "", "", "IT", "MNF inaccurate with irregular users; FAVAD fits data-dependent"),
 "wang2026carbon": ("simulation", "statistical", "city-scale", "energy-cost;emissions;potable-offset", "F-loss;F-ops", "", "", "", "pipe cleaning choices change energy, carbon and water at scale"),
 # C6 ops / nexus
 "menke2016": ("simulation", "LP/MILP", "benchmark-WDN", "energy-cost;emissions", "F-ops", "", "", "UK", "pump scheduling can offer grid demand response"),
 "tasseff2024": ("simulation", "LP/MILP", "benchmark-WDN", "energy-cost", "F-ops", "", "", "US", "polyhedral relaxations tighten pump scheduling bounds"),
 "wu2020": ("review", "review", "none", "energy-cost;emissions", "F-ops", "", "integrated-modelling", "", "WEN responses across planning, design, operation"),
 "putri2025": ("simulation", "MPC", "benchmark-WDN", "energy-cost;pressure-service", "F-ops", "", "", "", "stability-guaranteed data-driven NMPC, 8% cost saving"),
 "rambo2017": ("empirical-stats", "statistical", "city-scale", "energy-cost", "F-ops;F-alloc", "silo", "", "SA", "water and energy treated as silos in Saudi Arabia"),
 # C7 demand
 "boyle2013": ("review", "review", "none", "potable-offset", "F-demand", "privacy;cost-benefit", "cost-benefit", "", "smart metering moving from pilot to mainstream"),
 "sonderlund2016": ("review", "review", "none", "potable-offset", "F-demand", "cost-benefit", "cost-benefit", "", "feedback cuts use 2.5-28.6% (mean 12.15%)"),
 "ferraro2013": ("experiment", "field-experiment", "real-utility", "potable-offset", "F-demand", "", "", "US", "social comparison works best for high users and decays"),
 "olmstead2009": ("review", "statistical", "none", "potable-offset;NPV-cost", "F-demand;F-econ", "", "", "US", "price more cost-effective than nonprice conservation"),
 "monks2020": ("survey", "survey/interview", "none", "NPV-cost", "F-demand;F-econ", "", "stochastic-benefit-modelling", "AU", "expert-elicited DWM benefit distributions"),
 "gonzalez2018": ("empirical-stats", "statistical", "building", "potable-offset", "F-demand", "", "", "DE", "hospital water 103 m3 per bed per year"),
 # C8 governance
 "alshiekh2018": ("method", "formal-shield", "none", "safety-violations", "F-gov", "", "", "", "shield corrects unsafe RL actions against temporal-logic spec"),
 "hobbs2023": ("review", "formal-shield", "none", "safety-violations", "F-gov", "", "", "US", "runtime assurance safety filters for complex control"),
 "taormina2018": ("simulation", "ML-detection;rule-based", "benchmark-WDN", "detection-accuracy", "F-gov", "", "", "", "BATADAL on C-Town: detection time and accuracy"),
 "hassanzadeh2020": ("review", "review", "none", "safety-violations", "F-gov", "", "cooperative-defense", "US", "15 water cyber incidents: rising frequency and complexity"),
 "tuptuk2021": ("review", "review", "none", "safety-violations", "F-gov", "", "", "", "state of water-sector cyber-security research"),
 "doorn2021": ("review", "review", "none", "trade-offs", "F-gov", "", "participatory-design", "", "responsible AI in water needs plural values and participation"),
 "savic2022": ("review", "review", "none", "safety-violations", "F-gov", "", "human-in-the-loop;fallback;cybersecurity", "UK", "automation lessons: humans in loop, fallback, redundant sensors"),
 "olsson2020": ("conceptual", "rule-based", "none", "trade-offs", "F-ops;F-gov", "", "integration", "", "automation is precondition for integrated urban water cycle"),
 "almheiri2024": ("empirical-stats", "survey/interview", "real-utility", "adoption", "F-gov", "skills;data-security", "", "AE", "AI adoption barriers in a UAE utility"),
 "okwori2026": ("empirical-stats", "survey/interview", "real-utility", "adoption", "F-gov", "kpi;governance", "impact-measurement", "SE", "AI decision support stalls; unclear impact KPIs"),
 # C9 econ / evaluation
 "daniel2023": ("survey", "survey/interview", "real-utility", "adoption;NPV-cost", "F-econ;F-gov", "", "", "", "survey of utility digital transformation drivers and impacts"),
 "erfani2018": ("simulation", "LP/MILP", "city-scale", "NPV-cost", "F-alloc;F-econ", "", "", "UK", "real-options multistage scenario trees for supply planning"),
 "gillingham2018": ("review", "statistical", "none", "NPV-cost", "F-econ", "measurement", "causal-evaluation", "US", "ex post evaluation of efficiency programs"),
}

ledger = {r["key"]: r for r in csv.DictReader((ROOT / "source_ledger.csv").open(encoding="utf-8"))}
cols = ["id", "citation_key", "title", "authors", "year", "venue", "doi_or_url", "source_tool", "verification_level",
        "preprint", "cluster", "study_type", "method", "data_source", "data_end_year", "population", "country",
        "setting", "theory", "predictors", "mediators", "moderators", "outcomes", "relations", "key_finding",
        "limitations_tags", "future_work_tags", "notes"]
with (ROOT / "extraction_sheet.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for i, (k, v) in enumerate(C.items(), 1):
        L = ledger[k]
        st, me, se, out, fn, lim, fw, cc, kf = v
        nfun = len([x for x in fn.split(";") if x])
        w.writerow({"id": i, "citation_key": k, "title": L["title"], "authors": L["authors"], "year": L["year"],
                    "venue": L["venue"], "doi_or_url": L["doi_or_url"], "source_tool": L["retrieved_via"],
                    "verification_level": L["verification_level"] + " (abstract)", "preprint": L["preprint"],
                    "cluster": L["cluster"], "study_type": st, "method": me, "data_source": "", "data_end_year": "",
                    "population": "", "country": cc, "setting": se, "theory": "", "predictors": "",
                    "mediators": "", "moderators": fn, "outcomes": out, "relations": "", "key_finding": kf,
                    "limitations_tags": lim, "future_work_tags": fw, "notes": f"functions_covered={nfun}"})
print("coded", len(C))
