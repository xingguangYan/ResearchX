# Research Integrity & Ethics — Practical Checks

Applies to every module that produces a claim, a figure, or an author list. Policies change; when a
decision matters (submission, funding), read the target venue's *current* guidelines rather than relying
on this file.

---

## 1. Authorship

- Authorship requires substantial contribution, drafting or critical revision, final approval, and
  accountability for the work (ICMJE and equivalent). Ordering conventions differ by field — confirm early.
- Guest, gift and ghost authorship are misconduct. So is listing a supervisor who did not contribute, or
  omitting a contributor who did.
- AI tools cannot be authors: they cannot take responsibility, consent, or be accountable.
- Agree authorship, data ownership and submission strategy **at the start** of a project; revisiting it at
  submission is where disputes come from.
- For large collaborations, use a contributorship statement (CRediT roles) rather than a vague "all
  authors contributed equally".

---

## 2. Text and image integrity

- **Plagiarism**: verbatim reuse without quotation and citation — including from your own previous work
  (self-plagiarism) and including machine-generated prose that closely paraphrases a source.
- **Paraphrasing is not laundering**: rewriting a sentence while keeping its structure and claim still
  requires citation.
- **Image integrity**: no selective enhancement, no spliced lanes, no duplicated panels presented as
  different conditions, no changed brightness across a comparison. Keep raw files; report processing steps
  (e.g. "contrast adjusted linearly across the whole image").
- **Figure honesty**: axes start where they should, error bars defined, no truncated bar charts for small
  differences, no 3D effects on 2D data, colour ramps perceptually uniform.
- **Data**: no selective deletion of inconvenient points without disclosure; outlier handling stated;
  exclusion criteria pre-specified.

---

## 3. AI use disclosure

Different publishers differ, and policies have been revised repeatedly. Check the venue and funder before
writing the statement. General patterns:

- **Assistance that must usually be disclosed**: text generation, translation, image generation, code
  generation, literature screening, data analysis steps performed by a tool.
- **Placement**: methods section, acknowledgements, or a dedicated declaration, per venue instructions.
- **Content**: tool name and version, purpose, extent of use, and human verification.
- **Never**: presenting AI-generated text as human-written against venue rules; using AI to generate
  References; using AI to produce images that look like primary data.

Working statement pattern:

> During the preparation of this work the authors used [tool, version] for [literature retrieval support /
> language editing / code drafting]. All references were verified against Crossref and OpenAlex; all
> analysis, interpretation and conclusions were produced and reviewed by the authors, who take full
> responsibility for the content of the publication.

For evidence syntheses, add the PRISMA-trAIce style stage-level reporting
(`systematic-review-prisma.md` §6).

---

## 4. Data, code and materials

- Publish the split files, code and hyperparameters; "available upon request" is increasingly refused.
- State licences for reused datasets and respect their terms (some forbid redistribution).
- For human data: consent, anonymisation, ethics approval number, data-management plan, and the jurisdiction's rules (GDPR/HIPAA/当地伦理委员会).
- Keep a data dictionary and a version tag; unpublished intermediate data is where reproducibility dies.
- Cite datasets and software with their DOI — they are research outputs.

---

## 5. Conflicts, funding and reporting bias

- Declare funding, employment, patents, advisory roles and personal relationships that a reader could
  reasonably see as influencing the work.
- Report negative and null results when you can; suppressing them distorts the literature for everyone.
- Do not cite a paper as support when its findings contradict yours; cite it and explain the difference.
- Register trials, reviews and pre-registered analyses before data collection where the field expects it.

---

## 6. Ethics of the research assistant itself

- Never fabricate a citation, a number, a dataset, a result, or a quotation.
- Never present a preprint as peer-reviewed, or a model's output as evidence.
- Never write a fabricated peer-review response claiming work that was not done.
- Never provide guidance that helps bypass ethics review, plagiarism detection, or journal policy.
- When the user asks for something that crosses these lines, refuse, explain the specific risk, and offer
  the legitimate alternative (e.g. "I can't invent that reference; here are three verified papers on the
  same claim").
- Flag suspected misconduct you encounter in a user's draft (image duplication, improbable statistics,
  unverifiable references) as a factual observation, without accusation.

---

## 7. Predatory venues and integrity signals

Warning signs in a venue or a paper: promises of rapid review for a fee, fake or unverifiable editorial
boards, near-identical scopes across many journals, aggressive solicitation emails, DOIs that do not
resolve, missing ethics statements where required, citation rings, and papers whose reference lists do not
survive `verify_citations.py`. Check a journal's indexing (DOAJ, Web of Science, Scopus) before
recommending it as a target.
