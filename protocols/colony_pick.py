culture_blocks_dict = {"culture_block_0": [[{"name": "2-E0040m_CD-1", "source": "Agar_plate_test", "x": 11.922279082563948, "y": -9.35430426236991}, {"name": "5-E0030m_CD-1", "source": "Agar_plate_test", "x": 20.67726540696941, "y": -18.238595561153435}, {"name": "5-eBFP2_CD-4", "source": "Agar_plate_test", "x": 109.8031176335886, "y": -16.365986100700535}], [{"name": "2-E1010m_CD-1", "source": "Agar_plate_test", "x": 31.86863899681191, "y": -6.577047345641228}, {"name": "5-E1010m_CD-1", "source": "Agar_plate_test", "x": 29.705759190306193, "y": -18.05632518245692}, {"name": "8-E0030m_CD-1", "source": "Agar_plate_test", "x": 22.9960990841049, "y": -26.156427195035512}], [{"name": "2-eBFP2_CD-1", "source": "Agar_plate_test", "x": 38.652097474725636, "y": -6.485983051942361}, {"name": "5-eBFP2_CD-1", "source": "Agar_plate_test", "x": 38.812298578313474, "y": -15.700655466305342}, {"name": "8-E1010m_CD-1", "source": "Agar_plate_test", "x": 31.234566075882363, "y": -28.225983105294116}], [{"name": "2-E0030m_CD-2", "source": "Agar_plate_test", "x": 55.87366515443005, "y": -7.109133758091522}, {"name": "5-E0030m_CD-2", "source": "Agar_plate_test", "x": 57.07774896436387, "y": -17.967113080817427}, {"name": "8-eBFP2_CD-1", "source": "Agar_plate_test", "x": 38.731470232966366, "y": -29.55136677485912}], [{"name": "2-eBFP2_CD-2", "source": "Agar_plate_test", "x": 74.19925270973239, "y": -9.64519057920524}, {"name": "5-E1010m_CD-2", "source": "Agar_plate_test", "x": 65.14720966138688, "y": -18.68881005728397}, {"name": "8-E1010m_CD-2", "source": "Agar_plate_test", "x": 68.85769532598854, "y": -25.3215703202538}], [{"name": "2-E0030m_CD-4", "source": "Agar_plate_test", "x": 93.24939533041481, "y": -9.370748119069134}, {"name": "5-E0040m_CD-4", "source": "Agar_plate_test", "x": 83.68456122278833, "y": -14.932254252042721}, {"name": "8-E0040m_CD-4", "source": "Agar_plate_test", "x": 86.8079253365645, "y": -23.816671844506466}], [{"name": "2-E1010m_CD-4", "source": "Agar_plate_test", "x": 104.30378477993115, "y": -9.617418397594248}, {"name": "5-E0030m_CD-4", "source": "Agar_plate_test", "x": 95.71875028295052, "y": -17.09092004712128}, {"name": "8-E1010m_CD-4", "source": "Agar_plate_test", "x": 101.64420337903454, "y": -25.022767361710798}], [{"name": "2-eBFP2_CD-4", "source": "Agar_plate_test", "x": 114.95078440128883, "y": -8.950104738434062}, {"name": "5-E1010m_CD-4", "source": "Agar_plate_test", "x": 104.71585389382552, "y": -15.541923221148675}, {"name": "8-eBFP2_CD-4", "source": "Agar_plate_test", "x": 112.68077301269405, "y": -24.875921701485947}]]}

# Colony Picking Template Protocol Version 1 for Opentrons Python API Version 2

# Written by Rita Chen 2020-03-18
# Modify by Rita Chen 2020-03-22
# Modify by Rita Chen 2020-03-26

import math
from opentrons import protocol_api
from opentrons.types import Point
#from from opentrons.types import (Point,Location)

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

    # Constants & variables for this protocol
    plate_depth = -4  # How far from the calibration point to move the pipette down when picking colonies.

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

    # Distribute Media + Antibiotic in Culture Block
    # Increment num_cols by 1 to include the control column
    '''
    protocol.comment('Begin distributing media and antibiotic!')
    p300_m.pick_up_tip()
    for i in range(0, (num_cols + 1)):
        reagent = reagent_plate['A1'].bottom(3)
        reactions = [well.bottom(5) for well in culture_block.columns()[i]]
        p300_m.transfer(1500, reagent, reactions, new_tip='never')
    p300_m.drop_tip()
    protocol.pause()
    '''
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
        #--------Version 4 Mistakes--------
        #locations = source_plates['A1'].center()

    # Picking colonies from agar plate & placing colonies in culture block
    # Starting at count = 8 because the first column of culture block (wells 0-7) are controls -- Media + Antibiotics only
    protocol.comment('Begin picking colony!')
    count = 8
    for block_name, block_map in culture_blocks_dict.items():
        for row in block_map:
            for colony in row:
                p10_s.pick_up_tip()
                x_pos = round(colony["x"], 4)
                y_pos = round(colony["y"], 4)
                z_pos = plate_depth

                off_x = x_pos + 3.7
                off_y = y_pos + 83.0

                #--------Option 1--------
                #location = protocol.deck.position_for('2').move(Point(-11.7, 8.9, -3.9)) # Deck coordinate used to calibrate for labware "point_for_colony_picking"
                #adjusted_locations = location.move(Point(x_pos, y_pos, z_pos))
                #p10_s.move_to(adjusted_locations)

                #--------Option 2--------
                #print(source_plates.calibrated_offset)
                #source_plates.set_calibration(Point(-11.7, 8.9, -3.9))
                #print(source_plates.calibrated_offset)
                p10_s.move_to(protocol.deck.position_for('2').move(Point(off_x, off_y, z_pos)))

                #--------Option 3--------
                #location = source_plates.set_calibration(source_plates, Point(-11.7, 8.9, -3.9))
                #adjusted_locations = location.move(source_plates, Point(x_pos, y_pos, z_pos))
                #p10_s.move_to(adjusted_locations)

                #--------Version 4 Mistakes--------
                #Using "locations = source_plates['A1'].center()" as location reference
                #adjusted_locations = locations.move(Point(x_pos, y_pos, z_pos))

                #--------Version 3 Mistakes--------
                #adjusted_locations = Location(Point(x_pos, y_pos, z_pos), source_plates[colony['source']])

                #--------Version 2 Mistakes--------
                #p10_s.move_to(source_plates[colony['source']], Vector([colony['x'], colony['y'], plate_depth]))

                #--------Version 1 Mistakes--------
                #p10.aspirate(10, source_plates[colony['source']].wells(0))
                #robot.move_to((source_plates[colony['source']], Vector([colony['x'], colony['y'], plate_depth])), p10)

                # This aspirate ensures that the OT2 app realizes we are actually using this plate (so that it will tell the user to calibrate for it).
                p10_s.aspirate(10)
                p10_s.dispense(10, culture_block.wells()[count].bottom(5))
                p10_s.mix(3, 10)
                p10_s.drop_tip()
                count += 1

    protocol.comment('Protocol completed!')
    # Turn off robot rail lights
    protocol.set_rail_lights(False)