import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
from pathlib import Path
from collections import defaultdict
from pyscf import lib, dft, scf, df, gto
import pyscf
from qtpy.QtCore import QThread, Signal
from draw import get_validated_dm

def export_pov_header_mo(filename="test.inc", object_name="name", 
                       trans=0.66, color_pos="#F60505F3", 
                       color_neg="#1D09F0EF"):
    rgb_pos = pv.Color(color_pos).float_rgb
    rgb_neg = pv.Color(color_neg).float_rgb

    with open(filename, 'w') as f:
        f.write(f"""\
// created with OrbVista by Dr. Tobias Schulz
// MO Cube Object Object: #include "{object_name}.inc" into povray
//use "object{{{object_name}}}" in code
//declare Variables
#declare trans = {trans}; //Mesh Transparency
#declare color_pos = rgb <{rgb_pos[0]:.3f}, {rgb_pos[1]:.3f}, {rgb_pos[2]:.3f}>;
#declare color_neg = rgb <{rgb_neg[0]:.3f}, {rgb_neg[1]:.3f}, {rgb_neg[2]:.3f}>;
// Pre-defined Finishes
// 1. Die Presets definieren (mit umschließenden finish-Klammern)
#declare Fin_Std      = finish {{ phong 0.3 ambient 0.2 diffuse 0.6 }}
#declare Fin_Glassy   = finish {{ phong 0.9 specular 0.8 reflection 0.1 roughness 0.001 }}
#declare Fin_Metallic = finish {{ phong 0.5 metallic 0.7 brilliance 2.0 diffuse 0.3 }}
#declare Fin_Matte    = finish {{ phong 0.0 ambient 0.1 diffuse 0.8 }}
// 2. Die Auswahl treffen (das macht dein Python-Export)
#declare OrbFinish = Fin_Glassy; 
//
        """) 

def export_pov_header_esp(filename="test.inc", object_name="name", trans=0.66):
    with open(filename, 'w') as f:
        f.write(f"""\
// created with OrbVista by Dr. Tobias Schulz
// ESP Surface Object: #include "{object_name}.inc" into povray
// use "object{{{object_name}}}" in code
// Scalar_Bar is also available as "Colorbar"
//declare Variables
#declare trans = {trans}; //Mesh Transparency
//
        """)

def export_pov_header_spin(filename="test.inc", object_name="name", 
                       trans=0.66, color_pos="#F60505F3", 
                       color_neg="#1D09F0EF"):
    rgb_pos = pv.Color(color_pos).float_rgb
    rgb_neg = pv.Color(color_neg).float_rgb

    with open(filename, 'w') as f:
        f.write(f"""\
// created with OrbVista by Dr. Tobias Schulz
// Spin Density Object Object: #include "{object_name}.inc" into povray
//use "object{{{object_name}}}" in code
//declare Variables
#declare trans = {trans}; //Mesh Transparency
#declare color_pos = rgb <{rgb_pos[0]:.3f}, {rgb_pos[1]:.3f}, {rgb_pos[2]:.3f}>;
#declare color_neg = rgb <{rgb_neg[0]:.3f}, {rgb_neg[1]:.3f}, {rgb_neg[2]:.3f}>;
// Pre-defined Finishes
// 1. Die Presets definieren (mit umschließenden finish-Klammern)
#declare Fin_Std      = finish {{ phong 0.3 ambient 0.2 diffuse 0.6 }}
#declare Fin_Glassy   = finish {{ phong 0.9 specular 0.8 reflection 0.1 roughness 0.001 }}
#declare Fin_Metallic = finish {{ phong 0.5 metallic 0.7 brilliance 2.0 diffuse 0.3 }}
#declare Fin_Matte    = finish {{ phong 0.0 ambient 0.1 diffuse 0.8 }}
// 2. Die Auswahl treffen (das macht dein Python-Export)
#declare OrbFinish = Fin_Glassy; 
//
        """) 

def export_pov_header_spin_mapped(filename="test.inc", object_name="name", trans=0.66):
    with open(filename, 'w') as f:
        f.write(f"""\
// created with OrbVista by Dr. Tobias Schulz
// Mapped Spin Density Object: #include "{object_name}.inc" into povray
// use "object{{{object_name}}}" in code
// Scalar_Bar is also available as "Colorbar"
//declare Variables
#declare trans = {trans}; //Mesh Transparency
//
        """)

def export_pov_header_mol(filename="test.inc"):
    with open(filename, 'a') as f:
        f.write(f"""\
//
// ---- Atom and Bond Section
//transparency
#declare trans_bd = 0;
#declare trans_atom = 0;
//atom radius
#declare atom_rad_h = 0.24;
#declare atom_rad_2 = 0.35;
#declare atom_rad_3 = 0.42;
#declare atom_rad_def = 0.5;
#declare bond_rad = 0.08;
// predefined finishes:
#declare Fin_Glassy   = finish {{ phong 0.9 specular 0.8 reflection 0.1 roughness 0.001 }}
#declare Fin_Metallic = finish {{ phong 0.5 metallic 0.7 brilliance 2.0 diffuse 0.3 }}
#declare Fin_Matte    = finish {{ phong 0.0 ambient 0.1 diffuse 0.8 }}
// Define Bond Finishes
#declare Fin_Bd_Std = finish {{ phong 0.2 ambient 0.2 }}
// Select bond Finish
#declare BdFinish = Fin_Bd_Std;
// Definde Atom finishes
#declare Fin_Atom_Std = finish {{ phong 0.6 specular 0.4 ambient 0.2 }}
// select Atom Finish
#declare AtomFinish = Fin_Atom_Std;
        """)

def export_pov_colorbar(filename="test.inc", cmap_name="bwr", clim=[-0.02,0.02],
                        height=2.0, radius=0.08 ):
    v_min, v_max = clim
    cmap = plt.get_cmap(cmap_name)
    num_samples = 10 
    
    # positional argument for text label
    text_offset_x = radius + 0.2
    font_name = "arial.ttf" # font must exist in POV-Ray path

    with open(filename, 'a') as f:
        f.write("\n// --- Colorbar with Labels ---\n")
        # 1. Cylinder
        f.write(f"#declare Bar = cylinder {{ <0, 0, 0>, <0, {height}, 0>, {radius}\n")
        f.write("  pigment { gradient y color_map {\n")
        for i in range(num_samples):
            frac = i / (num_samples - 1)
            rgba = cmap(frac)
            f.write(f"    [{frac:.3f} color rgb <{rgba[0]:.4f}, {rgba[1]:.4f}, {rgba[2]:.4f}>]\n")
        f.write(f"  }} scale <1, {height}, 1> }}\n")
        f.write("  finish { ambient 0.7 diffuse 0.3 }\n}\n")

        # 2. Text Label
        # text { ttf "font.ttf" "string" thickness, offset }
        label_min = f'text {{ ttf "{font_name}" "{v_min:.2f}" 0.05, 0 pigment {{ rgb 1 }} finish {{ ambient 1 diffuse 0 }} scale 0.35 }}'
        label_max = f'text {{ ttf "{font_name}" "{v_max:.2f}" 0.05, 0 pigment {{ rgb 1 }} finish {{ ambient 1 diffuse 0 }} scale 0.35 }}'
        label_legend = f'text {{ ttf "{font_name}" "Legend" 0.05, 0 pigment {{ rgb 1 }} finish {{ ambient 1 diffuse 0 }} scale 0.35 }}'

        # 3. Combine Cylinder and Text Label
        f.write("#declare Colorbar = union {\n")
        f.write("  object { Bar }\n")
        f.write(f"  object {{ {label_min} translate <{text_offset_x}, 0, 0> }}\n")
        f.write(f"  object {{ {label_max} translate <{text_offset_x}, {height - 0.2}, 0> }}\n")
        f.write(f"  object {{ {label_legend} translate <0, {height + 0.4}, 0> }}\n")
        f.write("}\n")

##############################################################
def export_pov_mol(points, atom_types, cov_radii, default_radius, cpk_colors=None, 
                       filename="test.inc", ):
    #AtomsGroup
    with open(filename, 'a') as f:
        f.write(f"#declare AtomsGroup = union {{\n")
        for i, pos in enumerate(points):
            val = int(atom_types[i])
            # get colors from Color Dictionary
            color_name = cpk_colors.get(val, "magenta")
            # Conversion of Names to RGB for POV-Ray 
            rgb = {"white": "<1,1,1>", "gray": "<.3,.3,.3>", "blue": "<0,0,1>", 
                "red": "<1,0,0>", "orange": "<1, 0.55, 0>", "yellow": "<1,1,0>", 
                "brown": "<1,0.65,0>", "darkred": "<0.5,0,0>", "green": "<0, 0.82,0>"}.get(color_name, "<1,0,1>")

            atomic_num = int(atom_types[i])
            match atomic_num:
                case 1: # Hydrogen
                    rad_var = "atom_rad_h"
                case _ if 3 <= atomic_num <= 10: # 2nd period (He-Ne)
                    rad_var = "atom_rad_2"
                case _ if 11 <= atomic_num <= 18: # 3rd period (Na-Ar)
                    rad_var = "atom_rad_3"
                case _: # every other element
                    rad_var = "atom_rad_def"

            f.write(f"  sphere {{ <{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}>, {rad_var}\n")
            f.write(f"    pigment {{ color rgb {rgb} filter trans_atom }}\n")
            f.write("    finish { AtomFinish }\n")
            f.write("  }\n")
        f.write("}\n")
    #BondsGroup
    with open(filename, 'a') as f:
        f.write(f"#declare BondsGroup = union {{\n")
        for i in range(len(points)):
            type_i = int(atom_types[i])
            rad_i = cov_radii.get(type_i, default_radius)
            for j in range(i + 1, len(points)):
                type_j = int(atom_types[j])
                rad_j = cov_radii.get(type_j, default_radius) 
                bd_threshold = rad_i + rad_j + 0.6
                dist = np.linalg.norm(points[i] - points[j])
                # Threshold for Bonds in Angstrom
                if 0.6 < dist < bd_threshold:
                    p1 = points[i]
                    p2 = points[j]
                    f.write(f"  cylinder {{ <{p1[0]:.4f}, {p1[1]:.4f}, {p1[2]:.4f}>, "
                            f"<{p2[0]:.4f}, {p2[1]:.4f}, {p2[2]:.4f}>, bond_rad\n")
                    f.write("    pigment { color rgb <0.7, 0.7, 0.7> filter trans_bd }\n")
                    f.write("    finish { BdFinish }\n")
                    f.write("  }\n")
        f.write("}\n")
   
##############################################################
def export_pov_mo(mesh1, mesh2, filename="test.inc", object_name="name"):
    #MeshObject 
    # Prepare 1. Mesh
    if mesh1.n_points > 0 and mesh1.n_cells > 0:
        mesh1 = mesh1.extract_surface(algorithm='dataset_surface').triangulate().compute_normals(cell_normals=False, point_normals=True)
        normals = mesh1.point_data["Normals"]
        verts = mesh1.points
        faces = mesh1.faces.reshape(-1, 4)[:, 1:]

        with open(filename, 'a') as f:
            f.write(f"#declare MeshObject_1 = mesh2 {{\n")
        
            # --- A. Vertex Vectors (coordinates)
            f.write("  vertex_vectors {\n")
            f.write(f"    {len(verts)},\n")
            for v in verts:
                f.write(f"    <{v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}>,\n")
            f.write("  }\n")

            # --- B. Normal Vectors ---
            f.write("  normal_vectors {\n")
            f.write(f"    {len(normals)},\n")
            for n in normals:
                f.write(f"    <{n[0]:.6f}, {n[1]:.6f}, {n[2]:.6f}>,\n")
            f.write("  }\n")

            # --- C. Point Indices (Geometry) ---
            f.write("  face_indices {\n")
            f.write(f"    {len(faces)},\n")
            for face in faces:
                f.write(f"    <{face[0]}, {face[1]}, {face[2]}>,\n")
            f.write("  }\n")

            # --- D. Normal Indices (Smoothing) ---
            f.write("  normal_indices {\n")
            f.write(f"    {len(faces)},\n")
            for face in faces:
                f.write(f"    <{face[0]}, {face[1]}, {face[2]}>,\n")
            f.write("  }\n")
        
            f.write("}\n")
    else:
    # in case one mesh is empty
        with open(filename, 'a') as f:
            f.write(f"#declare MeshObject_1 = union {{ }}\n")

    # Prepare 2. Mesh
    if mesh2.n_points > 0 and mesh2.n_cells > 0:
        mesh2 = mesh2.extract_surface(algorithm='dataset_surface').triangulate().compute_normals(cell_normals=False, point_normals=True)
        normals = mesh2.point_data["Normals"]
        verts = mesh2.points
        faces = mesh2.faces.reshape(-1, 4)[:, 1:]

        with open(filename, 'a') as f:
            f.write(f"#declare MeshObject_2 = mesh2 {{\n")
            
            # --- A. Vertex Vectors (coordinates) 
            f.write("  vertex_vectors {\n")
            f.write(f"    {len(verts)},\n")
            for v in verts:
                f.write(f"    <{v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}>,\n")
            f.write("  }\n")

            # --- B. Normal Vectors ---
            f.write("  normal_vectors {\n")
            f.write(f"    {len(normals)},\n")
            for n in normals:
                f.write(f"    <{n[0]:.6f}, {n[1]:.6f}, {n[2]:.6f}>,\n")
            f.write("  }\n")

            # --- C. Point Indices (Geometry) ---
            f.write("  face_indices {\n")
            f.write(f"    {len(faces)},\n")
            for face in faces:
                f.write(f"    <{face[0]}, {face[1]}, {face[2]}>,\n")
            f.write("  }\n")

            # --- D. Normal Indices (Smooting) ---
            f.write("  normal_indices {\n")
            f.write(f"    {len(faces)},\n")
            for face in faces:
                f.write(f"    <{face[0]}, {face[1]}, {face[2]}>,\n")
            f.write("  }\n")
            
            f.write("}\n")
    else:
        # in case the mesh is empty
        with open(filename, 'a') as f:
            f.write(f"#declare MeshObject_2 = union {{ }}\n")
 
# combine all objects
    with open(filename, 'a') as f:
        f.write(f"""\
// Combine Atoms, Bonds and Mesh 
#declare {object_name} = union {{
    object {{AtomsGroup}}
    object {{BondsGroup}}
    object {{ MeshObject_1 texture {{ pigment {{ color color_pos filter trans }} finish {{OrbFinish}} }} }}
    object {{ MeshObject_2 texture {{ pigment {{ color color_neg filter trans }} finish {{OrbFinish}} }} }}
}}
        """)

##############################################################
def export_pov_esp(mesh, filename="test.inc", object_name="name", 
                   cmap_name="bwr", clim=[-0.02,0.02]):  
    #MeshObject
    # 1. Prepare Mesh Object
    mesh=mesh.mapper.dataset
    mesh = mesh.triangulate()
    verts = mesh.points
    faces = mesh.faces.reshape(-1, 4)[:, 1:]
    
    # 2. Calculate colors (mapping ESP values to RGB)
    # Assuming ESP values are stored in mesh.active_scalars.
    scalars = mesh.active_scalars
    norm = plt.Normalize(vmin=clim[0], vmax=clim[1])
    colormap = cm.get_cmap(cmap_name)
    
    # RGB Colors for each Vertex (0.0 bis 1.0 for POV-Ray)
    colors = colormap(norm(scalars))[:, :3] 

    # 1. Calculate normals in PyVista
    mesh = mesh.compute_normals(cell_normals=False, point_normals=True)
    normals = mesh.point_data["Normals"]

    with open(filename, 'a') as f:
        f.write(f"#declare MeshObject = mesh2 {{\n")
        
        # Vertices
        f.write("  vertex_vectors {\n")
        f.write(f"    {len(verts)},\n")
        for v in verts:
            f.write(f"    <{v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}>,\n")
        f.write("  }\n")

        # write Normal Vectors
        f.write("  normal_vectors {\n")
        f.write(f"    {len(normals)},\n")
        for n in normals:
            f.write(f"    <{n[0]:.6f}, {n[1]:.6f}, {n[2]:.6f}>,\n")
        f.write("  }\n")
        
        # 2. Textures (Colors per Vertex)
        f.write("  texture_list {\n")
        f.write(f"    {len(verts)},\n")
        for c in colors:
            # texture for each point
            f.write(f"    texture {{ pigment {{ color rgb <{c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f}> filter trans }}  }}\n")
        f.write("  }\n")
        
        # 3. Faces with texture interpolation
        f.write("  face_indices {\n")
        f.write(f"    {len(faces)},\n")
        for face in faces:
            # The three values following the mesh index <v1, v2, v3>:
            # Represent the texture indices for EACH vertex.
            # POV-Ray automatically interpolates colors between them.
            f.write(f"    <{face[0]}, {face[1]}, {face[2]}>, {face[0]}, {face[1]}, {face[2]},\n")
        f.write("  }\n")
        
        f.write("}\n")

# combine all objects
    with open(filename, 'a') as f:
        f.write(f"""\
// Combine Atoms, Bonds and Mesh 
#declare {object_name} = union {{
    object {{AtomsGroup}}
    object {{BondsGroup}}
    object {{MeshObject}}
}}
        """)

##### CUBE EXPORT ##########

def save_cube(filename, mol, data_grid, nx=50, ny=50, nz=50, comment="Density"):
    # Constant
    to_bohr = 1.889726125 
    
    # 1. Header Values from  Bounds
    b = data_grid.bounds
    origin_bohr = np.array([b[0], b[2], b[4]]) * to_bohr
    
    # Calculate Spacing (Bohr)
    spacing_bohr = [
        ((b[1] - b[0]) / (nx - 1)) * to_bohr,
        ((b[3] - b[2]) / (ny - 1)) * to_bohr,
        ((b[5] - b[4]) / (nz - 1)) * to_bohr
    ]

    # --- Write CUBE FILE ---
    with open(filename, 'w') as f:
        f.write(f"Generated with PySCF-GUI\n")
        f.write(f"{comment}\n")
        
        # Atoms & Origin (Number of Atoms, x, y, z)
        f.write("%5d%12.6f%12.6f%12.6f\n" % (mol.natm, *origin_bohr))
        
        # Grid Definition (nx, dx, 0, 0), (ny, 0, dy, 0), (nz, 0, 0, dz)
        f.write("%5d%12.6f%12.6f%12.6f\n" % (nx, spacing_bohr[0], 0.0, 0.0))
        f.write("%5d%12.6f%12.6f%12.6f\n" % (ny, 0.0, spacing_bohr[1], 0.0))
        f.write("%5d%12.6f%12.6f%12.6f\n" % (nz, 0.0, 0.0, spacing_bohr[2]))
        
        # Atoms (Atomic Number, Charge, x, y, z) - Koordinates in Bohr
        for i in range(mol.natm):
            z = int(mol.atom_charge(i))
            c = mol.atom_coord(i) # PySCF yields Bohr
            f.write("%5d%12.6f%12.6f%12.6f%12.6f\n" % (z, float(z), *c))

        # --- DATA-FIX ---
        # IMPORTANT: PyVista grids often use (X, Y, Z) with Fortran order.
        # Cube files require (X, Y, Z) with C-order (Z as the fastest-varying index).
        scalar_name = data_grid.array_names[0]
        data_flat = data_grid.point_data[scalar_name]
        
        # Convert in 3D (nx, ny, nz)
        # If the meshgrid was created with indexing='ij':
        data_3d = data_flat.reshape((nx, ny, nz), order='F')
        
        # In Case Transpose from (X, Y, Z) to (X, Z, Y) is needed
        # most stable way for VMD/Avogadro:
        flat_to_write = data_3d.flatten(order='C')

        # Formatted export (6 values per line).
        for i, val in enumerate(flat_to_write):
            f.write("%13.5E" % val)
            if (i + 1) % 6 == 0:
                f.write("\n")
        if len(flat_to_write) % 6 != 0: f.write("\n")

def save_xyz(filename, mol):
    # Constants
    to_bohr = 1.889726125 
    
    # ---- XYZ FILE ----
    new_fname = Path(filename).with_suffix(".xyz")

    element_dic = defaultdict(lambda: "X", {
        1: "H",   # Hydrogen
        5: "B",   # Boron
        6: "C",   # Carbon
        7: "N",   # Nitrogen
        8: "O",   # Oxygen
        9: "F",   # Fluorine
        14: "Si", # Silicon
        15: "P",  # Phosphorus
        16: "S",  # Sulfur
        17: "Cl", # Chlorine
        35: "Br", # Bromine
        53: "I",  # Iodine
        21: "Sc", # Scandium
        22: "Ti", # Titanium
        23: "V",  # Vanadium
        24: "Cr", # Chromium
        25: "Mn", # Manganese
        26: "Fe", # Iron
        27: "Co", # Cobalt
        28: "Ni", # Nickel
        29: "Cu", # Copper
        30: "Zn", # Zinc
        46: "Pd", # Palladium
        47: "Ag", # Silver
        74: "W",  # Tungsten
        78: "Pt", # Platinum
        79: "Au", # Gold
        80: "Hg"  # Mercury
    })

    #corresponding xyz file
    with open(new_fname, 'w') as f:      
        # Header (Strict column format)
        f.write(f"{mol.natm}\n\n")
        
        # Atoms (Directly from  PySCF - Bohr!)
        for i in range(mol.natm):
            z = int(mol.atom_charge(i)) # guarantee integer value
            e_symb=element_dic.get(z,"X")
            # 1. Column Identifier (Int), 2. Column Charge (Float)
            ca = mol.atom_coord(i) / to_bohr # Bohr Coordinates from PySCF
            
            # EXACT FORMAT: 5-digit integer followed by 4x 12-digit floats
            f.write("%-2s %12.6f %12.6f %12.6f\n" % (e_symb, ca[0], ca[1], ca[2]))

class CubeWorkerThread(QThread):
    finished = Signal(str)  # returns filename
    error = Signal(str)

    def __init__(self, data_obj, filename, nx=50, ny=50, nz=50, padding=4):
        super().__init__()
        self.data_obj = data_obj
        self.filename = filename
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.padding = padding

    def run(self):
        try:
            # Constant
            to_bohr = 1.889726125 

            # 1. Preparation (Multiprocessing via OpenMP)
            mol = self.data_obj.mol

            dm = get_validated_dm(mol, self.data_obj.mo_coeff, self.data_obj.mo_occ)
            
            # 2. Grid Definition directly in BOHR (Standard for Cube-Files)
            # large padding to prevent cut-off
            padding_bohr = self.padding * to_bohr 
            at_coords_bohr = mol.atom_coords() # PySCF yields Bohr
            
            mins = np.min(at_coords_bohr, axis=0) - padding_bohr
            maxs = np.max(at_coords_bohr, axis=0) + padding_bohr
            
            xs = np.linspace(mins[0], maxs[0], self.nx)
            ys = np.linspace(mins[1], maxs[1], self.ny)
            zs = np.linspace(mins[2], maxs[2], self.nz)
            
            # Calculate Spacing (Bohr)
            spacing_bohr = [
                ((maxs[0] - mins[0]) / (self.nx - 1)) ,
                ((maxs[1] - mins[1]) / (self.ny - 1)) ,
                ((maxs[2] - mins[2]) / (self.nz - 1)) 
                ]
            
            # Generate all Grid Points
            grid_points = lib.cartesian_prod([xs, ys, zs])
            
            # 3. ESP-Calculation
            v_mat = mol.intor('int1e_grids', grids=grid_points)
            v_elec = -np.einsum('kij,ij->k', v_mat, dm)
            
            at_charges = mol.atom_charges()
            diff = grid_points[:, None, :] - at_coords_bohr[None, :, :]
            dists = np.sqrt(np.einsum('ijk,ijk->ij', diff, diff))
            v_nuc = np.sum(at_charges / dists, axis=1)
            
            v_tot_flat = v_elec + v_nuc
            
            # --- Fix
            # PyVista/lib.cartesian_prod uses Fortran-style ordering (X-Y-Z)
            v_3d = v_tot_flat.reshape((self.nx, self.ny, self.nz), order='F')
            # Cube files require C-order (Z as the fastest-varying index).
            v_3d_final = v_3d.transpose(2, 1, 0) 
            final_data = v_3d_final.flatten(order='C')

            # 4. Write Cube File
            self._write_cube_file(mol, final_data, mins, spacing_bohr)
            
            self.finished.emit(self.filename)
            
        except Exception as e:
            self.error.emit(str(e))

    def _write_cube_file(self, mol, data, origin, spacing):
        with open(self.filename, 'w') as f:
            f.write("ESP Cube File - Generated by BatchMol (Parallel)\n")
            f.write("Electrostatic Potential in Hartree (Atomic Units)\n")
            
            # NAtoms, Origin (Bohr)
            f.write(f"{mol.natm:5d} {origin[0]:12.6f} {origin[1]:12.6f} {origin[2]:12.6f}\n")
            
            # Grid Vectors (Number, Stepsize)
            f.write(f"{self.nx:5d} {spacing[0]:12.6f} {0.0:12.6f} {0.0:12.6f}\n")
            f.write(f"{self.ny:5d} {0.0:12.6f} {spacing[1]:12.6f} {0.0:12.6f}\n")
            f.write(f"{self.nz:5d} {0.0:12.6f} {0.0:12.6f} {spacing[2]:12.6f}\n")
            
            # Atoms (Z, Charge, x, y, z in Bohr)
            for i in range(mol.natm):
                z_num = int(mol.atom_charge(i)) # Ordnungszahl
                c = mol.atom_coord(i)
                f.write(f"{z_num:5d} {float(z_num):12.6f} {c[0]:12.6f} {c[1]:12.6f} {c[2]:12.6f}\n")
            
            # Data Blocks (6 values per Line)
            for i in range(0, len(data), 6):
                line_vals = data[i:i+6]
                f.write(" ".join(f"{v:13.5E}" for v in line_vals) + "\n")
