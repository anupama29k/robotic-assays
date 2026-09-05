import os
import random
import datetime
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".env"
))

from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

random.seed(42)  # reproducible


# ════════════════════════════════════════════════════
# DATASET 1 — Diverse historical CHO batches
# ════════════════════════════════════════════════════

DIVERSE_BATCHES = [
    {
        "batch_id": "CHO-040-DS-024",
        "narrative": "Routine release batch, all attributes well within historical norms",
        "harvest_date": "2025-12-15",
        "results": [
            {"assay_id": "BIO_001", "result_value": 4.6, "status": "pass", "notes": "Titer at historical mean"},
            {"assay_id": "BIO_003", "result_value": 0.7, "status": "pass", "notes": "HMWS within spec, clean profile"},
            {"assay_id": "BIO_013", "result_value": 24.8, "status": "pass", "notes": "Charge variants normal"},
        ],
    },
    {
        "batch_id": "CHO-042-DS-026",
        "narrative": "Higher than typical titer with otherwise normal quality profile — reflects process improvement campaign",
        "harvest_date": "2026-01-08",
        "results": [
            {"assay_id": "BIO_001", "result_value": 5.4, "status": "pass", "notes": "+17% vs historical, process gain"},
            {"assay_id": "BIO_003", "result_value": 0.9, "status": "pass", "notes": "HMWS slightly elevated but in spec"},
            {"assay_id": "BIO_013", "result_value": 24.5, "status": "pass", "notes": "Charge variants stable"},
        ],
    },
    {
        "batch_id": "CHO-043-DS-027",
        "narrative": "Endotoxin failure in otherwise normal batch — isolated contamination event, root cause traced to single-use bag",
        "harvest_date": "2026-01-22",
        "results": [
            {"assay_id": "BIO_001", "result_value": 4.5, "status": "pass", "notes": "Titer normal"},
            {"assay_id": "BIO_003", "result_value": 0.8, "status": "pass", "notes": "HMWS normal"},
            {"assay_id": "BIO_006", "result_value": 1.2, "status": "fail", "notes": "Endotoxin 1.2 EU/mL exceeds 0.5 limit — isolated event, no upstream signal"},
        ],
    },
    {
        "batch_id": "CHO-044-DS-029",
        "narrative": "Elevated HMWS with normal titer and charge variants — root cause: formulation buffer agitation during transfer",
        "harvest_date": "2026-02-10",
        "results": [
            {"assay_id": "BIO_001", "result_value": 4.6, "status": "pass", "notes": "Titer at historical mean"},
            {"assay_id": "BIO_003", "result_value": 1.4, "status": "fail", "notes": "HMWS elevated but isolated — no coordinated signal across other quality attributes"},
            {"assay_id": "BIO_013", "result_value": 24.4, "status": "pass", "notes": "Charge variants stable"},
        ],
    },
    {
        "batch_id": "CHO-046-DS-030",
        "narrative": "Subtle simultaneous drift across titer, aggregation, and charge variants — early warning signal preceding CHO-047 failure",
        "harvest_date": "2026-03-05",
        "results": [
            {"assay_id": "BIO_001", "result_value": 4.2, "status": "pass", "notes": "-9% vs historical, mild drift"},
            {"assay_id": "BIO_003", "result_value": 1.1, "status": "partial", "notes": "HMWS elevated, marginal"},
            {"assay_id": "BIO_013", "result_value": 26.0, "status": "pass", "notes": "Acidic +1.5pp, watch trend"},
        ],
    },
]


def insert_diverse_batches():
    inserted = 0
    for batch in DIVERSE_BATCHES:
        existing = sb.table("run_records").select("id").eq(
            "batch_id", batch["batch_id"]
        ).execute()
        if existing.data:
            print(f"  SKIP {batch['batch_id']} — exists")
            continue

        for result in batch["results"]:
            sb.table("run_records").insert({
                "run_id": f"RUN-{batch['batch_id']}-{result['assay_id']}",
                "batch_id": batch["batch_id"],
                "assay_id": result["assay_id"],
                "sample_id": f"{batch['batch_id']}-S01",
                "sample_type": "post_protein_a_eluate",
                "protocol_version": "2.0",
                "timestamp": batch["harvest_date"] + "T00:00:00Z",
                "acceptance_outcomes": {"overall": result["status"]},
                "raw_results": {
                    "primary_value": result["result_value"],
                    "operator": "system_seed",
                    "instrument_id": "demo",
                },
                "status": result["status"],
                "notes": result["notes"],
            }).execute()
            inserted += 1

        print(f"  Seeded {batch['batch_id']}: {len(batch['results'])} runs")
    return inserted


# ════════════════════════════════════════════════════
# DATASET 2 — HTS screening campaign
# ════════════════════════════════════════════════════

def generate_hts_campaign():
    """Generate a 384-compound HTS campaign with realistic
    dose-response and known hits."""
    campaign_id = "HTS-CAMP-2026-Q1"

    known_hit_ids = random.sample(range(1, 385), 19)  # ~5% hit rate

    plates = []
    for plate_num in range(1, 5):
        plate_id = f"{campaign_id}-P{plate_num:02d}"
        compounds_on_plate = list(range((plate_num - 1) * 96 + 1, plate_num * 96 + 1))

        wells = []
        for compound_id in compounds_on_plate:
            is_hit = compound_id in known_hit_ids
            doses_uM = [100, 30, 10, 3, 1, 0.3, 0.1, 0.03]

            if is_hit:
                ic50 = random.uniform(0.1, 10)
                hill = random.uniform(0.8, 1.5)
                bottom = random.uniform(2, 8)
                top = random.uniform(85, 100)
                responses = []
                for dose in doses_uM:
                    pct = bottom + (top - bottom) / (1 + (ic50 / dose) ** hill)
                    pct += random.gauss(0, 3)
                    responses.append(round(pct, 1))
            else:
                responses = [round(random.gauss(5, 4), 1) for _ in doses_uM]
                ic50 = None

            max_response = max(responses)

            wells.append({
                "compound_id": f"CMPD-{compound_id:04d}",
                "doses_uM": doses_uM,
                "responses_pct": responses,
                "ic50_uM": ic50,
                "is_hit": is_hit,
                "max_response": max_response,
            })

        z_factor = round(random.uniform(0.55, 0.85), 3)

        plates.append({
            "plate_id": plate_id,
            "campaign_id": campaign_id,
            "plate_num": plate_num,
            "n_compounds": len(wells),
            "n_hits": sum(1 for w in wells if w["is_hit"]),
            "z_factor": z_factor,
            "wells": wells,
            "run_date": (datetime.date(2026, 2, 5) + datetime.timedelta(days=plate_num)).isoformat(),
        })

    return campaign_id, plates


def insert_hts_campaign():
    campaign_id, plates = generate_hts_campaign()

    existing = sb.table("run_records").select("id").eq(
        "batch_id", campaign_id
    ).limit(1).execute()
    if existing.data:
        print(f"  SKIP HTS campaign — exists")
        return 0

    inserted = 0
    for plate in plates:
        sb.table("run_records").insert({
            "run_id": plate["plate_id"],
            "batch_id": campaign_id,
            "assay_id": "HTS_004",
            "sample_id": plate["plate_id"],
            "sample_type": "compound_library_plate",
            "protocol_version": "2.0",
            "timestamp": plate["run_date"] + "T00:00:00Z",
            "acceptance_outcomes": {
                "z_factor_pass": plate["z_factor"] >= 0.5,
                "hit_rate_pct": round(plate["n_hits"] / plate["n_compounds"] * 100, 1),
            },
            "raw_results": {
                "z_factor": plate["z_factor"],
                "n_compounds": plate["n_compounds"],
                "n_hits": plate["n_hits"],
                "operator": "system_seed",
                "instrument_id": "AutoMATE96-WB1",
                "wells": plate["wells"][:10],  # truncate for readability
            },
            "status": "pass" if plate["z_factor"] >= 0.5 else "fail",
            "notes": f"Plate {plate['plate_num']}/4, {plate['n_hits']} hits, Z-factor {plate['z_factor']}",
        }).execute()
        inserted += 1
        print(f"  Seeded {plate['plate_id']}")

    return inserted


# ════════════════════════════════════════════════════
# DATASET 3 — Extended instrument health timeline
# ════════════════════════════════════════════════════

def insert_extended_health():
    """26 weekly HPLC pressure data points spanning 6 months
    with one anomalous spike at week 18."""
    instrument_id = "HPLC_ProteinA_01"

    existing = sb.table("instrument_health").select(
        "id", count="exact"
    ).eq("instrument_id", instrument_id).execute()
    if existing.count and existing.count >= 25:
        print(f"  SKIP extended health — already populated ({existing.count} records)")
        return 0

    base_pressure = 168
    drift_per_week = 1.6  # bar/week

    records = []
    start_date = datetime.date(2025, 11, 1)

    for week in range(0, 26):
        date = start_date + datetime.timedelta(weeks=week)
        pressure = base_pressure + drift_per_week * week + random.gauss(0, 1.5)

        if week == 18:
            pressure += 22
            event_note = (
                "Anomalous pressure spike — root cause: "
                "particulate breakthrough from bioreactor harvest filter, "
                "resolved with column flush"
            )
        else:
            event_note = "Routine monitoring"

        records.append({
            "instrument_id": instrument_id,
            "assay_id": "BIO_001",
            "run_id": f"HEALTH-{date.strftime('%Y%m%d')}",
            "timestamp": date.isoformat() + "T00:00:00Z",
            "health_metrics": {
                "metric_name": "back_pressure",
                "metric_value": round(pressure, 1),
                "metric_unit": "bar",
                "back_pressure_bar": round(pressure, 1),
                "status": "warning" if pressure > 215 else "normal",
                "notes": event_note,
            },
        })

    inserted = 0
    for rec in records:
        sb.table("instrument_health").insert(rec).execute()
        inserted += 1

    print(f"  Seeded {inserted} health records")
    return inserted


# ════════════════════════════════════════════════════
# RUN ALL
# ════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("BIOINTERFACE — DEMO DATA EXPANSION")
    print("=" * 60)

    print("\n[1/3] Diverse historical batches...")
    n1 = insert_diverse_batches()
    print(f"  Inserted {n1} run records")

    print("\n[2/3] HTS screening campaign...")
    n2 = insert_hts_campaign()
    print(f"  Inserted {n2} plate records")

    print("\n[3/3] Extended instrument health...")
    n3 = insert_extended_health()
    print(f"  Inserted {n3} health records")

    print("\n" + "=" * 60)
    print("SUPABASE DATA STATUS")
    print("=" * 60)

    runs = sb.table("run_records").select("id", count="exact").execute()
    health = sb.table("instrument_health").select("id", count="exact").execute()

    print(f"  run_records       : {runs.count} total")
    print(f"  instrument_health : {health.count} total")
    print("=" * 60)


if __name__ == "__main__":
    main()
