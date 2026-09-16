"""Verdict logic and reference extraction must be deterministic and offline-testable."""

from __future__ import annotations

import json

import pytest

import rx_common as rx
import verify_citations as vc


# --------------------------------------------------------------------------- #
# Extraction                                                                  #
# --------------------------------------------------------------------------- #


def test_skips_headings_and_prose():
    text = (
        "# References\n\n"
        "This paper studies crop mapping. We used Sentinel-2 imagery and a U-Net.\n\n"
        "[1] Chen, W., Kumar, A. (2024). A foundation model for crop mapping. "
        "Remote Sensing of Environment. doi:10.1016/j.rse.2024.114123\n"
    )
    queries = vc.extract_queries(text, ".md")
    assert len(queries) == 1
    assert queries[0]["doi"] == "10.1016/j.rse.2024.114123"
    assert "foundation model" in queries[0]["title"]
    assert "Chen" in queries[0]["surnames"]


def test_parses_bibtex():
    bib = """@article{chen2024crop,
  title = {A foundation model for crop mapping},
  author = {Chen, Wei and Kumar, Anil},
  journal = {Remote Sensing of Environment},
  year = {2024},
  doi = {10.1016/j.rse.2024.114123}
}"""
    queries = vc.extract_queries(bib, ".bib")
    assert len(queries) == 1
    assert queries[0]["doi"] == "10.1016/j.rse.2024.114123"
    assert queries[0]["surnames"][:2] == ["Chen", "Kumar"]
    assert queries[0]["year"] == "2024"


def test_parses_json_references():
    payload = json.dumps(
        {"references": [{"doi": "10.1000/x.1", "title": "A study of things", "authors": ["Lee, K"], "year": 2020}]}
    )
    queries = vc.extract_queries(payload, ".json")
    assert queries and queries[0]["doi"] == "10.1000/x.1"
    assert queries[0]["surnames"] == ["Lee"]


def test_doi_cleaning_strips_trailing_punctuation():
    text = "See Smith 2020 (doi:10.1000/abc.123.)."
    assert rx.find_dois(text) == ["10.1000/abc.123"]


# --------------------------------------------------------------------------- #
# Verdicts                                                                    #
# --------------------------------------------------------------------------- #


def test_verified_doi(fake_net, crossref_doi_body):
    fake_net({"api.crossref.org/works/10.1016": crossref_doi_body})
    assert vc.main(["--doi", "10.1016/j.rse.2024.114123", "--format", "json", "--quiet"]) == 0


def test_cli_json_report_is_machine_readable(fake_net, crossref_doi_body, capsys):
    fake_net({"api.crossref.org/works/10.1016": crossref_doi_body})
    vc.main(["--doi", "10.1016/j.rse.2024.114123", "--format", "json", "--quiet"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["verified"] == 1
    assert payload["results"][0]["verdict"] == rx.VERIFIED
    assert payload["results"][0]["doi"] == "10.1016/j.rse.2024.114123"


def test_retraction_is_flagged():
    from conftest import load_fixture

    result = vc.verify_one(
        rx.Net(transport=lambda url: load_fixture("crossref_retracted.json"), cache_dir=None),
        vc.blank_query(raw="x", doi="10.1000/retracted.2021.001"),
        ["crossref", "openalex", "doi"],
        0.8,
    )
    assert result["verdict"] == rx.RETRACTED
    assert "retract" in " ".join(result["notes"]).lower()


def test_title_search_verifies_without_doi(fake_net, crossref_search_body):
    fake_net({"api.crossref.org/works": crossref_search_body})
    verdict = vc.verify_one(
        rx.Net(transport=lambda url: crossref_search_body, cache_dir=None),
        vc.blank_query(title="A foundation model for global crop mapping from Sentinel-2 time series",
                       surnames=["Chen"], year="2024"),
        ["crossref"],
        0.8,
    )
    assert verdict["verdict"] == rx.VERIFIED


def test_metadata_drift_is_correctable():
    query = vc.blank_query(title="A foundation model for global crop mapping", surnames=["Chen"], year="2018")
    record = rx.blank_record(
        source="crossref",
        doi="10.1016/j.rse.2024.114123",
        title="A foundation model for global crop mapping from Sentinel-2 time series",
        authors=["Chen", "Kumar"],
        year=2024,
        type="journal-article",
    )
    verdict = rx.judge(query, record)
    assert verdict["verdict"] == rx.CORRECTED
    assert any("year differs" in note for note in verdict["notes"])


def test_unrelated_record_is_not_found():
    query = vc.blank_query(title="Quantum crop mapping with entanglement", surnames=["Smith"], year="2024")
    record = rx.blank_record(
        source="crossref",
        title="Deep learning for urban land use classification",
        authors=["Wang"],
        year=2019,
        type="journal-article",
    )
    assert rx.judge(query, record)["verdict"] == rx.NOT_FOUND


def test_network_failure_is_an_error_not_a_fake_verdict():
    def boom(url):
        raise RuntimeError("TLS connection closed")

    net = rx.Net(transport=boom, cache_dir=None)
    verdict = vc.verify_one(net, vc.blank_query(title="Some plausible paper title"), ["crossref"], 0.8)
    assert verdict["verdict"] == rx.ERROR
    assert "failed" in verdict["notes"][0]


def test_arxiv_match():
    from conftest import FIXTURES

    atom = (FIXTURES / "arxiv_query.xml").read_text(encoding="utf-8")
    net = rx.Net(transport=lambda url: atom, cache_dir=None)
    verdict = vc.verify_one(
        net,
        vc.blank_query(title="Self-supervised pretraining for label-scarce crop type mapping", year="2025"),
        ["arxiv"],
        0.8,
    )
    assert verdict["verdict"] == rx.VERIFIED
    assert verdict["record"]["source"] == "arxiv"


def test_fail_on_unverified_exit_code(fake_net):
    fake_net({}, default_error="not found (404)")
    code = vc.main(
        ["--title", "A fabricated paper that does not exist anywhere", "--format", "text",
         "--fail-on-unverified", "--quiet"]
    )
    assert code == 1


def test_missing_input_returns_usage_error(capsys):
    assert vc.main(["--quiet"]) == 2


# --------------------------------------------------------------------------- #
# Markdown report                                                             #
# --------------------------------------------------------------------------- #


def test_markdown_report_has_audit_sections(fake_net, crossref_doi_body, tmp_path):
    fake_net({"api.crossref.org/works/10.1016": crossref_doi_body})
    out = tmp_path / "citation_audit.md"
    vc.main(["--doi", "10.1016/j.rse.2024.114123", "--format", "md", "--out", str(out), "--quiet"])
    text = out.read_text(encoding="utf-8")
    assert "# Citation Audit" in text
    assert "VERIFIED" in text
    assert "not proof of fabrication" in text.lower()


@pytest.mark.parametrize(
    "cited, registry, expected",
    [
        ("Attention is all you need", "Attention is all you need", 1.0),
        ("attention is all you need", "Attention Is All You Need", 1.0),
        ("Crop mapping with U-Net", "Urban land use classification", 0.0),
    ],
)
def test_title_similarity_bounds(cited, registry, expected):
    score = rx.title_similarity(cited, registry)
    assert 0.0 <= score <= 1.0
    if expected == 1.0:
        assert score > 0.95
    else:
        assert score < 0.5
