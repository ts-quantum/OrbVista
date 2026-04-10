import psi4
import os

psi4.set_memory('1000mb')
psi4.core.set_num_threads(8)

prefix = 'job'

with open('start.xyz', 'r') as f:
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
wfn.molecule().save_xyz_file(f'{prefix}_final.xyz', True)

#generation of output files
psi4.fchk(wfn, f'{prefix}.fchk')
psi4.molden(wfn, f'{prefix}.molden')

wfn.to_file('opt.npy')

#FREQ JOB
wfn_rel = psi4.core.Wavefunction.from_file(f'opt.npy')
wfn_rel.to_file('18.npy')
psi4.set_options({
    'normal_modes_write' : True,
    'guess':'read'
    })
energy, wfn = psi4.frequency('scf', molecule=mol, return_wfn=True)

psi4.fchk(wfn, f'{prefix}_freq.fchk')
psi4.molden(wfn, f'{prefix}_freq.molden')

#CUBE JOB
psi4.set_options({
     'g_convergence': 'gau_tight',
     'cubeprop_tasks': ['esp','density','orbitals'],
     'cubeprop_orbitals': [11, 12, 13],
     'cubic_grid_overage': [4.0, 4.0, 4.0 ], # buffer around molecule
     'cubic_grid_spacing': [0.2, 0.2, 0.2 ]
})

psi4.cubeprop(wfn)

if os.path.exists('Dt.cube'): os.rename('Dt.cube', f'{prefix}_dens.cube')
if os.path.exists('ESP.cube'): os.rename('ESP.cube', f'{prefix}_esp.cube')

if os.path.exists('Psi_a_11_1-1.cube'): os.rename('Psi_a_11_1-1.cube', f'{prefix}_alpha_HOMO_11.cube')
if os.path.exists('Psi_a_12_1-1.cube'): os.rename('Psi_a_12_1-1.cube', f'{prefix}_alpha_SOMO_12.cube')
if os.path.exists('Psi_a_13_1-1.cube'): os.rename('Psi_a_13_1-1.cube', f'{prefix}_alpha_LUMO_13.cube')

# Beta-Orbitals
if os.path.exists('Psi_b_11_1-1.cube'): os.rename('Psi_b_11_1-1.cube', f'{prefix}_beta_HOMO_11.cube')
if os.path.exists('Psi_b_12_1-1.cube'): os.rename('Psi_b_12_1-1.cube', f'{prefix}_beta_LUMO_12.cube') 
if os.path.exists('Psi_b_13_1-1.cube'): os.rename('Psi_b_13_1-1.cube', f'{prefix}_beta_LUMO_13.cube')
