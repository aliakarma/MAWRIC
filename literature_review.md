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

### C1. Urban water digital twins and hydroinformatics (9)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `eggimann2017` | Eggimann et al. | 2017 | The Potential of Knowing More: A Review of Data-Driven Urban Water Management | Environmental Science & Technology | [10.1021/acs.est.6b04267](https://doi.org/10.1021/acs.est.6b04267) |
| `makropoulos2019` | Makropoulos and Savić | 2019 | Urban Hydroinformatics: Past, Present and Future | Water | [10.3390/w11101959](https://doi.org/10.3390/w11101959) |
| `fu2022` | Fu et al. | 2022 | The role of deep learning in urban water management: A critical review | Water Research | [10.1016/j.watres.2022.118973](https://doi.org/10.1016/j.watres.2022.118973) |
| `pesantez2022` | Pesantez et al. | 2022 | Using a digital twin to explore water infrastructure impacts during the COVID-19 pandemic | Sustainable Cities and Society | [10.1016/j.scs.2021.103520](https://doi.org/10.1016/j.scs.2021.103520) |
| `ramos2022` | Ramos et al. | 2022 | New Challenges towards Smart Systems’ Efficiency by Digital Twin in Water Distribution Networks | Water | [10.3390/w14081304](https://doi.org/10.3390/w14081304) |
| `ciliberti2023` | Gino Ciliberti et al. | 2023 | From digital twin paradigm to digital water services | Journal of Hydroinformatics | [10.2166/hydro.2023.237](https://doi.org/10.2166/hydro.2023.237) |
| `ramos2023` | Ramos et al. | 2023 | Smart Water Grids and Digital Twin for the Management of System Efficiency in Water Distribution Networks | Water | [10.3390/w15061129](https://doi.org/10.3390/w15061129) |
| `bam2025` | Ghorbani Bam et al. | 2025 | Digital Twin Applications in the Water Sector: A Review | Water | [10.3390/w17202957](https://doi.org/10.3390/w17202957) |
| `altindas2026` | Altındaş et al. | 2026 | Urban digital twins and water sensitive urban design: A systematic literature review | Sustainable Cities and Society | [10.1016/j.scs.2026.107456](https://doi.org/10.1016/j.scs.2026.107456) |

### C2. Multi-agent control, decomposition and task allocation (19)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `smith1980` | Smith | 1980 | The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver | IEEE Transactions on Computers | [10.1109/tc.1980.1675516](https://doi.org/10.1109/tc.1980.1675516) |
| `gerkey2004` | Gerkey and Matarić | 2004 | A Formal Analysis and Taxonomy of Task Allocation in Multi-Robot Systems | The International Journal of Robotics Research | [10.1177/0278364904045564](https://doi.org/10.1177/0278364904045564) |
| `boyd2011` | Boyd et al. | 2011 | Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers | Foundations and Trends® in Machine Learning | [10.1561/2200000016](https://doi.org/10.1561/2200000016) |
| `korsah2013` | Korsah et al. | 2013 | A comprehensive taxonomy for multi-robot task allocation | The International Journal of Robotics Research | [10.1177/0278364913496484](https://doi.org/10.1177/0278364913496484) |
| `pascual2013` | Pascual et al. | 2013 | Operational predictive optimal control of Barcelona water transport network | Control Engineering Practice | [10.1016/j.conengprac.2013.01.009](https://doi.org/10.1016/j.conengprac.2013.01.009) |
| `grosso2016` | Grosso et al. | 2016 | Stochastic model predictive control approaches applied to drinking water networks: Stochastic model predictive control approaches applied to drinking water networks | Optimal Control Applications and Methods | [10.1002/oca.2269](https://doi.org/10.1002/oca.2269) |
| `han2018` | Han et al. | 2018 | Water Resource Optimal Allocation Based on Multi-Agent Game Theory of HanJiang River Basin | Water | [10.3390/w10091184](https://doi.org/10.3390/w10091184) |
| `radulescu2019` | Rădulescu et al. | 2019 | Multi-objective multi-agent decision making: a utility-based analysis and survey | Autonomous Agents and Multi-Agent Systems | [10.1007/s10458-019-09433-x](https://doi.org/10.1007/s10458-019-09433-x) |
| `aydin2021` | Aydin and Keleş | 2021 | A multi agent-based approach for energy efficient water resource management | Computers & Industrial Engineering | [10.1016/j.cie.2020.106679](https://doi.org/10.1016/j.cie.2020.106679) |
| `segovia2021` | Segovia et al. | 2021 | Distributed model predictive control using optimality condition decomposition and community detection | Journal of Process Control | [10.1016/j.jprocont.2021.01.007](https://doi.org/10.1016/j.jprocont.2021.01.007) |
| `castelletti2023` | Castelletti et al. | 2023 | Model Predictive Control of water resources systems: A review and research agenda | Annual Reviews in Control | [10.1016/j.arcontrol.2023.03.013](https://doi.org/10.1016/j.arcontrol.2023.03.013) |
| `hu2023` | Hu et al. | 2023 | Multi-agent reinforcement learning framework for real-time scheduling of pump and valve in water distribution networks | Water Supply | [10.2166/ws.2023.163](https://doi.org/10.2166/ws.2023.163) |
| `negm2024` | Negm et al. | 2024 | Deep reinforcement learning challenges and opportunities for urban water systems | Water Research | [10.1016/j.watres.2024.121145](https://doi.org/10.1016/j.watres.2024.121145) |
| `agyeman2025` | Agyeman et al. | 2025 | A semi-centralized multi-agent RL framework for efficient irrigation scheduling | Control Engineering Practice | [10.1016/j.conengprac.2024.106183](https://doi.org/10.1016/j.conengprac.2024.106183) |
| `doostmohammadian2025` | Doostmohammadian et al. | 2025 | Survey of distributed algorithms for resource allocation over multi-agent systems | Annual Reviews in Control | [10.1016/j.arcontrol.2024.100983](https://doi.org/10.1016/j.arcontrol.2024.100983) |
| `javed2025` | Javed et al. | 2025 | Leak Management in Water Distribution Networks Through Deep Reinforcement Learning: A Review | Water | [10.3390/w17131928](https://doi.org/10.3390/w17131928) |
| `jia2025` | Jia and Pei | 2025 | Recent Advances in Multi-Agent Reinforcement Learning for Intelligent Automation and Control of Water Environment Systems | Machines | [10.3390/machines13060503](https://doi.org/10.3390/machines13060503) |
| `kage2025` | Kåge et al. | 2025 | Reinforcement learning applications in water resource management: a systematic literature review | Frontiers in Water | [10.3389/frwa.2025.1537868](https://doi.org/10.3389/frwa.2025.1537868) |
| `amarnath2026` | Amarnath | 2026 | Robust Control of Water Distribution Networks Under Drought Stress: A Multi-Agent Curriculum Learning Approach | Water Resources Management | [10.1007/s11269-026-04592-5](https://doi.org/10.1007/s11269-026-04592-5) |

### C3. LLM and agentic AI in water and smart cities (21)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `alevizos2025` | Alevizos et al. | 2025 | Multi-Agentic Water Health Surveillance | Water | [10.3390/w17172653](https://doi.org/10.3390/w17172653) |
| `bandi2025` | Bandi et al. | 2025 | The Rise of Agentic AI: A Review of Definitions, Frameworks, Architectures, Applications, Evaluation Metrics, and Challenges | Future Internet | [10.3390/fi17090404](https://doi.org/10.3390/fi17090404) |
| `choi2025` | Choi and Yoon | 2025 | AI Agent-Based Intelligent Urban Digital Twin (I-UDT): Concept, Methodology, and Case Studies | Smart Cities | [10.3390/smartcities8010028](https://doi.org/10.3390/smartcities8010028) |
| `he2025iwms` | He et al. | 2025 | IWMS-LLM: an intelligent water resources management system based on large language models | Journal of Hydroinformatics | [10.2166/hydro.2025.130](https://doi.org/10.2166/hydro.2025.130) |
| `kalyuzhnaya2025` | Kalyuzhnaya et al. | 2025 | LLM Agents for Smart City Management: Enhancing Decision Support Through Multi-Agent AI Systems | Smart Cities | [10.3390/smartcities8010019](https://doi.org/10.3390/smartcities8010019) |
| `li2025urban` | Li et al. | 2025 | Urban Computing in the Era of Large Language Models | ACM Transactions on Intelligent Systems and Technology | [10.1145/3768163](https://doi.org/10.1145/3768163) |
| `xu2025` | Xu et al. | 2025 | Towards domain-adapted large language models for water and wastewater management: methods, datasets and benchmarking | npj Clean Water | [10.1038/s41545-025-00509-8](https://doi.org/10.1038/s41545-025-00509-8) |
| `arslan2026` | Arslan and Munawar | 2026 | Large language models for sustainable water management: A review | Sustainable Cities and Society: Advances | [10.1016/j.scsadv.2026.100044](https://doi.org/10.1016/j.scsadv.2026.100044) |
| `chen2026sched` | Chen et al. | 2026 | Towards autonomous scheduling agents for water distribution networks: Self-evolving data-centric AI via continuous data-model coevolution | Water Research | [10.1016/j.watres.2026.126284](https://doi.org/10.1016/j.watres.2026.126284) |
| `hosseini2026` | Hosseini et al. | 2026 | Making waves: A conceptual framework exploring how large language model-based multi-agent systems could reshape water engineering | Water Research | [10.1016/j.watres.2025.125157](https://doi.org/10.1016/j.watres.2025.125157) |
| `khadam2026` | Khadam et al. | 2026 | AI-Driven Agent-Based Urban Digital Twins: A Systematic Literature Review | IEEE Access | [10.1109/access.2026.3738118](https://doi.org/10.1109/access.2026.3738118) |
| `mu2026leak` | Mu et al. | 2026 | LeakAgent: a multi-agent system for leak detection using multi-modal large language model coordination in water distribution network | Communications AI & Computing | [10.1038/s44488-026-00024-w](https://doi.org/10.1038/s44488-026-00024-w) |
| `mu2026wds` | Mu et al. | 2026 | WDS-Modality: A Physics-Informed Multi-Modal Agent Framework for Resilient Water Distribution System Assessment Using Large Language Models without Fine-tuning | Water Research | [10.1016/j.watres.2026.126384](https://doi.org/10.1016/j.watres.2026.126384) |
| `restuccia2026` | Restuccia et al. | 2026 | From Digital Twins to Autonomous Local Agents: Rethinking AI for Smart Water Networks | IEEE Internet of Things Journal | [10.1109/jiot.2026.3700039](https://doi.org/10.1109/jiot.2026.3700039) |
| `syed2026agentic` | Syed et al. | 2026 | Agentic AI-enhanced digital twins for Smart City civil infrastructure: A secure, autonomous and auditable management framework | PLOS One | [10.1371/journal.pone.0353610](https://doi.org/10.1371/journal.pone.0353610) |
| `syed2026climate` | Syed et al. | 2026 | Agentic AI for Climate-Resilient Cities: A PRISMA-Guided Review and Digital Twin Framework | Sustainability | [10.3390/su18178917](https://doi.org/10.3390/su18178917) |
| `tamuka2026` | Tamuka et al. | 2026 | A scoping review of human-governed agentic AI for SCADA cybersecurity in water and wastewater treatment systems | Discover Computing | [10.1007/s10791-026-10697-7](https://doi.org/10.1007/s10791-026-10697-7) |
| `wang2026agentic` | Wang et al. | 2026 | EPANET-Agentic: A multi-agent system for natural language-controlled simulations of water distribution networks | Water Research | [10.1016/j.watres.2026.125433](https://doi.org/10.1016/j.watres.2026.125433) |
| `wang2026light` | Wang et al. | 2026 | LightWDN-Agent: A Quality-Gated Multi-Agent Framework for Privacy-Aware Automation of Water Distribution Network Simulations | Elsevier BV | [10.2139/ssrn.7157742](https://doi.org/10.2139/ssrn.7157742) |
| `wang2026llm` | Wang et al. | 2026 | Leveraging large language models for automating water distribution network optimization | Water Research | [10.1016/j.watres.2025.124536](https://doi.org/10.1016/j.watres.2025.124536) |
| `wang2027control` | Wang et al. | 2027 | Where should control sit? Reliability-cost trade-offs in delegating water distribution network optimisation to LLM agents | Water Research | [10.1016/j.watres.2026.126823](https://doi.org/10.1016/j.watres.2026.126823) |

### C4. Fit-for-purpose allocation, alternative sources and reuse (35)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `davis2009` | Davis et al. | 2009 | Landscape irrigation by evapotranspiration-based irrigation controllers under dry conditions in Southwest Florida | Agricultural Water Management | [10.1016/j.agwat.2009.08.005](https://doi.org/10.1016/j.agwat.2009.08.005) |
| `padula2013` | Padula et al. | 2013 | Least Economic Cost Regional Water Supply Planning: Optimising Infrastructure Investments and Demand Management for South East England’s 17.6 Million People | Water Resources Management | [10.1007/s11269-013-0437-6](https://doi.org/10.1007/s11269-013-0437-6) |
| `sapkota2015` | Sapkota et al. | 2014 | An Overview of Hybrid Water Supply Systems in the Context of Urban Water Management: Challenges and Opportunities | Water | [10.3390/w7010153](https://doi.org/10.3390/w7010153) |
| `matrosov2015` | Matrosov et al. | 2015 | Many-objective optimization and visual analytics reveal key trade-offs for London’s water supply | Journal of Hydrology | [10.1016/j.jhydrol.2015.11.003](https://doi.org/10.1016/j.jhydrol.2015.11.003) |
| `lopezzavala2016` | López Zavala et al. | 2016 | Potential of Rainwater Harvesting and Greywater Reuse for Water Consumption Reduction and Wastewater Minimization | Water | [10.3390/w8060264](https://doi.org/10.3390/w8060264) |
| `wilcox2016` | Wilcox et al. | 2016 | Urban water reuse: A triple bottom line assessment framework and review | Sustainable Cities and Society | [10.1016/j.scs.2016.06.021](https://doi.org/10.1016/j.scs.2016.06.021) |
| `porse2017` | Porse et al. | 2017 | Systems Analysis and Optimization of Local Water Supplies in Los Angeles | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0000803](https://doi.org/10.1061/(asce)wr.1943-5452.0000803) |
| `rohrer2017` | Rohrer and Armitage | 2017 | Improving the Viability of Stormwater Harvesting through Rudimentary Real Time Control | Water | [10.3390/w9060371](https://doi.org/10.3390/w9060371) |
| `kisakye2018` | Kisakye and Van der Bruggen | 2018 | Effects of climate change on water savings and water security from rainwater harvesting systems | Resources, Conservation and Recycling | [10.1016/j.resconrec.2018.07.009](https://doi.org/10.1016/j.resconrec.2018.07.009) |
| `schoen2018` | Schoen et al. | 2018 | Human Health Impact of Cross-Connections in Non-Potable Reuse Systems | Water | [10.3390/w10101352](https://doi.org/10.3390/w10101352) |
| `paul2019` | Paul et al. | 2019 | How scale and technology influence the energy intensity of water recycling systems-An analytical review | Journal of Cleaner Production | [10.1016/j.jclepro.2018.12.148](https://doi.org/10.1016/j.jclepro.2018.12.148) |
| `radcliffe2020` | Radcliffe and Page | 2020 | Water reuse and recycling in Australia, history, current situation and future perspectives | Water Cycle | [10.1016/j.watcyc.2020.05.005](https://doi.org/10.1016/j.watcyc.2020.05.005) |
| `zhang2020storm` | Zhang et al. | 2020 | Quantifying the benefits of stormwater harvesting for pollution mitigation | Water Research | [10.1016/j.watres.2019.115395](https://doi.org/10.1016/j.watres.2019.115395) |
| `giammar2021` | Giammar et al. | 2021 | Cost and Energy Metrics for Municipal Water Reuse | ACS ES&T Engineering | [10.1021/acsestengg.1c00351](https://doi.org/10.1021/acsestengg.1c00351) |
| `mosleh2021` | Mosleh and Negahban-Azar | 2021 | Role of Models in the Decision-Making Process in Integrated Urban Water Management: A Review | Water | [10.3390/w13091252](https://doi.org/10.3390/w13091252) |
| `mytton2021` | Mytton | 2021 | Data centre water consumption | npj Clean Water | [10.1038/s41545-021-00101-w](https://doi.org/10.1038/s41545-021-00101-w) |
| `badruzzaman2022` | Badruzzaman et al. | 2022 | Municipal reclaimed water as makeup water for cooling systems: Water efficiency, biohazards, and reliability | Water Resources and Industry | [10.1016/j.wri.2022.100188](https://doi.org/10.1016/j.wri.2022.100188) |
| `jeffrey2022` | Jeffrey et al. | 2022 | The status of potable water reuse implementation | Water Research | [10.1016/j.watres.2022.118198](https://doi.org/10.1016/j.watres.2022.118198) |
| `ndeketeya2022` | Ndeketeya and Dundu | 2022 | Alternative water sources as a pragmatic approach to improving water security | Resources, Conservation & Recycling Advances | [10.1016/j.rcradv.2022.200071](https://doi.org/10.1016/j.rcradv.2022.200071) |
| `otaki2022` | Otaki et al. | 2022 | Demand-side water management using alternative water sources based on residential end-use | Water Practice and Technology | [10.2166/wpt.2022.031](https://doi.org/10.2166/wpt.2022.031) |
| `ferreira2023` | Ferreira et al. | 2023 | Hybrid Decentralized Systems of Non-potable Water Supply: Performance and Effectiveness Analysis | Water Resources Management | [10.1007/s11269-023-03531-y](https://doi.org/10.1007/s11269-023-03531-y) |
| `porse2023` | Porse | 2023 | Systems analysis of metropolitan-scale reuse with effects on water supply resilience and water quality | Civil Engineering and Environmental Systems | [10.1080/10286608.2023.2263746](https://doi.org/10.1080/10286608.2023.2263746) |
| `vandewalle2023` | Van de Walle et al. | 2023 | Greywater reuse as a key enabler for improving urban wastewater management | Environmental Science and Ecotechnology | [10.1016/j.ese.2023.100277](https://doi.org/10.1016/j.ese.2023.100277) |
| `chen2024recycled` | Chen et al. | 2024 | Benefits and limitations of recycled water systems in the building sector: a review | Environmental Chemistry Letters | [10.1007/s10311-023-01683-2](https://doi.org/10.1007/s10311-023-01683-2) |
| `exposito2024` | Expósito et al. | 2024 | How much does reclaimed wastewater cost? A comprehensive analysis for irrigation uses in the European Mediterranean context | Water Reuse | [10.2166/wrd.2024.040](https://doi.org/10.2166/wrd.2024.040) |
| `garridobaserba2024` | Garrido-Baserba et al. | 2024 | Using water and wastewater decentralization to enhance the resilience and sustainability of cities | Nature Water | [10.1038/s44221-024-00303-9](https://doi.org/10.1038/s44221-024-00303-9) |
| `jahne2024` | Jahne et al. | 2024 | Microbial Treatment Targets for Potable and Nonpotable Water Reuse: A Comprehensive Update and Harmonization | Environmental Science & Technology Letters | [10.1021/acs.estlett.4c00512](https://doi.org/10.1021/acs.estlett.4c00512) |
| `lunstad2024` | Lunstad and Sowby | 2024 | Smart Irrigation Controllers in Residential Applications and the Potential of Integrated Water Distribution Systems | Journal of Water Resources Planning and Management | [10.1061/jwrmd5.wreng-5871](https://doi.org/10.1061/jwrmd5.wreng-5871) |
| `swinbourne2024` | Swinbourne et al. | 2024 | Urban greenery and alternative water sources critically interconnect water supply, cooling, and drainage in urban precincts | Urban Climate | [10.1016/j.uclim.2024.101812](https://doi.org/10.1016/j.uclim.2024.101812) |
| `thakur2024` | Thakur et al. | 2024 | A systematic review of integrated urban water management (IUWM) | Environment, Development and Sustainability | [10.1007/s10668-024-05649-4](https://doi.org/10.1007/s10668-024-05649-4) |
| `hsieh2025` | Hsieh and Chiueh | 2025 | A dynamic allocation framework for urban multi-source water under compound risk: integrating water deficit and quality indices | Journal of Water and Climate Change | [10.2166/wcc.2025.160](https://doi.org/10.2166/wcc.2025.160) |
| `maldonado2025` | Maldonado Benitez et al. | 2025 | Towards Resilient Cities: Systematic Review of the Literature on the Use of AI to Optimize Water Harvesting and Mitigate Scarcity | Water | [10.3390/w17131978](https://doi.org/10.3390/w17131978) |
| `zhong2025` | Zhong et al. | 2025 | Optimizing Investments in Alternative Water Infrastructure for Urban Food Production in Water Stressed Cities | Water Resources Research | [10.1029/2024wr039025](https://doi.org/10.1029/2024wr039025) |
| `jeffrey2026` | Jeffrey et al. | 2026 | Dual-pipe reticulation for non-potable water: a survey of public health risks and their mitigation | Urban Water Journal | [10.1080/1573062x.2026.2695186](https://doi.org/10.1080/1573062x.2026.2695186) |
| `seguela2026` | Seguela et al. | 2026 | When Are Decentralised Non-Potable Water Systems Environmentally and Financially Viable? Evidence from a Water-Energy-GHG Evaluation of a Healthcare Facility in an Arid City | Sustainability | [10.3390/su18062932](https://doi.org/10.3390/su18062932) |

### C5. Loss recovery: leakage, pressure, detection, repair and robots (39)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `lambert1999` | Lambert et al. | 1999 | A review of performance indicators for real losses from water supply systems | Journal of Water Supply: Research and Technology, AQUA | [10.2166/aqua.1999.0025](https://doi.org/10.2166/aqua.1999.0025) |
| `rajani2001` | Rajani and Kleiner | 2001 | Comprehensive review of structural deterioration of water mains: physically based models | Urban Water | [10.1016/s1462-0758(01)00032-2](https://doi.org/10.1016/s1462-0758(01)00032-2) |
| `lambert2005` | Lambert and Fantozzi | 2005 | Recent advances in calculating economic intervention frequency for active leakage control, and implications for calculation of economic leakage levels | Water Supply | [10.2166/ws.2005.0072](https://doi.org/10.2166/ws.2005.0072) |
| `araujo2006` | Araujo et al. | 2006 | Pressure Control for Leakage Minimisation in Water Distribution Systems Management | Water Resources Management | [10.1007/s11269-006-4635-3](https://doi.org/10.1007/s11269-006-4635-3) |
| `vanzyl2007` | van Zyl and Clayton | 2007 | The effect of pressure on leakage in water distribution systems | Proceedings of the Institution of Civil Engineers - Water Management | [10.1680/wama.2007.160.2.109](https://doi.org/10.1680/wama.2007.160.2.109) |
| `mounce2010` | Mounce et al. | 2010 | Development and Verification of an Online Artificial Intelligence System for Detection of Bursts and Other Abnormal Flows | Journal of Water Resources Planning and Management | [10.1061/(ASCE)WR.1943-5452.0000030](https://doi.org/10.1061/(ASCE)WR.1943-5452.0000030) |
| `puust2010` | Puust et al. | 2010 | A review of methods for leakage management in pipe networks | Urban Water Journal | [10.1080/15730621003610878](https://doi.org/10.1080/15730621003610878) |
| `karadirek2012` | Karadirek et al. | 2012 | Implementation of Hydraulic Modelling for Water-Loss Reduction Through Pressure Management | Water Resources Management | [10.1007/s11269-012-0032-2](https://doi.org/10.1007/s11269-012-0032-2) |
| `britton2013` | Britton et al. | 2013 | Smart metering: enabler for rapid and effective post meter leakage identification and water loss management | Journal of Cleaner Production | [10.1016/j.jclepro.2013.05.018](https://doi.org/10.1016/j.jclepro.2013.05.018) |
| `islam2013` | Islam and Babel | 2013 | Economic Analysis of Leakage in the Bangkok Water Distribution System | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0000235](https://doi.org/10.1061/(asce)wr.1943-5452.0000235) |
| `vanzyl2014` | van Zyl and Cassa | 2014 | Modeling Elastically Deforming Leaks in Water Distribution Pipes | Journal of Hydraulic Engineering | [10.1061/(asce)hy.1943-7900.0000813](https://doi.org/10.1061/(asce)hy.1943-7900.0000813) |
| `gonelas2015` | Gonelas and Kanakoudis | 2015 | Reaching economic leakage level through pressure management | Water Supply | [10.2166/ws.2015.181](https://doi.org/10.2166/ws.2015.181) |
| `mancuso2016` | Mancuso et al. | 2016 | Risk-based optimization of pipe inspections in large underground networks with imprecise information | Reliability Engineering & System Safety | [10.1016/j.ress.2016.03.011](https://doi.org/10.1016/j.ress.2016.03.011) |
| `memarzadeh2016insp` | Memarzadeh and Pozzi | 2016 | Integrated Inspection Scheduling and Maintenance Planning for Infrastructure Systems | Computer-Aided Civil and Infrastructure Engineering | [10.1111/mice.12178](https://doi.org/10.1111/mice.12178) |
| `memarzadeh2016voi` | Memarzadeh and Pozzi | 2016 | Value of information in sequential decision making: Component inspection, permanent monitoring and system-level scheduling | Reliability Engineering & System Safety | [10.1016/j.ress.2016.05.014](https://doi.org/10.1016/j.ress.2016.05.014) |
| `vicente2016` | Vicente et al. | 2016 | Pressure Management in Water Distribution Systems: Current Status, Proposals, and Future Trends | Journal of Water Resources Planning and Management | [10.1061/(ASCE)WR.1943-5452.0000589](https://doi.org/10.1061/(ASCE)WR.1943-5452.0000589) |
| `creaco2017` | Creaco and Walski | 2017 | Economic Analysis of Pressure Control for Leakage and Pipe Burst Reduction | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0000846](https://doi.org/10.1061/(asce)wr.1943-5452.0000846) |
| `vanzyl2017` | van Zyl and Malde | 2017 | Evaluating the pressure-leakage behaviour of leaks in water pipes | Journal of Water Supply: Research and Technology - Aqua | [10.2166/aqua.2017.136](https://doi.org/10.2166/aqua.2017.136) |
| `aboelnga2018` | Aboelnga et al. | 2018 | Component analysis for optimal leakage management in Madaba, Jordan | Journal of Water Supply: Research and Technology - Aqua | [10.2166/aqua.2018.180](https://doi.org/10.2166/aqua.2018.180) |
| `brentan2018` | Brentan et al. | 2018 | Joint Operation of Pressure-Reducing Valves and Pumps for Improving the Efficiency of Water Distribution Systems | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0000974](https://doi.org/10.1061/(asce)wr.1943-5452.0000974) |
| `liemberger2019` | Liemberger and Wyatt | 2018 | Quantifying the global non-revenue water problem | Water Supply | [10.2166/ws.2018.129](https://doi.org/10.2166/ws.2018.129) |
| `balut2019` | Bałut et al. | 2019 | Ranking Approach to Scheduling Repairs of a Water Distribution System for the Post-Disaster Response and Restoration Service | Water | [10.3390/w11081591](https://doi.org/10.3390/w11081591) |
| `shao2019` | Shao et al. | 2019 | Leakage Control and Energy Consumption Optimization in the Water Distribution Network Based on Joint Scheduling of Pumps and Valves | Energies | [10.3390/en12152969](https://doi.org/10.3390/en12152969) |
| `ahopelto2020` | Ahopelto and Vahala | 2020 | Cost-Benefit Analysis of Leakage Reduction Methods in Water Supply Networks | Water | [10.3390/w12010195](https://doi.org/10.3390/w12010195) |
| `assad2020` | Assad et al. | 2020 | Resilience-Driven Multiobjective Restoration Planning for Water Distribution Networks | Journal of Performance of Constructed Facilities | [10.1061/(asce)cf.1943-5509.0001478](https://doi.org/10.1061/(asce)cf.1943-5509.0001478) |
| `moslehi2020` | Moslehi et al. | 2020 | Developing a framework for leakage target setting in water distribution networks from an economic perspective | Structure and Infrastructure Engineering | [10.1080/15732479.2020.1777568](https://doi.org/10.1080/15732479.2020.1777568) |
| `aitken2021` | Aitken et al. | 2021 | Simultaneous Localization and Mapping for Inspection Robots in Water and Sewer Pipe Networks: A Review | IEEE Access | [10.1109/access.2021.3115981](https://doi.org/10.1109/access.2021.3115981) |
| `marzola2021` | Marzola et al. | 2021 | Analysis of MNF and FAVAD Model for Leakage Characterization by Exploiting Smart-Metered Data: The Case of the Gorino Ferrarese (FE-Italy) District | Water | [10.3390/w13050643](https://doi.org/10.3390/w13050643) |
| `vrachimis2022` | Vrachimis et al. | 2022 | Battle of the Leakage Detection and Isolation Methods | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0001601](https://doi.org/10.1061/(asce)wr.1943-5452.0001601) |
| `kahnamouei2023` | Kahnamouei and Moallem | 2023 | A comprehensive review of in-pipe robots | Ocean Engineering | [10.1016/j.oceaneng.2023.114260](https://doi.org/10.1016/j.oceaneng.2023.114260) |
| `romeroben2023` | Romero-Ben et al. | 2023 | Leak detection and localization in water distribution networks: Review and perspective | Annual Reviews in Control | [10.1016/j.arcontrol.2023.03.012](https://doi.org/10.1016/j.arcontrol.2023.03.012) |
| `farah2024` | Farah and Shahrour | 2024 | Water Leak Detection: A Comprehensive Review of Methods, Challenges, and Future Directions | Water | [10.3390/w16202975](https://doi.org/10.3390/w16202975) |
| `ferrarese2024` | Ferrarese et al. | 2024 | Review of Metaheuristic Methodologies for Leakage Reduction and Energy Saving in Water Distribution Networks | Water Resources Management | [10.1007/s11269-024-03822-y](https://doi.org/10.1007/s11269-024-03822-y) |
| `jeon2024` | Jeon et al. | 2024 | Development of an In-Pipe Inspection Robot for Large-Diameter Water Pipes | Sensors | [10.3390/s24113470](https://doi.org/10.3390/s24113470) |
| `santos2024` | Santos | 2024 | Beyond Leakage: Non-Revenue Water Loss and Economic Sustainability | Urban Science | [10.3390/urbansci8040194](https://doi.org/10.3390/urbansci8040194) |
| `serafeim2024` | Serafeim et al. | 2024 | Leakages in Water Distribution Networks: Estimation Methods, Influential Factors, and Mitigation Strategies, A Comprehensive Review | Water | [10.3390/w16111534](https://doi.org/10.3390/w16111534) |
| `barfuss2025` | Barfuss and Fugal | 2025 | Water Main Break Rates in the United States and Canada | Journal AWWA | [10.1002/awwa.2401](https://doi.org/10.1002/awwa.2401) |
| `arrington2026` | Arrington | 2026 | Leak Detection Strategies: One Size Does Not Fit All | Journal AWWA | [10.1002/awwa.70038](https://doi.org/10.1002/awwa.70038) |
| `wang2026carbon` | Wang et al. | 2026 | Unlocking energy-carbon-water synergies in global water supply system maintenance | Nature Communications | [10.1038/s41467-026-72300-3](https://doi.org/10.1038/s41467-026-72300-3) |

### C6. Operations and the water-energy nexus (8)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `plappally2012` | Plappally and Lienhard V | 2012 | Energy requirements for water production, treatment, end use, reclamation, and disposal | Renewable and Sustainable Energy Reviews | [10.1016/j.rser.2012.05.022](https://doi.org/10.1016/j.rser.2012.05.022) |
| `nair2014` | Nair et al. | 2014 | Water-energy-greenhouse gas nexus of urban water systems: Review of concepts, state-of-art and methods | Resources, Conservation and Recycling | [10.1016/j.resconrec.2014.05.007](https://doi.org/10.1016/j.resconrec.2014.05.007) |
| `menke2016` | Menke et al. | 2016 | Demonstrating demand response from water distribution system through pump scheduling | Applied Energy | [10.1016/j.apenergy.2016.02.136](https://doi.org/10.1016/j.apenergy.2016.02.136) |
| `lee2017` | Lee et al. | 2017 | Water-energy nexus for urban water systems: A comparative review on energy intensity and environmental impacts in relation to global water risks | Applied Energy | [10.1016/j.apenergy.2017.08.002](https://doi.org/10.1016/j.apenergy.2017.08.002) |
| `rambo2017` | Rambo et al. | 2017 | Water-Energy Nexus in Saudi Arabia | Energy Procedia | [10.1016/j.egypro.2017.03.782](https://doi.org/10.1016/j.egypro.2017.03.782) |
| `wu2020` | Wu et al. | 2020 | The changing nature of the water-energy nexus in urban water supply systems: a critical review of changes and responses | Journal of Water and Climate Change | [10.2166/wcc.2020.276](https://doi.org/10.2166/wcc.2020.276) |
| `tasseff2024` | Tasseff et al. | 2024 | Polyhedral Relaxations for Optimal Pump Scheduling of Potable Water Distribution Networks | INFORMS Journal on Computing | [10.1287/ijoc.2022.0233](https://doi.org/10.1287/ijoc.2022.0233) |
| `putri2025` | Putri and Moazeni | 2025 | Stability-guaranteed data-driven nonlinear predictive control of water distribution systems | Control Engineering Practice | [10.1016/j.conengprac.2025.106243](https://doi.org/10.1016/j.conengprac.2025.106243) |

### C7. Demand, metering, behaviour and sectors (12)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `olmstead2009` | Olmstead and Stavins | 2009 | Comparing price and nonprice approaches to urban water conservation | Water Resources Research | [10.1029/2008WR007227](https://doi.org/10.1029/2008WR007227) |
| `gatotrinidad2011` | Gato-Trinidad et al. | 2011 | Understanding urban residential end uses of water | Water Science and Technology | [10.2166/wst.2011.436](https://doi.org/10.2166/wst.2011.436) |
| `willis2011` | Willis et al. | 2011 | Quantifying the influence of environmental and water conservation attitudes on household end use water consumption | Journal of Environmental Management | [10.1016/j.jenvman.2011.03.023](https://doi.org/10.1016/j.jenvman.2011.03.023) |
| `boyle2013` | Boyle et al. | 2013 | Intelligent Metering for Urban Water: A Review | Water | [10.3390/w5031052](https://doi.org/10.3390/w5031052) |
| `ferraro2013` | Ferraro and Price | 2013 | Using Nonpecuniary Strategies to Influence Behavior: Evidence from a Large-Scale Field Experiment | Review of Economics and Statistics | [10.1162/rest_a_00344](https://doi.org/10.1162/rest_a_00344) |
| `beal2015` | Beal and Flynn | 2015 | Toward the digital water age: Survey and case studies of Australian water utility smart-metering programs | Utilities Policy | [10.1016/j.jup.2014.12.006](https://doi.org/10.1016/j.jup.2014.12.006) |
| `cominola2015` | Cominola et al. | 2015 | Benefits and challenges of using smart meters for advancing residential water demand modeling and management: A review | Environmental Modelling & Software | [10.1016/j.envsoft.2015.07.012](https://doi.org/10.1016/j.envsoft.2015.07.012) |
| `sonderlund2016` | Sønderlund et al. | 2016 | Effectiveness of Smart Meter-Based Consumption Feedback in Curbing Household Water Use: Knowns and Unknowns | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0000703](https://doi.org/10.1061/(asce)wr.1943-5452.0000703) |
| `gonzalez2018` | González et al. | 2018 | Quantitative Determination of Potable Cold Water Consumption in German Hospitals | Sustainability | [10.3390/su10040932](https://doi.org/10.3390/su10040932) |
| `nguyen2018` | Nguyen et al. | 2018 | Re-engineering traditional urban water management practices with smart metering and informatics | Environmental Modelling & Software | [10.1016/j.envsoft.2017.12.015](https://doi.org/10.1016/j.envsoft.2017.12.015) |
| `monks2020` | Monks et al. | 2020 | Expert Opinion Valuation Method to Quantify Digital Water Metering Benefits | Water | [10.3390/w12051436](https://doi.org/10.3390/w12051436) |
| `alzahrani2025` | Alzahrani et al. | 2025 | The Role of Smart Infrastructure in Residential Water Demand Management: A Global Survey | Water | [10.3390/w17213119](https://doi.org/10.3390/w17213119) |

### C8. Governance, safety, security and human factors (16)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `parasuraman2000` | Parasuraman et al. | 2000 | A model for types and levels of human interaction with automation | IEEE Transactions on Systems, Man, and Cybernetics - Part A: Systems and Humans | [10.1109/3468.844354](https://doi.org/10.1109/3468.844354) |
| `lee2004` | Lee and See | 2004 | Trust in Automation: Designing for Appropriate Reliance | Human Factors: The Journal of the Human Factors and Ergonomics Society | [10.1518/hfes.46.1.50.30392](https://doi.org/10.1518/hfes.46.1.50.30392) |
| `alshiekh2018` | Alshiekh et al. | 2018 | Safe Reinforcement Learning via Shielding | Proceedings of the AAAI Conference on Artificial Intelligence | [10.1609/aaai.v32i1.11797](https://doi.org/10.1609/aaai.v32i1.11797) |
| `housh2018` | Housh and Ohar | 2018 | Model-based approach for cyber-physical attack detection in water distribution systems | Water Research | [10.1016/j.watres.2018.03.039](https://doi.org/10.1016/j.watres.2018.03.039) |
| `taormina2018` | Taormina et al. | 2018 | Battle of the Attack Detection Algorithms: Disclosing Cyber Attacks on Water Distribution Networks | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0000969](https://doi.org/10.1061/(asce)wr.1943-5452.0000969) |
| `hassanzadeh2020` | Hassanzadeh et al. | 2020 | A Review of Cybersecurity Incidents in the Water Sector | Journal of Environmental Engineering | [10.1061/(asce)ee.1943-7870.0001686](https://doi.org/10.1061/(asce)ee.1943-7870.0001686) |
| `nistzt` | Rose et al. | 2020 | Zero Trust Architecture |  | [10.6028/NIST.SP.800-207](https://doi.org/10.6028/NIST.SP.800-207) |
| `olsson2020` | Olsson | 2020 | Urban water supply automation: today and tomorrow | Journal of Water Supply: Research and Technology-Aqua | [10.2166/aqua.2020.115](https://doi.org/10.2166/aqua.2020.115) |
| `doorn2021` | Doorn | 2021 | Artificial intelligence in the water domain: Opportunities for responsible use | Science of The Total Environment | [10.1016/j.scitotenv.2020.142561](https://doi.org/10.1016/j.scitotenv.2020.142561) |
| `moazeni2021` | Moazeni and Khazaei | 2021 | Sequential false data injection cyberattacks in water distribution systems targeting storage tanks, a bi-level optimization model | Sustainable Cities and Society | [10.1016/j.scs.2021.102895](https://doi.org/10.1016/j.scs.2021.102895) |
| `tuptuk2021` | Tuptuk et al. | 2021 | A Systematic Review of the State of Cyber-Security in Water Systems | Water | [10.3390/w13010081](https://doi.org/10.3390/w13010081) |
| `savic2022` | Savić | 2022 | Digital Water Developments and Lessons Learned from Automation in the Car and Aircraft Industries | Engineering | [10.1016/j.eng.2021.05.013](https://doi.org/10.1016/j.eng.2021.05.013) |
| `hobbs2023` | Hobbs et al. | 2023 | Runtime Assurance for Safety-Critical Systems: An Introduction to Safety Filtering Approaches for Complex Control Systems | IEEE Control Systems | [10.1109/mcs.2023.3234380](https://doi.org/10.1109/mcs.2023.3234380) |
| `nistairmf` | Tabassi | 2023 | Artificial Intelligence Risk Management Framework (AI RMF 1.0) |  | [10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1) |
| `almheiri2024` | Almheiri et al. | 2024 | Examining the Challenges of Implementing Artificial Intelligence in the Water Supply Sector: A Case Study | Water | [10.3390/w16233539](https://doi.org/10.3390/w16233539) |
| `okwori2026` | Okwori et al. | 2026 | A loop unclosed: why AI decision support in water asset management stalls and how utilities can unlock its value | Water Practice & Technology | [10.2166/wpt.2026.260](https://doi.org/10.2166/wpt.2026.260) |

### C9. Economics, evaluation and sensitivity analysis (9)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `sobol2001` | Sobol′ | 2001 | Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates | Mathematics and Computers in Simulation | [10.1016/S0378-4754(00)00270-6](https://doi.org/10.1016/S0378-4754(00)00270-6) |
| `saltelli2010` | Saltelli et al. | 2010 | Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index | Computer Physics Communications | [10.1016/j.cpc.2009.09.018](https://doi.org/10.1016/j.cpc.2009.09.018) |
| `brodersen2015` | Brodersen et al. | 2015 | Inferring causal impact using Bayesian structural time-series models | The Annals of Applied Statistics | [10.1214/14-AOAS788](https://doi.org/10.1214/14-AOAS788) |
| `hemming2015` | Hemming et al. | 2015 | The stepped wedge cluster randomised trial: rationale, design, analysis, and reporting | BMJ | [10.1136/bmj.h391](https://doi.org/10.1136/bmj.h391) |
| `pianosi2016` | Pianosi et al. | 2016 | Sensitivity analysis of environmental models: A systematic review with practical workflow | Environmental Modelling & Software | [10.1016/j.envsoft.2016.02.008](https://doi.org/10.1016/j.envsoft.2016.02.008) |
| `herman2017` | Herman and Usher | 2017 | SALib: An open-source Python library for Sensitivity Analysis | The Journal of Open Source Software | [10.21105/joss.00097](https://doi.org/10.21105/joss.00097) |
| `erfani2018` | Erfani et al. | 2018 | Real‐Options Water Supply Planning: Multistage Scenario Trees for Adaptive and Flexible Capacity Expansion Under Probabilistic Climate Change Uncertainty | Water Resources Research | [10.1029/2017wr021803](https://doi.org/10.1029/2017wr021803) |
| `gillingham2018` | Gillingham et al. | 2018 | Advances in Evaluating Energy Efficiency Policies and Programs | Annual Review of Resource Economics | [10.1146/annurev-resource-100517-023028](https://doi.org/10.1146/annurev-resource-100517-023028) |
| `daniel2023` | Daniel et al. | 2023 | A survey of water utilities’ digital transformation: drivers, impacts, and enabling technologies | npj Clean Water | [10.1038/s41545-023-00265-7](https://doi.org/10.1038/s41545-023-00265-7) |

### C10. Tools and data (4)

| Key | Authors | Year | Title | Venue | DOI |
|----------------------|--------------|-----|------------------------------|--------------|------------------|
| `hargreaves1985` | Hargreaves and Samani | 1985 | Reference Crop Evapotranspiration from Temperature | Applied Engineering in Agriculture | [10.13031/2013.26773](https://doi.org/10.13031/2013.26773) |
| `menne2012` | Menne et al. | 2012 | An Overview of the Global Historical Climatology Network-Daily Database | Journal of Atmospheric and Oceanic Technology | [10.1175/jtech-d-11-00103.1](https://doi.org/10.1175/jtech-d-11-00103.1) |
| `marchi2014` | Marchi et al. | 2014 | Battle of the Water Networks II | Journal of Water Resources Planning and Management | [10.1061/(asce)wr.1943-5452.0000378](https://doi.org/10.1061/(asce)wr.1943-5452.0000378) |
| `klise2017` | Klise et al. | 2017 | A software framework for assessing the resilience of drinking water systems to disasters with an example earthquake case study | Environmental Modelling & Software | [10.1016/j.envsoft.2017.06.022](https://doi.org/10.1016/j.envsoft.2017.06.022) |
