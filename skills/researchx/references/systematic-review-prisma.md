# Systematic Reviews, PRISMA 2020 and Reproducible Screening

Use when the user asks for a systematic review, meta-analysis, evidence synthesis, "综述" with a protocol,
or a literature review that must withstand scrutiny (thesis chapter, grant rationale, journal review
article). PRISMA 2020 is the reporting standard; PRISMA-trAIce extends it to AI-assisted workflows.

---

## 1. Protocol first (before any screening)

Write and freeze:

1. **Question** in PICO/PICOS form — Population, Intervention/Exposure, Comparator, Outcome, Study design.
2. **Eligibility criteria** — inclusion and exclusion, written as rules that can be applied to a title/abstract (year window, language, study design, data type, minimum sample, peer-review status).
3. **Information sources** — which registries, which query strings, which date of search.
4. **Screening process** — who screens, how many screeners, how disagreements are resolved, what counts as "maybe".
5. **Data extraction fields** — the columns you will fill for each included study.
6. **Risk-of-bias tool** — choose per design (e.g. RoB 2 for RCTs, ROBINS-I for non-randomised, QUADAS-2 for diagnostics, JBI/NOS for observational, or a domain-appropriate checklist).
7. **Synthesis plan** — narrative, or meta-analysis with model choice and heterogeneity measure (I²).
8. **Deviations log** — where you will record post-hoc changes. Deviating is allowed; hiding it is not.

The protocol is the deliverable that makes everything after it reproducible. If the user has no protocol,
produce one before searching (or at least before screening).

---

## 2. Pipeline with the bundled scripts

```bash
# 1. retrieve (repeat per query; keep the JSON)
python skills/researchx/scripts/search_literature.py \
  --query "crop mapping deep learning" --query "crop type transfer learning" \
  --from-year 2015 --limit 50 --format json --out hits_all.json

# 2. dedupe + rule-based screen + PRISMA counts + flow diagram + ledger
python skills/researchx/scripts/prisma_screen.py \
  --input hits_all.json \
  --include "crop|agricultur|yield" --exclude "review|editorial|comment" \
  --from-year 2015 --type article \
  --out-prefix review1

# 3. record your eligibility decisions (human stage) and regenerate counts
python skills/researchx/scripts/prisma_screen.py --input hits_all.json \
  --include "crop" --exclude "review" --decisions decisions.json --out-prefix review1
```

Outputs: `review1_flow.md` (Mermaid + counts), `review1_ledger.csv` (every record with stage, decision,
reason), `review1_counts.json`, `review1_included.json`.

The ledger is the audit trail: every record is either included or excluded **with a reason**. Regenerate
the flow after every change instead of hand-counting.

---

## 3. PRISMA 2020 checklist (what a complete report contains)

**Title / abstract**
- [ ] Identify the report as a systematic review (and meta-analysis if applicable)
- [ ] Structured abstract with eligibility criteria, sources, risk of bias, synthesis method, results, limitations, registration

**Introduction**
- [ ] Rationale in terms of what is already known
- [ ] Explicit objectives / review question

**Methods**
- [ ] Eligibility criteria with rationale
- [ ] Information sources + date of last search for each
- [ ] Full search strategies for at least one database (and enough for all)
- [ ] Selection process (screening levels, number of reviewers, automation used, disagreement resolution)
- [ ] Data collection process and extraction form
- [ ] Data items (variables, assumptions)
- [ ] Risk-of-bias assessment method and how it fed the synthesis
- [ ] Effect measures (or the qualitative equivalent)
- [ ] Synthesis method (narrative structure, meta-analytic model, heterogeneity, software)
- [ ] Reporting-bias assessment (funnel plot, Egger's, or a reason it was not possible)
- [ ] Certainty assessment (e.g. GRADE) if applicable
- [ ] Registration (PROSPERO/OSF number) or a statement that the review was not registered
- [ ] Protocol availability and amendments
- [ ] Funding / competing interests

**Results**
- [ ] Study selection flow (the PRISMA diagram) with reasons for exclusion
- [ ] Study characteristics table
- [ ] Risk-of-bias judgements per study
- [ ] Individual study results (with uncertainty)
- [ ] Synthesised results (with precision/heterogeneity)
- [ ] Reporting-bias findings
- [ ] Certainty of evidence

**Discussion**
- [ ] Interpretation in context of other evidence
- [ ] Limitations of the evidence and of the review process
- [ ] Implications for practice/policy/research

**Other**
- [ ] Support/registration details, competing interests, availability of data/code/other materials

---

## 4. Screening discipline

- Screen on **title + abstract**, never title alone; then full text for eligibility.
- Two independent screeners for at least a 10% sample; report agreement (e.g. Cohen's κ) when it matters.
- Log the reason at the moment of the decision, in the ledger — reasons recalled afterwards are unreliable.
- "Maybe" is a category: it goes to full-text review, never silently to inclusion.
- Pre-register or at least timestamp the criteria; criteria that drift late in the process must be reported as deviations.
- Keep the raw hit list and the ledger; they are the evidence that the review was reproducible.

---

## 5. Risk of bias / quality appraisal (narrative shortcuts)

| Design | Look for |
|---|---|
| Randomised | randomisation, allocation concealment, blinding, attrition, selective reporting |
| Non-randomised | confounding, recruitment, outcome definition, follow-up completeness |
| Diagnostic accuracy | patient selection, index test, reference standard, flow/timing |
| Modelling / ML studies | data leakage, split independence, tuning on test, seed variance, external validation, code availability |
| Observational/ecological | sampling frame, spatial autocorrelation, temporal confounding, scale mismatch |

Report per study, then summarise (low / some concerns / high). Never average quality into a single number
without saying what it means.

---

## 6. AI-assisted review (PRISMA-trAIce style disclosure)

If any stage used AI assistance, report it:

- which stages (search string generation, deduplication, title/abstract screening, data extraction, synthesis drafting);
- the tool/model and version, plus the date;
- how many records the automated step processed;
- how humans verified it (e.g. full double-screening of automated inclusions and a random 10% of exclusions);
- which decisions remained fully human (final eligibility, risk-of-bias judgement, conclusions).

Never let the tool be an author. State that the authors take responsibility for the content.

---

## 7. Synthesis notes

- Group thematically (by mechanism, population, method family), not chronologically.
- For each group: what is agreed, what conflicts, what explains the conflict (data, design, scale).
- Quantify when possible: effect ranges, not adjectives.
- Present counter-evidence explicitly — a review that only confirms is a review that will be rejected.
- End with the gap paragraph: what no included study addressed, why that matters, what study would settle it.
