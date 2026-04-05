import psi4
import os

psi4.set_memory('1000mb')
psi4.core.set_num_threads(8)

prefix = 'uhf'

with open('geo.xyz', 'r') as f:
    xyz_content = f.read()

#skip line one and two
xyz_body = "\n".join(xyz_content.strip().split("\n")[2:])

mol= psi4.geometry(f"""
0 2 
{xyz_body}
units angstrom
no_reorient
no_com
""")

psi4.set_options({
     'basis': 'cc-pVDZ',
     'scf_type': 'df',
     'reference': 'uhf',  
     'g_convergence': 'gau_tight'
})

#opt calculation
energy, wfn = psi4.optimize('scf', molecule=mol, return_wfn=True)

psi4.set_options({
     'cubeprop_tasks': ['esp','density'],
     'cubic_grid_overage': [4.0, 4.0, 4.0 ], # buffer around molecule
     'cubic_grid_spacing': [0.2, 0.2, 0.2 ],
})

#generation of output files
psi4.cubeprop(wfn)
psi4.fchk(wfn, f'{prefix}.fchk')
psi4.molden(wfn, f'{prefix}.molden')

#rename files

default_cubes = ['Dt.cube', 'Da.cube', 'Db.cube', 'V.cube', 'ESP.cube', 'Ds.cube']

for cube in default_cubes:
    if os.path.exists(cube):
        os.replace(cube,f"{prefix}_{cube}")

psi4.core.clean()

if os.path.exists("geom.xyz"):
    os.replace("geom.xyz", f"{prefix}_geom.xyz")
