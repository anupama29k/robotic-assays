# seed_demo_data.py
# BioInterface — Demo Data Seeder
# Run once: python seed_demo_data.py

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("ERROR: Run: pip install supabase")
    exit(1)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL or SUPABASE_KEY not found in .env file.")
    exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
BATCH_ID = "CHO-047-DS-031"

def ts(days_ago=0, hours_ago=0):
    dt = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
    return dt.isoformat()

def check_existing():
    result = sb.table("run_records").select("id").eq("batch_id", BATCH_ID).limit(1).execute()
    return len(result.data) > 0

def seed_run_records():
    records = [
        {
            "run_id": "RUN-CHO047-001",
            "assay_id": "BIO_001",
            "batch_id": BATCH_ID,
            "sample_id": "CHO-047-S01",
            "sample_type": "post_protein_a_eluate",
            "protocol_version": "2.0",
            "timestamp": ts(days_ago=3, hours_ago=8),
            "acceptance_outcomes": {
                "standard_curve_r2": "PASS 0.9991",
                "qc_sample_recovery": "PASS 88%",
                "column_pressure_bar": "PASS 187 bar"
            },
            "raw_results": {
                "titer_mg_mL": 3.8,
                "standard_curve_r2": 0.9991,
                "qc_recovery_pct": 88,
                "column_pressure_bar": 187,
                "historical_mean_titer_mg_mL": 4.6,
                "deviation_from_historical_pct": -17.4
            },
            "status": "pass",
            "notes": "Titer PASS per spec but 17% below batch historical mean of 4.6 mg/mL. Flag for trending review."
        },
        {
            "run_id": "RUN-CHO047-002",
            "assay_id": "BIO_003",
            "batch_id": BATCH_ID,
            "sample_id": "CHO-047-S01",
            "sample_type": "post_protein_a_eluate",
            "protocol_version": "2.0",
            "timestamp": ts(days_ago=3, hours_ago=6),
            "acceptance_outcomes": {
                "hmws_investigation_threshold": "FAIL 3.1% HMWS — exceeds 2% investigation threshold"
            },
            "raw_results": {
                "hmws_pct": 3.1,
                "monomer_pct": 95.4,
                "lmws_pct": 1.5,
                "historical_mean_hmws_pct": 0.8,
                "delta_hmws_from_historical": 2.3
            },
            "status": "fail",
            "notes": "HMWS 3.1% significantly elevated vs historical mean 0.8%. Aggregation elevation combined with titer reduction suggests upstream stress event. Escalated to bioprocess team."
        },
        {
            "run_id": "RUN-CHO047-003",
            "assay_id": "BIO_006",
            "batch_id": BATCH_ID,
            "sample_id": "CHO-047-S01",
            "sample_type": "post_protein_a_eluate",
            "protocol_version": "2.0",
            "timestamp": ts(days_ago=2, hours_ago=10),
            "acceptance_outcomes": {
                "standard_curve_r2": "PASS 0.9940",
                "ppc_recovery_percent": "PASS 112%"
            },
            "raw_results": {
                "endotoxin_eu_mL": 0.08,
                "specification_limit_eu_mL": 0.5,
                "ppc_recovery_pct": 112
            },
            "status": "pass",
            "notes": "Endotoxin 0.08 EU/mL — well within 0.5 EU/mL limit. Run fully valid."
        },
        {
            "run_id": "RUN-CHO047-004",
            "assay_id": "BIO_010",
            "batch_id": BATCH_ID,
            "sample_id": "CHO-047-S01",
            "sample_type": "post_protein_a_eluate",
            "protocol_version": "2.0",
            "timestamp": ts(days_ago=2, hours_ago=8),
            "acceptance_outcomes": {
                "specification_range": "PASS 298 mOsm/kg (spec 270-350)"
            },
            "raw_results": {
                "osmolality_mosm_kg": 298,
                "ph": 7.02,
                "historical_mean_osmolality": 302
            },
            "status": "pass",
            "notes": "Osmolality 298 mOsm/kg within spec. pH 7.02 within spec. Formulation attributes normal."
        },
        {
            "run_id": "RUN-CHO047-005",
            "assay_id": "BIO_013",
            "batch_id": BATCH_ID,
            "sample_id": "CHO-047-S01",
            "sample_type": "post_protein_a_eluate",
            "protocol_version": "2.0",
            "timestamp": ts(days_ago=1, hours_ago=6),
            "acceptance_outcomes": {
                "reference_standard_main_peak_drift": "WARN main peak 64.2% vs historical 68.1% (delta 3.9%)"
            },
            "raw_results": {
                "acidic_variants_pct": 28.3,
                "main_peak_pct": 64.2,
                "basic_variants_pct": 7.5,
                "historical_mean_acidic_pct": 24.1,
                "historical_mean_main_pct": 68.1,
                "delta_acidic_from_historical": 4.2,
                "delta_main_from_historical": -3.9
            },
            "status": "partial",
            "notes": "Acidic variants 28.3% vs historical 24.1% (+4.2%). Main peak reduced 3.9%. Pattern aligns with aggregation and titer signals — likely same upstream cause."
        },
    ]
    inserted = 0
    for r in records:
        try:
            sb.table("run_records").insert(r).execute()
            print(f"  Inserted: {r['run_id']} | {r['assay_id']} | {r['status'].upper()}")
            inserted += 1
        except Exception as e:
            print(f"  SKIPPED {r['run_id']}: {e}")
    return inserted

def seed_historical_failure():
    record = {
        "run_id": "RUN-CHO045-001",
        "assay_id": "BIO_001",
        "batch_id": "CHO-045-DS-028",
        "sample_id": "CHO-045-S01",
        "sample_type": "post_protein_a_eluate",
        "protocol_version": "2.0",
        "timestamp": ts(days_ago=21),
        "acceptance_outcomes": {
            "qc_sample_recovery": "FAIL 76% (spec 85-115%)",
            "column_pressure_bar": "WARN 291 bar"
        },
        "raw_results": {
            "titer_mg_mL": 4.1,
            "qc_recovery_pct": 76,
            "column_pressure_bar": 291
        },
        "status": "fail",
        "notes": "QC recovery failed. Column pressure elevated at 291 bar. Root cause: column aging (injection count 478/500). Column replaced on next run."
    }
    try:
        sb.table("run_records").insert(record).execute()
        print(f"  Inserted historical: RUN-CHO045-001 | BIO_001 | FAIL")
        return 1
    except Exception as e:
        print(f"  SKIPPED historical: {e}")
        return 0

def seed_instrument_health():
    records = [
        {"instrument_id": "HPLC_ProteinA_01", "assay_id": "BIO_001",
         "run_id": "HEALTH-20260401", "timestamp": ts(days_ago=20),
         "health_metrics": {"back_pressure_bar": 168, "retention_time_min": 3.42,
                            "system_suitability_cv_pct": 0.3, "injection_count": 380}},
        {"instrument_id": "HPLC_ProteinA_01", "assay_id": "BIO_001",
         "run_id": "HEALTH-20260410", "timestamp": ts(days_ago=11),
         "health_metrics": {"back_pressure_bar": 198, "retention_time_min": 3.45,
                            "system_suitability_cv_pct": 0.5, "injection_count": 421}},
        {"instrument_id": "HPLC_ProteinA_01", "assay_id": "BIO_001",
         "run_id": "HEALTH-20260418", "timestamp": ts(days_ago=3),
         "health_metrics": {"back_pressure_bar": 231, "retention_time_min": 3.48,
                            "system_suitability_cv_pct": 0.7, "injection_count": 455}},
    ]
    inserted = 0
    for r in records:
        try:
            sb.table("instrument_health").insert(r).execute()
            print(f"  Inserted health: {r['run_id']} | pressure {r['health_metrics']['back_pressure_bar']} bar")
            inserted += 1
        except Exception as e:
            print(f"  SKIPPED {r['run_id']}: {e}")
    return inserted

def seed_sensor_logs():
    readings = [
        {"hplc_pressure_bar": 185, "uv_baseline_mau": 1.8, "retention_time_min": 3.44},
        {"hplc_pressure_bar": 189, "uv_baseline_mau": 2.1, "retention_time_min": 3.44},
        {"hplc_pressure_bar": 201, "uv_baseline_mau": 2.0, "retention_time_min": 3.45},
        {"hplc_pressure_bar": 218, "uv_baseline_mau": 2.3, "retention_time_min": 3.46},
        {"hplc_pressure_bar": 237, "uv_baseline_mau": 2.2, "retention_time_min": 3.47},
    ]
    inserted = 0
    for i, r in enumerate(readings):
        record = {
            "run_id": "RUN-CHO047-001", "assay_id": "BIO_001",
            "timestamp": (datetime.utcnow() - timedelta(hours=8) + timedelta(minutes=i*12)).isoformat(),
            "readings": r
        }
        try:
            sb.table("sensor_logs").insert(record).execute()
            print(f"  Inserted sensor {i+1}/5: pressure {r['hplc_pressure_bar']} bar")
            inserted += 1
        except Exception as e:
            print(f"  SKIPPED sensor {i+1}: {e}")
    return inserted

if __name__ == "__main__":
    print("\nRAIL SYSTEM — DEMO DATA SEEDER")
    print("=" * 60)

    if check_existing():
        print(f"Records for {BATCH_ID} already exist — skipping.")
        print("To re-seed, delete existing records in Supabase first.")
        exit(0)

    print("Inserting run records...")
    r1 = seed_run_records()
    print("\nInserting historical failure...")
    r2 = seed_historical_failure()
    print("\nInserting instrument health records...")
    r3 = seed_instrument_health()
    print("\nInserting sensor logs...")
    r4 = seed_sensor_logs()

    print(f"\n{'='*60}")
    print(f"DONE — {r1} run records | {r2} historical | {r3} health | {r4} sensors")
    print(f"AI correlation, batch record, RCA and instrument health")
    print(f"functions are now ready to demo.")
    print(f"{'='*60}")
