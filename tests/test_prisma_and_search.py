"""Screening/PRISMA maths and literature-search plumbing."""

from __future__ import annotations

import csv
import json

import prisma_screen as ps
import rx_common as rx
import search_literature as sl


def test_dedupe_merges_doi_and_title_duplicates():
    records = [
        {"id": "1", "title": "A foundation model for global crop mapping", "doi": "10.1/a", "source": "openalex"},
        {"id": "2", "title": "A foundation model for global crop mapping!", "doi": None, "source": "crossref"},
        {"id": "3", "title": "Crop yield prediction with LSTMs", "doi": "10.1/c", "source": "openalex"},
    ]
    unique = sl.dedupe(records)
    assert len(unique) == 2


def test_rule_screening_records_reasons():
    records = [
        {"id": "1", "title": "Crop mapping with transformers", "year": "2024", "type": "article"},
        {"id": "2", "title": "A review of crop mapping", "year": "2022", "type": "review"},
        {"id": "3", "title": "Urban land use classification", "year": "2024", "type": "article"},
        {"id": "4", "title": "Crop mapping in 2005", "year": "2005", "type": "article"},
    ]
    kept, excluded, undecided = ps.rule_stage(records, ["crop mapping"], ["review"], 2015, None, ["article"])
    kept_ids = {r["id"] for r in kept}
    excluded_ids = {r["id"] for r in excluded}
    undecided_ids = {r["id"] for r in undecided}
    assert kept_ids == {"1"}
    assert {"2", "4"} <= excluded_ids  # review excluded, old excluded
    assert undecided_ids == {"3"}  # no inclusion criterion matched -> needs a human
    assert all(r.get("reason") for r in excluded)


def test_full_pipeline_writes_prisma_artifacts(tmp_path, hits):
    hits_path = tmp_path / "hits.json"
    hits_path.write_text(json.dumps(hits), encoding="utf-8")
    prefix = tmp_path / "review1"

    code = ps.main(
        [
            "--input", str(hits_path),
            "--include", "crop mapping",
            "--exclude", "editorial",
            "--out-prefix", str(prefix),
            "--format", "json",
            "--quiet",
        ]
    )
    assert code == 0

    counts = json.loads((tmp_path / "review1_counts.json").read_text())
    assert counts["identified_total"] == 7
    assert counts["duplicates_removed"] == 1          # ids 1 and 2 are the same paper
    assert counts["records_screened"] == 6
    assert counts["included"] >= 2
    assert counts["included"] < 7
    assert counts["excluded_by_rule"]

    flow = (tmp_path / "review1_flow.md").read_text(encoding="utf-8")
    assert "```mermaid" in flow
    assert "Studies included in synthesis" in flow
    assert "PRISMA-trAIce" in flow or "AI" in flow

    ledger = list(csv.DictReader((tmp_path / "review1_ledger.csv").read_text().splitlines()))
    assert ledger and {"id", "stage", "decision", "reason"} <= set(ledger[0].keys())
    assert any(row["decision"] == "pending-human" for row in ledger)

    included = json.loads((tmp_path / "review1_included.json").read_text())
    assert included["results"]


def test_decisions_file_moves_records_at_eligibility(tmp_path, hits):
    hits_path = tmp_path / "hits.json"
    hits_path.write_text(json.dumps(hits), encoding="utf-8")
    decisions = tmp_path / "decisions.json"
    decisions.write_text(
        json.dumps({"3": {"decision": "exclude", "reason": "review, not primary study"}}), encoding="utf-8"
    )
    code = ps.main(
        ["--input", str(hits_path), "--include", "crop mapping", "--decisions", str(decisions),
         "--out-prefix", str(tmp_path / "r"), "--format", "json", "--quiet"]
    )
    assert code == 0
    counts = json.loads((tmp_path / "r_counts.json").read_text())
    assert counts["excluded_at_eligibility"] >= 1


def test_missing_input_is_usage_error(tmp_path):
    assert ps.main(["--input", str(tmp_path / "nope.json"), "--quiet"]) == 2


def test_search_returns_records_from_openalex(fake_net, openalex_search_body, tmp_path):
    fake_net({"api.openalex.org/works": openalex_search_body})
    out = tmp_path / "hits.json"
    code = sl.main(["--query", "crop mapping foundation model", "--format", "json",
                    "--out", str(out), "--limit", "5", "--quiet"])
    assert code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["results"][0]["doi"] == "10.1016/j.rse.2024.114123"
    assert payload["retrieved"] >= 1


def test_search_markdown_table(fake_net, openalex_search_body, capsys):
    fake_net({"api.openalex.org/works": openalex_search_body})
    sl.main(["--query", "crop mapping", "--limit", "3", "--quiet", "--no-dedupe"])
    out = capsys.readouterr().out
    assert "| # | Title | Year |" in out
    assert "doi.org/10.1016/j.rse.2024.114123" in out


def test_search_exit_code_when_nothing_retrievable(fake_net):
    fake_net({}, default_error="network error: offline")
    assert sl.main(["--query", "nothing at all here", "--quiet"]) == 3


def test_forward_chaining_builds_openalex_filter(fake_net):
    registry = fake_net(
        {
            "api.openalex.org/works/doi:": {"id": "https://openalex.org/W123"},
            "api.openalex.org/works?": {"results": [
                {"id": "https://openalex.org/W999", "title": "A citing paper", "publication_year": 2025,
                 "authorships": [], "primary_location": {}, "is_retracted": False}
            ]},
        }
    )
    code = sl.main(["--cited-by", "10.1/anchor", "--format", "json", "--quiet"])
    assert code == 0
    chained = [url for url in registry.calls if "cites%3AW123" in url or "cites:W123" in url]
    assert chained, registry.calls


def test_helpers_are_robust():
    assert rx.extract_surnames("Chen, W., Kumar, A.")[:2] == ["Chen", "Kumar"]
    assert rx.extract_surnames(["Wei Chen", "Anil Kumar"]) == ["Chen", "Kumar"]
    assert rx.years_apart("2024", 2024)
    assert not rx.years_apart("2019", 2024, tolerance=1)
    assert rx.title_similarity(None, "x") == 0.0
    assert rx.slugify("Ürban  Land-Use!! 2024") == "urban-land-use-2024"
