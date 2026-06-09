# Species Naming Rules

Species are organised according to the following tree structure:
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

## Fixed Species

### Electron

The name of an electron is fixed as `ele`.

### Site

A site name must consist of one or more lowercase letters only.

## MoleculeSpecies

A `MoleculeSpecies` name is composed of **four parts** in sequence:

`[configuration~]formula[:charge]_state`

Only the `formula` and `state` are required.

### 1. Configuration (optional)

- Must be entirely lowercase letters.
- If present, it is connected to the chemical formula by a tilde `~`.
- Used to distinguish species that have the same chemical formula but different structures (e.g., isomers).

### 2. Chemical Formula

- Written in the usual chemical notation: element symbols followed by numbers.
- An element symbol starts with an uppercase letter, optionally followed by one or more lowercase letters.
- Parentheses `( )` are **not** supported.
- The following characters are allowed between atoms for better structural representation: `|` , `-` (hyphen), `-` (comma).
    - For `SurfaceSpecies`: if a hyphen `-` appears in the formula, the species is classified as **Transition**; otherwise, it is an **Adsorbate**.

### 3. Charge (optional)

- Usually only present for `Aqua` species.
- Format: a number (the digit `1` can be omitted) followed by `+` or `-`.
- Separated from the chemical formula by a colon `:`.

### 4. State (physical state / adsorption site)

- Determines the species category:
    - `_g` → **Gas**
    - `_l` → **Liquid**
    - `_aq` → **Aqua**
    - Any other suffix → **SurfaceSpecies**

- For `SurfaceSpecies`, the state suffix specifies the **adsorption site(s)**:
    - Single site: `_` + site name, e.g., `_s`, `_t`.  
      Use `*` to denote the default site.
    - Multiple sites:
        - Separate site names with `|`, e.g., `_a|b`.
        - Or prefix a number before a site name to indicate multiplicity, e.g., `_2a|b`.

## Examples
```
trans~CH2CHCHCH2_g # Gas, configuration "trans", formula "CH2CHCHCH2"
H2O_l # Liquid water
CO3:2-_aq # Aqua carbonate ion, charge 2-
H* # Adsorbed hydrogen on the default site
O|O_2s # Adsorbed O₂ on site "2s" (two oxygen atoms sharing the site)
O-O_s|t # Transition state with a bridging O-O bond, sites "s" and "t"
```

## Equality of Species Names

Two species names are considered **identical** if and only if:

1. **Species type** (Electron, Site, Fluid subtype, SurfaceSpecies subtype) matches exactly.
2. **Configuration** (if any) matches exactly.
3. **Chemical formula** matches exactly (character‑by‑character).
4. **Charge** (if any) matches exactly.
5. For **SurfaceSpecies** only: the sets of adsorption sites must be the same – order does **not** matter.
    - Example: `O|O_2s|t` and `O|O_s|t|s` represent the same species.