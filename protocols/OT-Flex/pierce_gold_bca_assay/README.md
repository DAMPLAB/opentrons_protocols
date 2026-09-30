> [!WARNING]
> Not validated.
> This protocol is a work in progress, and the results have not been validated. 

# Pierce Dilution-Free Rapid Gold BCA Protein Assay Kit (OT-Flex)

## Overview
This protocol performs automated protein quantification using the Pierce Gold BCA Assay Kit in a 96-well plate format. This protocol can process 96 samples per run using the Opentrons Flex liquid handler, equipped with a 1000 uL 8-channel and 50 uL 1-channel pipette. The protocol is flexible, allowing unique combinations of unknowns and replicates. The Assay Kit has a working range of 20 to 10,000 μg/mL.

<details>
<summary>Click here for Pierce Gold BCA Assay Kit Information</summary>
  - Reference the DAMP Lab protocols.io Workspace, and see the protocol entitiled "Automated (Opentrons Flex) Pierce™ Dilution-Free™ Rapid Gold BCA Protein Assay Kit". 
  - Reference the ThermoFisher product [here](https://www.thermofisher.com/order/catalog/product/A55862?ef_id=Cj0KCQjwkYLPBhC3ARIsAIyHi3S2QQBcdnyjjJAmqoOAEseGD5ktgiSlgmm253NlINClxLJku0LY_pcaAqCMEALw_wcB:G:s&s_kwcid=AL!3652!3!772389377757!!!g!!!22974799911!183617388854&cid=bid_pca_wwa_r01_co_cp1359_pjt0000_bid00000_0se_gaw_dy_con_con&gad_source=1&gad_campaignid=22974799911&gbraid=0AAAAADxi_GTrlxOZN5nMBP6P5_vqFkAtX&gclid=Cj0KCQjwkYLPBhC3ARIsAIyHi3S2QQBcdnyjjJAmqoOAEseGD5ktgiSlgmm253NlINClxLJku0LY_pcaAqCMEALw_wcB)
  </details>

## First-Time Use Instructions
1. Download the pierce_gold_bca_assay.py file and import it into the Opentrons software.
2. Upload the file to the Opentrons Flex.

<details>
<summary>Click here for further information about how to set-up for your first time</summary>
  This is what the screen should look like when loaded. Note that this uses the Promega Miniprep script as an setup example. 
  <img width="1531" height="299" alt="image" src="https://github.com/user-attachments/assets/5f80b3b5-0a5f-4a53-b624-a169e2c26481" />
  
  To see robot set-up on the software, press on your chosen protocol. 
  <img width="800" height="405" alt="image" src="https://github.com/user-attachments/assets/1ca5895e-dd85-4b84-956a-730e730ac0ec" />
  
  Click on the 'Visualize' button.
  In this window, you can view the specific labware name when hovering over it, along with the steps with well view, tip pickup usage, etc.
  >Make sure to see step 1 or 2 to make sure all liquid has been loaded before moving on to the next step.
  <img width="800" height="484" alt="image" src="https://github.com/user-attachments/assets/be943cf2-f015-4152-ac51-b64af2421700" />
  
  When clicking on labware, specifics like liquid type and liquid volume are shown.\
  <img width="478" height="374" alt="image" src="https://github.com/user-attachments/assets/fe6c7f59-05e1-4fc0-b8c8-14c592bba52e" />
</details>


## Parameters
>[!IMPORTANT]
>The required liquid volumes displayed on the Flex are the minimum. Perfect liquid dispersion may not always be guaranteed, so it is suggested to follow the amount specified in the protocol on protocols.io.

1. Sample Count: Enter the total number of samples to be run, excluding replicates and excluding unknowns. 
2. Sample Replicates: Enter the number of replicates per sample.
3. Well Type: Select appropriate type of resevoir.


## Deck Layout
Example Setup for 4 unknowns: <img width="399" height="316" alt="image" src="https://github.com/user-attachments/assets/6aa10b0c-dbd5-4398-a208-318e86ddb5c3" />


### Labware Required
This protocol requires the following custom labware:

[custom_labware/nunc_96_wellplate_optical_bottom_400ul.json](https://github.com/bingling-w/opentrons_protocols/blob/4070e261d453abb1e0a81ed08c07d66fa3a36a12/custom_labware/nunc_96_wellplate_optical_bottom_400ul.json)

## Automated Procedure Walk-Through
1. The 50 uL 1-channel pipette picks up a 50 uL tip.
2. The 50 uL pipette aspirates 10 uL × (number of replicates) of standard solution 1, located in well A1 of the standards tube rack.
3. 10 uL of standard 1 is dispensed into well A1 of the 96-well plate.
     - If the replicates parameter is greater than 1, the same pipette tip continues dispensing 10 uL into the adjacent wells in that row (A2, A3, etc.).
4. The used tip is discarded.
5. Steps 2–4 are repeated for all 8 standards in the tube rack.
6. The 50 uL 1-channel pipette picks up a 50 uL tip.
7. The 50 uL pipette aspirates 10 uL × (number of replicates) of sample 1, located in well A1 of the samples tube rack.
8. 10 uL of sample 1 is dispensed into the row of wells immediately following the standards' columns.
     - For example, if replicates = 2, the standards occupy columns 1 and 2, and sample 1 is dispensed into wells A3 and A4.
9. The used tip is discarded.
10. Steps 6–9 are repeated for the number of unknowns in the tube rack.
11. The 50 uL 1-channel pipette picks up a 50 uL tip.
      - If the protocol requires more than 200 uL of reagent B, this step is skipped.
12. The 1000 uL 8-channel pipette picks up eight 200 uL tips.
13. The 8-channel pipette moves to well A1 of the reservoir, aspirates the necessary amount of reagent A, and dispenses it into well A2 of the same reservoir.
14. The used tips are discarded.
15. The 1-channel pipette moves to well A6 of the standards tube rack, where reagent B is held, aspirates the necessary amount of reagent B, and dispenses it into well A2 of the reservoir.
      - If the protocol requires more than 200 uL of reagent B, the 8-channel pipette instead picks up one 200 uL tip to aspirate and dispense reagent B.
16. Reagent A and reagent B are mixed thoroughly by aspirating and dispensing the liquid at different heights.
17. The used tips are discarded.
18. The 8-channel pipette picks up a new set of tips to aspirate and dispense 200 uL of working reagent into the 96-well plate.
      - Depending on how many columns have unknowns, the pipette picks up the necessary number of tips.
19. After all standards and unknowns have received working reagent, the heater-shaker activates to shake the 96-well plate at 825 rpm for 25 seconds.
20.  After 5 minutes have passed, the protocol is completed.

## Protocol Validation Runs
- $R^2$ value close to 1, signaling strong correlation between absorbance and concentration values.
- Food coloring validation:
  - Using 10% glycerol, do a serial dilution with red food coloring as standards.
  - Add red coloring to reagent B, and use 10% glycerol as reagent A.
  - Do an automated and manual run of the protocol.
  - Compare the standard curves of the two; the slopes of both should be close when using the same standards.


## Protocol Updates
- Ver. 14: Code now contains parameters. 
- Ver. 13: Increased the number of unknown samples allowed for 3 replicates, and added an extra rack of 200 uL tips for when the unknown number exceeds 16 and replicates equal 3, to prevent running out of tips. When reagent B volume exceeds 150 uL, switches to a 200 uL tip using the 8-channel pipette for quicker transfer (wastes 8 more tips, but is much more efficient when reagent B volume is high). 
- Ver. 12: Includes flexible input for changing module locations and changing pipette locations (left or right mount) to further simplify the process, especially for new users. 
- Ver. 11: Includes flexible input for v-bottom or diamond-bottom wells, accessible for users with different labware. 
- Ver. 10: Changed flow rate to be even slower, and added correct dead volume for working reagent. Slower flow rate results in more accurate pipetting, and the correct dead volume reduces liquid waste.
- Ver. 9: Code is made to blow out, touch tip, and blow out again to account for the viscosity of unknowns and standards, to prevent droplets. 
- Ver. 8: Code is optimized to dispense and aspirate more slowly for more accurate pipetting. 
- Ver. 7: Code is optimized to use small-volume pipette arms and tips to minimize the machine's % error.
- Ver. 6: Code is optimized to use a partial nozzle setup for the 8-channel pipette when there is not a full column, to reduce reagent waste and tip waste.
- Ver. 5: Code is made so the pipette goes to the very bottom of the reservoir to reduce dead volume. 
- Ver. 4: Code is optimized to distribute reagent B uniformly across the reservoir, and mixed with reagent A at different heights for a more uniform mixture. 
- Ver. 2: Code contains mixing and blow-out steps, though it does not mix as well because the tip can mix a maximum of 50 uL volumes. 
- Ver. 1: Code is optimized for flexibility, allowing the user to change the protocol based on how many replicates and unknowns are necessary.
