# Architecture diagrams

Copy-paste Mermaid for docs, slides and proposals. Keep them in sync with `SKILL.md` if you change the
module list.

## 1. The lifecycle loop

```mermaid
flowchart LR
    Q[Question / draft / idea] --> M2[M2 Gap mining]
    M2 --> M2b[M2b Novelty check]
    M2b --> M3[M3 Method mining]
    M3 --> M4[M4 Experiment design]
    M4 --> M5[M5 Manuscript]
    M5 --> M11[M11 Citation audit]
    M11 --> M6[M6 Journal fit & upgrade]
    M6 --> M7[M7 Adversarial peer review]
    M7 --> M5
    M5 --> M8[M8 Visuals]
    M8 --> M12[M12 Reproducibility packaging]
    M12 --> S[Submission]
```

## 2. Where the guarantees come from

```mermaid
flowchart TD
    subgraph Retrieval
      W[Web search] --> R[(OpenAlex · Crossref · arXiv)]
      R --> P[search_literature.py]
    end
    subgraph Skill["skills/researchx"]
      SK[SKILL.md: contract + router] --> REF[references/*.md on demand]
      SK --> TPL[assets/* templates]
    end
    subgraph Verification["Citation integrity (M11)"]
      V[verify_citations.py] --> J{judge}
      J -->|match| OK[VERIFIED / CORRECTED]
      J -->|no match| UF[NOT_FOUND → label UNVERIFIED]
      J -->|retraction| RET[RETRACTED → remove]
      J -->|network| ERR[ERROR → say the check did not run]
    end
    P --> SK
    SK --> V
    OK --> OUT[Deliverable + citation_audit.md]
    UF --> OUT
    RET --> OUT
    ERR --> OUT
    subgraph Review["Systematic review (M9)"]
      P --> PS[prisma_screen.py] --> F[PRISMA counts · flow · ledger]
    end
```

## 3. Progressive disclosure (context budget)

```mermaid
flowchart TD
    L1["Tier 1 — loaded at session start: name + description (~100 tokens)"]
    L2["Tier 2 — loaded on activation: SKILL.md body (233 lines, <5k tokens)"]
    L3["Tier 3 — loaded on demand: references/*.md, assets/*.md, scripts/*.py"]
    L1 --> L2 --> L3
```

## 4. Module chaining for a full paper

```mermaid
sequenceDiagram
    participant U as User
    participant RX as ResearchX
    participant API as Registries
    participant V as verify_citations.py
    U->>RX: "I want a publication on [topic]"
    RX->>API: search_literature (queries + chaining)
    API-->>RX: records with DOIs
    RX->>U: 5 topics (novelty, data, venue, scoop risk)
    U->>RX: "topic 3"
    RX->>API: method landscape
    RX->>U: experiment plan + missing-experiment scan
    U->>RX: "write the manuscript"
    RX->>V: audit every reference
    V-->>RX: verdicts + corrections
    RX->>U: draft + citation_audit.md
    RX->>U: upgrade plan, adversarial review, response letter
```

## 5. Multi-agent pattern (platforms with subagents)

```mermaid
flowchart LR
    SC[Scout: retrieve] --> SR[Screener: include/exclude + reason]
    SR --> EX[Extractor: structured fields]
    EX --> CR[Critic: adversarial check]
    CR --> WR[Writer: synthesis]
    CR -.->|objection cites the record| SR
```

Each agent returns artifacts, not prose summaries; the Critic must name the record it objects to.
