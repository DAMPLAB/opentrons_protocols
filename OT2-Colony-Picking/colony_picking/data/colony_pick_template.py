# Colony Picking Template Protocol Version 1 for Opentrons Python API Version 2

# Written by Rita Chen 2020-03-18
# Modify by Rita Chen 2020-03-22
# Modify by Rita Chen 2020-03-26
# Modify by Rita Chen 2020-05-20

import math
from opentrons import protocol_api
from opentrons.types import Point

metadata = {
    "apiLevel": "2.8",
    "protocolName": "colony_pick_template_v2",
    "author": "Rita Chen",
    "description": "Perform Colony Picking to rectangular agar plate containing CFU",
}


def run(protocol: protocol_api.ProtocolContext):
    # Load labware, tiprack, and pipettes
    reagent_plate = protocol.load_labware(
        load_name="agilent_1_reservoir_290ml",
        location=4,
        label="Media + Antibiotic",
    )

    culture_block = protocol.load_labware(
        load_name="usascientific_96_wellplate_2.4ml_deep",
        location=1,
        label="Culture Block",
    )

    tiprack_20 = protocol.load_labware(
        load_name="opentrons_96_filtertiprack_20ul",
        location=3,
        label="Filter Tip 20",
    )

    tiprack_200 = protocol.load_labware(
        load_name="opentrons_96_filtertiprack_200ul",
        location=6,
        label="Filter Tip 200",
    )

    p10_s = protocol.load_instrument(
        instrument_name="p10_single",
        mount="right",
        tip_racks=[tiprack_20],
    )

    p300_m = protocol.load_instrument(
        instrument_name="p300_multi_gen2",
        mount="left",
        tip_racks=[tiprack_200],
    )

    # Adding media and antibiotic mixture to each culture block well for reactions with first column being the control column
    agar_plate_contents = culture_blocks_dict[
        "culture_block_0"
    ]  # should be a list of lists

    # Counts for number of reactions
    num_rxns = 0
    for row in agar_plate_contents:
        for colony in row:
            num_rxns += 1

    # Increment num_cols by 1 to include the control column
    num_cols = math.ceil(num_rxns / 8.0) + 1

    # available_deck_slots = ['11', '10', '9', '8', '7', '5', '2']

    #######################Start the Colony Picking protocol####################
    protocol.comment("Begin colony picking protocol!")
    # Turn on robot rail lights
    protocol.set_rail_lights(True)

    # Distribute Media + Antibiotic in Culture Block
    protocol.comment("Begin distributing media and antibiotic!")
    p300_m.pick_up_tip()
    for i in range(0, num_cols):
        reagent = reagent_plate["A1"].bottom(3)
        reactions = [well.bottom(5) for well in culture_block.columns()[i]]
        p300_m.transfer(1500, reagent, reactions, new_tip="never")
    p300_m.drop_tip()
    protocol.pause()

    # Identifies and appends the plasmid names to the list and output Cultural Block Map
    source_plate_names = []
    for block_name, block_map in culture_blocks_dict.items():
        for row in block_map:
            for element in row:
                source_name = element["source"]
                if not source_name in source_plate_names:
                    source_plate_names.append(source_name)

    # Identifies the plasmid names exist in the Cultural Block Map and use this as a reference to pick colonies from the Agar Plate (custom labware)

    # Labware type for point_for_colony_picking doesn't exist in Opentrons Labware Library, user will have to create custom labware for this specific labware
    source_plates = {}
    for name in source_plate_names:
        source_plates[name] = protocol.load_labware(
            load_name="point_for_colony_picking",
            location=2,
            label="Agar Plate Calibrated for Colony Picking",
        )

    # Create a well list for colony picking dispense locations to output the correct culture_block map
    count = 8
    well_list = []
    for i in range(0,(num_cols-1)):
        for j in range(count):
            well_list.append(f"{chr(j + 65)}{i + 2}")

    # Picking colonies from agar plate & placing colonies in culture block
    # Starting at the second column of culture block, the first column (wells 0-7) is a control column -- Media + Antibiotics only
    protocol.comment("Begin picking colony!")
    for block_name, block_map in culture_blocks_dict.items():
        for column in block_map:
            for colony in column:
                p10_s.pick_up_tip()
                x_pos = round(colony["x"], 1)
                y_pos = round(colony["y"], 1)
                z_pos = 3.5  # z-coordinate for the depth of the labware when picking colonies

                # offset the x/y coordinates for reference origin, upper left corner of labware
                off_x = x_pos + 1.0
                off_y = y_pos + 82.0

                p10_s.move_to(
                    protocol.deck.position_for("2").move(Point(off_x, off_y, z_pos))
                )
                # This aspirate ensures that the OT2 app realizes we are actually using this plate (so that it will tell the user to calibrate for it).
                p10_s.aspirate(10)
                p10_s.dispense(10, culture_block[well_list.pop(0)].bottom(5))
                p10_s.mix(2, 10)
                p10_s.blow_out()  
                p10_s.drop_tip()

    protocol.comment("Protocol completed!")
    # Turn off robot rail lights
    protocol.set_rail_lights(False)
