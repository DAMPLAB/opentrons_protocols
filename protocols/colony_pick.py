"""
--------------------------------------------------------------------------------
Description: Colony Picking Template Protocol Version 2 for Opentrons
Python API Version 2

Roadmap:

Written by Rita Chen, DAMP Lab 2020-03-22
--------------------------------------------------------------------------------
"""
# TODO: We should find a way to put deck layouts in this repository.

import math
from opentrons import protocol_api
from opentrons.types import (
    Point,
    Location,
)
import yaml

# TODO: This is the load for the culture block dict. We should probably pass it
# in as a better argument, but this is an exercise left to the reader.
with open("example_colony_positions.yml", "r") as input_file:
    culture_blocks_dict = yaml.load(input_file, Loader=yaml.SafeLoader)

metadata = {
    "apiLevel": "2.8",
    "protocolName": "colony_pick_template_v2",
    "author": "Rita Chen",
    "description": "Perform Colony Picking to rectangular agar plate containing " "CFU",
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
    # Constants & variables for this protocol
    # How far from the calibration point to move the pipette down when picking
    # colonies.
    PLATE_DEPTH = -7

    # Adding media and antibiotic mixture to each culture block well for
    # reactions with first column being the control column
    agar_plate_contents = culture_blocks_dict[
        "culture_block_0"
    ]  # should be a list of lists

    # Counts for number of reactions

    num_rxns = 0 #

    for row in agar_plate_contents:

        for colony in row:
            num_rxns += 1

    num_cols = math.ceil(num_rxns / 8.0)

    # available_deck_slots = ['11', '10', '9', '8', '7', '5', '2']

    #######################Start the Colony Picking protocol####################

    protocol.comment("Begin colony picking protocol!")

    # Turn on robot rail lights

    protocol.set_rail_lights(True)

    # Distribute Media + Antibiotic in Culture Block
    # Increment num_cols by 1 to include the control column
    protocol.comment("Begin distributing media and antibiotic!")

    p300_m.pick_up_tip()

    for i in range(0, (num_cols + 1)):
        reagent = reagent_plate["A1"].bottom()
        reactions = [well.bottom(2) for well in culture_block.columns()[i]]
        p300_m.transfer(1500, reagent, reactions, mix_before=(2, 150), new_tip="never")
    p300_m.drop_tip()
    # Identifies and appends the plasmid names to the list and output Cultural Block Map
    source_plate_names = []
    for block_name, block_map in culture_blocks_dict.items():
        for row in block_map:
            for element in row:
                source_name = element["source"]
                if source_name not in source_plate_names:
                    source_plate_names.append(source_name)

    # Identifies the plasmid names exist in the Cultural Block Map and use this
    # as a reference to pick colonies from  the Agar Plate (custom labware)

    # Labware type for point_for_colony_picking doesn't exist in Opentrons
    # Labware Library, user will have to create  custom labware for this
    # specific labware

    source_plates = {}

    for name in source_plate_names:
        source_plates[name] = protocol.load_labware(
            load_name="point_for_colony_picking",
            location=2,
            label="Agar Plate Calibrated for Colony Picking",
        )
        locations = source_plates[name]["A1"].center()

    # Picking colonies from agar plate & placing colonies in culture block
    # Starting at count = 8 because the first column of culture block (wells 0-7) are controls -- Media + Antibiotics
    # only
    protocol.comment("Begin picking colony!")
    count = 8

    for block_name, block_map in culture_blocks_dict.items():
        for row in block_map:
            for colony in row:
                p10_s.pick_up_tip()
                x_pos = round(colony["x"], 4)
                y_pos = round(colony["y"], 4)
                z_pos = PLATE_DEPTH
                adjusted_location = Location(Point(x_pos, y_pos, z_pos), culture_block)
                p10_s.move_to(adjusted_location)
                # p10_s.move_to(source_plates[colony['source']], Vector([colony['x'], colony['y'], PLATE_DEPTH]))
                # This aspirate ensures that the OT2 app realizes we are actually using this plate (so that it will
                # tell the user to calibrate for it).
                p10_s.aspirate(10)
                positions = [well.bottom(5) for well in culture_block.columns()[count]]
                p10_s.dispense(10, positions, mix_after=(3, 10))
                p10_s.drop_tip()
                count += 1

    protocol.comment("Protocol completed!")
    # Turn off robot rail lights
    protocol.set_rail_lights(False)
