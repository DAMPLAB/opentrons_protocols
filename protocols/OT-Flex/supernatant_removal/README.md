# Supernatant Removal Protocol: GROQ-SEQ Pipeline (OT-Flex)

## Overview
This protocol performs automated supernatant removal from a 96-well deep well plate using the Opentrons Flex robot with an 8-channel 1000 µL pipette. The protocol is optimized to protect centrifuged pellets by using slow offset aspiration and fast dispense to waste.

This protocol is part of the GROQ-SEQ pipeline.

## Protocol Summary
- Robot: Opentrons Flex
- Pipette: Flex 8-Channel 1000 µL
- Plate: Greiner 96 Deep Well Plate (2000 µL)
- Volume removed: 1800 µL per well
- Aspiration: Slow, offset from pellet
- Dispense: Fast to reservoir (waste)
- Tips: Single tip set used across column transfers

## Labware Required
This protocol requires the following custom labware:

custom_labware/greiner_96_deep_wellplate_2000ul.json