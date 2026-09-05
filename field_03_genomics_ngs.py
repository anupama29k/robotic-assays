# field_03_genomics_ngs.py
# BioInterface — Field 3: Genomics / NGS Library Preparation
# 8 assays covering an end-to-end Illumina-style DNA library prep workflow
# Optimized for Opentrons OT-2 with thermocycler + magnetic + heater-shaker modules

GENOMICS_ASSAYS = [
    # ─────────────────────────────────────────────────────────────
    # NGS_001 — End repair + A-tailing
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_001",
        "name": "End repair and A-tailing (NEBNext Ultra II)",
        "field": "Genomics / NGS",
        "product_types": ["Fragmented DNA", "WGS libraries", "Exome libraries", "Amplicon libraries"],
        "purpose": "Polish fragmented DNA ends and add 3' A-overhangs in preparation for adapter ligation, using NEBNext Ultra II chemistry on an Opentrons OT-2.",
        "robot_steps": [
            "Confirm thermocycler module on OT-2 deck S7 is at 4C and lid open.",
            "Pick up 200 uL tips from S1 (opentrons_96_tiprack_200ul).",
            "Aspirate 50 uL fragmented DNA sample from input plate at S2 (column 1).",
            "Dispense into 96-well PCR plate at S7 thermocycler module, column 1.",
            "Add 7 uL End Prep enzyme mix from reservoir reagent A (S3 well A1).",
            "Add 3 uL End Prep reaction buffer from S3 well A2.",
            "Mix by 10 cycles of pipette aspirate/dispense; final volume 60 uL per well.",
            "Close thermocycler lid; run programme: 20C 30 min, 65C 30 min, 4C hold.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm thermocycler reached temperature setpoints within +/-1C and reaction held at 4C upon completion.",
            "Open thermocycler lid; transfer plate to magnetic module at S6 (gripper-equipped) or analyst-mediated transfer (OT-2 base).",
            "Log thermocycler run completion timestamp; flag if any temperature deviation > 2C during incubation.",
            "Discard tips to trash at S12.",
            "Export end-prep reaction completion record to run file with reagent lot numbers.",
            "Park OT-2 pipettor at home position; flag thermocycler block for cleaning if next run uses different reagent set.",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_200ul (filtered, low retention)",
            "S2": "Sample input plate -- nest_96_wellplate_200ul_flat (fragmented DNA, 50 uL/well)",
            "S3": "Reagent reservoir -- nest_12_reservoir_15ml (End Prep enzyme + buffer)",
            "S7": "Thermocycler module gen2 -- holds reaction plate during incubation",
            "S12": "Trash -- fixed waste",
        },
        "workbench_id": "WB-NGS1",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Thermocycler module gen2", "Multichannel P200 pipettor"],
        "consumables": ["Filtered 200 uL tips", "96-well PCR plate", "12-channel reagent reservoir"],
        "reagents": ["NEBNext Ultra II End Prep enzyme mix", "NEBNext Ultra II End Prep reaction buffer", "Nuclease-free water"],
        "throughput_samples_per_run": 96,
        "throughput_notes": "96 samples per run; ~75 min including 60 min thermocycle",
        "robot_active_minutes": 12,
        "total_assay_duration_hours": 1.25,
        "sample_volume_uL": 50,
        "detection": "None (enzymatic prep step)",
        "regulatory": ["CAP/CLIA when used clinically", "ENCODE library construction guidelines"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "thermocycler_temperature_accuracy": "+/-1C of setpoint",
            "reaction_volume_accuracy": "60 +/-3 uL per well after combine",
            "tip_consumable_count": "1 tip per sample (no carryover)",
        },
        "environment_requirement": "Standard lab bench (BSL-1 / BSL-2 for clinical samples)",
        "platform_compatibility": "Opentrons OT-2 with thermocycler module; ~30 min setup time per run",
        "notes": "End repair and A-tailing are combined in NEBNext Ultra II to reduce hands-on time. Fragmented DNA input range: 50 ng - 1 ug. For inputs < 100 ng, consider switching to KAPA HyperPrep with bead-based purification before this step.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "Opentrons OT-2 uses 8-channel + single-channel pipettors, not Hamilton AutoMATE 96. Volume range covered by OT-2 P200 multichannel for all liquid handling steps.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S2", "S3", "S7"],
            "analyst": ["S12"]
        },
        "autonomy_level": 2,
        "autonomy_level_reason": "Easy automation with all liquid handling on OT-2; analyst reviews thermocycler temperature log and confirms reaction completion before proceeding to ligation.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "incubate", "instrument": "thermocycler", "description": "Confirm thermocycler at 4C, lid open", "parameters": {"temperature_C": 4}, "duration_seconds": 30},
            {"step_number": 2, "step_type": "dispense", "instrument": "liquid_handler", "description": "Pick up 200 uL tips from S1", "parameters": {}, "duration_seconds": 10},
            {"step_number": 3, "step_type": "aspirate", "instrument": "liquid_handler", "description": "Aspirate 50 uL fragmented DNA from S2 column 1", "parameters": {"volume_uL": 50}, "duration_seconds": 30},
            {"step_number": 4, "step_type": "dispense", "instrument": "liquid_handler", "description": "Dispense to thermocycler S7 column 1", "parameters": {"volume_uL": 50}, "duration_seconds": 30},
            {"step_number": 5, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 7 uL End Prep enzyme mix from S3 A1", "parameters": {"volume_uL": 7}, "duration_seconds": 30},
            {"step_number": 6, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 3 uL End Prep buffer from S3 A2", "parameters": {"volume_uL": 3}, "duration_seconds": 30},
            {"step_number": 7, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 10 cycles aspirate/dispense", "parameters": {"cycles": 10}, "duration_seconds": 60},
            {"step_number": 8, "step_type": "thermocycle", "instrument": "thermocycler", "description": "Programme: 20C 30 min, 65C 30 min, 4C hold", "parameters": {"temperature_C": 65, "duration_minutes": 60}, "duration_seconds": 3600},
            {"step_number": 9, "step_type": "analyst", "instrument": "analyst", "description": "Confirm thermocycler temperature setpoints reached and held", "parameters": {}, "duration_seconds": 60},
            {"step_number": 10, "step_type": "transport", "instrument": "analyst", "description": "Transfer reaction plate from thermocycler to magnetic module", "parameters": {"source_instrument": "thermocycler", "destination_instrument": "magnetic_separator"}, "duration_seconds": 30},
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # NGS_002 — Adapter ligation
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_002",
        "name": "Adapter ligation with unique dual indexes (UDI)",
        "field": "Genomics / NGS",
        "product_types": ["End-repaired DNA", "Indexed libraries", "Multiplexed libraries"],
        "purpose": "Ligate Illumina TruSeq-compatible adapters with unique dual indexes onto end-prepped, A-tailed DNA fragments using NEBNext Ultra II ligation master mix.",
        "robot_steps": [
            "Pre-cool thermocycler at S7 to 20C; confirm setpoint reached.",
            "Aspirate 30 uL NEBNext Ultra II Ligation Master Mix from S3 reservoir well B1; add to each sample well in plate at S7.",
            "Aspirate 1 uL Ligation Enhancer from S3 well B2; add to each sample well.",
            "From UDI adapter plate at S5 (96-format), transfer 2.5 uL of unique adapter per sample using single-channel P20.",
            "Total reaction volume now 93.5 uL per well.",
            "Mix by 10 cycles aspirate/dispense at slow flow rate (avoid foam).",
            "Close thermocycler lid; run programme: 20C 15 min, hold at 4C.",
            "[ANALYST STEP -- robot pauses and alerts]: Verify all 96 wells received adapter (visual check under transilluminator if dye-tracked); flag any missed wells before proceeding to cleanup.",
            "Add 3 uL USER enzyme to each well (only required if using NEBNext Methylated Adapter for methylation studies); skip otherwise.",
            "Mix and incubate 15 min at 37C if USER added.",
            "Park pipettor at home; record adapter plate ID and indexing scheme to run file.",
            "Mark plate for immediate transition to AMPure XP cleanup (NGS_003) -- ligation products are unstable to repeated freeze-thaw.",
            "Discard adapter plate to designated index-tracking storage at -20C.",
            "Export ligation reaction record with adapter lot, master mix lot, and well-to-index mapping.",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_200ul",
            "S2": "Sample plate -- end-prepped DNA from NGS_001 (60 uL/well)",
            "S3": "Reagent reservoir -- nest_12_reservoir_15ml (Ligation master mix B1, Enhancer B2, optional USER B3)",
            "S4": "Tip rack -- opentrons_96_tiprack_20ul (for adapter transfer)",
            "S5": "UDI adapter plate -- 96-well unique dual index plate (2.5 uL/well)",
            "S7": "Thermocycler module gen2",
            "S12": "Trash",
        },
        "workbench_id": "WB-NGS1",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Thermocycler module gen2", "Multichannel P200", "Single-channel P20"],
        "consumables": ["Filtered 200 uL tips", "Filtered 20 uL tips", "96-well PCR plate", "UDI adapter plate"],
        "reagents": ["NEBNext Ultra II Ligation Master Mix", "Ligation Enhancer", "UDI adapter plate (Illumina TruSeq-compatible)", "Optional: USER enzyme for methylation"],
        "throughput_samples_per_run": 96,
        "throughput_notes": "96 samples per run; ~30 min including 15 min thermocycle",
        "robot_active_minutes": 18,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 60,
        "detection": "None (enzymatic ligation)",
        "regulatory": ["ENCODE library construction guidelines", "Illumina library prep best practices"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "adapter_well_coverage": "100% of 96 wells received adapter (no skipped wells)",
            "ligation_temperature": "20C +/- 1C for 15 min minimum",
            "udi_index_traceability": "Plate position to index mapping logged for downstream demultiplexing",
        },
        "environment_requirement": "Standard lab bench; BSL-2 for clinical samples",
        "platform_compatibility": "Opentrons OT-2 with thermocycler; benefits from heater-shaker module for gentle mixing",
        "notes": "UDI plate position must be logged accurately -- mis-mapping breaks downstream demultiplexing. Use barcoded UDI plates from Illumina or NEB; never reuse adapter plates between runs to avoid index hopping. For low-input libraries (< 50 ng), increase ligation time to 30 min.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "OT-2 uses multichannel P200 + single-channel P20; no AutoMATE 96 head selection needed.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S2", "S3", "S4", "S5", "S7"],
            "analyst": ["S12"]
        },
        "autonomy_level": 2,
        "autonomy_level_reason": "Easy automation; analyst verifies adapter well coverage before cleanup to catch any missed wells that would invalidate downstream demultiplexing.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "incubate", "instrument": "thermocycler", "description": "Pre-cool thermocycler to 20C", "parameters": {"temperature_C": 20}, "duration_seconds": 60},
            {"step_number": 2, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 30 uL Ligation Master Mix", "parameters": {"volume_uL": 30}, "duration_seconds": 30},
            {"step_number": 3, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 1 uL Ligation Enhancer", "parameters": {"volume_uL": 1}, "duration_seconds": 30},
            {"step_number": 4, "step_type": "transfer", "instrument": "liquid_handler", "description": "Transfer 2.5 uL UDI adapter from S5 to each sample", "parameters": {"volume_uL": 2.5}, "duration_seconds": 120},
            {"step_number": 5, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 10 cycles slow flow", "parameters": {"cycles": 10}, "duration_seconds": 60},
            {"step_number": 6, "step_type": "thermocycle", "instrument": "thermocycler", "description": "Ligation: 20C 15 min, 4C hold", "parameters": {"temperature_C": 20, "duration_minutes": 15}, "duration_seconds": 900},
            {"step_number": 7, "step_type": "analyst", "instrument": "analyst", "description": "Verify all 96 wells received adapter", "parameters": {}, "duration_seconds": 60},
            {"step_number": 8, "step_type": "incubate", "instrument": "incubator", "description": "Optional USER enzyme step (37C 15 min)", "parameters": {"temperature_C": 37, "duration_minutes": 15}, "duration_seconds": 900},
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # NGS_003 — Post-ligation AMPure XP cleanup
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_003",
        "name": "AMPure XP bead cleanup (post-ligation)",
        "field": "Genomics / NGS",
        "product_types": ["Adapter-ligated libraries", "Size-selected libraries"],
        "purpose": "SPRI-bead cleanup of adapter-ligated libraries to remove excess adapters, adapter dimers, and small fragments using AMPure XP magnetic beads at 0.9x sample volume.",
        "robot_steps": [
            "Verify magnetic module at S6 is engaged-able and bead reservoir at S3 is mixed (auto-shake on heater-shaker S4 for 30 sec at 1500 rpm if available).",
            "Aspirate 84 uL AMPure XP beads (0.9x sample volume of 93.5 uL ligation reaction) from S3 well A1.",
            "Dispense beads into ligation plate at S6 magnetic module; mix by 10 cycles aspirate/dispense at slow flow.",
            "Disengage magnet; incubate at room temperature 5 minutes (off-magnet bead binding).",
            "Engage magnetic module; wait 5 minutes for bead pellet to form against side wall.",
            "Aspirate and discard supernatant (~177 uL per well) to trash at S12.",
            "While magnet still engaged, add 200 uL freshly prepared 80% ethanol from S3 well A2.",
            "Wait 30 seconds; aspirate and discard ethanol.",
            "Repeat ethanol wash: add 200 uL 80% ethanol; wait 30 sec; aspirate and discard.",
            "[ANALYST STEP -- robot pauses and alerts]: Inspect wells for residual ethanol droplets; if visible, allow additional 60 sec air-dry before elution.",
            "Air-dry beads on magnet for 5 minutes; flag if cracking visible (over-drying reduces yield).",
            "Disengage magnet; resuspend bead pellet in 22 uL nuclease-free water from S3 well A3.",
            "Mix by 15 cycles aspirate/dispense; incubate off-magnet 2 minutes.",
            "Engage magnet; wait 2 minutes for clarification.",
            "Transfer 20 uL eluate to fresh 96-well plate at S5; this is the cleaned-up library.",
            "Discard tips; record bead lot number and ethanol preparation timestamp.",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_200ul",
            "S3": "Reagent reservoir -- nest_12_reservoir_15ml (AMPure XP beads A1, 80% ethanol A2, NF-water A3)",
            "S4": "Heater-shaker module gen1 -- optional bead resuspension",
            "S5": "Output plate -- nest_96_wellplate_200ul_flat (cleaned library, 20 uL/well)",
            "S6": "Magnetic module gen2 -- bead capture during cleanup",
            "S12": "Trash",
        },
        "workbench_id": "WB-NGS1",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Magnetic module gen2", "Heater-shaker module (optional)", "Multichannel P200"],
        "consumables": ["Filtered 200 uL tips", "96-well PCR plate (input)", "96-well storage plate (output)"],
        "reagents": ["AMPure XP beads (Beckman A63881)", "Freshly prepared 80% ethanol (must be < 1 hour old)", "Nuclease-free water"],
        "throughput_samples_per_run": 96,
        "throughput_notes": "96 samples per run; ~25 min total including bead binding and ethanol washes",
        "robot_active_minutes": 16,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 93.5,
        "detection": "None (purification step)",
        "regulatory": ["ENCODE NGS library construction guidelines"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "bead_to_sample_ratio": "0.9x (84 uL beads to 93.5 uL ligation reaction)",
            "ethanol_freshness": "80% ethanol prepared within 1 hour of use",
            "pellet_drying": "5 min air-dry on magnet; no visible droplets, no cracking",
            "elution_volume_recovery": ">= 19 uL recovered from 22 uL elution input",
        },
        "environment_requirement": "Standard lab bench",
        "platform_compatibility": "Opentrons OT-2 with magnetic module gen2 mandatory; heater-shaker improves bead resuspension",
        "notes": "Bead-to-sample ratio is the most critical parameter -- 0.9x retains fragments above ~150 bp while removing adapter dimers (~125 bp) and free adapters. Lower ratio (0.7x) selects for larger inserts; higher ratio (1.0x+) retains more small fragments. Always use freshly diluted 80% ethanol -- older preparations contain water that strips beads.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "OT-2 multichannel P200 handles all volumes (84 uL beads, 200 uL ethanol washes, 22 uL elution).",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S3", "S4", "S5", "S6"],
            "analyst": ["S12"]
        },
        "autonomy_level": 3,
        "autonomy_level_reason": "Medium difficulty multi-step purification with magnetic separation cycles; robot reads bead pellet visually-assisted, analyst confirms drying state to prevent over/under-drying that affects yield.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "shake", "instrument": "shaker", "description": "Resuspend bead reservoir at 1500 rpm 30 sec", "parameters": {"rpm": 1500, "duration_seconds": 30}, "duration_seconds": 30},
            {"step_number": 2, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 84 uL AMPure XP beads (0.9x ratio)", "parameters": {"volume_uL": 84}, "duration_seconds": 60},
            {"step_number": 3, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 10 cycles slow flow", "parameters": {"cycles": 10}, "duration_seconds": 60},
            {"step_number": 4, "step_type": "incubate", "instrument": "incubator", "description": "Off-magnet bead binding 5 min", "parameters": {"duration_minutes": 5}, "duration_seconds": 300},
            {"step_number": 5, "step_type": "magnetic_separation", "instrument": "magnetic_separator", "description": "Engage magnet; wait 5 min for pellet", "parameters": {"duration_seconds": 300}, "duration_seconds": 300},
            {"step_number": 6, "step_type": "aspirate", "instrument": "liquid_handler", "description": "Aspirate supernatant to trash", "parameters": {"volume_uL": 177}, "duration_seconds": 60},
            {"step_number": 7, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 200 uL 80% ethanol wash 1", "parameters": {"volume_uL": 200}, "duration_seconds": 60},
            {"step_number": 8, "step_type": "aspirate", "instrument": "liquid_handler", "description": "Aspirate ethanol wash 1", "parameters": {"volume_uL": 200}, "duration_seconds": 60},
            {"step_number": 9, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 200 uL 80% ethanol wash 2", "parameters": {"volume_uL": 200}, "duration_seconds": 60},
            {"step_number": 10, "step_type": "aspirate", "instrument": "liquid_handler", "description": "Aspirate ethanol wash 2", "parameters": {"volume_uL": 200}, "duration_seconds": 60},
            {"step_number": 11, "step_type": "analyst", "instrument": "analyst", "description": "Inspect for residual ethanol droplets", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": "incubate", "instrument": "incubator", "description": "Air-dry on magnet 5 min", "parameters": {"duration_minutes": 5}, "duration_seconds": 300},
            {"step_number": 13, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 22 uL nuclease-free water for elution", "parameters": {"volume_uL": 22}, "duration_seconds": 30},
            {"step_number": 14, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 15 cycles to resuspend beads", "parameters": {"cycles": 15}, "duration_seconds": 90},
            {"step_number": 15, "step_type": "magnetic_separation", "instrument": "magnetic_separator", "description": "Engage magnet 2 min for clarification", "parameters": {"duration_seconds": 120}, "duration_seconds": 120},
            {"step_number": 16, "step_type": "transfer", "instrument": "liquid_handler", "description": "Transfer 20 uL eluate to S5 output plate", "parameters": {"volume_uL": 20}, "duration_seconds": 60},
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # NGS_004 — PCR library enrichment
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_004",
        "name": "PCR library enrichment (KAPA HiFi)",
        "field": "Genomics / NGS",
        "product_types": ["Adapter-ligated libraries", "Indexed libraries", "Enriched libraries"],
        "purpose": "Amplify adapter-ligated libraries using minimal cycle PCR with KAPA HiFi to add full P5/P7 sequencing primer sites and enrich library yield without introducing PCR duplicates.",
        "robot_steps": [
            "Pre-cool thermocycler S7 to 4C; confirm setpoint.",
            "Aspirate 25 uL KAPA HiFi 2x master mix from S3 well A1; dispense to PCR plate at S7.",
            "Aspirate 5 uL KAPA Library Amp Primer Mix from S3 well A2; add to each well.",
            "Add 20 uL cleaned-up library from S5 (NGS_003 output).",
            "Total reaction volume now 50 uL per well.",
            "Mix by 8 cycles aspirate/dispense; close thermocycler lid.",
            "Run programme: 98C 45 sec initial denaturation; 8 cycles of (98C 15 sec / 60C 30 sec / 72C 30 sec); 72C 1 min final extension; 4C hold.",
            "Cycle count is critical -- 8 cycles for 100-500 ng input; 10 cycles for 50-100 ng; 12 cycles for 10-50 ng. Verify input quantification before this step.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm cycle count matches library input quantification and that lid temperature is 105C throughout to prevent condensation.",
            "Open thermocycler lid after 4C hold; transfer enriched library plate to magnetic module S6 for cleanup.",
            "Park pipettor; record cycle count and master mix lot to run file.",
            "Flag any wells where reaction volume appears < 45 uL (possible evaporation through cracked seal).",
            "Discard tips; alert operator to proceed with NGS_005 (post-PCR cleanup) within 1 hour to minimize PCR product degradation.",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_200ul",
            "S3": "Reagent reservoir -- nest_12_reservoir_15ml (KAPA 2x master mix A1, primer mix A2)",
            "S5": "Cleaned library plate -- input from NGS_003",
            "S7": "Thermocycler module gen2",
            "S12": "Trash",
        },
        "workbench_id": "WB-NGS1",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Thermocycler module gen2", "Multichannel P200"],
        "consumables": ["Filtered 200 uL tips", "96-well PCR plate (skirted)"],
        "reagents": ["KAPA HiFi HotStart Ready Mix 2x", "KAPA Library Amplification Primer Mix"],
        "throughput_samples_per_run": 96,
        "throughput_notes": "96 samples per run; ~25 min total including 12 min PCR programme",
        "robot_active_minutes": 8,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 20,
        "detection": "None (amplification step)",
        "regulatory": ["ENCODE NGS guidelines", "GA4GH library prep standards"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "cycle_count_match_input": "Cycle count matches library input ng range per protocol",
            "thermocycler_lid_temp": "105C throughout to prevent condensation",
            "post_pcr_volume": ">= 45 uL recovered (no significant evaporation)",
        },
        "environment_requirement": "Standard lab bench; BSL-2 for clinical",
        "platform_compatibility": "Opentrons OT-2 with thermocycler; mandatory heated lid (105C) to prevent condensation",
        "notes": "PCR cycle count is the dominant quality lever -- too few cycles yields insufficient library; too many cycles introduces duplicates and bias. Always titrate cycle count empirically for new sample types. KAPA HiFi has lower bias than NEB Q5 for high-GC genomes.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "OT-2 multichannel P200 handles 25 uL master mix, 5 uL primer, 20 uL library transfers.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S3", "S5", "S7"],
            "analyst": ["S12"]
        },
        "autonomy_level": 2,
        "autonomy_level_reason": "Easy automation; analyst confirms cycle count selection matches library input range to avoid over-amplification artifacts.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "incubate", "instrument": "thermocycler", "description": "Pre-cool thermocycler to 4C", "parameters": {"temperature_C": 4}, "duration_seconds": 30},
            {"step_number": 2, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 25 uL KAPA HiFi 2x master mix", "parameters": {"volume_uL": 25}, "duration_seconds": 30},
            {"step_number": 3, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 5 uL primer mix", "parameters": {"volume_uL": 5}, "duration_seconds": 30},
            {"step_number": 4, "step_type": "transfer", "instrument": "liquid_handler", "description": "Transfer 20 uL cleaned library from S5", "parameters": {"volume_uL": 20}, "duration_seconds": 60},
            {"step_number": 5, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 8 cycles aspirate/dispense", "parameters": {"cycles": 8}, "duration_seconds": 60},
            {"step_number": 6, "step_type": "thermocycle", "instrument": "thermocycler", "description": "98C 45s initial; 8 cycles (98C 15s, 60C 30s, 72C 30s); 72C 1min", "parameters": {"temperature_C": 98, "duration_minutes": 12}, "duration_seconds": 720},
            {"step_number": 7, "step_type": "analyst", "instrument": "analyst", "description": "Verify cycle count and lid temperature", "parameters": {}, "duration_seconds": 30},
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # NGS_005 — Post-PCR AMPure XP cleanup
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_005",
        "name": "AMPure XP bead cleanup (post-PCR)",
        "field": "Genomics / NGS",
        "product_types": ["PCR-enriched libraries", "Final libraries"],
        "purpose": "Remove primers, primer dimers, and PCR byproducts from enriched libraries using 1.0x AMPure XP bead cleanup to deliver sequencing-ready libraries.",
        "robot_steps": [
            "Resuspend AMPure XP beads at S3 well A1 by heater-shaker (S4) at 1500 rpm 30 sec.",
            "Aspirate 50 uL AMPure XP beads (1.0x sample volume of 50 uL PCR reaction) from S3 well A1.",
            "Dispense beads into PCR-enriched plate at S6 magnetic module; mix by 10 cycles aspirate/dispense slow flow.",
            "Disengage magnet; incubate room temperature 5 minutes for off-magnet binding.",
            "Engage magnet; wait 5 minutes for pellet formation.",
            "Aspirate and discard supernatant (~100 uL per well) to trash.",
            "On magnet, add 200 uL freshly prepared 80% ethanol from S3 well A2; wait 30 sec; aspirate.",
            "Repeat ethanol wash second time: add 200 uL 80% ethanol; wait 30 sec; aspirate.",
            "[ANALYST STEP -- robot pauses and alerts]: Visual check for residual ethanol; allow 60 sec extra dry if droplets visible.",
            "Air-dry beads on magnet 4 minutes (do not over-dry; cracking reduces yield > 30%).",
            "Disengage magnet; add 22 uL 10 mM Tris pH 8.0 from S3 well A3 for elution.",
            "Mix 15 cycles aspirate/dispense; incubate 2 min off-magnet.",
            "Engage magnet 2 min; transfer 20 uL eluate to fresh storage plate at S5.",
            "This is the final cleaned library; ready for quantification (NGS_006).",
            "Discard tips; record bead lot, ethanol prep time, and elution buffer details.",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_200ul",
            "S3": "Reagent reservoir -- nest_12_reservoir_15ml (AMPure XP A1, 80% ethanol A2, 10 mM Tris pH 8.0 A3)",
            "S4": "Heater-shaker module -- bead resuspension",
            "S5": "Output plate -- final library (20 uL/well)",
            "S6": "Magnetic module gen2",
            "S12": "Trash",
        },
        "workbench_id": "WB-NGS1",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Magnetic module gen2", "Heater-shaker module", "Multichannel P200"],
        "consumables": ["Filtered 200 uL tips", "96-well PCR plate (input)", "96-well storage plate (output)"],
        "reagents": ["AMPure XP beads", "Freshly prepared 80% ethanol", "10 mM Tris pH 8.0 elution buffer"],
        "throughput_samples_per_run": 96,
        "throughput_notes": "96 samples per run; ~25 min including bead binding and washes",
        "robot_active_minutes": 16,
        "total_assay_duration_hours": 0.5,
        "sample_volume_uL": 50,
        "detection": "None (purification)",
        "regulatory": ["ENCODE NGS library prep standards"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "bead_ratio": "1.0x (50 uL beads to 50 uL PCR product)",
            "elution_buffer": "10 mM Tris pH 8.0 (NOT water -- pH 8 stabilizes library)",
            "drying_time": "4 min max; no cracking",
            "fragment_size_distribution_bp": "250-500",
            "library_concentration_ng_per_uL": ">5",
        },
        "environment_requirement": "Standard lab bench",
        "platform_compatibility": "Opentrons OT-2 with magnetic module + heater-shaker",
        "notes": "1.0x cleanup retains all post-PCR products including main library peak (~300-500 bp typical) and any dimer artifacts. For aggressive dimer removal, follow with second cleanup at 0.8x. Always elute in Tris pH 8.0 -- water-eluted libraries lose ~5-10% per freeze-thaw cycle. TapeStation D1000/HS-D1000 QC after this step is recommended; library_concentration_ng_per_uL and fragment_size_distribution_bp acceptance criteria expect inputs from that QC.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "OT-2 multichannel P200 covers all volumes.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S3", "S4", "S5", "S6"],
            "analyst": ["S12"]
        },
        "autonomy_level": 3,
        "autonomy_level_reason": "Medium difficulty bead cleanup with magnetic cycles and timed drying; analyst flags drying state to prevent yield loss.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "shake", "instrument": "shaker", "description": "Resuspend AMPure beads 1500 rpm 30s", "parameters": {"rpm": 1500, "duration_seconds": 30}, "duration_seconds": 30},
            {"step_number": 2, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 50 uL AMPure XP beads 1.0x ratio", "parameters": {"volume_uL": 50}, "duration_seconds": 30},
            {"step_number": 3, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 10 cycles", "parameters": {"cycles": 10}, "duration_seconds": 60},
            {"step_number": 4, "step_type": "incubate", "instrument": "incubator", "description": "Off-magnet bind 5 min", "parameters": {"duration_minutes": 5}, "duration_seconds": 300},
            {"step_number": 5, "step_type": "magnetic_separation", "instrument": "magnetic_separator", "description": "Engage magnet 5 min", "parameters": {"duration_seconds": 300}, "duration_seconds": 300},
            {"step_number": 6, "step_type": "aspirate", "instrument": "liquid_handler", "description": "Discard supernatant", "parameters": {"volume_uL": 100}, "duration_seconds": 30},
            {"step_number": 7, "step_type": "dispense", "instrument": "liquid_handler", "description": "Ethanol wash 1: 200 uL", "parameters": {"volume_uL": 200}, "duration_seconds": 30},
            {"step_number": 8, "step_type": "aspirate", "instrument": "liquid_handler", "description": "Aspirate wash 1", "parameters": {"volume_uL": 200}, "duration_seconds": 30},
            {"step_number": 9, "step_type": "dispense", "instrument": "liquid_handler", "description": "Ethanol wash 2: 200 uL", "parameters": {"volume_uL": 200}, "duration_seconds": 30},
            {"step_number": 10, "step_type": "aspirate", "instrument": "liquid_handler", "description": "Aspirate wash 2", "parameters": {"volume_uL": 200}, "duration_seconds": 30},
            {"step_number": 11, "step_type": "analyst", "instrument": "analyst", "description": "Inspect for residual ethanol", "parameters": {}, "duration_seconds": 30},
            {"step_number": 12, "step_type": "incubate", "instrument": "incubator", "description": "Air-dry 4 min", "parameters": {"duration_minutes": 4}, "duration_seconds": 240},
            {"step_number": 13, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 22 uL Tris pH 8.0", "parameters": {"volume_uL": 22}, "duration_seconds": 30},
            {"step_number": 14, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 15 cycles", "parameters": {"cycles": 15}, "duration_seconds": 90},
            {"step_number": 15, "step_type": "magnetic_separation", "instrument": "magnetic_separator", "description": "Engage magnet 2 min", "parameters": {"duration_seconds": 120}, "duration_seconds": 120},
            {"step_number": 16, "step_type": "transfer", "instrument": "liquid_handler", "description": "Transfer 20 uL final library to S5", "parameters": {"volume_uL": 20}, "duration_seconds": 60},
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # NGS_006 — Qubit fluorometric quantification
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_006",
        "name": "Qubit dsDNA HS fluorometric quantification",
        "field": "Genomics / NGS",
        "product_types": ["Final libraries", "Quantified libraries"],
        "purpose": "Measure dsDNA concentration of NGS libraries using Invitrogen Qubit 4 fluorometer with dsDNA HS assay; values feed normalization (NGS_007).",
        "robot_steps": [
            "Prepare Qubit working solution: 1 uL HS reagent per 199 uL HS buffer (sufficient for n+2 reactions).",
            "From S3 reservoir, aspirate 199 uL Qubit dsDNA HS buffer per Qubit tube.",
            "Add 1 uL HS reagent per tube; mix briefly (Opentrons in-tube mix limited).",
            "Add 10 uL of standard 1 (0 ng/uL) and standard 2 (10 ng/uL) from S5 standards rack to dedicated tubes.",
            "Add 2 uL of each library sample from S2 to its dedicated Qubit tube.",
            "Total volume per tube: 200 uL working solution + 1-10 uL sample = ~202-210 uL.",
            "Mix each tube by 5 cycles aspirate/dispense; incubate 2 min at room temperature in S6.",
            "[ANALYST STEP -- robot pauses and alerts]: Robot signals operator to manually transfer Qubit tube rack to Qubit 4 fluorometer (no API integration; user reads each tube manually).",
            "Operator performs Qubit calibration with standards 1 and 2; saves calibration to instrument.",
            "Operator reads each library tube; selects 'sample volume = 2 uL' on instrument; records ng/uL.",
            "[ANALYST STEP -- robot pauses and alerts]: Operator enters concentration values into BioInterface run file or uploads CSV from Qubit instrument.",
            "Validate readings: any sample with concentration < 1 ng/uL flag for re-prep; > 50 ng/uL flag for dilution before pooling.",
            "Calculate molarity assuming average library size 350 bp: nM = (ng/uL) × 1000 / (350 × 660).",
            "Export quantification table with sample IDs, concentrations, calculated molarity to run file.",
            "Tubes can be re-read multiple times within 3 hours; discard after.",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_20ul",
            "S2": "Library plate -- final libraries from NGS_005 (96 samples)",
            "S3": "Reagent reservoir -- nest_12_reservoir_15ml (Qubit HS reagent A1, HS buffer A2)",
            "S5": "Standards rack -- 0 ng/uL std A1, 10 ng/uL std A2",
            "S6": "Qubit tube rack -- 96 Qubit assay tubes (analyst-transferred to Qubit 4 instrument after prep)",
            "S12": "Trash",
        },
        "workbench_id": "WB-NGS2",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Single-channel P20", "Qubit 4 fluorometer (manual)"],
        "consumables": ["Qubit assay tubes (Invitrogen)", "Filtered 20 uL tips"],
        "reagents": ["Qubit dsDNA HS reagent", "Qubit dsDNA HS buffer", "Qubit dsDNA HS standards (0 + 10 ng/uL)"],
        "throughput_samples_per_run": 96,
        "throughput_notes": "96 samples per OT-2 prep; Qubit reads ~1 sample per 5 sec on Qubit 4 = ~10 min hands-on read time",
        "robot_active_minutes": 25,
        "total_assay_duration_hours": 0.6,
        "sample_volume_uL": 2,
        "detection": "Fluorescence (Qubit dsDNA HS dye binding)",
        "regulatory": ["Illumina library QC requirements", "Internal QC SOP"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "standards_passing": "0 ng/uL std reads < 0.1 ng/uL; 10 ng/uL std reads 8-12 ng/uL",
            "concentration_range": "0.5 - 50 ng/uL acceptable for downstream pooling",
            "duplicate_cv": "< 5% across replicate reads",
        },
        "environment_requirement": "Standard lab bench; Qubit instrument access required",
        "platform_compatibility": "OT-2 prep + manual Qubit read; full automation requires Qubit Flex or alternate fluorometer with API",
        "notes": "Qubit 4 doesn't have a Python API for OT-2 integration -- analyst transfers tubes and reads manually. For high-throughput labs, switch to fluorescent plate reader (e.g. PicoGreen on FLUOstar) which can be fully automated. Bioanalyzer/TapeStation provide both concentration AND size info but require separate runs.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "Tube-format prep; OT-2 P20 single-channel handles per-sample pipetting. Qubit read is analyst-only.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S2", "S3", "S5", "S6"],
            "analyst": ["S12"]
        },
        "autonomy_level": 2,
        "autonomy_level_reason": "Mixed automation -- OT-2 handles tube prep, but Qubit instrument has no API so analyst reads each tube manually and enters values. Robot reads Qubit standards but cannot drive the Qubit 4 itself.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 199 uL Qubit HS buffer per tube", "parameters": {"volume_uL": 199}, "duration_seconds": 60},
            {"step_number": 2, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 1 uL HS reagent per tube", "parameters": {"volume_uL": 1}, "duration_seconds": 60},
            {"step_number": 3, "step_type": "transfer", "instrument": "liquid_handler", "description": "Add 10 uL standards to 2 tubes", "parameters": {"volume_uL": 10}, "duration_seconds": 30},
            {"step_number": 4, "step_type": "transfer", "instrument": "liquid_handler", "description": "Add 2 uL of each sample to library tubes", "parameters": {"volume_uL": 2}, "duration_seconds": 240},
            {"step_number": 5, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 5 cycles per tube", "parameters": {"cycles": 5}, "duration_seconds": 90},
            {"step_number": 6, "step_type": "incubate", "instrument": "incubator", "description": "Room temp 2 min", "parameters": {"duration_minutes": 2}, "duration_seconds": 120},
            {"step_number": 7, "step_type": "transport", "instrument": "analyst", "description": "Transfer Qubit tube rack to Qubit 4 fluorometer", "parameters": {"source_instrument": "liquid_handler", "destination_instrument": "fluorometer"}, "duration_seconds": 60},
            {"step_number": 8, "step_type": "read", "instrument": "fluorometer", "description": "Calibrate with standards; read each tube", "parameters": {"read_type": "fluorescence"}, "duration_seconds": 600},
            {"step_number": 9, "step_type": "analyst", "instrument": "analyst", "description": "Enter concentrations into run file or upload Qubit CSV", "parameters": {}, "duration_seconds": 120},
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # NGS_007 — Library normalization and pooling
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_007",
        "name": "Library normalization and equimolar pooling",
        "field": "Genomics / NGS",
        "product_types": ["Quantified libraries", "Pooled libraries", "Sequencing-ready pools"],
        "purpose": "Normalize each library to a common molar concentration (typically 4 nM) and combine into an equimolar pool for sequencing run loading.",
        "robot_steps": [
            "Load library quantification CSV from NGS_006 into run file; calculate normalization volumes.",
            "Target normalization: each library at 4 nM in 30 uL final volume per well in normalization plate at S5.",
            "Calculate water volume per library: V_water = 30 - V_library (where V_library = (30 × 4) / library_nM).",
            "Aspirate calculated water volume from S3 reservoir well A1 into normalization plate.",
            "Aspirate calculated library volume from each source well at S2 into corresponding normalization well.",
            "[ANALYST STEP -- robot pauses and alerts]: Verify normalization volumes calculated correctly; flag any library requiring < 1 uL transfer (resolution limit).",
            "For high-concentration libraries (> 20 nM), perform 1:5 pre-dilution to achieve accurate aliquoting.",
            "Mix normalized libraries 5 cycles aspirate/dispense at slow flow.",
            "From normalization plate at S5, transfer 5 uL of each normalized library into pool tube at S6 well A1 (single tube; multichannel sequential dispenses).",
            "Total pool volume: 5 uL × N libraries (e.g. 96 × 5 = 480 uL).",
            "Mix pool by 10 cycles aspirate/dispense.",
            "Quantify pool concentration (should be 4 nM if normalization was accurate); aliquot 100 uL into S6 well A2 for storage.",
            "[ANALYST STEP -- robot pauses and alerts]: Optional QC re-read of pool by Qubit to confirm 4 nM target +/- 10%.",
            "Export pooling table: sample ID, calculated normalization volumes, pool composition with index sequences.",
            "Pool is now ready for denaturation and sequencer loading (NGS_008).",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_20ul (for small-volume library transfers)",
            "S2": "Quantified library plate -- input from NGS_005 with concentrations from NGS_006",
            "S3": "Reagent reservoir -- nest_12_reservoir_15ml (10 mM Tris pH 8.0 dilution buffer)",
            "S5": "Normalization plate -- nest_96_wellplate_200ul_flat (4 nM normalized libraries, 30 uL/well)",
            "S6": "Pool tube rack -- 1.5 mL tube for combined pool (well A1) + storage aliquot (A2)",
            "S12": "Trash",
        },
        "workbench_id": "WB-NGS2",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Single-channel P20", "Multichannel P200"],
        "consumables": ["Filtered 20 uL tips", "Filtered 200 uL tips", "96-well plate (normalization)", "1.5 mL Eppendorf tubes (pool)"],
        "reagents": ["10 mM Tris pH 8.0 (dilution buffer)"],
        "throughput_samples_per_run": 96,
        "throughput_notes": "96 libraries pooled per run; ~30 min total",
        "robot_active_minutes": 22,
        "total_assay_duration_hours": 0.6,
        "sample_volume_uL": 5,
        "detection": "None (normalization step; QC by Qubit if performed)",
        "regulatory": ["Illumina sequencing input requirements", "ENCODE pooling guidelines"],
        "automation_difficulty": "medium",
        "acceptance_criteria": {
            "normalization_target": "4 nM +/- 10% per well after normalization",
            "minimum_transfer_volume": ">= 1 uL (resolution limit; pre-dilute if needed)",
            "pool_concentration": "Pool concentration within 10% of theoretical 4 nM",
            "index_uniqueness": "All UDI indexes in pool unique (no collisions)",
        },
        "environment_requirement": "Standard lab bench",
        "platform_compatibility": "OT-2 multichannel + single-channel handles wide volume range",
        "notes": "Normalization accuracy directly affects per-sample read depth uniformity. Libraries deviating > 20% from target nM cause read count imbalance > 2-fold across the pool. For high-throughput labs, consider Echo acoustic dispenser for nanoliter-level normalization accuracy.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "OT-2 P20 single-channel for sub-uL transfers; P200 multichannel for water dispenses.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S2", "S3", "S5", "S6"],
            "analyst": ["S12"]
        },
        "autonomy_level": 3,
        "autonomy_level_reason": "Medium difficulty calculation-driven step; robot computes per-library volumes from quantification data, analyst confirms calculation correctness for samples requiring sub-uL transfers.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "analyst", "instrument": "analyst", "description": "Load Qubit CSV; calculate normalization volumes", "parameters": {}, "duration_seconds": 120},
            {"step_number": 2, "step_type": "dispense", "instrument": "liquid_handler", "description": "Aspirate per-library water from reservoir", "parameters": {}, "duration_seconds": 240},
            {"step_number": 3, "step_type": "transfer", "instrument": "liquid_handler", "description": "Transfer per-library volumes to normalization plate", "parameters": {}, "duration_seconds": 360},
            {"step_number": 4, "step_type": "analyst", "instrument": "analyst", "description": "Verify normalization volumes; flag sub-uL transfers", "parameters": {}, "duration_seconds": 60},
            {"step_number": 5, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix normalized libraries 5 cycles", "parameters": {"cycles": 5}, "duration_seconds": 60},
            {"step_number": 6, "step_type": "transfer", "instrument": "liquid_handler", "description": "Pool 5 uL of each library into S6 A1", "parameters": {"volume_uL": 5}, "duration_seconds": 480},
            {"step_number": 7, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix pool 10 cycles", "parameters": {"cycles": 10}, "duration_seconds": 90},
            {"step_number": 8, "step_type": "transfer", "instrument": "liquid_handler", "description": "Aliquot 100 uL pool to storage tube", "parameters": {"volume_uL": 100}, "duration_seconds": 60},
            {"step_number": 9, "step_type": "analyst", "instrument": "analyst", "description": "Optional Qubit QC re-read of pool", "parameters": {}, "duration_seconds": 300},
        ]
    },

    # ─────────────────────────────────────────────────────────────
    # NGS_008 — Denaturation and dilution for sequencing
    # ─────────────────────────────────────────────────────────────
    {
        "assay_id": "NGS_008",
        "name": "Library denaturation and dilution for MiSeq/NovaSeq loading",
        "field": "Genomics / NGS",
        "product_types": ["Pooled libraries", "Sequencing-ready loaded libraries"],
        "purpose": "Denature pooled library to single-stranded form using NaOH and dilute to instrument-specific loading concentration (typically 10-20 pM for MiSeq, 200-300 pM for NovaSeq).",
        "robot_steps": [
            "Verify pooled library at 4 nM from NGS_007 is at room temperature and quantification is current.",
            "Mix 5 uL pool with 5 uL freshly prepared 0.2 N NaOH in tube at S6 well A1.",
            "Mix by 10 cycles aspirate/dispense; incubate exactly 5 minutes at room temperature.",
            "[ANALYST STEP -- robot pauses and alerts]: Confirm 0.2 N NaOH is < 7 days old; older NaOH gives inconsistent denaturation.",
            "After 5 min denaturation, add 990 uL pre-chilled HT1 hybridization buffer from S3 well A1 (4C cold block).",
            "Mix 10 cycles; this gives 20 pM denatured library (5 uL × 4 nM × 1000 / 1000 uL).",
            "For MiSeq target loading at 10 pM: take 600 uL of 20 pM and add 600 uL HT1 = 10 pM × 1.2 mL.",
            "For NovaSeq 6000 target loading at 200 pM: take 100 uL of 4 nM pool, mix with 100 uL 0.2 N NaOH 5 min, then add 1.8 mL HT1 = 200 pM × 2 mL.",
            "Optional: spike-in PhiX control at 1% v/v from PhiX library prepared in parallel (typically 10 uL of 100 pM PhiX into 990 uL diluted pool).",
            "[ANALYST STEP -- robot pauses and alerts]: Operator transports denatured loading volume to sequencer cartridge; load within 30 minutes of denaturation (PhiX added after if not pre-mixed).",
            "Record: pool ID, NaOH lot, HT1 lot, final loading concentration, target instrument, PhiX spike percentage.",
            "Discarded denaturation tube + tips to trash; do not store denatured library (single-stranded form degrades rapidly).",
            "Export sequencing run sheet: sample sheet CSV, pool composition with indexes, loading concentration, instrument target.",
            "Operator initiates sequencing run on instrument with sample sheet linked back to BioInterface run file.",
        ],
        "robot_deck_layout": {
            "S1": "Tip rack -- opentrons_96_tiprack_20ul + opentrons_96_tiprack_1000ul",
            "S3": "Reagent reservoir + cold block -- nest_12_reservoir_15ml on opentrons_24_aluminumblock (HT1 buffer at 4C A1, 0.2 N NaOH A2, optional PhiX A3)",
            "S6": "Tube rack -- 1.5 mL pool tube A1, denaturation tube A2, final loading tube A3",
            "S12": "Trash",
        },
        "workbench_id": "WB-NGS2",
        "rail_handoff": None,
        "instruments_needed": ["Opentrons OT-2", "Single-channel P20", "Single-channel P1000", "Aluminum cold block (4C)"],
        "consumables": ["Filtered 20 uL tips", "Filtered 1000 uL tips", "1.5 mL Eppendorf tubes"],
        "reagents": ["Freshly prepared 0.2 N NaOH (< 7 days old)", "Illumina HT1 hybridization buffer (pre-chilled to 4C)", "Optional: PhiX control library at 100 pM"],
        "throughput_samples_per_run": 1,
        "throughput_notes": "1 pool denatured per run (one sequencer load); ~15 min including 5 min denaturation",
        "robot_active_minutes": 6,
        "total_assay_duration_hours": 0.3,
        "sample_volume_uL": 5,
        "detection": "None (denaturation step)",
        "regulatory": ["Illumina sequencer loading SOPs", "MiSeq/NovaSeq operating manuals"],
        "automation_difficulty": "easy",
        "acceptance_criteria": {
            "denaturation_time": "5 min +/- 30 sec at room temperature",
            "naoh_age": "0.2 N NaOH prepared within 7 days",
            "ht1_temperature": "HT1 buffer pre-chilled to 4C before addition",
            "load_within": "Sequencer load within 30 min of denaturation",
            "phix_spike": "1% PhiX standard for benchmarking",
        },
        "environment_requirement": "Standard lab bench; sequencer access required",
        "platform_compatibility": "OT-2 prep + manual sequencer load; full automation possible with NovaSeq integrated cluster generation",
        "notes": "Denatured library is single-stranded and unstable -- must load within 30 minutes or denature fresh. NaOH is the most common failure point; freshly prepared from 1 N stock is mandatory. Loading concentration directly affects cluster density on the flow cell; under-loaded gives low yield, over-loaded gives polyclonal clusters and poor base quality.",
        "automate_96_steps": [],
        "automate_96_head": "not applicable",
        "automate_96_head_note": "Single-tube preparation; OT-2 P20 + P1000 single-channel for the small-volume mixing.",
        "automate_96_head_change": False,
        "instrument_assignment": {
            "rail_robot": [],
            "automate_96": ["S1", "S3", "S6"],
            "analyst": ["S12"]
        },
        "autonomy_level": 2,
        "autonomy_level_reason": "Easy automation in OT-2 but analyst-mediated transfer to sequencer instrument and final cartridge loading; robot prepares precise dilution series, analyst loads and starts run.",
        "protocol_steps_v3": [
            {"step_number": 1, "step_type": "analyst", "instrument": "analyst", "description": "Verify pool at 4 nM and at room temperature", "parameters": {}, "duration_seconds": 60},
            {"step_number": 2, "step_type": "transfer", "instrument": "liquid_handler", "description": "Mix 5 uL pool with 5 uL 0.2 N NaOH", "parameters": {"volume_uL": 5}, "duration_seconds": 60},
            {"step_number": 3, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 10 cycles", "parameters": {"cycles": 10}, "duration_seconds": 30},
            {"step_number": 4, "step_type": "incubate", "instrument": "incubator", "description": "Denaturation 5 min room temp", "parameters": {"duration_minutes": 5}, "duration_seconds": 300},
            {"step_number": 5, "step_type": "analyst", "instrument": "analyst", "description": "Confirm NaOH freshness < 7 days", "parameters": {}, "duration_seconds": 30},
            {"step_number": 6, "step_type": "dispense", "instrument": "liquid_handler", "description": "Add 990 uL pre-chilled HT1 buffer", "parameters": {"volume_uL": 990}, "duration_seconds": 60},
            {"step_number": 7, "step_type": "mix", "instrument": "liquid_handler", "description": "Mix 10 cycles for final loading concentration", "parameters": {"cycles": 10}, "duration_seconds": 60},
            {"step_number": 8, "step_type": "dispense", "instrument": "liquid_handler", "description": "Optional PhiX 1% spike-in", "parameters": {"volume_uL": 10}, "duration_seconds": 30},
            {"step_number": 9, "step_type": "transport", "instrument": "analyst", "description": "Transfer to sequencer cartridge within 30 min", "parameters": {"source_instrument": "liquid_handler", "destination_instrument": "analyst"}, "duration_seconds": 120},
        ]
    },
]


# ═══════════════════════════════════════════════════════════════════════════
#  QUERY API — matches field_01/field_04 conventions
# ═══════════════════════════════════════════════════════════════════════════

def get_all_assays():
    """Return the full assay list."""
    return GENOMICS_ASSAYS


def get_assay_by_id(assay_id):
    """Look up a single assay by its ID string (e.g. 'NGS_003')."""
    for a in GENOMICS_ASSAYS:
        if a["assay_id"] == assay_id:
            return a
    return None


def get_assays_by_product(product_type):
    """Return all assays that list a given product type."""
    return [a for a in GENOMICS_ASSAYS if product_type in a.get("product_types", [])]


def get_assays_by_difficulty(difficulty):
    """Return all assays matching an automation difficulty level."""
    return [a for a in GENOMICS_ASSAYS if a.get("automation_difficulty") == difficulty]


def get_assays_by_workbench(workbench_id):
    """Return all assays assigned to a specific workbench."""
    return [a for a in GENOMICS_ASSAYS if a.get("workbench_id") == workbench_id]


def get_field_summary():
    total = len(GENOMICS_ASSAYS)
    easy = len(get_assays_by_difficulty("easy"))
    medium = len(get_assays_by_difficulty("medium"))
    cpx = len(get_assays_by_difficulty("complex"))
    workbenches = sorted(set(a.get("workbench_id", "N/A") for a in GENOMICS_ASSAYS))
    return {
        "field": "Genomics / NGS",
        "version": "1.0",
        "total_assays": total,
        "easy": easy,
        "medium": medium,
        "complex": cpx,
        "workbenches": workbenches,
    }


if __name__ == "__main__":
    s = get_field_summary()
    print(f"\n{'=' * 80}")
    print(f"  GENOMICS / NGS ASSAY LIBRARY -- BioInterface v1.0")
    print(f"  Total assays: {s['total_assays']}")
    print(f"{'=' * 80}\n")
    print(f"  Easy automation:    {s['easy']} assays")
    print(f"  Medium automation:  {s['medium']} assays")
    print(f"  Complex automation: {s['complex']} assays")
    print(f"  Workbenches used:   {', '.join(s['workbenches'])}")
    print(f"\n{'-' * 80}")
    for a in GENOMICS_ASSAYS:
        diff = {"easy": "EASY  ", "medium": "MEDIUM", "complex": "COMPLEX"}[a["automation_difficulty"]]
        print(f"  {a['assay_id']}  [{diff}]  {a['name']}")
        print(f"           Robot: {a['robot_active_minutes']} min | "
              f"Total: {a['total_assay_duration_hours']} hr | "
              f"Samples: {a['throughput_samples_per_run']}/run | "
              f"Steps: {len(a['protocol_steps_v3'])} v3")
        print()
