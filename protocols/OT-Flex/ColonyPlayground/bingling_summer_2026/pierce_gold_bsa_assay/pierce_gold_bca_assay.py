from opentrons import protocol_api
from opentrons.types import Point
from opentrons.protocol_api import PARTIAL_COLUMN, ALL
from opentrons.protocol_api import SINGLE, ALL

# Edit the numbers here to suit your needs
# Note this code can accept up to 24 unknowns and up to 2 replicates
# or accpet up to 18 unknowns and 3 replicates
standards_number = 8
unknown_number = 4

# Supports up to 3 replicates depending on number of unknowns
replicates_number = 1 

volume_reagent_per_sample = 200  # uL

#v-well or diamond-well? Input 1 for v-well or 2 for diamond-well
well_type = 1

#Change module deck location base on your own setup
temp_module_location = 'C3'
heater_shaker_location = 'C1'

#Change pipette location base on your own setup ('left' or 'right')
pipette_8channel_1000_location = 'right'
pipette_1channel_50_location = 'left'

metadata = {
    'protocolName': 'Pierce Gold BCA Assay',
    'author': 'Bing',
    'description': 'Automated liquid handling for Pierce Gold BCA Protein Assay to determine protein concentrations'
}

requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.25'
}

def run(protocol: protocol_api.ProtocolContext):

    # well type
    if well_type == 1:
        well = 'nest_12_reservoir_15ml'
    else: 
        well = 'usascientific_12_reservoir_22mL'
    
    # Load trash bin
    trash = protocol.load_trash_bin('A3')

    # Load modules
    thermocycler = protocol.load_module('thermocyclerModuleV2')
    temp_module = protocol.load_module('temperature module gen2', temp_module_location)
    heater_shaker = protocol.load_module('heaterShakerModuleV1', heater_shaker_location)

    # Load labware
    reservoir = protocol.load_labware(well, 'D1')
    standard_tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 'D2')
    unknown_tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 'D3')

    # Load heater shaker adapter
    hs_adapter = heater_shaker.load_adapter("opentrons_universal_flat_adapter")

    # Load labware on heater shaker module
    hs_plate = hs_adapter.load_labware(
        "nunc_96_wellplate_optical_bottom_400ul",
        label="Nunc well plate on Heater_Shaker"
    )

    # Load tip racks for all operations
    tiprack200 = protocol.load_labware('opentrons_flex_96_tiprack_200ul', 'B3')
    tiprack50 = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'B2')

    # Load pipettes
    p1000_single = protocol.load_instrument(
        'flex_1channel_50',
        mount=pipette_1channel_50_location,
        tip_racks=[tiprack50]
    )
    p1000_multi = protocol.load_instrument(
        'flex_8channel_1000',
        mount=pipette_8channel_1000_location,
        tip_racks=[tiprack200]
    )

    # Define liquids
    reagent_a = protocol.define_liquid(
        name='Reagent A',
        description='BCA Reagent A',
        display_color='#00FF00'
    )
    reagent_b = protocol.define_liquid(
        name='Reagent B',
        description='BCA Reagent B',
        display_color='#0000FF'
    )
    bsa_standard = protocol.define_liquid(
        name='BSA Standard',
        description='BSA standard',
        display_color='#FF0000'
    )
    bsa_unknown = protocol.define_liquid(
        name='BSA unknowns',
        description='BSA unknowns',
        display_color='#FFFF00'
    )

    # Calculating total reagent needed
    if well_type == 1:
        # Calculating total reagent needed for v-well reservoir
        total_reagent = (round(((standards_number + unknown_number) * replicates_number * volume_reagent_per_sample))) + 300

        # Load liquids into labware
        reservoir['A1'].load_liquid(liquid=reagent_a, volume=(total_reagent + 200))
        standard_tube_rack['D6'].load_liquid(liquid=reagent_b, volume=(total_reagent / 50) + 30)

    else: 
        total_reagent = (round(
        ((standards_number + unknown_number) * replicates_number * volume_reagent_per_sample) * 1.15)) + (150 * (8 - (unknown_number % 8)))

        # Load liquids into labware
        reservoir['A1'].load_liquid(liquid=reagent_a, volume=(total_reagent + 400))
        standard_tube_rack['D6'].load_liquid(liquid=reagent_b, volume=(total_reagent / 50) + 30)

    # Establishing where the standards will go in the tube rack
    standard_sources = standard_tube_rack.wells()[:standards_number]
    # Load BSA standards into labware
    for tube in standard_sources:
        tube.load_liquid(liquid=bsa_standard, volume=200)

    # Establishing where the unknowns will go in the tube rack
    unknown_sources = unknown_tube_rack.wells()[:unknown_number]
    # Load BSA unknowns into labware
    for tube in unknown_sources:
        tube.load_liquid(liquid=bsa_unknown, volume=200)

    # Helper function to calculate destination wells for unknowns and standards
    import math
    def get_destination_wells(source_idx, start_column, columns_per_replicate):
        """Calculate destination wells for a given source across all replicates"""
        destinations = []
        for replicate in range(replicates_number):
            column_offset = source_idx // 8
            row_in_column = source_idx % 8
            dest_column = start_column + (replicate * columns_per_replicate) + column_offset
            destinations.append(hs_plate.columns()[dest_column][row_in_column])
        return destinations

    # Close heater shaker latch
    heater_shaker.close_labware_latch()

    # ===== STEP 1: Microplate Procedure - Transferring Standards =============================================
    protocol.comment('Transferring BSA standards to well plate')

    p1000_single.flow_rate.aspirate = 15
    p1000_single.flow_rate.dispense = 15

    # Get the replicate destination columns (columns 2, 3, 4, etc.)
    for idx, source in enumerate(standard_sources):
        destinations = get_destination_wells(idx, start_column=0, columns_per_replicate=1)

        p1000_single.pick_up_tip(tiprack50)
        p1000_single.mix(1, 50, source)  # Mix at source before aspirating
        p1000_single.blow_out(source.top())
        p1000_single.aspirate(10 * replicates_number, source.bottom(1))  # Single source (will be stretched to match destinations)

        for dest in destinations:  # Dispensing to list of destinations
            p1000_single.dispense(10, dest)
            p1000_single.blow_out(dest.top())
            p1000_single.touch_tip()
            p1000_single.blow_out(dest.top())

        p1000_single.drop_tip()

    # ===== STEP 2: Microplate Procedure - Transferring Unknowns =============================================

    protocol.comment('Transferring unknown samples to well plate')

    for idx, source in enumerate(unknown_sources):
        destinations = get_destination_wells(idx,
                                             start_column=replicates_number,
                                             columns_per_replicate=math.ceil(unknown_number / 8)
                                             )

        p1000_single.pick_up_tip(tiprack50)
        p1000_single.mix(1, 50, source)  # Mix at source before aspirating
        p1000_single.blow_out(source.top())
        p1000_single.aspirate(10 * replicates_number, source.bottom(1))  # Single source (will be stretched to match destinations)

        for dest in destinations:  # Dispensing to list of destinations
            p1000_single.dispense(10, dest)
            p1000_single.blow_out(dest.top())
            p1000_single.touch_tip()
            p1000_single.blow_out(dest.top())

        p1000_single.drop_tip()

    # ===== STEP 3: Prepare BCA Working Reagent ===============================================================
    reagent_a_volume = total_reagent  # µL
    reagent_b_volume = total_reagent / 50  # µL

    protocol.comment('Preparing BCA working reagent in reservoir A2')

    # Transfer Reagent A to reservoir A2
    p1000_multi.pick_up_tip()
    p1000_single.pick_up_tip()

    p1000_multi.flow_rate.aspirate = 200
    p1000_multi.flow_rate.dispense = 100

    p1000_multi.transfer(
        reagent_a_volume / 8,
        reservoir['A1'].bottom(-0.20),
        reservoir['A2'],
        new_tip='never',
        touch_tip = True
    )

    # Transfer Reagent B to reservoir A2
    reagent_b_transfer = []

    counts = reagent_b_volume // 50
    remainder = reagent_b_volume % 50

    for i in range(int(counts)):
        reagent_b_transfer.append(50)

    if remainder > 0:
        reagent_b_transfer.append(remainder)

    # Reagent B is uniformly distributed across reservoir well A2
    for count in reagent_b_transfer:
        res = reservoir['A2'].bottom(5)
        res_position = [res.move(Point(y=10 * i)) for i in range(-3, 4)]
        p1000_single.aspirate(count, standard_tube_rack['D6'])
        for position in res_position:
            p1000_single.dispense((count / 7), position)
        p1000_single.blow_out(reservoir['A2'].top())

    # Mixing reagent A and B
    p1000_multi.mix(1, 200, reservoir['A2'].bottom(2))
    p1000_multi.mix(2, 200 * 0.7, reservoir['A2'].bottom(3))
    p1000_multi.blow_out(reservoir['A2'].top())
    p1000_multi.mix(1, 200 * 0.5, reservoir['A2'].bottom(4))
    p1000_multi.blow_out(reservoir['A2'].top())

    p1000_single.drop_tip()
    p1000_multi.drop_tip()

    # ===== STEP 4: Adding Working Reagent to Standards ============================================================
    protocol.comment('Adding working reagent to standards')
    p1000_multi.pick_up_tip()

    p1000_multi.aspirate(200, reservoir['A2'])
    p1000_multi.dispense(200, hs_plate['A1'])
    p1000_multi.blow_out(hs_plate['A1'].top())

    p1000_multi.drop_tip()

    if replicates_number > 1:
        dest_columns_WR = hs_plate.columns()[1:replicates_number]
        p1000_multi.transfer(
            200,
            reservoir['A2'],
            dest_columns_WR,
            blow_out=True,
            blowout_location='destination well',
            new_tip='always',
            touch_tip = True
        )

    # ===== STEP 5: Adding Working Reagent to Unknowns =================================================================

    # Calculate columns needed for unknowns
    columns_per_replicate = math.ceil(unknown_number / 8)
    total_unknown_columns = columns_per_replicate * replicates_number

    # Calculate total wells that need working reagent
    total_unknown_wells = unknown_number * replicates_number

    # NOZZLE CONFIGURATION MAPPING
    nozzle_map = {
        1: 'H1', 2: 'G1', 3: 'F1', 4: 'E1',
        5: 'D1', 6: 'C1', 7: 'B1', 8: 'A1'
    }

    protocol.comment('Adding working reagent to unknown wells')

    # Calculate how unknowns are distributed
    unknown_start_column = replicates_number

    # Process each replicate set
    for replicate in range(replicates_number):
        replicate_start_col = unknown_start_column + (replicate * columns_per_replicate)

        # Calculate full and partial columns for this replicate
        full_columns_in_replicate = unknown_number // 8
        remaining_wells_in_replicate = unknown_number % 8

        # Handle full columns
        if full_columns_in_replicate > 0:
            p1000_multi.configure_nozzle_layout(
                style=ALL,
                tip_racks=[tiprack200]
            )

            for col_offset in range(full_columns_in_replicate):
                dest_col = replicate_start_col + col_offset
                p1000_multi.transfer(
                    200,
                    reservoir['A2'].bottom(0),
                    hs_plate.columns()[dest_col][0],
                    blow_out=True,
                    blowout_location='destination well',
                    touch_tip = True,
                    new_tip='always'
                )

        # Handle partial column
        if remaining_wells_in_replicate > 0 and remaining_wells_in_replicate != 1:
            end_nozzle = nozzle_map[remaining_wells_in_replicate]

            p1000_multi.configure_nozzle_layout(
                style=PARTIAL_COLUMN,
                start='H1',
                end=end_nozzle,
                tip_racks=[tiprack200]
            )

            # Calculate destination column and target well
            dest_col = replicate_start_col + full_columns_in_replicate
            target_row = chr(ord('A') + remaining_wells_in_replicate - 1)
            target_well = f"{target_row}{dest_col + 1}"

            p1000_multi.transfer(
                200,
                reservoir['A2'].bottom(-0.20),
                hs_plate[target_well],
                blow_out=True,
                blowout_location='destination well',
                touch_tip = True,
                new_tip='always'
            )

        # Handle partial column if it is only 1 well for that column
        if remaining_wells_in_replicate == 1:
            # Calculate destination column and target well
            dest_col = replicate_start_col + full_columns_in_replicate
            target_row = chr(ord('A') + remaining_wells_in_replicate - 1)
            target_well = f"{target_row}{dest_col + 1}"

            p1000_single.transfer(
                200,
                reservoir['A2'].bottom(-0.20),
                hs_plate[target_well],
                blow_out=True,
                blowout_location='destination well',
                touch_tip = True,
                new_tip='always'
            )

    protocol.comment('Working reagent distribution complete')

    # ===== STEP 6: Shake ===============================================================================================
    protocol.comment("Shaking at 825 rpm")
    heater_shaker.set_and_wait_for_shake_speed(825)  # Set rpm
    protocol.delay(seconds=25)  # Shake for 25 seconds

    # Stop shaking
    heater_shaker.deactivate_shaker()

    # Open heater shaker latch
    heater_shaker.open_labware_latch()
    delay_time = (260 - ((10 * replicates_number) + (10 * total_unknown_columns)))
    protocol.comment(f'Incubating at room temperature for {delay_time}')
    protocol.delay(seconds=delay_time)

    protocol.comment(
        'BCA Protein Assay protocol complete, please send wellplate to platereader immediately to read at 480nm. You have 20 seconds')
