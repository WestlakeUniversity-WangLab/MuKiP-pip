# Setup File Format (JSON5)

The program reads a **setup file** in **JSON5** format. This file defines all the components and parameters needed for
the computation.

The program has several **component classes**. Each class can have multiple concrete implementations, and components
can inherit from each other. Some component classes are **abstract** – they define common behavior but cannot be used
directly. Only **non‑abstract** (concrete) components can be instantiated and defined in the setup file. Every concrete
component is defined as a JSON object inside the setup file. If a component class does **not** specify a default
implementation, the `"class"` field inside its JSON object tells the program which specific implementation to use.
---

# ReactionModel

`ReactionModel` is a component that defines global settings, elementary reactions, species attributes, and the overall workflow.  
The content of the setup file is exactly the definition of a `ReactionModel`.  
Currently, there is only one implementation of `ReactionModel`, called `KineticModel`, which is also the default type.

It contains the following fields:

### `log` (string, optional, default = `null`)
Controls logging (console and file output).

- `null` (default): Print logs to the console only. No log file is created.
- `"on"`: Print logs to the console **and** create a log file in the same folder as the setup file.
- `"off"`: Turn off all logging – nothing printed to console, no log file.

### `convergence_precision` (integer, default = `50`)
Convergence precision – number of decimal places used to decide if a solution has converged.  
This value must be higher than the smallest quantity in your system; otherwise, the solver may fail to converge.

### `decimal_precision` (integer, default = `75`)
Decimal precision – number of decimal places kept during all high‑precision numerical calculations.  
This must be **greater than** `convergence_precision`. A good rule of thumb is to set it at least 20 higher.

### `max_precision` (integer, default = `400`)
Maximum precision – the largest allowed total number of decimal digits (including both sides of the decimal point). Used to prevent numbers from becoming too large.  
This should be **significantly larger** than `decimal_precision`. You normally never need to change it.

### `extra_atoms` (JSON array of strings, optional)
List of JSON file names that define extra atoms.  
The files can be placed in the program directory or in your project directory.  
Reference format:  
[https://github.com/WestlakeUniversity-WangLab/MuKiP/blob/main/src/main/resources/com/wang_lab/mukip/Atoms.json](https://github.com/WestlakeUniversity-WangLab/MuKiP/blob/main/src/main/resources/com/wang_lab/mukip/Atoms.json)

### `extra_molecules` (JSON array of strings, optional)
List of JSON file names that define extra molecules.  
The files can be placed in the program directory or in your project directory.  
Reference format:  
[https://github.com/WestlakeUniversity-WangLab/MuKiP/blob/main/src/main/resources/com/wang_lab/mukip/Molecules.json](https://github.com/WestlakeUniversity-WangLab/MuKiP/blob/main/src/main/resources/com/wang_lab/mukip/Molecules.json)

### `extra_shomate` (JSON array of strings, optional)
[![Status](https://img.shields.io/badge/status-not%20implemented-red)]()

List of JSON file names that define extra Shomate parameters.  
The files can be placed in the program directory or in your project directory.  
Reference format:  
[https://github.com/WestlakeUniversity-WangLab/MuKiP/blob/main/src/main/resources/com/wang_lab/mukip/ShomateGas.json](https://github.com/WestlakeUniversity-WangLab/MuKiP/blob/main/src/main/resources/com/wang_lab/mukip/ShomateGas.json)

### `parameter` (JSON object)
Fixed parameters used in the reaction model.  
Keys are parameter names, values are in form of float.  
Common examples: temperature (`T`), pressure (`p`), pH, etc. You can also add custom parameters.  
These values can be used inside expressions.

### `default_thermo` (JSON object)
Sets the default thermodynamic correction method for each type of species. The correction is applied on top of the species’ formation energy.  
Keys are species types, values are thermodynamic correction methods.  
The species type tree (child types override the parent type):
```
Species
├─ Electron
├─ Site
└─ MoleculeSpecies
   ├─ Fluid
   │   ├─ Gas
   │   ├─ Liquid
   │   └─ Aqua
   └─ SurfaceSpecies
      ├─ Adsorbate
      └─ Transition
```
Available thermodynamic correction methods:

| Method Name    | Description                                                                                                                                                                                                              |
|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Frozen`       | No correction.                                                                                                                                                                                                           |
| `HS`           | Read `H` and `S` from [`SpeciesAttributes`](#species-JSON-object) and use them as enthalpy and entropy.                                                                                                                  |
| `Shomate`      | Compute using Shomate parameters. The Shomate data must cover the temperature range of the species.                                                                                                                      |
| `Harmonic`     | Harmonic oscillator approximation – includes vibrational enthalpy, zero‑point energy, and vibrational entropy.                                                                                                           |
| `IdealGas`     | Ideal gas approximation – includes translational & rotational enthalpy, heat capacity, vibrational enthalpy, zero‑point energy, translational/rotational/electronic/vibrational entropy, and pressure‑dependent entropy. |
| `ZeroPoint`    | Include only the zero‑point energy.                                                                                                                                                                                      |
| `ZeroPointHS`  | Read `H` and `S` from [`SpeciesAttributes`](#species-JSON-object) (like `HS`) **plus** add zero‑point energy.                                                                                                            |
| `VapourLiquid` | For liquids: first compute the free energy of the gas with the same name, then add the vaporisation free energy. The species must define `vapor_pressure` (saturated vapour pressure) in `SpeciesAttributes`.            |

### `default_site` (string, default = `"s"`)
The default site name. In species names and reaction expressions, you can use the `*` wildcard to stand for this site.

### `reactions` (JSON object)
Elementary reactions.  
Keys are reaction names, values are components of type [`Reaction`](#Reaction).

### `species` (JSON object)
Species attributes.  
Keys are species names, values are components of type [`SpeciesAttribute`](#SpeciesAttribute).

### `custom_plot` (JSON object)
Custom function plots.  
Keys are function names, values are expressions (strings or formula objects).

## `KineticModel`

`KineticModel` is a `ReactionModel` that handles kinetic steady‑state models. On top of the fields inherited from
`ReactionModel`, it adds the following fields:

### `mapper` (component of type [`Mapper`](#Mapper))
Handles descriptors and grid points.

### `reader` (JSON array)
Elements are components of type [`Reader`](#Reader), which read data from external files.

### `solver` (component of type [`Solver`](#Solver))
Solves the steady state of the reaction model.

### `guesser` (JSON array)
Elements are components of type [`Guesser`](#Guesser), which provide initial guesses for the solver.

### `scaler` (component of type [`Scaler`](#Scaler))
Scales species formation energies and free energies.

### `modifier` (JSON array)
Elements are components of type [`Modifier`](#Modifier), which can modify calculation methods or add extra functionality.

### `writer` (JSON array)
Elements are components of type [`Writer`](#Writer), which write data to output files.

# Reaction

`Reaction` is a component that represents an elementary reaction. It forms the building block of the reaction network and is responsible for generating its own rate expression. The component itself is the only implementation and also the default one.

It contains the following fields:

### `equation` (string)

The reaction expression. Format: `xA + yB + ... -> zC + ...`  
If a transition state is involved: `xA + yB + ... <-> TS -> zC + ...`

Here `x`, `y`, `z` are stoichiometric coefficients; they can be omitted if equal to `1`.  
`A`, `B`, `C` are species names and must follow the [species naming rules](SpeciesNaming.md).

When the `Reaction` is initialized, it checks that the total numbers of atoms, sites, and charges in the initial state, final state, and transition state (if any) are consistent. An error is reported if they do not match.

Any species appearing in the reaction expression will be registered.

### `disabled` (boolean, default = `false`)

If set to `true`, this reaction is ignored.

### `prefactor` (algebraic expression, optional)

The pre‑exponential factor (Arrhenius prefactor). If omitted, the transition state theory prefactor `kBT/h` is used.

### `hertz_knudsen` (boolean, default = `false`)

Whether to use Hertz-Knudsen equation to replace the prefactor. `Acat` (the area of a site, in square meter) and `p0` (reference presser, 1e5 usually) must be set in parameters.

### `correction` (algebraic expression, default = `1`)

An extra multiplicative factor in the reaction rate expression.  
If the user provides `kf` or `kr`, this parameter has no effect.

### `dGr` (algebraic expression, optional)

The reaction free energy of the forward reaction, in eV.  
If both `dGr` and `kr` are omitted, then every species must have a known free energy. The rate constant is then calculated from these free energies.

### `dGa` (algebraic expression, optional)

The forward reaction barrier (activation free energy), in eV.  
If omitted and `dGr` is provided, the barrier is taken as the larger of `dGr` and `0`.

### `kf` (algebraic expression, optional)

The forward rate constant. If omitted, the rate constant is calculated using the energy barrier (from free energies of species), `prefactor`, and `correction`.

### `kr` (algebraic expression, optional)

The reverse rate constant. If omitted, it is calculated using the energy barrier (from free energies of species), `prefactor`, and `correction`.

### `energy_source` (string)

This option allows the reaction free energy of this reaction to be replaced by that of another reaction.  
With this option, this reaction no longer needs the free energies of its own species; instead, it needs the free energies of all species appearing in the replacement reaction.  
Furthermore, the replacement reaction is marked as `virtual`, meaning its species are only used for free energy calculation and do not participate in the kinetic simulation.

The format is the same as [`equation`](#equation-string).

### `is_virtual` (boolean, default = `false`)

Marks the reaction as `virtual`. In a virtual reaction, the species appear only for free energy calculation and do not participate in kinetic simulation. Usually this does not need to be set manually.

# SpeciesAttribute

`SpeciesAttribute` is a component used to supply additional properties for a species. It can also register new species, allowing species that do not appear in any elementary reaction to participate in the kinetic simulation. The component itself is the only implementation and also the default one.

It contains the following fields:

### `concentration` (algebraic expression, optional)

The concentration of the species. If omitted, it defaults to `0`.
- For `Aqua` species, the unit is **mol/L**.
- For `Gas` species, the unit is **bar**.

`SurfaceSpecies` do not need this field.

### `attributes` (JSON object)
Keys are attribute names, values are in form of float.
Some solvers or thermodynamic correction methods require additional parameters. These can be written here.  
In algebraic expressions, they become constants named `"attributeName[speciesName]"` (e.g., `"H[H_s]"`).

### `expressions` (JSON object)
Keys are attribute names, values are algebraic expressions.
Similar to `attributes`, but the values are algebraic expressions instead of fixed numbers.  
These can be used for derived or variable properties. In algebraic expressions, they become dependent variables or constants named `"expressionName[speciesName]"`.

### `not_virtual` (boolean, default = `false`)

Marks whether the species is **virtual**. If set to `true`, the species does **not** participate in the kinetic simulation.  
This is useful for species that appear only in descriptors or in replacement reactions (`energy_source`).

### `thermo` (thermodynamic correction method name)

Specifies the thermodynamic correction method for this species.  
If provided, it overrides the method set in [`default_thermo`](#default_thermo-json-object) for this species.

# Mapper

`Mapper` is a component that handles descriptors and manages map functions.

## StandardMapper (abstract)

A general‑purpose `Mapper` that lets you define a specified number of descriptors and their values.  
This component combines all descriptor values to generate grid points, and manages the solving logic over the
descriptor space. Four solving methods are available:

- `"map_in_turn"`: conventional sequential solution approach (CSSA) – solves the specified grid points one after
  another, allowing parallel solving.
- `"map_sample"`: Sampling‑Expansion Method (SEM) – first solves sample points, then expands using results from
  neighbouring points. Compared to CSSA, it greatly improves both speed and success rate.
- `"map_expand"`: when some grid points already have results, solves the remaining points using only the
  expansion method.
- `"map_check"`: checks whether the data at specified points satisfy the steady‑state condition. It first tries to solve
  using the existing data as initial guesses; if solving fails, the original data are removed, ensuring that only correct results remain.

It contains the following fields:

### `descriptors` (JSON object, keys are descriptor names, values are descriptor value sets)

At each grid point, the variable named after a descriptor takes a specific value – these behave like variable reaction parameters.  
A descriptor can be a simple expression, e.g. `T-298.15`, `log(p)`. The program automatically deduces the original physical value.

The value set for a descriptor is a JSON array. Each item can be either:

- a single real number – directly specifies one value, or
- an array of three numbers – defines a linear space: `[start, end, count]`

**Example:**  
`"pH": [[1, 13, 13], 2.5, 10.5]` means pH takes the values:  
1, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 10.5, 11, 12, 13.

The number of descriptors must match the specific `Mapper` type (1D, 2D, 3D, etc.).

### `allow_multiple` (boolean, default = `true`)

Determines whether the same grid point is allowed to be solved from multiple directions when using the SEM method.  
Turning this off (`false`) reduces redundant calculations, but may cause the solver to deadlock.

### `max_bisect` (integer, default = `10`)

Maximum number of bisection steps when solving with continuation (bisection).  
Increasing this value may improve the chance of convergence, but will also increase the solving time.

### `predictor_enabled` (boolean, default = `true`)

When using SEM with bisection continuation, whether to use quadratic regression on already solved data to predict the initial guess for the next target point.  
Prediction is only used when the R² value is sufficiently high. This usually reduces the number of bisection steps and speeds up the solving process.

### `predictor_size` (integer, default = `5`)

Number of previously solved results used for quadratic regression.

---

## Mapper1D

A `StandardMapper` that allows exactly **one** descriptor.

---

## Mapper2D

A `StandardMapper` that allows exactly **two** descriptors.

---

## Mapper3D

A `StandardMapper` that allows exactly **three** descriptors.

Higher‑dimensional mappers are not provided because the results become impossible to visualise directly.  
If you need more dimensions, you can write your own custom mapper.

# Reader

`Reader` is a component that reads data from external files. Currently, it only supports reading species formation energy data.

Common fields:

### `input_file` (string)

The name of the file to read. Can be a relative or absolute path.

## EnergyTableReader

Reads species formation energies and vibrational frequencies from a table‑formatted file.  
File format reference: see [documentation](EnergyInputFileFormat.md).

---

# Solver

`Solver` is a component that builds the system of equations from the reaction model and solves them. It also manages all physical quantities in the reaction model and the algebraic relationships among them.

The `Solver` constructs the full set of equations. During initialisation, modules such as `Reaction`, `Scaler`, and `Modifier` can add or modify algebraic relationships. When initialisation finishes, the solver analyses all algebraic relations and classifies variables into constants, independent variables, and dependent variables, which reduces the amount of computation.

## NewtonSolver (abstract)

`NewtonSolver` is a solver base that solves multivariate equation systems using Newton’s method. It does not include the equation‑building process, but provides the solving method.  
After initialisation, `NewtonSolver` differentiates all equations with respect to the independent variables, obtaining the algebraic form of the Jacobian matrix. During solving, it substitutes the values of the independent variables to evaluate the Jacobian matrix, solves for the step, and iterates until the residual falls below the convergence precision.

Common fields:

### `error_threshold` (float, default = `0.9`)

If the ratio between the residuals of two consecutive iterations is greater than this value, the solver considers it as non‑convergent.  
This value can be adjusted between 0 and 1. The closer to 1, the less likely it is to falsely declare non‑convergence – but the solver may waste more time on failed attempts.

### `expressions` (JSON object)

Custom expressions. Keys are variable names, values are expressions. These can override existing expressions.

### `use_double` (boolean, default = `false`)

If `true`, the solver first attempts to solve the Jacobian matrix using double‑precision numbers.  
For models with a convergence precision around 30 decimal places, this can significantly speed up calculations. For higher‑precision models, it may reduce efficiency.

### `mixed_lm` (boolean, default = `false`)

Whether to use the Levenberg‑Marquardt algorithm for solving.  
Enable this when numerical instability occurs and the SEM method also fails. It may improve the chance of convergence, but will consume more time.

## SteadyStateSolver

Inherits from `NewtonSolver`. This solver is designed for microkinetic simulations. It builds the steady‑state approximation equations from elementary reactions and computes the state where the coverages of all adsorbates no longer change.

It contains the following fields:

### `extra_variables` (JSON array)

User-defined additional variables. Array elements are variable names. Variable names must not duplicate any existing variable names. The length of the array must match that of `extra_equations`.

### `extra_equations` (JSON array)

User-defined additional equations. Array elements are algebraic expressions of the equations (no need to write the equals sign; the actual equation is the algebraic expression = 0). These equations will be combined with the steady-state approximation equations and solved. The length of the array must match that of `extra_variables`.

## GasPhaseEquilibriumSolver

Inherits from `NewtonSolver`. This solver calculates the composition of a gas‑phase reaction after it reaches thermal equilibrium.

# Guesser

`Guesser` is a component that provides initial guesses for the `Solver`. It includes both simple and advanced guessers.

Simple guessers include `ZeroGuess`, `RandomGuess`, and `AverageGuess`, which generate initial guess values based on the number of independent variables. There is also `OriginalDataGuess`, which uses the independent variable results at the current grid point as the initial guess (the results at that grid point may come from a previously solved model with modified parameters).

Advanced guessers compute more reasonable initial guesses from reaction parameters.

## BoltzmannGuesser

Renormalizes the free energy of gases to zero, obtains the relative energies of adsorbates, and then computes coverages via the Boltzmann distribution. These coverages are used as the initial guess.

## ODEGuesser

Treats the microkinetic process as a system of ordinary differential equations (ODEs). Starting from zero coverage, it repeatedly updates the coverage by taking the current rate of change multiplied by an appropriate step size. The iteration continues until the residual falls below a coarse tolerance, at which point the current coverage is passed to the `Solver` as the initial guess. If the `Solver` fails to converge, the iteration continues until the maximum number of iterations is exceeded.

It contains the following fields:

### `rough_tolerance` (float, default = `1e8`)

The coarse tolerance. When the residual falls below this value, the guesser becomes ready to provide an initial guess.

### `max_iterations` (integer, default = `1000`)

The maximum number of iterations allowed.

### `trial_interval` (integer, default = `100`)

The minimum number of iterations between successive attempts to provide an initial guess.

# Scaler

(This component is likely to be adjusted in the future.)

`Scaler` is a component that generates species free energies. It filters the formation energies and frequencies read by the `EnergyTableReader` according to the required criteria, applies thermodynamic correction methods to the species, and produces algebraic expressions for the free energies.

It contains the following fields:

### `item_filter` (JSON object)

Keys are attribute names to filter by, values are regular expressions. The filter logic is **AND** – all conditions must match when selecting energy data.

### `ele_energy_use_u` (boolean, default = `false`)

When enabled, the free energy of an electron becomes `-U`; otherwise it is `0`.

## LinearScaler

A component that relates the formation energies of surface species to descriptors using linear scaling relations and BEP (Bronsted‑Evans‑Polanyi) relations. It requires the formation energies of each surface species on a set of surfaces. In the [`EnergyTableReader`](#energytablereader) data, there should be a `surface` column, and the descriptors should include at least one formation energy (e.g., `"E[speciesName]"`). This component fits the formation energies of all surface species as linear functions of one or more descriptors, and uses these linear functions as the new formation energies at each grid point.

It includes the base fields of `Scaler` plus the following fields:

### `surfaces` (JSON array)

Defines the names of the surfaces used in the scaling.

### `scaling_formula` (JSON object)

Keys are species names, values are algebraic expressions. This allows custom fitting results (the expression can be arbitrary, not limited to linear functions of descriptors). Species defined here will **not** be fitted by the default linear scaling procedure.

---

# Modifier

`Modifier` is a component that can alter existing components, including adding functionality, inserting or modifying algebraic relations, or injecting actions during iteration. Currently only `SpeciesEnergyDRCModifier` is available.

## SpeciesEnergyDRCModifier

This modifier computes the influence of a species’ energy on the turnover frequency (TOF), i.e., the degree of rate control (DRC). It identifies which elementary reaction most strongly affects the TOF. When enabled, the `Mapper` gains a new operation `"map_drc"`, which runs after the main calculation. It shifts the free energy of selected species by a tiny amount, recomputes the TOF, obtains the partial derivative, and then computes the DRC as `∂(ln TOF) / ∂(-G/RT)`.

It contains the following fields:

### `species` (JSON array, default = `["all"]`)

Names of the species to include in the DRC calculation. Special values:
- `"all"`: all surface species
- `"ads"`: all adsorbates
- `"ts"`: all transition states

### `excepted_species` (JSON array, default = empty array)

Species names to exclude from the DRC calculation.

### `target_tof` (JSON array)

The TOF(s) to use for the DRC calculation. Must be fluid species. `A_g` here is equivalent to `"A_g": "ln(tof(A_g))"` in `target_expressions`.

### `target_expressions` (JSON object)

Customized items to use for the DRC calculation. Each item has a name (key) and an algebraic expression (value).

### `delta` (float, default = `1E-10`)

The amount by which the species’ free energy is changed when computing the DRC. Normally no need to modify this value.

# Writer

`Writer` is a component that writes data to output files. You need to choose a type that matches your `Mapper`. It contains the following common fields:

### `output_file` (string)

The path to the output file. Relative and absolute paths are both supported.

### `overwrite` (boolean, default = `true`)

If the output file already exists, whether to overwrite it (`true`) or skip writing (`false`).

## CSV1DWriter

A `Writer` suitable for `Mapper1D`. It outputs **all data** of the selected data type for each grid point into a CSV table.

### Additional field

#### `data_type` (string)

The Reaction Model provides multiple exportable data types. If an invalid type is provided, the error message will list all available data types.

## CSV2DWriter

A `Writer` suitable for `Mapper2D`. It outputs **selected data** of the selected data type for each grid point into a CSV table.

### Additional fields

#### `data_type` (string)

The Reaction Model provides multiple exportable data types. If an invalid type is provided, the error message will list all available data types.

#### `data_name` (string)

Each data type contains one or more data items. If an invalid name is provided, the error message will list all available data names for that type.

## CSV1DMultiWriter

A `Writer` suitable for `Mapper1D`. It evaluates multiple custom expressions at each grid point and writes the results into a CSV table.

Additional field:

### `expressions` (JSON array)

Custom expressions. Each item has a name (key) and an algebraic expression (value).

## CSV2DCustomWriter

A `Writer` suitable for `Mapper2D`. It evaluates a custom expression at each grid point and writes the results into a CSV table.

Additional field:

### `expression` (algebraic expression)

The expression to be evaluated.
