# ResearchX Architecture Diagram

This directory contains architecture and workflow diagrams for ResearchX.

## System Architecture

```mermaid
graph TB
    subgraph "User Input Layer"
        U[User Request]
        PDF[PDF Upload]
        DOI[DOI / Paper Link]
    end

    subgraph "ResearchX Core"
        direction TB
        R[Task Router]
        R -->|Analyze Paper| P[Paper Analysis]
        R -->|Find Topic| G[Gap Mining]
        R -->|Methods| M[Method Mining]
        R -->|Experiments| E[Experiment Design]
        R -->|Write Paper| W[Manuscript Writer]
        R -->|Publish| S[SCI Upgrade]
        R -->|Review| RV[Peer Review]
        R -->|Visuals| V[Visual Generation]
        R -->|Grant| GR[Grant Proposal]
        R -->|Review| LR[Lit Review Builder]
    end

    subgraph "Knowledge Sources"
        WS[web_search ~ 2023-2026 Literature]
        LS[Local Scripts: analyze_methods.py]
        VG[Local Scripts: generate_visuals.py]
    end

    subgraph "Output Layer"
        O1[analysis_*.md]
        O2[topics_*.md]
        O3[methods_*.md]
        O4[manuscript_*.md]
        O5[review_report.md]
        O6[grant_proposal.md]
        O7[visual_prompts.md]
        O8[literature_matrix.md]
    end

    U --> R
    PDF --> P
    DOI --> P

    P --> WS
    G --> WS
    M --> WS
    W --> WS
    GR --> WS
    LR --> WS

    M --> LS
    V --> VG

    P --> O1
    G --> O2
    M --> O3
    W --> O4
    RV --> O5
    GR --> O6
    V --> O7
    LR --> O8
```

## Module Chaining Logic

```mermaid
flowchart LR
    subgraph "Vague Idea -> Paper"
        A1[Clarify Topic] --> A2[§2 Gap Mining]
        A2 --> A3[§3 Method Mining]
        A3 --> A4[§4 Experiment Design]
        A4 --> A5[§5 Manuscript Writing]
        A5 --> A6[§6 SCI Upgrade]
        A6 --> A7[§7 Peer Review]
        A7 --> A8[§8 Visuals]
    end

    subgraph "Paper Analysis -> Improvement"
        B1[§1 Paper Analysis] --> B2[§3 Method Comparison]
        B2 --> B3[§4 Missing Experiments]
        B3 --> B4[§6 Upgrade Plan]
    end

    subgraph "Gap -> Proposal"
        C1[§2 Gap Mining] --> C2[§3 Methods]
        C2 --> C3[§10 Grant Proposal]
    end
```

## Literature-Driven Methodology Flow

```mermaid
sequenceDiagram
    participant U as User
    participant RX as ResearchX
    participant WS as Web Search
    participant LS as Local Scripts

    U->>RX: "I want to study [topic]"
    RX->>WS: Search 1: review + survey
    RX->>WS: Search 2: challenges + gaps
    RX->>WS: Search 3: SOTA methods
    WS-->>RX: Papers data
    RX->>LS: analyze_methods.py
    LS-->>RX: Method taxonomy + trends
    RX->>RX: Identify research gaps
    RX->>U: Present 5 topics with methods
    U->>RX: "I like topic 3"
    RX->>WS: Search methods for topic 3
    RX->>LS: Generate method landscape
    RX->>U: Method recommendation + experiment plan
    U->>RX: "Write the paper"
    RX->>U: Manuscript (+ lit citations)
    RX->>U: "Shall I continue to SCI upgrade?"
    U->>RX: "Yes"
    RX->>U: Upgrade plan + review simulation
```
