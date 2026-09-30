from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, ALL
from opentrons.protocol_api import SINGLE, ALL

# Edit the numbers here to suit your needs
bacteria_number = 8 # up to 96 (keep to multiples of 8 for the multichannel pipette)

#Change module location base on your own setup
temp_module_location = 'C3'
heater_shaker_location = 'C1'

metadata = {
    'protocolName': 'Promega Miniprep Draft',
    'author': 'Bing',
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
    temp_module = protocol.load_module('temperature module gen2', 'C3')
    heater_shaker = protocol.load_module('heaterShakerModuleV1', 'C1')

    # Load labware
    binding_plate = protocol.load_labware('greiner_96_microplate_280ul', 'A2')

    reservoir = temp_module.load_labware('usascientific_12_reservoir_22ml')

    # Load heater shaker adapter
    hs_adapter = heater_shaker.load_adapter("opentrons_universal_flat_adapter")
    # Load labware on heater shaker adapter
    deep_wellplate = hs_adapter.load_labware(
        "greiner_96_wellplate_2000ul",
        label="Deep wellplate on heater"
    )

    #Load magnetic block
    mag_block = protocol.load_module("magneticBlockV1", "D1") 
    # Load a compatible 96‑well plate onto the magnetic block
    clearing_plate = mag_block.load_labware("greiner_96_microplate_280ul") 

    # Load tip racks for all operations
    tiprack1000 = protocol.load_labware('opentrons_flex_96_tiprack_1000ul', 'B2')
    tiprack200 = protocol.load_labware('opentrons_flex_96_tiprack_200ul', 'B3')

    # Load pipettes
    p1000_multi = protocol.load_instrument(
        'flex_8channel_1000',
        mount='right',
        tip_racks=[tiprack1000, tiprack200]
    )

    # Define liquids
    bacterial_culture = protocol.define_liquid(
        name='Bacterial culture',
        display_color="#000000"
    )
    resuspension_solution = protocol.define_liquid(
        name='Resuspension Solution',
        display_color='#00FF00'
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

    # Load liquids into labware
    reservoir['A1'].load_liquid(liquid=lysis_solution, volume=1000)
    reservoir['A2'].load_liquid(liquid=neutralization_solution, volume=1000)
    reservoir['A3'].load_liquid(liquid=magnesil_blue, volume=1000)
    reservoir['A4'].load_liquid(liquid=magnesil_red, volume=1000)
    viscous_liquid = protocol.get_liquid_class(name="glycerol_50")
    reservoir['A5'].load_liquid(liquid=ethanol, volume=5000)
    volatile_liquid = protocol.get_liquid_class(name="ethanol_80")
    reservoir['A6'].load_liquid(liquid=elution_buffer, volume=1000)

    # Establishing where the bacteria culture will go in the deep well plate
    bacteria_location = deep_wellplate.wells()[:bacteria_number]
    # Load bacterial culture into the deep well plate
    for well in bacteria_location:
        well.load_liquid(liquid=bacterial_culture, volume=1000)

    if bacteria_number / 8 < 3:
        tipsize = tiprack200
    else:
        tipsize = tiprack1000

    # Determining where the 8-channel pipette will go
    well_location = []
    for i in range(int(bacteria_number / 8)):
        well_location.append(8 * i)

    # Get properties for your specific pipette and tip combination
    custom_viscous_properties = viscous_liquid.get_for(p1000_multi, tiprack200)
    
    # Enable mixing BEFORE aspirate
    custom_viscous_properties.aspirate.mix.enabled = True
    custom_viscous_properties.aspirate.mix.repetitions = 3  # Mix 3 times
    custom_viscous_properties.aspirate.mix.volume = 100      # Mix with 100 µL
    
    # Enable mixing AFTER dispense
    custom_viscous_properties.dispense.mix.enabled = True
    custom_viscous_properties.dispense.mix.repetitions = 3  # Mix 3 times
    custom_viscous_properties.dispense.mix.volume = 100     # Mix with 100 µL
  
    # ========================= STEP 1: Cell Lysis and Lysate Clearing =======================================================
    protocol.comment('Adding 120 uL of lysis solution to the deep well plate')

    p1000_multi.flow_rate.aspirate = 100
    p1000_multi.flow_rate.dispense = 100

    # Close heater shaker latch
    heater_shaker.close_labware_latch()
    
    deep_well_dest_top = [deep_wellplate.wells()[well].top(-2) for well in well_location]
    
    p1000_multi.distribute(
        120,
        reservoir['A1'],
        deep_well_dest_top,
        touch_tip=True,
        new_tip='once',
        disposal_volume=0,
        tip_racks = [tiprack1000]
        )

    #heater_shaker.set_and_wait_for_shake_speed(1800)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minutes

    # Stop shaking
    #heater_shaker.deactivate_shaker()

    protocol.comment('Adding 120 uL of neutralization solution to the deep well plate')
    
    p1000_multi.distribute(
        120,
        reservoir['A2'],
        deep_well_dest_top,
        touch_tip=True,
        new_tip='once',
        disposal_volume=0,
        tip_racks = [tiprack1000]
        )

    #heater_shaker.set_and_wait_for_shake_speed(1800)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minutes

    # Stop shaking
    #heater_shaker.deactivate_shaker()

    protocol.comment('Adding 25 uL of magnesil blue to the deep well plate')

    p1000_multi.flow_rate.aspirate = 25
    p1000_multi.flow_rate.dispense = 25

    deep_well_dest_middle = [deep_wellplate.wells()[well] for well in well_location]

    p1000_multi.transfer_with_liquid_class(
        liquid_class = viscous_liquid,
        volume = 25,
        source = reservoir['A3'],
        dest = deep_well_dest_middle,
        new_tip='always',
        tip_racks = [tiprack200]
    )

    p1000_multi.flow_rate.aspirate = 250
    p1000_multi.flow_rate.dispense = 250

    #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    #protocol.delay(minutes=1)  # Shake for 1 minute

    # Stop shaking
    #heater_shaker.deactivate_shaker()

    protocol.comment('Adding 300 uL of neutralized lysis from the deep well plate to the clearing plate')

    clearing_plate_dest = [clearing_plate.wells()[well] for well in well_location]

    for src, dest in zip(deep_well_dest_middle, clearing_plate_dest):
       p1000_multi.transfer(
           300,
           src,
           dest,
           touch_tip=True,
           new_tip='always'
        )
    
    protocol.comment('Delaying for 2 minutes to allow the magnetized pellet to form')

    #protocol.delay(minutes=2)  # delay 2 minutes


    # ========================= STEP 3: DNA Binding =======================================================

    protocol.comment('Adding 25 uL of magnesil red to the new binding plate')

    p1000_multi.flow_rate.aspirate = 20
    p1000_multi.flow_rate.dispense = 20

    protocol.move_labware(
        labware=binding_plate,
        new_location="D2", 
        use_gripper=True,  
        pick_up_offset={"x": 0, 'y': 0, 'z': (13*2)},    
        drop_offset={"x": 0, 'y': 0, 'z': 2.5}  # good
    )

    #Determining where the 8-channel pipette will go in the binding plate
    binding_plate_dest = [binding_plate.wells()[well] for well in well_location]

    p1000_multi.transfer_with_liquid_class(
        liquid_class = viscous_liquid,
        volume = 25,
        source = reservoir['A5'],
        dest = binding_plate_dest,
        new_tip='once',
        tip_racks = [tiprack200]
        )
    
    protocol.comment('Adding 120 uL of the clear lysate to the new binding plate')

    p1000_multi.flow_rate.aspirate = 120
    p1000_multi.flow_rate.dispense = 120

    binding_plate_dest_top = [binding_plate.wells()[well].top(-0.2) for well in well_location]

    for src, dest in zip(clearing_plate_dest, binding_plate_dest_top):
       p1000_multi.transfer(
           120,
           src,
           dest,
           touch_tip=True,
           new_tip='once',
           tip_racks = [tiprack200]
       )
       
    # Open heater shaker latch
    heater_shaker.open_labware_latch()
    
    protocol.move_labware(deep_wellplate, new_location="C2", use_gripper=True) 

    protocol.move_labware(
        binding_plate,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2}, 
        drop_offset={"x": 0.5, 'y': 0, 'z': -3} #good
    ) 

    heater_shaker.close_labware_latch()

    #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    #protocol.delay(minutes=2)  # Shake for 2 minutes

    # Stop shaking
    #heater_shaker.deactivate_shaker()
    heater_shaker.open_labware_latch()

    protocol.move_labware(
        clearing_plate,
        new_location="D3",
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2}, 
        drop_offset={"x": 0, 'y': 0, 'z': -1} 
    ) 

    protocol.move_labware(
        binding_plate,
        new_location=mag_block,
        use_gripper=True,
        drop_offset={"x": -0.2, 'y': 0, 'z': -3.5} #good
    )

    protocol.comment('Removing supernatant from the binding plate')

    binding_plate_supernatant_removal = [binding_plate.wells()[well].bottom(2) for well in well_location]

    p1000_multi.transfer(
        110,
        binding_plate_supernatant_removal,
        reservoir['A12'],
        new_tip = 'always',
        tip_rack = [tiprack200]
    )

    protocol.move_labware(
        binding_plate,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0.5, 'y': 0, 'z': 1}  #good
    )

    heater_shaker.close_labware_latch()

    protocol.move_labware(
        clearing_plate,
        new_location=mag_block,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0.5, 'y': 0, 'z': -6}  #good
    )

    protocol.comment('Adding 25 uL more Magnesil Red to the binding plate')

    binding_plate_dest = [binding_plate.wells()[well] for well in well_location]

    p1000_multi.flow_rate.aspirate = 20
    p1000_multi.flow_rate.dispense = 20

    p1000_multi.transfer_with_liquid_class(
        liquid_class = viscous_liquid,
        volume = 25,
        source = reservoir['A5'],
        dest = binding_plate_dest,
        new_tip='once',
        tip_racks = [tiprack200]
    )

    protocol.comment('Adding reamaining 120 uL of the clear lysate to the binding plate')

    binding_plate_dest_top = [binding_plate.wells()[well].top(-0.2) for well in well_location]

    p1000_multi.flow_rate.aspirate = 120
    p1000_multi.flow_rate.dispense = 120

    p1000_multi.transfer(
        120,
        clearing_plate_dest,
        binding_plate_dest_top,
        touch_tip=True,
        new_tip='once',
        tip_rack= [tiprack200]
    )
    
    #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    #protocol.delay(minutes=2)  # Shake for 2 minutes
    heater_shaker.open_labware_latch()

    protocol.comment('Moving clearing plate offdeck')
    protocol.move_labware(
        clearing_plate,
        new_location="D3",
        use_gripper=True,
        drop_offset={"x": 175, 'y': 0, 'z': 6} 
    )

    del protocol.deck["D3"]

    protocol.move_labware(
        binding_plate,
        new_location=mag_block,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0, 'y': 0, 'z': -7} #good
    )

    protocol.comment('Removing supernatant from the binding plate')

    p1000_multi.transfer(
        110,
        binding_plate_supernatant_removal,
        reservoir['A12'],
        tip_racks = [tiprack200]
    )
    
    # ========================= STEP 4: Washing =======================================================
    
    protocol.comment('Washing Binding plate 3 times')

    binding_plate_dest_top = [binding_plate.wells()[well].top(-0.2) for well in well_location]

    for i in range(2):

        protocol.comment('Adding 100 uL 80 percent ethanol to the binding plate')

        p1000_multi.transfer_with_liquid_class(
            liquid_class=volatile_liquid,
            volume=100,
            source=reservoir['A6'],
            dest=binding_plate['A1'],
            new_tip='once',
            tip_racks = [tiprack200]
        )

        heater_shaker.open_labware_latch()

        protocol.move_labware(
            binding_plate,
            new_location=hs_adapter,
            use_gripper=True,
            pick_up_offset={"x": 0, 'y': 0, 'z': -2},
            drop_offset={"x": 0.5, 'y': 0, 'z': 1} #good
        )

        heater_shaker.close_labware_latch()
        #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
        #protocol.delay(minutes=1)  # Shake for 2 minute
        heater_shaker.open_labware_latch()

        protocol.move_labware(
            binding_plate,
            new_location=mag_block,
            use_gripper=True,
            pick_up_offset={"x": 0, 'y': 0, 'z': -2},
            drop_offset={"x": 0, 'y': 0, 'z': -7} #good
        )

        #protocol.delay(minutes=2)  # Allow pellet to form for 2 minute

        protocol.comment('Removing spent wash from the binding plate')

        binding_plate_supernatant_removal = [binding_plate.wells()[well].bottom(2) for well in well_location]

        p1000_multi.transfer(
            100,
            binding_plate_supernatant_removal,
            reservoir['A11'],
            new_tip='once',
            tip_racks = [tiprack200]
        )

    # ========================= STEP 5: Drying =======================================================

    protocol.comment('Drying binding plate for 10 minutes')

    protocol.move_labware(
        binding_plate,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0.5, 'y': 0, 'z': 1}  #good
    )

    heater_shaker.close_labware_latch()

    #protocol.delay(minutes=10)

    # hs_mod.set_and_wait_for_temperature(51)
    # heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    # protocol.delay(minutes=2)  # Shake for 2 minute

    # hs_mod.deactivate_shaker()
    # protocol.delay(minutes=2)  # Shake for 2 minute
    # hs_mod.deactivate_heater()

    # ========================= STEP 6: Elution of DNA =======================================================
    
    protocol.comment('Adding 100 uL of elution buffer into the binding plate')  

    p1000_multi.flow_rate.aspirate = 90
    p1000_multi.flow_rate.dispense = 90

    binding_plate_dest_top = [binding_plate.wells()[well].top(-0.2) for well in well_location]
    p1000_multi.transfer(
        100,
        reservoir['A7'],
        binding_plate_dest_top,
        touch_tip=True,
        new_tip='once',
        tip_racks = [tipsize]
    ) 

    #heater_shaker.set_and_wait_for_shake_speed(1200)  # Set rpm
    #protocol.delay(minutes=5)  # Shake for 2 minute
    heater_shaker.open_labware_latch()

    protocol.move_labware(
        binding_plate,
        new_location=mag_block,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0, 'y': 0, 'z': -7} #good
    )

    protocol.comment('Moving elution plate')  
    elution_plate = protocol.load_labware('greiner_96_microplate_280ul', 'A2')

    protocol.move_labware(
        labware=elution_plate,
        new_location="D2", 
        use_gripper=True,  
        pick_up_offset={"x": 0, 'y': 0, 'z': 13},    
        drop_offset={"x": 0, 'y': 0, 'z': 2.5}   # good
    )

    protocol.comment('Transferring 80-90 uL of eluate from binding plate to the elution plate')  

    elution_plate_middle = [elution_plate.wells()[well] for well in well_location]
    binding_plate_supernatant_removal = [binding_plate.wells()[well].bottom(2) for well in well_location]

    p1000_multi.transfer(
        90,
        binding_plate_supernatant_removal,
        elution_plate_middle,
        touch_tip=True,
        new_tip='always',
        tip_racks = [tiprack200]
    ) 

    protocol.move_labware(
        binding_plate,
        new_location=hs_adapter,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2}, 
        drop_offset={"x": 0.2, 'y': 0, 'z': -3} #good
    ) 

    heater_shaker.close_labware_latch()

    protocol.move_labware(
        elution_plate,
        new_location=mag_block,
        use_gripper=True,
        pick_up_offset={"x": 0, 'y': 0, 'z': -2},
        drop_offset={"x": 0, 'y': 0, 'z': -7} #good
    )

    #protocol.delay(minutes=5)  # Stand for 5 minutes

    final_plate = protocol.load_labware('greiner_96_microplate_280ul', 'A2')

    protocol.move_labware(
        labware=final_plate,
        new_location="D2", 
        use_gripper=True,  
        pick_up_offset={"x": 0, 'y': 0, 'z': -1.2},    
        drop_offset={"x": -0.2, 'y': 0, 'z': 0}  # Fine-tune stacking height
    )

    protocol.comment('Transferring 80-90 uL of eluate from elution plate to the final plate')   

    elution_plate_removal = [elution_plate.wells()[well].bottom(2) for well in well_location]
    final_plate = [final_plate.wells()[well] for well in well_location]
    
    p1000_multi.transfer(
        90,
        elution_plate_removal,
        final_plate,
        touch_tip=True,
        new_tip='always',
        tip_racks = [tiprack200],
        flow_rate = 100
    ) 

    heater_shaker.open_labware_latch()

    protocol.comment('Protocol Done')   
