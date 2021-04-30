# Instructions for OT2-Colony-Picking
Rita R. Chen  
<p align="center">
  <img src="https://user-images.githubusercontent.com/32885235/95505810-fb33c200-097c-11eb-9cb9-3f299bb68920.png" />
</p>


## About
This document is intended to guide users through OT2 Colony Picking workflow on E. coli systems. This workflow enables colony detection and selection of dual-color colony-forming units (CFUs) using the OT2 liquid handling robot by Opentrons. This includes:
- Performing dual-color colony detection for blue-white screening with open-source software, [OpenCFU](http://opencfu.sourceforge.net/).
- Executing dual-color colony selection on a rectangular agar plate with circular colony growth regions of colony-forming units (CFUs).

In addition, this workflow is a continuation of a previously established end-to-end [modular cloning workflow](https://github.com/DAMPLAB/OT2-MoClo-Transformation-Ecoli) using the OT2 liquid handling robot by OpenTrons.

## Materials
Below we list the materials previously used to implement OT2 Colony Picking workflow. We recommend starting with these consumables, however certain standard labwares may be altered. Labware needs to be defined carefully when working with OpenTrons OT-2 liquid handling robot and changes to labware requires the user to update the protocol scripts and the labwares used during the execution of OT2 Colony Picking runs. In addition, a custom labware, *point_for_colony_picking*, is created using Opentrons [Custom Labware Creator](https://labware.opentrons.com/create/) and applied in the implementation of the OT2 Colony Picking workflow. Here is a general [OpenTrons’ Guideline](https://support.opentrons.com/en/articles/3137426-what-labware-can-i-use-with-the-ot-2) for utilizing labware for users new to OT2 and additional details regarding labware can be found on [OpenTrons Labware Library](https://labware.opentrons.com/).

### Software:
- OpenTrons OT-2 App (Version 3.10.3 or later)
- Python 3
- [OT2 Colony Picking GitHub repository](https://github.com/DAMPLAB/opentrons_protocols/tree/main/OT2-Colony-Picking)

### Hardware:
- [OpenTrons OT-2](https://opentrons.com/ot-2)
- [OpenTrons P10 Single-Channel Generation 1 Electronic Pipette](https://opentrons.com/pipettes)
- [OpenTrons P300 Multi-Channel Generation 2 Electronic Pipette](https://opentrons.com/pipettes)

### Consumables & Reagents:
- [OpenTrons 20 µL Filter Tips](https://shop.opentrons.com/collections/opentrons-tips/products/opentrons-20ul-filter-tips)
- [OpenTrons 200 µL Filter Tips](https://shop.opentrons.com/collections/opentrons-tips/products/opentrons-200ul-filter-tips)
- [USA Scientific 96 Deep Well Plate 2.4 mL](https://www.usascientific.com/plateone-96-deep-well-2ml/p/PlateOne-96-Deep-Well-2mL)
- [Agilent 1 Well Reservoir 290 mL](https://www.agilent.com/store/en_US/Prod-201252-100/201252-100)
- [Thermo Scientific Nunc OmniTray Single-Well Plate](https://www.fishersci.com/shop/products/nunc-omnitray/12565296?searchHijack=true&searchTerm=12565296&searchType=RAPID&matchedCatNo=12565296)
- Additional Reagents:
    - LB Agar Plate (70mL/Plate)
    - LB Growth Media
    - Antibiotic(s) diluted to the proper concentration

## Protocol
### OT-2 Preparation
Follow the Opentrons guidelines for setting up the OT-2 before executing any protocols.

### General Installation
Using any web browser, navigate to the [GitHub directory](https://github.com/DAMPLAB/opentrons_protocols/tree/main/OT2-Colony-Picking) and follow the instructions provided in the **README.md** for the Software Requirements to install the necessary software setup.

This workflow is a continuation of a previously established end-to-end [modular cloning workflow](https://github.com/DAMPLAB/OT2-MoClo-Transformation-Ecoli) using the OT2 liquid handling robot by OpenTrons.

### Construct Supplemental CSV File
Using any web browser, navigate to the following [GitHub directory](https://github.com/DAMPLAB/opentrons_protocols/tree/main/OT2-Colony-Picking), and follow the Step 1 of the Initial Setup for OT2 Colony Picking to generate necessary supplemental CSV file, LB agar plate map. Examples of LB agar plate map, ***Agar_Plate.csv***, are provided in the examples folder of the GitHub directory.

### Generate Opentrons Custom Labware
Using any web browser, navigate to the Opentrons Help Center for [creating custom labware definitons](https://support.opentrons.com/en/articles/3136504-creating-custom-labware-definitions), and follow the instructions provided to create your own definition of a custom labware. The custom labware definition for ***point_for_colony_picking*** is provided in the examples folder of the GitHub directory.

### Generate OT-2 Liquid Handler Instructions for Colony Picking Protocol
1. Gather the agar plate from the 37°C incubator and take an image with the benchtop gel imager (gel imager information). Be sure to follow the Image and Export Condition provided below.    
  **NOTE:** Use the ***location indicator A1*** from the previous modular cloning DNA assembly protocol, and place the corner of the Agar Plate that’s marked with ***A1 location indicator*** as the ***upper-right corner*** inside the gel imager when taking the image.
2. Image and Export Conditions:
  1. Navigate to Application *Image Lab 6.0*
  2. Open *New Protocol*
  3. Under *Acquisition Settings*
    1. Select checkbox for *1: Gel Imaging*
    2. For ***Application***, select *Colorimetric* from category *Blots (No Filter, White Epi Illumination)*
    3. For ***Imaging Area***, select option *Entire image area:*, and input *26.0 x 19.4 cm (WxL)* as setting
    4. For ***Image Exposure***, select option *Intense Bands* for *The software will automatically optimize the exposure time for…*
    5. For ***Display Options***, select *Spectrum* for ***Image Color***
    6. Select the yellow *Position Gel* button on the lower left corner, and specify the Camera Zoom value to *26.0 x 19.4* to capture the entire image
    7. Select the green *Run Protocol* button
    8. When image is generated, export the image for setting ***Export for Publication*** at *300dpi* as *.png format*

### Execute Colony Picking Protocols on OT-2
1. Using any web browser, navigate to the [GitHub directory](https://github.com/DAMPLAB/opentrons_protocols/tree/main/OT2-Colony-Picking) and follow the instructions provided in the **README.md** for the Software Requirements to install the necessary software setup.    
  **NOTE:** Save image(s) of your plate(s) to the ***ot2_colony_picking/data/images*** folder (the image saving location can be changed in *settings.yaml*). By default, when executing the protocol scripts, the most recently created images in this folder will be used first.
2. Open up the command-line interface at *colony_picking* folder, and input 'python3 colony_picking_generator.py' in your command-line interpreter.
3. Select the ***Agar_Plate.csv*** file that is previously generated
4. A protocol named 'colony_picking_protocol.py' and a CSV file named ***culture_block.csv*** will be saved to the same output folder that's specified during the previous protocol generation.
5. Open up OT2 APP, and upload 'colony_picking_protocol.py' to the Protocol Tab.
6. Once the protocol is uploaded, following the calibration instructions provided by the OT2 APP. Place the agar plate we have retrieved from the 37 °C incubator (Agar Plate), Agilent 1-well Reservoir containing LB growth media and appropriate antibiotic resistance (Reagent Plate), USA Scientific 96 deep-well plate (Culture Block), and one of each Opentrons 20 μL and 200 μL filtered tip racks onto the deck of the OT-2 liquid handler.    
  **NOTE:** Pipette replacement might be necessary, please follow the instructions provided by OT2 App.    
  **NOTE:** When calibrating for the Agar Plate, be sure to align the tip of the pipette to the upper leftmost corner of the Agar Plate to allow most accurate procedural results for Colony Picking executions.
7. Once the calibration processes are completed, proceed directly to running the protocol.    
  **NOTE:** Always allow the robotic liquid handler to complete the execution of a script before trying to access the deck space.
8. Remove the culture block and seal it with an oxygen permeable sealing membrane. Place the culture clock inside the 37 °C shaker with 900 rpm shaking condition overnight.    
  **NOTE:** The first column of the culture block will always contain controls, LB growth media with appropriate antibiotic(s).
9. We used this workflow to select 88 bacteria colonies during the protocol.

<p align="center">
  <img src="https://user-images.githubusercontent.com/32885235/113929104-a2bf6f00-97bd-11eb-88d2-ba575ff7d20c.png" />

  **Figure 1:** Workflow for executing Colony Picking protocols on OT-2.     
  **(A)** Representative OT-2 deck layout with labwares and pipette tip boxes placement locations.     
  **(B)** Representative OT-2 deck layout for plate setup instructions
</p>
