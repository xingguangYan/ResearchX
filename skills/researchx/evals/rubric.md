# Output rubric

Score any ResearchX deliverable 0-100. Below 70, do not ship it to the user without stating the failing
dimension.

| Dimension | Weight | 100 | 50 | 0 |
|---|---|---|---|---|
| Reference integrity | 30 | Every reference verified this session or labelled `[UNVERIFIED]` with a reason | Some references unverified but labelled | Any invented reference, DOI, author or year |
| Specificity | 20 | Names methods, datasets, metrics, numbers with sources | Some vague claims ("several studies") | Generic advice that fits any field |
| Critical review | 15 | Falsifiable weakness named; contrary evidence considered | Limitation mentioned in passing | Only strengths |
| Actionability | 15 | Ranked next steps with effort/impact | A list of options | No next steps |
| Reproducibility record | 10 | Queries, registries, date, scripts and filters recorded | Partial record | No provenance |
| Clarity | 10 | Structured, scannable, one message per section | Readable but dense | Wall of text |

## Automatic fails

- A reference that does not resolve and is not labelled.
- A number with no source and no "user-provided" marker.
- A claimed experiment that was not run.
- Fabricated peer-review responses.
- Any image presented as data that was generated.

## What "verified" means in the score

`verify_citations.py` returned `VERIFIED` or `CORRECTED` (and the corrected metadata was used), or a
human-checkable source was supplied by the user and marked as such. `PARTIAL`, `NOT_FOUND` and `ERROR`
do **not** count as verified.
