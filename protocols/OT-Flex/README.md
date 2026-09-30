# Scripting New Opentrons Protocols
## Creating New Scripts
The Opentrons Flex is run using the Opentrons App with protocols coded in Python with the Opentrons Python API. For full documentation of the Opentrons Python API and its function please see [here](https://docs.opentrons.com/python-api/).  

For protocols that have parameters, account for making the Python script flexible for different inputs. 

1. Read over the manual protocols.io (or a kit instruction if protocols.io doesn't exist) and understand the process.
   
2. List the materials and hardware needed for the protocols, match and replace labware if needed. Write down API names for each material and hardware.
   - API names for labware verified for Opentrons can be found in the 'Labwares' tab in the Opentrons app.
   - If your labware is not found, please check Opentrons [custom labware creator](https://docs.opentrons.com/flex/labware/definitions/#custom-labware-creator).
   
4. Before writing the protocol, begin by adding the imports, metadata, and requirements.
      -  You can also use the Opentrons official [Protocol Designer](https://designer.opentrons.com/?_gl=1*bagoc2*_ga*MTAyMjAwODcyMS4xNzc0MDM2NzU0*_ga_66HK7MC5D7*czE3ODQ3MzY0NTckbzUxJGcxJHQxNzg0NzM2NDY2JGo1MSRsMCRoMA..*_gcl_au*OTUzMDE4Nzc5LjE3ODE4MTgxMTA.*_ga_GNSMNLW4RY*czE3ODQ3MzY0NTckbzUxJGcxJHQxNzg0NzM2NDY2JGo1MSRsMCRoMTI2MTg1MjkzMA) to create a base script to then edit. 
5. Begin formatting the script by adding protocol comments to keep track of each step (action, volume, location and destination)  
   Example:
```ruby
from opentrons import protocol_api

metadata = {
    "apiLevel": "2.16",
    "protocolName": "Promega Miniprep Draft",
    "description": """Example python script""",
    "author": "Your name"
}

requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.25'
}

def run(protocol: protocol_api.ProtocolContext):
  protocol.comment('Adding 120 uL of neutralization solution to the lysis row in deep wellplate 1')

  protocol.comment('Shaking at 1800 rpm for 1 minute')

  protocol.comment('Adding 25 uL of magnesil blue to the lysis row in deep wellplate 1')

  ...
```
5. Explore Opentrons Python API documentation for commands and parameters for each step of the protocol. 

6. Edit the protocol based on dry runs, water runs, and runs with x% glycerol and food coloring if applicable.
   - Dry run: check for collisions, step order, flex gripper misalignment (if applicable).
   - Water run: check for bubbles, aspiration/dispense speed, accurate pipetting (liquid left in and/or on tip), reducing dead volume.
     - Water has a much higher surface tension than most liquids, keep this in mind when testing to reduce dead volume. 
   - Glycerol run: recheck everything in the water run when viscosity and surface tension change.

## TroubleShooting Script:
### Inaccurate pipetting:
- Using the right size tip and pipette
  - Use the pipette tip closest to your aspiration amount. 
  - Consider changing pipette sizes when the aspiration volume is < 25uL (Ex. Aspirate 10 uL with 20 uL tips and 50 uL pipette).
- Decreasing aspiration and dispensing flow rates.
  - Opentrons pipette flow rate is in uL/s.
  - For liquid with viscosity similar to water, change the flow rate to be about the same as the amount you're aspirating/dispensing.
  - For liquid with viscosity higher than 10% glycerol, always make the flow rate 50% of the amount you're aspirating/dispensing.
```ruby
    # If you are aspirating 60 uL of 10% glycerol
    pipette.flow_rate.aspirate = 50
    pipette.flow_rate.dispense = 20
```
- Using liquid class for highly viscous or volatile liquid. 
- Adding touch tip and/or blow out.
  - Touch tip will tap the side of the well to get rid of droplets hanging on the tip.
  - Blow out will blow air out of the tip to get rid of extra droplets hanging inside of the tip (does not always dispel everything)
```ruby
    # Touching tip and blowing out
    pipette.touch_tip()
    pipette.blow_out()
```
### Uneven Mixing:
- Mixing at different heights.
- Distributing liquid across a reservoir.
  - Check [Pierce Gold BCA Assay](https://github.com/bingling-w/opentrons_protocols/tree/1945bdec59cba9e938cb80d12edce98195e45748/protocols/OT-Flex/pierce_gold_bca_assay) for the rest of the protocol. 
```ruby
    # Distributing reagent b across the reservoir. 
    for count in reagent_b_transfer:
          res = reservoir['A2'].bottom(5)
          res_position = [res.move(Point(y=10 * i)) for i in range(-3, 4)]
          p50_single.aspirate(count, standard_tube_rack['D6'])
          for position in res_position:
                p50_single.dispense((count / 7), position)
          p50_single.blow_out(reservoir['A2'].top())

    # Mixing at different height
    p1000_multi.mix(1, 200, reservoir['A2'].bottom(2))
    p1000_multi.mix(2, 200 * 0.7, reservoir['A2'].bottom(3))
    p1000_multi.blow_out(reservoir['A2'].top())
    p1000_multi.mix(1, 200 * 0.5, reservoir['A2'].bottom(4))
    p1000_multi.blow_out(reservoir['A2'].top())
```
### Running out of deck space:
- Stacking labware using the Flex Gripper
  - Labware can be stacked, though this is not part of the Opentrons Python API.
```ruby
    # There’s two wellplate stacked on top of each other at D1. Plate1 is stacked on top of plate2
    plate1 = protocol.load_labware('greiner_96_microplate_280ul', 'D1')

    protocol.move_labware(
          labware=plate1,
          new_location="D2",
          use_gripper=True,  
          pick_up_offset={"x": 0, 'y': 0, 'z': 14.1},   
          drop_offset={"x": 0, 'y': 0, 'z': 0}        
    )

    # New plate loaded
    plate2 = protocol.load_labware('greiner_96_microplate_280ul', 'D1')
    # plate1 deleted from deck (Note: the plate is still physically there)
    del protocol.deck["D2"]

    protocol.move_labware(
            labware=plate2,
            new_location="D2",
            use_gripper=True,  
            pick_up_offset={"x": 0, 'y': 0, 'z': -1.5},
    )
```
      
    In this code, the gripper moves plate1 off plate2, moving plate1 onto deck D2.  
    Then, plate2 is moved to be stacked on top of plate1 at deck D2. 
      
    To make this possible, you have to delete plate1 when it is moved to location D2, tricking the OT-Flex to believe there is no more labware at deck D2.  
    Then, plate2 must be loaded on deck D1 through code, allowing you to then stack plate2 on top of plate1 with an offset.   
      
    The offset should be the height of the labware you are stacking, but the offset should be tested and adjusted to prevent liquid spill.  
    
- Moving unused labware offdeck using the Flex Gripper
  - Labware can be moved offdeck, though this is not part of the Opentrons Python API.
```ruby
      plate1 = protocol.load_labware('greiner_96_microplate_280ul', 'D1')

      protocol.move_labware(
            labware=plate1,
            new_location="D3",
            use_gripper=True,  
            drop_offset={"x": 0, 'y': 0, 'z': 175}        
      )
      
      # plate1 deleted from deck space "D3" to allow the space to be continuously used. 
      del protocol.deck["D3"]
```
      Labware can only be moved offdeck to locations B3, C3, and D3, and there must not be a hardware module placed in that deck space.
