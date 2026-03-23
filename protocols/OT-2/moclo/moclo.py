"""
--------------------------------------------------------------------------------
Description:
Modular Cloning Protocol for OT-2

Written by W.R. Jackson
--------------------------------------------------------------------------------
"""
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Modular Cloning',
    'author': 'W.R. Jackson <wrjackso@bu.edu>',
    'description': 'Modular Cloning Protocol for the assembly of gene fragments.',
    'apiLevel': '2.10'
}
ROW_COUNT = 3
COLUMN_COUNT = 6
VOLUME_TOLERANCE = 1.2

tube_volume_lut = {
    'ddh20': 4.5,
    'buffer': 2,
    'promoter_1': 2,
    'promoter_2': 2,
    'insulator': 2,
    'cds': 2,
    'terminator': 2,
    'backbone': 2,
    'bbs1': 1,
    't4': 0.5,
}

tube_reagent_map = {
    'A1': 'ddh20',
    'A2': 'buffer',
    'B1': 'promoter_1',
    'B2': 'promoter_2',
    'B3': 'insulator',
    'B4': 'cds',
    'B5': 'terminator',
    'B6': 'backbone',
    'A3': 'bbs1',
    'A4': 't4',
}


def run(protocol: protocol_api.ProtocolContext):
    # labware
    tiprack = protocol.load_labware('opentrons_96_tiprack_10ul', '1')
    reagent_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '2')
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')

    # pipettes
    pipette = protocol.load_instrument(
        'p10_single', 'right', tip_racks=[tiprack]
    )

    # commands
    # Perform a Reaction
    moclo_reaction = ['A1', 'A2', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'A3', 'A4']
    for reaction in moclo_reaction:
        pipette.pick_up_tip()
        RUNNING_VOLUME = 0
        if reaction == 'A3' or reaction == 'A4':
            protocol.pause()
        for i in range(ROW_COUNT):
            for j in range(COLUMN_COUNT):
                target_volume = tube_volume_lut[tube_reagent_map[reaction]]
                if RUNNING_VOLUME < target_volume:
                    pipette.aspirate(
                        10-RUNNING_VOLUME,
                        reagent_rack[reaction],
                        )
                    RUNNING_VOLUME = 10
                target_well = f'{chr(i + 65)}{j + 1}'
                pipette.dispense(
                    volume=tube_volume_lut[tube_reagent_map[reaction]],
                    location=plate[target_well],
                    rate=0.5,
                )
                pipette.touch_tip()
                RUNNING_VOLUME -= target_volume
        pipette.drop_tip()
