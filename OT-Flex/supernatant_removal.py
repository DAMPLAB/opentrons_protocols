import json
from opentrons import protocol_api, types

metadata = {
    "protocolName": "8-Channel 1000ul Supernatant Removal DW96 Well (FAST DISPENSE)",
    "author": "Dre/Ben - Fast Dispense Optimized",
    "created": "2025-12-02T15:43:08.354Z",
    "internalAppBuildDate": "Tue, 03 Feb 2026 18:27:38 GMT",
    "lastModified": "2026-02-03T18:47:08.542Z",
    "protocolDesigner": "8.8.0",
    "source": "Protocol Designer",
}

requirements = {"robotType": "Flex", "apiLevel": "2.27"}

def run(protocol: protocol_api.ProtocolContext) -> None:    
    # Load Modules:
    magnetic_block_1 = protocol.load_module("magneticBlockV1", "D3")
    heater_shaker_module_1 = protocol.load_module("heaterShakerModuleV1", "C1")
    thermocycler_module_1 = protocol.load_module("thermocyclerModuleV2", "B1")
    temperature_module_1 = protocol.load_module("temperatureModuleV2", "C3")

    # Load Labware:
    tip_rack_1 = protocol.load_labware(
        "opentrons_flex_96_tiprack_1000ul",
        location="B2",
        label="Opentrons Flex 96 Tip Rack 1000 µL (1)",
        namespace="opentrons",
        version=1,
    )
    tip_rack_2 = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        location="B3",
        namespace="opentrons",
        version=1,
    )
    tip_rack_3 = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        location="A2",
        label="Opentrons Flex 96 Tip Rack 200 µL (1)",
        namespace="opentrons",
        version=1,
    )
    well_plate_1 = protocol.load_labware(
        "nest_96_wellplate_2ml_deep",
        location="D2",
        namespace="opentrons",
        version=5,
    )
    reservoir_1 = protocol.load_labware(
        "agilent_1_reservoir_290ml",
        location="D1",
        namespace="opentrons",
        version=4,
    )

    # Load Pipettes:
    pipette_left = protocol.load_instrument("flex_8channel_1000", "left")
    pipette_right = protocol.load_instrument("flex_8channel_50", "right")

    # Speed Up Gantry:
    pipette_left.default_speed = 800

    # Load Trash Bin:
    trash_bin_1 = protocol.load_trash_bin("A3")

    # Define Liquids:
    liquid_1 = protocol.define_liquid(
        "Supernatant",
        display_color="#b925ff",
    )
    liquid_2 = protocol.define_liquid(
        "SuperN",
        display_color="#b925ffff",
    )

    # Load Liquids:
    well_plate_1.load_liquid(
        wells=[
            "A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1",
            "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2",
            "A3", "B3", "C3", "D3", "E3", "F3", "G3", "H3",
            "A4", "B4", "C4", "D4", "E4", "F4", "G4", "H4",
            "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5",
            "A6", "B6", "C6", "D6", "E6", "F6", "G6", "H6",
            "A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7",
            "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8",
            "A9", "B9", "C9", "D9", "E9", "F9", "G9", "H9",
            "A10", "B10", "C10", "D10", "E10", "F10", "G10", "H10",
            "A11", "B11", "C11", "D11", "E11", "F11", "G11", "H11",
            "A12", "B12", "C12", "D12", "E12", "F12", "G12", "H12"
        ],
        liquid=liquid_1,
        volume=1800,
    )

    # PROTOCOL STEPS:
    # Step 1: transfer
    # Aspiration: Slow to protect pellet
    # Dispensing: Max speed as supernatant not needed

    pipette_left.configure_nozzle_layout(
        protocol_api.ALL,
        start="A1",
    )
    pipette_left.transfer_with_liquid_class(
        volume=1800,
        source=[well_plate_1["A1"], well_plate_1["A2"], well_plate_1["A3"]],
        dest=[reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"]],
        new_tip="once",
        trash_location=trash_bin_1,
        keep_last_tip=True,
        group_wells=False,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_1_fast_dispense",
            properties={"flex_8channel_1000": {"opentrons/opentrons_flex_96_tiprack_1000ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": -1.6, "y": 0, "z": 7},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 100)],  
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": True, "duration": 0.2},
                        "speed": 50,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": True, "duration": 0.1},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 60,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": -5},
                        "position_reference": "well-top",
                    },
                    "flow_rate_by_volume": [(0, 1000)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 1000,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 1000,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": True, "location": "destination", "flow_rate": 1000},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 0)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()