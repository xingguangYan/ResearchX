# ResearchX — SCI Writing Templates & Style Guide

## 1. Abstract Templates

### Structured Abstract
```
Background: [1-2 sentences on context/problem importance]
Objective: [1 sentence on what this paper aims to solve]
Method: [2-3 sentences on the proposed approach]
Results: [1-2 sentences on key findings with numbers]
Conclusion: [1 sentence on significance and implication]
Keywords: [5-8 keywords]
```

### Highlight-Style Abstract (Nature/Science)
```
[1 sentence hook about the big-picture importance]
[1 sentence on the specific gap]
[1 sentence on the approach]
[1 sentence on the key result with evidence]
[1 sentence on the broader impact]
```

## 2. Introduction Funnel Structure

```
Paragraph 1: Broad context — why this field matters
Paragraph 2: Specific background — what is known
Paragraph 3: Research gap — what is NOT known (cite specific limitations)
Paragraph 4: Our approach — what we did and why
Paragraph 5: Contributions — numbered list of 3-5 specific contributions
Paragraph 6: Paper organization — "The remainder of this paper is organized as follows..."
```

## 3. Methods Section Structure

### Data Subsection
```
3.1 Study Area
  - Location, climate, geography
  - Justification for selection
3.2 Data Sources
  - Sensor/source, resolution, time range
  - Preprocessing steps with references
3.3 Reference Data
  - Collection method, sample size, split strategy
```

### Model Subsection
```
3.4 Proposed Method
  - Overall framework (reference figure)
  - Module 1: purpose + detail
  - Module 2: purpose + detail
  - Training details: optimizer, loss, hyperparameters
```

### Evaluation Subsection
```
3.5 Experimental Setup
  - Baselines (with justification)
  - Metrics (with formulas if necessary)
  - Implementation details (hardware, framework, seed)
```

## 4. Results & Discussion

### Results Structure
- Start with main finding (best result)
- Use tables for quantitative comparison
- Use figures for qualitative comparison
- Each paragraph: claim → evidence → interpretation

### Discussion Structure
- Restate main findings (don"t repeat results)
- Compare with literature (why is yours better/different)
- Address unexpected results
- Limitations section (honest and constructive)
- Future work

## 5. Common SCI Review Criteria

### Novelty
- Is the problem new? (20%)
- Is the method new? (30%)
- Are the findings new? (20%)
- Is the application new? (15%)
- Is the dataset new? (15%)

### Technical Quality
- Sound methodology (25%)
- Comprehensive experiments (25%)
- Proper baselines (20%)
- Statistical rigor (15%)
- Reproducibility (15%)

### Presentation
- Clear writing (30%)
- Effective figures (30%)
- Proper citations (20%)
- Logical structure (20%)
