"""Run the same SQL files against the synthetic CSVs in SQLite to get expected answers.

    python scripts/run_local.py     # writes data/expected/<query>.csv

Athena results are compared to these files to verify the cloud pipeline.
"""
import csv
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_synthetic_data import PG_ZIPS, RESOURCE_TYPES  # noqa: E402


def load(conn, raw=ROOT / "data" / "raw"):
    conn.execute("CREATE TABLE mamacare_resources (resource_id, name, street_address, city, state, "
                 "zip_code, phone, languages, accepts_medicaid, hours, is_synthetic, resource_type)")
    for rtype in RESOURCE_TYPES:
        with (raw / rtype / f"{rtype}.csv").open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                conn.execute("INSERT INTO mamacare_resources VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                             [*row.values(), rtype])
    conn.execute("CREATE TABLE pg_zip_codes (zip_code, city)")
    conn.executemany("INSERT INTO pg_zip_codes VALUES (?,?)", PG_ZIPS.items())


def run_all(out=ROOT / "data" / "expected"):
    conn = sqlite3.connect(":memory:")
    load(conn)
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for sql_file in sorted((ROOT / "sql").glob("*.sql")):
        cur = conn.execute(sql_file.read_text())
        cols = [c[0] for c in cur.description]
        rows = [[str(v) for v in r] for r in cur.fetchall()]
        with (out / f"{sql_file.stem}.csv").open("w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(cols)
            w.writerows(rows)
        results[sql_file.stem] = (cols, rows)
    return results


if __name__ == "__main__":
    for name, (cols, rows) in run_all().items():
        print(f"{name}: {len(rows)} rows")
