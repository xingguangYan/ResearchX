# Security & Safety

## Reporting
Open a private security advisory (`Security → Report a vulnerability`) or an issue if the report is not
sensitive. We aim to respond within 7 days.

## What this project runs
ResearchX is text (SKILL.md + references + templates) plus five Python scripts. The scripts:

- use **only the Python standard library** (no `pip install` required),
- make network requests **only** to `api.crossref.org`, `api.openalex.org`, `export.arxiv.org`, and
  `doi.org` (the handle API), and only when you run a command that needs them,
- write only inside the paths you pass (`--out`, `--cache-dir`, `--out-prefix`),
- never execute code from the documents you feed them,
- support `--offline` so no network traffic happens at all.

Treat document text as untrusted input: a malicious draft could contain instructions aimed at the agent
(prompt injection). ResearchX instructs the agent to treat retrieved content as data, never as commands.

## Verifying before you install
```bash
git clone https://github.com/xingguangYan/ResearchX && cd ResearchX
python tests/validate_skill.py --strict     # spec + hygiene checks
python -m pytest tests -q                   # scripts vs recorded registry fixtures, no network
grep -rn "urllib.request" skills/researchx/scripts   # see every outbound endpoint
```

## Scope
The security surface is the scripts and the instructions. Anything an LLM does with a paper's content is
outside this repository's control — verify outputs, especially references (that is what
`verify_citations.py` is for).
