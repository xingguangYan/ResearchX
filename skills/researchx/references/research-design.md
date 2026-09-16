# Research Design Reference

Framing questions, choosing designs, controlling validity threats, sizing studies.

---

## 1. Framing the question

**FINER** — is it Feasible (data, time, skills, ethics), Interesting, Novel (confirmed by retrieval, not
by feeling), Ethical, Relevant (to the field and to someone outside it)?

**PICO / PICOS** — Population, Intervention/Exposure, Comparator, Outcome, Study design. Write the
question in one sentence using the five slots; if a slot is empty, the design is not yet specified.

**Good research questions share three properties**: they name the object and the setting; the answer could
be "no"; and the answer changes a decision someone would otherwise make.

Turn a vague interest into a question:
1. What is measured? (variable, unit, threshold)
2. On what population/data/setting?
3. Compared with what?
4. Under what conditions would the answer be surprising?

---

## 2. Matching design to question

| Question type | Design | Watch out for |
|---|---|---|
| Does X cause Y? | experiment, RCT, controlled manipulation | randomisation, blinding, attrition |
| How does X change over time? | longitudinal, time series | seasonality, drift, censoring |
| How are X and Y associated? | observational, cross-sectional | confounding, reverse causality |
| Does method M beat baseline B? | benchmark comparison, re-run both | split leakage, tuning on test, seed variance |
| What does the literature say? | systematic review, meta-analysis | publication bias, screening reproducibility |
| Can a model generalise? | external validation, out-of-domain tests | site/time/population shift not tested |
| Is this feasible? | pilot, spike, simulation | over-reading a small pilot |

---

## 3. Validity threats (name them, then mitigate)

| Threat | Example | Mitigation |
|---|---|---|
| Confounding | seasonality explaining yield instead of the feature | control variables, stratification, design |
| Selection bias | training on accessible sites only | probability sampling, documented inclusion criteria |
| Measurement bias | reference labels produced by the model under test | independent reference data + accuracy report |
| Data leakage | normalisation fitted on the full dataset; overlapping tiles between splits | split first, fit on training only, spatial/temporal blocking |
| Overfitting | tuned until the test set agreed | validation split, pre-registered selection rule |
| Multiple comparisons | 40 configurations, best reported | correction, pre-registered primary outcome |
| Seed variance | one run reported as the result | ≥5 seeds, mean ± std, paired tests |
| Scale mismatch | conclusions at 10 m applied to policy at 1 km | discuss scale explicitly |
| Publication bias | only positive results retrieved | search grey literature, negative results, funnel check |
| Construct validity | proxy metric does not measure the goal | justify the metric or measure the real outcome |

---

## 4. Sample size and precision

- For comparative studies, report the effect size you can detect (power ≥ 0.8 is the usual bar) and say what
  the study is powered for. Underpowered studies produce unstable rankings.
- For machine learning: seeds, split sizes, and the class balance of the evaluation set matter more than a
  power calculation; report variance and the minimum class support.
- For reviews: report the number of records screened and included; do not claim comprehensiveness you did
  not test with recall checks.
- Small-n pilots are for feasibility, never for effect claims — say so in the output.

---

## 5. From question to plan (checklist)

- [ ] Question in one sentence with PICO elements
- [ ] Data identified: source, licence, access, sample size, time span
- [ ] Baselines and metrics chosen with a citation for their standard use
- [ ] Split strategy fixed *before* modelling (and released as files)
- [ ] Primary outcome and analysis pre-specified; secondary analyses labelled as such
- [ ] Confounders / validity threats listed with mitigations
- [ ] Ethics, consent, and data-protection requirements checked
- [ ] Failure plan: what result would make you abandon or pivot
- [ ] Pre-registration where the field expects it (OSF, PROSPERO, clinical trial registry)
- [ ] Authorship and data-sharing expectations agreed at the start

---

## 6. Diagnosing weak study designs (fast triage)

| Symptom in the draft | Likely problem | Fix |
|---|---|---|
| "We compare with state-of-the-art methods" but no source version | baseline obsolescence | re-run current baselines with code |
| Test set used for early stopping | leakage | carve a third split |
| One region, one year | external validity | add a region/period |
| Metrics only aggregate (overall accuracy) | hides failure | per-class metrics, confusion analysis |
| "Significant improvement" with no test | statistics | paired test + effect size + seeds |
| Novelty resting on an unverified literature claim | verification | run `verify_citations.py` and a prior-art scan |
| Review of "the literature" with no query log | reproducibility | record strings, dates, registries |
