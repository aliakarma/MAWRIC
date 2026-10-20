# Literature Review and Research-Gap Analysis for MAWRIC-X

**Paper:** MAWRIC-X, governed multi-agent coordination of fit-for-purpose water allocation, loss recovery and economics in smart cities
**Target journal:** MDPI *Water*
**Search window:** searches run 16 October 2026, publication years 1980 to 2026, with a recency sweep over 2025 and 2026
**Method:** the finding-gap protocol (modules M0, M1, M3, M4, M9, M10, M11, M12), with a logged search, a verified source ledger and a coded extraction sheet

Every paper named in this review resolved at doi.org during the search, and its metadata came from the publisher record (verification level V2). Claims about findings rest on the abstract. No full text was read, so method details and limitation statements are reported "per abstract". Epistemic tags follow the protocol: **[S]** source-verified in this session, **[B]** background knowledge not re-verified, **[I]** inference by the analyst.

Supporting files in `literature/`:

| File | Content |
|---|---|
| `search_log.csv` | every logged query (120 database queries plus the web lookups listed in Section 10) |
| `source_ledger.csv` | 172 verified sources with DOI, venue, verification level and use |
| `references_lit.bib` | publisher BibTeX for all 172 sources, keyed as in this review |
| `extraction_sheet.csv` | 104 core papers coded for method, testbed, metrics, functions covered and limitations |
| `gap_matrix_out/` | corpus analytics from `gap_matrix.py` (`summary.md`, `tables.tex`) |
| `abstracts.md` | the retrieved abstracts behind every finding claim |
| `primary_sources/` | notes on regulatory texts |

---

## 1. Scope and search strategy (M0)

**Scope sentence.** How AI agents, digital twins, humans and field robots can jointly allocate water of different quality to urban users, operate delivery, recover physical losses and justify the investment, while hard safety, quality, equity and authorization constraints hold.

| Concept block | Core terms | Synonyms and neighbouring terms searched |
|---|---|---|
| Urban water system | water distribution network, urban water cycle | integrated urban water management (IUWM), hybrid water supply, one water, water sensitive urban design, smart water grid |
| Intelligence and coordination | multi-agent system, agentic AI | MARL, LLM agents, LLM-based multi-agent systems, distributed MPC, decomposition, negotiation, Contract Net, digital twin |
| Water-cycle functions | fit-for-purpose allocation, loss recovery | reclaimed water, stormwater harvesting, rainwater harvesting, greywater, dual reticulation, leakage, pressure management, FAVAD, economic level of leakage, crew scheduling, in-pipe robot, pump scheduling |
| Governance | human-in-the-loop, autonomy | levels of automation, runtime assurance, safety shield, cyber-physical attack, false data injection, responsible AI, EU AI Act, NIST AI RMF |
| Economics and evaluation | cost-benefit, NPV | economic intervention frequency, smart-metering business case, real options, Sobol sensitivity, causal impact, stepped-wedge trial |

**Inclusion.** Journal articles, conference papers, reviews and preprints in English on urban water systems or on methods those systems adopt. **Exclusion.** Pure agriculture or river-basin allocation without an urban component, unless the method transfers directly. Gas and power-grid studies were kept only for generic coordination methods.

**Passes run.** A (reviews and seeds, 16 queries), B (cluster searches, 57 queries), E (recency 2025 to 2026, 6 queries), F (disconfirmation, 8 queries), plus parameter and tool lookups (19 queries), self-overlap and correction lookups (3 queries) and 7 web lookups for regulations and the authors' portfolio. Tools: OpenAlex API (99 queries) until its free daily budget ran out, then the Crossref API (21 queries), Semantic Scholar for missing abstracts and doi.org content negotiation for publisher BibTeX. The Consensus and Scholar Gateway connectors named in the protocol were not available in this session.

**Existing reviews found [S].** Eighteen reviews map parts of the field: digital twins in water (Ghorbani Bam et al. 2025), digital twins for water sensitive urban design (Altındaş et al. 2026), agent-based urban digital twins (Khadam et al. 2026), deep learning in urban water management (Fu et al. 2022), data-driven urban water management (Eggimann et al. 2017), deep reinforcement learning for urban water systems (Negm et al. 2024), reinforcement learning in water resources management (Kåge et al. 2025), MARL in water environment systems (Jia and Pei 2025), DRL for leak management (Javed et al. 2025), MPC of water resources systems (Castelletti et al. 2023), LLMs for sustainable water management (Arslan and Munawar 2026), human-governed agentic AI for SCADA security (Tamuka et al. 2026), integrated urban water management (Thakur et al. 2024, Mosleh et al. 2021), hybrid water supply (Sapkota et al. 2015), leak detection (Romero-Ben et al. 2023, Farah and Shahrour 2024), leakage estimation and mitigation (Serafeim et al. 2024), metaheuristics for leakage and energy (Ferrarese and Malavasi 2024) and pressure management (Vicente et al. 2016). None of these reviews names the gap this paper targets as its finding. Several name its ingredients: integration, field validation, governance and cost-benefit evidence (Section 4).

---

## 2. Map of the literature (M1)

Coded corpus: 104 papers (34 reviews, 38 simulation studies, 6 system demonstrations, 6 field studies, 7 empirical statistical studies, 13 other). Counts below describe this corpus only.

| Cluster | Core question | Representative papers | Dominant method | Well understood | Uncertain | Neglected question |
|---|---|---|---|---|---|---|
| C1 Urban water digital twins | Can a calibrated model coupled to live data support operation? | Ramos et al. 2022, 2023, Pesantez et al. 2022, Ghorbani Bam et al. 2025, Altındaş et al. 2026 | hydraulic model plus data | DT plus pressure management cuts real losses in single DMAs (28% in Ramos et al. 2022, about 80% potential in Ramos et al. 2023) [S] | operational benefit at city scale, governance, interoperability (48 DT-WSUD studies mostly conceptual or prototype, Altındaş et al. 2026) [S] | the twin as a safety check on proposed commands rather than as a dashboard [I] |
| C2 Multi-agent control and coordination | Does distributed or learned control match centralized performance? | Hu et al. 2023, Grosso et al. 2016, Segovia et al. 2021, Castelletti et al. 2023, Doostmohammadian et al. 2025 | MARL, MPC, decomposition | MPC and decomposition handle network operation under demand uncertainty [S] | benchmarking against other controllers and the value of forecasts (Castelletti et al. 2023) [S] | coordination among independent owners with private data and different objectives [I] |
| C3 LLM and agentic AI in water | Can LLM agents run water engineering workflows? | Wang et al. 2026a, 2026b, 2027, Mu et al. 2026a, Restuccia et al. 2026, Syed et al. 2026a | LLM multi-agent systems | agents can drive EPANET and code tools with high task success [S] | reliability across model sizes and where to delegate control (Wang et al. 2027) [S] | physical, safety and economic consequences of delegated decisions [I] |
| C4 Fit-for-purpose allocation and alternative sources | How much potable water can reclaimed, storm and rain water replace, and at what cost and risk? | Porse et al. 2017, 2023, Matrosov et al. 2015, Padula et al. 2013, Hsieh and Chiueh 2025, Zhong et al. 2025, Jahne et al. 2024 | network flow, MILP, QMRA, DCF | portfolios of new supplies and demand management outperform supply-only plans [S], fit-for-purpose treatment targets exist [S] | operational value of storage and timing under quality constraints at city scale [I] | value of coordinating independently operated alternative-water assets compared with departmental operation [I] |
| C5 Loss recovery | How to cut real losses economically? | Vicente et al. 2016, van Zyl and Clayton 2007, Lambert and Fantozzi 2005, Aboelnga et al. 2018, Shao et al. 2019, Vrachimis et al. 2022 | hydraulic model, DCF, metaheuristics | pressure-leakage exponents above 0.5, joint pump and PRV control beats separate control [S] | comparability across studies (Ferrarese and Malavasi 2024) and cost-benefit at moderate loss levels (Ahopelto et al. 2020) [S] | crew and robot dispatch policies tied to detection confidence and authority [I] |
| C6 Operations and the water-energy nexus | How to cut pumping energy and cost? | Menke et al. 2016, Tasseff et al. 2024, Putri et al. 2025, Wu et al. 2020 | MILP, NMPC | pump scheduling and demand response reduce cost [S] | integration with other functions [I] | energy effects of source substitution decided jointly with delivery [I] |
| C7 Demand, metering and behaviour | Do metering and feedback cut demand? | Sønderlund et al. 2016, Ferraro and Price 2013, Olmstead and Stavins 2009, Lunstad et al. 2024 | field experiment, review | feedback cuts use 2.5 to 28.6% (mean 12.15%) [S], social comparison works best for high users and fades [S] | persistence and cost-effectiveness [S] | coordinated control of distributed demand devices (Lunstad et al. 2024 future work) [S] |
| C8 Governance, safety and security | How to keep automated water systems safe and accountable? | Savić 2022, Tamuka et al. 2026, Taormina et al. 2018, Hassanzadeh et al. 2020, Alshiekh et al. 2018, Hobbs et al. 2023 | reviews, attack detection, formal shields | water-sector cyber incidents are rising [S], humans in the loop and fallback are recommended [S] | how to specify and test oversight for agentic systems [I] | measured safety and value effects of an assurance layer for water agents [I] |
| C9 Economics and evaluation | Is digital water worth it, and how to measure it? | Monks et al. 2020, Daniel et al. 2023, Gillingham et al. 2018, Brodersen et al. 2015, Hemming et al. 2015 | survey, DCF, causal inference | ex post causal evaluation designs exist [S] | business-case evidence beyond expert opinion [S] | non-additive benefits and double counting in integrated business cases [I] |

**Cross-cutting patterns in the coded corpus [S, counts from `gap_matrix_out/summary.md`].**

1. Of the 70 primary (non-review) studies, 29 address one water-cycle function and 34 address two. Seven address three or more. Six of those seven are single-planner strategic studies (Porse et al. 2017, 2023, Matrosov et al. 2015, Padula et al. 2013, Hsieh and Chiueh 2025, Zhong et al. 2025) and one is conceptual (Hosseini et al. 2026).
2. Only one primary study combines governance with allocation, loss or reuse, and it is conceptual (Hosseini et al. 2026).
3. The 11 LLM multi-agent studies report task success (9), energy or cost of computation or pumping (3), detection accuracy (1) and latency (1). None reports potable offset, real losses, pressure service, safety violations or cost-benefit.
4. Safety violations appear as a measured outcome in one primary study, and it is a generic reinforcement-learning shield (Alshiekh et al. 2018), not a water system.
5. Benchmark networks dominate operational studies (16 of 104), real-utility studies are mostly loss economics (19), and no coded agentic study ran on a real utility.

**Three gaps that follow from the map.**
- **Gap A (cells C2, C3, C4, C5):** no study quantifies what coordination across independently operated water-cycle functions adds beyond departmental operation of the same assets. Preliminary strength: Moderate to Strong, untested.
- **Gap B (cells C3, C8):** agentic water systems are evaluated on software task metrics, not on physical, safety or economic consequences. Preliminary strength: Strong, untested.
- **Gap C (cells C8, C9, C5):** human oversight is demanded but not specified as a testable autonomy envelope with measured costs and benefits. Preliminary strength: Moderate, untested.

---

## 3. Cluster syntheses

### 3.1 Digital twins for urban water (C1)

Digital twins couple a hydraulic or process model with live data to support monitoring, simulation and control. Ghorbani Bam et al. (2025) review applications across treatment, collection, distribution and reuse and describe the field as emerging, with technical challenges and knowledge gaps [S]. Ramos et al. (2022) show on a real DMA that fast leak detection plus optimal pressure-control-valve settings inside a twin can save up to 28% of water [S]. Ramos et al. (2023) apply a smart-water-grid twin to the Gaula network in Madeira and estimate a potential reduction of about 80% of real losses with an ILI of 21.15 [S]. Pesantez et al. (2022) couple AMI data with a hydraulic model to show how pandemic demand shifts changed water age, pressure and energy [S]. Ciliberti et al. (2023) argue for standardized digital water services built on twins [S].

Two recent reviews temper these results. Altındaş et al. (2026) screened 170 publications and analysed 48. Most twin-enabled water sensitive urban design studies stay at the conceptual or prototype stage, and interoperability, heterogeneous data and governance are the main obstacles [S]. Khadam et al. (2026) analyse 82 agent-based urban digital-twin studies and find low technology readiness, simulation or conceptual validation, and little explicit treatment of uncertainty [S]. Fu et al. (2022) reach a similar verdict for deep learning in urban water management and list multi-agent systems and digital twins among five open challenges [S].

**Implication for MAWRIC-X [I].** The twin should do work that a dashboard cannot: evaluate each proposed command against hard constraints before execution. That role links C1 to the governance gap.

### 3.2 Multi-agent control, decomposition and task allocation (C2)

Learning-based multi-agent control in water networks is still thin. Hu et al. (2023) apply MADDPG to joint pump and valve scheduling and report that water-loss cost dominates the schedule and that demand patterns matter more than tariffs [S]. Jia and Pei (2025) review MARL for water environment systems and stress heterogeneity, resource limits and unstable communication [S]. Kåge et al. (2025) find that reinforcement-learning agents in water management are trained mostly in simulation and call for sim-to-real transfer and explainability in this safety-critical setting [S]. Negm et al. (2024) and Javed et al. (2025) review DRL for urban water systems and leak management [S].

Model predictive control is the mature alternative. Grosso et al. (2016) compare chance-constrained, tree-based and multiple-scenario MPC on the Barcelona network [S]. Castelletti et al. (2023) review 149 MPC studies and identify four persistent problems: little benchmarking against other controllers, weak assessment of uncertainty, little analysis of forecast type and horizon, and neglect of multiple objectives [S]. Distributed MPC and decomposition split one network-wide problem among controllers (Segovia et al. 2021) [S, title and venue].

Coordination among *owners*, rather than among controllers of one owner, has a separate literature. Han et al. (2018) use a bi-level cooperative game for basin allocation and report that the cooperation willingness of agents rose from 20% to 80% at an 8% common-interest gain [S]. Doostmohammadian et al. (2025) survey distributed resource-allocation algorithms over multi-agent systems [S, title and venue]. Boyd et al. (2011) present ADMM, which solves sharing and exchange problems with local computation and coordination by prices [S]. Task allocation for robots and crews has formal taxonomies (Gerkey and Matarić 2004, Korsah et al. 2013) and a classic market protocol (Smith 1980) [S].

**Implication [I].** Price-based decomposition such as ADMM lets sector agents keep their demand data private while reaching a system optimum. No water allocation study in this search tests that property, its communication cost, or its exposure to misreporting.

### 3.3 LLM and agentic AI in water (C3)

This cluster grew fastest. Of its 16 coded papers, 13 appeared in 2025 or 2026.

- **EPANET-Agentic** (Wang et al. 2026a) nests three agents under an orchestrator, runs tasks on L-Town, C-Town and Net3, and reports a 100% task success rate with human-in-the-loop oversight for critical interventions [S].
- **LLM-driven optimization** (Wang et al. 2026b) automates calibration and pump optimization on Net2 and Anytown. The authors report that enforcing numerical constraints stated in natural language is difficult, and the agent often converged to suboptimal solutions on the looped Anytown network [S].
- **Where should control sit?** (Wang et al. 2027) delegates one pipeline node at a time to a ReAct agent over 250 runs on C-Town with five LLMs. Control allocation changed reliability and computational cost far more than solution quality (about 1% in pump energy), and full autonomy was reliable only for the largest models [S]. This is the closest prior work on the locus of control. It measures workflow reliability and token cost, not physical safety.
- **LeakAgent** (Mu et al. 2026a) unifies zoning, sensor placement and detection under an LLM coordinator and reports about 96% detection-and-partition accuracy at 20% leak magnitude on five networks of 191 to 920 nodes [S].
- **Edge agents** (Restuccia et al. 2026) run locally quantized LLMs for what-if hydraulic analysis and raise full-task success by 30 to 40% over zero-shot prompting while cutting execution failures by more than half [S].
- Further 2026 work extends agents to scheduling (Chen et al. 2026), resilience assessment (Mu et al. 2026b) and privacy-aware simulation automation (C. Wang et al. 2026, preprint) [S, title only].
- Conceptual and review work frames LLM multi-agent systems for water engineering, including negotiating agents (Hosseini et al. 2026), WaterGPT adaptation (Xu et al. 2025), LLM-based water resources management (He et al. 2025) and smart-city decision support (Kalyuzhnaya et al. 2025, Choi and Yoon 2025) [S].
- Arslan and Munawar (2026) review 34 LLM studies in sustainable water management and find most of them conceptual or observational [S]. Tamuka et al. (2026) review 25 studies on agentic AI for water SCADA security and conclude that AI should observe, detect and recommend while qualified staff keep final approval [S].

**Authors' own prior work (self-overlap check).** Syed et al. (2026a, *PLoS ONE*) propose an agentic-AI digital twin for civil infrastructure including water, with LangGraph orchestration and a permissioned blockchain, evaluated on 18,000 synthetic incidents. The agentic system cut mean detection latency from 39,374 s to 3,197 s and raised mitigation success from 45.5% to 66.2% against a rule-based baseline [S]. Syed et al. (2026b, *Sustainability*) review agentic AI for climate-resilient cities and find almost no validated cross-domain deployment [S]. MAWRIC-X must cite both and must not repeat their contributions (Section 7).

**Implication [I].** The agentic water literature asks whether agents can complete engineering tasks. It does not yet ask what happens to water, energy, service and safety when agents make or propose operational decisions, and it does not test what stops a wrong proposal.

### 3.4 Fit-for-purpose allocation and alternative water sources (C4)

Strategic portfolio studies show the value of planning supply and demand together. Padula et al. (2013) select among 316 supply schemes and 511 demand-management options for South East England with a MILP. Including demand management cut total discounted cost by 10% and removed two reservoirs from the least-cost plan [S]. Matrosov et al. (2015) show for London that many-objective search reveals portfolios that least-cost design hides [S]. Porse et al. (2017) model Los Angeles as a network-flow system. Higher stormwater capture, prioritized reuse and a regional demand target cut imports by 30%, and fragmented agencies create uneven vulnerability to shortage [S]. Porse et al. (2023) find that reuse can supply up to 30% of the region and that system energy intensity rises with reuse unless conservation accompanies it [S]. Hsieh and Chiueh (2025) reallocate surface water, groundwater, reclaimed water and transfers with a fuzzy quantity-quality model and raise supply resilience by 9.6% in Taichung [S]. Zhong et al. (2025) find that a reclaimed-water network is more cost-effective than rain tanks for urban food production in Tucson [S].

Asset-scale studies quantify what alternative sources deliver on site. Hybrid rain and greywater systems reach 42.8 to 93.6% effectiveness in service buildings, driven by the chosen end uses and storage volume (Ferreira et al. 2023) [S]. Rainwater harvesting plus greywater reuse cut campus potable use by 48% in Monterrey (López Zavala et al. 2016) [S]. Reclaimed cooling-tower makeup cut water use by 27% at a Saudi facility (Badruzzaman et al. 2022) [S]. A hospital in Abu Dhabi shows that greenhouse-gas intensity depends on source substitution and configuration more than on reuse volume (Seguela et al. 2026) [S]. Real-time control of existing stormwater ponds raised harvest yield at a unit cost close to the local potable tariff in Cape Town (Rohrer and Armitage 2017) [S]. In Johannesburg harvestable runoff is twice the non-potable requirement, and storage limits reliability (Ndeketeya and Dundu 2022) [S].

Quality and risk set the boundaries of substitution. Jahne et al. (2024) harmonize fit-for-purpose microbial treatment targets by source and end use and note the absence of US federal reuse regulation [S]. Schoen et al. (2018) find that wastewater intrusion into non-potable systems gives unacceptable infection risk without dilution or inactivation [S]. Jeffrey et al. (2026) survey dual-pipe incidents and find cross-connections, cross-contamination and misuse dominate [S]. Costs and energy of reuse are documented: levelized costs of 0.40 to 0.54 USD/m³ and 0.30 to 0.84 kWh/m³ for two treatment trains (Giammar et al. 2021) and production costs from Andalusian plants (Expósito et al. 2024) [S].

**Implication [I].** The literature answers "which portfolio should a single planner build" and "what does one building gain". It does not answer how much is lost when the same reclaimed, storm and potable assets are run by separate departments with fixed contracts and private information, and which coordination mechanism recovers that loss.

### 3.5 Loss recovery: pressure, detection, repair and robots (C5)

Physical losses are large. Liemberger and Wyatt (2019) estimate global non-revenue water at 126 billion m³ per year, worth USD 39 billion at 0.31 USD/m³ [S]. Pressure management is the most cost-effective lever. Vicente et al. (2016) review 140 sources and note that research progress has not reached practice [S]. The pressure-leakage relation is nonlinear. Field exponents exceed the orifice value of 0.5 because pipe materials deform (van Zyl and Clayton 2007), and the exponent tends to 0.5 at low pressure and 1.5 at high pressure for elastically deforming leaks (van Zyl and Cassa 2014) [S]. Joint control of pumps and pressure-reducing valves beats separate control: leakage fell 33.4%, energy 25.4% and total cost 33.1% on a small network (Shao et al. 2019), and energy savings near 50% were reported on D-Town (Brentan et al. 2018) [S]. Ferrarese and Malavasi (2024) find that 36 metaheuristic studies are hard to compare because definitions differ [S].

Economics decides how far to go. Lambert and Fantozzi (2005) compute economic intervention frequency for active leakage control from the rate of rise of unreported leakage, the marginal cost of water and the intervention cost [S]. Short-run economic leakage was 27 m³ per connection per year in Mashhad (Moslehi et al. 2020) [S]. Finnish utilities with moderate losses do not always recover the cost of leakage programs, and neither leakage percentage nor ILI suited target setting (Ahopelto and Vahala 2020) [S]. In Madaba, reported failures made up 37.2% of real losses, so response time matters (Aboelnga et al. 2018) [S].

Detection research leads in volume. BattLeDIM compared detection and isolation methods on L-Town and called for better methods and more open benchmarks (Vrachimis et al. 2022) [S]. LeakAgent reaches about 96% accuracy (Mu et al. 2026a) [S]. Repair and restoration scheduling appears mostly in post-disaster settings (Bałut et al. 2019, Assad et al. 2020, with a 48% duration reduction under crew limits) [S]. Robots are maturing: an MFL in-pipe robot for 900 to 1200 mm mains passed a 1 km field test bed (Jeon et al. 2024) [S], and SLAM for pipe robots remains the bottleneck for long autonomous missions (Aitken et al. 2021) [S]. Value-of-information inspection scheduling exists for infrastructure in general (Memarzadeh and Pozzi 2016) [S].

**Implication [I].** Detection accuracy is well studied. The decision that follows detection gets less attention: whether to verify, isolate, reduce pressure or repair, under crew limits and authority rules.

### 3.6 Operations and the water-energy nexus (C6)

Pump scheduling cuts energy cost and can provide grid demand response (Menke et al. 2016) [S]. Tight polyhedral relaxations improve optimal pump scheduling bounds (Tasseff et al. 2024) [S]. Data-driven nonlinear MPC with stability guarantees cut operating cost by 8% in simulation (Putri et al. 2025) [S]. Wu et al. (2020) review responses to the changing water-energy nexus in urban supply and list integrated modelling and planning among them [S]. In Saudi Arabia, water and energy have long been managed as separate silos despite their interdependence (Rambo et al. 2017) [S]. Energy intensities across the water cycle are compiled by Plappally and Lienhard (2012) and Lee et al. (2017) [S, title and venue].

### 3.7 Demand, metering and behaviour (C7)

Smart-meter feedback cut household water use by 2.5 to 28.6% (mean 12.15%) across 21 studies, but costs to utilities are under-studied (Sønderlund et al. 2016) [S]. In a field experiment with more than 100,000 households, social-comparison messages outperformed other messages, worked best for high users and faded over time (Ferraro and Price 2013) [S]. Prices conserve water more cost-effectively than nonprice programs (Olmstead and Stavins 2009) [S]. Smart irrigation controllers cut demand by about 15% for typical users and more than 40% for heavy users, and coordinating networks of controllers is open work (Lunstad et al. 2024) [S]. Sector benchmarks exist for hospitals (103 m³ per bed per year, González et al. 2018) and data centres, which in some cases draw 57% of cooling water from potable supply (Mytton 2021) [S].

### 3.8 Governance, safety and security (C8)

Water-sector cyber incidents are rising in frequency, diversity and complexity (Hassanzadeh et al. 2020) [S]. BATADAL compared seven attack-detection approaches on C-Town (Taormina et al. 2018) [S]. Savić (2022) draws lessons from the Boeing 737 MAX and self-driving cars: automation needs humans in the loop, trained operators, manual fallback, redundant sensors, cybersecurity and ethics [S]. Tamuka et al. (2026) propose that agentic AI observe and recommend while humans approve [S]. Doorn (2021) argues that responsible AI in water needs plural values and participation [S]. AI adoption stalls in practice because of skills, data governance and unclear impact measures (Almheiri et al. 2024 in the UAE, Okwori et al. 2026 in Sweden) [S].

Methods for enforcing safety exist outside water. A shield monitors a learner's actions and corrects only those that would violate a temporal-logic specification (Alshiekh et al. 2018) [S]. Runtime assurance switches from a complex controller to a verified fallback when a safety envelope is threatened (Hobbs et al. 2023) [S]. Levels-of-automation models (Parasuraman et al. 2000) and trust calibration (Lee and See 2004) frame how much authority to delegate [B].

**Practice and policy requirements (M11).**

| Requirement | Primary source | Research evidence status | Translation gap |
|---|---|---|---|
| AI systems used as safety components in the management and operation of the supply of water are high-risk | Regulation (EU) 2024/1689, Annex III point 2 [S, read via the AI Act Explorer mirror] | water agent studies rarely state a risk class or test safety components | no tested design for an agentic water system that meets high-risk obligations |
| High-risk AI must be effectively overseeable, with the ability to override and to stop the system in a safe state | Regulation (EU) 2024/1689, Article 14(1) and 14(4)(d)-(e) [S] | EPANET-Agentic keeps a human in the loop [S], reviews recommend human approval [S] | no measurement of what oversight costs (delay, workload) or prevents (unsafe actions) |
| Member States must assess leakage levels of large suppliers with the ILI or another method | Directive (EU) 2020/2184, Article 4(3) [S, via secondary sources quoting the provision] | ELL and pressure-management economics are mature [S] | leakage programs are evaluated in isolation, not jointly with other interventions |
| Minimum requirements for reclaimed water apply from 26 June 2023 for agricultural irrigation | Regulation (EU) 2020/741 [S, via EUR-Lex summary and national agency pages] | urban non-potable reuse governed by national rules, fit-for-purpose targets exist [S] | operational allocation that respects quality classes and cross-connection controls is rarely modelled |
| Govern, map, measure and manage AI risk | NIST AI RMF 1.0 [S] | generic | no water-specific measurement of agent risk [I] |

*Not legal advice. Article and annex numbers were checked against a mirror of the official text, because EUR-Lex blocked automated access during this session. Recheck against EUR-Lex before submission.*

### 3.9 Economics and evaluation (C9)

Business cases for digital water still lean on expert judgement. Monks et al. (2020) elicit expert distributions for digital-metering benefits and find 82% support with value ranges rather than measured savings [S]. Daniel et al. (2023) survey utilities on digital transformation drivers and impacts [S, title and venue]. Leakage economics are mature (Section 3.5). Ex post evaluation designs that can verify claimed savings exist: Bayesian structural time series (Brodersen et al. 2015) and stepped-wedge trials (Hemming et al. 2015) [S]. Variance-based sensitivity analysis is standard for exposing which assumptions drive a model (Saltelli et al. 2010, Pianosi et al. 2016, Herman and Usher 2017) [S].

---

## 4. Recurring recommendations (M3)

Recurrence threshold: at least 3 papers, 2 independent first-author groups, 2 distinct years. Tags were coded from abstracts.

| Repeated recommendation | Recurrence (papers / groups / years) | What was attempted [S] | What is still missing [I] | Research question it supports |
|---|---|---|---|---|
| Field or real-world validation | 6 / 6 / 3 (2022 to 2026) | pilots in single DMAs and buildings | city-scale operation of coordinated agents | outside the scope of a simulation paper, stated as a limitation with a field protocol |
| Integration across functions | 4 / 4 / 4 (2020 to 2026) | strategic portfolios with one planner | operational coordination among separate owners | RQ1, RQ2 |
| Benchmarking and comparability | 4 / 4 / 3 (2023 to 2026) | BattLeDIM, BATADAL | open benchmark for coordinated city operation | released code and data |
| Governance | 3 / 3 / 3 (2017 to 2026) | conceptual frameworks | tested oversight design | RQ3 |
| Human-in-the-loop | 3 / 3 / 2 (2021 to 2026) | approval gates in agent platforms | cost and benefit of approval | RQ3 |
| Cost-benefit evidence | 3 / 3 / 3 (2013 to 2017) | expert valuation, leakage CBA | integrated, non-double-counted business case | RQ4 |

Limitations recur in the same direction: field validation (9 papers, 8 groups), data availability (4), benchmarking (4), governance (3) and cost-benefit (3).

---

## 5. Methodology gap (M4)

| Dominant method | Share of coded corpus | Answers well | Cannot answer |
|---|---|---|---|
| Review | 30% | where the field stands | any causal or quantitative claim about coordination |
| Hydraulic model on one DMA or benchmark | 12% | pressure and leakage response | interactions with allocation, demand and governance |
| LLM multi-agent demonstration | 11% | whether agents complete tasks | water, safety and economic consequences |
| CBA or DCF of one intervention | 11% | whether one program pays | non-additive value of combined programs |
| LP or MILP portfolio | 7% | best strategic portfolio for one planner | loss from departmental operation, private information |

**Three methodology gaps.**
1. *Counterfactual coordination experiments.* Studies compare an optimized system with a baseline but not with a fair siloed counterfactual that holds assets constant and changes only decision rights and information. A factorial design over coordination mechanisms, with Shapley attribution, can isolate which mechanism produces value [I].
2. *Consequence-based evaluation of agents.* Agent studies count completed tasks. Fault injection against a hydraulic twin, with ground truth computed on the true system state, measures what proportion of unsafe proposals reach the physical system [I].
3. *Decomposition as an agent protocol.* Distributed optimization is used for computation (Segovia et al. 2021) but not tested as a negotiation protocol among owners with private data and incentives to misreport [I].

---

## 6. Assumption gaps (M12)

| Assumption | Where it appears [S] | Why it is questionable | Alternative assumption | Research question |
|---|---|---|---|---|
| Benefits of separate programs add up | business cases built from single-program savings (Monks et al. 2020, Ahopelto and Vahala 2020) | shared resources and storage create interactions, and gains can be super- or sub-additive [I] | the value of integration must be computed jointly | RQ1, RQ4 |
| More autonomy yields more value | agentic platforms that aim at end-to-end automation (Wang et al. 2026a, Restuccia et al. 2026) | delegating control changes reliability and cost more than quality (Wang et al. 2027) [S] | autonomy should be granted per action class after evidence | RQ3 |
| The language model is the controller | agents that write and run optimization code (Wang et al. 2026b) | natural-language constraint enforcement is hard [S] | numerical optimizers and deterministic rules decide, language models interface | design principle, tested in RQ3 |

---

## 7. Triangulation, scoring and stress tests (M9)

**Triangulation.**

| Candidate gap | M1 map | M3 recurrence | M4 method | M11 policy | M12 assumption | Lenses |
|---|---|---|---|---|---|---|
| A. Value of coordination across independently operated functions | yes | yes (integration) | yes | partial (DWD leakage, reuse rules) | yes (additivity) | 4 to 5 |
| B. Consequence-based evaluation of agentic water decisions | yes | yes (field validation, benchmarking) | yes | yes (AI Act) | yes (autonomy) | 5 |
| C. Testable oversight envelope with measured costs | yes | yes (governance, human-in-the-loop) | partial | yes (Art. 14) | yes | 4 |
| D. Privacy-preserving negotiation among owners | partial | no | yes | no | partial | 2 |
| E. Integrated, non-double-counted business case | partial | yes (cost-benefit) | yes | no | yes | 3 |

**Scores (rubric 0 to 3 per dimension).**

| Gap | E | T | P | N | C | R | Total | Gates | Kill criteria | Class |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 2 | 2 | 3 | 2 | 3 | 2 | 14 | pass | none found | Strong |
| B | 2 | 2 | 3 | 3 | 3 | 2 | 15 | pass | none found | Strong |
| C | 2 | 2 | 3 | 2 | 3 | 2 | 14 | pass | none found | Strong |
| D | 2 | 2 | 2 | 2 | 1 | 2 | 11 | pass | none found | Moderate |
| E | 2 | 1 | 2 | 1 | 2 | 1 | 9 | fails N | none | Weak |

E = 2 rather than 3 because Scopus and Web of Science were not searched and no full texts were read. Evidence confidence: **Medium**.

**Stress test of the combined central gap (A + B + C).**

| Attack | Searches run | Finding | Effect |
|---|---|---|---|
| Prior work | "integrated versus siloed urban water management value of coordination", "joint optimization water reuse leakage reduction demand management portfolio", "multi-agent architecture integrated urban water cycle management" | strategic portfolio models with one planner (Padula et al. 2013, Matrosov et al. 2015, Porse et al. 2017) | narrows the claim to operational coordination among separate owners |
| Synonyms | "hybrid water supply", "integrated urban water management", "water sensitive urban design", "one water" | reviews list integration and interaction effects as open (Sapkota et al. 2015, Mosleh et al. 2021, Altındaş et al. 2026) | supports the gap |
| Superficial novelty | | the claim rests on mechanisms (pooling, cross-source substitution, forecast-based storage) with an expected non-uniform effect | passes |
| Already connected | "multi-agent water allocation game", "distributed resource allocation" | basin game theory (Han et al. 2018), generic surveys (Doostmohammadian et al. 2025) | supports D as a component, not a closed gap |
| Theoretical "so what" | | any premium size is informative: a small premium says coordination platforms must be justified by safety or service, a large one locates where integration pays | passes |
| Practical "so what" | | utilities face AI Act oversight duties and leakage assessment duties | passes |
| Recency | 6 recency queries for 2025 to 2026 | 9 agentic water papers, all single-function and software-metric based | passes with differentiation |
| Answerability | | simulation with public weather data, a public benchmark network and open solvers is feasible now, field trials are not | scope limited to simulation, field protocol given |
| Self-overlap | portfolio site, Crossref | Syed et al. 2026a (PLoS ONE), Syed et al. 2026b (Sustainability), the authors' MAWRIC manuscript retargeted to *Polymers* (coverage-aware break-even for membrane reuse), and the AquaAgent and AquaGuard leak and pressure papers | MAWRIC-X must cite the published ones, avoid L-Town leak detection, avoid coverage-aware break-even propositions, and declare related manuscripts in the cover letter |

**Verdict: Strong. Evidence confidence: Medium. Feasibility: Go for a simulation study, Conditional for field validation.**

**Closest prior work and how MAWRIC-X differs.**

| Closest work | What it does | What MAWRIC-X adds |
|---|---|---|
| Wang et al. 2027, *Where should control sit?* | varies the locus of LLM control in an optimization pipeline, measures reliability and token cost | varies decision rights over physical actions, measures unsafe executions, rejected value, water lost and service impact |
| Wang et al. 2026a, EPANET-Agentic | natural-language control of simulations with human oversight | operational allocation and loss-response decisions screened by a deterministic assurance layer |
| Porse et al. 2017 and Padula et al. 2013 | single-planner portfolio optimization | siloed versus coordinated operation of fixed assets, with mechanism attribution |
| Syed et al. 2026a (authors) | agentic DT for civil infrastructure with blockchain audit, latency and mitigation metrics | water-specific allocation, loss recovery and oversight, with water, energy, safety and economic outcomes |
| Han et al. 2018 | cooperative game for basin allocation | negotiation among urban owners with private data, with optimality gap and misreporting tests |

---

## 8. The defensible gap and the research design (M10)

**Synthesis matrix.**

| Dimension | Evidence |
|---|---|
| Established | joint control of pumps and valves beats separate control (Shao et al. 2019, Brentan et al. 2018), portfolios beat supply-only plans (Padula et al. 2013, Matrosov et al. 2015), LLM agents can run hydraulic workflows (Wang et al. 2026a, Restuccia et al. 2026) |
| Disputed | whether autonomy improves outcomes or only shifts reliability and cost (Wang et al. 2027), whether leakage programs pay at moderate loss levels (Ahopelto and Vahala 2020) |
| Understudied | operational coordination among separate owners, physical consequences of agent decisions, oversight costs |
| Methodological limits | single-function testbeds, task-success metrics, no fair siloed counterfactual, no fault injection |
| Theoretical failures | additivity of program benefits, autonomy as a monotone good |

**Gap statement.** Studies of agentic and multi-agent AI for urban water evaluate whether agents complete engineering tasks, and integrated water planning studies optimize portfolios for a single planner. Neither line of work measures what coordinated operation of independently owned water-cycle functions adds beyond departmental operation of the same assets, and neither tests whether a governance layer can stop unsafe agent decisions, or at what cost in lost value and delay. This matters because utilities must both justify integration investments and meet emerging obligations for human oversight of AI in water supply.

**Research questions.**
- **RQ1.** How much potable water, energy and cost does coordinated fit-for-purpose allocation of reclaimed water and captured stormwater save beyond siloed departmental operation of the same assets, and which mechanism (pooling across users, cross-source integration, forecast-based storage) produces the premium?
- **RQ2.** Can sector agents that keep their demand data private reach the centralized optimum through price-based negotiation, at what communication cost, and how far can one misreporting agent shift the outcome?
- **RQ3.** Does a deterministic assurance layer stop unsafe agent proposals on a hydraulic network, how much beneficial action does it reject, and how does human approval latency change losses and service under different autonomy levels?
- **RQ4.** Under declared uncertainty, what is the economic value of the coordination layer and which parameters drive it?

**Hypotheses.**
- H1. The coordination premium is positive in every climate, and it is largest when alternative supply is comparable to eligible non-potable demand. Reason: when supply is abundant every policy meets the eligible demand, and when it is scarce every policy uses all of it.
- H2. Price-based negotiation reaches the centralized optimum within a small tolerance, while an unchecked misreporting agent gains at others' expense. Caps based on metered history bound the gain.
- H3. Without assurance, faulty or adversarial proposals reach the network. With rule checks plus a twin check, checkable violations do not, at a modest rejection rate of safe proposals. Approval latency raises losses for loss-response actions, and bounded autonomy for low-risk actions recovers most of that loss.
- H4. The sign of net present value depends mainly on the marginal value of potable water and the size of the coordination premium.

**Method fit.** A simulation study is the only feasible way to hold assets constant while changing decision rights, to inject faults with known ground truth, and to run thousands of weather-years. Real inputs anchor it: NOAA GHCN-Daily weather for climatically different cities (Menne et al. 2012), Hargreaves reference evapotranspiration (Hargreaves and Samani 1985), a public benchmark network simulated in EPANET through WNTR (Klise et al. 2017, Marchi et al. 2014), and published cost, energy and pressure-leakage relations (Giammar et al. 2021, Plappally and Lienhard 2012, van Zyl and Cassa 2014).

**Scope boundaries.** The study does not claim field performance, does not build a new leak detector, and does not evaluate LLM language quality. Language models are treated as interfaces whose proposals the assurance layer screens.

**Falsification.** The gap would close if a study were found that compares siloed and coordinated operation of the same alternative-water assets, or that measures unsafe executions of agent decisions on a water network under fault injection.

**Feasibility.** Go: public data, open-source solvers and a laptop-scale compute budget.

**Runner-up gaps.** D (negotiation among owners) is folded into RQ2 because it is the agent mechanism of the central gap. E (integrated business case) became RQ4, because on its own it is a weak gap.

**LaTeX-ready gap paragraph.**

```latex
\textbf{Research gap.} Agentic and multi-agent studies of urban water now drive hydraulic
simulators, optimize pumps and locate leaks with high task success
\cite{wang2026agentic,wang2026llm,mu2026leak,restuccia2026}, and integrated planning studies
optimize supply and demand portfolios for a single planner \cite{padula2013,matrosov2015,porse2017}.
Neither line of work measures what coordinated operation of independently owned water-cycle
functions adds beyond departmental operation of the same assets, and neither tests whether a
governance layer stops unsafe agent decisions, or what that protection costs
\cite{wang2027control,tamuka2026,savic2022}. Recent reviews still list integration, governance and
field validation as open problems \cite{altindas2026,khadam2026,arslan2026}. This study addresses
the gap with a counterfactual simulation design that holds assets constant while changing
decision rights, information and oversight.
```

---

## 9. How each gap is used in the MAWRIC-X manuscript

| Gap | Manuscript section | Experiment | Key citations |
|---|---|---|---|
| A. Coordination premium | Introduction, Section 2, Results 4.1 | E1: siloed versus coordinated allocation over real weather-years in three climates, factorial mechanism attribution | Porse et al. 2017, 2023, Padula et al. 2013, Matrosov et al. 2015, Hsieh and Chiueh 2025, Sapkota et al. 2015, Mosleh et al. 2021 |
| D. Negotiation among owners | Methods 3.4, Results 4.2 | E2: ADMM negotiation against the centralized optimum, misreporting test | Boyd et al. 2011, Doostmohammadian et al. 2025, Han et al. 2018, Hosseini et al. 2026 |
| B and C. Consequence-based governance | Methods 3.5, Results 4.3 | E3: fault-injected proposals on a benchmark network, autonomy levels with approval latency | Wang et al. 2026a, 2026b, Tamuka et al. 2026, Savić 2022, Alshiekh et al. 2018, Hobbs et al. 2023, Regulation (EU) 2024/1689 |
| E. Business case | Results 4.4, Discussion | E4: Monte Carlo NPV with Sobol indices, no double counting | Monks et al. 2020, Ahopelto and Vahala 2020, Saltelli et al. 2010, Herman and Usher 2017 |

**Corrections to the original manuscript found during verification.**
1. The original `exposito2021` entry pointed to DOI 10.3390/w13060846, which belongs to an unrelated article on microbial action in wastewater. The reclaimed-water cost study it meant is Expósito, Lorenzo López and Berbel (2024), *Water Reuse* 14(3), 434 to 447, DOI 10.2166/wrd.2024.040.
2. The original `boyle2013` entry gave the first author as "Tracy" Boyle. The publisher record gives Thomas Boyle.
3. The original `bam2025` entry gave the first author as "Parastoo" Ghorbani Bam. The publisher record gives Pooria Ghorbani Bam.
4. The original `smith1980` entry was typed `@inproceedings` with a journal field, which made BibTeX warn about an empty booktitle. It is a journal article in *IEEE Transactions on Computers*.

---

## 10. Limitations of this analysis

This analysis searched the OpenAlex API (99 queries) and the Crossref API (21 queries) on 16 October 2026, plus 7 web lookups (EU AI Act Annex III and Article 14 via the AI Act Explorer mirror, the Drinking Water Directive leakage provision, the Water Reuse Regulation scope, the Expósito et al. correction, and the authors' portfolio page). The OpenAlex free budget ran out mid-session, which cut the number of results available for the last searches. Scopus, Web of Science, IEEE Xplore and Google Scholar were not searched. Only English-language records were screened. No full texts were read, so every finding is "per abstract", and 48 of the 172 sources had no abstract in the open indexes and are used only for what their title and venue establish. One analyst (Claude) coded the 104-paper extraction sheet with no inter-rater check. Statements that a topic is understudied describe this search, not the whole literature. Tags [I] mark the analyst's inferences, which the authors should verify. Regulatory text was read from a mirror and secondary sources because EUR-Lex refused automated access, so article numbers should be checked against the official text before submission.

---

## Appendix A. Verified source ledger (172 sources, grouped by cluster)

Every entry resolved at doi.org on 16 October 2026 and has publisher BibTeX in `references_lit.bib` under the key shown.
