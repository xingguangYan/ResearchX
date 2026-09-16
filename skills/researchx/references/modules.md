# Module Specifications

Full step-by-step specs for M1–M12. SKILL.md carries the routing table and the gates;
this file carries the procedure. Load the section you need, not the whole file.

Shared preconditions for every module:

- Search first, write second. No module may state a fact about the literature it did not retrieve.
- Name the registries/queries and the date in the output header (that is what makes a review reproducible).
- Verify every reference with `scripts/verify_citations.py` before it is written into a deliverable.
- When data is missing, ask for the specific table/figure — never estimate silently.

---

## M1 · Paper Analysis

**Trigger**: uploaded PDF, DOI, arXiv ID, title, "review this paper", "帮我读这篇论文".

**Steps**
1. Resolve identity: DOI/arXiv ID → metadata via `verify_citations.py --doi`, then `--format json`.
   Record: title, venue, year, authors, retraction status.
2. Read the paper in this order: abstract → figures and tables (they carry the claims) → methods → results → discussion → limitations. Do not summarise from the abstract alone.
3. Build the logic chain: RQ → data → method → experiment → result → conclusion. Every arrow must be supported by something in the text; mark weak links explicitly.
4. Extract the "why" answers: why this problem, why this approach, why these baselines, why these metrics.
5. Strengths / weaknesses table — at least 3 rows each, each row citing the section it comes from.
6. Missing-experiment detection with the M4 checklist → list what a reviewer will demand.
7. Position against 2023-2026 SOTA: search the method family, compare metrics on comparable data. Flag comparisons that are not on the same dataset/metric as invalid.
8. Audit the paper's own references (spot-check 5-10 or all if short) and report notable failures.
9. Three actionable improvements, ranked by effort/impact, each naming the experiment or citation required.

**Output**: `analysis_[short-title]_YYYYMMDD.md` with the sections above + a "verification" block
(how many references checked, how many unresolved).

**Trap**: do not treat the paper's own numbers as independent evidence. Report them as "reported by
the authors", and say when the split, seed, or baseline is unclear.

---

## M2 · Gap Mining & Topic Discovery

**Steps**
1. Frame the domain in one paragraph (what is measured, on what data, for whom).
2. Run ≥5 searches covering: recent reviews, benchmark/SOTA, limitations/失败案例, adjacent-field methods, and the user's own language (e.g. Chinese queries for CNKI-indexed topics).
3. Classify literature into the gap taxonomy: solved / unsolved / controversial / unexplored. Every entry cites a real paper.
4. Cross-domain pass: `[method from field A] + [user's field B]`, keep only transfers with a plausible mechanism.
5. Generate **5 topics**. Each contains: research question (one sentence, testable), novelty claim vs the specific papers it beats, data needed (name datasets), proposed method (from M3 search, referenced), target venue, feasibility ★/5, and **scoop risk** (how likely someone is already doing this, and why).
6. Add a "how to falsify" line: the result that would kill the idea.
7. Rank on novelty × feasibility × data availability; state which single topic you would start with and why.

**Output**: `topics_[topic]_YYYYMMDD.md`.

**Trap**: a "gap" that is really just an absence of your own search. Before declaring unexplored, search
the exact phrasing twice (English + native language) and once more after removing the year filter.

---

## M2b · Novelty Check / Prior-Art Scan

**Steps**
1. Decompose the idea into 3-6 atomic claims.
2. For each claim run: keyword search (`search_literature.py`), forward chaining (`--cited-by` on the closest paper), and backward chaining (`--references-of`).
3. Classify each claim: `novel` / `incremental` / `already published (cite)`.
4. Identify the closest prior work and state the difference in one measurable sentence (data, setting, metric, assumption).
5. Write the novelty statement a reviewer would accept, plus the strongest objection it must survive and the experiment that answers it.

**Output**: `novelty_check_[topic]_YYYYMMDD.md` with a claim-by-claim table.

---

## M3 · Method Mining

**Steps**
1. Search method families: `"[topic] review methods"`, `"[topic] benchmark comparison"`, `"[topic] SOTA"`, `"[topic] [family] 2024..2026"`.
2. Build the family table: family → representative papers (DOI) → reported performance *with the dataset it was measured on* → strengths → failure modes → compute/data cost.
3. Build the evolution timeline; mark paradigm shifts, not just years.
4. Record assumptions that do not hold in the user's setting (resolution, label budget, sensor, language, case-mix).
5. Recommend one family for the user's sub-problem with three reasons tied to retrieved evidence.
6. Innovation opportunities: cross-domain transfer, missing combination, new evaluation setting. For each, name the required baseline and the expected reviewer objection.

**Output**: `methods_[topic]_YYYYMMDD.md` + machine-readable `methods_[topic]_YYYYMMDD.json`.

**Trap**: leaderboard numbers are not comparable across datasets. Never place two numbers in one row
without the dataset column filled.

---

## M4 · Experiment Design

**Required blocks**
1. **Baselines** — 3-5 recent SOTA, same data split, plus one simple/interpretable baseline to show the problem is non-trivial.
2. **Ablations** — remove each proposed component; include a "no added module" run and a parameter-count-matched control.
3. **Sensitivity** — key hyperparameters with a stated range and step; report the plateau, not just the peak.
4. **Generalisation** — ≥2 out-of-domain tests (region, sensor/device, time period, population).
5. **Robustness** — noise, missing data, class imbalance, adversarial or distribution shift as appropriate.
6. **Statistics** — ≥5 seeds, mean ± std, paired test (t-test/Wilcoxon/McNemar as appropriate), effect size, and a correction for multiple comparisons when many configurations are compared.
7. **Compute & cost** — hardware, training time, inference cost, memory; state if it does not fit a normal lab.
8. **Reproducibility** — seeds, versions, data split files, preprocessing order.

**Missing-experiment detector** — score the design N/10 and list what a hostile reviewer asks for:
the baseline you omitted, the test set you only used once, the ablation that removes two components at
once, the metric that hides failure on the class you care about.

**Output**: `experiment_plan_[topic]_YYYYMMDD.md` (+ table template the user can fill with results).

---

## M5 · Manuscript Writing

Write section by section; do not dump a whole paper at once unless asked.

| Section | Structure | Budget guide |
|---|---|---|
| Title | claim + object + setting | ≤ 15 words |
| Abstract | context (1s) → gap (1s) → method (2-3s) → results with numbers (2s) → implication (1s) | 150-250 words |
| Introduction | broad → known → gap (cited) → our approach → contributions (3-5 bullets) → organisation | 700-1000 words |
| Related work | thematic groups → each ends with why it does not solve the problem | 600-1200 words |
| Methods | data → preprocessing → model (equations) → training → evaluation metrics → implementation | 1500-2500 words |
| Results | overall table → ablations → sensitivity → generalisation → qualitative | 1200-2000 words |
| Discussion | findings → comparison to literature → unexpected results → limitations → future work | 700-1200 words |
| Conclusion | summary → contributions → limits → outlook | 200-350 words |

Rules: one idea per paragraph; every number in the text must exist in a table or figure; every claim
carries a citation or an experiment; define abbreviations at first use; past tense for what you did,
present tense for what is true.

**Output**: `manuscript_[topic]_YYYYMMDD.md`, plus a word-count table and a figure/table plan.

---

## M6 · Journal Fit & Upgrade

1. Score novelty / evidence / writing / related work (★/5) with one sentence of justification each.
2. Compare against the target venue's accepted-paper profile (search recent accepted papers on the same topic in that venue).
3. Ranked actions: Priority 1 must be the change with the largest expected reviewer impact; each action states the work required, the expected gain, and the citation needed.
4. Recommend 3 venues: scope fit, IF/quartile (state the source and year of the metric), typical time to first decision, APC/OA options, desk-rejection risks (e.g. scope mismatch, purely incremental).
5. Flag integrity issues found in the audit before recommending submission.

**Output**: `upgrade_plan_[paper]_YYYYMMDD.md`.

**Trap**: impact factors and acceptance rates drift and vary by source — state where the number came from
and when, or mark it `(verify)`.

---

## M7 · Peer Review Simulation

Personas: (1) domain expert — significance and positioning; (2) methodologist — design, statistics, reproducibility; (3) hostile Reviewer 2 — searches for the fatal flaw.

For each comment: `[Severity: major/minor]` + the evidence + the cheapest sufficient fix (new experiment, re-analysis, clarification, or removal of the claim).

Always include: at least one comment that would justify rejection if unanswered, one about baselines, and
one about reproducibility or statistics.

Then write the response letter: `Comment → Response (thanks + substance) → Change (exact location)`.
Refuse to promise work that was not done.

**Output**: `review_report.md`, `response_letter.md`.

---

## M8 · Visuals & Figures

- Graphical abstract: one visual story — input → method → outcome; audience level = reader of the abstract only. Provide 3 prompts (image models) × 3 aesthetics (Nature-like minimal, Elsevier-style diagrammatic, conference-bold), plus a "do not show" list (no invented numbers, no fake microscopy, no unlabelled axes).
- Poster: A0/A1/9:16 layouts — title block, motivation, method flow, key result (one hero figure), conclusion, QR to code/data.
- Diagrams: Mermaid for workflow, PRISMA, taxonomy, and concept maps (`generate_visuals.py workflow|prisma|taxonomy`).
- Figure spec: width in mm (single 85, double 170), 300-600 DPI, ≥7 pt font at final size, colour-blind-safe palette, vector where possible, no chartjunk, error bars always defined.

**Output**: prompt block file + `.mmd` snippets + `figure_spec.md` for the artist/yourself.

---

## M9 · Literature & Systematic Review

Choose the mode explicitly and tell the user which one you are running.

**Narrative mode**: retrieve → matrix → synthesis grouped thematically → gap paragraph → limitations of the review itself.

**Systematic mode (PRISMA 2020)**: follow `references/systematic-review-prisma.md`.
Pipeline: protocol → search (record strings + date + registries) → `search_literature.py --format json` → `prisma_screen.py` → full-text/eligibility with recorded reasons → risk of bias → synthesis → PRISMA flow + counts + disclosure.

**Output**: `literature_matrix_[topic]_YYYYMMDD.md`; systematic mode adds `prisma_flow.md`,
`screening_ledger.csv`, `prisma_counts.json`.

**Trap**: dedupe before screening (or the PRISMA counts lie); record exclusion reasons per record at the
moment you decide, not from memory afterwards.

---

## M10 · Grant Proposal

Structure (adapt to funder; NSFC shown):

1. 立项依据 / rationale — field state, the specific unsolved problem, why now, why this team. Cited.
2. 科学问题 / scientific questions — 2-3 questions, each falsifiable.
3. 研究目标 / objectives — measurable outcomes with numbers and a deadline.
4. 研究内容 / content — work packages with inputs, methods, milestones.
5. 技术路线 / technical route — Mermaid diagram plus narrative of the critical path.
6. 创新点 / innovation — 2-4 points, each contrasted with the closest existing work.
7. Feasibility — preliminary results, data access, facilities, team.
8. Risk mitigation — the two most likely failure modes and the fallback.
9. 预期成果 / outcomes — papers (venues), data/code release, training, societal impact.
10. Timeline + budget — with justification lines and dependencies.

**Output**: `grant_proposal_[topic]_YYYYMMDD.md`.

**Trap**: never write "international leading" claims without a citation; funders read the references too.

---

## M11 · Citation Audit

See SKILL.md §2 for the protocol. Additional checks beyond registry lookup:

- in-text citations without a reference entry, and entries never cited;
- the same work cited twice under different years;
- preprints presented as peer-reviewed (mark venue as arXiv/bioRxiv);
- dataset/software citations missing (they have DOIs too);
- citation-context mismatch: the cited source does not support the sentence — check the abstract at minimum, the cited section preferably;
- retracted or corrected works, and works with published expressions of concern.

**Output**: `citation_audit_YYYYMMDD.md` + `.json`; changes listed as a diff-ready checklist.

---

## M12 · Reproducibility & Artifact Packaging

Checklist to hand the user:

1. Data availability statement (repository, accession, licence, embargo).
2. Code repository with licence, install instructions tested on a clean machine, entry points per experiment.
3. Environment lock (requirements/pyproject with versions, CUDA/driver, OS).
4. Seeds and determinism notes; hardware used; expected runtime per experiment.
5. Hyperparameter table with search range and final values.
6. Data splits released as files, not described in prose.
7. A 30-minute reproduction path: the one command per headline result.
8. Ethics/consent and data-protection statements where relevant.

**Output**: `reproducibility_package_[topic]_YYYYMMDD.md` + `artifact_README.md` from
`assets/artifact-readme-template.md`.
