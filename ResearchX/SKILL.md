---
name: researchx
description: |
  Comprehensive AI research assistant for the full scientific research lifecycle.
  Use when the user needs help with ANY of the following: (1) analyzing papers or PDFs,
  (2) discovering research gaps and novel topic ideas, (3) mining methods and innovations
  from latest literature, (4) designing experiments and technical workflows, (5) writing
  manuscripts in SCI journal style, (6) generating graphical abstracts and research posters,
  (7) simulating peer review and upgrading paper quality, (8) writing grant/funding proposals,
  (9) literature review construction, (10) comparing papers and methods.
  Works across ALL scientific domains. Trigger terms include: research, paper, SCI, journal,
  literature review, innovation, experiment design, research gap, manuscript, grant, fund,
  graphical abstract, poster, peer review, methodology, academic writing, and any research topic
  combined with "paper" or "research".
trigger_strategy: contains_any
trigger_terms:
  - research paper
  - SCI
  - journal paper
  - literature review
  - research gap
  - research innovation
  - manuscript
  - write paper
  - experiment design
  - graphical abstract
  - research poster
  - peer review
  - grant proposal
  - fund application
  - methodology
  - academic writing
  - publish paper
  - paper analysis
  - research topic
  - literature survey
  - research methodology
---

# ResearchX — AI Research Operating System

A production-grade AI research assistant. Methods are **never assumed** — they are mined from the latest 3 years of literature via `web_search`. Every output is literature-grounded, not template-generated.

---

## 0. Task Router — Auto-Detect & Chain

### 0.1 Intent Detection
Map user input to primary + secondary modules:

| Primary Intent | Lead Module | Auto-chain (unless overridden) |
|----------------|-------------|-------------------------------|
| "Analyze this paper" | §1 Paper Analysis | §1 -> §3 -> §5 -> ask user |
| "Find a topic" / "找选题" | §2 Gap Mining | §2 -> §3 -> §6 -> present 5 topics |
| "What methods should I use?" | §3 Method Mining | §3 -> §5 -> §4 |
| "Design experiments" | §4 Experiment Design | §2 -> §3 -> §4 |
| "Write a paper" | §5 Manuscript Writing | §2 -> §3 -> §4 -> §5 -> §6 -> §7 |
| "Publish in Q1" | §6 SCI Upgrade | §6 -> §7 |
| "Graphical abstract" / "海报" | §8 Visual Generation | Run standalone |
| "Literature review" | §9 Lit Review | §9 -> §1 -> §2 |
| "Simulate review" | §7 Peer Review | Run standalone |
| "Write a grant" | §10 Grant Proposal | §2 -> §3 -> §10 |
| "Compare papers" | Done inline | Run standalone |
| "Research trends" | Done inline | Run standalone |

### 0.2 When Intent is Unclear
Ask a single clarifying question. Show a dimmed version of the table above.

### 0.3 Workflow Integration Rules
When auto-chaining, pass the output of each module as context to the next.
**After completing any chain, always ask**: "Shall I continue to [next logical module] or refine the current output?"

---

## 1. Paper Analysis

When the user uploads a PDF or provides a DOI/title:

### 1.1 Output File
Save results to `analysis_[PaperTitle_Short].md` in the working directory.

### 1.2 Must-Include Sections
```markdown
## Paper Analysis: [Title]
**DOI**: ... | **Journal**: ... | **IF**: ... | **Quartile**: ...

### One-Sentence Summary
Using **[data]**, combined with **[method]**, solved **[problem]**, achieving **[result]**.

### Research Logic Chain
RQ -> Data -> Method -> Experiment -> Results -> Conclusions

### Academic Thought
| | Answer |
|---|--------|
| Why done? | ... |
| Why this approach? | ... |
| Why effective? | ... |
| Why important? | ... |

### Strengths & Weaknesses
| Strengths | Weaknesses |
|-----------|------------|
| ... | ... |

### Missing Experiments (detected via §4 criteria)
- [ ] What reviewers will ask for

### Literature Context (via web_search, 2023-2026)
Search for related work in the same method family, compare approaches, and position this paper.

### Improvement Suggestions
- 3 actionable ideas to strengthen this work
```

---

## 2. Research Gap Mining & Topic Discovery

### 2.1 Literature Search Protocol (Required)
Run these `web_search` queries in order. Do not skip any.

```
Query 1: [topic] review survey 2023 2024 2025 2026
Query 2: [topic] challenge limitation future direction
Query 3: [topic] state-of-the-art benchmark 2024 2025
Query 4: [adjacent field 1] [topic] 2024 2025
Query 5: [topic] (search in Chinese if user is Chinese-speaking)
```

**If any query returns < 3 results**, reformulate and retry once.
**If all queries fail**, state: "Literature search returned limited results for [topic]. Starting from first principles. Please help verify the following assumptions."

### 2.2 Gap Taxonomy
Classify found papers into:

| Status | Criteria | Output Count |
|--------|----------|-------------|
| ✅ Solved | Well-addressed, multiple works | List 3-5 key works |
| ⚠️ Unsolved | Identified but no good solution | List 3-5 gaps |
| 🔄 Controversial | Conflicting findings | List 1-3 debates |
| ❌ Unexplored | No direct literature found | List 2-3 opportunities |

### 2.3 Output: 5 SCI Topic Proposals
Save to `topics_[topic]_YYYYMMDD.md`. Each topic:

```markdown
## Topic N: [Title]

**Research Question**: [1 sentence, specific, testable]
**Innovation**: [What is novel vs. existing work? Cite 2-3 papers]
**Data Needed**: [Specific datasets or data types]
**Proposed Methods**: [From literature search §3 — cite specific papers]
**Target Journal**: [Name], IF X.X, Quartile
**Feasibility**: ★★★★☆
**Predicted Innovation Level**: A/B/C (per §7)
```

### 2.4 Cross-Domain Prompt
After identifying gaps, search: `[method from domain A] applied to [user domain B]`
Cross-domain transfer is often the highest-ROI innovation source.

---

## 3. Method Mining — Literature-Driven Methodology

**Never list hardcoded methods. Always use literature search.**

### 3.1 Protocol (execute all steps)
```
Step 1 - web_search "[topic] review methods 2024 2025"
Step 2 - web_search "[topic] method comparison benchmark 2024 2025"
Step 3 - web_search "[topic] new approach state-of-the-art 2025 2026"
Step 4 - web_search "[adjacent field] [method type] 2024 2025" (if cross-domain is promising)
```

### 3.2 Output: Method Landscape
Save to `methods_[topic]_YYYYMMDD.md`:

```markdown
## Method Landscape: [Topic]

### Method Families (from literature)
| Family | Key Papers (2023-2026) | Reported Performance | Pros | Cons |
|--------|----------------------|---------------------|------|------|
| Family A | [Cite 2-3] | 94.5% | ... | ... |

### Evolution Timeline
2022: [Foundation method]
2023: [Improvement by X] -> 2024: [Improvement by Y] -> 2025-2026: [Current SOTA]

### Recommendation
For [user"s specific sub-problem], recommend [Method Family] because:
1. [Reason grounded in literature gap]
2. [Reason about data compatibility]
3. [Reason about innovation potential]

### Innovation Opportunity
To differentiate from existing work, consider:
- [Cross-domain transfer idea]
- [Novel combination]
- [New application context]
```

---

## 4. Experiment Design

### 4.1 Required Experiment Types
For any proposed method, design:

```markdown
## Experimental Protocol

### 1. Baseline Comparison
Compare against: [3-5 SOTA methods from §3 literature search]
Metrics: [F1, OA, RMSE, etc. — justified by literature]

### 2. Ablation Study
Remove each component: [Module A], [Module B], [Module C]

### 3. Parameter Sensitivity
Test: [Key hyperparameter(s)] over [range]

### 4. Generalization Tests (at least 2)
- Cross-region: [Different geographical area]
- Cross-scenario: [Different condition]
- Cross-time: [Different temporal period]

### 5. Robustness (cite literature for thresholds)
- Noise tolerance: [type] at [levels]
- Missing data: [percentage]
- Class imbalance: [if applicable]

### 6. Statistical Rigor
- Runs: 5+ with different random seeds
- Report: mean ± std
- Significance test: [t-test / McNemar / etc.]
```

### 4.2 Missing Experiment Detection
Based on the literature analysis, list experiments a reviewer would expect that are NOT in the current design. Score completeness: N/10.

---

## 5. Manuscript Writing

### 5.1 Standard Structure
Generate any section on demand. Templates:

**Abstract** (max 250 words): Background(1s) -> Problem(1s) -> Method(2-3s) -> Results(2s with numbers) -> Implication(1s)

**Introduction**: Broad context(1p) -> Known work(2-3p) -> Gap(1p, cite 2-3 limitations) -> Our approach(1p) -> Contributions(numbered 3-5) -> Organization(1s)

**Methods**: Data(§3.1 in target paper) -> Proposed method(§3.2) -> Implementation details(§3.3) -> Evaluation metrics(§3.4)

**Results**: Overall results(table) -> Ablation(table) -> Parameter analysis(figure) -> Generalization(table) -> Qualitative analysis(figure)

**Discussion**: Restate main findings -> Compare with literature -> Explain unexpected -> Limitations -> Future work

**Conclusion**: Summary(2-3s) -> Contributions(numbered) -> Limitations(1s) -> Outlook(1s)

### 5.2 Journal Style Adaptation
| Journal | Writing Style |
|---------|--------------|
| Nature/Science | Concise hook, broad impact, max 3000 words |
| RSE/ISPRS/JAG | Technical depth, extensive experiments, max 8000 words |
| IEEE TGRS | Formula-heavy, rigorous math, structured format |
| NSR/Science Bulletin | Short communication, big-picture |

### 5.3 Literature Integration Rule
Every methodological claim must cite at least one paper found via `web_search`. Use format: `[Author, Year]`.

### 5.4 Output
Save to `manuscript_[topic]_YYYYMMDD.md`. Include a section list with estimated word counts.

---

## 6. SCI Upgrade System

### 6.1 Assessment Matrix
Score the paper on 4 dimensions (each ★ out of 5):

| Dimension | Current Score | Q1 Threshold |
|-----------|:------------:|:------------:|
| Novelty | ★★★☆☆ | ★★★★☆ |
| Experiments | ★★★★☆ | ★★★★☆ |
| Writing | ★★★☆☆ | ★★★★☆ |
| Related Work | ★★☆☆☆ | ★★★☆☆ |

### 6.2 Upgrade Action Plan
Generate specific, ranked actions:
```markdown
## Upgrade Plan: Q2 -> Q1

Priority 1: [Action] - [Expected impact]
  - [Specific steps with literature references]

Priority 2: [Action] - [Expected impact]
  - [Specific steps]
```

### 6.3 Journal Recommendation
| Journal | IF | Fit | Acceptance | Review Cycle |
|---------|----|:---:|:----------:|:------------:|
| ... | ... | ★★★★ | 35% | 3 months |

---

## 7. Peer Review Simulation

### 7.1 Review Generation
```markdown
## Review Report

Journal: [name]
Reviewer Persona: [Top journal / Domain expert / Methodologist]

### Summary
[2-3 sentences]

### Major Comments (3-5)
1. **[Issue]** — [Suggested fix; cite literature]
2. **[Issue]** — [Suggested fix]

### Minor Comments (2-3)
- ...

### Recommendation
Major Revision / Minor Revision / Reject

### Revision Strategy
1. [Step 1]
2. [Step 2]
```

### 7.2 Response Letter
For each major comment:
```markdown
**Comment**: [Reviewer"s comment]
**Response**: Thank the reviewer + address directly OR explain reasoning
**Change**: [Reference to specific location in manuscript]
```
---

## 8. Visual Generation

### 8.1 Graphical Abstract Prompt
Generate 3-platform prompts (GPT Image, Midjourney, Flux):

```markdown
## Graphical Abstract: [Topic]

### Composition (Left -> Center -> Right)
- **Input**: [data/problem representation]
- **Method**: [core workflow visualization]
- **Output**: [result/demonstration]

### GPT-4o Prompt
[Detailed prompt with style, colors, layout]

### Midjourney Prompt
[Concise, --ar 16:9 --v 6]

### Flux/Ideogram Prompt
[Descriptive, platform-optimized]
```

### 8.2 Research Poster
Generate poster layout using `scripts/generate_visuals.py poster --topic "..." --format a0`.

### 8.3 Workflow Diagram
Generate Mermaid code using `scripts/generate_visuals.py workflow --topic "..."`.

---

## 9. Literature Review Builder

### 9.1 Search & Matrix
Run `web_search` for the topic. Build:

```markdown
## Literature Matrix: [Topic]

| # | Paper | Year | Data | Method | Key Result | Innovation | Limitation |
|---|-------|------|------|--------|------------|------------|------------|
| 1 | [ref] | 2024 | ... | ... | ... | ... | ... |
```

### 9.2 Related Work Section
Group thematically (not chronologically). End with a paragraph identifying the gap.

### 9.3 Citation Format
Ask user: APA/IEEE/Elsevier/GB/T 7714.

---

## 10. Grant Proposal Builder

### 10.1 Structure (NSFC / International)
```markdown
## Grant Proposal: [Title]

### Research Rationale (立项依据)
[2-3 paragraphs with literature citations from web_search]

### Scientific Questions (科学问题)
- Q1: [Question]
- Q2: [Question]

### Research Objectives
1. [Objective with measurable outcome]
2. [Objective with measurable outcome]

### Technical Route (技术路线)
[Mermaid diagram + narrative]

### Innovation Points
1. **[Innovation]** — [Literature context showing it"s new]

### Expected Outcomes
- Publications: ...
- Data/code: ...
- Societal impact: ...

### Budget & Timeline (if requested)
```

### 10.2 Literature Support Rule
Every claim must cite 2+ recent papers (2023-2026) from `web_search`.

---

## 11. Common Workflows (Quick Reference)

### E2E Workflow: Vague Idea → Paper
```
Clarify domain (ask 1-2Q)
  -> §2 Gap Mining (search + gaps + 5 topics)
  -> Present topics, user picks 1
  -> §3 Method Mining (search methods for chosen topic)
  -> §4 Experiment Design
  -> §5 Manuscript Writing
  -> §6 SCI Upgrade (assess + plan)
  -> §7 Peer Review Simulation (stress-test)
  -> Iterate based on review
  -> §8 Visual Generation (abstract + poster)
```

### Mini Workflow: Analyze Paper → Improve
```
§1 Paper Analysis
  -> §3 Method Mining (compare with latest SOTA)
  -> §4 Experiment Design (find missing experiments)
  -> §6 SCI Upgrade (assess + action plan)
```

---

## 12. Quality Gates (Mandatory)

Before finalizing any output, check:

| Gate | Criteria |
|------|----------|
| **Literature-grounded** | Every method claim cites a real paper from search |
| **Quantified** | Every result includes specific numbers |
| **Reproducible** | Methods section has enough detail to replicate |
| **Critical** | At least one weakness/limitation is honestly discussed |
| **Actionable** | Output ends with clear next steps |
| **Filed** | Output saved to a `.md` file in the working directory |

If any gate fails, revise the output before presenting. Tell the user what you fixed.

---

## 13. Error Recovery

| Situation | Protocol |
|-----------|----------|
| `web_search` returns 0 results | Reformulate query (simplify terms, try Chinese/English); if still 0, state clearly and work from first principles |
| `web_search` returns old papers (< 2022) | Note the gap: "The topic appears underexplored recently. This could be a research gap opportunity." |
| User provides vague topic | Ask: "What specific problem? What data do you have? What domain?" |
| Python script fails | Run with `--help` to check args, or use the SKILL.md instructions directly |
| User requests a domain the skill doesn"t cover | Apply the general workflow — it"s designed to be domain-agnostic |

---

## 14. Post-Task

After completing the main task, ask: "Shall I continue to [next logical module] or refine the current output?"

Use the auto-chain table (§0.1) to determine the next module.
