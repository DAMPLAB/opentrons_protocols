from opentrons import protocol_api

metadata = {
    'protocolName': 'Promega Miniprep Draft',
    'author': 'Zach',
    'description': 'Automated miniprep protocol using the promega magnesil kit'
}

requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.25'
}


def add_parameters(parameters: protocol_api.ParameterContext):
    parameters.add_int(
        variable_name="sample_count",
        display_name="Sample count",
        description="Number of samples to process (1-23). Walk-away build: no mid-run pauses.",
        default=8,
        minimum=1,
        maximum=23
    )
    parameters.add_int(
        variable_name="elution_buffer_vol_ul",
        display_name="Elution buffer (uL)",
        description="Elution buffer volume per sample, 30-100 uL.",
        default=50,
        minimum=30,
        maximum=100
    )


def run(protocol: protocol_api.ProtocolContext):
    sample_count = protocol.params.sample_count
    elution_buffer_vol_ul = protocol.params.elution_buffer_vol_ul

    # For each reservoir
    DEAD_VOLUME_UL = 300

    RESUSPENSION_VOL_UL = 115
    RESUSPENSION_SHAKE_RPM = 1200
    RESUSPENSION_SHAKE_MIN = 3

    LYSIS_VOL_UL = 150
    LYSIS_SHAKE_RPM = 1200
    LYSIS_SHAKE_MIN = 5

    NEUTRALIZATION_VOL_UL = 150
    NEUTRALIZATION_SHAKE_RPM = 1200
    NEUTRALIZATION_SHAKE_MIN = 1

    MAGNESIL_BLUE_VOL_UL = 25
    MAGNESIL_BLUE_MIX_REPS = 10
    MAGNESIL_BLUE_MIX_VOL_UL = 265
    BLUE_MIX_SHAKE_RPM = 1200
    BLUE_MIX_SHAKE_MIN = 5

    LYSIS_MAGNET_MIN = 5
    CLEARING_MAGNET_MIN = 5
    # Total liquid added to a well. Used for both "transfer all of the cleared lysate" moves.
    CLEARED_LYSATE_VOL_UL = (
        RESUSPENSION_VOL_UL + LYSIS_VOL_UL + NEUTRALIZATION_VOL_UL + MAGNESIL_BLUE_VOL_UL
    )

    ISOPROPANOL_VOL_UL = 400
    MAGNESIL_RED_VOL_UL = 50
    BINDING_SHAKE_RPM = 1200
    BINDING_SHAKE_MIN = 10
    BINDING_MAGNET_MIN = 5
    # Everything in the binding well that isn't bound DNA/beads.
    BINDING_SUPERNATANT_VOL_UL = CLEARED_LYSATE_VOL_UL + ISOPROPANOL_VOL_UL + MAGNESIL_RED_VOL_UL

    WASH_4_40_VOL_UL = 200
    WASH_4_40_SHAKE_RPM = 1400
    WASH_4_40_SHAKE_MIN = 2
    WASH_4_40_MAGNET_MIN = 1

    ETHANOL_VOL_UL = 190
    ETHANOL_WASH_CYCLES = 2
    ETHANOL_SHAKE_RPM = 1200
    ETHANOL_SHAKE_MIN = 1
    ETHANOL_MAGNET_MIN = 1

    AIR_DRY_MAGNET_MIN = 5
    # SOP says "residual ethanol" -- assumed value, using 200uL tips.
    RESIDUAL_ETHANOL_VOL_UL = 20

    HEAT_DRY_TEMP_C = 65
    HEAT_DRY_MIN = 10

    ELUTION_BUFFER_VOL_UL = elution_buffer_vol_ul
    ELUTION_SHAKE_RPM = 1200
    ELUTION_SHAKE_MIN = 5
    ELUTION_MAGNET_MIN = 2
    # Leave a 10uL margin below whatever was added so the transfer never
    # tries to pull more liquid than exists in the well.
    ELUATE_TRANSFER_VOL_UL = ELUTION_BUFFER_VOL_UL - 10

    protocol.load_trash_bin('A3')
    protocol.load_module('thermocyclerModuleV2')     # Loaded but unused in this protocol
    temp_module = protocol.load_module('temperature module gen2', 'C3')
    heater_shaker = protocol.load_module('heaterShakerModuleV1', 'C1')

    clearing_plate = protocol.load_labware('greiner_96_microplate_280ul', 'A2')
    binding_plate = protocol.load_labware('greiner_96_microplate_280ul', 'D2')
    reservoir = temp_module.load_labware('usascientific_12_reservoir_22ml')

    hs_adapter = heater_shaker.load_adapter("opentrons_universal_flat_adapter")
    deep_wellplate = hs_adapter.load_labware(
        "greiner_96_wellplate_2000ul",
        label="Deep wellplate on heater"
    )

    mag_block = protocol.load_module("magneticBlockV1", "D1")

    tiprack1000 = protocol.load_labware('opentrons_flex_96_tiprack_1000ul', 'B2')
    tiprack200 = protocol.load_labware('opentrons_flex_96_tiprack_200ul', 'B3')

    # 2nd 1000uL rack, native at D3 (pipette-accessible, not a staging slot --
    # no gripper move needed). B4/D4, the only usable staging slots (A4/C4
    # are permanently blocked by the trash bin and temp module), are spent
    # parking spent plates instead of staging spare tip racks, so the run
    # never pauses for a human. That trade is why sample_count tops out at
    # 23 rather than higher -- see pick_up_1000()/pick_up_200() below.
    tiprack1000_d3 = protocol.load_labware('opentrons_flex_96_tiprack_1000ul', 'D3')

    # Dedicated single-channel rack. Every other working slot is claimed
    # (permanently or transiently) by this point, so it goes on C2.
    tiprack1000_single = protocol.load_labware('opentrons_flex_96_tiprack_1000ul', 'C2')

    p1000_multi = protocol.load_instrument(
        'flex_8channel_1000',
        mount='right',
        tip_racks=[tiprack1000, tiprack200]
    )

    # Handles the remainder (non-multiple-of-8) samples
    p1000_single = protocol.load_instrument(
        'flex_1channel_1000',
        mount='left',
        tip_racks=[tiprack1000_single]
    )

    # No 200uL spare/swap -- D4 parks the spent clearing plate instead, and
    # 200uL usage never gets close to tight enough to need one. This wrapper
    # exists so every call site is uniform and a run that somehow exceeds
    # capacity fails with a clear message instead of silently misbehaving.
    tip200_state = {"columns_used": 0}

    def pick_up_200(pipette):
        if tip200_state["columns_used"] >= 12:
            raise RuntimeError(
                'The 200 uL tip rack is empty -- lower sample count.'
            )
        pipette.pick_up_tip(tiprack200)
        tip200_state["columns_used"] += 1

    # Two native 1000uL racks (B2, D3)
    tip1000_native_racks = [(tiprack1000, "B2"), (tiprack1000_d3, "D3")]
    tip1000_state = {"native_index": 0, "columns_used": 0, "current_rack": tiprack1000}

    def pick_up_1000(pipette):
        if tip1000_state["columns_used"] >= 12:
            next_index = tip1000_state["native_index"] + 1
            if next_index >= len(tip1000_native_racks):
                raise RuntimeError(
                    'Both 1000 uL tip racks are empty -- lower sample count.'
                )
            tip1000_state["native_index"] = next_index
            tip1000_state["current_rack"] = tip1000_native_racks[next_index][0]
            tip1000_state["columns_used"] = 0
        pipette.pick_up_tip(tip1000_state["current_rack"])
        tip1000_state["columns_used"] += 1

    bacterial_culture = protocol.define_liquid(name='Bacterial culture', display_color="#000000")
    resuspension_solution = protocol.define_liquid(name='Resuspension Solution', display_color='#00FF00')
    lysis_solution = protocol.define_liquid(name='Cell Lysis Solution', display_color="#73D3BB")
    neutralization_solution = protocol.define_liquid(name='Neutralization Solution', display_color='#FFFF00')
    magnesil_blue = protocol.define_liquid(name='Magnesil Blue', display_color="#3A93E6")
    magnesil_red = protocol.define_liquid(name='Magnesil Red', display_color="#CC2121")
    isopropanol = protocol.define_liquid(name='100% Isopropanol', display_color="#F5A623")
    wash_4_40 = protocol.define_liquid(name='4/40 Wash Buffer', display_color="#9013FE")
    elution_buffer = protocol.define_liquid(name='Elution Buffer', display_color="#913FFC")
    ethanol_80 = protocol.define_liquid(name='80 percent Ethanol', display_color="#D6D6D6")

    # Reservoir wells hold 22 mL; loaded volume = usage for sample_count
    # samples + a 300uL dead volume. At this build's ceiling (23, tip-bound)
    # the tightest well (isopropanol) sits at ~9.5mL, well under capacity.
    reservoir['A1'].load_liquid(liquid=resuspension_solution, volume=RESUSPENSION_VOL_UL * sample_count + DEAD_VOLUME_UL)
    reservoir['A2'].load_liquid(liquid=lysis_solution, volume=LYSIS_VOL_UL * sample_count + DEAD_VOLUME_UL)
    reservoir['A3'].load_liquid(liquid=neutralization_solution, volume=NEUTRALIZATION_VOL_UL * sample_count + DEAD_VOLUME_UL)
    reservoir['A4'].load_liquid(liquid=magnesil_blue, volume=MAGNESIL_BLUE_VOL_UL * sample_count + DEAD_VOLUME_UL)
    reservoir['A5'].load_liquid(liquid=magnesil_red, volume=MAGNESIL_RED_VOL_UL * sample_count + DEAD_VOLUME_UL)
    reservoir['A6'].load_liquid(liquid=ethanol_80, volume=ETHANOL_VOL_UL * ETHANOL_WASH_CYCLES * sample_count + DEAD_VOLUME_UL)
    reservoir['A7'].load_liquid(liquid=elution_buffer, volume=ELUTION_BUFFER_VOL_UL * sample_count + DEAD_VOLUME_UL)
    reservoir['A8'].load_liquid(liquid=isopropanol, volume=ISOPROPANOL_VOL_UL * sample_count + DEAD_VOLUME_UL)
    reservoir['A9'].load_liquid(liquid=wash_4_40, volume=WASH_4_40_VOL_UL * sample_count + DEAD_VOLUME_UL)

    bacteria_location = deep_wellplate.wells()[:sample_count]
    for well in bacteria_location:
        well.load_liquid(liquid=bacterial_culture, volume=1000)

    # full_columns: complete 8-well columns, handled by the 8-channel pipette.
    # remainder: leftover samples (1-7), handled individually by the 1-channel.
    full_columns = sample_count // 8
    remainder = sample_count % 8

    well_location = [8 * i for i in range(full_columns)]
    remainder_start = full_columns * 8
    remainder_wells = list(range(remainder_start, remainder_start + remainder))

    def shake(rpm, minutes):
        heater_shaker.set_and_wait_for_shake_speed(rpm)
        protocol.delay(minutes=minutes)
        heater_shaker.deactivate_shaker()

    # ========================= STEP 1: Cell Resuspension =======================================================
    protocol.comment(f'Adding {RESUSPENSION_VOL_UL} uL of resuspension solution to the deep well plate')

    heater_shaker.close_labware_latch()

    deep_well_dest_top = [deep_wellplate.wells()[well].top(-2) for well in well_location]
    deep_well_dest_top_remainder = [deep_wellplate.wells()[well].top(-2) for well in remainder_wells]

    if full_columns > 0:
        pick_up_1000(p1000_multi)
        p1000_multi.distribute(
            RESUSPENSION_VOL_UL,
            reservoir['A1'],
            deep_well_dest_top,
            touch_tip=False,
            new_tip='never'
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.distribute(
            RESUSPENSION_VOL_UL,
            reservoir['A1'],
            deep_well_dest_top_remainder,
            touch_tip=False,
            new_tip='once',
        )

    protocol.comment(f'Shaking lysis plate at {RESUSPENSION_SHAKE_RPM} rpm for {RESUSPENSION_SHAKE_MIN} min')
    shake(RESUSPENSION_SHAKE_RPM, RESUSPENSION_SHAKE_MIN)

    # ========================= STEP 2: Cell Lysis and Lysate Clearing =======================================================
    protocol.comment(f'Adding {LYSIS_VOL_UL} uL of lysis solution to the deep well plate')

    if full_columns > 0:
        pick_up_1000(p1000_multi)
        p1000_multi.distribute(
            LYSIS_VOL_UL,
            reservoir['A2'],
            deep_well_dest_top,
            touch_tip=False,
            new_tip='never',
            disposal_volume=0
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.distribute(
            LYSIS_VOL_UL,
            reservoir['A2'],
            deep_well_dest_top_remainder,
            touch_tip=False,
            new_tip='once',
            disposal_volume=0
        )

    protocol.comment(f'Shaking lysis plate at {LYSIS_SHAKE_RPM} rpm for {LYSIS_SHAKE_MIN} min')
    shake(LYSIS_SHAKE_RPM, LYSIS_SHAKE_MIN)

    protocol.comment(f'Adding {NEUTRALIZATION_VOL_UL} uL of neutralization solution to the deep well plate')

    if full_columns > 0:
        pick_up_1000(p1000_multi)
        p1000_multi.distribute(
            NEUTRALIZATION_VOL_UL,
            reservoir['A3'],
            deep_well_dest_top,
            touch_tip=False,
            new_tip='never',
            disposal_volume=0
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.distribute(
            NEUTRALIZATION_VOL_UL,
            reservoir['A3'],
            deep_well_dest_top_remainder,
            touch_tip=False,
            new_tip='once',
            disposal_volume=0
        )

    protocol.comment(f'Shaking lysis plate at {NEUTRALIZATION_SHAKE_RPM} rpm for {NEUTRALIZATION_SHAKE_MIN} min')
    shake(NEUTRALIZATION_SHAKE_RPM, NEUTRALIZATION_SHAKE_MIN)

    protocol.comment(f'Adding {MAGNESIL_BLUE_VOL_UL} uL of magnesil blue to the deep well plate and mixing')

    # Mixing submerges the tip -- fresh tip per column.
    deep_well_dest_mix = [deep_wellplate.wells()[well].bottom(5) for well in well_location]
    deep_well_dest_mix_remainder = [deep_wellplate.wells()[well].bottom(5) for well in remainder_wells]

    if full_columns > 0:
        for dest in deep_well_dest_mix:
            pick_up_1000(p1000_multi)
            p1000_multi.transfer(
                MAGNESIL_BLUE_VOL_UL,
                reservoir['A4'],
                dest,
                touch_tip=False,
                new_tip='never',
                disposal_volume=0,
                mix_after=(MAGNESIL_BLUE_MIX_REPS, MAGNESIL_BLUE_MIX_VOL_UL)
            )
            p1000_multi.drop_tip()

    if remainder > 0:
        for dest in deep_well_dest_mix_remainder:
            p1000_single.pick_up_tip(tiprack1000_single)
            p1000_single.transfer(
                MAGNESIL_BLUE_VOL_UL,
                reservoir['A4'],
                dest,
                touch_tip=False,
                new_tip='never',
                disposal_volume=0,
                mix_after=(MAGNESIL_BLUE_MIX_REPS, MAGNESIL_BLUE_MIX_VOL_UL)
            )
            p1000_single.drop_tip()

    protocol.comment(f'Shaking lysis plate at {BLUE_MIX_SHAKE_RPM} rpm for {BLUE_MIX_SHAKE_MIN} min')
    shake(BLUE_MIX_SHAKE_RPM, BLUE_MIX_SHAKE_MIN)

    protocol.comment('Moving lysis plate to the magnet')
    heater_shaker.open_labware_latch()
    protocol.move_labware(deep_wellplate, new_location=mag_block, use_gripper=True)
    protocol.comment(f'Magnetizing lysis plate for {LYSIS_MAGNET_MIN} min')
    protocol.delay(minutes=LYSIS_MAGNET_MIN)

    protocol.comment('Transferring cleared lysate to the clearing plate')

    deep_well_lysate_src = [deep_wellplate.wells()[well].bottom(2) for well in well_location]
    deep_well_lysate_src_remainder = [deep_wellplate.wells()[well].bottom(2) for well in remainder_wells]
    clearing_plate_dest = [clearing_plate.wells()[well] for well in well_location]
    clearing_plate_dest_remainder = [clearing_plate.wells()[well] for well in remainder_wells]

    if full_columns > 0:
        for src, dest in zip(deep_well_lysate_src, clearing_plate_dest):
            pick_up_1000(p1000_multi)
            p1000_multi.transfer(
                CLEARED_LYSATE_VOL_UL,
                src,
                dest,
                touch_tip=True,
                new_tip='never'
            )
            p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.transfer(
            CLEARED_LYSATE_VOL_UL,
            deep_well_lysate_src_remainder,
            clearing_plate_dest_remainder,
            touch_tip=True,
            new_tip='always'
        )

    # Parked on staging slot D4 (gripper-only) rather than sent off-deck --
    # never touched again, and this keeps the run walk-away friendly.
    protocol.comment('Moving spent lysis plate to a staging slot')
    protocol.move_labware(deep_wellplate, new_location="D4", use_gripper=True)

    protocol.comment('Moving clearing plate to the magnet for second-pass clearing')
    protocol.move_labware(clearing_plate, new_location=mag_block, use_gripper=True)
    protocol.delay(minutes=CLEARING_MAGNET_MIN)

    # ========================= Prep 3: Binding =======================================================
    # Isopropanol + MagneSil Red go in up front so the plate is ready the
    # moment cleared lysate arrives
    protocol.comment('Preparing binding plate with isopropanol and MagneSil Red')

    binding_plate_dest_top = [binding_plate.wells()[well].top(-0.2) for well in well_location]
    binding_plate_dest_top_remainder = [binding_plate.wells()[well].top(-0.2) for well in remainder_wells]

    if full_columns > 0:
        pick_up_1000(p1000_multi)
        p1000_multi.distribute(
            ISOPROPANOL_VOL_UL,
            reservoir['A8'],
            binding_plate_dest_top,
            touch_tip=False,
            new_tip='never'
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.distribute(
            ISOPROPANOL_VOL_UL,
            reservoir['A8'],
            binding_plate_dest_top_remainder,
            touch_tip=False,
            new_tip='once'
        )

    if full_columns > 0:
        pick_up_200(p1000_multi)
        p1000_multi.distribute(
            MAGNESIL_RED_VOL_UL,
            reservoir['A5'],
            binding_plate_dest_top,
            touch_tip=False,
            new_tip='never'
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.distribute(
            MAGNESIL_RED_VOL_UL,
            reservoir['A5'],
            binding_plate_dest_top_remainder,
            touch_tip=False,
            new_tip='once'
        )

    # ========================= STEP 3: DNA Binding =======================================================
    protocol.comment('Transferring cleared lysate to the binding plate')

    clearing_plate_src = [clearing_plate.wells()[well].bottom(2) for well in well_location]
    clearing_plate_src_remainder = [clearing_plate.wells()[well].bottom(2) for well in remainder_wells]

    if full_columns > 0:
        for src, dest in zip(clearing_plate_src, binding_plate_dest_top):
            pick_up_1000(p1000_multi)
            p1000_multi.transfer(
                CLEARED_LYSATE_VOL_UL,
                src,
                dest,
                touch_tip=True,
                new_tip='never'
            )
            p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.transfer(
            CLEARED_LYSATE_VOL_UL,
            clearing_plate_src_remainder,
            binding_plate_dest_top_remainder,
            touch_tip=True,
            new_tip='always'
        )

    protocol.comment('Moving spent clearing plate to a staging slot')
    protocol.move_labware(clearing_plate, new_location="B4", use_gripper=True)

    protocol.comment('Binding plasmid DNA to MagneSil Red')
    protocol.move_labware(
        binding_plate,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0.5, 'y': 0, 'z': -3}
    )
    heater_shaker.close_labware_latch()
    protocol.comment(f'Shaking binding plate at {BINDING_SHAKE_RPM} rpm for {BINDING_SHAKE_MIN} min')
    shake(BINDING_SHAKE_RPM, BINDING_SHAKE_MIN)
    heater_shaker.open_labware_latch()

    protocol.move_labware(
        binding_plate,
        new_location=mag_block,
        use_gripper=True,
        drop_offset={"x": 0, 'y': 0, 'z': -4.5}
    )
    protocol.comment(f'Magnetizing binding plate for {BINDING_MAGNET_MIN} min')
    protocol.delay(minutes=BINDING_MAGNET_MIN)

    protocol.comment('Carefully removing lysate/isopropanol supernatant from the binding plate, DRAFTING')

    #CAREFUL HERE, MUST CHECK AND TWEAK FOR DIFFERENT PLATES
    binding_plate_supernatant = [binding_plate.wells()[well].bottom(2) for well in well_location]
    binding_plate_supernatant_remainder = [binding_plate.wells()[well].bottom(2) for well in remainder_wells]

    if full_columns > 0:
        for well in binding_plate_supernatant:
            pick_up_1000(p1000_multi)
            p1000_multi.transfer(
                BINDING_SUPERNATANT_VOL_UL,
                well,
                reservoir['A12'],
                new_tip='never'
            )
            p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.transfer(
            BINDING_SUPERNATANT_VOL_UL,
            binding_plate_supernatant_remainder,
            reservoir['A12'],
            new_tip='always'
        )

    # ========================= STEP 4: Washing =======================================================
    protocol.comment(f'Adding {WASH_4_40_VOL_UL} uL of 4/40 Wash Buffer to the binding plate')

    if full_columns > 0:
        pick_up_1000(p1000_multi)
        p1000_multi.distribute(
            WASH_4_40_VOL_UL,
            reservoir['A9'],
            binding_plate_dest_top,
            touch_tip=False,
            new_tip='never'
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.distribute(
            WASH_4_40_VOL_UL,
            reservoir['A9'],
            binding_plate_dest_top_remainder,
            touch_tip=False,
            new_tip='once'
        )

    protocol.move_labware(
        binding_plate,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0.5, 'y': 0, 'z': 3}
    )
    heater_shaker.close_labware_latch()
    protocol.comment(f'Shaking binding plate at {WASH_4_40_SHAKE_RPM} rpm for {WASH_4_40_SHAKE_MIN} min')
    shake(WASH_4_40_SHAKE_RPM, WASH_4_40_SHAKE_MIN)
    heater_shaker.open_labware_latch()

    protocol.move_labware(
        binding_plate,
        new_location=mag_block,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0, 'y': 0, 'z': -4.5}
    )
    protocol.comment(f'Magnetizing binding plate for {WASH_4_40_MAGNET_MIN} min')
    protocol.delay(minutes=WASH_4_40_MAGNET_MIN)
    # CAREFUL HERE, MUST CHECK AND TWEAK FOR DIFFERENT PLATES
    protocol.comment('Carefully removing 4/40 wash supernatant from the binding plate, DRAFTING')

    if full_columns > 0:
        for well in binding_plate_supernatant:
            pick_up_1000(p1000_multi)
            p1000_multi.transfer(
                WASH_4_40_VOL_UL,
                well,
                reservoir['A11'],
                new_tip='never'
            )
            p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.transfer(
            WASH_4_40_VOL_UL,
            binding_plate_supernatant_remainder,
            reservoir['A11'],
            new_tip='always'
        )

    protocol.comment(f'Washing binding plate {ETHANOL_WASH_CYCLES} times with 80% ethanol')

    for i in range(ETHANOL_WASH_CYCLES):
        if full_columns > 0:
            pick_up_1000(p1000_multi)
            p1000_multi.distribute(
                ETHANOL_VOL_UL,
                reservoir['A6'],
                binding_plate_dest_top,
                touch_tip=False,
                new_tip='never',
            )
            p1000_multi.drop_tip()

        if remainder > 0:
            p1000_single.distribute(
                ETHANOL_VOL_UL,
                reservoir['A6'],
                binding_plate_dest_top_remainder,
                touch_tip=False,
                new_tip='once',
            )

        protocol.move_labware(
            binding_plate,
            new_location=hs_adapter,
            use_gripper=True,
            pick_up_offset={"x": 0, 'y': 0, 'z': -2},
            drop_offset={"x": 0.5, 'y': 0, 'z': 3}
        )
        heater_shaker.close_labware_latch()
        protocol.comment(f'Shaking binding plate at {ETHANOL_SHAKE_RPM} rpm for {ETHANOL_SHAKE_MIN} min')
        shake(ETHANOL_SHAKE_RPM, ETHANOL_SHAKE_MIN)
        heater_shaker.open_labware_latch()

        protocol.move_labware(
            binding_plate,
            new_location=mag_block,
            use_gripper=True,
            pick_up_offset={"x": 0, 'y': 0, 'z': -2},
            drop_offset={"x": 0, 'y': 0, 'z': -4.5}
        )
        protocol.comment(f'Magnetizing binding plate for {ETHANOL_MAGNET_MIN} min')
        protocol.delay(minutes=ETHANOL_MAGNET_MIN)
        # CAREFUL HERE, MUST CHECK AND TWEAK FOR DIFFERENT PLATES
        protocol.comment('Carefully removing spent ethanol wash from the binding plate, DRAFTING')

        if full_columns > 0:
            for well in binding_plate_supernatant:
                pick_up_1000(p1000_multi)
                p1000_multi.transfer(
                    ETHANOL_VOL_UL,
                    well,
                    reservoir['A11'],
                    new_tip='never'
                )
                p1000_multi.drop_tip()

        if remainder > 0:
            p1000_single.transfer(
                ETHANOL_VOL_UL,
                binding_plate_supernatant_remainder,
                reservoir['A11'],
                new_tip='always'
            )

    # ========================= STEP 5: Drying =======================================================
    protocol.comment(f'Air drying binding plate on the magnet for {AIR_DRY_MAGNET_MIN} min')
    protocol.delay(minutes=AIR_DRY_MAGNET_MIN)

    # CAREFUL HERE, MUST CHECK AND TWEAK FOR DIFFERENT PLATES
    protocol.comment('Removing residual ethanol from the binding plate, DRAFTING')
    protocol.comment('Removing residual ethanol from the binding plate, DRAFTING')

    if full_columns > 0:
        for well in binding_plate_supernatant:
            pick_up_200(p1000_multi)
            p1000_multi.transfer(
                RESIDUAL_ETHANOL_VOL_UL,
                well,
                reservoir['A11'],
                new_tip='never'
            )
            p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.transfer(
            RESIDUAL_ETHANOL_VOL_UL,
            binding_plate_supernatant_remainder,
            reservoir['A11'],
            new_tip='always'
        )

    protocol.comment('Moving binding plate to the heater-shaker for heat drying')
    protocol.move_labware(
        binding_plate,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0.5, 'y': 0, 'z': 3}
    )
    heater_shaker.close_labware_latch()
    protocol.comment(f'Heat drying binding plate at {HEAT_DRY_TEMP_C} C for {HEAT_DRY_MIN} min')
    heater_shaker.set_target_temperature(HEAT_DRY_TEMP_C)
    heater_shaker.wait_for_temperature()
    protocol.delay(minutes=HEAT_DRY_MIN)
    heater_shaker.deactivate_heater()

    # ========================= STEP 6: Elution of DNA =======================================================
    protocol.comment(f'Adding {ELUTION_BUFFER_VOL_UL} uL of elution buffer into the binding plate')

    if full_columns > 0:
        pick_up_1000(p1000_multi)
        p1000_multi.distribute(
            ELUTION_BUFFER_VOL_UL,
            reservoir['A7'],
            binding_plate_dest_top,
            touch_tip=False,
            new_tip='never'
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.distribute(
            ELUTION_BUFFER_VOL_UL,
            reservoir['A7'],
            binding_plate_dest_top_remainder,
            touch_tip=False,
            new_tip='once'
        )

    protocol.comment(f'Shaking binding plate at {ELUTION_SHAKE_RPM} rpm for {ELUTION_SHAKE_MIN} min')
    shake(ELUTION_SHAKE_RPM, ELUTION_SHAKE_MIN)
    heater_shaker.open_labware_latch()

    protocol.move_labware(
        binding_plate,
        new_location=mag_block,
        use_gripper=True,
        drop_offset={"x": 0, 'y': 0, 'z': -5}
    )
    protocol.comment(f'Magnetizing binding plate for {ELUTION_MAGNET_MIN} min')
    protocol.delay(minutes=ELUTION_MAGNET_MIN)

    protocol.comment('Transferring eluate to the final plate')
    final_plate = protocol.load_labware('greiner_96_microplate_280ul', 'A2')

    # UNVERIFIED offset -- see the note on binding_plate's first move above.
    protocol.move_labware(
        labware=final_plate,
        new_location="D2",
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': 13},
        drop_offset={"x": 0, 'y': 0, 'z': 2.5}
    )

    final_plate_dest = [final_plate.wells()[well] for well in well_location]
    final_plate_dest_remainder = [final_plate.wells()[well] for well in remainder_wells]

    if full_columns > 0:
        pick_up_1000(p1000_multi)
        p1000_multi.transfer(
            ELUATE_TRANSFER_VOL_UL,
            binding_plate_supernatant,
            final_plate_dest,
            touch_tip=True,
            new_tip='never'
        )
        p1000_multi.drop_tip()

    if remainder > 0:
        p1000_single.transfer(
            ELUATE_TRANSFER_VOL_UL,
            binding_plate_supernatant_remainder,
            final_plate_dest_remainder,
            touch_tip=True,
            new_tip='once'
        )

    protocol.comment('Protocol Done')
