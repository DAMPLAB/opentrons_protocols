culture_blocks_dict = {"culture_block_0": [[{"name": "2-E0040m_CD-1", "source": "Agar_plate_test", "x": 11.93836632116028, "y": -7.159746248217287}, {"name": "2-E0040m_CD-4", "source": "Agar_plate_test", "x": 83.3217916500889, "y": -10.41684432028171}, {"name": "5-E0030m_CD-2", "source": "Agar_plate_test", "x": 58.23551675068854, "y": -17.631905579673475}, {"name": "8-E0040m_CD-2", "source": "Agar_plate_test", "x": 47.61374288881535, "y": -25.81679039227033}], [{"name": "2-E0030m_CD-1", "source": "Agar_plate_test", "x": 18.71359396554928, "y": -9.321270132209403}, {"name": "2-E0030m_CD-4", "source": "Agar_plate_test", "x": 96.69708317502116, "y": -7.905298162352176}, {"name": "5-E1010m_CD-2", "source": "Agar_plate_test", "x": 65.43068275739718, "y": -19.560476641574144}, {"name": "8-E0030m_CD-2", "source": "Agar_plate_test", "x": 60.226121526900315, "y": -27.394171636534313}], [{"name": "2-E1010m_CD-1", "source": "Agar_plate_test", "x": 32.40317807448553, "y": -10.481691711265505}, {"name": "2-eBFP2_CD-4", "source": "Agar_plate_test", "x": 114.12589200806389, "y": -9.631446921655305}, {"name": "5-E0040m_CD-4", "source": "Agar_plate_test", "x": 83.27365529466547, "y": -20.146773584794857}, {"name": "8-E0040m_CD-4", "source": "Agar_plate_test", "x": 87.40847505023451, "y": -23.800369692668173}], [{"name": "2-eBFP2_CD-1", "source": "Agar_plate_test", "x": 36.97592163689536, "y": -7.833566725596249}, {"name": "5-E0040m_CD-1", "source": "Agar_plate_test", "x": 15.501117501164241, "y": -18.2420607156744}, {"name": "5-E0030m_CD-4", "source": "Agar_plate_test", "x": 96.92258150552391, "y": -16.68565494858859}, {"name": "8-E1010m_CD-4", "source": "Agar_plate_test", "x": 104.58104765486232, "y": -25.458385740613924}], [{"name": "2-E0040m_CD-2", "source": "Agar_plate_test", "x": 50.11903681006354, "y": -6.94272243342458}, {"name": "5-E0030m_CD-1", "source": "Agar_plate_test", "x": 23.308175159312785, "y": -20.866647224583257}, {"name": "5-E1010m_CD-4", "source": "Agar_plate_test", "x": 104.95413418327931, "y": -16.477856527785907}], [{"name": "2-E0030m_CD-2", "source": "Agar_plate_test", "x": 60.156996352980045, "y": -8.918634380817354}, {"name": "5-E1010m_CD-1", "source": "Agar_plate_test", "x": 29.237536507726478, "y": -19.792070030944664}, {"name": "5-eBFP2_CD-4", "source": "Agar_plate_test", "x": 114.64983269634389, "y": -16.111652153845863}], [{"name": "2-E1010m_CD-2", "source": "Agar_plate_test", "x": 68.22402891596478, "y": -5.904395379007679}, {"name": "5-eBFP2_CD-1", "source": "Agar_plate_test", "x": 41.15357595901072, "y": -21.121690127931874}, {"name": "8-E0030m_CD-1", "source": "Agar_plate_test", "x": 25.327519397491038, "y": -27.83815870208244}], [{"name": "2-eBFP2_CD-2", "source": "Agar_plate_test", "x": 77.58610769991762, "y": -10.829469408661325}, {"name": "5-E0040m_CD-2", "source": "Agar_plate_test", "x": 50.93740791458196, "y": -19.578460425229647}, {"name": "8-eBFP2_CD-1", "source": "Agar_plate_test", "x": 40.92906357515603, "y": -29.15338646361533}]]}

# Colony Picking Template Protocol Version 1 for Opentrons Python API Version 2

# Written by Rita Chen 2020-03-18
# Modify by Rita Chen 2020-03-22
# Modify by Rita Chen 2020-03-26

import math
from opentrons import protocol_api
from opentrons.types import Point

metadata = {'apiLevel': '2.8',
            'protocolName': 'colony_pick_template_v2',
            'author': 'Rita Chen',
            'description': 'Perform Colony Picking to rectangular agar plate containing CFU'}


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
    agar_plate_contents = culture_blocks_dict['culture_block_0']  # should be a list of lists

    # Counts for number of reactions
    num_rxns = 0
    for row in agar_plate_contents:
        for colony in row:
            num_rxns += 1
    num_cols = math.ceil(num_rxns/8.0)

    #available_deck_slots = ['11', '10', '9', '8', '7', '5', '2']

    #######################Start the Colony Picking protocol####################
    protocol.comment('Begin colony picking protocol!')
    # Turn on robot rail lights
    protocol.set_rail_lights(True)

    # Identifies and appends the plasmid names to the list and output Cultural Block Map
    source_plate_names = []
    for block_name, block_map in culture_blocks_dict.items():
        for row in block_map:
            for element in row:
                source_name = element['source']
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

    # Picking colonies from agar plate & placing colonies in culture block
    # Starting at count = 8 because the first column of culture block (wells 0-7) are controls -- Media + Antibiotics only
    protocol.comment('Begin picking colony!')
    count = 8
    for block_name, block_map in culture_blocks_dict.items():
        for column in block_map:
            for colony in column:
                p10_s.pick_up_tip()
                x_pos = round(colony["x"], 1)
                y_pos = round(colony["y"], 1)
                z_pos = 3 # z-coordinate for the depth of the labware when picking colonies

                # offset the x/y coordinates for reference origin, upper left corner of labware
                off_x = x_pos + 1.0
                off_y = y_pos + 82.0

                p10_s.move_to(protocol.deck.position_for('2').move(Point(off_x, off_y, z_pos)))
                # This aspirate ensures that the OT2 app realizes we are actually using this plate (so that it will tell the user to calibrate for it).
                p10_s.aspirate(10)
                p10_s.dispense(10, culture_block.wells()[count].bottom(5))
                p10_s.mix(2, 10)
                p10_s.drop_tip()
                count += 1

    protocol.comment('Protocol completed!')
    # Turn off robot rail lights
    protocol.set_rail_lights(False)
