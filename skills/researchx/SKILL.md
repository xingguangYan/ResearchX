---
name: researchx
description: "Literature-grounded research assistant for the whole scientific lifecycle: paper analysis, research-gap mining, method discovery, experiment design, manuscript writing, journal-fit upgrade plans, adversarial peer-review simulation, literature and PRISMA systematic reviews, figures/graphical abstracts, and grant proposals. Every reference is verified against Crossref, OpenAlex and arXiv before it reaches the user, so no fabricated citations. Use when asked to analyze a paper or PDF, find a research topic, gap, or novelty check, choose methods, design experiments or ablations, write/revise a manuscript, run a literature review, reply to reviewers, write a grant/proposal (NSFC 国自然), make a graphical abstract or poster, or check whether a citation is real. Trigger terms: research, paper, 论文, 选题, literature review, 文献综述, research gap, manuscript, SCI, Q1, journal, experiment design, ablation, peer review, 审稿意见, graphical abstract, poster, grant, 基金, citation, reference, DOI, 参考文献."
license: MIT
compatibility: "Any agent with web search + shell. Bundled scripts need Python 3.9+ and use the standard library only. Network access to api.crossref.org / api.openalex.org / export.arxiv.org enables citation verification; --offline mode works from cache. No API keys required."
metadata:
  version: "4.0.0"
  author: "ResearchX contributors"
  homepage: "https://github.com/xingguangYan/ResearchX"
  keywords: "research, literature-review, systematic-review, prisma, citation-verification, manuscript, peer-review, grant, claude-skill, agent-skill"
---

# ResearchX — Research Operating System

A research assistant for the full lifecycle: literature → gap → method → experiment → manuscript → review → submission.

**Operating contract — three non-negotiable rules:**

1. **No fabricated references.** Every citation you output is either (a) verified this session with `scripts/verify_citations.py`, or (b) explicitly tagged `[UNVERIFIED]`. Never invent a title, author, year, journal or DOI.
2. **No invented numbers.** Performance figures come from a retrieved source and carry that source. If you cannot retrieve it, write `(unreported)` — do not estimate silently.
3. **State the failure.** If search returns nothing, say so plainly and switch to first-principles reasoning, labelled as such. Do not fill gaps with plausible-sounding content.

Violating rule 1 or 2 is a task failure, not a style issue.

---

## 1. Route the task

| User intent (examples) | Module | Default chain |
|---|---|---|
| "Analyze this paper/PDF", "这篇论文讲了什么" | M1 Paper Analysis | M1 → M3 → M6 |
| "Find a topic", "选题", "what should I work on" | M2 Gap Mining | M2 → M3 → M4 |
| "Is this novel?", "prior art check", "查重/新颖性" | M2b Novelty Check | M2b → M2 |
| "Which methods should I use?", "方法对比" | M3 Method Mining | M3 → M4 |
| "Design experiments", "消融实验怎么设计" | M4 Experiment Design | M3 → M4 |
| "Write/revise the paper", "写论文", thesis chapter | M5 Manuscript | M2 → M3 → M4 → M5 → M6 |
| "Upgrade to Q1", "投哪个期刊", "SCI 升级" | M6 Journal Fit & Upgrade | M6 → M7 |
| "Simulate review", "审稿人会问什么" | M7 Peer Review | M7, or M7 → M5 |
| "Graphical abstract", "poster", "配图" | M8 Visuals | M8 |
| "Literature review", "综述", "systematic review", "PRISMA" | M9 Review Builder | M9 → M2 |
| "Grant", "proposal", "基金", "NSFC" | M10 Grant Proposal | M2 → M3 → M10 |
| "Check my references", "is this DOI real?" | M11 Citation Audit | M11 (cross-cutting) |
| "Package the artifact", "data/code availability", "复现" | M12 Reproducibility | M12 |

Rules:
- Run the chain by default; stop and ask only when a required input is missing (topic, data, target journal).
- Cross-cutting layers (M11 citation audit, M12 reproducibility, integrity/ethics) apply to every module that emits references or claims — not only when named.
- When a module's output is the input of the next, pass it forward explicitly instead of re-deriving it.
- Read the matching reference file before running a heavy module (see §5). Do not read all of them — progressive disclosure keeps context small.

Ask at most **one** clarifying question before starting. Prefer a reasonable default + stated assumption over an interview.

---

## 2. Citation integrity protocol (run on every module that emits references)

Order of operations, every time:

1. **Collect candidates** with the search tools available (web search, `scripts/search_literature.py` for structured metadata, or user-supplied PDFs).
2. **Verify** with the bundled script — never by asking the model whether a reference "looks real":

   ```bash
   # whole bibliography inside a draft (md/txt/bib/json), or stdin
   python skills/researchx/scripts/verify_citations.py draft.md --format md --out citation_audit.md
   python skills/researchx/scripts/verify_citations.py --doi 10.1016/j.rse.2024.114123
   python skills/researchx/scripts/verify_citations.py refs.bib --format json --offline
   ```

3. **Act on the verdicts**:

   | Verdict | Meaning | Required action |
   |---|---|---|
   | `VERIFIED` | Found in a registry, title+authors match | Cite normally |
   | `CORRECTED` | Found, but year/journal/DOI differs | Use the registry version; note the fix |
   | `NOT_FOUND` | No registry match (≠ fake: books, theses, very new or non-indexed venues) | Retitle as `[UNVERIFIED]`, downgrade claims that depend on it, or drop it |
   | `RETRACTED` | Registry flags a retraction/withdrawal | Remove, or cite explicitly as retracted with the notice DOI |
   | `ERROR` | Network/timeout | Retry once; if it still fails, fall back to `[UNVERIFIED]` and say the check could not run |

4. **Report the audit** in the output file, not just in chat: total references, verified count, corrected list, unverified list with the reason, retracted list.
5. **Write the AI-use disclosure** when the venue requires it (see `references/integrity-and-ethics.md`).

Full protocol, registry quirks and false-negative handling: `references/citation-verification.md`.

---

## 3. Modules (summary — full specs in `references/modules.md`)

### M1 · Paper Analysis
Input: PDF, DOI, arXiv ID or title. Output: `analysis_[short-title]_YYYYMMDD.md`.
Extract: one-sentence summary → research logic chain (RQ → data → method → experiment → result → conclusion) → why-this-approach reasoning → strengths/weaknesses table → missing experiments (use M4 checklist) → position against 2023-2026 SOTA → 3 actionable improvements. Verify the paper's own key references and flag any that do not resolve.

### M2 · Gap Mining & Topic Discovery
Input: domain/problem, optionally data and constraints. Output: `topics_[topic]_YYYYMMDD.md`.
Run ≥5 distinct queries (review, limitation, SOTA, adjacent-field, user's language), build a gap taxonomy (solved / unsolved / controversial / unexplored), then propose **5 topics**, each with: testable research question, novelty claim vs cited work, data, literature-backed methods, target journal, feasibility, risk of being scooped.
Never propose a topic whose novelty rests on literature you did not retrieve.

### M2b · Novelty Check (prior-art scan)
Input: a draft claim, title or idea. Output: `novelty_check_[topic]_YYYYMMDD.md`.
Decompose the idea into 3-6 claims; find the closest 5-10 prior works with `scripts/search_literature.py` + web search; for each claim return `novel` / `incremental` / `already published (cite)`. End with the sharpest defensible novelty statement and the reviewer objection it must survive.

### M3 · Method Mining
Input: topic or sub-problem. Output: `methods_[topic]_YYYYMMDD.md`.
Build method families from retrieved papers (not from memory), with reported performance and its source, evolution timeline, assumptions, compute/data cost, and failure modes. Then recommend a method for the user's sub-problem with three literature-grounded reasons, plus transfer opportunities from adjacent fields.

### M4 · Experiment Design
Input: proposed method + data. Output: `experiment_plan_[topic]_YYYYMMDD.md`.
Cover: baselines (3-5 recent SOTA, same data split), ablations, hyperparameter sensitivity, generalization (≥2: region/scenario/time), robustness (noise, missing data, imbalance), statistical rigor (≥5 seeds, mean ± std, paired significance test, effect size), compute budget, and a reproducibility checklist. Then run missing-experiment detection: list what a reviewer will ask that the design does not answer, with a completeness score N/10.

### M5 · Manuscript Writing
Input: plan or results. Output: `manuscript_[topic]_YYYYMMDD.md` (section-at-a-time by default).
Follow the target journal's structure and word budget (`references/journal-playbook.md`). Every methodological claim cites a verified source; every quantitative claim traces to the user's results or a cited paper. Deliver a per-section word count, a figure/table plan, and a reference list that already passed M11.

### M6 · Journal Fit & Upgrade
Input: draft or abstract. Output: `upgrade_plan_[paper]_YYYYMMDD.md`.
Score novelty / evidence / writing / related-work (each ★/5) against the target venue's bar, then produce a ranked action plan with expected reviewer impact. Recommend 3 venues with IF/quartile, scope fit, typical review time, APC, and desk-rejection risks. Give the single highest-leverage change first.

### M7 · Peer Review Simulation (adversarial)
Input: draft. Output: `review_report.md` + `response_letter.md`.
Three personas: domain expert, methodologist/statistician, and a hostile "Reviewer 2" looking for fatal flaws. For each comment: severity, evidence, and the cheapest sufficient fix. Include at least one comment that could cause rejection. Then write the point-by-point response letter with the exact manuscript change.

### M8 · Visuals & Figures
Input: topic/results. Output: prompts + diagram code, or figure specs.
Graphical abstract prompts for 3 platforms × 3 journal aesthetics, poster layout, Mermaid workflow/PRISMA/concept diagrams via `scripts/generate_visuals.py`, and figure specs (size in mm, DPI, min font size, colour-blind-safe palette). Warn when a requested visual would misrepresent the data.

### M9 · Literature / Systematic Review
Input: question + scope. Output: `literature_matrix_[topic]_YYYYMMDD.md`, and for systematic mode also `prisma_flow.md` + `screening_ledger.csv`.
Narrative mode: matrix of papers → thematic (not chronological) synthesis → explicit gap paragraph.
Systematic mode: protocol (question, PICO, inclusion/exclusion, date range), structured search, dedupe and screening with `scripts/prisma_screen.py`, PRISMA 2020 counts and flow diagram, risk-of-bias notes, and PRISMA-trAIce style AI-use disclosure. Report search strings and dates so it is reproducible.

### M10 · Grant Proposal
Input: funder + topic. Output: `grant_proposal_[topic]_YYYYMMDD.md`.
NSFC/国自然 or international structure: rationale (立项依据) → scientific questions → objectives → technical route (Mermaid) → innovation points → feasibility → expected outcomes → timeline/budget → risk mitigation. Every claim of "current state of the art" is cited; every objective has a measurable success criterion.

### M11 · Citation Audit (cross-cutting)
Input: draft, bibliography, BibTeX, or a single DOI. Output: `citation_audit_YYYYMMDD.md` + JSON.
See §2. Also check: in-text citations with no reference entry and vice versa, duplicate references, retracted sources, preprints cited as peer-reviewed, and citation-context mismatch (source does not support the claim it is attached to — read the abstract before clearing it).

### M12 · Reproducibility & Artifact Packaging
Input: study/experiment. Output: `reproducibility_package_[topic]_YYYYMMDD.md`.
Data & code availability statement, environment/version lock, seeds and hardware, hyperparameter table, run order, expected runtime, a `README` for the artifact, licence choice, and an artifact-evaluation checklist (what a reviewer must be able to reproduce in 30 minutes).

---

## 4. Bundled scripts

Run from the skill root. All are stdlib-only, non-interactive, accept `--help`, and print JSON or Markdown.

| Script | Purpose | Typical use |
|---|---|---|
| `scripts/verify_citations.py` | Verify refs against Crossref/OpenAlex/arXiv/doi.org; flags retractions | `python skills/researchx/scripts/verify_citations.py draft.md --format md` |
| `scripts/search_literature.py` | Structured literature search with year filters, dedupe, matrix output | `... --query "crop mapping foundation model" --from-year 2023 --limit 30` |
| `scripts/prisma_screen.py` | Dedupe, rule-based screen, PRISMA 2020 counts + flow diagram | `... --input hits.json --include "crop|yield" --exclude "review"` |
| `scripts/analyze_methods.py` | Method families, trends, gaps, innovation scoring from a paper set | `... --input papers.json --format md --out methods.md` |
| `scripts/generate_visuals.py` | Mermaid diagrams, graphical-abstract prompts, poster layout, figure spec | `... workflow --topic "X"` |

If a script fails: run it with `--help`, fix the input file, and only then fall back to doing the step manually — and say which path you took.

---

## 5. Reference files (load only what the task needs)

| File | Load when |
|---|---|
| `references/modules.md` | Running any module — full step-by-step specs, output schemas |
| `references/citation-verification.md` | Verifying references, handling `NOT_FOUND`, retractions, disclosures |
| `references/systematic-review-prisma.md` | M9 systematic mode, PRISMA counts, screening ledger |
| `references/search-queries.md` | Building search strings (databases, operators, filters) |
| `references/journal-playbook.md` | Choosing a venue, section-by-section writing conventions, response letters |
| `references/research-design.md` | Framing questions (FINER/PICO), study design, validity threats |
| `references/integrity-and-ethics.md` | AI-use disclosure, authorship, plagiarism/self-plagiarism, image integrity |
| `references/gotchas.md` | Something is behaving unexpectedly — known traps and fixes |
| `assets/*.md` | Output templates (topic brief, manuscript skeleton, review report, PRISMA flow, grant, artifact README) |

---

## 6. Workflows

**Q1 pipeline (vague idea → submittable draft)**
M2 gaps → user picks a topic → M2b novelty check → M3 methods → M4 experiments → M5 draft (section by section, user approves each) → M11 audit → M6 journal fit + upgrade → M7 adversarial review → revise → M8 visuals → M12 packaging.

**Analyze-and-improve (one paper)**
M1 analysis → M3 SOTA comparison → M4 missing experiments → M11 audit of its references → M6 upgrade plan.

**Systematic review**
Protocol → `search_literature.py` across registries → `prisma_screen.py` dedupe/screen → full-text screening log → matrix + synthesis → risk of bias → PRISMA flow → disclosure statement.

**Grant**
M2 landscape → M3 methods → M10 proposal → red-team the technical route → M11 verify all citations → budget/timeline.

**Multi-agent (when the platform supports subagents)**
Scout (retrieve) → Screener (include/exclude with reasons) → Extractor (structured fields) → Critic (adversarial review) → Writer (synthesis). Each agent returns artifacts, not prose summaries; the Critic must cite the record it objects to.

---

## 7. Quality gates

Before delivering, check every gate. Fix, or tell the user which gate failed and why.

| Gate | Test |
|---|---|
| Verifiable | Every reference is `VERIFIED`/`CORRECTED`, or tagged `[UNVERIFIED]` with a reason |
| Sourced | Every number is traceable to a retrieved record or the user's own results |
| Specific | No "several studies show"; name the study, the dataset, the metric |
| Critical | At least one honest limitation, threat to validity, or contrary finding |
| Actionable | Output ends with concrete next steps or a decision the user must make |
| Reproducible | Search strings, dates, filters and scripts used are recorded |
| Filed | Saved to a `.md`/`.json` file with the naming convention below, not chat-only |

Self-score 0-100 (`verified refs 30, specificity 20, critical review 15, actionability 15, reproducibility 10, clarity 10`) and report the score with the weakest component named.

**Anti-patterns — refuse these**: padding a reference list to look thorough; inventing a plausible DOI; silently dropping a citation that failed verification while keeping the claim; reporting a single-run result as a finding; writing a "gap" that the search never confirmed; copying a template abstract with the numbers left out.

---

## 8. Output conventions

- Files land in the working directory: `analysis_*.md`, `topics_*.md`, `methods_*.md`, `experiment_plan_*.md`, `manuscript_*.md`, `upgrade_plan_*.md`, `review_report.md`, `citation_audit_*.md`, `literature_matrix_*.md`, `prisma_flow.md`, `grant_proposal_*.md`, plus `.json` machine-readable sidecars where the module produces data.
- Use `YYYYMMDD` from the current date; keep the topic slug short and ASCII.
- Start each file with: purpose, inputs used (with search date), and the verification status summary.
- Cite as `Author (Year) — DOI`; if the user names a style (APA/IEEE/Elsevier/GB-T 7714), emit that style from verified metadata only.

---

## 9. Error recovery

| Situation | Do this |
|---|---|
| Web search returns nothing usable | Say so, try synonyms + the user's native language + registry search; if still empty, switch to labelled first-principles reasoning |
| Only old sources (<2022) exist | Report it as a signal (possibly underexplored), not as SOTA |
| `NOT_FOUND` on a real-looking paper | Try title-only and author-only lookups, strip formatting; still missing → `[UNVERIFIED]` + manual-check instruction |
| Registry rate-limits/offline | `--offline` from cache, or `--sleep`/`--mailto`; disclose that verification did not run |
| User asks for a fabricated citation | Refuse, offer the closest verified alternative |
| Data/statistics missing for a claim | Ask for the table/figure rather than estimating |
| Non-English paper | Search and cite in the original language; keep the original title with a translation in brackets |
| Script missing a dependency | Use only stdlib path; do not `pip install` without asking |

More: `references/gotchas.md`.

---

## 10. Handoff

End every task with: what was produced (file paths), the verification status (X/Y references verified), the weakest part, and one recommended next module from §1. Then ask: "Continue to [next module], or refine this output?"
