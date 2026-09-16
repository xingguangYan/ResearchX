# How ResearchX compares

The question that matters for a research assistant is not "can it write?" but **"can I check what it
wrote?"** ResearchX is built around that second question.

| Capability | General chat models | Reference managers (Zotero/Mendeley) | Commercial AI literature tools | **ResearchX** |
|---|---|---|---|---|
| Finds recent papers | model memory, often stale | ✗ | ✓ (their corpus) | ✓ OpenAlex + Crossref + arXiv + web |
| Citation verification | ✗ — fabricates plausible DOIs | stores, does not check | partial (own index) | ✓ 4 registries + retraction flags, verdicts per reference |
| Flags retracted work | ✗ | partial | rare | ✓ |
| Structured metadata (DOI, venue, citations) | ✗ | ✓ | ✓ | ✓ |
| Experiment / ablation / statistics design | generic advice | ✗ | ✗ | ✓ protocol + missing-experiment scan |
| Adversarial peer review + response letter | soft | ✗ | ✗ | ✓ 3 personas incl. hostile reviewer |
| Systematic review (PRISMA 2020) | ✗ | screening only | paid tiers | ✓ counts, flow, ledger, disclosure |
| Reproducibility record per output | ✗ | ✗ | partial | ✓ queries + registries + date in every file |
| Works offline / no keys / no account | n/a | ✓ | ✗ | ✓ cached, stdlib-only scripts |
| Portable across agents | one vendor | one app | one app | Claude Code, Codex, Cursor, Gemini CLI, Copilot CLI, Antigravity, MCP, plain files |
| Price | subscription | free/paid tiers | subscription | free, MIT |

## Where ResearchX is deliberately weaker

Honesty is part of the design, so:

- **It does not have a proprietary full-text corpus.** It relies on open registries plus web search; some
  paywalled work is visible only as metadata.
- **It cannot read a paywalled PDF you do not have access to.** Upload what you can legally read.
- **It does not do meta-analytic statistics** (pooled effect sizes, I²) automatically — it designs the
  protocol and reports the counts; the analysis is yours (or a stats tool's).
- **It will not tell you your paper is great.** Module M7 exists to find the fatal flaw before a reviewer
  does.
- **Verification is evidence, not proof.** A registry match is strong evidence a paper exists; it is not a
  judgement about the paper's quality.

## Why the citation layer is the differentiator

Fabricated references are the one AI failure that costs a researcher their submission. The literature on
this is consistent: AI-assisted manuscripts have been found with fabricated, chimeric and retracted
citations, and journals increasingly audit reference lists. A tool that cannot verify a reference should
not be allowed to write one.

ResearchX therefore does the verification **in code, against registries**, not by asking a model whether a
citation "looks right" — a model that hallucinated the reference will happily confirm it. The output of a
verification run is a file you can attach to your submission notes.
