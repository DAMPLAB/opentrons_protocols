from opentrons import protocol_api

# Edit the numbers here to suit your needs
bacteria_number = 8 # up to 32 (keep to multiples of 8 for the multichannel pipette)

#Enter 1 for manual pelleting and resuspending bacterias in tubes
#Enter 2 for manual pelleting bacterias in deep wellplate and automated resuspension step
resuspension = 2

#Change module location base on your own setup
temp_module_location = 'C3'
heater_shaker_location = 'C1'

#Change pipette location base on your own setup ('left' or 'right')
pipette_8channel_1000_location = 'right'


metadata = {
    'protocolName': 'Promega Miniprep Draft',
    'description': 'Automated miniprep protocol using the promega magnesil kit'
}

requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.25'
}


def run(protocol: protocol_api.ProtocolContext):
    # Load trash bin
    trash = protocol.load_trash_bin('A3')

    # Load modules
    thermocycler = protocol.load_module('thermocyclerModuleV2')
    temp_module = protocol.load_module('temperature module gen2', temp_module_location)
    heater_shaker = protocol.load_module('heaterShakerModuleV1', heater_shaker_location)

    # Load labware
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 'D3')

    # Load heater shaker adapter
    hs_adapter = heater_shaker.load_adapter("opentrons_universal_flat_adapter")

    # Load labware on heater shaker adapter
    deep_wellplate_1 = hs_adapter.load_labware(
        "greiner_96_wellplate_2000ul"
    )

    deep_wellplate_2 = protocol.load_labware("greiner_96_wellplate_2000ul", 'D2')

    #Load magnetic block
    mag_block = protocol.load_module("magneticBlockV1", "D1")

    # Load tip racks for all operations
    tiprack1000 = protocol.load_labware('opentrons_flex_96_tiprack_1000ul', 'A2')

    tiprack200_slots = ["B2","C2"]
    tiprack200 = [protocol.load_labware(load_name="opentrons_flex_96_tiprack_200ul", location=slot) 
                  for slot in tiprack200_slots
                  ]
    
    tiprack50 = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'B3')

    # Load pipettes
    p1000_multi = protocol.load_instrument(
        'flex_8channel_1000',
        mount= pipette_8channel_1000_location,
        tip_racks= tiprack200 + [tiprack50, tiprack1000]
    )

    # Define liquids
    bacterial_culture = protocol.define_liquid(
        name='Bacterial culture',
        display_color="#353434"
    )
    lysis_solution = protocol.define_liquid(
        name='Cell lysis solution',
        display_color="#73D3BB"
    )
    neutralization_solution = protocol.define_liquid(
        name='neutralization_solution',
        display_color='#FFFF00'
    )
    magnesil_blue = protocol.define_liquid(
        name='Magnesil Blue',
        display_color="#3A93E6"
    )
    magnesil_red = protocol.define_liquid(
        name='Magnesil Red',
        display_color="#CC2121"
    )

    elution_buffer = protocol.define_liquid(
        name='Elution Buffer',
        display_color="#913FFC"
    )

    ethanol = protocol.define_liquid(
        name='80 percent Ethanol',
        display_color="#D6D6D6"
    )

    wash = protocol.define_liquid(
        name='4/40 wash',
        display_color="#8AA1A7"
    )

    isopropanol = protocol.define_liquid(
        name='Isopropanol',
        display_color="#463535"
    )

    # Load liquids into labware
    reservoir['A1'].load_liquid(liquid=lysis_solution, volume=(120*bacteria_number)+150)
    reservoir['A2'].load_liquid(liquid=neutralization_solution, volume=(120*bacteria_number)+150)
    reservoir['A3'].load_liquid(liquid=magnesil_blue, volume=(25*bacteria_number)+100)
    reservoir['A4'].load_liquid(liquid=magnesil_red, volume=(50*bacteria_number)+100)
    reservoir['A5'].load_liquid(liquid=wash, volume=(100*bacteria_number)+150)
    reservoir['A6'].load_liquid(liquid=ethanol, volume=(200*bacteria_number)+150)
    reservoir['A7'].load_liquid(liquid=elution_buffer, volume=(100*bacteria_number)+150)
    reservoir['A8'].load_liquid(liquid=isopropanol, volume=(350*bacteria_number)+150)

    # Establishing where the bacteria culture will go in the deep well plate
    bacteria_location = deep_wellplate_1.wells()[:bacteria_number]
    # Load bacterial culture into the deep well plate
    for well in bacteria_location:
        well.load_liquid(liquid=bacterial_culture, volume=150)

    # Determining where the 8-channel pipette will go
    location_1 = []
    for i in range(int(bacteria_number / 8)):
        location_1.append(8 * i)

    location_2 = []
    for i in location_1:
        location_2.append(i+bacteria_number)

    location_3 = []
    for i in location_1:
        location_3.append(i+(bacteria_number*2))


    # Define viscous liquid class
    viscous_liquid = protocol.get_liquid_class(name="glycerol_50")
    custom_viscous_properties = viscous_liquid.get_for(p1000_multi, tiprack50)

    # Change aspirate height for viscous liquid class
    custom_viscous_properties.aspirate.aspirate_position = {
    "position_reference": "well-bottom",
    "offset": {"x": 0, "y": 0, "z": -0.48}
    }

    # Enable different flow rate for different volume for viscous liquid
    for (custom_viscous_aspirate_volume, custom_viscous_flow_rate) in [[25.0, 18.0], [50.0, 30.0]]:
        custom_viscous_properties.aspirate.flow_rate_by_volume.set_for_volume(custom_viscous_aspirate_volume, custom_viscous_flow_rate)
    
    # Enable mixing BEFORE aspirate for viscous liquid
    custom_viscous_properties.aspirate.mix.enabled = True
    custom_viscous_properties.aspirate.mix.repetitions = 2  # Mix 3 times
    custom_viscous_properties.aspirate.mix.volume = 25      
    
    # Enable mixing AFTER dispense for viscous liquid
    custom_viscous_properties.dispense.mix.enabled = True
    custom_viscous_properties.dispense.mix.repetitions = 2  # Mix 3 times
    custom_viscous_properties.dispense.mix.volume = 40


    # Define volatile liquid class
    volatile_liquid = protocol.get_liquid_class(name="ethanol_80")
    custom_volatile_properties = volatile_liquid.get_for(p1000_multi, "opentrons/opentrons_flex_96_tiprack_200ul/1")

    # Change aspirate height for volatile liquid class
    custom_volatile_properties.aspirate.aspirate_position = {
    "position_reference": "well-bottom",
    "offset": {"x": 0, "y": 0, "z": -0.4}
    }

    # Change dispense height for volatile liquid class
    custom_volatile_properties.dispense.dispense_position = {
    "position_reference": "well-top",
    "offset": {"x": 0, "y": 0, "z": -3}
    }

    custom_volatile_properties2 = volatile_liquid.get_for(p1000_multi, tiprack1000)

    # Change aspirate height for volatile liquid class
    custom_volatile_properties2.aspirate.aspirate_position = {
    "position_reference": "well-bottom",
    "offset": {"x": 0, "y": 0, "z": -0.4}
    }

    # Change dispense height for volatile liquid class
    custom_volatile_properties2.dispense.dispense_position = {
    "position_reference": "well-top",
    "offset": {"x": 0, "y": 0, "z": -3}
    }
    
    # ========================= STEP 1: Cell Resuspension, Lysis and Lysate Clearing=======================================================

    # Close heater shaker latch
    heater_shaker.close_labware_latch()

    if resuspension == 2:
        p1000_multi.flow_rate.aspirate = 60
        p1000_multi.flow_rate.dispense = 80

        resuspension_solution = protocol.define_liquid(
            name='Resuspension solution',
            display_color="#1E3C5E"
        )
        reservoir['A9'].load_liquid(liquid=resuspension_solution, volume=(90*bacteria_number)+100)
        
        protocol.comment('Adding 90 uL of resuspension solution to the lysis row in deep wellplate 1')

        resuspension_dest_bottom = [deep_wellplate_1.wells()[well].bottom(2) for well in location_1]
        p1000_multi.distribute(
            90,
            reservoir['A9'].bottom(-0.40),
            resuspension_dest_bottom,
            touch_tip=True,
            new_tip='always',
            disposal_volume=0,
            mix_after = (3, 100),
            tip_racks = [tiprack200]
        )

        protocol.comment('Shaking at 1800 rpm for 3 minute')

        #heater_shaker.set_and_wait_for_shake_speed(1800)  # Set rpm
        #protocol.delay(minutes=3)  # Shake for 3 minutes

        # Stop shaking
        #heater_shaker.deactivate_shaker()
    
    p1000_multi.flow_rate.aspirate = 100
    p1000_multi.flow_rate.dispense = 100

    lysis_dest_top = [deep_wellplate_1.wells()[well].top(-4) for well in location_1]

    protocol.comment('Adding 120 uL of lysis solution to the lysis row in deep wellplate 1')

    p1000_multi.distribute(
        120,
        reservoir['A1'].bottom(-0.40),
        lysis_dest_top,
        touch_tip=True,
        new_tip='once',
        disposal_volume=0,
        tip_racks = [tiprack200]
        )
    
    protocol.comment('Shaking at 1800 rpm for 1 minute')

    #heater_shaker.set_and_wait_for_shake_speed(1800)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minutes

    # Stop shaking
    #heater_shaker.deactivate_shaker()

    protocol.comment('Adding 120 uL of neutralization solution to the lysis row in deep wellplate 1')
    
    p1000_multi.distribute( 
        120,
        reservoir['A2'].bottom(-0.40),
        lysis_dest_top,
        touch_tip=True,
        new_tip='once',
        disposal_volume=0,
        tip_racks = [tiprack200]
        )

    protocol.comment('Shaking at 1800 rpm for 1 minute')
    #heater_shaker.set_and_wait_for_shake_speed(1800)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minutes

    # Stop shaking
    #heater_shaker.deactivate_shaker()

    lysis_dest = [deep_wellplate_1.wells()[well] for well in location_1]

    protocol.comment('Adding 25 uL of magnesil blue to the lysis row in deep wellplate 1')
    p1000_multi.distribute_with_liquid_class(
        liquid_class = viscous_liquid,
        volume = 25,
        source = reservoir['A3'],
        dest = lysis_dest,
        new_tip='always',
        tip_racks = [tiprack50]
    )

    #Determining where the 8-channel pipette will go in the binding plate
    binding_dest = [deep_wellplate_1.wells()[well] for well in location_3]

    protocol.comment('Adding 50 uL of magnesil red to the binding row in deep wellplate 1')
    p1000_multi.distribute_with_liquid_class(
        liquid_class = viscous_liquid,
        volume = 50,
        source = reservoir['A4'],
        dest = binding_dest,
        new_tip='always',
        tip_racks = [tiprack50]
        )
    
    p1000_multi.flow_rate.aspirate = 300
    p1000_multi.flow_rate.dispense = 250

    heater_shaker.close_labware_latch()
    protocol.comment('Shaking at 1200 for 1 minute')
    #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minute
    # Stop shaking
    #heater_shaker.deactivate_shaker()
    heater_shaker.open_labware_latch()

    protocol.comment('Moving deep wellplate 1 from heater shaker to magnetic block')
    protocol.move_labware(
        labware=deep_wellplate_1,
        new_location=mag_block, 
        use_gripper=True,  
        drop_offset={"x": 0, 'y': 0, 'z': -12.5}    
    )

    protocol.comment('Waiting for 3 minutes for pellets to form')
    #protocol.delay(minutes=2.5)

    binding_dest = [deep_wellplate_1.wells()[well] for well in location_3]

    protocol.comment('Adding 350 uL isopropanol to the binding row in deep wellplate 1')
    p1000_multi.pick_up_tip(tiprack1000)
    p1000_multi.distribute_with_liquid_class(
        liquid_class=volatile_liquid,
        volume=350,
        source=reservoir['A8'],
        dest=binding_dest,
        new_tip='never',
        tip_racks = [tiprack1000]
    )
    p1000_multi.drop_tip()

    lysis_dest_bottom = [deep_wellplate_1.wells()[well].bottom(3) for well in location_1]
    clearing_dest_top = [deep_wellplate_1.wells()[well].top(-5) for well in location_2]

    protocol.comment('Adding 400 uL of neutralized lysis from lysis row to the clearing row in deep wellplate 1')
    for src, dest in zip(lysis_dest_bottom, clearing_dest_top):
       p1000_multi.pick_up_tip(tiprack1000)
       p1000_multi.transfer(
           400,
           src,
           dest,
           touch_tip=True,
           new_tip = 'never'
        )
       p1000_multi.drop_tip()
    
    protocol.comment('Delaying for 2 minutes to allow the magnetized pellet to form')
    #protocol.delay(minutes=2)  # delay 2 minutes

    # ========================= STEP 2: DNA Binding =======================================================
    
    p1000_multi.flow_rate.aspirate = 300
    p1000_multi.flow_rate.dispense = 300

    clearing_dest_bottom = [deep_wellplate_1.wells()[well].bottom(3) for well in location_2]
    binding_dest = [deep_wellplate_1.wells()[well] for well in location_3]

    protocol.comment('Adding 400 uL of the clear lysate to the binding row in deep wellplate 1')
    for src, dest in zip(clearing_dest_bottom, binding_dest):
       p1000_multi.pick_up_tip(tiprack1000)
       p1000_multi.transfer(
           400,
           src,
           dest,
           touch_tip=True,
           new_tip='never',
           tip_racks = [tiprack1000]
       )
       p1000_multi.drop_tip()

    protocol.comment('Moving deep wellplate 1 from the magnetic block to the heater shaker')
    protocol.move_labware(
        deep_wellplate_1,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -5}
    ) 

    heater_shaker.close_labware_latch()

    protocol.comment('Shaking at 1200 rpm for 15 minutes')
    #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    #protocol.delay(minutes=15)  # Shake for 15 minutes

    # Stop shaking
    #heater_shaker.deactivate_shaker()
    heater_shaker.open_labware_latch()

    protocol.comment('Moving deep wellplate 1 from heater shaker to magnetic block')
    protocol.move_labware(
        labware=deep_wellplate_1,
        new_location=mag_block, 
        use_gripper=True,  
        drop_offset={"x": 0, 'y': 0, 'z': -12.5}    
    )  

    #protocol.delay(minutes=3)  # Wait for 3 minutes to allow the magnetized pellet to form

    binding_dest_supernatant_removal = [deep_wellplate_1.wells()[well].bottom(3) for well in location_3]

    p1000_multi.flow_rate.aspirate = 700
    p1000_multi.flow_rate.dispense = 700

    protocol.comment('Removing supernatant from the binding row in deep wellplate 1')

    if bacteria_number>24:
        protocol.pause("Please replenish 1000 uL tiprack at deck A2.")
        p1000_multi.reset_tipracks()  # Reset tip tracking
    
    for well in binding_dest_supernatant_removal:
        p1000_multi.pick_up_tip(tiprack1000)
        p1000_multi.transfer(
            650,
            well,
            reservoir['A12'].bottom(-0.2),
            new_tip = 'never',
            tip_rack = [tiprack1000]
        )
        p1000_multi.drop_tip()

    # ========================= STEP 3: Washing =======================================================
    
    protocol.comment('Moving deep wellplate 1 from magnetic block to heater shaker')
    protocol.move_labware(
        deep_wellplate_1,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -5}
    ) 

    heater_shaker.close_labware_latch()

    binding_dest_top = [deep_wellplate_1.wells()[well].top(-3) for well in location_3]

    p1000_multi.flow_rate.aspirate = 100
    p1000_multi.flow_rate.dispense = 100

    protocol.comment('Adding 100 uL wash into the binding row in deep wellplate 1')
    p1000_multi.distribute(
        100,
        reservoir['A5'].bottom(-0.4),
        binding_dest_top,
        new_tip = 'once',
        disposal_volume = 0,
        touch_tip = True,
        tip_racks = tiprack200
    )

    protocol.comment('Shaking at 1800 rpm for 1 minute')
    #heater_shaker.set_and_wait_for_shake_speed(1800)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minute

    # Stop shaking
    #heater_shaker.deactivate_shaker()
    heater_shaker.open_labware_latch()

    protocol.comment('Moving deep wellplate 1 from heater shaker to magnetic block')
    protocol.move_labware(
        labware=deep_wellplate_1,
        new_location=mag_block, 
        use_gripper=True,  
        drop_offset={"x": 0, 'y': 0, 'z': -12.5}    
    )

    #protocol.delay(minutes=1)  # Shake for 1 minute

    binding_dest_supernatant_removal = [deep_wellplate_1.wells()[well].bottom(2.5) for well in location_3]

    protocol.comment('Removing ~100uL wash from the binding row in deep wellplate 1')
    p1000_multi.consolidate(
        90,
        binding_dest_supernatant_removal,
        reservoir['A12'],
        new_tip = 'always',
        tip_racks = tiprack200
    )

    heater_shaker.open_labware_latch()

    protocol.comment('Moving deep wellplate 1 from magnetic block to heater shaker')
    protocol.move_labware(
        deep_wellplate_1,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -5}
    ) 
    
    heater_shaker.close_labware_latch()

    binding_dest = [deep_wellplate_1.wells()[well] for well in location_3]

    protocol.comment('Adding 100 uL 80 percent ethanol to the binding row in deep wellplate 1')

    p1000_multi.distribute_with_liquid_class(
        liquid_class=volatile_liquid,
        volume=100,
        source=reservoir['A6'],
        dest=binding_dest,
        new_tip='once'
    )

    protocol.comment('Shaking at 1600 rpm for 1 minute') 
    #heater_shaker.set_and_wait_for_shake_speed(1600)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minute
    heater_shaker.open_labware_latch()

    protocol.comment('Moving deep wellplate 1 from heater shaker to magnetic block')
    protocol.move_labware(
        labware=deep_wellplate_1,
        new_location=mag_block, 
        use_gripper=True,  
        drop_offset={"x": 0, 'y': 0, 'z': -12.5}    
    )

    #protocol.delay(minutes=1)  # Allow pellet to form for 1 minute

    protocol.comment('Removing ~100uL spent ethanol from the binding row in deep wellplate 1')

    binding_dest_supernatant_removal = [deep_wellplate_1.wells()[well].bottom(2) for well in location_3]

    p1000_multi.consolidate(
        100,
        binding_dest_supernatant_removal,
        reservoir['A11'],
        new_tip= 'always',
        tip_racks = [tiprack200]
    )

    protocol.comment('Moving deep wellplate 1 from magnetic block to heater shaker')
    protocol.move_labware(
        deep_wellplate_1,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -5}
    ) 

    heater_shaker.close_labware_latch()

    binding_dest = [deep_wellplate_1.wells()[well] for well in location_3]

    protocol.comment('Adding 100 uL 80 percent ethanol to the binding row in deep wellplate 1')

    p1000_multi.distribute_with_liquid_class(
        liquid_class=volatile_liquid,
        volume=100,
        source=reservoir['A6'],
        dest=binding_dest,
        new_tip='once'
    )

    protocol.comment('Shaking at 1200 rpm for 1 minute') 
    #heater_shaker.set_and_wait_for_shake_speed(1600)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minute
    heater_shaker.open_labware_latch()

    protocol.comment('Moving deep wellplate 1 from heater shaker to magnetic block')
    protocol.move_labware(
        labware=deep_wellplate_1,
        new_location=mag_block, 
        use_gripper=True,  
        drop_offset={"x": 0, 'y': 0, 'z': -12.5}    
    )

    #protocol.delay(minutes=1)  # Allow pellet to form for 1 minute

    protocol.comment('Removing ~100uL spent ethanol from the binding row in deep wellplate 1')

    binding_dest_supernatant_removal = [deep_wellplate_1.wells()[well].bottom(2) for well in location_3]

    p1000_multi.transfer(
        90,
        binding_dest_supernatant_removal,
        reservoir['A11'],
        new_tip='always',
        tip_racks = tiprack200
    )

    protocol.comment('Removing additional ethanol from the binding row in deep wellplate 1')

    binding_dest_supernatant_removal = [deep_wellplate_1.wells()[well].bottom(1.5) for well in location_3]

    for well in binding_dest_supernatant_removal:
        p1000_multi.pick_up_tip(tiprack50)
        p1000_multi.transfer(
            20,
            well,
            reservoir['A11'],
            new_tip='never'
        )
        p1000_multi.drop_tip()

    # ========================= STEP 4: Drying =======================================================

    protocol.comment('Drying deep wellplate 1 at 300 rpm for 10 minutes at 65 C')

    protocol.comment('Moving deep wellplate 1 from magnetic block to heater shaker')
    protocol.move_labware(
        deep_wellplate_1,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -5}
    ) 

    heater_shaker.close_labware_latch()

    # hs_mod.set_and_wait_for_temperature(65)
    # heater_shaker.set_and_wait_for_shake_speed(300)  # Set rpm
    # protocol.delay(minutes=10)  # Shake for 10 minute

    # hs_mod.deactivate_shaker()
    # hs_mod.deactivate_heater()

    # ========================= STEP 5: Elution of DNA =======================================================
    
    p1000_multi.flow_rate.aspirate = 90
    p1000_multi.flow_rate.dispense = 90

    binding_dest_top = [deep_wellplate_1.wells()[well].top(-2) for well in location_3]

    protocol.comment('Adding 100 uL of elution buffer into the binding row in deep wellplate 1')  
    p1000_multi.transfer(
        100,
        reservoir['A7'].bottom(-0.4),
        binding_dest_top,
        touch_tip=True,
        new_tip='once',
        tip_racks = tiprack200
    ) 

    protocol.comment('Shaking at 1200 rpm for 5 minutes')  
    #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    #protocol.delay(minutes=5)  # Shake for 5 minute
    heater_shaker.open_labware_latch()

    protocol.comment('Moving deep wellplate 1 from heater shaker to magnetic block')
    protocol.move_labware(
        labware=deep_wellplate_1,
        new_location=mag_block, 
        use_gripper=True,  
        drop_offset={"x": 0, 'y': 0, 'z': -12.5}    
    )

    #protocol.delay(seconds=100)  # Shake for 100 seconds

    protocol.comment('Transferring 80-90 uL of eluate from binding row in deep wellplate 1 to the elution row in deep wellplate 2')  

    binding_dest_supernatant_removal = [deep_wellplate_1.wells()[well].bottom(1.5) for well in location_3]
    elution_dest_middle = [deep_wellplate_2.wells()[well] for well in location_1]

    p1000_multi.transfer(
        90,
        binding_dest_supernatant_removal,
        elution_dest_middle,
        touch_tip=True,
        new_tip='always',
        tip_racks = tiprack200
    ) 

    protocol.comment('Moving deep wellplate 2 from D2 to heater shaker')
    protocol.move_labware(
        deep_wellplate_2,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -5}
    ) 

    protocol.comment('Moving deep wellplate 1 from magnetic block to D2')
    protocol.move_labware(
        deep_wellplate_1,
        new_location='D2',
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -5}
    )

    protocol.comment('Moving deep wellplate 2 from heatershaker to magnetic block')
    protocol.move_labware(
        labware=deep_wellplate_2,
        new_location=mag_block, 
        use_gripper=True,  
        drop_offset={"x": 0, 'y': 0, 'z': -12.5}    
    )

    #protocol.delay(minutes=5)  # Stand for 5 minutes

    protocol.comment('Transferring 80-90 uL of eluate from elution row to the final row in deep wellplate 2')   

    elution_plate_removal = [deep_wellplate_2.wells()[well].bottom(0) for well in location_1]
    final_plate = [deep_wellplate_2.wells()[well] for well in location_2]
    
    p1000_multi.transfer(
        90,
        elution_plate_removal,
        final_plate,
        touch_tip=True,
        new_tip='always',
        tip_racks = tiprack200
    ) 
    
    protocol.comment('Protocol Done')   
