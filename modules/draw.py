import pyvista as pv
pv.global_theme.allow_empty_mesh = True
import numpy as np
from pyscf import lib, dft, scf 
from PySide6.QtCore import QThread, Signal

# Molecule Structure Drawing
def get_radius_by_group(atomic_number):
    # Definition  (Start, End): Radius
    groups = {
        (1, 1): 0.2,    # Hydrogen
        (2, 2): 0.2,    # Helium
        (3, 10): 0.35,   # 2. Period (Li to Ne)
        (11, 18): 0.45,  # 3. Period (Na to Ar)
        (19, 36): 0.55,  # 4. Period (K to Kr)
        (37, 54): 0.65,  # 5. Period (Rb to Xe)
        (55, 86): 0.75, # 6. Period (Cs-Rn, incl. Pt, Au)
    }
    
    for (start, end), radius in groups.items():
        if start <= atomic_number <= end:
            return radius
    return 0.3  # Default-Wert

def draw_mol(atom_points, atom_types, cpk_colors, cov_radii, default_radius):
    visual_objects = [] # list for mesh and color
    # create PolyData-Object from all points
    atoms_poly = pv.PolyData(atom_points)
    # add atom-tpye as scalar for coloring
    atoms_poly.point_data["colors"] = atom_types
    #sphere as template
    #sphere_source = pv.Sphere(radius=0.3, theta_resolution=20, phi_resolution=20)
    # color mapping:
    # glyph object contains original atom IDs, Lookup Table (LUT) can be used
    # loop over type
    u_types = np.unique(atom_types)
    for atom_type in u_types:
        color = cpk_colors[atom_type]
        mask = atom_types == atom_type
        if np.any(mask):
            sub_atoms = atoms_poly.extract_points(mask)
            r=get_radius_by_group(atom_type)
            sphere_source = pv.Sphere(radius=r, theta_resolution=20, phi_resolution=20)
            glyphs = sub_atoms.glyph(geom=sphere_source, scale=False, orient=False)
            visual_objects.append((glyphs, {"color": color, "specular": 0.5}))
    # --- Bonds as single net
    lines = []
    for i in range(len(atom_points)):
        type_i = int(atom_types[i])
        rad_i = cov_radii.get(type_i, default_radius)
        for j in range(i + 1, len(atom_points)):
            type_j = int(atom_types[j])
            rad_j = cov_radii.get(type_j, default_radius) 
            dist = np.linalg.norm(atom_points[i] - atom_points[j])
            bd_threshold = rad_i + rad_j + 0.6
            if 0.6 < dist < bd_threshold:
                # only indices of linked points are saved
                lines.append([2, i, j]) # 2: line conects two points      
    tubes = None
    if lines:
        # Create PolyData-Object for lines
        bonds_poly = pv.PolyData(atom_points)
        bonds_poly.lines = np.hstack(lines)
        # convert lines into tubes
        tubes = bonds_poly.tube(radius=0.06)
        visual_objects.append((tubes, {"color": "lightgray", "specular": 0.3}))
    
    return visual_objects

# Orbital Plotting
def draw_orb(grid=None, iso=0.02):
    visual_objects = []
    if grid is None:
        return []

    # name
    name = grid.active_scalars_name 

    # 1. Generate Positive Lobe (directly from  Grid)
    pos_mesh = grid.contour([iso], scalars=name)
    if pos_mesh.n_points > 0:
        # smooting - only if mesh is not empty
        visual_objects.append(pos_mesh.smooth(n_iter=100))

    # 2. Generate Negative Lobe
    neg_mesh = grid.contour([-iso], scalars=name)
    if neg_mesh.n_points > 0:
        visual_objects.append(neg_mesh.smooth(n_iter=100))

    return visual_objects, grid
        
def draw_orb_molden(data_obj, orbital_index=0, spin_idx=0, iso_level=0.02,
                    nx=50, ny=50, nz=50, padding = 4):
    visual_objects = [] # list object for mesh and color
    # extract coordinates
    # PySCF uses Bohr, Angstrom is needed for plotting
    atom_coords_angstrom = data_obj.mol.atom_coords() * 0.529177 # conversion Bohr -> Angström

    # set Grid boundaries (in Angström)
    padding = padding
    xmin, ymin, zmin = np.min(atom_coords_angstrom, axis=0) - padding
    xmax, ymax, zmax = np.max(atom_coords_angstrom, axis=0) + padding

    # calculate Grid points (resolution nxxnyxnz)
    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)
    z = np.linspace(zmin, zmax, nz)

    # PySCF eval_gto uses coordinates in Bohr
    coords_angstrom = lib.cartesian_prod([x, y, z])
    coords_bohr = coords_angstrom / 0.529177

    # GTO-Werte at points (AO = Atomic Orbitals)
    # "GTOval" selects automatically "spherical" or "cartesian" depending on mol object
    ao_values = data_obj.mol.eval_gto("GTOval", coords_bohr)

     # Select the correct MO coefficients (handle RKS vs UKS/UHF)
    if isinstance(data_obj.mo_coeff, (list, tuple)):
        # UHF/UKS: Select coefficients for the specific spin channel
        target_coeffs = data_obj.mo_coeff[spin_idx][:, orbital_index]
    else:
        # RHF/RKS: Only one set of coefficients exists
        target_coeffs = data_obj.mo_coeff[:, orbital_index]

    # MO = Linear combination of AO (Dot product)
    mo_values = np.dot(ao_values, target_coeffs)

    # prepare data for PyVista
    grid_values = mo_values.reshape(nx, ny, nz)

    # create structured Grid
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij') ###
    grid = pv.StructuredGrid(X, Y, Z)

    # assign grid values
    grid_values = mo_values.reshape((nx, ny, nz), order='F')
    grid_values = np.transpose(grid_values, (0, 2, 1)) 
    #grid.point_data["values"] = grid_values.flatten()
    grid.point_data["values"]=mo_values.reshape((nx,ny,nz),order='F').ravel(order='C')

    # create two Mesh object and assign names
    iso_pos = grid.contour([iso_level], scalars="values")
    iso_neg = grid.contour([-iso_level], scalars="values")

    visual_objects.append((iso_pos))
    visual_objects.append((iso_neg)) 
       
    return visual_objects, grid

def get_validated_dm(mol, mo_coeff, mo_occ):
    """Generates the density matrix and corrects basis mismatch errors."""
    # 1. Case: UKS (Radical/Tupel) vs. RKS (Array)
    if isinstance(mo_occ, (list, tuple)):
        # mo_coeff[0] = Alpha Orbitals, mo_occ[0] = Alpha Occupation
        dm_a = scf.hf.make_rdm1(mo_coeff[0], mo_occ[0])
        dm_b = scf.hf.make_rdm1(mo_coeff[1], mo_occ[1])
        dm = dm_a + dm_b
        target_n = np.sum(mo_occ[0]) + np.sum(mo_occ[1])
    else:
        # RKS/RHF (Simple Array)
        dm = scf.hf.make_rdm1(mo_coeff, mo_occ)
        target_n = np.sum(mo_occ)
    
    # 2. Renormalization
    s = mol.intor('int1e_ovlp')
    current_n = np.trace(dm @ s)
    if not np.isclose(current_n, target_n, atol=1e-5):
        dm *= (target_n / current_n)
    return dm

def draw_dens(data_obj, iso_val=0.002, nx=50, ny=50, nz=50, padding = 4):
    mol = data_obj.mol
    to_ang = 0.529177249
    padding_ang = padding

    # 1. Alles in Bohr berechnen
    at_coords_bohr = mol.atom_coords()
    pad_bohr = padding_ang / to_ang # Padding einheitlich umrechnen!
    
    mins = np.min(at_coords_bohr, axis=0) - pad_bohr
    maxs = np.max(at_coords_bohr, axis=0) + pad_bohr
    
    # 2. Gitterachsen in Bohr
    x_b = np.linspace(mins[0], maxs[0], nx)
    y_b = np.linspace(mins[1], maxs[1], ny)
    z_b = np.linspace(mins[2], maxs[2], nz)
    
    # 3. Dichte berechnen (PySCF braucht Bohr)
    coords_bohr = lib.cartesian_prod([x_b, y_b, z_b])
    ao_values = mol.eval_gto("GTOval", coords_bohr)
    dm = get_validated_dm(mol, data_obj.mo_coeff, data_obj.mo_occ)
    rho = dft.numint.NumInt().eval_rho(mol, ao_values, dm)
    
    # 4. PyVista Grid in Ångström für die Darstellung
    X, Y, Z = np.meshgrid(x_b * to_ang, y_b * to_ang, z_b * to_ang, indexing='ij')
    grid = pv.StructuredGrid(X, Y, Z)
    grid.point_data["rho"] = rho.reshape((nx, ny, nz), order='F').ravel(order='C')
    surf = grid.contour([iso_val], scalars="rho")

    visual_objects = [] # list object for mesh and color
    visual_objects.append((surf))
    visual_objects.append(pv.PolyData())

    return visual_objects, grid

# ESP Plotting
def draw_esp(grid_dens=None, grid_esp=None, iso_val=0.002):
    #extract iso-density surface
    surface = grid_dens.contour([iso_val])
    #project ESP values on surface
    mapped_surface = surface.sample(grid_esp)
    # 
    active_scalar = mapped_surface.active_scalars_name

    v_min=np.min(mapped_surface.active_scalars)
    v_max=np.max(mapped_surface.active_scalars)

    smoothed_surface = mapped_surface.smooth(n_iter=100)
    return smoothed_surface, v_min, v_max, active_scalar

# sub procedures for ESP Mapping

def calculate_esp_on_surface(mol, dm, surf):   
    to_ang = 0.529177249
    points_bohr = surf.points / to_ang
    
    # --- 1. BLOCK: ELEKTRONs (multiprocessing) ---
    # int1e_grids automatically uses multiple Threads on C-Level
    v_mat = mol.intor('int1e_grids', grids=points_bohr) # Form: (n_pts, n_ao, n_ao)
    
    # extremely fast contraction via einsum 
    v_elec = -np.einsum('kij,ij->k', v_mat, dm)
    del v_mat # release RAM
    
    # --- 2. BLOCK: Nuclear Part (vectorized) ---
    at_coords = mol.atom_coords()
    at_charges = mol.atom_charges()
    # fast distance matrix without explicit loops
    diff = points_bohr[:, None, :] - at_coords[None, :, :]
    dists = np.sqrt(np.einsum('ijk,ijk->ij', diff, diff))
    v_nuc = np.sum(at_charges / dists, axis=1)
    
    return v_elec + v_nuc

class ESPWorkerThread(QThread):
    # Signal returns the result array and the original surface object.
    finished = Signal(object) 

    def __init__(self, dm, mol, surf):
        super().__init__()
        self.dm = dm 
        self.mol = mol
        self.surf = surf
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        # Uses fast matrix logic (vectorized).
        # No basis errors occur as operations remain within the same memory space (thread).
        total_esp = calculate_esp_on_surface(self.mol, self.dm, self.surf)
        if not self._abort:
            self.finished.emit((total_esp, self.surf))

def prep_esp_molden(data_obj, iso_val=0.002, nx=50, ny=50, nz=50, padding=4):
    mol = data_obj.mol
    to_ang = 0.529177249
    padding_ang = padding

    # 1. Calculation in Bohr
    at_coords_bohr = mol.atom_coords()
    pad_bohr = padding_ang / to_ang # Padding also in Bohr
    
    mins = np.min(at_coords_bohr, axis=0) - pad_bohr
    maxs = np.max(at_coords_bohr, axis=0) + pad_bohr
    
    # 2. Grid Axes in Bohr
    x_b = np.linspace(mins[0], maxs[0], nx)
    y_b = np.linspace(mins[1], maxs[1], ny)
    z_b = np.linspace(mins[2], maxs[2], nz)
    
    # 3. Calculate Density (PySCF uses Bohr)
    coords_bohr = lib.cartesian_prod([x_b, y_b, z_b])
    ao_values = mol.eval_gto("GTOval", coords_bohr)
    dm = get_validated_dm(mol, data_obj.mo_coeff, data_obj.mo_occ)
    rho = dft.numint.NumInt().eval_rho(mol, ao_values, dm)
    
    # 4. PyVista Grid in Ångström for visualization
    X, Y, Z = np.meshgrid(x_b * to_ang, y_b * to_ang, z_b * to_ang, indexing='ij')
    grid = pv.StructuredGrid(X, Y, Z)
    grid.point_data["rho"] = rho.reshape((nx, ny, nz), order='F').ravel(order='C')
    surf = grid.contour([iso_val], scalars="rho")
    surf = surf.decimate(0.5) 

    return mol, dm, surf, grid

def draw_spin(data_obj, iso_val=0.02, nx=50, ny=50, nz=50, padding=4):
    mol, mo_coeff, mo_occ = data_obj.mol, data_obj.mo_coeff, data_obj.mo_occ
    
    # Check if we have an unrestricted system (tuple/list for alpha and beta)
    if isinstance(mo_coeff, (list, tuple)):
        # UHF/UKS: Generate two density matrices and sum them up
        dm_alpha = scf.hf.make_rdm1(mo_coeff[0], mo_occ[0])
        dm_beta = scf.hf.make_rdm1(mo_coeff[1], mo_occ[1])
         # 2. Renormalization 
        s = mol.intor('int1e_ovlp')
        target_a = np.sum(mo_occ[0])
        target_b = np.sum(mo_occ[1])
        
        # correction factor for each channel
        dm_alpha *= (target_a / np.trace(dm_alpha @ s))
        dm_beta *= (target_b / np.trace(dm_beta @ s))
    else:
        # RHF/RKS: Generate standard density matrix
        dm_alpha=scf.hf.make_rdm1(mo_coeff, mo_occ)
        dm_beta=dm_alpha

    to_ang = 0.529177249
    padding_ang = padding

    # 1. Calculation in Bohr 
    at_coords_bohr = mol.atom_coords()
    pad_bohr = padding_ang / to_ang # Padding also in Bohr
    
    mins = np.min(at_coords_bohr, axis=0) - pad_bohr
    maxs = np.max(at_coords_bohr, axis=0) + pad_bohr
    
    # 2. Grid Axes in Bohr
    x_b = np.linspace(mins[0], maxs[0], nx)
    y_b = np.linspace(mins[1], maxs[1], ny)
    z_b = np.linspace(mins[2], maxs[2], nz)
    
    # 3. Calculate (PySCF uses Bohr)
    coords_bohr = lib.cartesian_prod([x_b, y_b, z_b])
    ao_values = mol.eval_gto("GTOval", coords_bohr)
    # --- Density ---
    rho_alpha = dft.numint.NumInt().eval_rho(mol, ao_values, dm_alpha)
    rho_beta = dft.numint.NumInt().eval_rho(mol, ao_values, dm_beta)
    rho_spin = rho_alpha -  rho_beta

    # 4. PyVista Grid in Ångström (Visualization)
    X, Y, Z = np.meshgrid(x_b * to_ang, y_b * to_ang, z_b * to_ang, indexing='ij')
    grid = pv.StructuredGrid(X, Y, Z)
    grid.point_data["spin"] = rho_spin.reshape((nx, ny, nz), order='F').ravel(order='C')

    # create two Mesh object and assign names
    iso_pos = grid.contour([iso_val], scalars="spin")
    iso_neg = grid.contour([-iso_val], scalars="spin")

    visual_objects = [] # list object for mesh and color
    visual_objects.append((iso_pos))
    visual_objects.append((iso_neg)) 
       
    return visual_objects, grid
    
def draw_spin_mapped(data_obj, iso_val=0.002, nx=50, ny=50, nz=50, padding=4):
    mol, mo_coeff, mo_occ = data_obj.mol, data_obj.mo_coeff, data_obj.mo_occ
    
    # Check if we have an unrestricted system (tuple/list for alpha and beta)
    if isinstance(mo_coeff, (list, tuple)):
        # UHF/UKS: Generate two density matrices and sum them up
        dm_alpha = scf.hf.make_rdm1(mo_coeff[0], mo_occ[0])
        dm_beta = scf.hf.make_rdm1(mo_coeff[1], mo_occ[1])
         # 2. Renormalization
        s = mol.intor('int1e_ovlp')
        target_a = np.sum(mo_occ[0])
        target_b = np.sum(mo_occ[1])
        
        # correction factor
        dm_alpha *= (target_a / np.trace(dm_alpha @ s))
        dm_beta *= (target_b / np.trace(dm_beta @ s))
    else:
        # RHF/RKS: Generate standard density matrix
        dm_alpha=scf.hf.make_rdm1(mo_coeff, mo_occ)
        dm_beta=dm_alpha

    to_ang = 0.529177249
    padding_ang = padding

    # 1. Calculation in Bohr 
    at_coords_bohr = mol.atom_coords()
    pad_bohr = padding_ang / to_ang # Padding also in Bohr
    
    mins = np.min(at_coords_bohr, axis=0) - pad_bohr
    maxs = np.max(at_coords_bohr, axis=0) + pad_bohr
    
    # 2. Grid Axes in Bohr
    x_b = np.linspace(mins[0], maxs[0], nx)
    y_b = np.linspace(mins[1], maxs[1], ny)
    z_b = np.linspace(mins[2], maxs[2], nz)
    
    # 3. Calculate Density (PySCF uses Bohr)
    coords_bohr = lib.cartesian_prod([x_b, y_b, z_b])
    ao_values = mol.eval_gto("GTOval", coords_bohr)
    # --- Density ---
    rho_alpha = dft.numint.NumInt().eval_rho(mol, ao_values, dm_alpha)
    rho_beta = dft.numint.NumInt().eval_rho(mol, ao_values, dm_beta)

    rho_spin = rho_alpha - rho_beta
    rho_total = rho_alpha + rho_beta # physical unit: e/Bohr^3

    # 4. PyVista Grid in Ångström (Visualization)
    X, Y, Z = np.meshgrid(x_b * to_ang, y_b * to_ang, z_b * to_ang, indexing='ij')
    grid = pv.StructuredGrid(X, Y, Z)
    grid.point_data["spin_abs"] = rho_spin.reshape((nx, ny, nz), order='F').ravel(order='C')
    grid.point_data["total_rho"] = rho_total.reshape((nx, ny, nz), order='F').ravel(order='C')

    # create geometry based on physical density
    surf = grid.contour([iso_val], scalars="total_rho")
    surf = surf.interpolate(grid)

    # Polarization: in percentage of alpha-spin
    surf.point_data["mapped_data"] = surf.point_data["spin_abs"] / iso_val
    v_min, v_max = -1.0, 1.0 # normalized scale

    return surf, v_min, v_max, "mapped_data"

    """
    Second Option: normalized relative to total spin 

        # 1. absolute number of unpaired electrons (S = n_a - n_b)
        n_unpaired = abs(n_a - n_b)
        
        # 2. avoid division by zero  (Singletts)
        if n_unpaired < 1e-6:
            n_unpaired = 1.0 

        # 3. Calculate densities (WITHOUT the previous n_a / n_b division)
        rho_alpha = dft.numint.NumInt().eval_rho(mol, ao_values, dm_alpha)
        rho_beta = dft.numint.NumInt().eval_rho(mol, ao_values, dm_beta)
        
        rho_total = rho_alpha + rho_beta
        # Normiere die Spindichte auf die Anzahl der ungepaarten Elektronen
        rho_spin_norm = (rho_alpha - rho_beta) / n_unpaired

        # 4. Mapping onto the Grid
        X, Y, Z = np.meshgrid(x_b * to_ang, y_b * to_ang, z_b * to_ang, indexing='ij')
        grid = pv.StructuredGrid(X, Y, Z)
        grid.point_data["total_rho"] = rho_total.reshape((nx, ny, nz), order='F').ravel(order='C')
        grid.point_data["spin_norm"] = rho_spin_norm.reshape((nx, ny, nz), order='F').ravel(order='C')

        # 5. Generate isosurface based on the true total density
        surf = grid.contour([iso_val], scalars="total_rho")
        surf = surf.interpolate(grid)

        # 6. Symmetric scaling for the visualization
        v_max = np.max(np.abs(surf.point_data["spin_norm"]))
        v_min = -v_max

        return surf, v_min, v_max, "spin_norm"
    """

