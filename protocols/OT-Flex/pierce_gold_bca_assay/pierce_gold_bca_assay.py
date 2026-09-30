from opentrons import protocol_api
from opentrons.types import Point
from opentrons.protocol_api import PARTIAL_COLUMN, ALL
from opentrons.protocol_api import SINGLE, ALL


reservoirs = ['nest_12_reservoir_15ml', 'usascientific_12_reservoir_22mL']


def add_parameters(parameters: protocol_api.ParameterContext):

    parameters.add_int(
        variable_name='unknown_num',
        display_name='number of unknowns',
        description='number of unknowns being tested in the experiment',
        default=4,
        maximum=24,
        minimum=0
    )

    parameters.add_int(
        variable_name='replicates_num',
        display_name='number of replicates',
        description='how many times each sample test is being replicated',
        default=1,
        maximum=3,
        minimum=1
    )

    parameters.add_str(
        variable_name="well_type",
        display_name='type of well',
        choices=[
            {"display_name": "v-well", "value": reservoirs[0]},
            {"display_name": "diamond-well", "value": reservoirs[1]}
        ],
        default='nest_12_reservoir_15ml'
    )

    """ parameters.add_bool(
        variable_name='pickup_excess',
        display_name='pick up excess reagent',
        description='Pipette residual reagent after protocol (needs 2 extra tubes)',
        default=False
    ) """

    parameters.add_str(
        variable_name='pipette_config',
        display_name='8 channel 1000uL configuration',
        description='mount side for 8ch 1000uL pipette (defines single pipette side too)',
        choices=[
            {'display_name': 'right', 'value': 'right'},
            {'display_name': 'left', 'value': 'left'}
        ],
        default='right'
    )


# Edit the numbers here to suit your needs
# Note this code can accept up to 24 unknowns and up to 3 replicates
standards_number = 8

volume_reagent_per_sample = 200  # uL

# Change module deck location base on your own setup
temp_module_location = 'C3'
heater_shaker_location = 'C1'

metadata = {
    'protocolName': 'Pierce Gold BCA Assay',
    'author': 'OpentronsAI',
    'description': 'Automated liquid handling for Pierce Gold BCA Protein Assay to determine protein concentrations',
    'source': 'OpentronsAI'
}

requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.25'
}


def run(protocol: protocol_api.ProtocolContext):

    unknown_number = protocol.params.unknown_num
    replicates_number = protocol.params.replicates_num
    ## pickup_excess = protocol.params.pickup_excess

    # Runtime parameter driven pipette mount assignment
    # The 8-channel 1000uL pipette mount is chosen by the user;
    # the 1-channel 50uL pipette automatically takes the opposite mount.
    pipette_8channel_1000_location = protocol.params.pipette_config
    pipette_1channel_50_location = 'left' if pipette_8channel_1000_location == 'right' else 'right'

    # Load trash bin
    trash = protocol.load_trash_bin('A3')

    # Load modules
    thermocycler = protocol.load_module('thermocyclerModuleV2')
    temp_module = protocol.load_module('temperature module gen2', temp_module_location)
    heater_shaker = protocol.load_module('heaterShakerModuleV1', heater_shaker_location)

    # Load labware
    reservoir = protocol.load_labware(protocol.params.well_type, 'D1')
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
    if unknown_number > 16 and replicates_number == 3:
        tiprack200_slots = ["C2", "B3"]
        tiprack200 = [protocol.load_labware(load_name="opentrons_flex_96_tiprack_200ul", location=slot)
                      for slot in tiprack200_slots
                      ]
    else:
        tiprack200_slots = ["B3"]
        tiprack200 = [protocol.load_labware(load_name="opentrons_flex_96_tiprack_200ul", location=slot)
                      for slot in tiprack200_slots
                      ]

    tiprack50 = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'A2')

    # Load pipettes using runtime-parameter-driven mounts
    p50_single = protocol.load_instrument(
        'flex_1channel_50',
        mount=pipette_1channel_50_location,
        tip_racks=[tiprack50]
    )
    p1000_multi = protocol.load_instrument(
        'flex_8channel_1000',
        mount=pipette_8channel_1000_location,
        tip_racks=tiprack200
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
    if protocol.params.well_type == reservoirs[0]:
        # Calculating total reagent needed for v-well reservoir
        total_reagent = (standards_number + unknown_number) * replicates_number * volume_reagent_per_sample + 300

        # Load liquids into labware
        reservoir['A1'].load_liquid(liquid=reagent_a, volume=(total_reagent*50/51+ 300))

    else:
        total_reagent = (standards_number + unknown_number) * replicates_number * volume_reagent_per_sample + 600

        # Load liquids into labware
        reservoir['A1'].load_liquid(liquid=reagent_a, volume=(total_reagent*50/51 + 400))

    # Establishing where the standards will go in the tube rack
    """
    excess_tube = standard_tube_rack['C6']
    
    
    if pickup_excess is True:
        # load empty tube for reagent pick up
        excess_tube.load_liquid(liquid=reagent_a, volume=.1)
    """

    standard_tube_rack['D6'].load_liquid(liquid=reagent_b, volume=(total_reagent / 51) + 30)
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

    protocol.comment('Transferring 10 uL of BSA standards to well plate')

    p50_single.flow_rate.aspirate = 15
    p50_single.flow_rate.dispense = 10

    # Get the replicate destination columns (columns 2, 3, 4, etc.)
    for idx, source in enumerate(standard_sources):
        destinations = get_destination_wells(idx, start_column=0, columns_per_replicate=1)

        p50_single.pick_up_tip(tiprack50)
        p50_single.distribute(
            10,
            source.bottom(1),
            destinations,
            new_tip='never',
            touch_tip=True,
            disposal_volume=0
        )
        p50_single.drop_tip()

    # ===== STEP 2: Microplate Procedure - Transferring Unknowns =============================================

    protocol.comment('Transferring 10uL of unknown samples to well plate')

    for idx, source in enumerate(unknown_sources):
        destinations = get_destination_wells(idx,
                                              start_column=replicates_number,
                                              columns_per_replicate=math.ceil(unknown_number / 8)
                                              )

        p50_single.pick_up_tip(tiprack50)
        p50_single.distribute(
            10,
            source.bottom(1),
            destinations,
            new_tip='never',
            touch_tip=True,
            disposal_volume=0
        )
        p50_single.drop_tip()

    # ===== STEP 3: Prepare BCA Working Reagent ===============================================================
    reagent_a_volume = total_reagent * (50 / 51)  # µL
    reagent_b_volume = total_reagent / 51  # µL

    protocol.comment('Preparing BCA working reagent in reservoir A2')

    # Transfer Reagent A to reservoir A2
    p1000_multi.pick_up_tip()

    p1000_multi.flow_rate.aspirate = 200
    p1000_multi.flow_rate.dispense = 100

    protocol.comment(f'Transferring {round(reagent_a_volume)} uL of Reagent A to reservoir A2.')

    p1000_multi.transfer(
        reagent_a_volume / 8,
        reservoir['A1'].bottom(-0.20),
        reservoir['A2'],
        new_tip='never',
        touch_tip=True
    )

    # Transfer Reagent B to reservoir A2
    protocol.comment(f'Transferring {round(reagent_b_volume)} uL of Reagent B to reservoir A2.')

    res = reservoir['A1'].meniscus(.5)
    reservoir_positions = [res.move(Point(y=10 * i)) for i in range(-3, 4)]
    reservoir_positions.reverse()

    if reagent_b_volume > 150:
        p1000_multi.drop_tip()

        reagent_b_transfer = []

        counts = reagent_b_volume // 200
        remainder = reagent_b_volume % 200

        for i in range(int(counts)):
            reagent_b_transfer.append(200)

        if remainder > 0:
            reagent_b_transfer.append(remainder)

        p1000_multi.configure_nozzle_layout(
            style=SINGLE,
            start='H1',
            tip_racks=tiprack200
        )
        p1000_multi.pick_up_tip(tiprack200[0]['A12'])

        # Reagent B is uniformly distributed across reservoir well A2
        for count in reagent_b_transfer:

            res = reservoir['A2'].bottom(5)
            res_position = [res.move(Point(y=10 * i)) for i in range(-3, 4)]
            p1000_multi.aspirate(count, standard_tube_rack['D6'])
            for position in res_position:
                p1000_multi.dispense((count / 7), position)
            p1000_multi.blow_out(reservoir['A2'].top())

        p1000_multi.drop_tip()

        p1000_multi.configure_nozzle_layout(
            style=ALL,
            tip_racks=tiprack200
        )

        p1000_multi.pick_up_tip()

    else:
        # Reagent B is uniformly distributed across reservoir well A2
        p50_single.pick_up_tip()

        reagent_b_ul = reagent_b_volume
        if reagent_b_ul % 50 != 0:
            transfers_of_b = int(reagent_b_ul // 50 + 1)
        else:
            transfers_of_b = int(reagent_b_ul / 50)
        for transfer in range(transfers_of_b):
            transfer_volume = min(reagent_b_ul, 50)
            p50_single.aspirate(transfer_volume, standard_tube_rack['D6'])
            reagent_b_ul -= 50
            for position in reservoir_positions[:-1]:
                p50_single.dispense(transfer_volume / 7, position)
            p50_single.dispense(transfer_volume / 7, reservoir_positions[-1].move(Point(z=-1)))

        reagent_b_transfer = []

        counts = reagent_b_volume // 50
        remainder = reagent_b_volume % 50

        for i in range(int(counts)):
            reagent_b_transfer.append(50)

        if remainder > 0:
            reagent_b_transfer.append(remainder)

        for count in reagent_b_transfer:
            res = reservoir['A2'].bottom(5)
            res_position = [res.move(Point(y=10 * i)) for i in range(-3, 4)]
            p50_single.aspirate(count, standard_tube_rack['D6'])
            for position in res_position:
                p50_single.dispense((count / 7), position)
            p50_single.blow_out(reservoir['A2'].top())
        p50_single.drop_tip()

    # Mixing reagent A and B
    p1000_multi.mix(1, 200, reservoir['A2'].bottom(2))
    p1000_multi.mix(2, 200 * 0.7, reservoir['A2'].bottom(3))
    p1000_multi.blow_out(reservoir['A2'].top())
    p1000_multi.mix(1, 200 * 0.5, reservoir['A2'].bottom(4))
    p1000_multi.blow_out(reservoir['A2'].top())

    p1000_multi.drop_tip()

    # ===== STEP 4: Adding Working Reagent to Standards ============================================================

    p1000_multi.pick_up_tip()

    p1000_multi.aspirate(200, reservoir['A2'])
    p1000_multi.dispense(200, hs_plate['A1'])
    p1000_multi.blow_out(hs_plate['A1'].top())

    p1000_multi.drop_tip()

    protocol.comment('Transferring 200 uL of working reagent to standard wells.')
    if replicates_number > 1:
        dest_columns_WR = hs_plate.columns()[1:replicates_number]
        p1000_multi.transfer(
            200,
            reservoir['A2'],
            dest_columns_WR,
            blow_out=True,
            blowout_location='destination well',
            new_tip='always',
            touch_tip=True
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

    protocol.comment('Transferring 200 uL of working reagent to unknown wells.')

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
                tip_racks=tiprack200
            )

            for col_offset in range(full_columns_in_replicate):
                dest_col = replicate_start_col + col_offset
                p1000_multi.transfer(
                    200,
                    reservoir['A2'].bottom(0),
                    hs_plate.columns()[dest_col][0],
                    blow_out=True,
                    blowout_location='destination well',
                    touch_tip=True,
                    new_tip='always'
                )

        # Handle partial column
        if remaining_wells_in_replicate > 0 and remaining_wells_in_replicate != 1:
            end_nozzle = nozzle_map[remaining_wells_in_replicate]

            p1000_multi.configure_nozzle_layout(
                style=PARTIAL_COLUMN,
                start='H1',
                end=end_nozzle,
                tip_racks=tiprack200
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
                touch_tip=True,
                new_tip='always'
            )

        # Handle partial column if it is only 1 well for that column
        if remaining_wells_in_replicate == 1:
            end_nozzle = nozzle_map[remaining_wells_in_replicate]

            p1000_multi.configure_nozzle_layout(
                style=SINGLE,
                start='H1',
                tip_racks=tiprack200
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
                touch_tip=True,
                new_tip='always'
            )

    protocol.comment('Working reagent distribution complete')


    # ===== STEP 6: Shake ===============================================================================================
    protocol.comment("Shaking at 825 rpm for 25 seconds")
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
