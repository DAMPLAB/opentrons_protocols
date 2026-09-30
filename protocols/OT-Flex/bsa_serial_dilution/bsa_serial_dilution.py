from opentrons import protocol_api


#Change module deck location base on your own setup
temp_module_location = 'C3'
heater_shaker_location = 'C1'

#Change pipette location base on your own setup ('left' or 'right')
pipette_1channel_1000_location = 'right'


metadata = {
    'protocolName': 'BSA Serial Dilution in Duplicate',
    'description': 'Serial dilution of BSA stock in duplicate in 1.5mL tubes with three calibrations'
}

requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.25'
}

def run(protocol: protocol_api.ProtocolContext):
    # Load modules
    thermocycler = protocol.load_module('thermocyclerModuleV2')
    heater_shaker = protocol.load_module('heaterShakerModuleV1', 'heater_shaker_location')
    temp_module = protocol.load_module('temperature module gen2', 'temp_module_location')
    
    # Load trash bin
    trash = protocol.load_trash_bin('A3')
    
    # Load labware
    tube_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', 'D2')
    water_reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 'D3')
    
    # Load tip rack
    tiprack1000 = protocol.load_labware('opentrons_flex_96_tiprack_1000ul', 'B2')
    tiprack200 = protocol.load_labware('opentrons_flex_96_tiprack_200ul', 'B3')
    tiprack50 = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'A2')

    # Load pipette
    p1000_single = protocol.load_instrument('flex_1channel_1000', pipette_1channel_1000_location, tip_racks=[tiprack200, tiprack50, tiprack1000])
    
    # Define wells
    # BSA stock is in D1 (bottom first row)
    bsa_stock = protocol.define_liquid(
        name='BSA stock',
        display_color='#00FF00')
    tube_rack['D1'].load_liquid(liquid=bsa_stock, volume=400)


    water = protocol.define_liquid(
        name='Water stock',
        display_color="#407FF3")
    water_reservoir['A1'].load_liquid(liquid=water, volume=10000)


    # Blanks (A6 and B6)
    blank_a = tube_rack['A6']
    blank_b = tube_rack['B6']
    
    # ========================= STEP 1: Adding Water =======================================================
    protocol.comment('Step 1: Adding water to tubes')

    p1000_single.flow_rate.aspirate = 400
    p1000_single.flow_rate.dispense = 400
    
    # Pick up tip once for all water additions
    p1000_single.pick_up_tip(tiprack1000)
    
    # Add 200 µL water to calibration tube 1 & 2 (A1, A2, B1, B2)
    protocol.comment('Distributing 200 uL of water to tube A1, A2, B1 and B2')
    p1000_single.distribute(
        200,
        water_reservoir['A1'],
        [tube_rack['A1'], tube_rack['A2'], tube_rack['B1'], tube_rack['B2']],
        disposal_volume = 0,
        touch_tip = True,
        new_tip = 'never'
    )
    
    protocol.comment('Distributing 180 uL of water to tube A3 and B3')
    # Add 180 µL water to A3 and B3
    p1000_single.distribute(
        180,
        water_reservoir['A1'],
        [tube_rack['A3'], tube_rack['B3']],
        disposal_volume = 0,
        touch_tip = True,
        new_tip = 'never'
    )
    
    p1000_single.flow_rate.aspirate = 700
    p1000_single.flow_rate.dispense = 700 

    protocol.comment('Distributing 1000 uL of water to tube A6 and B6 (blanks)')
    # Add 1000 µL water to A6 and B6 (blanks)
    p1000_single.transfer(
        1000,
        water_reservoir['A1'],
        [blank_a, blank_b],
        touch_tip = True,
        new_tip = 'never',
    )

    p1000_single.drop_tip()

    # ========================= STEP 2: Adding BSA Stock and Performing Serial Dilution=======================================================
    protocol.comment('Step 2: Adding BSA stock to tubes')

    row = ['A', 'B']

    for i in row:
        protocol.comment(f"Performing serial dilution for row {i}, adding 200 uL of BSA stock to the first tube")

        p1000_single.flow_rate.aspirate = 250
        p1000_single.flow_rate.dispense = 130 

        p1000_single.pick_up_tip(tiprack200)
        p1000_single.mix(3, 200, tube_rack['D1'], dispense_flow_rate = 200)  # Mix 3 times with 200 µL
        p1000_single.blow_out(tube_rack['D1'].top())
        p1000_single.aspirate(200, tube_rack['D1'])
        p1000_single.dispense(200, tube_rack[f'{i}1'])
        p1000_single.mix(2, 200, tube_rack[f'{i}1'].bottom(2), dispense_flow_rate = 200)  # Mix 3 times with 200 µL
        p1000_single.mix(1, 200, tube_rack[f'{i}1'].bottom(4), dispense_flow_rate = 200)
        p1000_single.blow_out(tube_rack[f'{i}1'].top())
        p1000_single.drop_tip()
 
        protocol.comment(f"Performing serial dilution for row {i}, adding 200 uL of BSA stock to the second tube")
        # Transfer 200 µL from calibration tube 1 (A1) to calibration tube 2 (A2)
        p1000_single.pick_up_tip(tiprack200)
        p1000_single.mix(3, 200, tube_rack[f'{i}1'], dispense_flow_rate = 200)
        p1000_single.blow_out(tube_rack[f'{i}1'].top())
        p1000_single.aspirate(200, tube_rack[f'{i}1'])
        p1000_single.dispense(200, tube_rack[f'{i}2'])
        p1000_single.mix(2, 200, tube_rack[f'{i}2'].bottom(2), dispense_flow_rate = 200)  # Mix 3 times with 200 µL
        p1000_single.mix(1, 200, tube_rack[f'{i}2'].bottom(4), dispense_flow_rate = 200)
        p1000_single.blow_out(tube_rack[f'{i}2'].top())
        p1000_single.drop_tip()
        
        # Transfer 20 µL from calibration tube 2 (A2) to calibration tube 3 (A3)
        p1000_single.flow_rate.aspirate = 25
        p1000_single.flow_rate.dispense = 10

        protocol.comment(f"Performing serial dilution for row {i}, adding 20 uL of BSA stock to the third tube")
        p1000_single.pick_up_tip(tiprack50)
        p1000_single.aspirate(20, tube_rack[f'{i}2'])
        p1000_single.dispense(20, tube_rack[f'{i}3'])
        p1000_single.drop_tip()

    protocol.comment("Serial dilution complete")
