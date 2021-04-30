# OT2 Colony Picking in E. coli Workflow

OT-2 API V2 protocol scripts for Opentrons robot with material for using Ot-2 liquid handler to perform colony picking in E. coli workflow

This workflow enables colony detection and selection of dual-color colony-forming units (CFUs) using the OT2 liquid handling robot by Opentrons. This includes:
- Performing dual-color colony detection for blue-white screening with open-source software, [OpenCFU](http://opencfu.sourceforge.net/).
- Executing dual-color colony selection on a rectangular agar plate with circular colony growth regions of colony-forming units (CFUs).

In addition, this workflow is a continuation of a previously established end-to-end [molecular cloning workflow](https://github.com/DAMPLAB/OT2-MoClo-Transformation-Ecoli) using the OT2 liquid handling robot by OpenTrons.

Full setup instructions can be found [here](https://github.com/DAMPLAB/OT2-Colony-Picking/blob/master/instructions.md).

All code for this project is freely distributed for academic and commercial uses under the MIT license.

## Software Requirements

1. [Python 3](https://www.python.org/downloads/)

2. [OT2 APP](https://opentrons.com/ot-app)

3. Clone this [repository](https://github.com/DAMPLAB/OT2-Colony-Picking) to a local computer.

## Colony Picking

### Getting Started

Users looking to implement the OT2 Colony Picking in E. coli workflow are encouraged to consult the [instructions](https://github.com/DAMPLAB/OT2-Colony-Picking/blob/master/instructions.md). If you are looking to contribute to this project, please raise an issue or pull request. Otherwise, feel free to reach out to [rychen58](mailto:richen@bu.edu).

### Initial setup

1. Prepare 1 CSV file (which can be produced in Excel) representing the LB agar plate map. The LB agar plate map may contain up to 93 regions containing transformed bacterial colonies, 8 rows by 12 columns, with each cell containing the name for DNA constructs transformed into the selected bacteria strain and empty wells left blank. The CSV file should represent an LB agar plate containing 96 circular regions with bacterial colony-forming units (CFUs) previously created by the users.

### Generating protocol

2. Run the OT2-Colony-Picking/colony_picking/colony_picking_generator.py using Python (e.g. typing `python3 colony_picking_generator.py` in the command line). Select the plate map, and an output folder for the protocol when prompted.

3. A protocol named `colony_picking_protocol.py` should be saved in the output folder.

## Authors

* **Rita R. Chen** - [rychen58](https://github.com/rychen58)
* **Nick Emery** - [emernic](https://github.com/emernic)
