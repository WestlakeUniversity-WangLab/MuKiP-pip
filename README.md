[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

# MuKiP

The **Mu**lti-scale **Ki**netic modeling **P**latform (MuKiP) is a comprehensive software toolkit designed for 
addressing complex physicochemical processes at three-phase interfaces in heterogeneous catalysis, currently under 
development by Prof. Tao Wang’s group at Westlake University. It is written in Kotlin/Java and published on PyPI. 
The first release of this platform currently focuses on efficient descriptor-based microkinetic modeling and will, 
in the future, enable multiple multi-scale modules that integrate factors such as electrochemistry, reactor kinetics, 
and mass transport. Designed for modular construction of multi-scale kinetic models, it aims to automate the assembly 
of systems of equations using algebraic modules and to solve them efficiently with advanced algorithms. The platform 
also provides open interfaces, allowing third-party developers to create and distribute custom addons.

## Install

`pip install mukip`

If your device cannot connect to the internet, you need to manually download and extract the JRE as instructed.

### System Requirements

- **64-bit OS Required:** This application is designed exclusively for 64-bit systems.

### ⚠️ Known Issues

- **macOS (AArch64):** There is a known stability issue on ARM64 architecture (Apple Silicon). 
  Users may experience random crashes (`SIGBUS`). Use at your own risk.

## Format of Setup file

The reaction network, parameters, and workflow are all defined in a setup file. The program initializes by reading this
file. For the setup file specification, please refer to [Format](docs/Format.md), or adapt the files in examples.

## Examples

Example scripts demonstrating the usage of `mukip` are available in the GitHub repository.

The examples include:
- Basic model initialization and execution
- Running simulations with different samplers
- Accessing thermodynamic and kinetic results
- Plotting and data export

Obtain example data and scripts:

- **Local copy** (if you cloned the repository): [src/examples/example.py](src/examples/example.py)
- **Download from GitHub**: [Download examples](https://github.com/WestlakeUniversity-WangLab/MuKiP-pip/blob/main/src/examples/example.py)

### Test Data

The test data used in the examples is derived from these following publication:

> **DOI: [10.1016/j.jcat.2024.115749](https://doi.org/10.1016/j.jcat.2024.115749)**
> 
> **DOI: [10.1021/cs200055d](https://doi.org/10.1021/cs200055d)**
> 
> **DOI: [10.1021/jacs.5b12087](https://doi.org/10.1021/jacs.5b12087)**
> 
> **DOI: [10.1021/acscatal.1c04347](https://doi.org/10.1021/acscatal.1c04347)**

 ## Citation

If you use this software in your research, please cite the following paper:

> [Not published yet](https://doi.org/)

## 📜 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International 
(CC BY-NC-SA 4.0)** license.  
See the full text here: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Acknowledgement

This project was inspired by [CatMAP](https://github.com/SUNCAT-Center/catmap).
While the overall program structure and design ideas were influenced by this project, 
all implementation in this repository was written independently.



