# Search Queries & Retrieval Strategy

Two retrieval paths: **structured registries** (deterministic, citable, re-runnable) and **web search**
(broader, catches blogs, preprints, datasets, code). Use both, and record what you ran and when.

---

## 1. Structured retrieval (preferred for anything that will be cited)

```bash
# keyword search, recent window
python skills/researchx/scripts/search_literature.py \
    --query "crop mapping foundation model" --from-year 2023 --limit 30 --format json --out hits.json

# several queries merged and deduped
python skills/researchx/scripts/search_literature.py \
    --query "crop type mapping transformer" --query "label-efficient remote sensing segmentation" \
    --from-year 2022 --limit 25 --format md

# citation chaining from one anchor paper (find descendants and ancestors)
python skills/researchx/scripts/search_literature.py --cited-by 10.1016/j.rse.2024.114123 --limit 50
python skills/researchx/scripts/search_literature.py --references-of 10.1016/j.rse.2024.114123 --limit 50
```

Registry syntax worth knowing (when you query them directly):

| Registry | Useful operators |
|---|---|
| OpenAlex | `filter=publication_year:2023-2026,type:article,is_oa:true,cites:W123`; `search=`; `sort=cited_by_count:desc` |
| Crossref | `query.bibliographic=`, `filter=from-pub-date:2023-01-01,type:journal-article`, `sort=is-referenced-by-count`, `order=desc` |
| arXiv | `search_query=ti:"crop mapping" AND abs:"foundation model"`, `cat:eess.IV`, `sortBy=submittedDate` |
| PubMed | `("crop mapping"[tiab]) AND (deep learning[tiab]) AND 2023:2026[dp]` |
| Google Scholar | phrase in quotes, `filetype:pdf`, `intitle:`, `-word`, `author:`, limited year filters — high recall, low precision |
| CNKI / 万方 (Chinese) | `主题=遥感 作物分类`；`篇关摘=深度学习 + 时间:2023-2026`；use the Chinese term, not a translation |

---

## 2. Query patterns by intent

**Landscape / reviews**
```
[topic] review survey 2024 2025 2026
[topic] systematic review meta-analysis
[topic] comprehensive review deep learning
```

**SOTA / methods**
```
[topic] state of the art 2025 2026
[topic] benchmark comparison
[topic] outperforms / improves over
[topic] [method family] [year]
```

**Gaps and problems**
```
[topic] challenge limitation failure case
[topic] open problem unsolved
[topic] poor generalization / does not transfer
[topic] criticism of / reproducibility problem
```
Failure-oriented queries surface gaps far better than "future work" sections do.

**Data and benchmarks**
```
[topic] dataset benchmark 2024 2025
[topic] public dataset license
[topic] evaluation protocol standard
```

**Emerging paradigms**
```
[topic] foundation model pretraining
[topic] [topic] large language model agent
[topic] new paradigm 2025 2026
```

**Cross-domain transfer**
```
[method from field A] applied to [field B]
[field A] [technique] transfer learning domain adaptation
```

**Counter-evidence (do this before claiming a contribution)**
```
[topic] negative results
[topic] no improvement over baseline
[topic] survey of failures / reproducibility crisis
```

---

## 3. Web search patterns

```
"[exact paper title]"                       → find the paper and its DOI
"[title]" doi crossref                     → locate the DOI from a title
"[topic]" annual review 2025               → authoritative syntheses
"[topic]" site:arxiv.org                   → preprints
"[topic]" github benchmark leaderboard     → code and numbers
"[topic]" "reviewer" / editorial rejection → practice notes
"[method]" pytorch implementation          → reproducibility
```

---

## 4. Strategy rules

1. **Iterate**: start broad, read titles, then narrow with the vocabulary the field actually uses (that vocabulary is itself a finding).
2. **Three angles minimum**: by problem, by method, by application/data.
3. **Time window**: core = last 3 years; foundational = anything older that is still the reference point; say which is which.
4. **Language**: search English *and* the user's language. Non-English literature often covers different regions and is under-cited, which is an opportunity.
5. **Snowball**: from the best hit, run backward (its references) and forward (who cites it) chaining. `search_literature.py --references-of/--cited-by`.
6. **Stop rule**: stop when 3 successive queries return only papers you already have.
7. **Record**: exact strings, registry, date, filters, result count — this goes in the output header and is what makes a review reproducible.
8. **Dedupe before screening**: `prisma_screen.py` handles DOI and title duplicates; unscreened duplicates corrupt PRISMA counts.
9. **Verify before citing**: every kept record runs through `verify_citations.py`.
10. **Note the negative**: "searched X on date Y, nothing found" is a legitimate, citable finding — record it, since it may be your gap.

---

## 5. Query hygiene for gap claims

Before writing "no study has…":

- search the exact phrasing, then synonyms, then the native-language term;
- drop the year filter once (older work may have solved it and been forgotten);
- search the method name alone, and the dataset name alone;
- run one counter-evidence query;
- if still empty, write: "we found no study doing X (searched OpenAlex/Crossref/web on YYYY-MM-DD with
  queries: …)" — that is defensible. "Nobody has done X" is not.
