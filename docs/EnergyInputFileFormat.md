# Energy Input File Format

The energy input file consists of two parts: a **unit declaration section** and a **table section**.

## Unit Declaration Section

- This section must **not contain any tab characters**.
- Format: `declared_object: unit`
- Declarable objects: `formation_energy`, `frequencies`
- Available units:  
  `eV`, `MeV`, `meV`, `cm-1` (or `cm^-1`), `kJ/mol` (or `kJ / mol` or `kJ mol^-1`)
- Meaning: all numerical values of the declared object in the table are expressed in the specified unit.
- **Default**: if an object is not declared, `eV` is used as the unit.

## Table Section

- Columns are separated by **tab characters** – the table can be copied directly to/from Excel.
- The **first row** is the header row, defining the content of each column.

### Required Columns

| Column             | Description                                                            |
|--------------------|------------------------------------------------------------------------|
| `species`          | Species name – must match the naming rules used in the setup file.     |
| `formation_energy` | Formation energy of the species (in the declared or default unit).     |
| `frequencies`      | Vibrational frequencies – written as an array, e.g., `[a, b, c, ...]`. |

### Optional Columns

| Column           | Description                                                                       |
|------------------|-----------------------------------------------------------------------------------|
| `reference`      | Currently has no functional role (reserved for future use).                       |
| Any other column | Treated as an **extra attribute** that can be used by the `Scaler` for filtering. |

### Important Notes

- **Empty sites**: Even if the formation energy is typically `0`, you must still define it for the site species.
- **One row per species (after filtering)**: Under normal circumstances, after applying any filters, each species should have exactly **one** row containing its formation energy.
- **For `LinearScaler`**: An additional column `surface` is required. Each species must have formation energy data for **every** surface used in the scaling.