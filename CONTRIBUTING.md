# Contributing to DAMPLab Opentrons Protocols
 
Thank you for contributing to the DAMP Lab protocol repository! Please follow the guidelines below to keep the repo organized and consistent.
 
## Adding a Protocol
 
Each protocol should be placed in its own folder under the appropriate robot directory (`protocols/OT-2/` or `protocols/OT-Flex/`) and include:
 
- The protocol `.py` file
- A `README.md` describing the protocol (labware, volumes, and workflow)
- Input files (e.g., `.xlsx` sample sheets), if applicable
- Custom labware definitions (if only used by that protocol)
 
## Custom Labware
 
- Shared labware definitions (used by multiple protocols) should be placed in **`custom_labware/`**
- If a labware definition is only used by a single protocol, it may be stored inside that protocol's folder
- Do not duplicate shared labware definitions unless absolutely necessary
 
## Archiving Old Work
 
- **Do not delete** old protocols or labware
- Move unused or deprecated items to the **`archive/`** folder instead
 
## Naming Conventions
 
- Use lowercase with underscores for folder and file names
- Protocol file name should match the folder name
- Labware files should be clearly named and include volume if applicable (e.g., `greiner_96_deep_wellplate_2000ul.json`)

## General Guidelines
 
- OT-2 protocols go in `protocols/OT-2/`
- OT-Flex protocols go in `protocols/OT-Flex/`
- Every protocol folder must include a `README.md`
- Keep shared resources in their designated folders to avoid duplication
- Use clear, descriptive commit messages. [Conventional Commits](https://www.conventionalcommits.org/) format is encouraged but not required (e.g., `docs: update README`, `feat: add new OT-2 protocol`)