> [!WARNING]
> Not validated.
# BSA Dilutions in Duplicate (OT-Flex)
## Overview
The protocol performs automated serial dilutions of BSA in 2 duplicates using the Opentrons Flex robot with a 1-channel 1000 µL pipette. The protocol is currently inflexible and only performs the set dilution process displayed below:
<img width="680" height="567.2" alt="Screenshot 2026-05-26 102554" src="https://github.com/user-attachments/assets/13179b49-0864-43ce-a262-7972b876983c" />
## Protocol Materials
- Robot: Opentrons Flex
- Pipette: Flex 1-Channel 1000 uL
- Tips: One 50 uL tip rack, one 200 uL tip rack and one 1000 uL tip rack
- Reservoir: USA Scientific 12-well reservoir 22 mL
- Others: One Opentrons 24 tube rack holder, and seven 1.5 mL snapcap tubes. 
## Protocol Summary
### Setup
Before automation, download the bsa_serial_dilution.py file, and import it into the Opentrons software.\
Set up the Flex according to what the software shows. 
>[!IMPORTANT]
>The liquid volume displayed is the minimum; perfect liquid dispersion may not always be guaranteed, so it is suggested to add extra reagent to prevent bubbles every time.
<details>
<summary>Click here for further information about how to set-up for your first time</summary>
  What the screen should look like when loaded. 
  <img width="1531" height="299" alt="image" src="https://github.com/user-attachments/assets/5f80b3b5-0a5f-4a53-b624-a169e2c26481" />
  
  To see robot set-up on the software, press on your chosen protocol. 
  <img width="800" height="405" alt="image" src="https://github.com/user-attachments/assets/1ca5895e-dd85-4b84-956a-730e730ac0ec" />
  
  Click on the 'Visualize' button
  In this window, you can view the specific labware name when hovering over it, along with the steps with well view, tip pickup usage, etc.
  >Make sure to see step 1 or 2 to make sure all liquid has been loaded before moving on to the next step.
  <img width="800" height="484" alt="image" src="https://github.com/user-attachments/assets/be943cf2-f015-4152-ac51-b64af2421700" />
  
  When clicking on labware, specifics like liquid type and liquid volume are shown.\
  <img width="478" height="374" alt="image" src="https://github.com/user-attachments/assets/fe6c7f59-05e1-4fc0-b8c8-14c592bba52e" />
</details>
Example Setup image: <img width="761" height="600" alt="image" src="https://github.com/user-attachments/assets/4fa9f1dd-3b30-4eff-a561-6ec041e6c919" />

### Procedure
1. Place tubes in spots A1-A3 and B1-B3. Row A holds the 1st set of BSA dilutions, and row B holds the 2nd set (duplicate). Tube spots A6 and B6 will hold blanks.
2. Using the same tip, transfer all the water into the tubes.
3. Transfer BSA to the first column of tubes.
4. Perform serial dilution for row A.
5. Perform serial dilution for row B.

## Protocol Validation
- Water test: Testing with water and 10% glycerol with water coloring to validate even mixing.
- BCA Assay: Measure protein concentration through the BCA assay protocol.
- Compare manual and automated serial dilution using 10% glycerol and red water coloring, and then read the result in a plate reader. Absorbance values should be close.

## Protocol Updates
- Ver. 5: Improved step labelling through protocol comments to simplify understanding. 
- Ver. 4: Added 50 uL tip for even more accurate pipetting, removed mixing for last dilution of 1:10, and adjusted flow rate further.
- Ver. 3: Changed dilution patterns for consistency, and simplified code for easier editing.
- Ver. 2: Changed tip size for transferring 200 uL volumes to increase accuracy. 
- Ver. 1: Code is updated with mixing at different heights for more even mixing.
