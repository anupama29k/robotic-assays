"""
field_01_biopharma.py -- Biopharma / CDMO Assay Library
Rail System Assay Library v1.0
Author: Anu Kozhiyalam
Field: Biopharma / CDMO (Contract Development and Manufacturing)
Assays: 18
Purpose: Robot-executable assay protocols for biopharmaceutical manufacturing
         and contract development organizations. Each assay contains plain-language
         robot step instructions that Rail System can execute directly.
"""

BIOPHARMA_ASSAYS = [

    # ── TITER AND QUANTITATION ─────────────────────────────────────────────

    {
        "assay_id": "BIO_001",
        "name": "Protein A titer by HPLC",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Fc-fusion proteins"],
        "purpose": "Quantify mAb concentration in harvest, purification pools, and drug substance",
        "robot_steps": [
            "Verify deck layout: confirm sample rack at position D1, microcentrifuge tube rack at D2, HPLC vial rack at D3, 200 uL tip box at D4, 1000 uL tip box at D5, reagent reservoir with PBS pH 7.2 at D6, waste container at D9",
            "Confirm room temperature is 20-25 degrees C before starting — log ambient temp to worksheet",
            "Pick up 200 uL tips from tip box at deck position D4 — if tip pickup fails, retry once then pause and alert operator to check tip box alignment",
            "Pick up sample tube from input rack at deck position D1, position A1 — confirm liquid level detection before aspirating",
            "Vortex sample tube for 5 seconds at setting 3 — hold tube securely in vortex adapter",
            "Aspirate 50 uL of sample at 100 uL/sec dispensing speed from sample tube — verify liquid level detected, if no liquid detected pause and flag empty tube",
            "Dispense 50 uL of sample into a 1.5 mL microcentrifuge tube at deck position D2, position B1 at 80 uL/sec — touch off on tube wall to release residual",
            "Log trigger: record sample ID, source position A1, volume aspirated 50 uL, timestamp",
            "Discard used tip into waste at deck position D9 — pick up fresh 1000 uL tip from D5",
            "Aspirate 450 uL of HPLC mobile phase (PBS pH 7.2) at 200 uL/sec from reagent reservoir at deck position D6 — verify reagent level above minimum 5 mL",
            "Dispense 450 uL PBS into microcentrifuge tube at D2 position B1 at 150 uL/sec — this creates 1:10 dilution",
            "Cap tube and vortex for 3 seconds at setting 2",
            "Pick up fresh 200 uL tip from D4 — aspirate 200 uL of diluted sample at 80 uL/sec from microcentrifuge tube at D2",
            "Dispense 200 uL into HPLC glass vial at deck position D3, position C1 at 60 uL/sec — dispense slowly to avoid bubbles",
            "Cap vial with crimp cap using vial capper tool — verify cap is seated by downward pressure check",
            "Place capped vial into HPLC autosampler rack at numbered position matching sample ID — robot arm reaches to instrument interface at deck position D7",
            "Log trigger: record sample ID, dilution factor 1:10, vial rack position, HPLC autosampler position, timestamp, analyst initials",
            "Discard tip into waste at D9 — return to sample rack D1 and advance to next sample position",
            "Repeat for all samples in batch — up to 24 vials per rack — log total samples processed at end of batch"
        ],
        "robot_deck_layout": {
            "D1": "Sample input rack — 24-position tube rack for 1.5-2.0 mL sample tubes",
            "D2": "Microcentrifuge tube rack — 24-position rack with pre-loaded empty 1.5 mL tubes for dilutions",
            "D3": "HPLC vial rack — 24-position rack for 1.5 mL HPLC glass vials with crimp caps",
            "D4": "Tip box 200 uL — full box 96 tips",
            "D5": "Tip box 1000 uL — full box 96 tips",
            "D6": "Reagent reservoir — single trough with PBS pH 7.2 mobile phase, minimum 15 mL",
            "D7": "Instrument interface — HPLC autosampler loading position, robot arm reach zone",
            "D8": "Vial capper tool station",
            "D9": "Waste container — tip discard and liquid waste"
        },
        "instruments_needed": ["HPLC with Protein A column (POROS A 20 or MabSelect)", "Vortex mixer", "Vial capper", "Pipette 20-200 uL", "Pipette 200-1000 uL"],
        "consumables": ["1.5 mL microcentrifuge tubes", "HPLC glass vials 1.5 mL", "Crimp caps", "Tips 200 uL", "Tips 1000 uL"],
        "reagents": ["PBS pH 7.2 mobile phase", "0.1 M glycine-HCl pH 2.5 elution buffer"],
        "throughput": "24 samples per hour",
        "duration_minutes": 10,
        "sample_volume_uL": 50,
        "detection": "UV 280 nm",
        "regulatory": ["ICH Q6B", "USP 1046"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "titer_range": "0.1 - 20.0 mg/mL",
            "pass_condition": "Titer value falls within the validated linear range of the standard curve (R-squared >= 0.999) and system suitability passes (plates N > 2000, tailing 0.8-1.5)",
            "fail_action": "FLAG — mark sample for manual re-run at adjusted dilution; if system suitability fails, ABORT batch and alert analyst to recondition column"
        },
        "troubleshooting": [
            {"failure": "No peak or flat baseline on chromatogram", "diagnosis": "Sample may be too dilute, column may not be equilibrated, or UV lamp is failing", "action": "Check sample concentration by A280 on NanoDrop, re-equilibrate column with 10 column volumes mobile phase, verify UV lamp intensity"},
            {"failure": "Broad or tailing peaks with tailing factor > 1.5", "diagnosis": "Column degradation, incorrect pH of mobile phase, or sample matrix interference", "action": "Run blank injection to rule out carryover, check mobile phase pH, replace column if usage count exceeds 500 injections"},
            {"failure": "Tip pickup failure — robot cannot seat tip", "diagnosis": "Tip box misaligned on deck or tips are not fully seated in box", "action": "Pause run, re-seat tip box on deck position D4, verify alignment pins are engaged, resume"},
            {"failure": "Liquid level detection error — no liquid found in sample tube", "diagnosis": "Sample tube is empty, tube not properly seated, or capacitive sensor needs calibration", "action": "Pause and flag tube position to operator — skip sample and log as insufficient volume"},
            {"failure": "High %RSD between replicate injections (> 2%)", "diagnosis": "Air bubble in sample vial, inconsistent injection volume, or autosampler needle blockage", "action": "Re-prep sample vial ensuring no bubbles, flush autosampler needle, re-inject"}
        ],
        "notes": "Standard curve prepared from known mAb reference standard at 0.1 to 2.0 mg/mL. Run system suitability before batch — plates N > 2000, tailing factor 0.8-1.5."
    },

    {
        "assay_id": "BIO_002",
        "name": "BCA protein concentration assay",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "Vaccines", "ADCs"],
        "purpose": "Total protein quantification in samples, purification fractions, and formulated drug product",
        "robot_steps": [
            "Verify deck layout: confirm sample rack at D1, 96-well assay plate at D2, reagent reservoir with BCA working reagent at D3, standard rack at D4, 10-100 uL tip box at D5, 200 uL multichannel tip box at D6, plate seals at D7, waste at D9",
            "Confirm ambient temperature 20-25 degrees C — BCA reaction is temperature-sensitive",
            "Prepare BCA working reagent: mix 50 parts Reagent A with 1 part Reagent B in reagent reservoir at deck position D3 — minimum 25 mL total volume for one plate",
            "Pick up 10-100 uL tips from tip box at D5 — if tip pickup fails, retry once then alert operator",
            "Load BSA standards into column 1 of 96-well plate at D2: aspirate from standard rack at D4 — 0, 25, 125, 250, 500, 750, 1000, 1500, 2000 ug/mL at 50 uL/sec dispensing speed",
            "Log trigger: record standard curve concentrations loaded, plate ID, timestamp",
            "Pick up sample from input rack at D1 — verify liquid level, if empty flag and skip",
            "Dilute sample 1:10 in PBS — aspirate 10 uL sample at 30 uL/sec, dispense into 90 uL PBS pre-loaded in plate column 2 onwards at D2",
            "Mix by pipetting up and down 5 times at 50 uL/sec — avoid creating bubbles",
            "Transfer 25 uL of each standard and diluted sample in duplicate into assay plate wells at 30 uL/sec — columns 1-2 standards, columns 3 onward samples",
            "Log trigger: record sample IDs, well positions, dilution factors",
            "Discard single-channel tips to waste at D9 — pick up 200 uL multichannel tips from D6",
            "Add 200 uL of BCA working reagent from reservoir at D3 to each well using multichannel pipette at 100 uL/sec — verify reservoir level above 5 mL before each column",
            "Seal plate with adhesive film from D7 — press firmly across all wells",
            "Transfer plate to plate incubator — incubate at 37 degrees C for exactly 30 minutes",
            "After incubation remove seal carefully at room temperature — avoid disturbing wells or splashing",
            "Place plate in plate reader at instrument interface — read absorbance at 562 nm",
            "Log trigger: record plate ID, sample IDs, dilution factors, all OD values, standard curve R-squared, calculated concentrations, timestamp"
        ],
        "robot_deck_layout": {
            "D1": "Sample input rack — 24-position tube rack for sample tubes",
            "D2": "96-well flat-bottom clear assay plate — Corning or equivalent",
            "D3": "Reagent reservoir — single trough with freshly prepared BCA working reagent, minimum 25 mL",
            "D4": "Standard rack — 8-position tube strip with BSA standards 0-2000 ug/mL pre-prepared",
            "D5": "Tip box 10-100 uL — full box 96 tips for single channel",
            "D6": "Tip box 200 uL multichannel — full box 96 tips",
            "D7": "Plate seal station — adhesive film dispenser",
            "D8": "Plate incubator interface — 37C, robot arm transfers plate",
            "D9": "Waste container — tip discard and liquid waste"
        },
        "instruments_needed": ["Plate reader (562 nm)", "Multichannel pipette 8-channel 200 uL", "Plate incubator 37C", "Single channel pipette 10-100 uL"],
        "consumables": ["96-well flat-bottom clear plate", "Adhesive plate seal", "Tips 200 uL multichannel", "Tips 10-100 uL", "Reagent reservoir"],
        "reagents": ["BCA Reagent A (Thermo Pierce 23228)", "BCA Reagent B", "BSA standard 2 mg/mL", "PBS pH 7.4"],
        "throughput": "80 samples per plate, 2 plates per hour",
        "duration_minutes": 45,
        "sample_volume_uL": 10,
        "detection": "Absorbance 562 nm",
        "regulatory": ["ICH Q6B"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "standard_curve_R2": ">= 0.995",
            "duplicate_CV": "<= 10%",
            "concentration_range": "25 - 2000 ug/mL within linear range",
            "pass_condition": "Standard curve R-squared >= 0.995, sample OD falls within standard curve range, and duplicate CV <= 10%",
            "fail_action": "FLAG — if CV > 10% between duplicates, flag well pair for re-run; if OD exceeds standard curve, PAUSE and re-dilute sample at higher dilution; if R-squared < 0.995, ABORT plate and re-prepare standards"
        },
        "troubleshooting": [
            {"failure": "Standard curve R-squared < 0.995", "diagnosis": "Standards degraded, pipetting error during standard preparation, or plate reader malfunction", "action": "Re-prepare fresh BSA standards from stock, verify pipette calibration, run plate reader self-test"},
            {"failure": "High background OD in blank wells (> 0.1 AU)", "diagnosis": "Contaminated BCA reagent, plate not properly washed, or reagent too old", "action": "Prepare fresh BCA working reagent — working reagent is stable for 24 hours only, use new plate"},
            {"failure": "CV > 10% between duplicate wells", "diagnosis": "Inconsistent pipetting volume, bubbles in wells, or uneven incubation", "action": "Check pipette calibration, ensure no bubbles before sealing, verify incubator temperature uniformity"},
            {"failure": "All samples read above standard curve", "diagnosis": "Sample concentration too high for 1:10 dilution", "action": "Re-run samples at 1:50 or 1:100 dilution — adjust dilution factor in calculation"},
            {"failure": "Purple colour does not develop after incubation", "diagnosis": "BCA Reagent B missing or not mixed, incubator not at temperature, or wrong plate type", "action": "Verify working reagent was prepared with both A and B, check incubator displays 37C, confirm clear flat-bottom plate used"}
        ],
        "notes": "Linear range 25-2000 ug/mL. Run samples in duplicate minimum. If OD exceeds standard curve, dilute further and re-run. Robot should flag any well with CV > 10% between duplicates."
    },

    {
        "assay_id": "BIO_003",
        "name": "SEC-HPLC aggregation analysis",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Bispecific antibodies", "Fc-fusion proteins", "ADCs"],
        "purpose": "Quantify monomer purity and high/low molecular weight species (aggregates and fragments)",
        "robot_steps": [
            "Verify deck layout: confirm sample rack at D1 (cold block 2-8C), HPLC vial rack at D2, SEC mobile phase reservoir at D3, 200 uL tip box at D4, waste at D9",
            "Confirm cold block at D1 is 2-8 degrees C — log temperature before starting",
            "Remove sample from cold block at D1 and allow to equilibrate to room temperature 20-25C for 15 minutes — log start time",
            "Pick up 200 uL tip from tip box at D4 — if tip pickup fails, retry once then pause and alert operator",
            "Vortex sample gently for 3 seconds at setting 1 — do not foam, avoid introducing air bubbles",
            "Centrifuge sample tube at 10000 rpm for 2 minutes in microcentrifuge at deck position D8 to pellet any particulates",
            "After centrifuge, pick up fresh 200 uL tip from D4 — aspirate 90 uL of clarified supernatant at 50 uL/sec from sample tube, avoiding pellet at bottom",
            "Verify liquid level detected — if no liquid, flag sample tube as insufficient volume and skip",
            "Dispense 90 uL into HPLC vial at deck position D2, position A1 at 40 uL/sec — dispense slowly against vial wall",
            "If sample concentration exceeds 10 mg/mL (known from prior assay), dilute 1:2 — aspirate 45 uL sample plus 45 uL SEC mobile phase from D3",
            "Log trigger: record sample ID, concentration if known, dilution factor, vial position, timestamp",
            "Cap vial and place in autosampler rack — robot arm reaches to HPLC instrument interface at D7",
            "Inject 20 uL onto SEC column (TSKgel G3000SWxl or Acquity BEH SEC 200A) — injection at room temperature",
            "Run isocratic mobile phase PBS pH 6.8 with 200 mM NaCl at 0.5 mL/min for 30 minutes at 25 degrees C column temperature",
            "Record peak areas for: HMW species (aggregates), main monomer peak, LMW species (fragments) — UV detection at 280 nm",
            "Log trigger: sample ID, concentration, injection volume, HMW %, monomer %, LMW %, run date, column ID and usage count",
            "Discard tip to waste at D9 — advance to next sample",
            "After final sample, run column wash with mobile phase for 30 minutes to maintain column health"
        ],
        "robot_deck_layout": {
            "D1": "Sample input rack with cold block — 24-position rack maintained at 2-8C for sample stability",
            "D2": "HPLC vial rack — 24-position rack for 1.5 mL HPLC vials",
            "D3": "Reagent reservoir — SEC mobile phase (50 mM sodium phosphate pH 6.8 + 200 mM NaCl), minimum 20 mL",
            "D4": "Tip box 200 uL — full box 96 tips",
            "D5": "Empty — reserved",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — HPLC autosampler loading position",
            "D8": "Microcentrifuge — for clarification spin",
            "D9": "Waste container — tip discard and liquid waste"
        },
        "instruments_needed": ["HPLC or UPLC system", "SEC column TSKgel G3000SWxl or equivalent", "Microcentrifuge", "Pipette 20-200 uL"],
        "consumables": ["HPLC vials 1.5 mL", "Vial caps", "Tips 200 uL"],
        "reagents": ["SEC mobile phase: 50 mM sodium phosphate pH 6.8 with 200 mM NaCl"],
        "throughput": "12 samples per 6 hours (30 min run time each)",
        "duration_minutes": 15,
        "sample_volume_uL": 90,
        "detection": "UV 280 nm",
        "regulatory": ["ICH Q6B", "ICH Q2(R2)"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "monomer": ">= 95.0%",
            "HMW aggregates": "<= 5.0%",
            "LMW fragments": "<= 2.0%",
            "system_suitability_resolution": "> 1.5 between BSA monomer and dimer",
            "injection_RSD": "< 1.0% for replicate injections",
            "pass_condition": "Monomer purity >= 95.0%, HMW <= 5.0%, LMW <= 2.0%, and system suitability resolution > 1.5",
            "fail_action": "FLAG — if monomer < 95% or HMW > 5%, flag sample for investigation and notify QA; if system suitability fails, ABORT sequence and recondition column"
        },
        "troubleshooting": [
            {"failure": "Monomer peak is split or has shoulder", "diagnosis": "Column overloaded, sample concentration too high, or column degradation causing loss of resolution", "action": "Reduce injection volume to 10 uL or dilute sample 1:2, check column plate count — replace if below specification"},
            {"failure": "No peaks detected in chromatogram", "diagnosis": "Sample too dilute, injection failure, or UV detector lamp needs replacement", "action": "Verify sample concentration by A280, check autosampler injection log for errors, run UV lamp test"},
            {"failure": "Increasing HMW% across stability samples", "diagnosis": "Genuine aggregation trend in product — not an instrument error", "action": "Confirm by re-injection of retain sample, escalate to formulation scientist if trend is real"},
            {"failure": "Baseline drift during run", "diagnosis": "Mobile phase not properly degassed, column bleed from aging column, or temperature fluctuation", "action": "Degas mobile phase by sonication 15 min, check column temperature controller, replace mobile phase if older than 48 hours"},
            {"failure": "Ghost peaks appearing in blank injection", "diagnosis": "Carryover from previous high-concentration sample or contaminated mobile phase", "action": "Run 3 blank injections to clear, clean autosampler needle, prepare fresh mobile phase"}
        ],
        "notes": "System suitability: resolution between BSA monomer and dimer > 1.5. Injection repeatability %RSD < 1.0%. Run reference standard at start and end of sequence."
    },

    # ── CELL HEALTH AND VIABILITY ──────────────────────────────────────────

    {
        "assay_id": "BIO_004",
        "name": "Cell viability and density by Vi-CELL or Cedex",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Cell and Gene Therapy", "Vaccines", "Recombinant proteins"],
        "purpose": "Measure viable cell density (VCD) and viability percentage during bioreactor culture for process monitoring",
        "robot_steps": [
            "Verify deck layout: confirm 2 mL collection tube rack at D1, Vi-CELL sample cup rack at D2, offline analyser tube rack at D3, 1000 uL tip box at D4, ethanol spray bottle at D5, waste at D9",
            "Confirm bioreactor sample port is accessible at instrument interface position D7 — verify aseptic connection",
            "Pick up 1000 uL tip from tip box at D4 — if tip pickup fails, retry once then pause",
            "Collect 1.5 mL sample from bioreactor sample port at D7 into a 2 mL collection tube at D1 position A1 — aspirate at 200 uL/sec to avoid shearing cells",
            "Log trigger: record batch code, sample time, day of run, collection tube position",
            "Label tube with batch code, sample time, and day of run via barcode printer at D8",
            "Discard tip to waste at D9 — pick up fresh 1000 uL tip from D4",
            "Gently mix collection tube by inverting 3 times — do not vortex, cells are shear-sensitive",
            "Aspirate 500 uL of cell sample at 150 uL/sec from collection tube at D1 — use wide-bore tip if available",
            "Dispense 500 uL into Vi-CELL sample cup at D2 position 1 at 100 uL/sec — ensure sample reaches bottom of cup",
            "Verify liquid level in Vi-CELL cup — if not detected, aspirate additional 200 uL from collection tube",
            "Place cup into Vi-CELL or Cedex instrument carousel at instrument interface D7 — enter sample ID via robot software interface",
            "Instrument automatically stains with trypan blue and images 100+ cells — wait for completion signal (approximately 3 minutes)",
            "Record: viable cell density (cells/mL), total cell density (cells/mL), viability percentage, average cell diameter — all at room temperature 20-25C",
            "Pick up fresh 1000 uL tip from D4 — transfer remaining 1.0 mL sample from collection tube at D1 to offline analyser tube at D3 for metabolite analysis (BIO_015)",
            "Log trigger: record all Vi-CELL results, timestamp, operator ID, instrument serial number, calibration status",
            "Discard tip to waste at D9 — clean sample port with 70% ethanol from D5 — maintain aseptic technique",
            "Advance to next bioreactor if sampling multiple vessels"
        ],
        "robot_deck_layout": {
            "D1": "2 mL collection tube rack — 24-position rack for sample collection from bioreactor",
            "D2": "Vi-CELL sample cup rack — 10-position carousel cups",
            "D3": "Offline analyser tube rack — 24-position for metabolite analysis aliquots",
            "D4": "Tip box 1000 uL — full box 96 tips, wide-bore preferred",
            "D5": "Ethanol spray station — 70% ethanol for aseptic port cleaning",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — bioreactor sample port and Vi-CELL/Cedex carousel",
            "D8": "Barcode printer — label station for tube identification",
            "D9": "Waste container — tip discard and liquid waste"
        },
        "instruments_needed": ["Vi-CELL BLU (Beckman Coulter) or Cedex HiRes (Roche)", "Pipette 200-1000 uL"],
        "consumables": ["Vi-CELL sample cups", "Trypan blue solution (instrument internal)", "2 mL collection tubes", "Tips 1000 uL"],
        "reagents": ["Trypan blue 0.4% (internal to instrument)", "70% ethanol for port cleaning"],
        "throughput": "6-10 samples per hour",
        "duration_minutes": 8,
        "sample_volume_uL": 500,
        "detection": "Image analysis — brightfield microscopy",
        "regulatory": ["ICH Q5E", "ICH Q6B"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "viability_range": ">= 80% for active culture, >= 70% minimum for harvest",
            "VCD_range": "0.5 - 50.0 x10^6 cells/mL within instrument linear range",
            "cell_diameter": "12 - 22 um typical for CHO cells",
            "pass_condition": "Viability >= 80% during exponential growth and >= 70% at harvest; VCD within instrument validated range; cell images show clear viable/dead discrimination",
            "fail_action": "ALERT — if viability < 70%, immediately alert process scientist for culture assessment; if VCD is outside instrument range, PAUSE and dilute sample 1:2 in PBS before re-reading"
        },
        "troubleshooting": [
            {"failure": "Viability reads unexpectedly low (< 50%) for healthy culture", "diagnosis": "Sample sat too long before reading (> 30 min), trypan blue reagent expired, or shear damage during sampling", "action": "Re-sample and read within 10 minutes, check trypan blue expiry date, use wider-bore tips for aspiration"},
            {"failure": "Cell count reads zero or very low", "diagnosis": "Sample cup not properly seated, sample too dilute, or instrument optics dirty", "action": "Re-seat cup in carousel, verify sample was added, run instrument cleaning cycle and optics check"},
            {"failure": "High debris count obscuring cell images", "diagnosis": "Sample contains particulates, cell lysis has occurred, or media components interfering", "action": "Pre-filter sample through 40 um cell strainer if debris is excessive, check culture for contamination"},
            {"failure": "Instrument carousel jam or cup not detected", "diagnosis": "Cup not properly seated in carousel slot, carousel motor fault", "action": "Remove and re-seat cup ensuring click, restart carousel rotation, call service if motor error persists"},
            {"failure": "VCD values inconsistent between duplicate readings", "diagnosis": "Cells settling in sample cup, insufficient mixing, or air bubbles in sample path", "action": "Mix sample cup gently before re-reading, ensure 500 uL minimum volume, degas sample if foamy"}
        ],
        "notes": "Normal CHO range: VCD 5-30e6 cells/mL, viability >80%. Flag any viability below 70% immediately for process review. Record instrument serial number and calibration status."
    },

    {
        "assay_id": "BIO_005",
        "name": "ELISA — sandwich format for antigen or antibody quantification",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "Vaccines", "Fc-fusion proteins"],
        "purpose": "Quantify target protein, residual host cell protein (HCP), or specific antibody in process samples",
        "robot_steps": [
            "Verify deck layout: confirm high-binding ELISA plate at D1, sample rack at D2, standard/control rack at D3, reagent reservoirs at D4 (coating buffer, blocking buffer, PBS-T, TMB, stop solution), 100 uL multichannel tip box at D5, 10-100 uL single tip box at D6, plate seal station at D7, waste at D9",
            "Confirm all reagents are at room temperature 20-25 degrees C before starting — cold reagents cause uneven coating",
            "Pick up 100 uL multichannel tips from D5 — coat 96-well high-binding ELISA plate at D1 with 100 uL capture antibody at 1-4 ug/mL in coating buffer at 80 uL/sec from reservoir at D4",
            "Log trigger: record plate ID, capture antibody lot, coating concentration, timestamp",
            "Seal plate with adhesive film from D7 and incubate overnight at 4 degrees C or 2 hours at room temperature",
            "After incubation, wash plate 3 times with 300 uL PBS-T per well using plate washer at instrument interface D8 — verify washer aspirates all liquid, check for residual volume",
            "Block plate with 200 uL blocking buffer per well at 100 uL/sec from reservoir at D4 — incubate 1 hour at room temperature 20-25C",
            "Wash plate 3 times with 300 uL PBS-T via plate washer at D8",
            "Pick up 10-100 uL single tips from D6 — add 100 uL diluted standards in duplicate to columns 1-2 from standard rack at D3: 7-point curve from 1000 down to 3.9 ng/mL plus blank at 50 uL/sec",
            "Add 100 uL diluted samples in duplicate from sample rack D2 to remaining columns at 50 uL/sec — dilution factor per SOP",
            "Log trigger: record standard concentrations, sample IDs, well positions, dilution factors",
            "Seal plate and incubate 2 hours at room temperature on plate shaker at 300 rpm — temperature must remain 20-25C throughout",
            "Wash plate 3 times with 300 uL PBS-T via plate washer at D8",
            "Add 100 uL detection antibody at working concentration from reservoir at D4 at 80 uL/sec — incubate 1 hour at room temperature",
            "Wash plate 3 times with 300 uL PBS-T",
            "Add 100 uL streptavidin-HRP conjugate from reservoir at D4 at 80 uL/sec — incubate 30 minutes at room temperature in dark",
            "Wash plate 3 times with 300 uL PBS-T — ensure complete aspiration on final wash",
            "Add 100 uL TMB substrate from reservoir at D4 at 100 uL/sec — start timer, incubate exactly 10 minutes in dark, temperature 20-25C",
            "Add 100 uL stop solution (1 M H2SO4) from reservoir at D4 at 100 uL/sec — plate turns yellow, mix gently",
            "Read absorbance at 450 nm with reference at 620 nm in plate reader at instrument interface D8 within 30 minutes of stopping",
            "Log trigger: record plate ID, standard curve parameters and R-squared, sample IDs, dilution factors, OD values, calculated concentrations, timestamp"
        ],
        "robot_deck_layout": {
            "D1": "96-well high-binding ELISA plate — Corning 9018 or Nunc MaxiSorp",
            "D2": "Sample rack — 24-position tube rack with pre-diluted samples",
            "D3": "Standard and control rack — 8-position strip with 7-point standard curve plus blank, plus positive/negative controls",
            "D4": "Reagent reservoir bank — 5-trough reservoir: coating buffer, blocking buffer, PBS-T, TMB substrate, stop solution (1M H2SO4)",
            "D5": "Tip box 100 uL multichannel — full box 96 tips",
            "D6": "Tip box 10-100 uL single channel — full box 96 tips",
            "D7": "Plate seal station — adhesive film dispenser",
            "D8": "Instrument interface — plate washer and plate reader (450/620 nm)",
            "D9": "Waste container — tip discard and liquid waste"
        },
        "instruments_needed": ["Plate reader 450/620 nm", "Plate washer", "Multichannel pipette 8-channel", "Plate shaker/incubator", "Single channel pipette 10-100 uL"],
        "consumables": ["96-well high-binding ELISA plate (Corning 9018 or Nunc MaxiSorp)", "Adhesive plate seal", "Tips 100 uL multichannel", "Tips 10-100 uL", "Reagent reservoir"],
        "reagents": ["Capture antibody", "Blocking buffer (3% BSA or 5% milk in PBS)", "PBS-T (PBS + 0.05% Tween-20)", "Detection antibody biotinylated", "Streptavidin-HRP", "TMB substrate", "Stop solution 1M H2SO4", "Coating buffer (50 mM carbonate pH 9.6)"],
        "throughput": "80 samples per plate in 4 hours",
        "duration_minutes": 240,
        "sample_volume_uL": 100,
        "detection": "Absorbance 450 nm (reference 620 nm)",
        "regulatory": ["ICH Q6B", "ICH Q2(R2)"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "standard_curve_R2": ">= 0.995",
            "positive_control": "Within +/- 20% of expected value",
            "negative_control": "OD < 0.1 AU above blank",
            "sample_range": "Within linear range of standard curve (3.9 - 1000 ng/mL)",
            "pass_condition": "Standard curve R-squared >= 0.995, positive control within 20% of target, negative control near blank, and samples fall within linear range",
            "fail_action": "FLAG — if positive control out of range, flag plate for investigation; if sample OD above standard curve, PAUSE and re-dilute; if R-squared < 0.995, ABORT plate and repeat from coating step"
        },
        "troubleshooting": [
            {"failure": "High background across entire plate (OD > 0.3 in blank wells)", "diagnosis": "Insufficient washing, blocking buffer not effective, or TMB substrate contaminated", "action": "Increase wash cycles to 5x, switch blocking buffer from milk to BSA, use fresh TMB substrate"},
            {"failure": "Standard curve R-squared < 0.995", "diagnosis": "Standards improperly diluted, edge effect on plate, or coating was uneven", "action": "Re-prepare serial dilutions from fresh stock standard, move standards to inner columns, ensure plate was level during coating incubation"},
            {"failure": "No colour development after TMB addition", "diagnosis": "Streptavidin-HRP inactive or omitted, TMB substrate expired, or detection antibody not added", "action": "Check that all steps were performed in correct order, verify HRP conjugate storage at 2-8C and not frozen, use fresh TMB"},
            {"failure": "Edge effect — outer wells read higher than inner wells", "diagnosis": "Evaporation during long incubation, plate not sealed properly, or incubator humidity too low", "action": "Ensure plate seal is tight with no air gaps, add humidified chamber or wet paper towels in incubator, use inner wells only for critical samples"},
            {"failure": "Positive control out of range (> 20% deviation)", "diagnosis": "Control degraded, pipetting error, or plate-to-plate variability", "action": "Use fresh positive control aliquot, verify pipette accuracy with gravimetric check, include control on every plate to track trend"}
        ],
        "notes": "R-squared of standard curve must be >= 0.995. Samples outside the linear range must be re-run at adjusted dilution. Include positive and negative controls on every plate."
    },

    # ── SAFETY AND MICROBIOLOGICAL TESTING ───────────────────────────────

    {
        "assay_id": "BIO_006",
        "name": "Endotoxin testing by LAL gel-clot or kinetic chromogenic",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Vaccines", "Recombinant proteins", "ADCs", "Oligonucleotides"],
        "purpose": "Detect and quantify bacterial endotoxin (lipopolysaccharide) in drug substance and drug product — required for all parenteral products",
        "robot_steps": [
            "Verify deck layout: confirm endotoxin-free 96-well plate at D1, sample rack at D2 (depyrogenated tubes), LAL reagent vials at D3, endotoxin standard rack at D4, endotoxin-free tip box at D5, endotoxin-free water reservoir at D6, waste at D9 — ALL materials must be certified endotoxin-free",
            "Confirm all work is performed in dedicated endotoxin-free area — robot enclosure must be depyrogenated before run",
            "Set water bath or incubator at instrument interface D7 to exactly 37 degrees C — allow 30 minutes to equilibrate, verify temperature display reads 37.0 +/- 0.5C",
            "Log trigger: record incubator temperature, deck verification status, timestamp",
            "Pick up endotoxin-free tips from D5 — these must be depyrogenated, if tip pickup fails retry once then ABORT, do not use standard tips",
            "Reconstitute LAL reagent at D3 with endotoxin-free water from D6 per manufacturer instructions — aspirate water at 50 uL/sec, add to LAL vial, swirl gently, do not vortex",
            "Prepare endotoxin standard curve from CSE standard at D4: 4-point curve at 0.5, 0.25, 0.125, and 0.0625 EU/mL by serial dilution in endotoxin-free water at 30 uL/sec",
            "Prepare negative control: 100 uL endotoxin-free water into designated wells",
            "Dilute samples from D2 in endotoxin-free water to minimum valid dilution (MVD) per specification at 50 uL/sec",
            "For kinetic chromogenic method: add 100 uL LAL reagent at 60 uL/sec to each well of 96-well endotoxin-free plate at D1",
            "Add 100 uL of standard, control, or sample to each LAL well at 50 uL/sec — mix gently by pipetting 3 times",
            "Log trigger: record sample IDs, dilution factors, well positions, LAL reagent lot number",
            "Transfer plate to kinetic plate reader at instrument interface D7 at 37 degrees C — read at 405 nm every 1 minute for 60 minutes",
            "For gel-clot method: add 100 uL LAL reagent to endotoxin-free vial at D3, add 100 uL sample, incubate 60 min at 37C, invert — gel intact = positive",
            "After read, verify negative control shows no endotoxin detected and positive control spike recovery is 50-200%",
            "Log trigger: record sample ID, dilution factor, onset time, calculated EU/mL, spike recovery %, pass/fail vs specification, timestamp",
            "Discard all materials to endotoxin waste at D9 — do not reuse any consumables"
        ],
        "robot_deck_layout": {
            "D1": "Endotoxin-free 96-well plate — certified depyrogenated, sealed until use",
            "D2": "Sample rack — depyrogenated tube rack with samples in endotoxin-free vials",
            "D3": "LAL reagent station — lyophilised LAL vials and reconstitution position",
            "D4": "Endotoxin standard rack — CSE 10 EU/vial with serial dilution positions",
            "D5": "Tip box — depyrogenated endotoxin-free tips only",
            "D6": "Reagent reservoir — endotoxin-free water (LAL grade), minimum 20 mL",
            "D7": "Instrument interface — kinetic plate reader with 37C incubation and 405 nm detection",
            "D8": "Empty — reserved, must remain uncontaminated",
            "D9": "Endotoxin waste — dedicated waste container for depyrogenated materials"
        },
        "instruments_needed": ["Endotoxin-specific kinetic plate reader (Charles River Endosafe nexgen-PTS or Lonza ELx808)", "Water bath or incubator 37C exactly", "Pipette 10-100 uL", "Vortex mixer"],
        "consumables": ["LAL endotoxin-free 96-well plate", "Endotoxin-free tips depyrogenated", "Endotoxin-free vials", "Endotoxin-free water"],
        "reagents": ["LAL reagent (Lonza, Associates of Cape Cod, or Charles River)", "Control standard endotoxin (CSE) 10 EU/vial", "Endotoxin-free water"],
        "throughput": "32 samples per plate (run in duplicate with controls)",
        "duration_minutes": 90,
        "sample_volume_uL": 100,
        "detection": "Turbidimetric or chromogenic at 405 nm",
        "regulatory": ["USP 85 Bacterial Endotoxins Test", "Ph. Eur. 2.6.14", "21 CFR 610.13"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "drug_substance_mAb": "< 1.0 EU/mg",
            "drug_product_IV": "< 0.5 EU/mL",
            "spike_recovery": "50 - 200%",
            "negative_control": "< 0.0625 EU/mL (below lowest standard)",
            "pass_condition": "Sample endotoxin below specification limit, negative control undetectable, and positive product control spike recovery 50-200%",
            "fail_action": "ABORT — if spike recovery outside 50-200%, test is invalid and must be repeated with adjusted MVD; if sample exceeds specification, ALERT QA immediately and quarantine lot"
        },
        "troubleshooting": [
            {"failure": "Spike recovery outside 50-200% range", "diagnosis": "Product matrix is interfering with LAL reaction — either inhibiting or enhancing", "action": "Increase dilution to higher MVD to overcome matrix interference, perform full product interference test (PIT) at multiple dilutions"},
            {"failure": "Negative control shows endotoxin detected", "diagnosis": "Contamination of endotoxin-free water, tips, or plate — endotoxin is extremely sticky and ubiquitous", "action": "Discard all materials and start with fresh certified endotoxin-free supplies, clean robot deck with depyrogenation solution, re-run"},
            {"failure": "Standard curve does not meet linearity (R-squared < 0.980)", "diagnosis": "CSE standard degraded, serial dilution error, or reader temperature not stable at 37C", "action": "Use fresh CSE vial, re-prepare serial dilutions carefully with endotoxin-free tips, verify incubator temperature with independent thermometer"},
            {"failure": "All samples read as positive/high endotoxin", "diagnosis": "Widespread contamination of sampling materials, sample port, or robot deck", "action": "Investigate contamination source — re-sample using new endotoxin-free supplies, clean all contact surfaces, consider environmental monitoring"},
            {"failure": "Kinetic reader shows erratic onset times", "diagnosis": "Air bubbles in wells, plate not level in reader, or reader lamp failing", "action": "Ensure no bubbles before inserting plate, verify plate is seated flat in reader, run reader self-diagnostics"}
        ],
        "notes": "Conduct product interference test (PIT) before first use on a new product. Spike recovery must be 50-200%. Endotoxin-free technique is critical — gloves must be worn throughout. All materials must be certified endotoxin-free."
    },

    {
        "assay_id": "BIO_007",
        "name": "rFC recombinant endotoxin assay (PyroGene / Endosafe rFC)",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Vaccines", "Cell and Gene Therapy", "Recombinant proteins"],
        "purpose": "Animal-free alternative to LAL for endotoxin detection — recombinant Factor C method per USP 86",
        "robot_steps": [
            "Verify deck layout: confirm black flat-bottom fluorescence plate at D1, sample rack at D2 (endotoxin-free vials), rFC reagent station at D3, endotoxin standard rack at D4, 2-20 uL tip box at D5, multichannel tip box at D6, endotoxin-free water reservoir at D7, waste at D9",
            "Confirm all materials are certified endotoxin-free — log lot numbers for tips, plate, and water",
            "Equilibrate rFC reagent at D3 to room temperature 20-25C for 15 minutes — do not vortex, gentle swirl only",
            "Log trigger: record rFC reagent lot, expiry date, equilibration start time, ambient temperature",
            "Pick up 2-20 uL tips from D5 — if tip pickup fails, retry once then ABORT, must use endotoxin-free tips only",
            "Prepare endotoxin standard curve from CSE at D4: 5-point from 10 down to 0.1 EU/mL by serial dilution in endotoxin-free water from D7 at 10 uL/sec dispensing speed",
            "Prepare negative control: 10 uL endotoxin-free water into designated wells on plate at D1",
            "Prepare positive product control: spike sample with 1 EU/mL endotoxin for recovery check",
            "Aspirate 10 uL of rFC reagent working solution at 5 uL/sec from D3 — add to each well of black flat-bottom fluorescence plate at D1",
            "Add 10 uL of standard, control, or sample to each well at 5 uL/sec — slow dispensing critical for 10 uL volumes",
            "Mix by pipetting up and down 3 times at 8 uL/sec — avoid creating bubbles in black plate",
            "Log trigger: record well map, sample IDs, standard concentrations, spike concentration",
            "Seal plate with clear adhesive seal from seal station at D8 — press firmly, no air gaps",
            "Transfer plate to fluorescence plate reader at instrument interface D7 — incubate at 37 degrees C",
            "Read fluorescence (excitation 380 nm, emission 440 nm) every 5 minutes for 60 minutes at 37C",
            "Calculate onset time and endotoxin concentration from standard curve — verify R-squared >= 0.980",
            "Verify positive product control spike recovery is 50-200% — if outside range, test is invalid",
            "Log trigger: record sample ID, spiked control recovery %, calculated EU/mL, pass/fail, onset times, timestamp"
        ],
        "robot_deck_layout": {
            "D1": "Black flat-bottom 96-well fluorescence plate — certified endotoxin-free",
            "D2": "Sample rack — endotoxin-free vials with samples, depyrogenated rack",
            "D3": "rFC reagent station — reconstituted rFC working solution on ice or cold block",
            "D4": "Endotoxin standard rack — CSE serial dilution positions (5-point curve)",
            "D5": "Tip box 2-20 uL — depyrogenated endotoxin-free tips",
            "D6": "Tip box multichannel — depyrogenated endotoxin-free tips",
            "D7": "Instrument interface — fluorescence plate reader with 37C heating (ex380/em440)",
            "D8": "Plate seal station — clear adhesive seal dispenser",
            "D9": "Endotoxin waste — dedicated waste container"
        },
        "instruments_needed": ["Fluorescence plate reader (excitation 380 nm, emission 440 nm)", "Incubator or plate reader with heating 37C", "Pipette 2-20 uL", "Multichannel pipette"],
        "consumables": ["Black flat-bottom 96-well plate", "Clear adhesive plate seal", "Endotoxin-free tips", "Endotoxin-free water"],
        "reagents": ["rFC reagent (Lonza PyroGene or Charles River Endosafe rFC)", "CSE endotoxin standard", "Endotoxin-free water"],
        "throughput": "32 samples per plate",
        "duration_minutes": 75,
        "sample_volume_uL": 10,
        "detection": "Fluorescence excitation 380 nm emission 440 nm",
        "regulatory": ["USP 86 Bacterial Endotoxins Using Recombinant Factor C", "Ph. Eur. 2.6.32"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "endotoxin_limit_drug_substance": "< 1.0 EU/mg",
            "endotoxin_limit_drug_product": "< 0.5 EU/mL",
            "spike_recovery": "50 - 200%",
            "standard_curve_R2": ">= 0.980",
            "pass_condition": "Sample endotoxin below specification, spike recovery 50-200%, standard curve R-squared >= 0.980, and negative control undetectable",
            "fail_action": "ABORT — if spike recovery outside 50-200%, test is invalid, repeat with adjusted dilution; if sample exceeds limit, ALERT QA and quarantine lot immediately"
        },
        "troubleshooting": [
            {"failure": "Fluorescence signal does not increase over 60 minutes", "diagnosis": "rFC reagent inactive — may have been frozen, expired, or vortexed", "action": "Check reagent storage history (must be 2-8C, never frozen), use fresh vial, confirm by running positive control"},
            {"failure": "Spike recovery below 50%", "diagnosis": "Product matrix inhibiting rFC enzymatic reaction", "action": "Increase sample dilution to reduce matrix effect, verify MVD calculation, run inhibition/enhancement test at multiple dilutions"},
            {"failure": "High background fluorescence in blank wells", "diagnosis": "Plate autofluorescence, endotoxin contamination of water or tips, or reader settings incorrect", "action": "Verify black plate with low autofluorescence is used, open fresh endotoxin-free water, check reader excitation/emission wavelengths"},
            {"failure": "Standard curve onset times not decreasing with concentration", "diagnosis": "Serial dilution error — standards not prepared correctly", "action": "Re-prepare standards from fresh CSE vial using clean endotoxin-free tips at each dilution step"},
            {"failure": "Reader temperature not reaching 37C", "diagnosis": "Plate reader heating element fault or lid not closed properly", "action": "Pre-heat reader for 30 minutes before use, verify temperature with external probe, close reader lid securely"}
        ],
        "notes": "rFC method is animal-free and preferred for new product development. Spike recovery 50-200% required. Cross-validate with LAL for submission if regulatory agency requires."
    },

    {
        "assay_id": "BIO_008",
        "name": "Mycoplasma PCR detection (MycoAlert PLUS or MycoSEQ)",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Cell and Gene Therapy", "Vaccines", "Recombinant proteins"],
        "purpose": "Detect mycoplasma contamination in cell culture supernatants — required safety test for all biopharmaceutical products",
        "robot_steps": [
            "Verify deck layout: confirm 4 mL collection tube rack at D1, 1.5 mL tube rack at D2, luminometer tube rack at D3, MycoAlert reagent station at D4, 200 uL tip box at D5, 1000 uL tip box at D6, waste at D9",
            "Confirm room temperature 20-25 degrees C — MycoAlert reagents are temperature-sensitive",
            "Pick up 1000 uL tip from D6 — if tip pickup fails, retry once then pause and alert operator",
            "Collect 4 mL of cell culture supernatant from bioreactor or flask at instrument interface D7 — without cells, aspirate at 200 uL/sec from top of liquid to avoid cell pellet",
            "Transfer to collection tube at D1 position A1 — log sample ID, batch code, passage number",
            "Transfer collection tube to centrifuge at D8 — centrifuge at 300 x g for 5 minutes to remove cells and debris",
            "After centrifuge, pick up fresh 1000 uL tip from D6 — aspirate 1 mL of clarified supernatant at 150 uL/sec from top of liquid, avoid pellet",
            "Dispense 1 mL into a clean 1.5 mL tube at D2 at 100 uL/sec — verify liquid level after dispense",
            "Log trigger: record sample ID, batch code, passage number, clarification method, timestamp",
            "Discard 1000 uL tip — pick up 200 uL tip from D5 for MycoAlert PLUS luminescence method",
            "Aspirate 100 uL of sample at 50 uL/sec from 1.5 mL tube at D2 — dispense into luminometer tube at D3",
            "Aspirate 100 uL MycoAlert Assay Reagent at 50 uL/sec from reagent station D4 — dispense into luminometer tube",
            "Incubate 5 minutes at room temperature 20-25C — start timer",
            "Place luminometer tube in luminometer at instrument interface D7 — read luminescence (reading A)",
            "Pick up fresh 200 uL tip from D5 — aspirate 100 uL MycoAlert Substrate at 50 uL/sec from D4 — dispense into same luminometer tube",
            "Incubate exactly 10 minutes at room temperature — start timer",
            "Read luminescence again in luminometer (reading B) — calculate ratio B/A",
            "Log trigger: record sample ID, reading A, reading B, ratio B/A, result interpretation (< 0.9 negative, 0.9-1.2 borderline, > 1.2 positive), timestamp",
            "If ratio > 1.2: ALERT — mycoplasma positive, do not proceed with culture, notify QA immediately",
            "Discard all tips and tubes to waste at D9 — advance to next sample"
        ],
        "robot_deck_layout": {
            "D1": "4 mL collection tube rack — 24-position rack for raw supernatant collection",
            "D2": "1.5 mL tube rack — 24-position rack for clarified supernatant aliquots",
            "D3": "Luminometer tube rack — 12-position rack for luminometer-compatible tubes",
            "D4": "MycoAlert reagent station — Assay Reagent and Substrate vials, plus positive and negative controls",
            "D5": "Tip box 200 uL — full box 96 tips",
            "D6": "Tip box 1000 uL — full box 96 tips",
            "D7": "Instrument interface — luminometer and bioreactor sample port",
            "D8": "Microcentrifuge — for cell clarification at 300 x g",
            "D9": "Waste container — tip and tube discard"
        },
        "instruments_needed": ["Luminometer (MycoAlert) or qPCR instrument (MycoSEQ)", "Microcentrifuge", "Pipette 20-200 uL", "Pipette 200-1000 uL"],
        "consumables": ["Luminometer tubes or PCR plates", "1.5 mL collection tubes", "Tips 200 uL and 1000 uL"],
        "reagents": ["MycoAlert PLUS Assay Reagent (Lonza)", "MycoAlert Substrate", "Positive control provided with kit", "Negative control (culture medium)"],
        "throughput": "12 samples per 45 minutes",
        "duration_minutes": 45,
        "sample_volume_uL": 1000,
        "detection": "Bioluminescence ratio B/A > 1.2 positive",
        "regulatory": ["21 CFR 610.30", "Ph. Eur. 2.6.7", "USP 63", "ICH Q5A(R2)"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "negative_result": "Ratio B/A < 0.9",
            "borderline_result": "Ratio B/A 0.9 - 1.2 (requires repeat testing)",
            "positive_result": "Ratio B/A > 1.2 (mycoplasma detected)",
            "positive_control": "Must read positive (ratio > 1.2)",
            "negative_control": "Must read negative (ratio < 0.9)",
            "pass_condition": "Sample ratio B/A < 0.9, positive control > 1.2, negative control < 0.9",
            "fail_action": "ALERT — if ratio > 1.2, immediately alert QA and quarantine culture; if borderline 0.9-1.2, PAUSE and repeat test with fresh sample within 24 hours; if controls fail, ABORT and re-run with fresh reagents"
        },
        "troubleshooting": [
            {"failure": "Positive control reads negative (ratio < 0.9)", "diagnosis": "MycoAlert reagent degraded, incorrect reagent added, or luminometer sensitivity too low", "action": "Check reagent expiry date and storage (2-8C), verify correct reagent added in correct order, run luminometer calibration"},
            {"failure": "Borderline ratio 0.9-1.2 on repeat testing", "diagnosis": "Low-level contamination, media interference, or reagent variability at detection limit", "action": "Run confirmatory MycoSEQ PCR test which is more sensitive, test fresh sample from same culture, investigate culture visually for slow growth"},
            {"failure": "Very high reading A (background) masking ratio", "diagnosis": "Media contains high ATP from dead cells or media additives interfering", "action": "Centrifuge sample more thoroughly to remove all cells, dilute sample 1:2 in fresh media and re-test"},
            {"failure": "Luminometer gives error or no reading", "diagnosis": "Tube not properly seated, luminometer door not closed, or PMT tube aging", "action": "Re-seat tube ensuring click, close door fully, run luminometer self-test, replace PMT if readings are consistently low"},
            {"failure": "All samples reading positive in batch", "diagnosis": "Widespread contamination in incubator or media supply, or reagent contamination", "action": "Test media-only control to rule out reagent issue, inspect incubator for contamination, quarantine all affected cultures and notify QA"}
        ],
        "notes": "Test cell culture supernatant every 2 weeks during culture and before banking. Include positive and negative controls on every run. A ratio of 0.9-1.2 is borderline — repeat test before concluding negative."
    },

    {
        "assay_id": "BIO_009",
        "name": "Bioburden by membrane filtration",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Vaccines", "Recombinant proteins", "ADCs"],
        "purpose": "Count total viable microorganisms in in-process samples, purified drug substance, and drug product",
        "robot_steps": [
            "Verify deck layout: confirm membrane filtration apparatus at D1 (inside BSC), sample bottles at D2, SCDA plate rack at D3, SDA plate rack at D4, sterile diluent reservoir at D5, sterile forceps at D6, waste at D9 — all operations inside biological safety cabinet",
            "Confirm biological safety cabinet is running and certified — log BSC serial number, last certification date",
            "Confirm ambient temperature 20-25 degrees C in BSC — log temperature",
            "Pick up sterile membrane filter (0.45 um cellulose nitrate, 47 mm) using sterile forceps from D6 — place on filtration base at D1",
            "Prewet membrane with 10 mL sterile water from D5 at 200 uL/sec — apply gentle vacuum to draw through",
            "Log trigger: record membrane lot number, filter size, sample ID, timestamp",
            "Transfer sample volume per specification to membrane filtration funnel at D1 — for mAb drug substance: pour or pipette up to 100 mL (100000 uL) sample from D2",
            "Apply vacuum at 15-20 inHg to draw sample through membrane — monitor filtration time, if > 10 minutes the membrane may be clogged",
            "Wash membrane 3 times with 100 mL sterile diluent (0.1% peptone water) from D5 — each wash at full vacuum",
            "Release vacuum — carefully remove membrane using sterile forceps from D6",
            "Transfer first membrane aseptically onto SCDA (Soybean Casein Digest Agar) plate at D3 — ensure membrane is flat with no air bubbles underneath",
            "Repeat filtration with second aliquot — transfer second membrane onto SDA (Sabouraud Dextrose Agar) plate at D4",
            "Log trigger: record plate IDs, membrane placement, incubation start time",
            "Transfer SCDA plates to incubator at instrument interface D7 — incubate at 30-35 degrees C for 5 days (TAMC — total aerobic microbial count)",
            "Transfer SDA plates to second incubator at D7 — incubate at 20-25 degrees C for 5 days (TYMC — total yeast and mould count)",
            "At day 3 perform interim read — count any visible colonies, record but do not report as final",
            "At day 5 perform final count using colony counter at D8 — count all colonies on each plate",
            "Log trigger: record sample ID, volume filtered, TAMC count CFU/mL, TYMC count CFU/mL, pass/fail vs specification, incubation dates, analyst ID"
        ],
        "robot_deck_layout": {
            "D1": "Membrane filtration apparatus — sterile funnel, membrane support, and vacuum manifold inside BSC",
            "D2": "Sample bottles — sterile bottles containing up to 100 mL sample",
            "D3": "SCDA plate rack — pre-poured Soybean Casein Digest Agar plates",
            "D4": "SDA plate rack — pre-poured Sabouraud Dextrose Agar plates",
            "D5": "Sterile diluent reservoir — 0.1% peptone water, minimum 500 mL",
            "D6": "Sterile forceps station — autoclaved forceps for membrane handling",
            "D7": "Instrument interface — incubators (30-35C and 20-25C)",
            "D8": "Colony counter — illuminated platform for counting",
            "D9": "Biohazard waste — for used membranes, plates, and consumables"
        },
        "instruments_needed": ["Biological safety cabinet class II", "Membrane filtration apparatus", "Vacuum pump", "Colony counter", "Incubator 30-35C and 20-25C"],
        "consumables": ["0.45 um cellulose nitrate membrane filters 47mm", "SCDA plates", "SDA plates", "Sterile filtration funnels", "Sterile diluent (0.1% peptone water)", "Sterile forceps"],
        "reagents": ["SCDA (Soybean Casein Digest Agar)", "SDA (Sabouraud Dextrose Agar)", "0.1% peptone water diluent"],
        "throughput": "6 samples per setup per BSC",
        "duration_minutes": 30,
        "sample_volume_uL": 100000,
        "detection": "Visual colony count",
        "regulatory": ["USP 61 Microbial Examination of Non-Sterile Products", "USP 62 Tests for Specified Microorganisms", "Ph. Eur. 2.6.12", "Ph. Eur. 2.6.13"],
        "automation_difficulty": "complex",
        "acceptance_criteria": {
            "drug_substance_TAMC": "<= 100 CFU/mL",
            "drug_substance_TYMC": "<= 10 CFU/mL",
            "negative_control": "0 CFU (sterile diluent must show no growth)",
            "positive_control": "ATCC organisms must show expected recovery (50-200%)",
            "pass_condition": "TAMC <= 100 CFU/mL, TYMC <= 10 CFU/mL, negative control is zero, and positive control recovery 50-200%",
            "fail_action": "ALERT — if any plate exceeds specification, immediately alert QA and hold lot; if negative control shows growth, ABORT and investigate BSC sterility and technique; if positive control fails, ABORT and investigate media performance"
        },
        "troubleshooting": [
            {"failure": "Negative control plate shows colonies", "diagnosis": "Environmental contamination in BSC, non-sterile technique, or contaminated diluent", "action": "Repeat test with fresh sterile supplies, perform BSC settle plates to check environment, review aseptic technique training"},
            {"failure": "Membrane clogs during filtration — sample does not filter", "diagnosis": "Sample has high particulate load, protein concentration causing membrane fouling", "action": "Pre-filter sample through 5 um prefilter, dilute sample if appropriate, use larger pore size membrane if validated"},
            {"failure": "Positive control organisms not recovered (< 50%)", "diagnosis": "Media not supporting growth, wrong incubation temperature, or organisms were non-viable", "action": "Check media lot with growth promotion testing, verify incubator temperature with calibrated probe, use fresh ATCC cultures"},
            {"failure": "TNTC (too numerous to count) on sample plates", "diagnosis": "Very high bioburden indicating serious contamination or sampling error", "action": "Re-test with diluted sample (1:10, 1:100), investigate upstream process for contamination source, alert QA immediately"},
            {"failure": "Colony morphology is unusual or unrecognizable", "diagnosis": "Environmental contaminant from BSC, unusual organism in product, or mould growth", "action": "Subculture colony for Gram stain and identification, send to micro lab for species ID, document and photograph colony appearance"}
        ],
        "notes": "Positive controls (ATCC organisms) must be run with every batch to confirm media performance. Negative controls (sterile diluent) must show zero colonies. Record incubation dates and colony counts at interim read points."
    },

    # ── PHYSICOCHEMICAL CHARACTERISATION ──────────────────────────────────

    {
        "assay_id": "BIO_010",
        "name": "Osmolality measurement",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Vaccines", "Recombinant proteins", "Cell and Gene Therapy"],
        "purpose": "Measure osmotic concentration of formulation buffers, cell culture media, and drug product — critical for cell physiology and product stability",
        "robot_steps": [
            "Verify deck layout: confirm sample rack at D1, microcapillary tube dispenser at D2, lint-free wipe station at D3, calibration standard rack at D4, 10 uL tip box at D5, waste at D9",
            "Power on Vapro 5600 or Advanced Instruments 3320 osmometer at instrument interface D7 — allow 30 minute warm-up",
            "Confirm ambient temperature 20-25 degrees C — log room temperature",
            "Pick up 290 mOsm/kg calibration standard from D4 — calibrate instrument, record calibration result on worksheet",
            "Verify calibration with 500 mOsm/kg standard from D4 — must read within +/- 5 mOsm/kg of expected value",
            "Log trigger: record calibration results, standard lot numbers, instrument ID, timestamp",
            "Clean sample well with lint-free wipe from D3 between each measurement",
            "Pick up microcapillary tube from dispenser at D2 — aspirate exactly 10 uL of sample from sample rack D1 at slow speed 5 uL/sec",
            "Verify liquid level in microcapillary — if not detected or air gap present, discard and re-aspirate",
            "Dispense 10 uL into osmometer sample well at instrument interface D7 using supplied microcapillary",
            "Lower sample well cover and press measure — instrument freezes sample and measures freezing point depression automatically at controlled temperature",
            "Wait for reading to stabilize (approximately 60 seconds) — record osmolality in mOsm/kg from display",
            "Log trigger: record sample ID, reading number, osmolality value, timestamp",
            "Clean sample well with lint-free wipe from D3 — discard used microcapillary to waste at D9",
            "Repeat measurement 2 more times for triplicate — use fresh microcapillary each time",
            "Calculate mean and CV% from three readings — if CV > 2%, run 2 additional replicates and investigate",
            "Log trigger: record sample ID, all three readings, mean osmolality, CV%, pass/fail, date, instrument ID, calibration status",
            "Advance to next sample at D1 — repeat cleaning and measurement cycle"
        ],
        "robot_deck_layout": {
            "D1": "Sample rack — 24-position tube rack for sample tubes",
            "D2": "Microcapillary tube dispenser — pre-loaded with 10 uL capillary tubes",
            "D3": "Lint-free wipe station — stack of lint-free wipes for cleaning sample well",
            "D4": "Calibration standard rack — 290 mOsm/kg and 500 mOsm/kg standards",
            "D5": "Tip box 10 uL — full box (backup for capillary if needed)",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — Vapro 5600 or Advanced Instruments 3320 osmometer",
            "D8": "Empty — reserved",
            "D9": "Waste container — used capillaries and wipes"
        },
        "instruments_needed": ["Vapro 5600 (ELITechGroup) or Advanced Instruments Model 3320 osmometer"],
        "consumables": ["10 uL microcapillary tubes (supplied with instrument)", "Lint-free wipes", "290 mOsm calibration standard", "500 mOsm calibration standard"],
        "reagents": ["290 mOsm/kg calibration standard", "500 mOsm/kg calibration standard"],
        "throughput": "20 samples per hour",
        "duration_minutes": 3,
        "sample_volume_uL": 10,
        "detection": "Freezing point depression",
        "regulatory": ["USP 785 Osmolality and Osmolarity", "Ph. Eur. 2.2.35"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "drug_product_range": "280 - 310 mOsm/kg (isotonic)",
            "cell_culture_media": "280 - 320 mOsm/kg",
            "triplicate_CV": "<= 2%",
            "calibration_check": "500 mOsm standard reads 495 - 505 mOsm/kg",
            "pass_condition": "Osmolality within specified range for product type, triplicate CV <= 2%, and calibration verification within +/- 5 mOsm/kg",
            "fail_action": "FLAG — if osmolality outside 270-330 mOsm/kg for drug product, flag for formulation review; if CV > 2%, re-run with fresh capillaries; if calibration check fails, ABORT and recalibrate instrument"
        },
        "troubleshooting": [
            {"failure": "CV between triplicates exceeds 2%", "diagnosis": "Inconsistent sample loading in capillary, air bubbles in sample, or sample well not clean", "action": "Use fresh capillary for each reading, ensure no air gaps in sample, clean well thoroughly with lint-free wipe between each reading"},
            {"failure": "Calibration standard reads outside +/- 5 mOsm/kg", "diagnosis": "Calibration standard expired or contaminated, instrument sensor needs cleaning, or thermoelectric cooler degraded", "action": "Use fresh unopened calibration standard, clean sample well and sensor, call service if calibration still fails"},
            {"failure": "Reading shows ERROR or does not stabilize", "diagnosis": "Insufficient sample volume (< 10 uL), sample too viscous, or sensor malfunction", "action": "Ensure full 10 uL loaded into well, dilute viscous samples if appropriate, restart instrument and retry"},
            {"failure": "Osmolality reads significantly higher than expected", "diagnosis": "Sample has evaporated concentrating solutes, or sample was not at room temperature", "action": "Check sample storage conditions, equilibrate sample to room temperature, re-prepare if evaporation suspected"},
            {"failure": "Osmolality values drift upward over sequential readings", "diagnosis": "Sample evaporation during measurement, ambient temperature increasing, or carry-over between samples", "action": "Work quickly to minimize evaporation, check room temperature stability, increase cleaning between samples"}
        ],
        "notes": "Typical formulation buffer target: 280-310 mOsm/kg (isotonic). Cell culture media typically 280-320 mOsm/kg. Results outside 270-330 mOsm/kg for drug product should be investigated. CV between triplicates should be < 2%."
    },

    {
        "assay_id": "BIO_011",
        "name": "pH and conductivity measurement",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Vaccines", "Recombinant proteins", "ADCs", "Oligonucleotides"],
        "purpose": "In-process and final product pH and conductivity measurement for buffer verification, formulation QC, and process monitoring",
        "robot_steps": [
            "Verify deck layout: confirm sample beakers at D1 (minimum 15 mL per sample), pH calibration buffers at D2 (pH 4.01, 7.00, 10.01), conductivity standard at D3, rinse water reservoir at D4, lint-free wipes at D5, waste at D9",
            "Power on pH/conductivity meter (Mettler Toledo SevenExcellence or equivalent) at instrument interface D7 — allow 10 minute stabilization",
            "Confirm ambient temperature 20-25 degrees C — log room temperature (temperature affects both pH and conductivity)",
            "Calibrate pH electrode with 3-point calibration: immerse in pH 4.01 buffer from D2, wait for stable reading, accept; repeat with pH 7.00 and pH 10.01 — record slope and offset",
            "Verify pH calibration slope is 95-105% — if outside range, clean electrode and recalibrate",
            "Rinse electrode with purified water from D4 and blot dry with lint-free wipe from D5 — do not wipe, blot only",
            "Calibrate conductivity cell with standard (1413 uS/cm) from D3 — record cell constant",
            "Log trigger: record pH calibration slope, offset, buffer lot numbers, conductivity cell constant, timestamp",
            "For pH measurement: immerse electrode in minimum 10 mL (10000 uL) of sample at D1 — ensure electrode bulb and junction are fully submerged",
            "Wait for stable reading — stability symbol appears on display, typically 15-30 seconds, temperature must be 20-25C",
            "Record pH to 2 decimal places (e.g. 7.02) — press store on meter",
            "Log trigger: record sample ID, pH value, temperature at measurement, timestamp",
            "Rinse electrode with purified water from D4 — blot with lint-free wipe from D5",
            "For conductivity: immerse conductivity cell in same sample at D1 — ensure cell is fully submerged",
            "Wait for stable reading — record conductivity in mS/cm or uS/cm to appropriate precision",
            "Log trigger: record sample ID, conductivity value, temperature, units (mS/cm or uS/cm)",
            "Rinse both electrode and conductivity cell with purified water from D4 between samples — blot dry",
            "Advance to next sample at D1 — repeat measurement cycle for all samples in batch"
        ],
        "robot_deck_layout": {
            "D1": "Sample beakers — 24-position rack for 15 mL+ sample beakers or tubes",
            "D2": "pH calibration buffer rack — pH 4.01, 7.00, and 10.01 buffer bottles",
            "D3": "Conductivity standard — 1413 uS/cm or 12.88 mS/cm standard",
            "D4": "Rinse water reservoir — purified water for electrode rinsing, minimum 500 mL",
            "D5": "Lint-free wipe station — for blotting electrodes dry",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — pH/conductivity meter with electrode and cell mounted on robot arm",
            "D8": "Electrode storage — 3M KCl storage solution for pH electrode when not in use",
            "D9": "Waste container — rinse water waste"
        },
        "instruments_needed": ["pH/conductivity benchtop meter (Mettler Toledo SevenExcellence, Thermo Fisher Orion Versa Star)", "pH electrode InLab Expert Pro", "Conductivity cell InLab 731"],
        "consumables": ["pH 4.01, 7.00, 10.01 calibration buffers", "Conductivity standard", "Purified water for rinsing", "Lint-free wipes"],
        "reagents": ["pH calibration buffer 4.01", "pH calibration buffer 7.00", "pH calibration buffer 10.01", "Conductivity standard 1413 uS/cm"],
        "throughput": "30 samples per hour",
        "duration_minutes": 2,
        "sample_volume_uL": 10000,
        "detection": "Potentiometric (pH), conductometric",
        "regulatory": ["USP 791 pH", "USP 645 Water Conductivity", "Ph. Eur. 2.2.3 Potentiometric determination of pH", "Ph. Eur. 2.2.38"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "pH_calibration_slope": "95 - 105%",
            "pH_precision": "+/- 0.05 pH units between replicates",
            "conductivity_precision": "+/- 5% between replicates",
            "buffer_pH_target": "Within +/- 0.3 pH units of specification",
            "pass_condition": "pH and conductivity values within specification for the buffer or product being tested, calibration slope 95-105%, and replicate precision within tolerance",
            "fail_action": "FLAG — if pH or conductivity outside specification, flag for investigation and re-measurement; if calibration slope outside 95-105%, PAUSE and replace electrode or recalibrate with fresh buffers"
        },
        "troubleshooting": [
            {"failure": "pH reading drifts and never stabilizes", "diagnosis": "Electrode junction blocked, electrode dehydrated, or sample has very low ionic strength", "action": "Soak electrode in 3M KCl for 30 minutes, try conditioning in pH 4 buffer, add electrolyte bridge for low-conductivity samples"},
            {"failure": "Calibration slope below 95%", "diagnosis": "Electrode aging, junction contaminated with protein, or calibration buffers expired", "action": "Clean electrode with pepsin/HCl cleaning solution, use fresh calibration buffers, replace electrode if slope remains low after cleaning"},
            {"failure": "Conductivity reads zero or very low", "diagnosis": "Conductivity cell air bubble, cell not fully submerged, or cell constant lost", "action": "Ensure cell is fully submerged with no air bubbles, recalibrate cell constant with fresh standard, check cable connection"},
            {"failure": "pH reads same value for different samples", "diagnosis": "Electrode is not responding — possibly broken glass membrane or dried out", "action": "Check electrode glass bulb for cracks, soak in 3M KCl storage solution overnight, replace electrode if not responsive after conditioning"},
            {"failure": "Temperature compensation error on meter", "diagnosis": "Temperature probe disconnected or faulty, or sample temperature outside compensatable range", "action": "Verify temperature probe connection, ensure samples are equilibrated to 20-25C before reading, use manual temperature input if probe fails"}
        ],
        "notes": "Allow electrode to condition in sample for 30 seconds before reading if sample matrix differs significantly from calibration buffers. Store pH electrode in 3 M KCl storage solution when not in use — never store dry."
    },

    {
        "assay_id": "BIO_012",
        "name": "Subvisible particle count by Micro-Flow Imaging (MFI)",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Bispecific antibodies", "Vaccines", "ADCs"],
        "purpose": "Count and characterise subvisible particles at 2, 5, 10, and 25 micron thresholds in drug substance and drug product",
        "robot_steps": [
            "Verify deck layout: confirm sample rack at D1 (handle gently — do not shake), MFI sample vials at D2, HPLC-grade water reservoir at D3, 1000 uL low-protein-binding tip box at D4, waste at D9",
            "Power on ProteinSimple MFI 5200 at instrument interface D7 and allow 30 minute warm-up — verify illumination source is stable",
            "Confirm ambient temperature 20-25 degrees C — log room temperature",
            "Prime instrument with HPLC-grade water filtered through 0.1 um from D3 — run 3 purge cycles at 200 uL/sec",
            "Run system suitability blank: analyse 0.65 mL HPLC-grade water — verify background particle count below limit (< 25 particles/mL at >= 10 um)",
            "Log trigger: record system suitability result, background particle count, instrument ID, timestamp",
            "If background fails (>= 25 particles/mL at 10 um), run 3 additional purges and re-test — if still failing, ABORT and call service",
            "Pick up 1000 uL low-protein-binding tip from D4 — standard tips may shed particles",
            "Gently invert sample tube at D1 exactly 10 times — do not vortex, shake, or create bubbles, handle at room temperature 20-25C",
            "Aspirate 1000 uL (1 mL) of sample at 100 uL/sec from sample tube at D1 — slow aspiration to avoid generating particles",
            "Verify liquid level detected — if insufficient volume, flag and skip sample",
            "Dispense 1000 uL into MFI sample vial at D2 at 80 uL/sec — dispense against wall to avoid bubbles",
            "Load MFI sample vial into instrument at D7 — enter sample ID in software",
            "Run 0.65 mL analysis volume — instrument automatically discards first 0.2 mL as priming volume and images remaining sample",
            "Instrument images and counts particles automatically at 2, 5, 10, and 25 um thresholds — also records morphology (aspect ratio, transparency, circularity)",
            "Log trigger: record sample ID, particles/mL at 2 um, 5 um, 10 um, 25 um thresholds, morphology summary, run date",
            "Allow purge cycle between samples — 3 washes with filtered HPLC-grade water from D3, verify background returns to < 25 particles/mL at 10 um",
            "Discard tip to waste at D9 — advance to next sample"
        ],
        "robot_deck_layout": {
            "D1": "Sample rack — 24-position rack, handle with extreme care, no vibration or shaking",
            "D2": "MFI sample vial rack — clean glass or plastic vials for MFI analysis",
            "D3": "HPLC-grade water reservoir — 0.1 um filtered, minimum 50 mL for priming and washing",
            "D4": "Tip box 1000 uL low-protein-binding — certified low-particle tips",
            "D5": "Empty — reserved",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — ProteinSimple MFI 5200 or HIAC 9703+",
            "D8": "Empty — reserved",
            "D9": "Waste container — tip discard and purge waste"
        },
        "instruments_needed": ["ProteinSimple MFI 5200 (or HIAC 9703+)", "Pipette 200-1000 uL"],
        "consumables": ["HPLC-grade water 0.1 um filtered", "MFI sample vials", "Tips 1000 uL low-protein-binding"],
        "reagents": ["HPLC-grade water filtered through 0.1 um membrane"],
        "throughput": "8 samples per hour",
        "duration_minutes": 10,
        "sample_volume_uL": 1000,
        "detection": "Flow imaging microscopy — digital morphology analysis",
        "regulatory": ["USP 787 Subvisible Particulate Matter in Therapeutic Protein Injections", "USP 788 Particulate Matter in Injections", "Ph. Eur. 2.9.19"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "particles_10um": "<= 6000 per container",
            "particles_25um": "<= 600 per container",
            "system_suitability_background": "< 25 particles/mL at >= 10 um",
            "pass_condition": "Particle counts at 10 um <= 6000 and at 25 um <= 600 per container (USP 787), system suitability background below limit",
            "fail_action": "FLAG — if particle counts exceed specification, flag for investigation by formulation team; if system suitability fails, ABORT and clean instrument; if counts are borderline, re-test with fresh sample aliquot"
        },
        "troubleshooting": [
            {"failure": "System suitability fails — high background particle count", "diagnosis": "Flow cell contaminated, water supply not properly filtered, or tubing shedding particles", "action": "Run 10 purge cycles with fresh 0.1 um filtered water, inspect flow cell for scratches, replace tubing if > 6 months old"},
            {"failure": "Air bubbles detected in sample — false particle counts", "diagnosis": "Sample was shaken or vortexed, dispensing created bubbles, or sample contains surfactant causing foam", "action": "Re-prepare sample by gentle inversion only, dispense against vial wall, allow bubbles to dissipate 5 minutes before loading"},
            {"failure": "Very high particle count in formulated drug product", "diagnosis": "Real aggregation or particulate issue, silicone oil from syringe, or foreign particles from fill process", "action": "Use MFI morphology to distinguish protein aggregates (irregular, translucent) from silicone oil (circular, smooth) — report both with characterisation"},
            {"failure": "Particle counts vary widely between replicates of same sample", "diagnosis": "Particles settling in sample vial, inhomogeneous mixing, or bubbles in some replicates", "action": "Mix sample by gentle inversion immediately before each measurement, use same time delay between mixing and measurement for all replicates"},
            {"failure": "Flow cell blockage — instrument shows flow error", "diagnosis": "Large particle or aggregate blocking the flow cell channel", "action": "Run reverse flush with filtered water, if blockage persists disassemble flow cell for cleaning per manufacturer instructions, do not force flow"}
        ],
        "notes": "USP 787 applies to therapeutic protein injectables (< 100 mL containers). USP 788 applies to all injectables. MFI provides morphological characterisation (aspect ratio, transparency) that light obscuration cannot. Silicone oil droplets from prefilled syringes are identifiable by MFI."
    },

    # ── CHARGE AND PURITY ANALYSIS ────────────────────────────────────────

    {
        "assay_id": "BIO_013",
        "name": "IEX-HPLC charge variant analysis (CEX)",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Bispecific antibodies", "Fc-fusion proteins"],
        "purpose": "Resolve and quantify acidic species, main peak, and basic species in mAb drug substance — critical CQA for glycosylation and deamidation",
        "robot_steps": [
            "Verify deck layout: confirm sample rack at D1, desalting spin column rack at D2, HPLC vial rack at D3, acetate buffer reservoir at D4, 200 uL tip box at D5, waste at D9",
            "Confirm ambient temperature 20-25 degrees C — log room temperature, column compartment must be at 25C",
            "Pick up 200 uL tip from D5 — if tip pickup fails, retry once then pause and alert operator",
            "If sample buffer is not acetate pH 5.0: prepare sample by buffer exchange using desalting spin column from D2 — load 100 uL sample, centrifuge at instrument interface D8, collect exchanged sample",
            "Verify sample concentration — if not 1-2 mg/mL, dilute with acetate buffer pH 5.0 from D4 to target 1.5 mg/mL",
            "Aspirate 100 uL of buffer-exchanged sample at 60 uL/sec from desalting column eluate",
            "Dispense into HPLC vial at D3 position A1 at 40 uL/sec — avoid bubbles",
            "Log trigger: record sample ID, buffer exchange status, final concentration, vial position, timestamp",
            "Cap vial and place in HPLC autosampler at instrument interface D7",
            "Inject 20 uL onto CEX column (ProPac WCX-10 or MAbPac SCX-10) at column temperature 25C",
            "Run gradient: buffer A = 20 mM MES pH 5.6, buffer B = 20 mM MES pH 5.6 + 500 mM NaCl — 0 to 40% B over 60 minutes at 1 mL/min",
            "Detect at UV 280 nm — monitor baseline stability",
            "After run, verify system suitability: reference standard main peak retention time within +/- 2 minutes of expected",
            "Integrate chromatogram: acidic species (all peaks pre-main), main peak, basic species (all peaks post-main) — use consistent integration parameters",
            "Report relative peak areas as percentage of total: acidic %, main peak %, basic %",
            "Log trigger: record sample ID, main peak %, acidic %, basic %, retention times, run date, column ID and usage count",
            "Discard tip to waste at D9 — advance to next sample",
            "After final sample, run 2 column volumes of 100% buffer B for column cleaning, then re-equilibrate with buffer A"
        ],
        "robot_deck_layout": {
            "D1": "Sample rack — 24-position tube rack with samples for charge variant analysis",
            "D2": "Desalting spin column rack — pre-equilibrated Zeba or PD SpinTrap columns in acetate pH 5.0",
            "D3": "HPLC vial rack — 24-position rack for 1.5 mL HPLC vials",
            "D4": "Reagent reservoir — acetate buffer pH 5.0 for sample dilution, minimum 10 mL",
            "D5": "Tip box 200 uL — full box 96 tips",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — HPLC autosampler and CEX column compartment at 25C",
            "D8": "Microcentrifuge — for desalting spin columns",
            "D9": "Waste container — tip discard, spin column waste"
        },
        "instruments_needed": ["HPLC with binary gradient pump", "CEX column ProPac WCX-10 or MAbPac SCX-10", "UV detector 280 nm", "Desalting spin columns if needed", "Pipette 20-200 uL"],
        "consumables": ["HPLC vials", "Vial caps", "Tips 200 uL"],
        "reagents": ["20 mM MES buffer pH 5.6 (buffer A)", "20 mM MES pH 5.6 + 500 mM NaCl (buffer B)", "Acetate buffer pH 5.0 for dilution"],
        "throughput": "8 samples per 8 hours (60 min run time each)",
        "duration_minutes": 15,
        "sample_volume_uL": 100,
        "detection": "UV 280 nm",
        "regulatory": ["ICH Q6B", "ICH Q2(R2)"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "main_peak": ">= 70% (product-specific, establish from development batches)",
            "acidic_species": "<= 25% (product-specific)",
            "basic_species": "<= 15% (product-specific)",
            "system_suitability_RT": "Reference standard main peak RT within +/- 2 minutes of expected",
            "pass_condition": "Main peak, acidic, and basic species within product-specific ranges established during development; system suitability retention time within tolerance",
            "fail_action": "FLAG — if charge variant profile differs significantly from reference, flag for investigation; if system suitability fails, ABORT and troubleshoot column/buffer system before re-running"
        },
        "troubleshooting": [
            {"failure": "Poor resolution between acidic and main peak — peaks merge", "diagnosis": "Column degradation, gradient too steep, or column temperature not controlled", "action": "Extend gradient to 90 minutes, verify column compartment at exactly 25C, replace column if plate count below specification"},
            {"failure": "Retention time shift for all peaks", "diagnosis": "Buffer pH changed, ionic strength incorrect, or column contamination", "action": "Check buffer pH with calibrated meter, prepare fresh buffers, run blank gradient to check baseline"},
            {"failure": "Extra peaks not seen in reference standard", "diagnosis": "Sample degradation (deamidation, oxidation), or contaminant co-eluting", "action": "Check sample storage conditions, compare to freshly thawed reference standard, investigate peak identity by fraction collection"},
            {"failure": "Very low signal despite loading 1-2 mg/mL", "diagnosis": "Buffer exchange failed and sample eluted during desalting, or detector lamp weak", "action": "Check buffer exchange recovery by A280, verify UV lamp energy, increase injection volume to 40 uL if needed"},
            {"failure": "Baseline drift during gradient", "diagnosis": "Buffers not properly prepared, degassing incomplete, or column bleed", "action": "Re-prepare buffers with accurate pH adjustment, degas by sonication 15 min, check column usage log"}
        ],
        "notes": "Charge variant profile is product-specific — establish reference ranges from development batches. Temperature control of column at 25C improves reproducibility. Report acidic and basic species to 1 decimal place."
    },

    {
        "assay_id": "BIO_014",
        "name": "SDS-PAGE gel preparation and loading",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "ADCs", "Bispecific antibodies"],
        "purpose": "Assess molecular weight, purity, and chain identity under reducing and non-reducing conditions",
        "robot_steps": [
            "Verify deck layout: confirm sample rack at D1, gel loading station at D2 (NuPAGE cassette and buffer tank), sample buffer and reducing agent at D3, MW marker at D4, 2-20 uL gel loading tip box at D5, heat block at D6 (set to 70C), waste at D9",
            "Confirm heat block at D6 is at 70 degrees C — verify with independent thermometer, log temperature",
            "Confirm gel electrophoresis tank at D2 has MES or MOPS SDS running buffer — verify buffer level covers electrode wires",
            "Pick up 2-20 uL gel loading tips from D5 — narrow tips required for gel well loading",
            "Prepare reducing sample: in PCR tube rack at D3, add sample + LDS sample buffer + 10x reducing agent (DTT or BME) — target 0.5-1 mg/mL protein in final mix",
            "Prepare non-reducing sample: in separate PCR tube, add sample + LDS sample buffer without reducing agent — same target concentration",
            "Log trigger: record sample IDs, reducing/non-reducing designation, concentration, buffer lot numbers",
            "Transfer reducing sample tubes to heat block at D6 — heat at 70 degrees C for exactly 10 minutes — start timer",
            "After 10 minutes, remove from heat block — cool to room temperature 20-25C for 5 minutes",
            "Non-reducing samples: do NOT heat — keep at room temperature throughout",
            "Remove comb from NuPAGE gel cassette at D2 — rinse wells 3 times with running buffer using multichannel",
            "Pick up gel loading tip from D5 — aspirate 5 uL MW marker (Novex Sharp Pre-Stained) from D4 at 5 uL/sec",
            "Load 5 uL MW marker into lane 1 of gel at D2 — dispense at 3 uL/sec, steady hand, insert tip to bottom of well",
            "Load 10-15 uL of each sample into subsequent gel wells using gel loading tips at 3 uL/sec — change tip between each sample, load reducing and non-reducing in adjacent lanes",
            "Load 5 uL MW marker into last lane — log all lane assignments",
            "Log trigger: record gel ID, lane map (which sample in which lane), volumes loaded, timestamp",
            "Connect power supply — run gel at 200 V constant for 35 minutes in MES or MOPS SDS running buffer at room temperature",
            "After run: remove gel from cassette — fix in 40% methanol / 10% acetic acid at D3 for 30 minutes",
            "Stain with Coomassie SimplyBlue or InstantBlue from D3 for 1 hour at room temperature on rocker",
            "Destain with purified water until background is clear — change water 2-3 times",
            "Image gel using gel documentation system at instrument interface D7 — capture image with consistent exposure",
            "Log trigger: record gel image filename, sample IDs, MW marker lane positions, expected and observed band sizes, band purity by densitometry if applicable, date"
        ],
        "robot_deck_layout": {
            "D1": "Sample rack — 24-position tube rack with protein samples",
            "D2": "Gel loading station — NuPAGE gel cassette in electrophoresis tank with running buffer",
            "D3": "Reagent station — LDS sample buffer, reducing agent (DTT/BME), fixing solution, staining solution, destain water",
            "D4": "MW marker station — Novex Sharp Pre-Stained protein standard",
            "D5": "Tip box 2-20 uL gel loading tips — narrow bore tips for gel wells",
            "D6": "Heat block — set to 70C for reducing sample preparation",
            "D7": "Instrument interface — gel documentation imaging system",
            "D8": "Power supply — 200V constant voltage",
            "D9": "Waste container — tip discard, used gel cassettes, fixing solution waste"
        },
        "instruments_needed": ["NuPAGE or Novex gel electrophoresis system (Invitrogen)", "Power supply 200V", "Heat block 70C", "Gel documentation imaging system", "Pipette 2-20 uL with gel loading tips"],
        "consumables": ["4-12% Bis-Tris NuPAGE gel", "MES or MOPS SDS running buffer", "LDS sample buffer", "DTT or BME reducing agent", "MW marker", "Gel stain (SimplyBlue or InstantBlue)", "Methanol, acetic acid for fixing"],
        "reagents": ["NuPAGE LDS sample buffer", "NuPAGE reducing agent", "NuPAGE MES SDS running buffer", "SimplyBlue SafeStain or InstantBlue"],
        "throughput": "1 gel per hour — 10-12 samples per gel",
        "duration_minutes": 120,
        "sample_volume_uL": 15,
        "detection": "Coomassie staining — visual and densitometry",
        "regulatory": ["ICH Q6B", "ICH Q2(R2)"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "reduced_mAb_HC": "Band at 50 kDa +/- 5 kDa (heavy chain)",
            "reduced_mAb_LC": "Band at 25 kDa +/- 3 kDa (light chain)",
            "non_reduced_intact": "Band at 150 kDa +/- 10 kDa (intact IgG)",
            "purity_by_densitometry": ">= 95% main bands (product-specific)",
            "pass_condition": "Expected bands at correct molecular weights, no unexpected bands > 1% by densitometry, and MW marker bands resolve clearly",
            "fail_action": "FLAG — if unexpected bands detected, flag for identity investigation by Western blot or mass spec; if bands at wrong MW, PAUSE and verify sample identity; if gel fails to run properly, ABORT and repeat with fresh gel"
        },
        "troubleshooting": [
            {"failure": "Gel does not run — no current flow", "diagnosis": "Buffer not added, electrodes not connected, or gel cassette not seated properly", "action": "Check buffer level covers electrodes, verify cassette is clicked in, confirm power supply is connected and set to 200V"},
            {"failure": "Bands are smeared or diffuse", "diagnosis": "Sample overloaded, sample not fully denatured, or gel run too fast (high voltage)", "action": "Reduce sample load to 5 uL, ensure reducing samples heated at 70C for full 10 minutes, verify voltage at 200V not higher"},
            {"failure": "No bands visible after staining", "diagnosis": "Sample concentration too low, staining solution exhausted, or gel fixed too long", "action": "Increase sample load, use fresh staining solution, fix for no more than 30 minutes"},
            {"failure": "MW marker did not resolve — bands compressed", "diagnosis": "Wrong running buffer (MES vs MOPS), gel percentage inappropriate, or gel expired", "action": "Verify correct buffer for gel type (MES for low MW, MOPS for high MW), check gel expiry date, use fresh gel"},
            {"failure": "Extra bands in non-reducing lane that are not in reducing", "diagnosis": "Incomplete disulfide bond formation, product variants, or aggregates that dissociate under reducing conditions", "action": "This may be expected for some products — compare to reference standard, investigate by CE-SDS if new bands appear"}
        ],
        "notes": "Run both reduced and non-reduced samples. Reduced mAb should show HC at 50 kDa and LC at 25 kDa. Non-reduced intact at 150 kDa. ADCs may show DAR-related smearing under non-reducing conditions."
    },

    # ── PROCESS MONITORING ────────────────────────────────────────────────

    {
        "assay_id": "BIO_015",
        "name": "Metabolite offline analysis (glucose, lactate, glutamine, ammonia)",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "Vaccines", "Cell and Gene Therapy"],
        "purpose": "Measure key metabolites in bioreactor culture to monitor cell health, nutrient status, and feed strategy",
        "robot_steps": [
            "Verify deck layout: confirm 2 mL collection tube rack at D1, 1.5 mL tube rack at D2, instrument sample cups at D3, 1000 uL tip box at D4, QC control rack at D5, waste at D9",
            "Confirm BioProfile FLEX2 or YSI 2950 at instrument interface D7 is powered on and warmed up — verify daily calibration passed",
            "Confirm ambient temperature 20-25 degrees C — metabolite readings are temperature-compensated but sample should be at RT",
            "Pick up 1000 uL tip from D4 — if tip pickup fails, retry once then pause",
            "Collect 2 mL sample from bioreactor sample port at instrument interface D7 into collection tube at D1 position A1 — aspirate at 200 uL/sec",
            "Log trigger: record batch code, sample time, day of run, bioreactor ID, collection tube position",
            "Transfer collection tube to centrifuge at D8 — centrifuge at 300 x g for 5 minutes to remove cells",
            "After centrifuge, pick up fresh 1000 uL tip from D4 — aspirate 1 mL of clarified supernatant at 150 uL/sec from top of tube, avoid cell pellet",
            "Dispense 1 mL into a clean microcentrifuge tube at D2 at 100 uL/sec — this is the clarified sample for metabolite analysis",
            "Pick up fresh 1000 uL tip — aspirate 800 uL clarified supernatant from D2, dispense into instrument sample cup at D3",
            "Place sample cup into BioProfile FLEX2 or YSI 2950 carousel at instrument interface D7 — enter sample ID, batch code, and day of run",
            "Log trigger: record sample cup position, sample ID entered, timestamp",
            "Instrument automatically measures: glucose (g/L), lactate (g/L), glutamine (mM), glutamate (mM), ammonia (mM) — also pH, pO2, pCO2, osmolality if configured",
            "Wait for instrument to complete analysis (approximately 90 seconds) — verify no error codes on display",
            "Record all metabolite values from instrument display or software export — compare to previous timepoint",
            "Flag any value outside expected range for that batch day: glucose < 0.5 g/L (nutrient depletion), lactate > 4 g/L (metabolic stress), ammonia > 6 mM (toxic accumulation)",
            "Log trigger: record all metabolite values, sample time, batch code, day of run, instrument ID, QC status, any flags raised",
            "Discard tip and cup to waste at D9 — advance to next bioreactor sample"
        ],
        "robot_deck_layout": {
            "D1": "2 mL collection tube rack — 24-position for bioreactor sample collection",
            "D2": "1.5 mL microcentrifuge tube rack — 24-position for clarified supernatant",
            "D3": "Instrument sample cup rack — cups specific to BioProfile FLEX2 or YSI 2950",
            "D4": "Tip box 1000 uL — full box 96 tips",
            "D5": "QC control rack — high and low concentration QC control vials for daily verification",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — BioProfile FLEX2 or YSI 2950, and bioreactor sample port",
            "D8": "Microcentrifuge — for cell removal at 300 x g",
            "D9": "Waste container — tip and cup discard"
        },
        "instruments_needed": ["BioProfile FLEX2 (Nova Biomedical) or YSI 2950 (Xylem)", "Microcentrifuge", "Pipette 200-1000 uL"],
        "consumables": ["Instrument-specific sample cups", "2 mL collection tubes", "Tips 1000 uL"],
        "reagents": ["Instrument calibration standards (supplied with instrument)", "QC controls high and low concentration"],
        "throughput": "10 samples per hour",
        "duration_minutes": 5,
        "sample_volume_uL": 1000,
        "detection": "Electrochemical biosensors and optical sensors",
        "regulatory": ["ICH Q5E", "ICH Q6B process monitoring"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "glucose_normal_range": "1.0 - 6.0 g/L during fed-batch culture",
            "lactate_limit": "<= 4.0 g/L (metabolic stress indicator above this)",
            "ammonia_limit": "<= 5.0 mM (toxic above this level)",
            "glutamine_range": "0.5 - 4.0 mM",
            "QC_control_tolerance": "+/- 10% of assigned value",
            "pass_condition": "Metabolite values within normal ranges for culture day, and daily QC controls within +/- 10% of assigned values",
            "fail_action": "ALERT — if glucose < 0.5 g/L, alert process scientist for emergency feed; if lactate > 4 g/L or ammonia > 6 mM, alert for process review; if QC controls out of range, PAUSE and recalibrate instrument before continuing"
        },
        "troubleshooting": [
            {"failure": "QC control values outside +/- 10% tolerance", "diagnosis": "Instrument sensors drifting, calibration expired, or QC material degraded", "action": "Re-run daily calibration with fresh calibration pack, use fresh QC control aliquot, if still failing call instrument service"},
            {"failure": "Glucose reads zero but culture is actively growing", "diagnosis": "Sample may be from wrong bioreactor, cell pellet contaminating supernatant, or sensor depleted", "action": "Verify sample source bioreactor ID, re-centrifuge to ensure clear supernatant, check instrument sensor status"},
            {"failure": "Instrument displays error code or rejects sample", "diagnosis": "Sample cup not properly seated, insufficient sample volume, or air bubble in sample path", "action": "Re-seat sample cup ensuring proper orientation, verify minimum 500 uL sample, degas sample if foamy"},
            {"failure": "Ammonia reading unexpectedly high in early culture", "diagnosis": "Glutamine decomposition in media before use, or media stored too long at warm temperature", "action": "Check media preparation date and storage conditions, test fresh media-only sample for baseline ammonia"},
            {"failure": "All metabolite values identical to previous timepoint", "diagnosis": "Same sample cup re-read, instrument displayed previous result, or data entry error", "action": "Verify fresh sample was loaded, clear instrument memory, re-run with new sample cup"}
        ],
        "notes": "Critical process parameter monitoring — run at every sampling point. Normal CHO ranges: glucose 1-4 g/L, lactate < 3 g/L, ammonia < 5 mM, glutamine 0.5-4 mM. Values outside these ranges should trigger process review and may require feed adjustment."
    },

    {
        "assay_id": "BIO_016",
        "name": "Buffer preparation and sterile filtration",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Vaccines", "Recombinant proteins", "ADCs"],
        "purpose": "Prepare formulation buffers, wash buffers, and diluents to specification — sterile filter before use in GMP operations",
        "robot_steps": [
            "Verify deck layout: confirm analytical balance at D1, excipient containers at D2, mixing vessel at D3 (with magnetic stirrer), pH meter and conductivity meter at D4, NaOH/HCl adjustment solutions at D5, purified water supply at D6, 0.22 um filter assembly at D7, waste at D9",
            "Retrieve batch record and confirm target buffer composition, volume, pH, and conductivity specification",
            "Confirm ambient temperature 20-25 degrees C — log room temperature",
            "Calculate mass of each component per batch record for target volume — robot calculates based on batch record input",
            "Tare vessel on analytical balance at D1 (0.0001g readability) — weigh each excipient accurately from containers at D2",
            "Log trigger: record each excipient name, lot number, target weight, actual weight, balance ID, timestamp",
            "Add approximately 80% of target water volume from D6 to mixing vessel at D3 — monitor volume by weight",
            "Start magnetic stirrer at D3 — stir at 300 rpm",
            "Add each excipient in order specified in batch record from D2 — stir for 5 minutes between additions until dissolved",
            "Verify dissolution visually — solution should be clear, no particles or undissolved material",
            "Immerse pH electrode from D4 into solution at D3 — wait for stable reading at 20-25C",
            "Adjust pH to target using NaOH or HCl solutions from D5 — add in 0.1 mL increments near target, record volume added",
            "Log trigger: record pre-adjustment pH, NaOH/HCl lot numbers, volumes added, final pH",
            "Make up to final volume with purified water from D6 — mix for 10 minutes",
            "Measure pH and conductivity with meters at D4 — confirm both within specification before proceeding",
            "Log trigger: record final pH (to 0.01), conductivity (mS/cm), temperature, pass/fail vs specification",
            "Pre-rinse 0.22 um sterilising filter at D7 with 100 mL of same buffer to wet membrane and check integrity",
            "Filter entire batch through 0.22 um filter under positive pressure nitrogen at D7 — monitor filter pressure, if > 2 bar the filter may be clogged",
            "Collect filtered buffer in sterile container — measure pH and conductivity of filtered buffer, confirm unchanged from pre-filtration",
            "Log trigger: record pre-filter and post-filter pH and conductivity, filter lot number, integrity test result, container label details, expiry date"
        ],
        "robot_deck_layout": {
            "D1": "Analytical balance — calibrated, 0.0001g readability, tare capable",
            "D2": "Excipient containers — labelled with lot numbers, arranged in addition order per batch record",
            "D3": "Mixing vessel — glass or stainless steel with magnetic stir bar, capacity per batch size",
            "D4": "pH and conductivity meters — calibrated electrodes mounted for robotic immersion",
            "D5": "pH adjustment station — 1M and 0.1M NaOH, 1M and 0.1M HCl in dispensing bottles",
            "D6": "Purified water supply — WFI or purified water inlet with volume metering",
            "D7": "Sterile filtration assembly — 0.22 um Millipak or Durapore filter with pressure vessel and nitrogen supply",
            "D8": "Sterile container receiving station — for filtered buffer collection",
            "D9": "Waste container — rinse water, pH adjustment waste"
        },
        "instruments_needed": ["Analytical balance (0.0001g readability)", "pH meter calibrated", "Conductivity meter", "Peristaltic pump or pressure vessel for filtration", "Magnetic stirrer"],
        "consumables": ["0.22 um Millipak or Durapore sterilising filter", "Sterile storage containers", "pH electrode", "Conductivity cell"],
        "reagents": ["Excipients per buffer specification", "NaOH 1M and 0.1M for pH adjustment", "HCl 1M and 0.1M for pH adjustment", "WFI or purified water"],
        "throughput": "2-4 buffer batches per shift",
        "duration_minutes": 60,
        "sample_volume_uL": 0,
        "detection": "pH and conductivity measurement",
        "regulatory": ["ICH Q6B", "USP 1231 Water for Pharmaceutical Purposes", "21 CFR 211.94"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "pH_tolerance": "Target pH +/- 0.1 (product-specific)",
            "conductivity_tolerance": "Target conductivity +/- 10% (product-specific)",
            "post_filtration_pH_shift": "<= 0.05 pH units from pre-filtration",
            "filter_integrity": "Bubble point or pressure hold test must pass per filter manufacturer specification",
            "pass_condition": "pH and conductivity within specification both pre- and post-filtration, filter integrity passes, and all excipient weights within tolerance",
            "fail_action": "PAUSE — if pH outside specification after adjustment, add more NaOH/HCl in smaller increments; if conductivity out of range, investigate excipient weights; if filter integrity fails, ABORT and replace filter before re-filtering"
        },
        "troubleshooting": [
            {"failure": "pH will not reach target despite adding NaOH/HCl", "diagnosis": "Buffer capacity too high near target pH, wrong excipient weighed, or NaOH/HCl too dilute", "action": "Switch to more concentrated NaOH/HCl (1M instead of 0.1M), verify all excipients were added correctly per batch record"},
            {"failure": "Conductivity significantly different from specification", "diagnosis": "Excipient weighing error, wrong excipient used, or water volume incorrect", "action": "Review all balance printouts, confirm correct excipient identities, verify final volume is accurate"},
            {"failure": "Filter clogs during sterile filtration — pressure exceeds 2 bar", "diagnosis": "Undissolved particles in buffer, filter too small for batch volume, or buffer precipitating", "action": "Pre-filter through 0.45 um filter first, use larger filter area, check buffer for visible particles"},
            {"failure": "Post-filtration pH differs from pre-filtration by > 0.05", "diagnosis": "Filter membrane interacting with buffer, CO2 absorption during filtration, or temperature change", "action": "Pre-rinse filter with buffer before filtering batch, minimise air exposure during transfer, verify temperature is consistent"},
            {"failure": "Excipient does not dissolve — solution remains cloudy", "diagnosis": "Wrong excipient grade, concentration exceeds solubility, or mixing insufficient", "action": "Verify excipient grade matches specification, check solubility at target concentration, increase stirring time and speed, warm solution slightly if permitted by specification"}
        ],
        "notes": "Buffer specification must be approved before preparation. Record all weights, pH adjustments, and measurements on batch record in real time. All excipients must have approved CoA before use. Expiry date typically 30 days at 2-8C unless specified otherwise."
    },

    {
        "assay_id": "BIO_017",
        "name": "In-process pH and DO sampling from bioreactor",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "Vaccines", "Cell and Gene Therapy"],
        "purpose": "Collect discrete offline confirmation samples for bioreactor pH and dissolved oxygen to verify in-line probe accuracy during GMP runs",
        "robot_steps": [
            "Verify deck layout: confirm 10 mL syringe rack at D1, syringe cap station at D2, ice bucket at D3, pH calibration buffers at D4 (pH 7.00, 7.40), blood gas analyser cartridges at D5, waste at D9",
            "Confirm bioreactor sample port at instrument interface D7 is accessible and aseptic connection verified",
            "Prepare offline pH measurement station: calibrate pH meter at D4 with pH 7.00 and 7.40 buffers — record slope",
            "Confirm blood gas analyser (Radiometer ABL90 or equivalent) at instrument interface D8 is ready and cartridge loaded from D5",
            "Log trigger: record bioreactor ID, batch code, day of run, pH meter calibration slope, blood gas analyser cartridge lot, timestamp",
            "Open bioreactor sample port at D7 following aseptic technique — spray port with 70% ethanol, allow to dry",
            "Pick up pre-labelled 10 mL sampling syringe from D1 — connect to sample port",
            "Collect 5 mL sample (5000 uL) into syringe — draw slowly to avoid degassing, sample temperature will be at bioreactor temperature (typically 37C)",
            "Cap syringe immediately at cap station D2 — no air exposure for accurate pO2 measurement, this is critical",
            "If blood gas analyser at D8 is not immediately available, place capped syringe on ice at D3 — measure within 5 minutes maximum",
            "Immerse pH electrode from D4 into sample aliquot (minimum 2 mL) — wait for stable reading at sample temperature",
            "Record offline pH to 2 decimal places — note sample temperature at time of reading",
            "Load syringe into blood gas analyser at D8 — instrument aspirates approximately 200 uL for pO2 and pCO2 measurement",
            "Wait for blood gas analyser result (approximately 60 seconds) — record pO2 (mmHg), pCO2 (mmHg)",
            "Compare offline pH to bioreactor in-line probe reading — flag if difference > 0.05 pH units",
            "Compare offline pO2 to bioreactor in-line DO probe reading — flag if difference > 5%",
            "Log trigger: record offline pH, DO (pO2), pCO2, sample temperature, in-line probe readings, difference values, flag status, time, batch code, day of run",
            "Discard syringe to waste at D9 — clean sample port with 70% ethanol and recap"
        ],
        "robot_deck_layout": {
            "D1": "Syringe rack — pre-labelled 10 mL syringes for sample collection",
            "D2": "Syringe cap station — sterile caps for immediate sealing after collection",
            "D3": "Ice bucket — for holding syringe if blood gas analyser not immediately available",
            "D4": "pH calibration and measurement station — pH 7.00 and 7.40 buffers, calibrated pH meter",
            "D5": "Blood gas analyser cartridge storage — replacement cartridges",
            "D6": "Empty — reserved",
            "D7": "Instrument interface — bioreactor sample port with aseptic connector",
            "D8": "Instrument interface — blood gas analyser (Radiometer ABL90)",
            "D9": "Waste container — used syringes and caps"
        },
        "instruments_needed": ["Calibrated offline pH meter", "Blood gas analyser (Radiometer ABL90 or equivalent)", "10 mL sampling syringe"],
        "consumables": ["10 mL syringes", "Syringe caps", "pH calibration buffers", "Ice and ice bucket"],
        "reagents": ["pH 7.00 and 7.40 calibration buffers", "Blood gas analyser cartridges"],
        "throughput": "6 samples per hour",
        "duration_minutes": 10,
        "sample_volume_uL": 5000,
        "detection": "Potentiometric pH, electrochemical pO2",
        "regulatory": ["ICH Q6B process monitoring", "GMP 21 CFR 211.68 automatic mechanical equipment"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "pH_probe_correlation": "Offline pH within +/- 0.05 pH units of in-line probe",
            "DO_probe_correlation": "Offline pO2 within +/- 5% of in-line DO probe reading",
            "pH_calibration_slope": "95 - 105% for 2-point calibration",
            "measurement_time": "All readings completed within 5 minutes of sample collection",
            "pass_condition": "Offline-to-inline pH difference <= 0.05 units and DO difference <= 5%, measured within 5 minutes of sampling",
            "fail_action": "ALERT — if pH difference > 0.05, alert process engineer to investigate probe drift, recalibrate or replace in-line probe; if pH difference > 0.10, PAUSE bioreactor operations and escalate; if DO difference > 10%, flag probe for replacement at next opportunity"
        },
        "troubleshooting": [
            {"failure": "Offline pH consistently lower than in-line by > 0.05 units", "diagnosis": "In-line pH probe drifting high due to protein fouling, reference junction blockage, or calibration drift", "action": "Recalibrate in-line probe, clean probe junction if accessible, replace probe if calibration does not hold"},
            {"failure": "pO2 reading not obtained — blood gas analyser error", "diagnosis": "Air bubble introduced during sampling, cartridge expired, or sensor depleted", "action": "Re-sample with careful attention to avoid air exposure, replace cartridge, run quality control sample on analyser"},
            {"failure": "Sample temperature too low by time of measurement", "diagnosis": "Sample sat on ice too long, or delay between collection and measurement exceeded 5 minutes", "action": "Measure immediately after collection, record temperature and apply temperature correction if available on pH meter"},
            {"failure": "In-line DO probe reads 0% but cells are alive and growing", "diagnosis": "DO probe membrane damaged, probe disconnected, or calibration lost", "action": "Replace DO probe membrane, check probe cable connection, recalibrate with 2-point calibration (0% nitrogen, 100% air)"},
            {"failure": "Large variation between consecutive probe correlation samples", "diagnosis": "Sampling technique inconsistent, different sample port location, or bioreactor heterogeneous mixing", "action": "Standardise sampling technique and timing, always use same sample port, verify bioreactor agitation is adequate for homogeneous culture"}
        ],
        "notes": "Probe correlation samples should be taken at minimum twice per day during active culture. If in-line probe drifts more than 0.1 pH units from offline, recalibrate or replace probe. Document all comparisons and investigations in batch record."
    },

    {
        "assay_id": "BIO_018",
        "name": "Media preparation and sterility check",
        "field": "Biopharma / CDMO",
        "product_types": ["Monoclonal Antibodies", "Recombinant proteins", "Cell and Gene Therapy", "Vaccines"],
        "purpose": "Prepare and quality check cell culture media before use in bioreactor seeding — including sterility, pH, osmolality, and component verification",
        "robot_steps": [
            "Verify deck layout: confirm media base container at D1, supplement rack at D2 (L-glutamine, sodium bicarbonate, other additives), mixing vessel at D3, pH meter and osmometer at D4, 0.22 um filter assembly at D5, sterile containers at D6, sterility test tubes at D7, waste at D9",
            "Confirm biological safety cabinet is running for all aseptic operations — log BSC serial number and certification date",
            "Confirm ambient temperature 20-25 degrees C — log room temperature",
            "Retrieve powdered or liquid media base from cold storage at D1 — check expiry date and lot number before use",
            "Log trigger: record media base name, lot number, expiry date, storage temperature, timestamp",
            "For powdered media: add 80% of target WFI volume from water supply to mixing vessel at D3 — start magnetic stirrer",
            "Add powdered media slowly while stirring to avoid clumping — stir for 30 minutes until fully dissolved at room temperature",
            "Add supplements from D2 in specified order: L-glutamine (200 mM stock), sodium bicarbonate (7.5% stock), other additives per specification — record each lot number and volume added",
            "Add serum if required (FBS or serum-free for GMP processes) from D2 — calculate volume from percentage specification, add at room temperature",
            "Log trigger: record each supplement name, lot number, volume added, order of addition",
            "Adjust pH to 7.0-7.4 using NaOH from D2 or CO2 sparging — add in small increments, measure after each addition",
            "Make up to final volume with WFI — mix for additional 10 minutes",
            "Measure pH at D4 (target 7.0-7.4) — record to 2 decimal places at temperature 20-25C",
            "Measure osmolality at D4 (target 280-320 mOsm/kg) — run in triplicate, CV must be < 2%",
            "Observe colour — should be clear straw-coloured (phenol red indicator), any turbidity or unusual colour is grounds for rejection",
            "Log trigger: record pH, osmolality (mean and CV), colour observation, pass/fail pre-filtration",
            "Filter sterilise through 0.22 um filter at D5 into sterile vessel at D6 — monitor filter pressure",
            "Aseptically remove 10 mL sample from filtered media for sterility test — transfer to thioglycolate and TSB broth tubes at D7",
            "Incubate sterility tubes: thioglycolate at 30-35C and TSB at 20-25C for 14 days — inspect daily for turbidity",
            "Label media batch container with: name, lot, date, expiry, pH, osmolality, preparer, sterility test status",
            "Store at 2-8C until use — do not use if turbid or colour change observed",
            "Log trigger: record all specifications, measurements, component lot numbers, sterility test initiation date, storage location, expiry date"
        ],
        "robot_deck_layout": {
            "D1": "Media base container — powdered or liquid media from cold storage",
            "D2": "Supplement rack — L-glutamine 200 mM, sodium bicarbonate 7.5%, NaOH, other additives, FBS if required",
            "D3": "Mixing vessel — sterile glass or single-use bag with magnetic stir capability",
            "D4": "Measurement station — pH meter (calibrated) and osmometer (calibrated) with robotic electrode access",
            "D5": "Sterile filtration assembly — 0.22 um Millipak filter with pressure vessel",
            "D6": "Sterile container receiving station — sterile bags or bottles for filtered media",
            "D7": "Sterility test station — thioglycolate broth and TSB broth tubes",
            "D8": "Incubator interface — 30-35C and 20-25C incubators for sterility test",
            "D9": "Waste container — packaging waste, filter rinse waste"
        },
        "instruments_needed": ["Biological safety cabinet class II", "Osmometer", "pH meter", "0.22 um sterilising filter", "Peristaltic pump", "Analytical balance"],
        "consumables": ["0.22 um Millipak filter", "Sterile media storage bags or bottles", "TSB and thioglycolate broth tubes for sterility", "Labels"],
        "reagents": ["Cell culture media base (powder or liquid)", "L-Glutamine 200 mM", "Sodium bicarbonate 7.5%", "WFI or cell culture grade water", "NaOH for pH adjustment"],
        "throughput": "1-2 media batches per shift",
        "duration_minutes": 90,
        "sample_volume_uL": 0,
        "detection": "Visual, pH meter, osmometer",
        "regulatory": ["ICH Q6B", "USP 1085 Guidelines on Sterility Tests", "21 CFR 211"],
        "automation_difficulty": "complex",
        "acceptance_criteria": {
            "pH_range": "7.0 - 7.4",
            "osmolality_range": "280 - 320 mOsm/kg",
            "osmolality_CV": "<= 2% for triplicate readings",
            "appearance": "Clear, straw-coloured (with phenol red), no turbidity or particulates",
            "sterility_14day": "No turbidity in TSB or thioglycolate broth after 14-day incubation",
            "pass_condition": "pH 7.0-7.4, osmolality 280-320 mOsm/kg, clear straw-coloured appearance, and sterility test negative at 14 days",
            "fail_action": "ABORT — if pH outside 6.8-7.6 after adjustment, reject batch; if osmolality outside 260-340, reject batch; if turbid or unusual colour, reject immediately; if sterility test positive at any point, ALERT QA, quarantine batch, and discard all media from that lot"
        },
        "troubleshooting": [
            {"failure": "Media remains turbid after extended mixing", "diagnosis": "Powder clumped during addition, expired media, or water quality issue", "action": "Extend mixing to 60 minutes, check media expiry and storage conditions, verify WFI quality by conductivity test, filter through 0.45 um pre-filter before sterile filtration"},
            {"failure": "pH will not reach 7.0 despite NaOH addition", "diagnosis": "Bicarbonate missing or insufficient, media powder degraded, or wrong media formulation", "action": "Verify sodium bicarbonate was added at correct volume, check media powder lot against certificate of analysis, contact manufacturer if suspect"},
            {"failure": "Osmolality outside 280-320 range", "diagnosis": "Component volumes incorrect, water volume wrong, or supplement concentrations off", "action": "Review all additions against batch record, verify supplement stock concentrations, recalculate expected osmolality from components"},
            {"failure": "Sterility test positive — turbidity in broth tubes before 14 days", "diagnosis": "Contamination during preparation, filter integrity failed, or non-sterile container", "action": "Quarantine entire media lot, investigate contamination source (BSC settle plates, filter integrity test, container sterility), re-prepare with new materials"},
            {"failure": "Filter pressure exceeds 2 bar during sterile filtration", "diagnosis": "Undissolved particles blocking filter, media volume too large for filter size, or filter defective", "action": "Pre-filter through 5 um filter, use larger filter surface area, replace filter if defective"}
        ],
        "notes": "Media lot numbers must be recorded in batch record for full traceability. Sterility result available at 14 days — for early bioreactor seeding, use media with satisfactory appearance, pH, and osmolality and release retrospectively. Any visible turbidity is a rejection criterion."
    },

]


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_all_assays():
    return BIOPHARMA_ASSAYS


def get_assay_by_id(assay_id):
    for a in BIOPHARMA_ASSAYS:
        if a["assay_id"] == assay_id:
            return a
    return None


def get_assays_by_product(product_type):
    return [a for a in BIOPHARMA_ASSAYS if product_type in a.get("product_types", [])]


def get_assays_by_difficulty(difficulty):
    return [a for a in BIOPHARMA_ASSAYS if a.get("automation_difficulty") == difficulty]


def get_robot_instructions(assay_id):
    assay = get_assay_by_id(assay_id)
    if not assay:
        return None
    lines = [
        f"ASSAY: {assay['name']}",
        f"ID: {assay['assay_id']}",
        f"FIELD: {assay['field']}",
        f"DURATION: {assay['duration_minutes']} minutes",
        f"THROUGHPUT: {assay['throughput']}",
        f"DIFFICULTY: {assay['automation_difficulty'].upper()}",
        "",
        "INSTRUMENTS REQUIRED:",
    ]
    for inst in assay["instruments_needed"]:
        lines.append(f"  - {inst}")
    lines.append("")
    lines.append("CONSUMABLES:")
    for c in assay["consumables"]:
        lines.append(f"  - {c}")
    lines.append("")
    lines.append("ROBOT STEP INSTRUCTIONS:")
    for i, step in enumerate(assay["robot_steps"], 1):
        lines.append(f"  {i}. {step}")
    lines.append("")
    lines.append(f"REGULATORY: {', '.join(assay['regulatory'])}")
    if assay.get("notes"):
        lines.append(f"\nNOTES: {assay['notes']}")
    return "\n".join(lines)


def export_field_summary():
    print(f"\n{'='*80}")
    print(f"  BIOPHARMA / CDMO ASSAY LIBRARY -- Rail System")
    print(f"  Total assays: {len(BIOPHARMA_ASSAYS)}")
    print(f"{'='*80}\n")
    easy = get_assays_by_difficulty("easy")
    medium = get_assays_by_difficulty("medium")
    complex_ = get_assays_by_difficulty("complex")
    print(f"  Easy automation:    {len(easy)} assays")
    print(f"  Medium automation:  {len(medium)} assays")
    print(f"  Complex automation: {len(complex_)} assays")
    print(f"\n{'-'*80}")
    for a in BIOPHARMA_ASSAYS:
        diff_label = {"easy": "EASY  ", "medium": "MEDIUM", "complex": "COMPLEX"}[a["automation_difficulty"]]
        print(f"  {a['assay_id']}  [{diff_label}]  {a['name']}")
        print(f"           Throughput: {a['throughput']} | Duration: {a['duration_minutes']} min | Sample: {a['sample_volume_uL']} uL")
        print(f"           Regulatory: {', '.join(a['regulatory'])}")
        print()


if __name__ == "__main__":
    export_field_summary()
    print("\nSample robot instructions for BIO_001:")
    print("-" * 60)
    print(get_robot_instructions("BIO_001"))
