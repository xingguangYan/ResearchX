# ResearchX — Research Design Reference

## 1. How to Define a Good Research Question

### FINER Criteria
| Criterion | Question to ask |
|-----------|-----------------|
| **F**easible | Doable with available data, time, and resources |
| **I**nteresting | Interesting to the research community |
| **N**ovel | Adds new knowledge (confirmed via literature search) |
| **E**thical | No ethical concerns |
| **R**elevant | Relevant to the field and societal needs |

### PICO Framework (for applied sciences)
- **P**opulation/Problem — What is the study object?
- **I**ntervention — What method/approach is applied?
- **C**omparison — What is the alternative/baseline?
- **O**utcome — What is measured?

## 2. Literature Search Strategy

### Database Priority
1. Google Scholar / Web of Science / Scopus (broad coverage)
2. arXiv (latest pre-prints)
3. Domain-specific databases (IEEE Xplore, ACM DL, etc.)
4. Chinese databases — CNKI,万方 (for Chinese-language research)

### Search Query Template
```
(primary keyword) AND (secondary keyword) AND (method) AND (year:[2023 TO 2026])
```

### Evidence Pyramid for Research Design
1. Meta-analyses / Reviews — Best for understanding landscape
2. Recent SOTA papers (2024-2026) — Best for method selection
3. Benchmark papers — Best for baseline comparison
4. Dataset papers — Best for data sourcing

## 3. Common Research Design Problems

| Problem | Symptom | Fix |
|---------|---------|-----|
| Weak novelty | "Incremental improvement" | Search for cross-domain method transfer |
| Incomplete baselines | Only compares with outdated methods | Search for SOTA (2024-2026) |
| Missing ablation | "Black box" results | Design modular experiments |
| Poor generalization | Single dataset/region | Add cross-validation scenarios |
| Statistical weakness | No error bars | Run multiple trials with different seeds |
