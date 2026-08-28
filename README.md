[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

# MuKiP

The **Mu**lti-scale **Ki**netic modeling **P**latform (MuKiP) is a comprehensive software toolkit designed for 
addressing complex physicochemical processes at three-phase interfaces in heterogeneous catalysis, currently under 
development by Prof. Tao Wang’s group at Westlake University. It is written in Kotlin/Java and published on PyPI. 
The current release of this platform focuses on efficient descriptor-based microkinetic modeling and have implemented 
reactor kinetics. In the future, it will further enable multi-scale modules that integrate factors including 
mass transport. Designed for modular construction of multi-scale kinetic models, it aims to automate the assembly 
of systems of equations using algebraic modules and to solve them efficiently with advanced algorithms. The platform 
also provides open interfaces, allowing third-party developers to create and distribute custom addons.

## Install

`pip install mukip`

If your device cannot connect to the internet, you need to manually download and extract the JRE as instructed.

### System Requirements

- **64-bit OS Required:** This application is designed exclusively for 64-bit systems.

### ⚠️ Known Issues

- **macOS (Apple Silicon):** This program has known stability issues when run natively on ARM64 architecture and may 
cause random `SIGBUS` crashes. To avoid this, always execute the program under x86_64 emulation by using the 
`arch -x86_64` prefix, e.g., `arch -x86_64 python your_script.py`. It is crucial that all Python dependencies 
(such as `matplotlib`) are also installed for x86_64. The simplest way is to open an x86_64 shell with 
`arch -x86_64 /bin/zsh` (or `/bin/bash`), then install all required packages via `pip install -r requirements.txt` 
inside that shell. This ensures both the program and its libraries run in the same x86_64 environment and prevents 
architecture mismatch issues.

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

## Future Plans

More advanced functionalities, including reactor kinetics modeling, electrochemical kinetics modeling, and continuum transport models, 
will soon be released also in a comprehensive and efficient way.

## 📜 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International 
(CC BY-NC-SA 4.0)** license.  
See the full text here: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Acknowledgement

The descriptor-based microkinetic modeling part was inspired by [CatMAP](https://github.com/SUNCAT-Center/catmap).
All implementations in this repository were written independently in Kotlin.



