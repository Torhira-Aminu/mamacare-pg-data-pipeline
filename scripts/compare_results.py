"""Compare saved Athena results (docs/evidence/athena_results_*.json) with local SQLite answers."""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
evidence = sorted((ROOT / "docs" / "evidence").glob("athena_results_*.json"))[-1]
athena = json.loads(evidence.read_text())["queries"]
ok = True
for name, q in athena.items():
    with (ROOT / "data" / "expected" / f"{name}.csv").open() as f:
        exp = list(csv.reader(f))
    same = [q["header"]] + q["rows"] == exp
    ok &= same
    print(f"{name}: {'MATCH' if same else 'DIFFERENT'} ({len(q['rows'])} rows, {q['scanned_bytes']} bytes scanned)")
sys.exit(0 if ok else 1)
