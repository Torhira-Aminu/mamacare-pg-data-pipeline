import csv
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_synthetic_data import COLUMNS, PG_ZIPS, RESOURCE_TYPES, generate, write  # noqa: E402
import run_local  # noqa: E402


@pytest.fixture(scope="module")
def data():
    return generate()


def test_eight_resource_types(data):
    assert sorted(data) == sorted([
        "prenatal_clinics", "wic_locations", "medicaid_resources", "food_pantries",
        "diaper_banks", "childcare_providers", "transportation_assistance", "mental_health_services"])


def test_generator_is_deterministic(data):
    assert generate() == data


def test_every_record_is_marked_and_named_synthetic(data):
    for rows in data.values():
        for r in rows:
            assert r["is_synthetic"] == "true"
            assert r["name"].startswith("Synthetic ")


def test_only_fictional_phone_numbers(data):
    for rows in data.values():
        for r in rows:
            assert re.fullmatch(r"301-555-01\d\d", r["phone"])


def test_zip_codes_are_pg_county_and_city_matches(data):
    for rows in data.values():
        for r in rows:
            assert r["zip_code"] in PG_ZIPS and r["city"] == PG_ZIPS[r["zip_code"]]


def test_record_counts_and_unique_ids(data):
    for rtype, rows in data.items():
        assert len(rows) == RESOURCE_TYPES[rtype][1]
        assert len({r["resource_id"] for r in rows}) == len(rows)


def test_no_commas_in_fields(data):
    # The Athena table uses a simple comma-delimited SerDe without quoting.
    for rows in data.values():
        for r in rows:
            assert all("," not in v for v in r.values())


def test_written_files_have_expected_header(tmp_path, data):
    write(data, tmp_path / "raw")
    with (tmp_path / "raw" / "food_pantries" / "food_pantries.csv").open() as f:
        assert next(csv.reader(f)) == COLUMNS
    assert (tmp_path / "reference" / "pg_zip_codes" / "pg_zip_codes.csv").exists()


def test_local_queries_are_consistent(tmp_path):
    results = run_local.run_all(tmp_path)
    total = sum(n for _, n in RESOURCE_TYPES.values())
    by_zip_type = results["01_counts_by_zip_and_type"][1]
    assert sum(int(r[2]) for r in by_zip_type) == total
    summary_cols, summary = results["02_zip_summary"]
    assert len(summary) == len(PG_ZIPS)                      # every ZIP appears, even with 0
    assert sum(int(r[2]) for r in summary) == total
    for r in summary:                                        # per-type columns add up to the total
        assert sum(int(v) for v in r[3:]) == int(r[2])
    missing = results["03_zips_missing_types"][1]
    assert all(0 <= int(r[2]) <= 8 for r in missing)


def test_saved_athena_results_match_local_answers():
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "compare_results.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
