# Launch kit

Copy-paste material for sharing ResearchX. Edit the voice to match yours; keep the claims accurate.

---

## One-liner

> ResearchX: an agent skill that runs the research lifecycle — gap mining, methods, experiments,
> manuscripts, PRISMA reviews, grants — and verifies every citation against Crossref/OpenAlex/arXiv
> before it reaches you.

## Short post (X / Mastodon / LinkedIn)

> Most AI research assistants can write a paragraph. Almost none can prove it.
>
> ResearchX verifies every reference against Crossref, OpenAlex and arXiv before writing it, flags
> retractions, and labels anything it cannot verify as [UNVERIFIED] instead of inventing a DOI.
>
> One command to install in Claude Code:
> `/plugin marketplace add xingguangYan/ResearchX`
>
> 12 modules: gaps → methods → experiments → manuscript → peer review → submission, plus PRISMA 2020
> systematic reviews and NSFC-style grants. Free, MIT, stdlib-only, no API keys.
>
> github.com/xingguangYan/ResearchX

## Hacker News / Reddit (r/PhD, r/MachineLearning, r/academia)

**Title**: ResearchX – a research assistant that verifies every citation before writing it

> I kept seeing the same failure: an LLM writes a beautiful literature paragraph with references that
> resolve to nothing, and the researcher only finds out when a reviewer or editor checks.
>
> ResearchX is a skill (SKILL.md + stdlib Python tools) for the full research loop. The part I care about
> is the citation layer:
>
> - `verify_citations.py draft.md` checks every reference against Crossref, OpenAlex, arXiv and the DOI
>   handle service, returns VERIFIED / CORRECTED / PARTIAL / NOT_FOUND / RETRACTED / ERROR, and flags
>   retractions.
> - It never claims a reference is fake. `NOT_FOUND` means "not verified" — books, theses and brand-new
>   papers legitimately fail — so the agent labels them [UNVERIFIED] and downgrades the claim.
> - The audit is a file you can keep (`citation_audit.md`), so you can re-run it after revisions.
>
> The rest is the usual lifecycle: gap mining from real registries, method landscapes with the dataset
> each number came from, experiment/ablation design with a missing-experiment scan, manuscript writing,
> an adversarial 3-persona peer review, PRISMA 2020 systematic reviews (counts, flow, ledger, AI-use
> disclosure), figures, and NSFC-style grant drafting.
>
> Install: `/plugin marketplace add xingguangYan/ResearchX` (also Codex, Cursor, Gemini CLI, Copilot CLI,
> Antigravity, MCP). MIT. Happy to hear where the verification logic is wrong — that is the part worth
> attacking.

## Awesome-list submission block

```markdown
- [ResearchX](https://github.com/xingguangYan/ResearchX) — Research lifecycle skill (gap mining, methods,
  experiments, manuscripts, peer review, PRISMA systematic reviews, grants) with a citation-integrity
  layer: every reference verified against Crossref/OpenAlex/arXiv, retractions flagged, unverifiable
  references labelled instead of invented. Stdlib-only tools, MIT.
```

## Demo script (record a 60-second GIF)

```bash
# 1. install
/plugin marketplace add xingguangYan/ResearchX && /plugin install researchx@researchx

# 2. ask
"Find a research gap in crop mapping with foundation models and give me five topics."

# 3. the moment that sells it
python skills/researchx/scripts/verify_citations.py draft.md --format md
#   → 34 references | 31 verified | 2 corrected | 1 unverified | 0 retracted

# 4. show the correction
#   "Chen 2022" → registry says 2024, DOI 10.1016/j.rse.2024.114123
```

## What to ask people to do

1. Try the verifier on a draft you already have: `verify_citations.py yourpaper.md`.
2. Report wrong verdicts as issues — those become test fixtures.
3. Star the repo if it caught something. ⭐

## Launch checklist

- [ ] Push the release and confirm CI is green.
- [ ] Verify each install one-liner on a clean machine (Claude Code, Codex, Cursor, Gemini CLI).
- [ ] Post the demo, link the docs.
- [ ] Submit to curated lists (awesome-claude-skills, awesome-claude-code, awesome-agent-skills, AI4Science lists).
- [ ] Add topics/repo description (already: `agent-skills`, `research`, `citation-verification`, `prisma`).
- [ ] Open good-first-issue labels for contributors.
- [ ] Reply to every report of a wrong verdict within 48 h and turn it into a fixture.
