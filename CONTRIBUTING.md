# Contributing to DAMPLab Opentrons Protocols

Thank you for contributing to the DAMP Lab protocol repository! Please follow the guidelines below to keep the repo organized and consistent.

## Submission Workflow

1. Fork this repository by clicking the Fork button in the top right corner of the repo page on GitHub. This creates your own personal copy of the repo under your GitHub account.
2. Create a branch in your fork: `git checkout -b your-protocol-name`
3. Add your files to your branch following the folder structure and naming conventions below.
4. Open a Pull Request by clicking Contribute → Open a Pull Request on your fork. Provide a short title and description of what your protocol does.
5. Wait for approval. A maintainer will review your PR and either approve it to be merged or leave comments requesting changes.

> ⚠️ Do not attempt to push directly to `main`, it is protected and your push will be rejected.

## Adding a Protocol

Place each protocol in its own folder under `protocols/OT-2/` or `protocols/OT-Flex/`.

Each protocol folder should include:
- A `.py` protocol file
- A `README.md` (labware, volumes, workflow)
- Input files (e.g., `.xlsx`), if needed
- Custom labware (if specific to that protocol)

**Robotics Colony Members:**

Place shared/assigned work in `protocols/OT-Flex/ColonyPlayground/` and prefix folders with your BU username (e.g., `jsmith_supernatant_removal`).  
Individual protocols should go directly in `protocols/OT-Flex/`.

## Custom Labware

- Shared labware definitions (used by multiple protocols) should be placed in `custom_labware/`
- If a labware definition is only used by a single protocol, it may be stored inside that protocol's folder
- Do not duplicate shared labware definitions unless absolutely necessary

## Naming Conventions

- Use lowercase with underscores for folder and file names
- Protocol file name should match the folder name
- Labware files should be clearly named and include volume if applicable (e.g., `greiner_96_deep_wellplate_2000ul.json`)
- Name protocol folders descriptively to avoid conflicts

## General Guidelines

- OT-2 protocols go in `protocols/OT-2/`
- OT-Flex protocols go in `protocols/OT-Flex/`
- Every protocol folder must include a `README.md`
- Keep shared resources in their designated folders to avoid duplication
- Use clear, descriptive commit messages. [Conventional Commits](https://www.conventionalcommits.org/) format is encouraged but not required (e.g., `docs: update README`, `feat: add new OT-2 protocol`)