# Gotchas — traps that break research deliverables

Environment-specific and easily-missed facts. Read this when something behaves unexpectedly, or before
promising a deliverable.

---

## Retrieval

1. **`NOT_FOUND` is not "fake".** Books, theses, standards, very recent papers, non-English regional
   journals and non-DOI proceedings legitimately fail. Say "could not verify", never "fabricated".
2. **Crossref lag** — a paper published last week may already have a DOI that Crossref has not ingested.
   Try OpenAlex (which often indexes faster) and the publisher page.
3. **DOI resolves ≠ correct paper.** A chimera citation has a working DOI attached to invented metadata.
   Always compare title and authors.
4. **`--offline` silently returns ERROR for uncached queries.** If you pass `--offline`, say that
   verification did not run — do not present the result as a clean audit.
5. **Rate limits look like network errors.** Add `--mailto` and `--sleep 0.5`, and retry before concluding
   anything. Both APIs are generous when you identify yourself.
6. **OpenAlex title search returns near-duplicates** (preprint + published version). Dedupe by DOI and
   prefer the published version, but keep the preprint if it is the only accessible one.
7. **Google-Scholar-only references** are suspect but not automatically fake: check whether the linked
   source is real before including it. High recall, low precision.
8. **Year filters hide solved problems.** Before claiming "nobody has done this", drop the year filter —
   the work may exist and simply be old.

## Screening and reviews

9. **Dedupe before screening** or every PRISMA count downstream is wrong.
10. **Screening on titles alone** systematically excludes papers whose contribution is in the abstract.
11. **Reasons recorded from memory** are not reproducible. Write the reason into the ledger at decision time.
12. **Protocol drift** (criteria changed mid-review) must be reported as a deviation, not quietly applied.
13. **"Included" ≠ "supports my claim"** — record direction of the effect, including contrary findings.

## Writing

14. **Numbers must trace to an artifact.** If a result table was not provided, ask for it; do not infer it
    from a figure caption.
15. **Comparisons across datasets are invalid.** A 95% F1 on dataset A does not beat 93% on dataset B.
16. **Preprint ≠ peer-reviewed.** Mark venue type for every reference: journal / conference / preprint /
    report / thesis.
17. **Impact factors, acceptance rates and review times drift** and vary by source. Cite the source and
    year, or write `(verify)`.
18. **Abstract-only summaries miss the method's limits.** Read results and limitations before judging.
19. **"State of the art" moves.** SOTA from 2022 is a baseline, not a novelty argument, in 2026.
20. **Self-citation padding** is visible to reviewers; cite the field, not yourself.

## Statistics

21. **Single-run results are not findings.** Seeds, folds, or repeats — with variance reported.
22. **Tuning on the test set** is the most common fatal flaw in ML papers; check the split first.
23. **Multiple comparisons** inflate false positives; correct or pre-specify.
24. **Correlation language**: "associated with" unless the design supports causation.
25. **p < 0.05 alone** is not evidence of importance — report the effect size and interval.

## Figures and visuals

26. **Colour ramps** must be perceptually uniform and colour-blind safe (viridis/magma-like); avoid
    red-green pairs.
27. **Font sizes below ~7 pt at final print size** are unreadable; check after scaling to 85 mm or 170 mm.
28. **Graphical abstracts** must not imply results that the paper does not show. No invented numbers, no
    fake micrographs, no implied causation.
29. **Mermaid renders differently across platforms** — keep node labels short and avoid unescaped quotes.

## Tools in this skill

30. **Run scripts from the skill root** (or use the full path) so `rx_common` imports work.
31. **`--format json` goes to stdout** unless `--out` is given; progress lines go to stderr, so piping is safe.
32. **Exit codes**: `verify_citations.py` returns 1 with `--fail-on-unverified`, and 3 when every lookup
    failed (offline). `search_literature.py` returns 3 when nothing was retrievable — treat that as data
    ("no results"), not as a crash.
33. **Cache is per-directory** (`.researchx-cache`). Delete it if metadata changes upstream and you need a
    fresh pull.
34. **Scanned PDFs** need OCR before text extraction; if extraction returns gibberish, say so instead of
    guessing at the content.

## Collaboration

35. **Never promise an experiment the user has not run.** Write it as a plan item.
36. **Never silently drop a citation that failed verification** while keeping the sentence it supported.
37. **Disclose the AI's role** when the venue requires it (see `integrity-and-ethics.md`).
38. **Ask for the target journal early** — style, structure and word budget differ enough to matter before
    writing rather than after.
39. **Non-English sources**: keep the original title, add a bracketed translation, and state the language.
40. **When the user's claim is wrong**, say so with the evidence and offer the defensible version of the
    claim. Agreement is not assistance.
