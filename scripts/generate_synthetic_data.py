"""Generate 8 SYNTHETIC maternal-health resource datasets for Prince George's County, MD.

Everything here is made up by one seeded random generator: names, street addresses,
phone numbers (fictional 555-01xx range), hours, and how many resources sit in each
ZIP code. Only the ZIP codes and town names are real, so the data lines up with a
real map. These files are NOT eight independent data sources and say nothing about
real service availability.

    python scripts/generate_synthetic_data.py            # writes data/raw/<type>/<type>.csv
"""
from __future__ import annotations

import csv
import pathlib
import random

SEED = 20261109
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"

# Real Prince George's County ZIP codes with their postal town names.
PG_ZIPS = {
    "20705": "Beltsville", "20706": "Lanham", "20707": "Laurel", "20708": "Laurel",
    "20710": "Bladensburg", "20712": "Mount Rainier", "20715": "Bowie", "20716": "Bowie",
    "20720": "Bowie", "20721": "Bowie", "20737": "Riverdale", "20740": "College Park",
    "20743": "Capitol Heights", "20744": "Fort Washington", "20745": "Oxon Hill",
    "20746": "Suitland", "20747": "District Heights", "20748": "Temple Hills",
    "20769": "Glenn Dale", "20770": "Greenbelt", "20772": "Upper Marlboro",
    "20774": "Upper Marlboro", "20781": "Hyattsville", "20782": "Hyattsville",
    "20783": "Hyattsville", "20784": "Hyattsville", "20785": "Hyattsville",
}

# resource_type -> (label used in names, how many synthetic records to create)
RESOURCE_TYPES = {
    "prenatal_clinics": ("Prenatal Clinic", 22),
    "wic_locations": ("WIC Site", 14),
    "medicaid_resources": ("Medicaid Enrollment Help", 12),
    "food_pantries": ("Food Pantry", 30),
    "diaper_banks": ("Diaper Bank", 9),
    "childcare_providers": ("Childcare Provider", 35),
    "transportation_assistance": ("Ride Assistance", 8),
    "mental_health_services": ("Perinatal Mental Health", 15),
}

COLUMNS = ["resource_id", "name", "street_address", "city", "state", "zip_code",
           "phone", "languages", "accepts_medicaid", "hours", "is_synthetic"]
STREETS = ["Example Ave", "Sample Rd", "Placeholder St", "Demo Blvd", "Fictional Way", "Test Ln"]
LANGS = ["English", "English;Spanish", "English;French", "English;Spanish;Amharic", "English;Yoruba"]
HOURS = ["Mon-Fri 9:00-17:00", "Mon-Sat 8:00-18:00", "Tue-Thu 10:00-16:00", "Sat 9:00-13:00"]


def generate(seed: int = SEED) -> dict[str, list[dict]]:
    rng = random.Random(seed)
    zips = list(PG_ZIPS)
    datasets = {}
    phone_counter = 0
    for rtype, (label, count) in RESOURCE_TYPES.items():
        # Uneven weights so some ZIPs get many records and some get none, which gives
        # the queries something to show. The skew is random, not based on reality.
        weights = [rng.choice([0, 1, 1, 2, 3]) for _ in zips]
        rows = []
        for i in range(1, count + 1):
            z = rng.choices(zips, weights=[w or 0.0001 for w in weights])[0]
            phone_counter += 1
            rows.append({
                "resource_id": f"{rtype[:3].upper()}-{i:03d}",
                "name": f"Synthetic {label} {i:02d}",
                "street_address": f"{rng.randint(100, 9999)} {rng.choice(STREETS)}",
                "city": PG_ZIPS[z],
                "state": "MD",
                "zip_code": z,
                "phone": f"301-555-01{phone_counter % 100:02d}",
                "languages": rng.choice(LANGS),
                "accepts_medicaid": rng.choice(["true", "false"]) if rtype != "medicaid_resources" else "true",
                "hours": rng.choice(HOURS),
                "is_synthetic": "true",
            })
        datasets[rtype] = rows
    return datasets


def write(datasets: dict[str, list[dict]], out: pathlib.Path = OUT) -> list[pathlib.Path]:
    paths = []
    for rtype, rows in datasets.items():
        d = out / rtype
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{rtype}.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        paths.append(p)
    # Reference table of real PG County ZIPs so queries can show ZIPs with zero records.
    ref = out.parent / "reference" / "pg_zip_codes"
    ref.mkdir(parents=True, exist_ok=True)
    rp = ref / "pg_zip_codes.csv"
    with rp.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["zip_code", "city"])
        w.writerows(PG_ZIPS.items())
    paths.append(rp)
    return paths


if __name__ == "__main__":
    for p in write(generate()):
        print(p.relative_to(ROOT))
