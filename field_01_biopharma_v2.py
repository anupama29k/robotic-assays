# field_01_biopharma_v2.py
# BioInterface — Field 1: Biopharma / CDMO
# VERSION 2.0 — Enhanced schema
# Changes: robot_deck_layout, analyst step labeling, split duration fields,
# structured acceptance_criteria, normalised throughput, environment flags,
# workbench fields, full query API
# Builder: Anu Kozhiyalam

BIOPHARMA_ASSAYS = [
    {
        "assay_id": "BIO_001",
        "name": "Protein A titer by HPLC",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Fc-fusion proteins", "Antibody fragments"],
        "purpose": "Quantify mAb or Fc-fusion protein concentration in harvest or purified samples using Protein A affinity HPLC.",
        "robot_steps": [
            "Pick up sample tubes from input rack at deck position A1 (slots A1:1 through A1:12); centrifuge at 3000 x g for 5 minutes to clarify -- log centrifuge start time.",
            "Transfer 50 uL clarified supernatant from each sample tube to HPLC glass vials at position B1 using 200 uL tips from position D1.",
            "Add 150 uL PBS pH 7.2 mobile phase from reagent reservoir at position C1 to each vial -- mix by aspirating and dispensing 5 times.",
            "Cap HPLC vials and load into HPLC autosampler tray at position G1 according to run sequence loaded at job start.",
            "Load reference standard vials (Protein A calibrator, positions F1:1 through F1:5) into autosampler alongside samples -- log standard lot number.",
            "Load system suitability check vial (known-concentration QC at position F2:1) as first injection.",
            "Initiate HPLC run from instrument control at position H1 -- confirm mobile phase pressure is within 50-300 bar before run start.",
            "Robot monitors for injection complete signal -- confirms UV 280 nm signal detected and peak retention time is within +/-0.2 minutes of expected per injection; flag if outside range.",
            "[ANALYST STEP -- robot pauses and alerts]: Review chromatogram for unexpected peaks, baseline drift, or column pressure anomalies before proceeding with batch.",
            "After all injections complete, robot exports raw peak area data to run file.",
            "Calculate sample concentrations by linear regression against standard curve -- log R-squared and flag if below 0.998.",
            "Flag any samples with concentration outside instrument linear range (0.1-5 mg/mL) for re-injection at appropriate dilution.",
            "Export final titer report to run file; archive raw chromatogram files.",
            "Prime HPLC column with 5 column volumes PBS post-run -- log column flush completion.",
            "Log column injection count -- flag if cumulative injections exceed 500 (column re-qualification threshold)."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x 1.5 mL microcentrifuge tubes",
            "B1": "HPLC glass vial rack -- 48-position",
            "C1": "Reagent reservoir -- PBS pH 7.2 mobile phase (50 mL)",
            "D1": "Tip rack -- 200 uL filtered tips",
            "F1": "Standard rack -- Protein A calibration standards (5 concentrations)",
            "F2": "QC rack -- system suitability check vials",
            "G1": "HPLC autosampler interface position",
            "H1": "HPLC instrument control terminal"
        },
        "workbench_id": "WB1",
        "rail_handoff": None,
        "instruments_needed": ["HPLC with Protein A affinity column", "UV detector (280 nm)", "Centrifuge"],
        "consumables": ["1.5 mL microcentrifuge tubes", "HPLC glass vials with caps", "200 uL filtered pipette tips"],
        "reagents": ["PBS pH 7.2 mobile phase", "Protein A calibration standards (certified lot)", "0.1 M citric acid (elution buffer)", "1 M Tris pH 9.0 (neutralisation buffer)"],
        "throughput_samples_per_run": 24,
        "throughput_notes": "24 samples per hour; 48-vial autosampler tray per batch",
        "robot_active_minutes": 20,
        "total_assay_duration_hours": 2,
        "sample_volume_uL": 50,
        "detection": "UV 280 nm",
        "regulatory": ["ICH Q6B", "USP <1046>", "Ph. Eur. 2.7.9"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "system_suitability_retention_time_cv": "<= 1.0% across 3 injections",
            "standard_curve_r2": ">= 0.998",
            "qc_sample_recovery": "85-115% of known concentration",
            "peak_symmetry_factor": "0.8-1.5",
            "column_pressure_bar": "50-300 bar throughout run"
        },
        # ---- structured criteria pilot (see assay_criteria_schema.py) --------
        # The prose dict above is unchanged and still authoritative for humans.
        # This block restates the same rules in machine-scorable form so a
        # validator can score them without parsing English. Note how many turn
        # out to be project defaults rather than regulatory limits: USP <621>
        # standardises HOW tailing and RSD are calculated, it does not set the
        # numbers. Saying so out loud is the whole point of source_type.
        "acceptance_criteria_structured": [
            {"key": "system_suitability_retention_time_cv", "criterion_type": "replicate_cv", "scope": "run",
             "applies_to": "reference_standard", "min": None, "max": 1.0, "unit": "%",
             "display": "<= 1.0% across 3 injections",
             "source": "Method default (project-defined); calculation methodology per USP <621>",
             "source_type": "project_defined", "machine_scorable": True},
            {"key": "standard_curve_r2", "criterion_type": "curve_r2", "scope": "plate",
             "applies_to": "standard", "min": 0.998, "max": None, "unit": None,
             "display": ">= 0.998",
             "source": "Method default (project-defined); ICH Q2(R2) requires linearity be demonstrated and the coefficient reported, without fixing a threshold",
             "source_type": "project_defined", "machine_scorable": True},
            {"key": "qc_sample_recovery", "criterion_type": "recovery", "scope": "run",
             "applies_to": "qc", "min": 85.0, "max": 115.0, "unit": "% of nominal",
             "display": "85-115% of known concentration",
             "source": "Conventional recovery window for protein titer QC; numerically the same as the ICH M10 bioanalytical window but not itself an ICH requirement for this assay class",
             "source_type": "community_convention", "machine_scorable": True},
            {"key": "peak_symmetry_factor", "criterion_type": "peak_shape", "scope": "run",
             "applies_to": "reference_standard", "min": 0.8, "max": 1.5, "unit": None,
             "display": "0.8-1.5",
             "source": "Method default (project-defined); calculation methodology per USP <621>",
             "source_type": "project_defined", "machine_scorable": True},
            {"key": "column_pressure_bar", "criterion_type": "pressure", "scope": "run",
             "applies_to": "all", "min": 50.0, "max": 300.0, "unit": "bar",
             "display": "50-300 bar throughout run",
             "source": "Protein A column operating window; the 350 bar replacement trigger in notes is the same physical limit",
             "source_type": "instrument_physics", "machine_scorable": True},
        ],
        "well_roles": {
            "sample": {"min": 0.1, "max": 5.0, "unit": "mg/mL",
                       "note": "Instrument linear range. Outside it the sample is re-injected at an appropriate dilution rather than reported -- the same rule robot_steps already applies."},
            "qc": {"min": 85.0, "max": 115.0, "unit": "% of nominal",
                   "note": "System suitability check vial, injected first. It decides whether the batch is interpretable at all."},
            "standard": {"skip": True,
                         "note": "The five Protein A calibrators define the curve; they are scored collectively by standard_curve_r2, not individually against a range."},
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "Protein A column requires conditioning with 5 column volumes PBS before first use each day. If peak retention time drifts > 0.2 minutes, flag for column re-qualification. Replace Protein A column after 500 injections or when back-pressure exceeds 350 bar.",
        "autonomy_level": 1,
        "autonomy_level_reason": "Easy automation with no AutoMATE 96 steps — fixed instrument-driven execution; analyst sets up samples and interprets results manually.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — all liquid transfers are into HPLC glass vials, not 96-well plates.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "F1", "F2", "G1", "H1"],
            "automate_96": ["C1", "D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'centrifuge', "instrument": 'centrifuge', "description": "Pick up sample tubes from input rack at deck position A1 (slots A1:1 through A1:12); centrifuge at 3000 x g for 5 minutes to clarify -- log centrifuge start time.", "parameters": {"rpm": 3000, "duration_seconds": 300}, "duration_seconds": 300},
            {"step_number": 2, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer 50 uL clarified supernatant from each sample tube to HPLC glass vials at position B1 using 200 uL tips from position D1.", "parameters": {"volume_uL": 50.0}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Add 150 uL PBS pH 7.2 mobile phase from reagent reservoir at position C1 to each vial -- mix by aspirating and dispensing 5 times.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Cap HPLC vials and load into HPLC autosampler tray at position G1 according to run sequence loaded at job start.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load reference standard vials (Protein A calibrator, positions F1:1 through F1:5) into autosampler alongside samples -- log standard lot number.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load system suitability check vial (known-concentration QC at position F2:1) as first injection.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Initiate HPLC run from instrument control at position H1 -- confirm mobile phase pressure is within 50-300 bar before run start.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Robot monitors for injection complete signal -- confirms UV 280 nm signal detected and peak retention time is within +/-0.2 minutes of expected per injection; flag if outside range.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Review chromatogram for unexpected peaks, baseline drift, or column pressure anomalies before proceeding with batch.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "After all injections complete, robot exports raw peak area data to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate sample concentrations by linear regression against standard curve -- log R-squared and flag if below 0.998.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any samples with concentration outside instrument linear range (0.1-5 mg/mL) for re-injection at appropriate dilution.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export final titer report to run file; archive raw chromatogram files.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prime HPLC column with 5 column volumes PBS post-run -- log column flush completion.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Log column injection count -- flag if cumulative injections exceed 500 (column re-qualification threshold).", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_002",
        "name": "BCA protein concentration assay",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "Enzyme preparations", "In-process samples"],
        "purpose": "Quantify total protein concentration in purified or in-process samples using bicinchoninic acid (BCA) colorimetric assay.",
        "robot_steps": [
            "Prepare BSA standard curve from 2 mg/mL stock at position F1: 8-point serial dilution from 2000 to 31.25 ug/mL using PBS from position C1 -- dispense 25 uL of each standard into designated wells of 96-well plate at position B1 in duplicate.",
            "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12); aspirate 25 uL per sample and dispense into designated wells per plate map loaded at run start.",
            "Dispense 25 uL PBS blank into wells H11 and H12.",
            "Prepare BCA working reagent: aspirate from reagent A reservoir at position C2 and reagent B at position C3 in 50:1 ratio into mixing tube at position A9 -- sufficient volume for all wells plus 10% excess.",
            "Dispense 200 uL BCA working reagent into all sample, standard, and blank wells.",
            "Seal plate with adhesive film from position D1.",
            "Transfer sealed plate to incubator at position H2 -- incubate at 37C for exactly 30 minutes; log start time.",
            "After incubation, transfer plate to plate reader at position G1 -- allow 5 minutes to equilibrate to room temperature.",
            "Read absorbance at 562 nm -- log raw OD values for all wells.",
            "Subtract blank average (wells H11-H12) from all standards and samples.",
            "Generate linear standard curve -- flag and halt if R-squared < 0.995.",
            "Interpolate sample concentrations; multiply by dilution factor where applicable.",
            "Flag any sample with OD562 > 2.0 (out of linear range) -- log for re-run at 1:10 dilution.",
            "Export results with standard curve parameters and all raw ODs to run file.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm no known BCA interfering agents (DTT, BME, EDTA > 10 mM) are present in sample buffer before signing off results."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x 1.5 mL tubes",
            "A9": "BCA working reagent mixing tube (15 mL conical)",
            "B1": "96-well flat-bottom plate (clear, non-binding)",
            "C1": "Reagent reservoir -- PBS diluent",
            "C2": "Reagent reservoir -- BCA reagent A",
            "C3": "Reagent reservoir -- BCA reagent B",
            "D1": "Adhesive plate seal dispenser",
            "F1": "BSA standard stock (2 mg/mL, 1.5 mL tube)",
            "G1": "Plate reader interface (562 nm)",
            "H2": "Incubator (37C)"
        },
        "workbench_id": "WB1",
        "rail_handoff": None,
        "instruments_needed": ["Plate reader (562 nm)", "37C incubator or plate heater", "Microplate sealer"],
        "consumables": ["96-well flat-bottom plates (clear)", "Adhesive plate seals", "15 mL conical tubes", "200 uL tips"],
        "reagents": ["Pierce BCA reagent A and B", "BSA standard 2 mg/mL (certified lot)", "PBS"],
        "throughput_samples_per_run": 40,
        "throughput_notes": "40 samples per plate in duplicate; ~60 min total run time",
        "robot_active_minutes": 15,
        "total_assay_duration_hours": 1,
        "sample_volume_uL": 25,
        "detection": "Absorbance 562 nm",
        "regulatory": ["ICH Q6B", "USP <1057>"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "standard_curve_r2": ">= 0.995",
            "blank_od562_max": "< 0.10",
            "qc_sample_recovery": "90-110% of expected",
            "duplicate_cv_max": "<= 5%"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "BCA is inhibited by DTT (> 1 mM), beta-mercaptoethanol, and EDTA (> 10 mM). For samples containing reducing agents use Bradford or A280 instead. Warm reagents to room temperature before mixing. Use polypropylene tubes only -- not polycarbonate.",
        "autonomy_level": 2,
        "autonomy_level_reason": "Easy automation with 3 AutoMATE 96 dispense step(s) — robot executes and reads, analyst reviews flagged results.",
        "automate_96_steps": [1, 3, 5],
        "automate_96_head": "5-200uL",
        "automate_96_head_note": "BCA working reagent dispense is 200uL — 5-200uL head covers all plate steps. 25uL standard/blank dispenses also within range. No head change required.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "A9", "B1", "D1", "F1", "G1", "H2"],
            "automate_96": ["C1", "C2", "C3"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare BSA standard curve from 2 mg/mL stock at position F1: 8-point serial dilution from 2000 to 31.25 ug/mL using PBS from position C1 -- dispense 25 uL of each standard into designated wells of 96", "parameters": {"volume_uL": 25.0}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'aspirate', "instrument": 'liquid_handler', "description": "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12); aspirate 25 uL per sample and dispense into designated wells per plate map loaded at run start.", "parameters": {"volume_uL": 25.0}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Dispense 25 uL PBS blank into wells H11 and H12.", "parameters": {"volume_uL": 25.0}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Prepare BCA working reagent: aspirate from reagent A reservoir at position C2 and reagent B at position C3 in 50:1 ratio into mixing tube at position A9 -- sufficient volume for all wells plus 10% exc", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Dispense 200 uL BCA working reagent into all sample, standard, and blank wells.", "parameters": {"volume_uL": 200.0}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'pierce_seal', "instrument": 'plate_sealer', "description": "Seal plate with adhesive film from position D1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'incubate', "instrument": 'incubator', "description": "Transfer sealed plate to incubator at position H2 -- incubate at 37C for exactly 30 minutes; log start time.", "parameters": {"temperature_C": 37.0, "duration_seconds": 1800}, "duration_seconds": 1800},
            {"step_number": 8, "step_type": 'incubate', "instrument": 'incubator', "description": "After incubation, transfer plate to plate reader at position G1 -- allow 5 minutes to equilibrate to room temperature.", "parameters": {"duration_seconds": 300}, "duration_seconds": 300},
            {"step_number": 9, "step_type": 'read', "instrument": 'plate_reader', "description": "Read absorbance at 562 nm -- log raw OD values for all wells.", "parameters": {"wavelength_nm": 562}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Subtract blank average (wells H11-H12) from all standards and samples.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Generate linear standard curve -- flag and halt if R-squared < 0.995.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Interpolate sample concentrations; multiply by dilution factor where applicable.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'read', "instrument": 'plate_reader', "description": "Flag any sample with OD562 > 2.0 (out of linear range) -- log for re-run at 1:10 dilution.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'read', "instrument": 'plate_reader', "description": "Export results with standard curve parameters and all raw ODs to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Confirm no known BCA interfering agents (DTT, BME, EDTA > 10 mM) are present in sample buffer before signing off results.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_003",
        "name": "SEC-HPLC aggregation analysis",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Bispecific antibodies", "Fc-fusion proteins", "ADCs"],
        "purpose": "Quantify monomer, dimer, and high-molecular-weight species (HMWS) in purified mAb samples by size-exclusion chromatography.",
        "robot_steps": [
            "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12); centrifuge at 10,000 x g for 5 minutes to remove particulates.",
            "Transfer 100 uL clarified sample to HPLC glass vials at position B1; add 100 uL PBS mobile phase from reservoir at position C1 -- mix by gentle pipetting.",
            "Load reference standard vials (mAb reference with known aggregate profile) from position F1 into HPLC autosampler at position G1.",
            "Load system suitability vial (thyroglobulin MW standards) from position F2:1 into autosampler position 1 -- run as first injection.",
            "Load prepared sample vials into autosampler positions 2 onwards per run sequence.",
            "Confirm mobile phase (PBS pH 7.2, 0.22 um filtered) pressure is 50-200 bar before initiating run.",
            "Initiate SEC-HPLC run -- 20-minute runtime per injection at 0.5 mL/min; UV detection at 280 nm.",
            "Robot monitors for injection complete signal and confirms UV 280 nm trace is detected per injection.",
            "After all injections, export peak area data for each species (HMWS, monomer, LMWS) to run file.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm thyroglobulin standard shows expected retention time (+/-0.5 min) and theoretical plates >= 8000 before accepting run.",
            "Calculate %HMWS, %monomer, %LMWS from peak areas -- log values per sample.",
            "Flag any samples with %HMWS > 2% as exceeding standard investigation threshold.",
            "Compare reference standard monomer % to historical mean -- flag if drift > +/-1%.",
            "Export aggregate profile report to run file; archive raw chromatograms.",
            "Prime column with 5 column volumes PBS post-run -- log flush."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x 1.5 mL tubes",
            "B1": "HPLC glass vial rack -- 48-position",
            "C1": "Reagent reservoir -- PBS pH 7.2 mobile phase",
            "D1": "Tip rack -- 200 uL tips",
            "F1": "Reference standard rack -- mAb reference",
            "F2": "MW standard rack -- thyroglobulin",
            "G1": "HPLC autosampler interface",
            "H1": "HPLC instrument control"
        },
        "workbench_id": "WB1",
        "rail_handoff": None,
        "instruments_needed": ["HPLC with SEC column (e.g. TSKgel G3000SWxL)", "UV detector (280 nm)", "Centrifuge"],
        "consumables": ["HPLC glass vials with caps", "200 uL tips", "1.5 mL tubes"],
        "reagents": ["PBS pH 7.2 mobile phase (0.22 um filtered)", "Reference mAb standard", "Thyroglobulin MW standard"],
        "throughput_samples_per_run": 12,
        "throughput_notes": "12 samples per autosampler tray; 20 min per injection",
        "robot_active_minutes": 15,
        "total_assay_duration_hours": 5,
        "sample_volume_uL": 100,
        "detection": "UV 280 nm",
        "regulatory": ["ICH Q6B", "USP <1045>", "Ph. Eur. 2.2.30"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "system_suitability_column_plates": ">= 8000 theoretical plates (thyroglobulin)",
            "reference_standard_monomer_drift": "<= +/-1.0% from historical mean",
            "hmws_investigation_threshold": ">= 2% triggers investigation",
            "peak_resolution_monomer_dimer": ">= 1.5",
            "retention_time_reproducibility_cv": "<= 0.5%"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "SEC column stored in 20% ethanol when not in use. Do not inject samples containing > 0.5% polysorbate without method validation. Run reference standard at start and end of each sequence to bracket samples.",
        "autonomy_level": 1,
        "autonomy_level_reason": "Easy automation with no AutoMATE 96 steps — fixed instrument-driven execution; analyst sets up samples and interprets results manually.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — all liquid transfers are into HPLC glass vials.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "F1", "F2", "G1", "H1"],
            "automate_96": ["C1", "D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'centrifuge', "instrument": 'centrifuge', "description": "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12); centrifuge at 10,000 x g for 5 minutes to remove particulates.", "parameters": {"rpm": 10000, "duration_seconds": 300}, "duration_seconds": 300},
            {"step_number": 2, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Transfer 100 uL clarified sample to HPLC glass vials at position B1; add 100 uL PBS mobile phase from reservoir at position C1 -- mix by gentle pipetting.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load reference standard vials (mAb reference with known aggregate profile) from position F1 into HPLC autosampler at position G1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load system suitability vial (thyroglobulin MW standards) from position F2:1 into autosampler position 1 -- run as first injection.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load prepared sample vials into autosampler positions 2 onwards per run sequence.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Confirm mobile phase (PBS pH 7.2, 0.22 um filtered) pressure is 50-200 bar before initiating run.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Initiate SEC-HPLC run -- 20-minute runtime per injection at 0.5 mL/min; UV detection at 280 nm.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Robot monitors for injection complete signal and confirms UV 280 nm trace is detected per injection.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "After all injections, export peak area data for each species (HMWS, monomer, LMWS) to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Confirm thyroglobulin standard shows expected retention time (+/-0.5 min) and theoretical plates >= 8000 before accepting run.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate %HMWS, %monomer, %LMWS from peak areas -- log values per sample.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any samples with %HMWS > 2% as exceeding standard investigation threshold.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Compare reference standard monomer % to historical mean -- flag if drift > +/-1%.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export aggregate profile report to run file; archive raw chromatograms.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prime column with 5 column volumes PBS post-run -- log flush.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_004",
        "name": "Cell viability and density by Vi-CELL or Cedex",
        "field": "Biopharma / CDMO",
        "product_types": ["CHO cell culture", "HEK293 culture", "Hybridoma culture"],
        "purpose": "Measure viable cell density (VCD) and viability (%) in bioreactor or shake flask samples using automated image-based trypan blue exclusion counting.",
        "robot_steps": [
            "Pick up bioreactor sample tubes from input rack at position A1 (A1:1 through A1:8) -- confirm samples are at room temperature; log collection time.",
            "Vortex each sample tube for 3 seconds at position H1 to ensure homogeneous cell suspension.",
            "Transfer 500 uL of each sample to Vi-CELL sample cups at position B1 using 1 mL tips from position D1.",
            "Load Vi-CELL sample cups into instrument carousel at position G1 -- confirm cup positions match run sequence.",
            "Confirm trypan blue reagent reservoir in instrument is > 30% full before run -- log level.",
            "Initiate Vi-CELL run -- instrument acquires 50 images per sample; estimated 3-4 minutes per sample.",
            "Robot monitors for instrument complete signal after each sample.",
            "Retrieve results: VCD (cells/mL), viability (%), mean cell diameter (um), aggregate %.",
            "Flag any sample with viability < 70% -- log as process concern, alert operator immediately.",
            "Flag any sample with aggregate % > 15% -- log for microscopy review.",
            "[ANALYST STEP -- robot pauses and alerts]: Review flagged samples under inverted microscope at position H2 before clearing for process use.",
            "Log VCD and viability data against process day for trend tracking.",
            "Run 2 instrument cleaning cycles with cleaning solution at position H3 at run end.",
            "Export VCD and viability report to run file with timestamp.",
            "Archive all Vi-CELL image files for the run."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 8 x 15 mL conicals or sample tubes",
            "B1": "Vi-CELL sample cup rack -- 8 positions",
            "D1": "Tip rack -- 1 mL tips",
            "G1": "Vi-CELL / Cedex instrument carousel interface",
            "H1": "Vortex mixer",
            "H2": "Inverted microscope (analyst review station)",
            "H3": "Instrument cleaning station"
        },
        "workbench_id": "WB2",
        "rail_handoff": None,
        "instruments_needed": ["Vi-CELL XR or Cedex HiRes automated cell counter", "Vortex mixer", "Inverted microscope (analyst)"],
        "consumables": ["Vi-CELL sample cups", "1 mL pipette tips", "15 mL conical tubes"],
        "reagents": ["Trypan blue 0.4% w/v (instrument grade)", "Vi-CELL cleaning solution"],
        "throughput_samples_per_run": 8,
        "throughput_notes": "8 samples per run; ~4 min per sample including wash cycle",
        "robot_active_minutes": 10,
        "total_assay_duration_hours": 1,
        "sample_volume_uL": 500,
        "detection": "Image-based automated cell counting (trypan blue exclusion)",
        "regulatory": ["ICH Q5D", "USP <1010>"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "calibration_beads_cv": "<= 5% CV on standardisation beads (run daily)",
            "viability_alert_threshold": "< 70% triggers immediate operator alert",
            "aggregate_alert_threshold": "> 15% triggers microscopy review",
            "instrument_blank": "< 1e4 cells/mL background particle count"
        },
        "environment_requirement": "Standard lab bench (BSL-1); BSL-2 if handling lentiviral or AAV producer cells",
        "platform_compatibility": "Full for standard CHO/HEK cultures; Conditional for viral producer cell lines (BSL-2 required)",
        "notes": "Run calibration beads at start of each day and after instrument cleaning. For suspension cultures with clumps, pre-treat with 0.05% collagenase before analysis. Cell diameter changes can indicate osmotic stress -- trend alongside VCD/viability.",
        "autonomy_level": 1,
        "autonomy_level_reason": "Easy automation with no AutoMATE 96 steps — fixed instrument-driven execution; analyst sets up samples and interprets results manually.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — all transfers are into Vi-CELL sample cups, which are not in 96-well plate format.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "G1", "H1", "H3"],
            "automate_96": ["D1"],
            "analyst": ["H2"]
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up bioreactor sample tubes from input rack at position A1 (A1:1 through A1:8) -- confirm samples are at room temperature; log collection time.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Vortex each sample tube for 3 seconds at position H1 to ensure homogeneous cell suspension.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer 500 uL of each sample to Vi-CELL sample cups at position B1 using 1 mL tips from position D1.", "parameters": {"volume_uL": 500.0}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load Vi-CELL sample cups into instrument carousel at position G1 -- confirm cup positions match run sequence.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Confirm trypan blue reagent reservoir in instrument is > 30% full before run -- log level.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Initiate Vi-CELL run -- instrument acquires 50 images per sample; estimated 3-4 minutes per sample.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Robot monitors for instrument complete signal after each sample.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Retrieve results: VCD (cells/mL), viability (%), mean cell diameter (um), aggregate %.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any sample with viability < 70% -- log as process concern, alert operator immediately.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any sample with aggregate % > 15% -- log for microscopy review.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Review flagged samples under inverted microscope at position H2 before clearing for process use.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Log VCD and viability data against process day for trend tracking.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Run 2 instrument cleaning cycles with cleaning solution at position H3 at run end.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export VCD and viability report to run file with timestamp.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Archive all Vi-CELL image files for the run.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_005",
        "name": "Sandwich ELISA -- target antigen quantification",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Bispecific antibodies", "Cytokines", "In-process samples"],
        "purpose": "Quantify target antigen or product-related impurity concentration in process samples using a validated sandwich ELISA.",
        "robot_steps": [
            "Pick up 96-well ELISA plate (high-binding) from position B1.",
            "Aspirate 100 uL capture antibody (2-4 ug/mL in PBS) from reservoir at position C1; dispense into all 96 wells.",
            "Seal plate with adhesive film from position D1; transfer to 4C refrigerator for overnight coat -- log incubation start time and confirm refrigerator temperature.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm overnight coat is complete and plate seal is intact before resuming next morning.",
            "Remove seal; aspirate contents to liquid waste at position E1.",
            "Wash all wells with 300 uL PBST from reservoir at position C2 -- repeat 3 times; aspirate completely after each wash.",
            "Aspirate 200 uL blocking buffer (1% BSA-PBST) from position C3 into all wells; incubate 1 hour at room temperature.",
            "Aspirate blocking buffer; perform 3-cycle PBST wash.",
            "Prepare sample serial dilutions in 96-well dilution plate at position B2 from input rack at position A1 -- 3-fold dilutions.",
            "Transfer 100 uL diluted samples and standards into ELISA plate per plate map; dispense 100 uL standard curve (8-point, 2-fold, from position F1) into designated wells.",
            "Seal and incubate 2 hours at room temperature -- log start and end times.",
            "Perform 3-cycle PBST wash.",
            "Aspirate 100 uL HRP-detection antibody from position C4 into all wells; incubate 1 hour.",
            "Perform 3-cycle PBST wash.",
            "Aspirate 100 uL TMB substrate from position C5; dispense into all wells -- incubate exactly 10 minutes in dark; log start time.",
            "Aspirate 100 uL stop solution (2N H2SO4) from position C6; dispense into all wells in same order as substrate addition.",
            "Transfer plate to reader at position G1; read OD450 with reference at 620 nm -- log raw values.",
            "Flag wells with OD450 > 3.0 (saturation) for repeat at higher dilution.",
            "Calculate concentrations using 4-parameter logistic (4PL) fit of standard curve -- export to run file.",
            "Flag samples where all dilutions fall outside linear portion of 4PL curve -- require assay repeat at adjusted dilution range."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x 1.5 mL tubes",
            "B1": "96-well ELISA plate (high-binding, flat-bottom)",
            "B2": "96-well dilution plate (non-binding)",
            "C1": "Reagent reservoir -- capture antibody in PBS",
            "C2": "Reagent reservoir -- PBST wash buffer",
            "C3": "Reagent reservoir -- blocking buffer (1% BSA-PBST)",
            "C4": "Reagent reservoir -- HRP detection antibody",
            "C5": "Reagent reservoir -- TMB substrate",
            "C6": "Reagent reservoir -- stop solution (2N H2SO4)",
            "D1": "Adhesive plate seal dispenser",
            "E1": "Liquid waste container",
            "F1": "Standard rack -- antigen reference standard (top concentration)",
            "G1": "Plate reader interface (450/620 nm)"
        },
        "workbench_id": "WB1",
        "rail_handoff": None,
        "instruments_needed": ["Plate reader (450/620 nm)", "Plate washer or multichannel aspirator", "Microplate sealer", "4C refrigerator"],
        "consumables": ["96-well flat-bottom ELISA plates (high-binding)", "96-well non-binding dilution plates", "Adhesive plate seals", "Reagent reservoirs"],
        "reagents": ["Capture antibody (validated lot)", "HRP-detection antibody", "TMB substrate", "Stop solution 2N H2SO4", "BSA blocking buffer", "PBST", "Reference antigen standard (certified lot)"],
        "throughput_samples_per_run": 40,
        "throughput_notes": "40 samples per plate in duplicate; includes overnight coat",
        "robot_active_minutes": 45,
        "total_assay_duration_hours": 20,
        "sample_volume_uL": 100,
        "detection": "Absorbance 450 nm (reference 620 nm)",
        "regulatory": ["ICH Q6B", "USP <1106>", "Ph. Eur. 2.7.1"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "standard_curve_r2": ">= 0.995 (4PL fit)",
            "curve_bottom_asymptote_od": "< 0.10",
            "curve_top_asymptote_od": "> 1.5",
            "qc_sample_recovery": "80-120% of expected",
            "ppc_recovery": "70-130% of spike concentration",
            "intraplate_cv_max": "<= 15%"
        },
        "environment_requirement": "Standard lab bench (BSL-1); 4C refrigerator for overnight coat step",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "4PL regression mandatory -- linear interpolation not acceptable for ELISA. Minimum assay range must bracket expected sample concentrations. If all samples fall outside linear portion of curve, repeat at adjusted dilution.",
        "autonomy_level": 3,
        "autonomy_level_reason": "Medium difficulty with 11 AutoMATE 96 dispense step(s) across a 20-step protocol — robot reads results and flags anomalies; analyst decides only on exceptions.",
        "automate_96_steps": [2, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16],
        "automate_96_head": "5-200uL",
        "automate_96_head_note": "Primary dispense volumes 100-200uL (capture antibody, blocking, samples, detection, substrate, stop) — 5-200uL head covers all steps. 300uL PBST wash exceeds head capacity; either split into 2x150uL dispenses or switch to 100-1000uL head for wash cycles.",
        "automate_96_head_change": True,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "B2", "D1", "E1", "F1", "G1"],
            "automate_96": ["C1", "C2", "C3", "C4", "C5", "C6"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up 96-well ELISA plate (high-binding) from position B1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'read', "instrument": 'plate_reader', "description": "Aspirate 100 uL capture antibody (2-4 ug/mL in PBS) from reservoir at position C1; dispense into all 96 wells.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'incubate', "instrument": 'incubator', "description": "Seal plate with adhesive film from position D1; transfer to 4C refrigerator for overnight coat -- log incubation start time and confirm refrigerator temperature.", "parameters": {"temperature_C": 4.0}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'pierce_seal', "instrument": 'plate_sealer', "description": "-- robot pauses and alerts: Confirm overnight coat is complete and plate seal is intact before resuming next morning.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'pierce_seal', "instrument": 'plate_sealer', "description": "Remove seal; aspirate contents to liquid waste at position E1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'aspirate', "instrument": 'liquid_handler', "description": "Wash all wells with 300 uL PBST from reservoir at position C2 -- repeat 3 times; aspirate completely after each wash.", "parameters": {"volume_uL": 300.0}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'incubate', "instrument": 'incubator', "description": "Aspirate 200 uL blocking buffer (1% BSA-PBST) from position C3 into all wells; incubate 1 hour at room temperature.", "parameters": {"duration_seconds": 3600}, "duration_seconds": 3600},
            {"step_number": 8, "step_type": 'aspirate', "instrument": 'liquid_handler', "description": "Aspirate blocking buffer; perform 3-cycle PBST wash.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare sample serial dilutions in 96-well dilution plate at position B2 from input rack at position A1 -- 3-fold dilutions.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer 100 uL diluted samples and standards into ELISA plate per plate map; dispense 100 uL standard curve (8-point, 2-fold, from position F1) into designated wells.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'incubate', "instrument": 'incubator', "description": "Seal and incubate 2 hours at room temperature -- log start and end times.", "parameters": {"duration_seconds": 7200}, "duration_seconds": 7200},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Perform 3-cycle PBST wash.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'incubate', "instrument": 'incubator', "description": "Aspirate 100 uL HRP-detection antibody from position C4 into all wells; incubate 1 hour.", "parameters": {"duration_seconds": 3600}, "duration_seconds": 3600},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Perform 3-cycle PBST wash.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'incubate', "instrument": 'incubator', "description": "Aspirate 100 uL TMB substrate from position C5; dispense into all wells -- incubate exactly 10 minutes in dark; log start time.", "parameters": {"duration_seconds": 600}, "duration_seconds": 600},
            {"step_number": 16, "step_type": 'aspirate', "instrument": 'liquid_handler', "description": "Aspirate 100 uL stop solution (2N H2SO4) from position C6; dispense into all wells in same order as substrate addition.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 17, "step_type": 'read', "instrument": 'plate_reader', "description": "Transfer plate to reader at position G1; read OD450 with reference at 620 nm -- log raw values.", "parameters": {"wavelength_nm": 620}, "duration_seconds": 30},
            {"step_number": 18, "step_type": 'read', "instrument": 'plate_reader', "description": "Flag wells with OD450 > 3.0 (saturation) for repeat at higher dilution.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 19, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate concentrations using 4-parameter logistic (4PL) fit of standard curve -- export to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 20, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag samples where all dilutions fall outside linear portion of 4PL curve -- require assay repeat at adjusted dilution range.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_006",
        "name": "Endotoxin testing -- LAL kinetic turbidimetric",
        "field": "Biopharma / CDMO",
        "product_types": ["All injectable biologics", "mAb drug substance", "In-process samples"],
        "purpose": "Quantify bacterial endotoxin in biologic drug substance or in-process samples using kinetic turbidimetric LAL to confirm compliance with release limits.",
        "robot_steps": [
            "Confirm all labware is depyrogenated or certified endotoxin-free -- log lot numbers of LRW, LAL reagent, and CSE.",
            "Prepare CSE standard curve from position F1: 8-point 2-fold dilution from 50 EU/mL to 0.39 EU/mL in LRW at position C1.",
            "Dispense 100 uL of each standard concentration into duplicate wells of 96-well LAL plate at position B1.",
            "Prepare positive product controls (PPC): spike endotoxin into sample matrix at 2x MVD-adjusted concentration -- dispense 100 uL per PPC well.",
            "Calculate MVD for each sample: MVD = (Endotoxin Limit x concentration) / lambda -- log MVD per sample.",
            "Prepare sample dilutions in LRW at 3 dilution levels per sample from input rack at position A1 -- dispense 100 uL per well.",
            "Dispense 100 uL negative control (LRW only) into wells H11-H12.",
            "Reconstitute LAL reagent from position C2 -- gently swirl, do not vortex; log reconstitution time.",
            "Dispense 100 uL LAL reagent into all sample, standard, and control wells -- mix gently by pipetting 5 times without introducing bubbles.",
            "Transfer plate immediately to plate reader at position G1 preheated to 37C -- initiate kinetic turbidimetric read at 340 nm, 1 reading per minute for 60 minutes.",
            "Flag in real time any wells where onset time falls outside standard curve range.",
            "Verify standard curve log-log linear regression R-squared >= 0.980 -- abort report generation if below.",
            "Verify PPC recovery 50-200% -- invalidate run if any PPC outside range.",
            "Verify negative controls show no onset within run time.",
            "Calculate sample endotoxin concentrations accounting for MVD; compare to specification -- flag any exceedances.",
            "Export LAL report with curve statistics, PPC recoveries, and all sample results to run file."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x endotoxin-free 1.5 mL tubes",
            "B1": "96-well LAL plate (depyrogenated)",
            "C1": "Reagent reservoir -- LAL reagent water (LRW), certified",
            "C2": "LAL reagent vial (kinetic turbidimetric, in ice bucket)",
            "D1": "Tip rack -- endotoxin-free foil-wrapped tips",
            "F1": "CSE standard vials (control standard endotoxin)",
            "G1": "Kinetic plate reader (37C, 340 nm)"
        },
        "workbench_id": "WB3",
        "rail_handoff": None,
        "instruments_needed": ["Kinetic plate reader (37C, 340 nm)", "Depyrogenated pipettes and tips"],
        "consumables": ["96-well LAL plates (depyrogenated)", "Endotoxin-free tubes", "Endotoxin-free foil-wrapped tips"],
        "reagents": ["Kinetic turbidimetric LAL reagent", "Control standard endotoxin (CSE)", "LAL reagent water (LRW)"],
        "throughput_samples_per_run": 20,
        "throughput_notes": "20 samples per plate (3 dilutions + PPC per sample, duplicate); 90 min total",
        "robot_active_minutes": 30,
        "total_assay_duration_hours": 1.5,
        "sample_volume_uL": 100,
        "detection": "Turbidimetry 340 nm (kinetic onset time)",
        "regulatory": ["USP <85>", "EP 2.6.14", "Ph. Eur. 2.6.14"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "standard_curve_r2": ">= 0.980 (log-log linear regression)",
            "ppc_recovery_percent": "50-200%",
            "negative_control": "No turbidimetric onset detected within run time",
            "dilution_concordance": "Results at different MVD dilutions within 2-fold of each other"
        },
        "environment_requirement": "Standard lab bench (BSL-1); all labware must be depyrogenated (250C, 30 min) or certified endotoxin-free",
        "platform_compatibility": "Full -- dedicated endotoxin-free labware set required on this deck",
        "notes": "Inhibition/enhancement testing (IET) required for new product matrices or changed reagent lots. If IET shows > 50% inhibition or > 200% enhancement at MVD, sample must be further diluted or alternative method validated.",
        "autonomy_level": 3,
        "autonomy_level_reason": "Medium difficulty with 6 AutoMATE 96 dispense step(s) across a 16-step protocol — robot reads results and flags anomalies; analyst decides only on exceptions.",
        "automate_96_steps": [2, 3, 4, 6, 7, 9],
        "automate_96_head": "5-200uL",
        "automate_96_head_note": "All dispenses are 100uL (standards, PPCs, samples, negative controls, LAL reagent) — 5-200uL head covers every plate step. No head change required.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "F1", "G1"],
            "automate_96": ["C1", "C2", "D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Confirm all labware is depyrogenated or certified endotoxin-free -- log lot numbers of LRW, LAL reagent, and CSE.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare CSE standard curve from position F1: 8-point 2-fold dilution from 50 EU/mL to 0.39 EU/mL in LRW at position C1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Dispense 100 uL of each standard concentration into duplicate wells of 96-well LAL plate at position B1.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'read', "instrument": 'plate_reader', "description": "Prepare positive product controls (PPC): spike endotoxin into sample matrix at 2x MVD-adjusted concentration -- dispense 100 uL per PPC well.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate MVD for each sample: MVD = (Endotoxin Limit x concentration) / lambda -- log MVD per sample.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare sample dilutions in LRW at 3 dilution levels per sample from input rack at position A1 -- dispense 100 uL per well.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Dispense 100 uL negative control (LRW only) into wells H11-H12.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Reconstitute LAL reagent from position C2 -- gently swirl, do not vortex; log reconstitution time.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'read', "instrument": 'plate_reader', "description": "Dispense 100 uL LAL reagent into all sample, standard, and control wells -- mix gently by pipetting 5 times without introducing bubbles.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'read', "instrument": 'plate_reader', "description": "Transfer plate immediately to plate reader at position G1 preheated to 37C -- initiate kinetic turbidimetric read at 340 nm, 1 reading per minute for 60 minutes.", "parameters": {"wavelength_nm": 340}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag in real time any wells where onset time falls outside standard curve range.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Verify standard curve log-log linear regression R-squared >= 0.980 -- abort report generation if below.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Verify PPC recovery 50-200% -- invalidate run if any PPC outside range.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Verify negative controls show no onset within run time.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate sample endotoxin concentrations accounting for MVD; compare to specification -- flag any exceedances.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 16, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export LAL report with curve statistics, PPC recoveries, and all sample results to run file.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_007",
        "name": "Recombinant factor C (rFC) endotoxin assay",
        "field": "Biopharma / CDMO",
        "product_types": ["All injectable biologics", "Cell culture media", "Process intermediates"],
        "purpose": "Detect and quantify bacterial endotoxin using recombinant factor C (rFC) fluorescence-based assay as an animal-free alternative to LAL.",
        "robot_steps": [
            "Confirm all labware is certified endotoxin-free and all reagents are within expiry -- log lot numbers.",
            "Prepare rFC assay buffer from concentrate at position C1 per kit instructions -- mix gently; keep on ice.",
            "Prepare endotoxin standard curve from position F1: 8-point dilution from 10 EU/mL to 0.02 EU/mL in rFC buffer.",
            "Dispense 100 uL each standard into duplicate wells of black 96-well plate at position B1.",
            "Prepare PPC: spike endotoxin at 2x MVD concentration into sample matrix from position F1 -- dispense 100 uL per PPC well.",
            "Prepare sample dilutions at MVD and 2x MVD in rFC buffer from input rack at position A1 -- dispense 100 uL per well.",
            "Add 100 uL negative control (rFC buffer only) to designated wells.",
            "Prepare rFC working reagent: combine rFC enzyme, fluorescent substrate (Boc-Leu-Gly-Arg-AMC), and buffer per kit insert from position C2 -- prepare fresh and protect from light immediately.",
            "Dispense 100 uL rFC working reagent to all wells; mix by gently tapping plate.",
            "Seal plate with foil seal from position D1 -- protect from light throughout incubation.",
            "Transfer plate to incubator at position H2 -- incubate at 37C for exactly 60 minutes; log start time.",
            "Transfer plate to fluorescence reader at position G1; read emission at 440 nm (excitation 380 nm).",
            "Verify standard curve R-squared >= 0.980 -- abort if below.",
            "Verify PPC recovery 50-200% -- invalidate if outside.",
            "Calculate sample endotoxin concentrations accounting for MVD; flag exceedances.",
            "Export rFC report with all fluorescence values and QC outcomes to run file."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x endotoxin-free 1.5 mL tubes",
            "B1": "Black 96-well flat-bottom plate (endotoxin-free)",
            "C1": "Reagent reservoir -- rFC assay buffer",
            "C2": "rFC working reagent components (kit tubes, on ice, light-protected)",
            "D1": "Foil plate seal dispenser",
            "F1": "Endotoxin standard vials (CSE)",
            "G1": "Fluorescence plate reader (Ex 380 nm / Em 440 nm)",
            "H2": "Incubator (37C, light-excluded)"
        },
        "workbench_id": "WB3",
        "rail_handoff": None,
        "instruments_needed": ["Fluorescence plate reader (Ex 380 / Em 440 nm)", "37C incubator (light-excluded)"],
        "consumables": ["Black 96-well flat-bottom plates (endotoxin-free)", "Endotoxin-free foil seals", "Endotoxin-free tips"],
        "reagents": ["rFC endotoxin detection kit (PyroGene or equivalent)", "Control standard endotoxin (CSE)", "Endotoxin-free water"],
        "throughput_samples_per_run": 20,
        "throughput_notes": "20 samples per plate (2 dilutions + PPC, duplicate); 90 min total",
        "robot_active_minutes": 25,
        "total_assay_duration_hours": 1.5,
        "sample_volume_uL": 100,
        "detection": "Fluorescence Ex 380 nm / Em 440 nm (AMC release)",
        "regulatory": ["USP <85> (alternative methods)", "Ph. Eur. 2.6.32"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "standard_curve_r2": ">= 0.980",
            "ppc_recovery_percent": "50-200%",
            "negative_control_fluorescence": "Below lowest standard signal",
            "duplicate_cv_max": "<= 25% (endotoxin assays have wider tolerance)"
        },
        "environment_requirement": "Standard lab bench (BSL-1); endotoxin-free labware required; rFC reagent must be light-protected throughout",
        "platform_compatibility": "Full -- dedicated endotoxin-free labware set and light-protection protocol required",
        "notes": "rFC is not sensitive to (1->3)-beta-D-glucans unlike LAL -- advantage for certain matrices. Regulatory acceptance of rFC as sole release method varies by market -- confirm with regulatory strategy before substituting for LAL in formal release testing.",
        "autonomy_level": 3,
        "autonomy_level_reason": "Medium difficulty with 6 AutoMATE 96 dispense step(s) across a 16-step protocol — robot reads results and flags anomalies; analyst decides only on exceptions.",
        "automate_96_steps": [3, 4, 5, 6, 7, 9],
        "automate_96_head": "5-200uL",
        "automate_96_head_note": "All dispenses are 100uL (standards, PPC, samples, negative controls, rFC working reagent) — 5-200uL head covers every plate step. No head change required.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "D1", "F1", "G1", "H2"],
            "automate_96": ["C1", "C2"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Confirm all labware is certified endotoxin-free and all reagents are within expiry -- log lot numbers.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Prepare rFC assay buffer from concentrate at position C1 per kit instructions -- mix gently; keep on ice.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare endotoxin standard curve from position F1: 8-point dilution from 10 EU/mL to 0.02 EU/mL in rFC buffer.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Dispense 100 uL each standard into duplicate wells of black 96-well plate at position B1.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare PPC: spike endotoxin at 2x MVD concentration into sample matrix from position F1 -- dispense 100 uL per PPC well.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare sample dilutions at MVD and 2x MVD in rFC buffer from input rack at position A1 -- dispense 100 uL per well.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Add 100 uL negative control (rFC buffer only) to designated wells.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Prepare rFC working reagent: combine rFC enzyme, fluorescent substrate (Boc-Leu-Gly-Arg-AMC), and buffer per kit insert from position C2 -- prepare fresh and protect from light immediately.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Dispense 100 uL rFC working reagent to all wells; mix by gently tapping plate.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'incubate', "instrument": 'incubator', "description": "Seal plate with foil seal from position D1 -- protect from light throughout incubation.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'incubate', "instrument": 'incubator', "description": "Transfer plate to incubator at position H2 -- incubate at 37C for exactly 60 minutes; log start time.", "parameters": {"temperature_C": 37.0, "duration_seconds": 3600}, "duration_seconds": 3600},
            {"step_number": 12, "step_type": 'read', "instrument": 'plate_reader', "description": "Transfer plate to fluorescence reader at position G1; read emission at 440 nm (excitation 380 nm).", "parameters": {"wavelength_nm": 440}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Verify standard curve R-squared >= 0.980 -- abort if below.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Verify PPC recovery 50-200% -- invalidate if outside.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate sample endotoxin concentrations accounting for MVD; flag exceedances.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 16, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export rFC report with all fluorescence values and QC outcomes to run file.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_008",
        "name": "Mycoplasma detection by PCR",
        "field": "Biopharma / CDMO",
        "product_types": ["CHO cell banks", "HEK293 cell banks", "Hybridoma cultures", "Viral vector producer cells"],
        "purpose": "Detect mycoplasma contamination in cell culture samples using PCR-based detection as a rapid alternative to compendial culture methods.",
        "robot_steps": [
            "Pick up cell culture supernatant samples from input rack at position A1 (A1:1 through A1:8) -- confirm samples at room temperature.",
            "Transfer 200 uL per sample to DNA extraction tubes at position A9.",
            "Add 200 uL lysis buffer from position C1 to each tube; vortex 10 seconds at position H1.",
            "Incubate at 65C for 10 minutes in heat block at position H2 -- log start time.",
            "Add 10 uL magnetic beads from position C2; mix by pipetting 10 times; incubate 5 minutes at room temperature.",
            "Place tubes on magnetic rack at position D2 for 2 minutes until beads pellet; aspirate and discard supernatant to waste at position E1.",
            "Wash with 200 uL wash buffer 1 (position C3) -- resuspend, magnet, aspirate. Repeat twice.",
            "Wash with 200 uL wash buffer 2 (position C4) -- resuspend, magnet, aspirate. Once.",
            "Elute with 50 uL elution buffer (position C5, pre-heated to 70C in H2) for 5 minutes; transfer eluate to PCR plate at position B1.",
            "Set up qPCR reactions in 96-well qPCR plate at position B2: 10 uL 2x master mix + 0.5 uL forward primer + 0.5 uL reverse primer + 2 uL template + 7 uL nuclease-free water per reaction.",
            "Include mycoplasma-positive control (position F1) in well H11 and nuclease-free water negative control (position F2) in well H12.",
            "Seal qPCR plate with optical film from position D1; transfer to qPCR instrument at position G1.",
            "Run programme: 95C 5 min; 45 x (95C 15s, 60C 60s); melting curve 65-95C.",
            "Monitor Ct in real time -- positive control must show Ct < 35; negative control must show no amplification.",
            "[ANALYST STEP -- robot pauses and alerts]: Review melting curve for each presumptive positive -- confirm single peak at expected Tm before calling result.",
            "Call each sample pass (Ct > 40 or undetermined) or fail (Ct <= 40) -- export qPCR report to run file.",
            "Flag any failures for immediate QA escalation and batch quarantine."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 8 x 1.5 mL tubes (cell culture supernatant)",
            "A9": "Extraction tube rack -- 8 x 1.5 mL tubes",
            "B1": "Eluate collection rack -- 8 x 0.2 mL PCR tubes",
            "B2": "96-well qPCR plate",
            "C1": "Lysis buffer reservoir",
            "C2": "Magnetic bead tube",
            "C3": "Wash buffer 1 reservoir",
            "C4": "Wash buffer 2 reservoir",
            "C5": "Elution buffer (70C, at H2)",
            "D1": "Optical qPCR plate seal",
            "D2": "Magnetic rack",
            "E1": "Liquid waste container",
            "F1": "Mycoplasma-positive control DNA tube",
            "F2": "Nuclease-free water (negative control)",
            "G1": "qPCR instrument interface",
            "H1": "Vortex mixer",
            "H2": "Heat block (65C / 70C dual zone)"
        },
        "workbench_id": "WB2",
        "rail_handoff": None,
        "instruments_needed": ["Real-time qPCR instrument", "Heat block (65C/70C)", "Magnetic rack", "Vortex mixer"],
        "consumables": ["0.2 mL PCR strip tubes", "96-well qPCR plates", "Optical qPCR seals", "1.5 mL microcentrifuge tubes"],
        "reagents": ["qPCR master mix (2x, with ROX)", "Mycoplasma-specific validated primer set", "Magnetic bead extraction kit", "Nuclease-free water", "Mycoplasma-positive control DNA"],
        "throughput_samples_per_run": 8,
        "throughput_notes": "8 samples per run; ~3 hr total including extraction and qPCR",
        "robot_active_minutes": 60,
        "total_assay_duration_hours": 3,
        "sample_volume_uL": 200,
        "detection": "Real-time fluorescence qPCR (SYBR Green or TaqMan)",
        "regulatory": ["ICH Q5A", "USP <63>", "Ph. Eur. 2.6.7"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "positive_control_ct": "Ct < 35",
            "negative_control": "No amplification (Ct > 40 or undetermined)",
            "melting_curve": "Single peak at expected Tm +/- 1C",
            "sample_fail_threshold": "Ct <= 40 = mycoplasma detected (FAIL)"
        },
        "environment_requirement": "Standard lab bench (BSL-1); PCR-dedicated area strongly recommended to prevent amplicon contamination",
        "platform_compatibility": "Full -- PCR-dedicated deck area recommended; shared deck risk of amplicon contamination",
        "notes": "PCR screening does not replace compendial culture method (USP <63>) for formal cell bank characterisation. Confirm positives with culture-based method. Primer design must cover >= 40 mycoplasma species per ICH Q5A guidance.",
        "autonomy_level": 2,
        "autonomy_level_reason": "Easy automation with 1 AutoMATE 96 dispense step(s) — robot executes and reads, analyst reviews flagged results.",
        "automate_96_steps": [10],
        "automate_96_head": "1-20uL",
        "automate_96_head_note": "Only plate-based step is qPCR setup with sub-10uL dispenses (10uL master mix, 0.5uL primers, 2uL template, 7uL water). All extraction steps are tube-based, not AutoMATE 96 territory. 1-20uL head required for low-volume qPCR reagents.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "A9", "B1", "B2", "D1", "D2", "E1", "F1", "F2", "G1", "H1", "H2"],
            "automate_96": ["C1", "C2", "C3", "C4", "C5"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up cell culture supernatant samples from input rack at position A1 (A1:1 through A1:8) -- confirm samples at room temperature.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer 200 uL per sample to DNA extraction tubes at position A9.", "parameters": {"volume_uL": 200.0}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Add 200 uL lysis buffer from position C1 to each tube; vortex 10 seconds at position H1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'incubate', "instrument": 'incubator', "description": "Incubate at 65C for 10 minutes in heat block at position H2 -- log start time.", "parameters": {"temperature_C": 65.0, "duration_seconds": 600}, "duration_seconds": 600},
            {"step_number": 5, "step_type": 'incubate', "instrument": 'incubator', "description": "Add 10 uL magnetic beads from position C2; mix by pipetting 10 times; incubate 5 minutes at room temperature.", "parameters": {"duration_seconds": 300}, "duration_seconds": 300},
            {"step_number": 6, "step_type": 'magnetic_separation', "instrument": 'magnetic_separator', "description": "Place tubes on magnetic rack at position D2 for 2 minutes until beads pellet; aspirate and discard supernatant to waste at position E1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'magnetic_separation', "instrument": 'magnetic_separator', "description": "Wash with 200 uL wash buffer 1 (position C3) -- resuspend, magnet, aspirate. Repeat twice.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'magnetic_separation', "instrument": 'magnetic_separator', "description": "Wash with 200 uL wash buffer 2 (position C4) -- resuspend, magnet, aspirate. Once.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Elute with 50 uL elution buffer (position C5, pre-heated to 70C in H2) for 5 minutes; transfer eluate to PCR plate at position B1.", "parameters": {"volume_uL": 50.0}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Set up qPCR reactions in 96-well qPCR plate at position B2: 10 uL 2x master mix + 0.5 uL forward primer + 0.5 uL reverse primer + 2 uL template + 7 uL nuclease-free water per reaction.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Include mycoplasma-positive control (position F1) in well H11 and nuclease-free water negative control (position F2) in well H12.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'pierce_seal', "instrument": 'plate_sealer', "description": "Seal qPCR plate with optical film from position D1; transfer to qPCR instrument at position G1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Run programme: 95C 5 min; 45 x (95C 15s, 60C 60s); melting curve 65-95C.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Monitor Ct in real time -- positive control must show Ct < 35; negative control must show no amplification.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Review melting curve for each presumptive positive -- confirm single peak at expected Tm before calling result.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 16, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Call each sample pass (Ct > 40 or undetermined) or fail (Ct <= 40) -- export qPCR report to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 17, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any failures for immediate QA escalation and batch quarantine.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_009",
        "name": "Bioburden testing by membrane filtration",
        "field": "Biopharma / CDMO",
        "product_types": ["Drug substance bulk", "In-process samples", "Formulated drug product pre-fill"],
        "purpose": "Enumerate total viable aerobic microbial count in process samples by membrane filtration onto compendial growth media plates.",
        "robot_steps": [
            "Confirm ISO Class 5 (Grade A) laminar flow environment is operational -- log particle count and air velocity before starting.",
            "Pre-wet 0.45 um membrane filters with 10 mL sterile peptone water from position C1 in membrane filtration manifold at position H1.",
            "Pick up sample from position A1 -- aspirate specified test volume (typically 10 mL) using sterile serological pipette from position D1.",
            "Transfer sample onto pre-wetted membrane -- apply vacuum until completely filtered; log filter appearance after filtration.",
            "Rinse membrane 3 times with 10 mL sterile peptone water per rinse -- apply vacuum after each rinse until dry.",
            "[ANALYST STEP -- robot pauses and alerts]: Visually inspect membrane for cracks, holes, or uneven wetting before transfer -- reject and repeat if membrane integrity is compromised.",
            "Transfer membrane aseptically to SCDA agar plate at position B1 (total aerobic count) using sterile forceps from position D2.",
            "Transfer duplicate membrane to SDA agar plate at position B2 (yeast and mould count).",
            "Label both plates with sample ID, date, batch number, and analyst initials.",
            "Transfer SCDA plates to incubator at 30-35C at position H2; SDA plates to incubator at 20-25C at position H3 -- log incubation start times.",
            "[ANALYST STEP -- robot pauses and alerts]: Count colonies on SCDA plates at day 3 and day 5; count SDA plates at day 3 and day 5 -- record counts; robot cannot perform colony counting.",
            "Positive control (S. aureus ATCC 6538, 10-100 CFU from position F1) must show growth by day 2 -- invalidate run if positive control fails.",
            "Negative control (rinse water only) must show zero colonies at day 5.",
            "Calculate CFU/mL for each sample -- compare to specification limit.",
            "Export bioburden report with colony counts, incubation logs, and pass/fail status to run file.",
            "Archive plate photographs at incubation endpoint."
        ],
        "robot_deck_layout": {
            "A1": "Sample input -- sterile sample container (test volume)",
            "B1": "SCDA agar plates (30-35C incubation group)",
            "B2": "SDA agar plates (20-25C incubation group)",
            "C1": "Sterile peptone water reservoir (100 mL)",
            "D1": "Sterile serological pipettes (25 mL, in holder)",
            "D2": "Sterile forceps (in sterile packaging)",
            "F1": "Positive control organism suspension (S. aureus, 10-100 CFU/mL)",
            "H1": "Membrane filtration manifold (vacuum-driven, Grade A BSC-adjacent)",
            "H2": "Incubator 30-35C",
            "H3": "Incubator 20-25C"
        },
        "workbench_id": "WB3",
        "rail_handoff": None,
        "instruments_needed": ["Membrane filtration unit (vacuum manifold)", "ISO Class 5 laminar flow cabinet", "Two incubators (30-35C and 20-25C)"],
        "consumables": ["0.45 um cellulose nitrate membranes (47 mm)", "SCDA agar plates", "SDA agar plates", "Sterile forceps", "Sterile serological pipettes"],
        "reagents": ["Sterile peptone water (rinse)", "Positive control organisms (ATCC certified strains)"],
        "throughput_samples_per_run": 4,
        "throughput_notes": "4 samples per run (1 membrane per sample, 2 agar media); 5-day incubation to result",
        "robot_active_minutes": 45,
        "total_assay_duration_hours": 120,
        "sample_volume_uL": 10000,
        "detection": "Colony counting (analyst -- visual) on agar plates",
        "regulatory": ["USP <61>", "EP 2.6.12", "Ph. Eur. 2.6.12"],
        "automation_difficulty": "complex",
        "acceptance_criteria": {
            "positive_control_growth": "Confirmed growth by day 2",
            "negative_control": "Zero colonies at day 5",
            "membrane_integrity": "No cracks, tears, or uneven wetting confirmed before transfer",
            "specification_limit": "Per product specification (e.g. <= 100 CFU/mL for drug substance)"
        },
        "environment_requirement": "ISO Class 5 (Grade A) laminar flow cabinet mandatory for filtration and membrane transfer; robot must operate within or immediately adjacent to BSC",
        "platform_compatibility": "Conditional -- ISO Class 5 environment is a regulatory requirement; standard bench deployment not permitted for this assay",
        "notes": "Robot automates sample loading, filtration, and plate setup. Colony counting (step 11) is analyst-only -- robot flags plates for analyst review at day 3 and day 5. Preservative-containing samples require validated neutralisation before membrane filtration.",
        "autonomy_level": 4,
        "autonomy_level_reason": "Complex automation difficulty — robot makes go/no-go decisions on multi-stage workflows; analyst sets goals only.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — entire workflow is membrane filtration + agar plate transfer under ISO Class 5. AutoMATE 96 not used in this assay.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "B2", "D1", "D2", "F1", "H1", "H2", "H3"],
            "automate_96": ["C1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Confirm ISO Class 5 (Grade A) laminar flow environment is operational -- log particle count and air velocity before starting.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Pre-wet 0.45 um membrane filters with 10 mL sterile peptone water from position C1 in membrane filtration manifold at position H1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'aspirate', "instrument": 'liquid_handler', "description": "Pick up sample from position A1 -- aspirate specified test volume (typically 10 mL) using sterile serological pipette from position D1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Transfer sample onto pre-wetted membrane -- apply vacuum until completely filtered; log filter appearance after filtration.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Rinse membrane 3 times with 10 mL sterile peptone water per rinse -- apply vacuum after each rinse until dry.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "-- robot pauses and alerts: Visually inspect membrane for cracks, holes, or uneven wetting before transfer -- reject and repeat if membrane integrity is compromised.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer membrane aseptically to SCDA agar plate at position B1 (total aerobic count) using sterile forceps from position D2.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer duplicate membrane to SDA agar plate at position B2 (yeast and mould count).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Label both plates with sample ID, date, batch number, and analyst initials.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'incubate', "instrument": 'incubator', "description": "Transfer SCDA plates to incubator at 30-35C at position H2; SDA plates to incubator at 20-25C at position H3 -- log incubation start times.", "parameters": {"temperature_C": 35.0}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Count colonies on SCDA plates at day 3 and day 5; count SDA plates at day 3 and day 5 -- record counts; robot cannot perform colony counting.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Positive control (S. aureus ATCC 6538, 10-100 CFU from position F1) must show growth by day 2 -- invalidate run if positive control fails.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Negative control (rinse water only) must show zero colonies at day 5.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate CFU/mL for each sample -- compare to specification limit.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'incubate', "instrument": 'incubator', "description": "Export bioburden report with colony counts, incubation logs, and pass/fail status to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 16, "step_type": 'incubate', "instrument": 'incubator', "description": "Archive plate photographs at incubation endpoint.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_010",
        "name": "Osmolality measurement by freezing-point depression",
        "field": "Biopharma / CDMO",
        "product_types": ["Drug substance", "Drug product formulations", "Cell culture media", "Process buffers"],
        "purpose": "Measure osmolality of biopharmaceutical formulations and process solutions to confirm isotonicity and formulation consistency.",
        "robot_steps": [
            "Switch on osmometer at position H1 -- allow 30-minute warm-up; confirm instrument stability.",
            "[ANALYST STEP -- robot pauses and alerts]: Perform two-point calibration with 290 mOsm/kg and 100 mOsm/kg certified standards from positions F1 and F2 -- log calibration result and slope before proceeding.",
            "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12).",
            "Transfer 200 uL of each sample to osmometry cups at position B1 using 200 uL tips from position D1 -- ensure no air bubbles in cups.",
            "Load 290 mOsm/kg verification standard (position F1) as cup 1 and final cup in run to bracket all samples.",
            "Load sample cups into osmometer autosampler at position H1 in sequence matching run file.",
            "Initiate osmometer run -- instrument immerses probe, freezes sample, measures onset of freezing; approximately 90 seconds per sample.",
            "Rinse osmometer probe with ultrapure water from instrument internal reservoir between each sample -- log rinse completion.",
            "Retrieve osmolality reading (mOsm/kg) for each sample after each measurement.",
            "Flag any sample outside specification (typically 270-350 mOsm/kg for isotonic formulations).",
            "Verify bracketing calibration standards are within +/-10 mOsm/kg of certified value -- invalidate run if outside range.",
            "Export osmolality report with all readings and pass/fail vs specification to run file.",
            "Rinse osmometer probe with 3 cycles of ultrapure water at run end -- log cleaning.",
            "Archive run report.",
            "Log instrument calibration status -- flag if calibration is approaching expiry per instrument SOP."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x 1.5 mL tubes",
            "B1": "Osmometry cup rack (12-position)",
            "D1": "Tip rack -- 200 uL tips",
            "F1": "290 mOsm/kg certified calibration standard",
            "F2": "100 mOsm/kg certified calibration standard",
            "H1": "Freezing-point osmometer with autosampler"
        },
        "workbench_id": "WB2",
        "rail_handoff": None,
        "instruments_needed": ["Freezing-point osmometer (Advanced Instruments or equivalent)", "Certified calibration standards"],
        "consumables": ["Osmometry sample cups (instrument-compatible)", "200 uL tips"],
        "reagents": ["290 mOsm/kg certified standard", "100 mOsm/kg certified standard", "Ultrapure water"],
        "throughput_samples_per_run": 12,
        "throughput_notes": "12 samples per run; ~2 min per sample including probe rinse",
        "robot_active_minutes": 10,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 200,
        "detection": "Freezing-point depression (thermistor)",
        "regulatory": ["USP <785>", "Ph. Eur. 2.2.35", "ICH Q6B"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "bracketing_standards_tolerance": "Within +/-10 mOsm/kg of certified value",
            "instrument_drift": "< 5 mOsm/kg between sequential standard measurements",
            "specification_range": "Per product specification (typically 270-350 mOsm/kg)"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "Protein-rich samples (> 50 mg/mL) can foul osmometer probe -- clean with 0.1% SDS if protein carryover is suspected. Calibration must be performed at start of each day. For low-ionic-strength buffers, allow extra equilibration time.",
        "autonomy_level": 1,
        "autonomy_level_reason": "Easy automation with no AutoMATE 96 steps — fixed instrument-driven execution; analyst sets up samples and interprets results manually.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — osmometry uses dedicated instrument sample cups (non-microplate format). AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "F1", "F2", "H1"],
            "automate_96": ["D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Switch on osmometer at position H1 -- allow 30-minute warm-up; confirm instrument stability.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Perform two-point calibration with 290 mOsm/kg and 100 mOsm/kg certified standards from positions F1 and F2 -- log calibration result and slope before proceeding.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer 200 uL of each sample to osmometry cups at position B1 using 200 uL tips from position D1 -- ensure no air bubbles in cups.", "parameters": {"volume_uL": 200.0}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load 290 mOsm/kg verification standard (position F1) as cup 1 and final cup in run to bracket all samples.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load sample cups into osmometer autosampler at position H1 in sequence matching run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Initiate osmometer run -- instrument immerses probe, freezes sample, measures onset of freezing; approximately 90 seconds per sample.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Rinse osmometer probe with ultrapure water from instrument internal reservoir between each sample -- log rinse completion.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Retrieve osmolality reading (mOsm/kg) for each sample after each measurement.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any sample outside specification (typically 270-350 mOsm/kg for isotonic formulations).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Verify bracketing calibration standards are within +/-10 mOsm/kg of certified value -- invalidate run if outside range.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export osmolality report with all readings and pass/fail vs specification to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Rinse osmometer probe with 3 cycles of ultrapure water at run end -- log cleaning.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Archive run report.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Log instrument calibration status -- flag if calibration is approaching expiry per instrument SOP.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_011",
        "name": "pH and conductivity measurement",
        "field": "Biopharma / CDMO",
        "product_types": ["Drug substance", "Process buffers", "Cell culture media", "In-process samples"],
        "purpose": "Measure pH and conductivity of process solutions and formulations to confirm buffer composition, formulation identity, and process control.",
        "robot_steps": [
            "Switch on pH meter at position H1 and conductivity meter at position H2 -- allow 15-minute warm-up and electrode stabilisation.",
            "[ANALYST STEP -- robot pauses and alerts]: Perform two-point pH calibration using pH 4.0 and pH 7.0 certified buffers from positions F1 and F2 -- confirm slope 95-105% before proceeding.",
            "[ANALYST STEP -- robot pauses and alerts]: Calibrate conductivity meter using certified standard from position F3 -- confirm reading within +/-2% of certified value.",
            "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12).",
            "Transfer 2 mL of each sample to measurement cups at position B1 using 1 mL tips from position D1.",
            "Immerse pH electrode into first sample cup -- wait 30 seconds for stabilisation; record pH to 0.01 resolution.",
            "Rinse pH electrode with ultrapure water from position C1 (3 x 500 uL) between samples; blot dry with lint-free tissue.",
            "Repeat pH measurement for all 12 samples -- log each result.",
            "Immerse conductivity probe into first sample cup -- wait 20 seconds for stabilisation; record conductivity (mS/cm).",
            "Rinse conductivity probe with ultrapure water between samples.",
            "Repeat conductivity measurement for all 12 samples -- log each result.",
            "Flag any pH outside +/-0.1 pH units of target or conductivity outside +/-5% of target.",
            "Verify pH calibration: re-read pH 7.0 buffer at end of run -- must read within +/-0.05 pH units; flag if outside.",
            "Export pH and conductivity report with all readings and pass/fail status to run file.",
            "Store electrodes in appropriate solutions -- pH electrode in KCl 3M; conductivity probe in ultrapure water; log storage condition."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x 1.5 mL tubes",
            "B1": "Measurement cup rack (12-position, 5 mL cups)",
            "C1": "Ultrapure water reservoir (electrode rinse)",
            "D1": "Tip rack -- 1 mL tips",
            "F1": "pH 4.0 certified calibration buffer",
            "F2": "pH 7.0 certified calibration buffer",
            "F3": "Conductivity standard (1413 uS/cm certified)",
            "H1": "Calibrated pH meter with combination electrode",
            "H2": "Calibrated conductivity meter with probe"
        },
        "workbench_id": "WB2",
        "rail_handoff": None,
        "instruments_needed": ["Calibrated pH meter (+/-0.01 resolution)", "Calibrated conductivity meter", "Certified calibration buffers and standards"],
        "consumables": ["5 mL measurement cups", "1 mL tips", "Lint-free tissues", "Electrode storage solutions"],
        "reagents": ["pH 4.0 certified buffer", "pH 7.0 certified buffer", "Conductivity standard 1413 uS/cm", "Ultrapure water", "KCl 3M (electrode storage)"],
        "throughput_samples_per_run": 12,
        "throughput_notes": "12 samples per run for both pH and conductivity in single pass; ~1.5 min per sample",
        "robot_active_minutes": 15,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 2000,
        "detection": "Potentiometric (pH); conductimetric (conductivity)",
        "regulatory": ["USP <791>", "USP <645>", "Ph. Eur. 2.2.3", "Ph. Eur. 2.2.38"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "ph_calibration_slope": "95-105%",
            "conductivity_calibration_accuracy": "Within +/-2% of certified standard",
            "end_of_run_ph_verification": "pH 7.0 buffer reads within +/-0.05 pH units",
            "ph_specification_tolerance": "+/-0.1 pH units of target",
            "conductivity_specification_tolerance": "+/-5% of target"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "pH electrodes must be stored in KCl 3M -- never stored dry or in water. Replace pH electrode when slope falls below 90% or response time exceeds 2 minutes. Conductivity is temperature-dependent; report at 25C or apply temperature compensation.",
        "autonomy_level": 1,
        "autonomy_level_reason": "Easy automation with no AutoMATE 96 steps — fixed instrument-driven execution; analyst sets up samples and interprets results manually.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — pH and conductivity measured via direct electrode immersion into individual sample cups. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "F1", "F2", "F3", "H1", "H2"],
            "automate_96": ["C1", "D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'read', "instrument": 'plate_reader', "description": "Switch on pH meter at position H1 and conductivity meter at position H2 -- allow 15-minute warm-up and electrode stabilisation.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Perform two-point pH calibration using pH 4.0 and pH 7.0 certified buffers from positions F1 and F2 -- confirm slope 95-105% before proceeding.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Calibrate conductivity meter using certified standard from position F3 -- confirm reading within +/-2% of certified value.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer 2 mL of each sample to measurement cups at position B1 using 1 mL tips from position D1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'read', "instrument": 'plate_reader', "description": "Immerse pH electrode into first sample cup -- wait 30 seconds for stabilisation; record pH to 0.01 resolution.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'read', "instrument": 'plate_reader', "description": "Rinse pH electrode with ultrapure water from position C1 (3 x 500 uL) between samples; blot dry with lint-free tissue.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Repeat pH measurement for all 12 samples -- log each result.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Immerse conductivity probe into first sample cup -- wait 20 seconds for stabilisation; record conductivity (mS/cm).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Rinse conductivity probe with ultrapure water between samples.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Repeat conductivity measurement for all 12 samples -- log each result.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any pH outside +/-0.1 pH units of target or conductivity outside +/-5% of target.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Verify pH calibration: re-read pH 7.0 buffer at end of run -- must read within +/-0.05 pH units; flag if outside.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export pH and conductivity report with all readings and pass/fail status to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'read', "instrument": 'plate_reader', "description": "Store electrodes in appropriate solutions -- pH electrode in KCl 3M; conductivity probe in ultrapure water; log storage condition.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_012",
        "name": "Subvisible particle count by light obscuration",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Bispecific antibodies", "Drug product formulations", "ADCs"],
        "purpose": "Count and size subvisible particles (>=2 um, >=5 um, >=10 um, >=25 um) in injectable drug products per compendial requirements.",
        "robot_steps": [
            "Switch on HIAC light obscuration particle counter at position G1 -- allow 30-minute warm-up; confirm laser alignment and sensor calibration status.",
            "Flush sensor with 5 volumes particle-free water from position C1 -- verify background particle count < 5 particles/mL at >= 10 um.",
            "If background exceeds limit, repeat flush cycle up to 3 times -- abort and alert for service if still failing.",
            "Pick up sample containers from input rack at position A1 -- gently invert each 20 times to resuspend particles without creating bubbles.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm sample has been degassed (no visible bubbles) and is at room temperature before proceeding.",
            "Aspirate 5 mL from first sample container using 5 mL sterile syringe from position D1 -- aspirate slowly to avoid generating air bubbles.",
            "Inject sample into HIAC sensor at position G1 at 10 mL/min flow rate -- discard first 1 mL as priming volume.",
            "Collect 4 x 1 mL aliquots per sample per USP <787> requirements; record particle count at >=2 um, >=5 um, >=10 um, >=25 um per aliquot.",
            "Calculate mean and standard deviation across 4 aliquots -- flag if CV > 25% between aliquots (indicates sample heterogeneity).",
            "Flush sensor with particle-free water between samples -- verify background returns to < 5 particles/mL.",
            "Repeat for all samples in run.",
            "Compare results to USP <787> specification: <=6000 particles/container >=10 um; <=600 particles/container >=25 um.",
            "Flag any sample exceeding specification -- log for QA investigation.",
            "Export particle count report with per-aliquot data, means, and pass/fail status to run file.",
            "Flush and park sensor at run end -- log cleaning."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 8 x 20 mL glass vials or PFS containers",
            "C1": "Particle-free water reservoir (USP-grade, 0.22 um filtered)",
            "D1": "Sterile syringe rack -- 5 mL syringes",
            "G1": "HIAC light obscuration particle counter (with sensor and autosampler)"
        },
        "workbench_id": "WB2",
        "rail_handoff": None,
        "instruments_needed": ["HIAC 9703+ light obscuration particle counter", "Sterile syringes (5 mL)"],
        "consumables": ["5 mL sterile syringes", "Particle-free water (USP-grade)"],
        "reagents": ["Particle-free water (USP-grade, 0.22 um filtered)", "Count-Cal size standards (optional daily QC)"],
        "throughput_samples_per_run": 8,
        "throughput_notes": "8 samples per run; ~5 min per sample including flush cycles",
        "robot_active_minutes": 15,
        "total_assay_duration_hours": 1,
        "sample_volume_uL": 5000,
        "detection": "Light obscuration (laser diode sensor)",
        "regulatory": ["USP <787>", "USP <788>", "Ph. Eur. 2.9.19"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "background_particle_count": "< 5 particles/mL at >= 10 um",
            "usp787_10um_limit": "<= 6000 particles/container at >= 10 um",
            "usp787_25um_limit": "<= 600 particles/container at >= 25 um",
            "aliquot_cv": "<= 25% across 4 x 1 mL aliquots"
        },
        "environment_requirement": "Standard lab bench (BSL-1); ISO Class 7 or better recommended to minimise background contamination",
        "platform_compatibility": "Full -- particle-free water supply and clean environment recommended",
        "notes": "Air bubbles are the primary source of false-positive particle counts -- ensure samples are fully degassed. For silicone oil-containing prefilled syringes, use MFI or flow imaging for morphological differentiation of protein particles vs oil droplets.",
        "autonomy_level": 2,
        "autonomy_level_reason": "Medium difficulty without AutoMATE 96 dispensing — robot executes instrument-based reads; analyst reviews flagged results.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — HIAC particle counter is a syringe-based flow instrument, not plate-based. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "D1", "G1"],
            "automate_96": ["C1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Switch on HIAC light obscuration particle counter at position G1 -- allow 30-minute warm-up; confirm laser alignment and sensor calibration status.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flush sensor with 5 volumes particle-free water from position C1 -- verify background particle count < 5 particles/mL at >= 10 um.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "If background exceeds limit, repeat flush cycle up to 3 times -- abort and alert for service if still failing.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up sample containers from input rack at position A1 -- gently invert each 20 times to resuspend particles without creating bubbles.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Confirm sample has been degassed (no visible bubbles) and is at room temperature before proceeding.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'aspirate', "instrument": 'liquid_handler', "description": "Aspirate 5 mL from first sample container using 5 mL sterile syringe from position D1 -- aspirate slowly to avoid generating air bubbles.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Inject sample into HIAC sensor at position G1 at 10 mL/min flow rate -- discard first 1 mL as priming volume.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Collect 4 x 1 mL aliquots per sample per USP <787> requirements; record particle count at >=2 um, >=5 um, >=10 um, >=25 um per aliquot.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate mean and standard deviation across 4 aliquots -- flag if CV > 25% between aliquots (indicates sample heterogeneity).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flush sensor with particle-free water between samples -- verify background returns to < 5 particles/mL.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Repeat for all samples in run.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Compare results to USP <787> specification: <=6000 particles/container >=10 um; <=600 particles/container >=25 um.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag any sample exceeding specification -- log for QA investigation.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export particle count report with per-aliquot data, means, and pass/fail status to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flush and park sensor at run end -- log cleaning.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_013",
        "name": "IEX-HPLC charge variant analysis (CEX/AEX)",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Bispecific antibodies", "Fc-fusion proteins"],
        "purpose": "Resolve and quantify acidic, main, and basic charge variant species in mAb drug substance by ion-exchange chromatography for product quality assessment.",
        "robot_steps": [
            "Pick up sample tubes from input rack at position A1 (A1:1 through A1:8); verify sample concentration is 1-5 mg/mL.",
            "If sample requires buffer exchange: transfer 200 uL to desalting spin columns at position A9 pre-equilibrated in IEX mobile phase A; centrifuge at 1500 x g for 2 minutes.",
            "Transfer 100 uL buffer-exchanged sample to HPLC glass vials at position B1.",
            "Load reference standard (well-characterised mAb reference with known charge variant profile) from position F1 into autosampler at position G1.",
            "Load system suitability check standard from position F2 as first injection.",
            "Load sample vials into autosampler per run sequence.",
            "Confirm both mobile phase A (20 mM MES pH 5.6) and B (20 mM MES pH 5.6 + 500 mM NaCl) reservoirs are sufficient -- minimum 200 mL each.",
            "Initiate gradient run: 0-60 min linear gradient 0-50% B at 0.8 mL/min; UV 280 nm detection; column temperature 30C.",
            "Robot monitors for each injection complete signal and confirms UV trace detected.",
            "After all injections, export peak area data for acidic, main, and basic species groups to run file.",
            "[ANALYST STEP -- robot pauses and alerts]: Review chromatogram integration -- confirm peak grouping boundaries (acidic/main/basic) match validated method integration parameters.",
            "Calculate % acidic, % main, % basic from relative peak areas.",
            "Compare reference standard charge profile to historical mean -- flag if any group drifts > +/-2%.",
            "Export charge variant report to run file; archive raw chromatograms.",
            "Wash column with 10 column volumes 100% B, then re-equilibrate with 10 column volumes 100% A -- log column maintenance."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 8 x 1.5 mL tubes",
            "A9": "Desalting spin columns (pre-equilibrated in mobile phase A)",
            "B1": "HPLC glass vial rack -- 24-position",
            "C1": "Mobile phase A reservoir -- 20 mM MES pH 5.6",
            "C2": "Mobile phase B reservoir -- 20 mM MES pH 5.6 + 500 mM NaCl",
            "D1": "Tip rack -- 200 uL tips",
            "F1": "Reference standard -- mAb charge variant reference",
            "F2": "System suitability standard",
            "G1": "HPLC autosampler interface (column at 30C)"
        },
        "workbench_id": "WB1",
        "rail_handoff": None,
        "instruments_needed": ["HPLC with binary gradient pump and column heater (30C)", "CEX column (ProPac WCX-10 or equivalent)", "UV detector (280 nm)"],
        "consumables": ["HPLC glass vials with caps", "200 uL tips", "Desalting spin columns"],
        "reagents": ["20 mM MES pH 5.6 (mobile phase A)", "20 mM MES pH 5.6 + 500 mM NaCl (mobile phase B)", "mAb charge variant reference standard"],
        "throughput_samples_per_run": 8,
        "throughput_notes": "8 samples per run; 70 min per injection including wash and re-equilibration",
        "robot_active_minutes": 20,
        "total_assay_duration_hours": 10,
        "sample_volume_uL": 100,
        "detection": "UV 280 nm",
        "regulatory": ["ICH Q6B", "ICH Q2(R2)"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "system_suitability_main_peak_rt": "Within +/-0.5 min of expected",
            "reference_standard_drift": "<= +/-2% for any charge group vs historical mean",
            "peak_resolution_acidic_main": ">= 1.0",
            "column_back_pressure": "< 200 bar"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "Charge variant profiles are product-specific and method-specific -- integration parameters must match validated method exactly. Column temperature at 30C is critical for reproducibility. Mobile phase pH must be verified to +/-0.05 before each run.",
        "autonomy_level": 2,
        "autonomy_level_reason": "Medium difficulty without AutoMATE 96 dispensing — robot executes instrument-based reads; analyst reviews flagged results.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — all sample prep is into HPLC glass vials. Desalting spin columns are tube-based. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "A9", "B1", "F1", "F2", "G1"],
            "automate_96": ["C1", "C2", "D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up sample tubes from input rack at position A1 (A1:1 through A1:8); verify sample concentration is 1-5 mg/mL.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'centrifuge', "instrument": 'centrifuge', "description": "If sample requires buffer exchange: transfer 200 uL to desalting spin columns at position A9 pre-equilibrated in IEX mobile phase A; centrifuge at 1500 x g for 2 minutes.", "parameters": {"rpm": 1500, "duration_seconds": 120}, "duration_seconds": 120},
            {"step_number": 3, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer 100 uL buffer-exchanged sample to HPLC glass vials at position B1.", "parameters": {"volume_uL": 100.0}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load reference standard (well-characterised mAb reference with known charge variant profile) from position F1 into autosampler at position G1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load system suitability check standard from position F2 as first injection.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load sample vials into autosampler per run sequence.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Confirm both mobile phase A (20 mM MES pH 5.6) and B (20 mM MES pH 5.6 + 500 mM NaCl) reservoirs are sufficient -- minimum 200 mL each.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Initiate gradient run: 0-60 min linear gradient 0-50% B at 0.8 mL/min; UV 280 nm detection; column temperature 30C.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Robot monitors for each injection complete signal and confirms UV trace detected.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "After all injections, export peak area data for acidic, main, and basic species groups to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'read', "instrument": 'plate_reader', "description": "-- robot pauses and alerts: Review chromatogram integration -- confirm peak grouping boundaries (acidic/main/basic) match validated method integration parameters.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate % acidic, % main, % basic from relative peak areas.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Compare reference standard charge profile to historical mean -- flag if any group drifts > +/-2%.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export charge variant report to run file; archive raw chromatograms.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Wash column with 10 column volumes 100% B, then re-equilibrate with 10 column volumes 100% A -- log column maintenance.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_014",
        "name": "SDS-PAGE and gel imaging",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "ADCs", "Bispecific antibodies"],
        "purpose": "Assess molecular weight, purity, and structural integrity under reducing and non-reducing conditions using SDS-PAGE with Coomassie or silver staining.",
        "robot_steps": [
            "Prepare reducing samples: mix sample + LDS sample buffer + reducing agent (DTT) from positions C1, C2, C3 in PCR tubes at position A9 -- target 2-5 ug protein per lane.",
            "Prepare non-reducing samples: mix sample + LDS sample buffer (no DTT) in separate PCR tubes.",
            "Heat reducing samples at 70C for 10 minutes in heat block at position H1 -- log start/end times; non-reducing samples remain at room temperature.",
            "Cool reducing samples to room temperature -- 5 minutes minimum.",
            "Remove pre-cast gel (4-12% Bis-Tris) from position B1; rinse wells 3x with running buffer from position C4 using multichannel.",
            "Load 10 uL MW ladder (position F1) into lane 1 and last lane using 10 uL gel-loading tips from position D1.",
            "Load 10-15 uL each sample into designated lanes per lane map loaded at run start -- dispense at bottom of well slowly.",
            "Log lane assignments with sample IDs, reducing/non-reducing designation, and load volumes.",
            "Assemble gel cassette into electrophoresis tank at position H2; fill with MES SDS running buffer from position C4.",
            "Connect to power supply -- run at 200V constant for 35 minutes; robot monitors run completion.",
            "[ANALYST STEP -- robot pauses and alerts]: Check dye front has reached bottom of gel before stopping run.",
            "Remove gel from cassette; transfer to staining tray at position H3.",
            "Stain: add SimplyBlue Coomassie stain from position C5; incubate 1 hour on orbital shaker.",
            "Destain: rinse 3x with ultrapure water; leave in water until background is clear.",
            "Transfer gel to gel imaging system at position G1 -- capture white-light image.",
            "Export gel image to run file; log band pattern observations per lane."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 12 x 1.5 mL tubes",
            "A9": "PCR tube strip rack -- sample preparation",
            "B1": "Pre-cast gel storage (4-12% Bis-Tris NuPAGE gel)",
            "C1": "LDS sample buffer reservoir",
            "C2": "DTT reducing agent tube",
            "C3": "Non-reducing sample buffer reservoir",
            "C4": "MES SDS running buffer reservoir",
            "C5": "SimplyBlue Coomassie stain",
            "D1": "Gel-loading tips (10 uL, narrow bore)",
            "F1": "MW ladder tube (pre-stained protein standard)",
            "G1": "Gel imaging system (white light)",
            "H1": "Heat block (70C)",
            "H2": "Gel electrophoresis tank with power supply",
            "H3": "Staining tray on orbital shaker"
        },
        "workbench_id": "WB1",
        "rail_handoff": None,
        "instruments_needed": ["NuPAGE gel electrophoresis system", "Power supply (200V)", "Heat block (70C)", "Gel imaging system", "Orbital shaker"],
        "consumables": ["4-12% Bis-Tris NuPAGE gels", "10 uL gel-loading tips", "PCR tube strips", "Staining trays"],
        "reagents": ["LDS sample buffer", "DTT reducing agent", "MES SDS running buffer", "SimplyBlue Coomassie stain", "Pre-stained MW ladder", "Ultrapure water"],
        "throughput_samples_per_run": 10,
        "throughput_notes": "10 samples per gel (reduced + non-reduced = 2 lanes per sample); 2.5 hr total",
        "robot_active_minutes": 30,
        "total_assay_duration_hours": 2.5,
        "sample_volume_uL": 15,
        "detection": "Coomassie staining with white-light gel imaging",
        "regulatory": ["ICH Q6B", "ICH Q2(R2)"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "mw_ladder_resolution": "All bands clearly resolved with expected MW migration",
            "reduced_mab_hc": "Band at ~50 kDa (heavy chain)",
            "reduced_mab_lc": "Band at ~25 kDa (light chain)",
            "non_reduced_mab_intact": "Band at ~150 kDa (intact IgG)",
            "purity_by_densitometry": ">= 95% in main bands (product-specific)"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "Gel loading is the most precision-critical step in this protocol -- gel-loading tips and slow dispensing are essential. For ADCs, non-reducing SDS-PAGE may show additional drug-loaded species. Gel images should be archived with standardised exposure settings for comparability.",
        "autonomy_level": 2,
        "autonomy_level_reason": "Medium difficulty without AutoMATE 96 dispensing — robot executes instrument-based reads; analyst reviews flagged results.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — SDS-PAGE uses pre-cast gels loaded via gel-loading tips into gel wells, not 96-well plates. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "A9", "B1", "F1", "G1", "H1", "H2", "H3"],
            "automate_96": ["C1", "C2", "C3", "C4", "C5", "D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Prepare reducing samples: mix sample + LDS sample buffer + reducing agent (DTT) from positions C1, C2, C3 in PCR tubes at position A9 -- target 2-5 ug protein per lane.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Prepare non-reducing samples: mix sample + LDS sample buffer (no DTT) in separate PCR tubes.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Heat reducing samples at 70C for 10 minutes in heat block at position H1 -- log start/end times; non-reducing samples remain at room temperature.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Cool reducing samples to room temperature -- 5 minutes minimum.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Remove pre-cast gel (4-12% Bis-Tris) from position B1; rinse wells 3x with running buffer from position C4 using multichannel.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load 10 uL MW ladder (position F1) into lane 1 and last lane using 10 uL gel-loading tips from position D1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load 10-15 uL each sample into designated lanes per lane map loaded at run start -- dispense at bottom of well slowly.", "parameters": {"volume_uL": 15.0}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Log lane assignments with sample IDs, reducing/non-reducing designation, and load volumes.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Assemble gel cassette into electrophoresis tank at position H2; fill with MES SDS running buffer from position C4.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Connect to power supply -- run at 200V constant for 35 minutes; robot monitors run completion.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Check dye front has reached bottom of gel before stopping run.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Remove gel from cassette; transfer to staining tray at position H3.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'incubate', "instrument": 'incubator', "description": "Stain: add SimplyBlue Coomassie stain from position C5; incubate 1 hour on orbital shaker.", "parameters": {"duration_seconds": 3600}, "duration_seconds": 3600},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Destain: rinse 3x with ultrapure water; leave in water until background is clear.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer gel to gel imaging system at position G1 -- capture white-light image.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 16, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export gel image to run file; log band pattern observations per lane.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_015",
        "name": "Metabolite offline analysis (glucose, lactate, glutamine, ammonia)",
        "field": "Biopharma / CDMO",
        "product_types": ["CHO cell culture", "HEK293 culture", "Bioreactor process monitoring"],
        "purpose": "Measure key metabolite concentrations in bioreactor samples offline to guide feed strategy, monitor cell health, and support process trending.",
        "robot_steps": [
            "Pick up bioreactor sample tubes from input rack at position A1 (A1:1 through A1:8) -- confirm samples at room temperature.",
            "Centrifuge samples at 300 x g for 5 minutes to pellet cells; transfer 1 mL clarified supernatant to clean tubes at position A9.",
            "Load BioProfile FLEX2 or YSI 2950 sample cups at position B1 with 800 uL clarified supernatant per cup using 1 mL tips from position D1.",
            "Run daily QC controls from position F1 (high and low concentration) before samples -- verify all analytes within +/-10% of assigned values; log QC results.",
            "If any QC analyte fails, run instrument maintenance and recalibrate before proceeding with samples -- log calibration.",
            "Load sample cups into instrument carousel at position G1 in sequence matching run file.",
            "Initiate instrument run -- instrument automatically measures glucose (g/L), lactate (g/L), glutamine (mM), glutamate (mM), ammonia (mM), and optionally pH, pO2, pCO2.",
            "Robot monitors for each sample complete signal; retrieves results from instrument output.",
            "Compare each metabolite to process day-specific expected ranges -- flag deviations.",
            "Flag critical alerts: glucose < 0.5 g/L (nutrient depletion), lactate > 4 g/L (metabolic stress), ammonia > 6 mM (growth inhibition).",
            "[ANALYST STEP -- robot pauses and alerts]: If any critical alert triggered, notify process scientist immediately for feed adjustment decision.",
            "Export metabolite report with all values, flags, and trend vs process day to run file.",
            "Archive data for batch trending and process characterisation.",
            "Run instrument cleaning cycle at end of run -- log cleaning completion."
        ],
        "robot_deck_layout": {
            "A1": "Sample input rack -- 8 x 15 mL bioreactor sample tubes",
            "A9": "Clarified supernatant tube rack -- 8 x 1.5 mL tubes",
            "B1": "Instrument sample cup rack (BioProfile FLEX2 or YSI compatible)",
            "D1": "Tip rack -- 1 mL tips",
            "F1": "QC control rack -- high and low concentration controls",
            "G1": "BioProfile FLEX2 / YSI 2950 instrument carousel interface"
        },
        "workbench_id": "WB2",
        "rail_handoff": None,
        "instruments_needed": ["BioProfile FLEX2 (Nova Biomedical) or YSI 2950", "Microcentrifuge"],
        "consumables": ["Instrument-specific sample cups", "1 mL tips", "1.5 mL tubes"],
        "reagents": ["Instrument calibration pack (supplier-specific)", "QC controls high and low (certified values)"],
        "throughput_samples_per_run": 8,
        "throughput_notes": "8 samples per run; ~2 min per sample on instrument",
        "robot_active_minutes": 15,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 800,
        "detection": "Electrochemical biosensors (glucose, lactate, glutamine, glutamate, ammonia)",
        "regulatory": ["ICH Q5E", "ICH Q6B (process monitoring)"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "qc_control_tolerance": "+/-10% of assigned value for all analytes",
            "glucose_critical_low": "< 0.5 g/L triggers immediate feed alert",
            "lactate_critical_high": "> 4.0 g/L triggers metabolic stress alert",
            "ammonia_critical_high": "> 6.0 mM triggers growth inhibition alert"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "Metabolite results should be plotted against process day to detect trends. Glucose depletion and lactate accumulation are the earliest indicators of culture distress. For fed-batch cultures, feed timing decisions are often driven by glucose consumption rate calculated from these measurements.",
        "autonomy_level": 1,
        "autonomy_level_reason": "Easy automation with no AutoMATE 96 steps — fixed instrument-driven execution; analyst sets up samples and interprets results manually.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — metabolite analyser uses dedicated instrument sample cups, not 96-well plates. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "A9", "B1", "F1", "G1"],
            "automate_96": ["D1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Pick up bioreactor sample tubes from input rack at position A1 (A1:1 through A1:8) -- confirm samples at room temperature.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'centrifuge', "instrument": 'centrifuge', "description": "Centrifuge samples at 300 x g for 5 minutes to pellet cells; transfer 1 mL clarified supernatant to clean tubes at position A9.", "parameters": {"rpm": 300, "duration_seconds": 300}, "duration_seconds": 300},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load BioProfile FLEX2 or YSI 2950 sample cups at position B1 with 800 uL clarified supernatant per cup using 1 mL tips from position D1.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Run daily QC controls from position F1 (high and low concentration) before samples -- verify all analytes within +/-10% of assigned values; log QC results.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "If any QC analyte fails, run instrument maintenance and recalibrate before proceeding with samples -- log calibration.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Load sample cups into instrument carousel at position G1 in sequence matching run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Initiate instrument run -- instrument automatically measures glucose (g/L), lactate (g/L), glutamine (mM), glutamate (mM), ammonia (mM), and optionally pH, pO2, pCO2.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Robot monitors for each sample complete signal; retrieves results from instrument output.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Compare each metabolite to process day-specific expected ranges -- flag deviations.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Flag critical alerts: glucose < 0.5 g/L (nutrient depletion), lactate > 4 g/L (metabolic stress), ammonia > 6 mM (growth inhibition).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: If any critical alert triggered, notify process scientist immediately for feed adjustment decision.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export metabolite report with all values, flags, and trend vs process day to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Archive data for batch trending and process characterisation.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Run instrument cleaning cycle at end of run -- log cleaning completion.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_016",
        "name": "Buffer preparation and verification",
        "field": "Biopharma / CDMO",
        "product_types": ["Process buffers", "Formulation buffers", "Chromatography buffers"],
        "purpose": "Prepare, pH-adjust, and verify process buffers to specification including pH, conductivity, and visual appearance for GMP manufacturing.",
        "robot_steps": [
            "Retrieve batch record and confirm buffer specification: target composition, volume, pH, conductivity, and appearance.",
            "Weigh each excipient on calibrated analytical balance at position H1 (0.0001 g resolution) from excipient containers at position A1 -- record each weight and lot number.",
            "Transfer excipients to mixing vessel at position B1; add 80% of target water volume from position C1 (WFI or purified water).",
            "Start stirrer at 300 rpm -- mix until fully dissolved; robot monitors dissolution by periodic visual check (clarity sensor at position H3 if available).",
            "After dissolution, immerse pH electrode from position H2 into solution; record initial pH.",
            "Adjust pH to target using 1M NaOH or 1M HCl from positions C2/C3 -- add in 0.5 mL increments near target; record volume added at each step.",
            "When pH is within +/-0.02 of target, switch to 0.1M NaOH/HCl from positions C4/C5 for fine adjustment.",
            "Make up to final volume with water from C1; mix 10 additional minutes.",
            "Measure final pH -- confirm within specification (+/-0.05 of target); record to 0.01 resolution.",
            "Measure conductivity using probe at position H4 -- confirm within specification (+/-10% of target); record in mS/cm.",
            "Record visual appearance: clear, colourless, no particulates visible.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm all weights, pH adjustments, and final measurements match batch record before proceeding to filtration.",
            "Pre-wet 0.22 um sterilising filter at position D1 with 100 mL of same buffer.",
            "Filter entire batch through 0.22 um filter under nitrogen pressure (1-2 bar) into sterile receiving vessel at position B2.",
            "Measure pH and conductivity of filtered buffer -- confirm unchanged from pre-filtration values (pH shift <= 0.05, conductivity shift <= 5%).",
            "Label container with buffer name, lot, pH, conductivity, date, expiry, and preparer ID.",
            "Export buffer preparation report with all weights, adjustments, and measurements to run file."
        ],
        "robot_deck_layout": {
            "A1": "Excipient containers -- arranged in addition order per batch record",
            "B1": "Mixing vessel (glass or stainless steel) with magnetic stir bar",
            "B2": "Sterile receiving vessel for filtered buffer",
            "C1": "Water supply -- WFI or purified water",
            "C2": "1M NaOH dispensing bottle",
            "C3": "1M HCl dispensing bottle",
            "C4": "0.1M NaOH dispensing bottle",
            "C5": "0.1M HCl dispensing bottle",
            "D1": "0.22 um sterilising filter assembly with nitrogen supply",
            "H1": "Calibrated analytical balance (0.0001 g)",
            "H2": "pH meter with combination electrode",
            "H3": "Clarity sensor or visual inspection station",
            "H4": "Conductivity meter with probe"
        },
        "workbench_id": "WB1",
        "rail_handoff": None,
        "instruments_needed": ["Calibrated analytical balance", "pH meter", "Conductivity meter", "Magnetic stirrer", "0.22 um filter assembly"],
        "consumables": ["0.22 um Millipak or Durapore sterilising filters", "Sterile receiving vessels", "pH electrode", "Conductivity cell"],
        "reagents": ["Buffer excipients per specification", "1M and 0.1M NaOH", "1M and 0.1M HCl", "WFI or purified water"],
        "throughput_samples_per_run": 1,
        "throughput_notes": "1 buffer batch per run; 60-90 min per batch",
        "robot_active_minutes": 40,
        "total_assay_duration_hours": 1.5,
        "sample_volume_uL": 0,
        "detection": "pH meter, conductivity meter, visual inspection",
        "regulatory": ["ICH Q6B", "USP <1231>", "21 CFR 211.94"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "ph_tolerance": "Target +/-0.05 pH units",
            "conductivity_tolerance": "Target +/-10%",
            "post_filtration_ph_shift": "<= 0.05 pH units",
            "post_filtration_conductivity_shift": "<= 5%",
            "filter_integrity": "Bubble point or pressure hold per manufacturer specification",
            "appearance": "Clear, colourless, no particulates"
        },
        "environment_requirement": "Standard lab bench (BSL-1)",
        "platform_compatibility": "Full -- no environmental controls required",
        "notes": "All excipient weights must be recorded on batch record in real time. pH adjustment near target must use dilute acid/base to avoid overshoot. Post-filtration verification confirms filter did not alter buffer composition. Buffer expiry typically 30 days at 2-8C.",
        "autonomy_level": 2,
        "autonomy_level_reason": "Medium difficulty without AutoMATE 96 dispensing — robot executes instrument-based reads; analyst reviews flagged results.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — buffer preparation occurs in a bulk mixing vessel with in-line pH/conductivity probes. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "B2", "D1", "H1", "H2", "H3", "H4"],
            "automate_96": ["C1", "C2", "C3", "C4", "C5"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Retrieve batch record and confirm buffer specification: target composition, volume, pH, conductivity, and appearance.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Weigh each excipient on calibrated analytical balance at position H1 (0.0001 g resolution) from excipient containers at position A1 -- record each weight and lot number.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Transfer excipients to mixing vessel at position B1; add 80% of target water volume from position C1 (WFI or purified water).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'read', "instrument": 'plate_reader', "description": "Start stirrer at 300 rpm -- mix until fully dissolved; robot monitors dissolution by periodic visual check (clarity sensor at position H3 if available).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'read', "instrument": 'plate_reader', "description": "After dissolution, immerse pH electrode from position H2 into solution; record initial pH.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Adjust pH to target using 1M NaOH or 1M HCl from positions C2/C3 -- add in 0.5 mL increments near target; record volume added at each step.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "When pH is within +/-0.02 of target, switch to 0.1M NaOH/HCl from positions C4/C5 for fine adjustment.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Make up to final volume with water from C1; mix 10 additional minutes.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Measure final pH -- confirm within specification (+/-0.05 of target); record to 0.01 resolution.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Measure conductivity using probe at position H4 -- confirm within specification (+/-10% of target); record in mS/cm.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Record visual appearance: clear, colourless, no particulates visible.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Confirm all weights, pH adjustments, and final measurements match batch record before proceeding to filtration.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Pre-wet 0.22 um sterilising filter at position D1 with 100 mL of same buffer.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Filter entire batch through 0.22 um filter under nitrogen pressure (1-2 bar) into sterile receiving vessel at position B2.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Measure pH and conductivity of filtered buffer -- confirm unchanged from pre-filtration values (pH shift <= 0.05, conductivity shift <= 5%).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 16, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Label container with buffer name, lot, pH, conductivity, date, expiry, and preparer ID.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 17, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export buffer preparation report with all weights, adjustments, and measurements to run file.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_017",
        "name": "In-process pH and dissolved oxygen probe verification",
        "field": "Biopharma / CDMO",
        "product_types": ["Bioreactor process monitoring", "CHO cell culture", "Microbial fermentation"],
        "purpose": "Collect offline reference samples from bioreactor to verify accuracy of in-line pH and dissolved oxygen (DO) probes during GMP production runs.",
        "robot_steps": [
            "Confirm offline pH meter at position H1 is calibrated with pH 7.00 and pH 7.40 certified buffers from positions F1 and F2 -- log slope (must be 95-105%).",
            "Confirm blood gas analyser at position G1 is ready with fresh cartridge loaded -- log cartridge lot and expiry.",
            "Record current bioreactor in-line pH and DO probe readings from DCS/SCADA before sampling -- log both values with timestamp.",
            "Open bioreactor sample port at position H3 following aseptic technique -- discard first 5 mL to clear dead volume.",
            "Collect 5 mL sample into pre-labelled syringe from position D1 -- draw slowly to avoid degassing; cap immediately.",
            "For pO2/pCO2 measurement: immediately load capped syringe into blood gas analyser at position G1 -- analyse within 2 minutes of collection.",
            "Record offline pO2 (mmHg), pCO2 (mmHg), and blood gas pH from analyser output.",
            "For offline pH: transfer 2 mL aliquot from syringe to measurement cup at position B1; immerse pH electrode from H1; wait 30 seconds for stabilisation; record pH to 0.01.",
            "Calculate pH delta: offline pH minus in-line probe pH -- flag if |delta| > 0.05 pH units.",
            "Calculate DO delta: convert offline pO2 to %DO using calibration; compare to in-line DO -- flag if |delta| > 5%.",
            "If pH delta > 0.10 pH units: ALERT -- in-line probe requires recalibration or replacement; notify process engineer immediately.",
            "Log all offline values, in-line values, and calculated deltas in batch record with timestamp.",
            "Export probe verification report to run file.",
            "Clean sample port with 70% ethanol from position C1 after sampling."
        ],
        "robot_deck_layout": {
            "A1": "Not used -- samples collected directly from bioreactor",
            "B1": "Measurement cup rack (6-position, 5 mL cups)",
            "C1": "70% ethanol for port cleaning",
            "D1": "Pre-labelled syringe rack -- 10 mL syringes with caps",
            "F1": "pH 7.00 certified calibration buffer",
            "F2": "pH 7.40 certified calibration buffer",
            "G1": "Blood gas analyser (Radiometer ABL90 or equivalent)",
            "H1": "Calibrated offline pH meter",
            "H3": "Bioreactor sample port (aseptic connector)"
        },
        "workbench_id": "WB2",
        "rail_handoff": None,
        "instruments_needed": ["Calibrated offline pH meter", "Blood gas analyser (Radiometer ABL90 or equivalent)", "Bioreactor with accessible sample port"],
        "consumables": ["10 mL syringes with caps", "5 mL measurement cups", "70% ethanol wipes"],
        "reagents": ["pH 7.00 certified buffer", "pH 7.40 certified buffer", "Blood gas analyser cartridges"],
        "throughput_samples_per_run": 6,
        "throughput_notes": "6 bioreactor samples per run; ~5 min per sample",
        "robot_active_minutes": 15,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 5000,
        "detection": "Potentiometric pH; electrochemical pO2/pCO2",
        "regulatory": ["ICH Q6B (process monitoring)", "21 CFR 211.68"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "ph_probe_correlation": "Offline vs in-line pH within +/-0.05 pH units",
            "do_probe_correlation": "Offline vs in-line DO within +/-5%",
            "ph_recalibration_trigger": "|pH delta| > 0.10 pH units triggers immediate recalibration",
            "measurement_timing": "All measurements completed within 5 minutes of sample collection",
            "ph_calibration_slope": "95-105%"
        },
        "environment_requirement": "Standard lab bench (BSL-1); bioreactor area access required",
        "platform_compatibility": "Full -- requires proximity to bioreactor sample port",
        "notes": "Probe verification samples must be taken at least twice per day during active GMP production runs. Time from sampling to measurement is critical for pO2 accuracy -- delays > 5 minutes invalidate DO results. Blood gas analyser provides the most accurate offline pO2 reference.",
        "autonomy_level": 2,
        "autonomy_level_reason": "Medium difficulty without AutoMATE 96 dispensing — robot executes instrument-based reads; analyst reviews flagged results.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — bioreactor samples collected via syringe and measured in individual 5 mL cups. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "B1", "D1", "F1", "F2", "G1", "H1", "H3"],
            "automate_96": ["C1"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Confirm offline pH meter at position H1 is calibrated with pH 7.00 and pH 7.40 certified buffers from positions F1 and F2 -- log slope (must be 95-105%).", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'read', "instrument": 'plate_reader', "description": "Confirm blood gas analyser at position G1 is ready with fresh cartridge loaded -- log cartridge lot and expiry.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Record current bioreactor in-line pH and DO probe readings from DCS/SCADA before sampling -- log both values with timestamp.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Open bioreactor sample port at position H3 following aseptic technique -- discard first 5 mL to clear dead volume.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Collect 5 mL sample into pre-labelled syringe from position D1 -- draw slowly to avoid degassing; cap immediately.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'read', "instrument": 'plate_reader', "description": "For pO2/pCO2 measurement: immediately load capped syringe into blood gas analyser at position G1 -- analyse within 2 minutes of collection.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'read', "instrument": 'plate_reader', "description": "Record offline pO2 (mmHg), pCO2 (mmHg), and blood gas pH from analyser output.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'read', "instrument": 'plate_reader', "description": "For offline pH: transfer 2 mL aliquot from syringe to measurement cup at position B1; immerse pH electrode from H1; wait 30 seconds for stabilisation; record pH to 0.01.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate pH delta: offline pH minus in-line probe pH -- flag if |delta| > 0.05 pH units.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Calculate DO delta: convert offline pO2 to %DO using calibration; compare to in-line DO -- flag if |delta| > 5%.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "If pH delta > 0.10 pH units: ALERT -- in-line probe requires recalibration or replacement; notify process engineer immediately.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Log all offline values, in-line values, and calculated deltas in batch record with timestamp.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export probe verification report to run file.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Clean sample port with 70% ethanol from position C1 after sampling.", "parameters": {}, "duration_seconds": 30}
        ]
    },
    {
        "assay_id": "BIO_018",
        "name": "Cell culture media preparation and QC",
        "field": "Biopharma / CDMO",
        "product_types": ["CHO cell culture", "HEK293 culture", "Hybridoma culture", "Viral vector production"],
        "purpose": "Prepare cell culture media from powder or liquid concentrates, supplement, sterile filter, and perform quality control testing before use in GMP bioreactor operations.",
        "robot_steps": [
            "Retrieve media batch record and confirm formulation: base media, supplements, target volume, pH, osmolality specifications.",
            "Confirm biological safety cabinet at position H1 is running and certified for aseptic work -- log BSC serial number.",
            "Retrieve powdered or liquid media base from cold storage at position A1 -- verify lot number and expiry date; log both.",
            "For powdered media: add 80% target volume WFI from position C1 to sterile mixing vessel at position B1; start stirrer.",
            "Add powdered media slowly while stirring at 300 rpm -- stir for 30 minutes until fully dissolved; robot monitors dissolution.",
            "Add supplements in specified order from position A2: L-glutamine (200 mM stock), sodium bicarbonate (7.5% stock), additional supplements per specification -- log each lot number and volume.",
            "If serum required: add FBS from position A3 at specified percentage -- calculate volume; log lot number and volume.",
            "Adjust pH to 7.0-7.4 using NaOH from position C2 -- add in 0.5 mL increments; measure with pH electrode at position H2 between additions.",
            "Make up to final volume with WFI from position C1; mix additional 10 minutes.",
            "Measure pH at position H2 -- must be 7.0-7.4; record to 0.01.",
            "Measure osmolality at position H3 in triplicate -- must be 280-320 mOsm/kg; record mean and CV.",
            "Observe appearance: must be clear, straw-coloured (with phenol red); any turbidity or unusual colour is grounds for rejection.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm pH, osmolality, and appearance meet specification before proceeding to filtration.",
            "Pre-wet 0.22 um sterilising filter at position D1 with 100 mL of same media.",
            "Filter entire batch through 0.22 um filter into sterile receiving vessel at position B2 under nitrogen pressure.",
            "Aseptically remove 10 mL sample from filtered media -- transfer to TSB broth tube at position F1 and thioglycolate broth tube at position F2 for sterility testing.",
            "Incubate sterility tubes: TSB at 20-25C and thioglycolate at 30-35C for 14 days -- robot logs incubation start; analyst inspects daily.",
            "Measure pH and osmolality of filtered media -- confirm unchanged from pre-filtration values.",
            "Label container with media name, lot, date, expiry (30 days at 2-8C), pH, osmolality, preparer.",
            "Transfer to 2-8C storage; log storage location.",
            "Export media preparation report with all measurements, component lot numbers, and sterility test initiation to run file."
        ],
        "robot_deck_layout": {
            "A1": "Media base container (powder or liquid concentrate, from cold storage)",
            "A2": "Supplement rack -- L-glutamine, sodium bicarbonate, additional additives",
            "A3": "FBS container (if required, from -20C thawed to RT)",
            "B1": "Sterile mixing vessel with magnetic stir bar",
            "B2": "Sterile receiving vessel for filtered media",
            "C1": "WFI or cell culture-grade water supply",
            "C2": "NaOH for pH adjustment (1M and 0.1M)",
            "D1": "0.22 um sterilising filter assembly",
            "F1": "TSB sterility broth tube",
            "F2": "Thioglycolate sterility broth tube",
            "H1": "Biological safety cabinet (certified, Grade A)",
            "H2": "Calibrated pH meter",
            "H3": "Calibrated osmometer"
        },
        "workbench_id": "WB3",
        "rail_handoff": None,
        "instruments_needed": ["Biological safety cabinet class II", "pH meter", "Osmometer", "Magnetic stirrer", "0.22 um sterilising filter", "Analytical balance"],
        "consumables": ["0.22 um Millipak sterilising filter", "Sterile media storage bags or bottles", "TSB and thioglycolate broth tubes", "Labels"],
        "reagents": ["Cell culture media base (powder or liquid)", "L-glutamine 200 mM", "Sodium bicarbonate 7.5%", "WFI", "NaOH for pH adjustment", "FBS (if required)"],
        "throughput_samples_per_run": 1,
        "throughput_notes": "1 media batch per run; 90-120 min preparation + 14-day sterility incubation",
        "robot_active_minutes": 60,
        "total_assay_duration_hours": 2,
        "sample_volume_uL": 0,
        "detection": "pH meter, osmometer, visual inspection, 14-day sterility culture",
        "regulatory": ["ICH Q6B", "USP <1085>", "21 CFR 211"],
        "automation_difficulty": "complex",
        "acceptance_criteria": {
            "ph_range": "7.0-7.4",
            "osmolality_range": "280-320 mOsm/kg",
            "osmolality_cv": "<= 2% across triplicate readings",
            "appearance": "Clear, straw-coloured, no turbidity or particulates",
            "sterility_14day": "No turbidity in TSB or thioglycolate broth at 14 days",
            "post_filtration_ph_shift": "<= 0.05 pH units",
            "post_filtration_osmolality_shift": "<= 5 mOsm/kg"
        },
        "environment_requirement": "ISO Class 5 (Grade A) within BSC for aseptic operations; BSL-1 for preparation steps",
        "platform_compatibility": "Conditional -- BSC-adjacent operation required for sterile filtration and sterility sampling steps",
        "notes": "Media lot numbers must be recorded for full traceability. Sterility result available at 14 days -- for early bioreactor seeding, use media with satisfactory appearance, pH, and osmolality and release retrospectively. Any visible turbidity at any point during sterility incubation is a rejection criterion.",
        "autonomy_level": 4,
        "autonomy_level_reason": "Complex automation difficulty — robot makes go/no-go decisions on multi-stage workflows; analyst sets goals only.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "No microplate dispensing — media preparation occurs in a bulk sterile mixing vessel inside a biological safety cabinet. AutoMATE 96 not used.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": ["A1", "A2", "A3", "B1", "B2", "D1", "F1", "F2", "H1", "H2", "H3"],
            "automate_96": ["C1", "C2"],
            "analyst": []
        },
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Retrieve media batch record and confirm formulation: base media, supplements, target volume, pH, osmolality specifications.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 2, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Confirm biological safety cabinet at position H1 is running and certified for aseptic work -- log BSC serial number.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 3, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Retrieve powdered or liquid media base from cold storage at position A1 -- verify lot number and expiry date; log both.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 4, "step_type": 'mix', "instrument": 'liquid_handler', "description": "For powdered media: add 80% target volume WFI from position C1 to sterile mixing vessel at position B1; start stirrer.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 5, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Add powdered media slowly while stirring at 300 rpm -- stir for 30 minutes until fully dissolved; robot monitors dissolution.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": 'read', "instrument": 'plate_reader', "description": "Add supplements in specified order from position A2: L-glutamine (200 mM stock), sodium bicarbonate (7.5% stock), additional supplements per specification -- log each lot number and volume.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 7, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "If serum required: add FBS from position A3 at specified percentage -- calculate volume; log lot number and volume.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 8, "step_type": 'read', "instrument": 'plate_reader', "description": "Adjust pH to 7.0-7.4 using NaOH from position C2 -- add in 0.5 mL increments; measure with pH electrode at position H2 between additions.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 9, "step_type": 'mix', "instrument": 'liquid_handler', "description": "Make up to final volume with WFI from position C1; mix additional 10 minutes.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 10, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Measure pH at position H2 -- must be 7.0-7.4; record to 0.01.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 11, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Measure osmolality at position H3 in triplicate -- must be 280-320 mOsm/kg; record mean and CV.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Observe appearance: must be clear, straw-coloured (with phenol red); any turbidity or unusual colour is grounds for rejection.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 13, "step_type": 'analyst', "instrument": 'analyst', "description": "-- robot pauses and alerts: Confirm pH, osmolality, and appearance meet specification before proceeding to filtration.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 14, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Pre-wet 0.22 um sterilising filter at position D1 with 100 mL of same media.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 15, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Filter entire batch through 0.22 um filter into sterile receiving vessel at position B2 under nitrogen pressure.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 16, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Aseptically remove 10 mL sample from filtered media -- transfer to TSB broth tube at position F1 and thioglycolate broth tube at position F2 for sterility testing.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 17, "step_type": 'incubate', "instrument": 'incubator', "description": "Incubate sterility tubes: TSB at 20-25C and thioglycolate at 30-35C for 14 days -- robot logs incubation start; analyst inspects daily.", "parameters": {"temperature_C": 25.0}, "duration_seconds": 30},
            {"step_number": 18, "step_type": 'vacuum_filtration', "instrument": 'vacuum_manifold', "description": "Measure pH and osmolality of filtered media -- confirm unchanged from pre-filtration values.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 19, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Label container with media name, lot, date, expiry (30 days at 2-8C), pH, osmolality, preparer.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 20, "step_type": 'transfer', "instrument": 'liquid_handler', "description": "Transfer to 2-8C storage; log storage location.", "parameters": {}, "duration_seconds": 30},
            {"step_number": 21, "step_type": 'dispense', "instrument": 'liquid_handler', "description": "Export media preparation report with all measurements, component lot numbers, and sterility test initiation to run file.", "parameters": {}, "duration_seconds": 30}
        ]
    },
]


# ═══════════════════════════════════════════════════════════════════════════
#  QUERY API — v2.0
# ═══════════════════════════════════════════════════════════════════════════

def get_all_assays():
    """Return the full assay list."""
    return BIOPHARMA_ASSAYS


def get_assay_by_id(assay_id):
    """Look up a single assay by its ID string (e.g. 'BIO_005')."""
    for a in BIOPHARMA_ASSAYS:
        if a["assay_id"] == assay_id:
            return a
    return None


def get_assays_by_product(product_type):
    """Return all assays that list a given product type."""
    return [a for a in BIOPHARMA_ASSAYS if product_type in a.get("product_types", [])]


def get_assays_by_difficulty(difficulty):
    """Return all assays matching an automation difficulty level (easy, medium, complex)."""
    return [a for a in BIOPHARMA_ASSAYS if a.get("automation_difficulty") == difficulty]


def get_assays_by_workbench(workbench_id):
    """Return all assays assigned to a specific workbench (e.g. 'WB1', 'WB2', 'WB3')."""
    return [a for a in BIOPHARMA_ASSAYS if a.get("workbench_id") == workbench_id]


def get_assays_by_environment(keyword):
    """Return all assays whose environment_requirement contains a keyword (e.g. 'BSL-2', 'ISO Class 5')."""
    kw = keyword.lower()
    return [a for a in BIOPHARMA_ASSAYS if kw in a.get("environment_requirement", "").lower()]


def get_assays_by_detection(keyword):
    """Return all assays whose detection method contains a keyword (e.g. 'UV', 'fluorescence', 'PCR')."""
    kw = keyword.lower()
    return [a for a in BIOPHARMA_ASSAYS if kw in a.get("detection", "").lower()]


def get_assays_by_regulatory(standard):
    """Return all assays that reference a given regulatory standard (e.g. 'ICH Q6B', 'USP <85>')."""
    std = standard.lower()
    return [a for a in BIOPHARMA_ASSAYS if any(std in r.lower() for r in a.get("regulatory", []))]


def get_assays_with_analyst_steps():
    """Return all assays that contain at least one [ANALYST STEP] requiring human intervention."""
    results = []
    for a in BIOPHARMA_ASSAYS:
        analyst_steps = [s for s in a.get("robot_steps", []) if "[ANALYST STEP" in s]
        if analyst_steps:
            results.append({"assay_id": a["assay_id"], "name": a["name"], "analyst_step_count": len(analyst_steps), "analyst_steps": analyst_steps})
    return results


def get_robot_instructions(assay_id):
    """Generate formatted plain-text robot instructions for a given assay."""
    assay = get_assay_by_id(assay_id)
    if not assay:
        return None
    lines = [
        f"ASSAY: {assay['name']}",
        f"ID: {assay['assay_id']}",
        f"FIELD: {assay['field']}",
        f"WORKBENCH: {assay.get('workbench_id', 'N/A')}",
        f"ROBOT ACTIVE TIME: {assay.get('robot_active_minutes', 'N/A')} minutes",
        f"TOTAL DURATION: {assay.get('total_assay_duration_hours', 'N/A')} hours",
        f"THROUGHPUT: {assay.get('throughput_samples_per_run', 'N/A')} samples/run",
        f"DIFFICULTY: {assay['automation_difficulty'].upper()}",
        f"ENVIRONMENT: {assay.get('environment_requirement', 'N/A')}",
        "",
        "DECK LAYOUT:",
    ]
    for pos, desc in assay.get("robot_deck_layout", {}).items():
        lines.append(f"  [{pos}] {desc}")
    lines.append("")
    lines.append("INSTRUMENTS REQUIRED:")
    for inst in assay.get("instruments_needed", []):
        lines.append(f"  - {inst}")
    lines.append("")
    lines.append("CONSUMABLES:")
    for c in assay.get("consumables", []):
        lines.append(f"  - {c}")
    lines.append("")
    lines.append("REAGENTS:")
    for r in assay.get("reagents", []):
        lines.append(f"  - {r}")
    lines.append("")
    lines.append("ROBOT STEP INSTRUCTIONS:")
    for i, step in enumerate(assay["robot_steps"], 1):
        prefix = "  >>>" if "[ANALYST STEP" in step else f"  {i:2d}."
        lines.append(f"{prefix} {step}")
    lines.append("")
    lines.append("ACCEPTANCE CRITERIA:")
    for k, v in assay.get("acceptance_criteria", {}).items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append(f"REGULATORY: {', '.join(assay.get('regulatory', []))}")
    if assay.get("notes"):
        lines.append(f"\nNOTES: {assay['notes']}")
    return "\n".join(lines)


def search_assays(query):
    """Full-text search across assay name, purpose, notes, reagents, instruments, and detection."""
    q = query.lower()
    results = []
    for a in BIOPHARMA_ASSAYS:
        searchable = " ".join([
            a.get("name", ""),
            a.get("purpose", ""),
            a.get("notes", ""),
            a.get("detection", ""),
            a.get("environment_requirement", ""),
            " ".join(a.get("reagents", [])),
            " ".join(a.get("instruments_needed", [])),
            " ".join(a.get("product_types", [])),
        ]).lower()
        if q in searchable:
            results.append(a)
    return results


def get_field_summary():
    """Return summary statistics for the entire field library."""
    total = len(BIOPHARMA_ASSAYS)
    easy = len(get_assays_by_difficulty("easy"))
    medium = len(get_assays_by_difficulty("medium"))
    cpx = len(get_assays_by_difficulty("complex"))
    workbenches = sorted(set(a.get("workbench_id", "N/A") for a in BIOPHARMA_ASSAYS))
    analyst_steps_total = sum(
        len([s for s in a.get("robot_steps", []) if "[ANALYST STEP" in s])
        for a in BIOPHARMA_ASSAYS
    )
    return {
        "field": "Biopharma / CDMO",
        "version": "2.0",
        "total_assays": total,
        "easy": easy,
        "medium": medium,
        "complex": cpx,
        "workbenches": workbenches,
        "total_analyst_steps": analyst_steps_total,
    }


def export_field_summary():
    """Print formatted summary table to console."""
    summary = get_field_summary()
    print(f"\n{'='*80}")
    print(f"  BIOPHARMA / CDMO ASSAY LIBRARY -- BioInterface v1.0")
    print(f"  Total assays: {summary['total_assays']}")
    print(f"{'='*80}\n")
    print(f"  Easy automation:    {summary['easy']} assays")
    print(f"  Medium automation:  {summary['medium']} assays")
    print(f"  Complex automation: {summary['complex']} assays")
    print(f"  Workbenches used:   {', '.join(summary['workbenches'])}")
    print(f"  Analyst steps:      {summary['total_analyst_steps']} across all assays")
    print(f"\n{'-'*80}")
    for a in BIOPHARMA_ASSAYS:
        diff_label = {"easy": "EASY  ", "medium": "MEDIUM", "complex": "COMPLEX"}[a["automation_difficulty"]]
        analyst_count = len([s for s in a.get("robot_steps", []) if "[ANALYST STEP" in s])
        analyst_tag = f" [{analyst_count} analyst step(s)]" if analyst_count > 0 else ""
        print(f"  {a['assay_id']}  [{diff_label}]  {a['name']}{analyst_tag}")
        print(f"           Robot: {a.get('robot_active_minutes', '?')} min | Total: {a.get('total_assay_duration_hours', '?')} hr | Samples: {a.get('throughput_samples_per_run', '?')}/run | WB: {a.get('workbench_id', '?')}")
        print(f"           Regulatory: {', '.join(a.get('regulatory', []))}")
        print()


if __name__ == "__main__":
    export_field_summary()
    print("\n" + "="*80)
    print("  ANALYST STEP SUMMARY")
    print("="*80)
    for entry in get_assays_with_analyst_steps():
        print(f"\n  {entry['assay_id']} -- {entry['name']} ({entry['analyst_step_count']} analyst step(s)):")
        for step in entry['analyst_steps']:
            print(f"    >> {step[:120]}...")
    print("\n" + "-"*80)
    print("\nSample robot instructions for BIO_001:")
    print("-" * 60)
    print(get_robot_instructions("BIO_001"))
