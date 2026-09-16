# Journal Playbook — writing, venue choice, revision

Covers: section templates, venue-fit assessment, submission strategy, reviewer response patterns.

---

## 1. Section templates

### Abstract
Structured (medical/Elsevier style):
```
Background: context + why it matters (1-2 sentences)
Objective:   the specific question (1 sentence)
Methods:     data, approach, validation (2-3 sentences)
Results:     key numbers, with uncertainty (1-2 sentences)
Conclusion:  what changes because of this (1 sentence)
```
Highlight style (Nature/Science): hook → gap → approach → key result → implication, one sentence each,
no citations, no undefined abbreviations.

Rules: no citation in the abstract; no number the paper does not support; the abstract must survive being
read alone (it is what 90% of readers see).

### Introduction funnel
1. Broad context (why the field matters).
2. Specific background (what is established — cite reviews, not ten primaries).
3. Gap (what is not known/solved — cite the papers that fail to solve it).
4. Approach (what you did and the key idea, one paragraph).
5. Contributions (3-5 numbered items, each falsifiable and specific).
6. Organisation (one sentence).

### Methods
```
Data → preprocessing → study area/population → proposed method (framework figure + module equations)
→ training/implementation (optimiser, loss, hyperparameters, hardware, seeds)
→ evaluation (baselines with justification, metrics with definitions, splits)
→ statistics (test, correction, number of runs)
```
Reproducibility minimum: dataset version, split strategy, code availability, environment.

### Results
Claim → evidence → interpretation, one paragraph per result. Main result first. Tables for quantitative
comparison (include the baseline's reported number *and* your re-run when they differ), figures for
qualitative. Every figure caption must state what to look for. Error bars defined in the caption.

### Discussion
Restate the finding (do not repeat the numbers) → compare with the literature and explain differences →
address unexpected results honestly → limitations (constructive, specific) → future work (what the next
paper should test).

### Conclusion
2-3 sentences of summary, contributions, one limitation, one outlook. No new citations.

---

## 2. Venue-fit assessment

Score the draft 1-5 on: novelty, evidence strength, scope match, method rigour, writing clarity.
Then match against the venue:

| Signal | What to check |
|---|---|
| Scope | Does the venue publish this *object of study*? Search its last 12 months of titles on your keywords. |
| Bar | Compare your contribution type with what it recently accepted (new method vs new application vs benchmark). |
| Format | Word/figure limits, structured vs unstructured abstract, reference style, mandatory sections (data availability, ethics, CRediT). |
| Speed | Typical time to first decision and to acceptance — report the source and date of the number. |
| Cost | APC / open-access requirements; waivers for low-income countries. |
| Risk | Desk-rejection triggers: out of scope, incremental, purely local datasets, SOTA-chasing without insight. |

Recommend three routes: an ambitious target, a strong fit, and a safe fallback — with the reason each
could say yes, and the reason each could desk-reject.

**Never invent metrics.** Impact factors, acceptance rates and review times change every year and differ by
source. Fetch them, cite the source and the year, or write `(verify)`.

---

## 3. Upgrade levers, ranked by expected reviewer impact

1. **Weak novelty** → reframe against the closest prior work with a measurable difference, or add the missing comparison; do not merely add adjectives.
2. **Incomplete baselines** → re-run at least two 2024-2026 SOTA methods on your split.
3. **Missing ablations** → one table removing each component; add a parameter-matched control.
4. **No generalisation** → one extra region/period/population; report the drop, not just the average.
5. **Weak statistics** → multiple seeds, paired test, effect size; report variance.
6. **Thin related work** → add the 5-8 papers a domain expert would expect, grouped thematically.
7. **Unclear writing** → tighten the abstract and the contribution list first; they carry the desk-review.
8. **Reproducibility gaps** → data/code availability + a 30-minute reproduction path.
9. **Figures** → one hero figure that states the contribution visually.

---

## 4. Review-response patterns

| Reviewer comment type | Useful opening | Then |
|---|---|---|
| Missing baseline | "We agree this comparison strengthens the paper." | run it, add the table, report honestly even if the baseline wins on one metric |
| Novelty doubt | "We thank the reviewer for the chance to sharpen the positioning." | one paragraph contrasting with the specific closest work, cite it |
| Statistical concern | "The reviewer is right that variance was under-reported." | multiple seeds, test, effect size, revised claims |
| Out-of-scope demand | "This is a valuable direction; it is a distinct study." | explain the boundary, add a limitations sentence, cite it as future work |
| Misunderstanding | "We apologise for the unclear phrasing." | rewrite the passage; quote the old and new text |
| Data request | "We have released the split files and code." | give the persistent link |

Response-letter rules: quote the comment, answer with substance (not "we thank the reviewer"), name the
exact revised location, keep it courteous, and never claim an experiment you did not run. If you disagree,
disagree with evidence — reviewers accept a well-argued "we chose X because Y" far more often than they
accept silence.

---

## 5. Common rejection causes (fix these before submitting)

- The contribution is stated only in the abstract, never demonstrated.
- The best baseline is an outdated version of the proposed method.
- The test set was used for model selection.
- Results without variance, or variance with no test.
- Claims of "first" that a reviewer can falsify with one citation.
- The paper's novelty depends on an unverified assumption about the literature.
- Figures unreadable at print size; tables with unexplained abbreviations.
- References that do not resolve (see `citation-verification.md`) — increasingly a desk-reject trigger.
