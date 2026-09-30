from opentrons import protocol_api
from opentrons.types import Point

from opentrons.protocol_api import SINGLE, PARTIAL_COLUMN, ALL

metadata = {
    'protocolName': 'BCA with 50uL',
    'description': 'BCA protein assay — 50µL single channel (left) for samples, 8-channel 1000µL (right) for bulk reagents',
    'source': 'OpentronsAI'
}

requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.28'
}

def run(protocol: protocol_api.ProtocolContext):
    # Load trash bin
    trash = protocol.load_trash_bin('A3')

    # Load modules
    tc_mod   = protocol.load_module('thermocyclerModuleV2')           # A1+B1 (default)
    temp_mod = protocol.load_module('temperature module gen2', 'C3')
    hs_mod   = protocol.load_module('heaterShakerModuleV1', 'C1')
    hs_adapter = hs_mod.load_adapter('opentrons_universal_flat_adapter')

    # Load labware
    assay_plate = hs_adapter.load_labware('nunc_96_wellplate_optical_bottom_400ul')
    tube_rack_1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 'D2')
    tube_rack_2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 'C2')
    reservoir   = protocol.load_labware('usascientific_12_reservoir_22ml', 'D1')

    # Tip racks
    # Left (50µL): 50µL tiprack at B2
    # Right (1000µL): two 200µL tipracks at D3 and B3
    tiprack_50ul   = protocol.load_labware('opentrons_flex_96_tiprack_50ul',   'B2')
    tiprack_1000_1 = protocol.load_labware('opentrons_flex_96_tiprack_1000ul', 'B3')
    tiprack_200_2 = protocol.load_labware('opentrons_flex_96_tiprack_200ul', 'D3')

    # ==========================
    # USER-DEFINED PARAMETERS
    # ==========================
    NUM_STANDARDS = 8
    NUM_UNKNOWNS  = 4
    replicates    = 1

    SAMPLE_VOLUME          = 10    # µL — well within 50µL pipette range
    WORKING_REAGENT_VOLUME = 200   # µL per well

    WR_needed  = (NUM_STANDARDS + NUM_UNKNOWNS) * WORKING_REAGENT_VOLUME * replicates
    WR_needed_with_overage = WR_needed + 400

    # Pierce Rapid Gold BCA Working Reagent ratio: 50 parts A : 1 part B
    REAGENT_A_VOLUME = WR_needed_with_overage * (50 / 51)
    REAGENT_B_VOLUME = WR_needed_with_overage * (1 / 51)

    # ==========================
    # LOAD PIPETTES
    # Left  → flex_1channel_50   (precise 10µL sample transfers)
    # Right → flex_8channel_1000 (bulk reagent handling — full column at once)
    # ==========================
    left_pipette = protocol.load_instrument(
        'flex_1channel_50',
        mount='left',
        tip_racks=[tiprack_50ul]
    )

    right_pipette = protocol.load_instrument(
        'flex_8channel_1000',
        mount='right',
        tip_racks=[tiprack_1000_1, tiprack_200_2]
    )

    # Configure 8-channel to use all 8 tips by default
    right_pipette.configure_nozzle_layout(
        style=ALL,
        start='A1',
        tip_racks=[tiprack_1000_1]
    )

    # Flow rates
    # Left  (50µL)  — conservative for small-volume accuracy
    left_pipette.flow_rate.aspirate  = 15
    left_pipette.flow_rate.dispense  = 15
    left_pipette.default_speed       = 750

    # Right (8-channel 1000µL)
    right_pipette.flow_rate.aspirate = 450
    right_pipette.flow_rate.dispense = 450
    right_pipette.default_speed      = 750

    # Define liquids
    reagent_a = protocol.define_liquid(
        name='Reagent A',
        description='BCA Reagent A', 
        display_color='#00FF00')
    reagent_b = protocol.define_liquid(
        name='Reagent B', 
        description='BCA Reagent B', 
        display_color='#0000FF')
    bsa_standard = protocol.define_liquid(
        name='BSA Standard', 
        description='BSA protein standards', 
        display_color='#FF0000')
    unknown_sample = protocol.define_liquid(
        name='Unknown Sample', 
        description='Unknown protein samples', 
        display_color='#FFA500')

    # Load liquids
    reservoir['A1'].load_liquid(liquid=reagent_a, volume=REAGENT_A_VOLUME)
    tube_rack_1['D6'].load_liquid(liquid=reagent_b, volume=REAGENT_B_VOLUME)
    for i in range(8):
        tube_rack_1.wells()[i].load_liquid(liquid=bsa_standard, volume=100)
    for i in range(4):
        tube_rack_2.wells()[i].load_liquid(liquid=unknown_sample, volume=100)

    # =========================================================
    # PROTOCOL STEPS
    # =========================================================

    # Open/close heater-shaker latch
    hs_mod.open_labware_latch()
    protocol.comment('Please ensure plate is properly seated on heater-shaker')
    hs_mod.close_labware_latch()

    # ===== STEP 1: BSA STANDARDS — left 50µL pipette =====
    # 10µL is only 20% of a 1000µL pipette range — very inaccurate.
    # 10µL is 20% of a 50µL pipette range — much more accurate.
#    protocol.comment('Transferring BSA standards to assay plate column 1 (left 50µL pipette)')
#    for i in range(NUM_STANDARDS):
#        left_pipette.pick_up_tip()
#        left_pipette.aspirate(SAMPLE_VOLUME, tube_rack_1.wells()[i].bottom(1))
 #       protocol.delay(seconds=1)                                    # allow liquid to settle
  #      left_pipette.dispense(SAMPLE_VOLUME, assay_plate.wells()[i].bottom(2))
   #     left_pipette.touch_tip()
    #    left_pipette.drop_tip()

    # ===== STEP 2: UNKNOWN SAMPLES — left 50µL pipette =====
#    protocol.comment('Transferring unknown samples to assay plate column 2 (left 50µL pipette)')
#    for i in range(NUM_UNKNOWNS):
 #       left_pipette.pick_up_tip()
  #      left_pipette.aspirate(SAMPLE_VOLUME, tube_rack_2.wells()[i].bottom(1))
   #     protocol.delay(seconds=1)
    #    left_pipette.dispense(SAMPLE_VOLUME, assay_plate.wells()[i + 8].bottom(2))
     #   left_pipette.touch_tip()
      #  left_pipette.drop_tip()


    # ===== STEP 3: TRANSFER REAGENT A — right 8-channel pipette (looped) =====
    # With 8 tips each aspirating simultaneously, each trip moves 8 × vol.
    # We loop until the full REAGENT_A_VOLUME is transferred.
    protocol.comment('Transferring Reagent A to reservoir A2 (right 8-channel pipette)')
    remaining_a = REAGENT_A_VOLUME
    right_pipette.pick_up_tip()
    while remaining_a > 0:
        # Each tip takes vol µL; 8 tips × vol = total moved per trip
        vol_per_tip = min(remaining_a / 8, 950)
        right_pipette.aspirate(vol_per_tip, reservoir['A1'].bottom(2))
        right_pipette.dispense(vol_per_tip, reservoir['A2'].bottom(3))
        remaining_a -= vol_per_tip * 8
    right_pipette.blow_out(reservoir['A2'].top(-5))

    # ===== STEP 4: TRANSFER REAGENT B — right 8-channel (1 tip via PARTIAL_COLUMN) =====
    # Reagent B is in a single 1.5 mL tube (tube_rack_1['D6']).
    # Using PARTIAL_COLUMN with 1 tip to avoid the other 7 tips crashing into empty positions.
    # ===== STEP 4: TRANSFER REAGENT B — left 50µL pipette (two trips) =====
    protocol.comment('Transferring Reagent B to reservoir A2 (left 50µL pipette, two trips)')
    res = reservoir['A2'].bottom(3)
    reservoir_positions = [res.move(Point(y=10 * i)) for i in range(-3, 4)]
    half_b = REAGENT_B_VOLUME / 2  # ~27.5µL per trip, well within 50µL range
    left_pipette.pick_up_tip()

# Trip 1 — first half
    left_pipette.aspirate(half_b, tube_rack_1['D6'].bottom(1))
    protocol.delay(seconds=1)
    for location in reservoir_positions:
        left_pipette.dispense(half_b / 7, location)
    left_pipette.blow_out(reservoir['A2'].top(-5))

# Trip 2 — second half
    left_pipette.aspirate(half_b, tube_rack_1['D6'].bottom(1))
    protocol.delay(seconds=1)
    for location in reservoir_positions:
        left_pipette.dispense(half_b / 7, location)
    left_pipette.blow_out(reservoir['A2'].top(-5))

    left_pipette.drop_tip()


    # ===== STEP 5: MIX WORKING REAGENT — right 8-channel pipette =====
    protocol.comment('Mixing Working Reagent in reservoir A2 (right 8-channel pipette)')
    right_pipette.flow_rate.aspirate = 250
    right_pipette.flow_rate.dispense = 250
    for height in [1.5, 2.5]:
        right_pipette.mix(
            3,
            min(WR_needed_with_overage / 10, 950),
            reservoir['A2'].bottom(height)
        )
    right_pipette.drop_tip()

    right_pipette.configure_nozzle_layout(
        style=ALL,
        start='A1',
        tip_racks=[tiprack_200_2]
    )
    # ===== STEP 6: ADD WR TO STANDARDS — right 8-channel pipette (one shot) =====
    # 8-channel dispenses to all 8 wells in column 1 (A1–H1) simultaneously.
    protocol.comment('Adding Working Reagent to BSA standard wells — column 1 in one shot (8-channel)')
    right_pipette.flow_rate.aspirate = 100
    right_pipette.flow_rate.dispense = 100

    right_pipette.pick_up_tip()
    right_pipette.aspirate(WORKING_REAGENT_VOLUME, reservoir['A2'].bottom(1))
    right_pipette.dispense(WORKING_REAGENT_VOLUME, assay_plate['A1'].top(-2))
    right_pipette.blow_out(assay_plate['A1'].top(-2))
    right_pipette.touch_tip(radius=0.7, v_offset=-1, speed=15)
    right_pipette.drop_tip()

    # ===== STEP 7: ADD WR TO UNKNOWNS — right 8-channel, 4-tip PARTIAL_COLUMN =====
    # 4 unknown wells occupy A2–D2 (top half of column 2).
    # PARTIAL_COLUMN with tips H1–E1 (bottom 4) maps to wells A2–D2.
    protocol.comment('Adding Working Reagent to unknown wells — 4-tip partial column (8-channel)')
    right_pipette.configure_nozzle_layout(
        style=PARTIAL_COLUMN,
        start='H1',
        end='E1',
        tip_racks=[tiprack_200_2]
    )

    def partial_wr_aspirate(pipette, volume, reservoir):
        positions = [-20, 20]
        
        for y in positions:
            pipette.move_to(reservoir.top())
            
            pipette.aspirate(
                volume / 2,
                reservoir.bottom(0.5).move(Point(y=y))
        )
            protocol.delay(seconds=0.5)
    
    right_pipette.pick_up_tip() 

    partial_wr_aspirate(
        right_pipette,
        WORKING_REAGENT_VOLUME,
        reservoir['A2']
)

    right_pipette.dispense(
          WORKING_REAGENT_VOLUME, assay_plate['D2'].top(-2))

    right_pipette.blow_out(assay_plate['D2'].top(-2))

    right_pipette.touch_tip(radius=0.7, v_offset=-1, speed=15
)

    right_pipette.drop_tip()

    # ===== STEP 8: MIX ON HEATER-SHAKER =====
    protocol.comment('Mixing all samples using heater-shaker at 250 rpm for 30 seconds')
    hs_mod.set_and_wait_for_shake_speed(rpm=250)
    protocol.delay(seconds=30)
    hs_mod.deactivate_shaker()

    # ===== STEP 9: INCUBATE =====
    protocol.comment('Incubating for 3 minutes at room temperature')
    protocol.delay(minutes=3)

    # ===== DONE =====
    hs_mod.open_labware_latch()
    protocol.comment('Protocol complete. Plate ready for absorbance reading at 480 nm.')
    protocol.comment('Column 1 (A1-H1): BSA standards')
    protocol.comment('Column 2 (A2-D2): Unknown samples')
    protocol.comment('Note: Working Reagent must be used within 1.5 hours of preparation.')
    protocol.comment('Remove plate from heater-shaker and read absorbance using external plate reader.')
