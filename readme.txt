# OrbVista


**OrbVista** is an advanced graphical suite for the interactive visualization and 
volumetric analysis of Molecular Orbitals (MO), Electrostatic Potentials (ESP), 
and Spin Densities. It serves as the visual bridge between computational chemistry 
results and publication-quality rendering.

## Key Features
- **Wide Format Support**: Load and visualize data from `.cube`, `.molden`, 
  and `.fchk` files.
- **Dynamic Property Mapping**: Project ESP or Spin Density onto electron density 
  isosurfaces with customizable colormaps and scaling.
- **Interactive UI**: 
  - Manage multiple files in a synchronized session.
  - Customize lobe colors and background settings via intuitive context menus.
  - Dedicated **Grid Settings** for on-the-fly volumetric calculations.
- **High-End Export**: 
  - **POV-Ray**: Generates detailed `.inc` files for ray-traced imagery.
  - **Blender**: Exports `.glb` files with automated import scripts for cinematic 
    animations.
  - **Analysis**: Save calculated grids back to `.cube` format (including synchronized 
    `.xyz` for ChimeraX).

## Interface Overview
- **File List**: Manage your computational results. Double-click to remove, 
  single-click to focus.
- **Orbital Tabs**: Browse Alpha and Beta orbitals directly from Molden/FCHK outputs.
- **Property Controls**: Real-time adjustment of opacity, isolevels, and $v_{max}/v_{min}$ 
  scaling for mapping.
- **Grid Settings**: Fine-tune your calculation resolution ($n_x, n_y, n_z$) and 
  spatial padding.

## Workflow & Integration

### From QC to Visualization
1. **Load**: Import your `molden` or `fchk` file via `App -> Load`.
2. **Calculate**: Select the desired property (e.g., `Draw -> ESP molden`).
3. **Analyze**: Adjust the isosurface and colormap (e.g., `turbo`, `hsv`, `coolwarm`).
4. **Export**: Use `Export -> POV-Ray` for professional rendering or `Export -> MO Cube` 
for further analysis.

## Project Structure

```text
.
├── main.py               # Main application entry point
├── requirements.txt      # Project dependencies
├── README.md             # Documentation
├── /examples             # examples
    ├── ex1               # orca examples
    ├── ex2               # NWChem examples
    ├── ex3               # Psi-4 examples
├── /modules              # Core logic and UI components
│   ├── draw.py           # functions required for plotting
│   ├── export.py         # export routines
│   ├── gui_ui.py         # main GUI python file
│   ├── gui.ui            # main GUI raw ui file
│   ├── grid.ui           # grid settings window ui file
│   └── manual.html       # manual for help menu
├── /screenshots          # 
    ├── ...               # screenshots

## Examples & Tutorials
some molden and fchk input files can be found under examples as well as native cube
files for comparison

## Installation

1. Clone the repository
    git clone https://github.com
    cd MolVista

2. Install dependencies
    pip install -r requirements.txt

3. Requirements
    - Python 3.x
    - PySide6, or compatible Qt wrapper
    - Matplotlib, NumPy, SciPy
    - PySCF (for on-the-fly grid generation from Molden/FCHK)
    - Scikit-Image (Marching Cubes algorithm)
    - ...

## Usage

    python3 main.py

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file 
for details.

