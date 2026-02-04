import json
from opentrons import protocol_api, types

metadata = {
    "protocolName": "8-Channel 1000ul Supernatant Removal DW96 Well",
    "author": "Dre/Ben",
    "created": "2025-12-02T15:43:08.354Z",
    "lastModified": "2025-12-02T16:19:04.326Z",
    "protocolDesigner": "8.6.3",
    "source": "Protocol Designer",
}

requirements = {"robotType": "Flex", "apiLevel": "2.26"}

def run(protocol: protocol_api.ProtocolContext) -> None:
    # Load Modules:
    magnetic_block_1 = protocol.load_module("magneticBlockV1", "D3")
    heater_shaker_module_1 = protocol.load_module("heaterShakerModuleV1", "C1")
    thermocycler_module_1 = protocol.load_module("thermocyclerModuleV2", "B1")
    temperature_module_1 = protocol.load_module("temperatureModuleV2", "C3")

    # Load Labware:
    tip_rack_3 = protocol.load_labware(
        "opentrons_flex_96_tiprack_1000ul",
        location="B2",
        label="Opentrons Flex 96 Tip Rack 1000 µL (1)",
        namespace="opentrons",
        version=1,
    )
    tip_rack_1 = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        location="B3",
        namespace="opentrons",
        version=1,
    )
    tip_rack_2 = protocol.load_labware(
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
        version=4,
    )
    reservoir_1 = protocol.load_labware(
        "agilent_1_reservoir_290ml",
        location="D1",
        namespace="opentrons",
        version=3,
    )

    # Load Pipettes:
    pipette_left = protocol.load_instrument("flex_8channel_1000", "left")
    pipette_right = protocol.load_instrument("flex_8channel_50", "right")

    # Load Trash Bins:
    trash_bin_1 = protocol.load_trash_bin("A3")

    # Define Liquids:
    liquid_1 = protocol.define_liquid(
        "Supernatant",
        display_color="#b925ff",
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

    # PROTOCOL STEPS

    # Step 1: transfer
    pipette_left.transfer_with_liquid_class(
        volume=1800,
        source=[well_plate_1["A1"], well_plate_1["A2"], well_plate_1["A3"], well_plate_1["A4"], well_plate_1["A5"], well_plate_1["A6"], well_plate_1["A7"], well_plate_1["A8"], well_plate_1["A9"], well_plate_1["A10"], well_plate_1["A11"], well_plate_1["A12"]],
        dest=[reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"], reservoir_1["A1"]],
        new_tip="per source",
        trash_location=trash_bin_1,
        keep_last_tip=True,
        group_wells=False,
        tip_racks=[tip_rack_3],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_1",
            properties={"flex_8channel_1000": {"opentrons/opentrons_flex_96_tiprack_1000ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 1},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 716)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 100,
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
                        "speed": 50,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 716)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 100,
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
                        "speed": 50,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 20)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

DESIGNER_APPLICATION = """{"robot":{"model":"OT-3 Standard"},"designerApplication":{"name":"opentrons/protocol-designer","version":"8.6.0","data":{"pipetteTiprackAssignments":{"054f0ce0-027c-45ca-8e35-b4c3dca73364":["opentrons/opentrons_flex_96_tiprack_1000ul/1"],"1e73b1cd-978b-42ae-95bb-f96dc0a37e15":["opentrons/opentrons_flex_96_tiprack_200ul/1"]},"dismissedWarnings":{"form":[],"timeline":[]},"ingredients":{"0":{"displayName":"Supernatant","displayColor":"#b925ff","description":null,"liquidGroupId":"0"}},"ingredLocations":{"91ec8f0c-b026-40fe-80d8-e754fd6409f3:opentrons/nest_96_wellplate_2ml_deep/4":{"A1":{"0":{"volume":1800}},"B1":{"0":{"volume":1800}},"C1":{"0":{"volume":1800}},"D1":{"0":{"volume":1800}},"E1":{"0":{"volume":1800}},"F1":{"0":{"volume":1800}},"G1":{"0":{"volume":1800}},"H1":{"0":{"volume":1800}},"A2":{"0":{"volume":1800}},"B2":{"0":{"volume":1800}},"C2":{"0":{"volume":1800}},"D2":{"0":{"volume":1800}},"E2":{"0":{"volume":1800}},"F2":{"0":{"volume":1800}},"G2":{"0":{"volume":1800}},"H2":{"0":{"volume":1800}},"A3":{"0":{"volume":1800}},"B3":{"0":{"volume":1800}},"C3":{"0":{"volume":1800}},"D3":{"0":{"volume":1800}},"E3":{"0":{"volume":1800}},"F3":{"0":{"volume":1800}},"G3":{"0":{"volume":1800}},"H3":{"0":{"volume":1800}},"A4":{"0":{"volume":1800}},"B4":{"0":{"volume":1800}},"C4":{"0":{"volume":1800}},"D4":{"0":{"volume":1800}},"E4":{"0":{"volume":1800}},"F4":{"0":{"volume":1800}},"G4":{"0":{"volume":1800}},"H4":{"0":{"volume":1800}},"A5":{"0":{"volume":1800}},"B5":{"0":{"volume":1800}},"C5":{"0":{"volume":1800}},"D5":{"0":{"volume":1800}},"E5":{"0":{"volume":1800}},"F5":{"0":{"volume":1800}},"G5":{"0":{"volume":1800}},"H5":{"0":{"volume":1800}},"A6":{"0":{"volume":1800}},"B6":{"0":{"volume":1800}},"C6":{"0":{"volume":1800}},"D6":{"0":{"volume":1800}},"E6":{"0":{"volume":1800}},"F6":{"0":{"volume":1800}},"G6":{"0":{"volume":1800}},"H6":{"0":{"volume":1800}},"A7":{"0":{"volume":1800}},"B7":{"0":{"volume":1800}},"C7":{"0":{"volume":1800}},"D7":{"0":{"volume":1800}},"E7":{"0":{"volume":1800}},"F7":{"0":{"volume":1800}},"G7":{"0":{"volume":1800}},"H7":{"0":{"volume":1800}},"A8":{"0":{"volume":1800}},"B8":{"0":{"volume":1800}},"C8":{"0":{"volume":1800}},"D8":{"0":{"volume":1800}},"E8":{"0":{"volume":1800}},"F8":{"0":{"volume":1800}},"G8":{"0":{"volume":1800}},"H8":{"0":{"volume":1800}},"A9":{"0":{"volume":1800}},"B9":{"0":{"volume":1800}},"C9":{"0":{"volume":1800}},"D9":{"0":{"volume":1800}},"E9":{"0":{"volume":1800}},"F9":{"0":{"volume":1800}},"G9":{"0":{"volume":1800}},"H9":{"0":{"volume":1800}},"A10":{"0":{"volume":1800}},"B10":{"0":{"volume":1800}},"C10":{"0":{"volume":1800}},"D10":{"0":{"volume":1800}},"E10":{"0":{"volume":1800}},"F10":{"0":{"volume":1800}},"G10":{"0":{"volume":1800}},"H10":{"0":{"volume":1800}},"A11":{"0":{"volume":1800}},"B11":{"0":{"volume":1800}},"C11":{"0":{"volume":1800}},"D11":{"0":{"volume":1800}},"E11":{"0":{"volume":1800}},"F11":{"0":{"volume":1800}},"G11":{"0":{"volume":1800}},"H11":{"0":{"volume":1800}},"A12":{"0":{"volume":1800}},"B12":{"0":{"volume":1800}},"C12":{"0":{"volume":1800}},"D12":{"0":{"volume":1800}},"E12":{"0":{"volume":1800}},"F12":{"0":{"volume":1800}},"G12":{"0":{"volume":1800}},"H12":{"0":{"volume":1800}}}},"savedStepForms":{"__INITIAL_DECK_SETUP_STEP__":{"stepType":"manualIntervention","id":"__INITIAL_DECK_SETUP_STEP__","labwareLocationUpdate":{"e11106c2-2139-43e4-bf4f-93683806128f:opentrons/opentrons_flex_96_tiprack_1000ul/1":"B2","8d7c3a6a-3244-4664-bddd-d97ceb406c30:opentrons/opentrons_flex_96_tiprack_200ul/1":"B3","931035fc-f041-4d1c-b664-0f3f92e74a47:opentrons/opentrons_flex_96_tiprack_200ul/1":"A2","91ec8f0c-b026-40fe-80d8-e754fd6409f3:opentrons/nest_96_wellplate_2ml_deep/4":"D2","7a01a882-27a1-4f47-b17d-f95ce0bfff98:opentrons/agilent_1_reservoir_290ml/3":"D1"},"pipetteLocationUpdate":{"054f0ce0-027c-45ca-8e35-b4c3dca73364":"left","1e73b1cd-978b-42ae-95bb-f96dc0a37e15":"right"},"moduleLocationUpdate":{"57383cbb-616c-46d4-92c2-0560f7229a63:magneticBlockType":"D3","f451dea6-9081-46e7-8bab-c03271525fe6:heaterShakerModuleType":"C1","d277cacd-5268-4272-9f8b-c1a4267e2465:thermocyclerModuleType":"B1","b6ecaa76-3d6a-4fb2-a47f-d27a311b67ea:temperatureModuleType":"C3"},"trashBinLocationUpdate":{"f4e799fa-0f49-41e1-b6f8-0bc0bd29df20:trashBin":"cutoutA3"},"wasteChuteLocationUpdate":{},"stagingAreaLocationUpdate":{},"gripperLocationUpdate":{"09e69681-d092-4477-8ea2-b29e585f49f4:gripper":"mounted"}},"8a5f4533-4bf2-411d-aa9a-8d6b00a9eb8d":{"id":"8a5f4533-4bf2-411d-aa9a-8d6b00a9eb8d","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"716","aspirate_labware":"91ec8f0c-b026-40fe-80d8-e754fd6409f3:opentrons/nest_96_wellplate_2ml_deep/4","aspirate_mix_checkbox":false,"aspirate_mix_times":"","aspirate_mix_volume":"","aspirate_mmFromBottom":1,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"50","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"100","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":-1,"aspirate_touchTip_speed":"30","aspirate_touchTip_mmFromEdge":"0.5","aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"716","blowout_location":null,"changeTip":"perSource","conditioning_checkbox":false,"conditioning_volume":"","dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"716","dispense_labware":"7a01a882-27a1-4f47-b17d-f95ce0bfff98:opentrons/agilent_1_reservoir_290ml/3","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":"","dispense_mmFromBottom":1,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"50","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"100","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":-1,"dispense_touchTip_speed":"30","dispense_touchTip_mmFromEdge":"0.5","dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A1"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":false,"disposalVolume_volume":"","dropTip_location":"f4e799fa-0f49-41e1-b6f8-0bc0bd29df20:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"054f0ce0-027c-45ca-8e35-b4c3dca73364","preWetTip":false,"pushOut_checkbox":true,"pushOut_volume":"20","tipRack":"opentrons/opentrons_flex_96_tiprack_1000ul/1","volume":"1800"}},"orderedStepIds":["8a5f4533-4bf2-411d-aa9a-8d6b00a9eb8d"],"pipettes":{"054f0ce0-027c-45ca-8e35-b4c3dca73364":{"pipetteName":"p1000_multi_flex"},"1e73b1cd-978b-42ae-95bb-f96dc0a37e15":{"pipetteName":"p50_multi_flex"}},"modules":{"57383cbb-616c-46d4-92c2-0560f7229a63:magneticBlockType":{"model":"magneticBlockV1"},"f451dea6-9081-46e7-8bab-c03271525fe6:heaterShakerModuleType":{"model":"heaterShakerModuleV1"},"d277cacd-5268-4272-9f8b-c1a4267e2465:thermocyclerModuleType":{"model":"thermocyclerModuleV2"},"b6ecaa76-3d6a-4fb2-a47f-d27a311b67ea:temperatureModuleType":{"model":"temperatureModuleV2"}},"labware":{"e11106c2-2139-43e4-bf4f-93683806128f:opentrons/opentrons_flex_96_tiprack_1000ul/1":{"displayName":"Opentrons Flex 96 Tip Rack 1000 µL (1)","labwareDefURI":"opentrons/opentrons_flex_96_tiprack_1000ul/1"},"8d7c3a6a-3244-4664-bddd-d97ceb406c30:opentrons/opentrons_flex_96_tiprack_200ul/1":{"displayName":"Opentrons Flex 96 Tip Rack 200 µL","labwareDefURI":"opentrons/opentrons_flex_96_tiprack_200ul/1"},"931035fc-f041-4d1c-b664-0f3f92e74a47:opentrons/opentrons_flex_96_tiprack_200ul/1":{"displayName":"Opentrons Flex 96 Tip Rack 200 µL (1)","labwareDefURI":"opentrons/opentrons_flex_96_tiprack_200ul/1"},"91ec8f0c-b026-40fe-80d8-e754fd6409f3:opentrons/nest_96_wellplate_2ml_deep/4":{"displayName":"NEST 96 Deep Well Plate 2 mL","labwareDefURI":"opentrons/nest_96_wellplate_2ml_deep/4"},"7a01a882-27a1-4f47-b17d-f95ce0bfff98:opentrons/agilent_1_reservoir_290ml/3":{"displayName":"Agilent 1 Well Reservoir 290 mL","labwareDefURI":"opentrons/agilent_1_reservoir_290ml/3"}}}},"metadata":{"protocolName":"8-Channel 1000ul Supernatant Removal DW96 Well","author":"Dre/Ben","description":"","source":"Protocol Designer","created":1764690188354,"lastModified":1764692344326}}"""
