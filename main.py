import sys
import os

# 
os.environ["QT_API"] = "pyside6"
#only in python3.12 environment: pyscf_prara

from qtpy import QtWidgets, QtCore, uic, QtGui
from PySide6.QtWidgets import QApplication, QColorDialog, QFileDialog
from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout
from PySide6.QtGui import QColor
from PySide6.QtCore import QStringListModel, Qt
import pyvista as pv
from pyvistaqt import QtInteractor 
import matplotlib.pyplot as plt
from matplotlib import colormaps
import numpy as np
import pyscf.tools.molden as molden_tools
from pyscf import data
from cclib.io import ccread
from collections import defaultdict
import vtk
import time, platform, subprocess

sys.path.insert(1,'./modules')
from export import *
from draw import *
from draw import ESPWorkerThread
from export import CubeWorkerThread

class GridSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, nx, ny, nz, padding, iso, iso_m):
        super().__init__(parent)
        uic.loadUi("modules/grid.ui", self)
        
        # current values from main app are written to UI fields
        self.edit_nx.setText(str(nx))
        self.edit_ny.setText(str(ny))
        self.edit_nz.setText(str(nz))
        self.edit_padding.setText(str(padding))
        self.edit_iso.setText(str(iso))
        self.edit_iso_m.setText(str(iso_m))
        
        # connect events and define signals ("Accept" returns 'Accepted')
        self.apply.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)

    def get_values(self):
        # return values (from UI fields)
        try:
            return (
                int(self.edit_nx.text()),
                int(self.edit_ny.text()),
                int(self.edit_nz.text()),
                int(self.edit_padding.text()),
                int(self.edit_iso.text()),
                int(self.edit_iso_m.text())
            )
        except ValueError:
            return None

class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OrbVista Help & Manual")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        help_text_html = self.load_help_content()
        self.text_area.setHtml(help_text_html) 
        layout.addWidget(self.text_area)

    def load_help_content(self):
        file_path = os.path.join(os.path.dirname(__file__), "./modules/manual.html")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>Manual file not found.</h1>"

class ColormapDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Basic Options (Background, Focus)
        self.initStyleOption(option, index)
        painter.save()
        # 1. Background
        option.widget.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)
        # 2. retriece data
        cmap_name = index.data(QtCore.Qt.DisplayRole)
        #PyQt6:
        #cmap_name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        cmap = plt.get_cmap(cmap_name)
        # 3. draw colorbar
        rect = option.rect
        bar_width = 60
        margin = 5
        # Gradient (0.0 bis 1.0)
        gradient_rect = QtCore.QRect(rect.left() + margin, rect.top() + 2, bar_width, rect.height() - 4)
        grad = QtGui.QLinearGradient(gradient_rect.topLeft(), gradient_rect.topRight())
        # Generate support points for the gradient from Matplotlib.
        for x in np.linspace(0, 1, 10):
            rgba = cmap(x)
            color = QtGui.QColor.fromRgbF(rgba[0], rgba[1], rgba[2])
            grad.setColorAt(x, color)
        painter.fillRect(gradient_rect, grad)
        # 4. Text next to colorbar
        text_rect = QtCore.QRect(gradient_rect.right() + 10, rect.top(), rect.width() - bar_width - 20, rect.height())
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter, cmap_name)
        #PyQt6
        #painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignVCenter, cmap_name)
        painter.restore()

class MoleculeData: #always call arguments by name! 
                    #no special order "*"
                    #e.g. obj=MoleculeData(atoms=atoms, type="molden")
    def __init__(self, *, name=None, type=None,
                 atoms=None, grid=None, atom_points=None, atom_types=None,
                 mol=None, mo_energy=None, mo_coeff=None, mo_occ=None,
                 orb_labels=None, spin=None, grid_values=None, surf_mesh=None,
                 grid_indices=None
                 ):
        self.name=name
        self.atoms=atoms
        self.grid=grid
        self.atom_points=atom_points
        self.atom_types=atom_types
        self.type=type
        self.mol=mol
        self.mo_energy=mo_energy
        self.mo_coeff=mo_coeff
        self.mo_occ=mo_occ
        self.orb_labels=orb_labels
        self.spin=spin
        self.grid_values = grid_values
        self.surf_mesh = surf_mesh
        self.grid_indices = grid_indices
    
    @classmethod
    def from_cube(cls, filepath):
        bohr_to_angstrom = 0.529177
        fname = os.path.basename(filepath)
        reader=pv.get_reader(filepath)
        atoms = reader.read(grid=False)
        grid = reader.read(grid=True)

        p0 = atoms.points[0]
        p1 = atoms.points[1] 
        raw_dist = np.linalg.norm(p0 - p1)
        bohr_to_ang = 0.529177
        if 0.8 < raw_dist < 2.1:
            factor = 1.0
            print(f"Auto-Detect: Angström (Dist {raw_dist:.2f})")
        elif 2.2 < raw_dist < 4.0:
            factor = bohr_to_ang
            print(f"Auto-Detect: Bohr (Dist {raw_dist:.2f})")
        else:
            if raw_dist > 4.0:
                factor = (2.76 * bohr_to_ang) / raw_dist 
            else:
                factor = 1.0
        atoms.points = np.array(atoms.points) * factor
        if hasattr(grid, 'origin'):
            grid.origin = np.array(grid.origin) * factor
            grid.spacing = np.array(grid.spacing) * factor
        atom_points = atoms.points
        atom_types = atoms.point_data["atom_type"].astype(int) + 1
        return cls(
            name=fname,
            atoms=atoms,
            atom_points=atom_points,
            atom_types=atom_types,
            grid=grid) 

    @classmethod
    def from_molden(cls, filepath):
        short_name = os.path.basename(filepath)
        mol, mo_energy, mo_coeff, mo_occ, orb_labels, spin = molden_tools.load(filepath)
        mol.build()
        atom_points = mol.atom_coords() * 0.529177 
        atom_types = [data.elements.charge(mol.atom_symbol(i))
                        for i in range(mol.natm)]
        return cls(
            name=short_name, 
            atom_points=atom_points,
            atom_types=atom_types,
            type="molden",
            mol=mol,
            mo_energy=mo_energy,
            mo_coeff=mo_coeff,
            mo_occ=mo_occ,
            orb_labels=orb_labels,
            spin=spin
        )

    @classmethod
    def fix_fchk_format(cls,filepath):
        import re
        import io    
        with open(filepath, 'r') as f:
            lines = f.readlines()
        fixed_lines = []
        for line in lines:
            # check and repair all lines containing data (if necessary)
            if line.startswith(" "):
                # look for number followed by sign (no e/E)
                # e.g.: 0.123-4.567 -> 0.123 -4.567
                line = re.sub(r'(\d)([+-]\d\.)', r'\1 \2', line)
                # Special case for 'lost' spaces with extreme exponents.
                # e.g.: 5.78e-02-4.48e-149 -> 5.78e-02 -4.48e-149
                line = re.sub(r'(e[+-]\d{2,3})([+-]\d\.)', r'\1 \2', line)
                
            fixed_lines.append(line)
            
        return io.StringIO("".join(fixed_lines))

    @classmethod
    def from_fchk(cls, filepath):
        
        # Apply fix
        fixed_file_stream = MoleculeData.fix_fchk_format(filepath)
        # 1. load data with cclib 
        data = ccread(fixed_file_stream)
        
        # 2. manually build PySCF molecule
        mol = gto.Mole()
        # Atoms from cclib (atomnos = atomic number, atomcoords in Angström)
        mol.atom = [[data.atomnos[i], data.atomcoords[-1][i]] for i in range(data.natom)]
        
        mol.basis = data.metadata.get('basis_set')

        mol.charge = data.charge
        mol.spin = data.mult - 1
        
        mol.cart = True 
        mol.build()

        n_ao_fchk = data.mocoeffs[0].shape[1]
        
        if mol.nao != n_ao_fchk:
            mol.cart = False
            mol.build()
            if mol.nao != n_ao_fchk:
                print(f"KRITISCH: Basis-Mismatch! PySCF AOs: {mol.nao}, FCHK AOs: {n_ao_fchk}")

        # 4. Data Extraction (Alpha/Beta Handling)
        is_uhf = len(data.homos) == 2
        if is_uhf:
            mo_coeff = [m.T for m in data.mocoeffs] # Transpose for (AO, MO)
            mo_energy = data.moenergies
            # Generate Occupation
            mo_occ = [np.zeros(len(e)) for e in mo_energy]
            mo_occ[0][:data.homos[0]+1] = 1.0
            mo_occ[1][:data.homos[1]+1] = 1.0
            orb_labels = [[f"Alpha MO {i}" for i in range(len(mo_energy[0]))],
                        [f"Beta MO {i}" for i in range(len(mo_energy[1]))]]
        else:
            mo_coeff = data.mocoeffs[0].T
            mo_energy = data.moenergies[0]
            mo_occ = np.zeros(len(mo_energy))
            mo_occ[:data.homos[0]+1] = 2.0
            orb_labels = [f"MO {i}" for i in range(len(mo_energy))]

        return cls(
            name=os.path.basename(filepath),
            atom_points=data.atomcoords[-1],
            atom_types=data.atomnos.tolist(),
            type="molden",  #fchk
            mol=mol,
            mo_energy=mo_energy,
            mo_coeff=mo_coeff,
            mo_occ=mo_occ,
            orb_labels=orb_labels,
            spin=mol.spin
        )

from gui_ui import Ui_MainWindow # import gui_ui.py
class MoleculeApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        # pyside6-uic gui.ui -o gui_ui.py
        self.setupUi(self)
        self.menuBar().setNativeMenuBar(False)

        # 2. Create PyVista Plotter 
        self.plotter = QtInteractor(self.plot_widget) 
        self.plotter.set_background("#19135BED")
        self.plotter.add_axes()
        
        # 3. Embed the plotter into the container layout.
        # Missing layout for vtk_container in the Designer:
        if self.plot_widget.layout() is None:
            layout = QtWidgets.QVBoxLayout(self.plot_widget)
            layout.addWidget(self.plotter.interactor)
        else:
            self.plot_widget.layout().addWidget(self.plotter.interactor)
        self.plotter.enable_depth_peeling(number_of_peels=4, occlusion_ratio=0.0)
        # prepare for color picking (right-click) and initialize
        self.orb_mesh = []
        self.color_pos = "#E24040B1"
        self.color_neg = "#26BBD269"
        self.plotter.iren.add_observer("RightButtonPressEvent", self._on_right_click)
        self.plotter.picker = vtk.vtkPropPicker() 
        self.ESP_mesh = None
        #colorbox
        self.colorbox.setItemDelegate(ColormapDelegate(self.colorbox))
        # read all cmaps and hand over to list
        cmap_list = list(colormaps)
        #w/o reverse:
        cmap_list=[name for name in colormaps if not name.endswith('_r')]
        cmap_list.sort()
        #self.colorbox.addItems(["viridis", "plasma", "inferno", "magma", "cividis"])
        self.colorbox.addItems(cmap_list)
        self.colorbox.currentTextChanged.connect(self.color_changed)
        self.color = "rainbow"
        self.colorbox.setCurrentText(self.color)

        self.progressBar.setTextVisible(True)
        self.progressBar.setAlignment(Qt.AlignCenter)

        #Event connector
        self.actionQuit.triggered.connect(QApplication.instance().quit)
        
        self.actionLoad_MO_cube.triggered.connect(self.load_mo_cube)
        self.actionLoad_Dens_cube.triggered.connect(self.load_dens_cube)
        self.actionLoad_ESP_cube.triggered.connect(self.load_esp_cube)
        self.actionLoad_molden_file.triggered.connect(self.load_molden)
        self.actionLoad_fchk_file.triggered.connect(self.load_fchk)
        
        self.action_draw_mo_cube.triggered.connect(self.draw_mo_cube)
        self.action_draw_esp_cube.triggered.connect(self.draw_esp_cube)
        self.action_draw_mo_molden.triggered.connect(self.draw_mo_molden)
        self.action_draw_esp_molden.triggered.connect(self.draw_esp_molden)
        self.action_draw_dens_molden.triggered.connect(self.draw_dens_molden)
        self.action_draw_spin_dens.triggered.connect(self.draw_spin_dens)
        self.action_draw_spin_mapped.triggered.connect(self.draw_spin_mapped)

        self.actionSave_Image.triggered.connect(self.save_image)
        self.action_export_povray.triggered.connect(self.export_povray)
        self.action_export_blender.triggered.connect(self.export_blender)
        self.action_export_Cube.triggered.connect(self.export_cube)
        self.action_export_esp_cube.triggered.connect(self.export_esp_cube)

        self.actionHelp.triggered.connect(self.show_help)

        self.abort.clicked.connect(self.abort_esp)

        self.grid_settings.clicked.connect(self.show_grid_settings)

        #file_list
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_model = QStringListModel()
        self.file_list.setModel(self.list_model)
        self.file_list.clicked.connect(self.file_select)
        self.file_list.doubleClicked.connect(self.remove_item)
        #mo_list
        self.mo_list_model = QStringListModel()
        self.mo_list.setModel(self.mo_list_model)
        #mo_list_beta
        self.mo_list_beta_model = QStringListModel()
        self.mo_list_beta.setModel(self.mo_list_beta_model)
        #
        self.mo_views = [self.mo_list, self.mo_list_beta]
        self.mo_models = [self.mo_list_model,self.mo_list_beta_model]
        for view in self.mo_views:
            view.setFont(QtGui.QFont("Courier New", 9))

        self.dataset_dict = {} # initialize dictionary for molecule files

        self.sargs = dict(    #s scale_bar properties
            title="ESP (Hartree)",
            title_font_size=18,
            label_font_size=14,
            shadow=False,               # no shadwo with dark background
            n_labels=5,
            fmt="%.3f",
            font_family="arial",
            color="white",              # title and label 
            position_x=0.85,     # 85% to the right (near the right edge)
            position_y=0.25,     # starts at 25% Height
            vertical=True               # Optional: vertical orientation
        )
        
        self.cpk_colors = defaultdict(lambda: "magenta")
        self.cpk_colors.update({
            1: "white",  #H
            5: "pink",  #B
            6: "gray",   #C
            7: "blue",   #N
            8: "red",    #O
            9: "orange",  #F
            14: "darkgrey", #Si
            12: "darkgreen", #Mg
            15: "brown",  #P
            16: "yellow", #S
            17: "green",  #Cl
            26: "darkorange", #Fe
            24: "darkcyan",    # Cr (Chromium)
            27: "royalblue",   # Co (Cobalt)
            28: "silver",      # Ni (Nickel)
            29: "chocolate",   # Cu (Copper)
            40: "cadetblue",   # Zr (Zirconium)
            44: "teal",        # Ru (Ruthenium)
            45: "deeppink",    # Rh (Rhodium) 
            78: "lightgrey",    # Pt (Platinum)
            35: "darkred",   #Br
            53: "darkviolet" # I
        })
        # Bond Parameters
        self.cov_radii = {
        1: 0.31,   # H
        5: 0.82,   # B
        6: 0.76,   # C
        7: 0.71,   # N
        8: 0.66,   # O
        9: 0.57,   # F
        14: 1.11,  # Si
        15: 1.06,  # P
        16: 1.05,  # S
        17: 1.02,  # Cl
        35: 1.20,  # Br
        53: 1.39,  # I
        24: 1.39,  # Cr
        27: 1.26,  # Co
        28: 1.21,  # Ni
        29: 1.32,  # Cu
        40: 1.48,  # Zr
        44: 1.26,  # Ru
        45: 1.35,  # Rh
        78: 1.28   # Pt
        }
        # Standard Radius for unknown elements
        self.default_radius = 1.0

        #check scalar bar
        self.check_scalar_bar.stateChanged.connect(self.scalar_bar)

        #Grid Variables
        self.nx = self.ny = self.nz = 50
        self.padding = 4
        self.iso_value = 0.02
        self.iso_value_m = 0.002

#  ----  General Procedures  -------
    def prep_esp(self,v_min,v_max,esp_mesh,act_scalars, scalar_title="ESP (Hartree)"):
        self.input_v_min.setEnabled(True)
        self.input_v_max.setEnabled(True)
        raw_text = self.input_opacity.text()
        if raw_text: 
            try:
                opac = float(raw_text) / 100
            except ValueError:
                opac = 0.4
                self.input_opacity.setText("40")
        try:
            self.plotter.remove_scalar_bar()
        except:
            None
        if self.input_v_min.text() == "" or self.input_v_max.text() == "":
            self.v_min=v_min
            self.v_max=v_max
            self.input_v_min.setText(str(round(self.v_min, 4)))
            self.input_v_max.setText(str(round(self.v_max, 4)))
        else:
            try:
                self.v_min=float(self.input_v_min.text())
                self.v_max=float(self.input_v_max.text())
            except ValueError:
                self.v_min=v_min
                self.v_max=v_min
        mesh_args = {
            "mesh":esp_mesh,
            "scalars":act_scalars,
            "cmap":self.color, 
            "clim":[self.v_min, self.v_max], 
            "opacity":opac,
            "smooth_shading":True
            }
        dynamic_sargs = self.sargs.copy()
        dynamic_sargs["title"] = scalar_title

        if self.check_scalar_bar.isChecked():
            mesh_args["scalar_bar_args"] = dynamic_sargs
            mesh_args["show_scalar_bar"] = True
        else:
            mesh_args["show_scalar_bar"] = False
        return mesh_args

    def show_help(self):
        if not hasattr(self, 'help_win'):
            self.help_win = HelpWindow(self)
        self.help_win.show()
        self.help_win.raise_()

    def show_grid_settings(self):
        # current values in main app are handed over to grid_settings dialog
        dialog = GridSettingsDialog(self, self.nx, self.ny, self.nz, self.padding, self.iso_value, self.iso_value_m)
        
        # User clicks 'Apply':
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_data = dialog.get_values()
            if new_data:
                # new values are handed over to main app
                self.nx, self.ny, self.nz, self.padding, self.iso_value, self.iso_vaulue_m = new_data

# change color by right click
    def _on_right_click(self, interactor=None, event=None):
        # 1. Set Zoom Factor to 0 
        # Disables right-click zoom (two-finger gesture).
        style = self.plotter.iren.get_interactor_style()
        if hasattr(style, 'SetDollyMotionFactor'):
            style.SetDollyMotionFactor(0.0)
        
        self.plotter.iren.terminate_app()
        
        # 2. Picking
        click_pos = self.plotter.iren.get_event_position()
        self.plotter.picker.PickProp(click_pos[0], click_pos[1], self.plotter.renderer)
        picked_actor = self.plotter.picker.GetActor()
        
        # 3. Show Dialog
        if picked_actor is not None and hasattr(picked_actor, "_is_orbital"):
            self._change_orbital_color(picked_actor)
        else:
            self._change_background_color()

    def _finalize_ui(self):
        """Macht die GUI wieder ansprechbar."""
        self.plotter.render()
        self.activateWindow()
        self.plotter.setFocus()

    def _open_color_dialog(self, initial_color, title, target_type, actor=None):
        """Zentrale Methode zum Öffnen des nicht-modalen Dialogs."""
        # safe target; either background or orbital-mesh
        self._color_target = {"type": target_type, "actor": actor}
        
        dialog = QColorDialog(QColor(initial_color), self)
        dialog.setWindowTitle(title)
        
        # The 'colorSelected' signal fires when the user clicks OK.
        dialog.colorSelected.connect(self._apply_selected_color)
        # GUI reactivation after closing (regardless of OK or Cancel).
        dialog.finished.connect(self._finalize_ui)
        
        dialog.show() # Non-modal: Prevents macOS from hanging.

    def _apply_selected_color(self, color):
        """Called when a color is selected in the dialog."""
        if not color.isValid():
            return    
        new_hex = color.name()
        new_rgb = color.getRgbF()[:3]
        if self._color_target["type"] == "orbital":
            actor = self._color_target["actor"]
            # 1. Set color on the actor.
            actor.GetProperty().SetColor(new_rgb)
            # 2. Store in class variables for re-plot/export.
            idx = getattr(actor, "_orbital_index", None)
            if idx == 0: self.color_pos = new_hex
            elif idx == 1: self.color_neg = new_hex
            # 3. Store in the mesh field for POV-Ray.
            try:
                actor.GetMapper().GetInput().field_data["chosen_color"] = [new_hex]
            except: pass
        elif self._color_target["type"] == "background":
            self.plotter.set_background(new_hex)
        self.plotter.render()

    def _change_orbital_color(self, actor):
        rgb = actor.GetProperty().GetColor()
        initial_color = QColor.fromRgbF(*rgb).name()
        self._open_color_dialog(initial_color, "Select Orbital Color", "orbital", actor)

    def _change_background_color(self):
        bg_color = pv.Color(self.plotter.background_color).name
        self._open_color_dialog(bg_color, "Select Background Color", "background")
# end color change by right click

# change cmap for esp
    def color_changed(self,value):  # cmap for esp
        self.color=value
        if self.ESP_mesh is not None:
            mapper = self.ESP_mesh.mapper # retrieve mapper
            # create new Lookup Table (LUT), using data range from mesh
            s_range = mapper.dataset.get_data_range()
            lut = pv.LookupTable(cmap=self.color)
            lut.scalar_range = s_range
            # assign LUT to Mapper
            mapper.lookup_table = lut
            # update scale_bar
            for title, actor in self.plotter.scalar_bars.items():
                # Der Actor speichert den Text intern
                verifizierter_titel = actor.GetTitle() 
            self.sargs["title"]=verifizierter_titel
            self.plotter.add_scalar_bar(mapper=self.ESP_mesh.mapper, **self.sargs)
            self.plotter.render()
       
# turn scalar_bar on/off
    def scalar_bar(self,state):  
        showit = (state==0)
        try:
            if showit:
                self.plotter.remove_scalar_bar()
            else:
                self.plotter.add_scalar_bar(mapper=self.ESP_mesh.mapper, **self.sargs)
            self.plotter.render()
        except:
            None

# ----  LOAD FILES ------
    def load_mo_cube(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
        self, "Load MO Cube", "", "output file (*.cube)")
        if files:
            current=self.list_model.stringList()
            for name in files:
                fname=os.path.basename(name)
                if fname not in current:
                    new_data = MoleculeData.from_cube(name)
                    new_data.type="mo_cube"
                    self.dataset_dict[fname]=new_data
                    current.append(fname)
            self.list_model.setStringList(current)
    
    def load_dens_cube(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
        self, "Load Dens Cube", "", "output file (*.cube)")
        if files:
            current=self.list_model.stringList()
            for name in files:
                fname=os.path.basename(name)
                if fname not in current:
                    new_data = MoleculeData.from_cube(name)
                    new_data.type="dens_cube"
                    self.dataset_dict[fname]=new_data
                    current.append(fname)
                    
            self.list_model.setStringList(current)

    def load_esp_cube(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
        self, "Load ESP Cube", "", "output file (*.cube)")
        if files:
            current=self.list_model.stringList()
            for name in files:
                fname=os.path.basename(name)
                if fname not in current:
                    new_data = MoleculeData.from_cube(name)
                    new_data.type="esp_cube"
                    self.dataset_dict[fname]=new_data
                    current.append(fname)
            self.list_model.setStringList(current)

    def load_molden(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
        self, "Load molden file", "", "output file (*.molden)")
        if files:
            current=self.list_model.stringList()
            for name in files:
                fname=os.path.basename(name)
                if fname not in current:
                    try:
                        new_data=MoleculeData.from_molden(name)
                        self.dataset_dict[fname]=new_data
                        current.append(fname)
                    except Exception as e:
                        print(f"Fehler bei {fname}:{e}")
            self.list_model.setStringList(current)

    def load_fchk(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
        self, "Load fchk file", "", "output file (*.fchk)")
        if files:
            current=self.list_model.stringList()
            for name in files:
                fname=os.path.basename(name)
                if fname not in current:
                    try:
                        new_data=MoleculeData.from_fchk(name)
                        self.dataset_dict[fname]=new_data
                        current.append(fname)
                    except Exception as e:
                        print(f"Fehler bei {fname}:{e}")
            self.list_model.setStringList(current)

# ---- SELECT FILES -----
    def file_select(self,index): #click on imported file in "file_list"
        select = index.data()
        self.input_v_min.setText("")
        self.input_v_max.setText("")
        self.mo_list_model.setStringList([]) # delete MO list
        self.mo_list_beta_model.setStringList([]) # delete beta MO list
        try:
            data_ = self.dataset_dict.get(select)
            self.plotter.clear_actors() # clear PyVista Plotter 
            if data_.type != "molden":  #cube file
                visual_objects = draw_mol(data_.atom_points, data_.atom_types, 
                                      self.cpk_colors,self.cov_radii, self.default_radius)
                for mesh, args in visual_objects:
                    self.plotter.add_mesh(mesh, smooth_shading=True, **args)
            else:  #molden file
                if data_:
                    visual_objects = draw_mol(data_.atom_points, data_.atom_types, 
                                      self.cpk_colors,self.cov_radii, self.default_radius)
                    for mesh, args in visual_objects:
                        self.plotter.add_mesh(mesh, smooth_shading=True, **args)
                    is_unrestricted = isinstance(data_.mo_energy[0],(list, tuple, np.ndarray))
                    if is_unrestricted:  # UKS/UHF
                        energy_sets = data_.mo_energy
                        occ_sets = data_.mo_occ
                    else: # closed shell
                        energy_sets = [data_.mo_energy]
                        occ_sets = [data_.mo_occ]
                    for j in range(len(energy_sets)):
                        energies = energy_sets[j]
                        occs = occ_sets[j]
                        orbital_strings = []
                        for i in range(len(energies)):
                            e = energies[i]
                            occ = occs[i]
                            # Formatting: Index (3 digits), Energy (8.4f), Occupation (1.1f)
                            label = f"{i:3d}: {e:8.4f} Ha (Occ: {occ:1.1f})"
                            orbital_strings.append(label)
                        self.mo_models[j].setStringList(orbital_strings)
        except:
            None
    
    def remove_item(self,index): # double click on file in "file_list"
        if not index.isValid():
            return
        item_name= index.data()
        if item_name in self.dataset_dict:
            del self.dataset_dict[item_name]
        self.file_list.model().removeRow(index.row())
        # 1. Clear everything and reset labels.
        self.plotter.clear_actors()

# ---- DRAW MO or ESP -----
    def draw_mo_cube(self):
        self.input_v_min.setEnabled(False) # relevant only for esp grid
        self.input_v_max.setEnabled(False)
        self.input_v_min.setText("")
        self.input_v_max.setText("")
        raw_text = self.input_opacity.text() # opacity
        if raw_text: 
            try:
                opac = float(raw_text) / 100
            except ValueError:
                opac = 0.5
                self.input_opacity.setText("50")
        index = self.file_list.currentIndex()
        data = self.dataset_dict.get(index.data())
        if data.type in {"mo_cube", "dens_cube"}:
            self.orb_mesh = []
            self.plotter.clear_actors()
            # plot molecule structure
            visual_objects  = draw_mol(data.atom_points,data.atom_types, 
                                        self.cpk_colors,self.cov_radii, self.default_radius)
            for mesh, args in visual_objects:
                self.plotter.add_mesh(mesh, smooth_shading=True, **args)
            # plot density
            mesh_args={
                    "opacity":opac, 
                    "pbr":True,            # activate PBR 
                    #"metallic":0.5,        # Metallic
                    "roughness":0.3,       # Gloss-factor
                    "smooth_shading":True
                    }
            
            visual_objects_raw, self.grid = draw_orb(grid=data.grid, iso=0.02)

            # Check: Is it a single object or a MultiBlock
            if isinstance(visual_objects_raw, pv.MultiBlock):
                visual_objects = [visual_objects_raw[i] for i in range(visual_objects_raw.n_blocks)]
            elif hasattr(visual_objects_raw, "n_points"):
                # Single grid (Unstructured/Structured/ImageData)
                # Manually wrapping in a list to enable len() and iteration.
                visual_objects = [visual_objects_raw]
            else:
                visual_objects = list(visual_objects_raw)

            for i in range(len(visual_objects)):
                mesh = visual_objects[i]
                if mesh.n_points == 0:
                    continue 
                # first mesh is positive orbital lobe
                current_color = self.color_pos if i == 0 else self.color_neg
                args.pop('color', None)
                actor = self.plotter.add_mesh(mesh, color=current_color, **mesh_args, **args)
                actor._is_orbital = True
                actor._orbital_index = i 
                self.orb_mesh.append(mesh)
    
    def draw_esp_cube(self):
        self.plotter.clear_actors()
        selection = self.file_list.selectionModel().selectedIndexes()
        items = [index.data() for index in selection]
        data_1=self.dataset_dict.get(items[0])
        data_2=self.dataset_dict.get(items[1])
        #exactly one dens_cube and esp_cube
        if {data_1.type, data_2.type} == {"dens_cube", "esp_cube"}:
            dens_data=next(d for d in [data_1, data_2] if d.type == "dens_cube")
            esp_data=next(d for d in [data_1, data_2] if d.type == "esp_cube")
            # plot molecule structure
            visual_objects = draw_mol(dens_data.atom_points, dens_data.atom_types, 
                                      self.cpk_colors,self.cov_radii, self.default_radius)
            for mesh, args in visual_objects:
                self.plotter.add_mesh(mesh, smooth_shading=True, **args)
            # plot esp surface
            esp_mesh, vmin, vmax, active_scalar = draw_esp(grid_dens=dens_data.grid, 
                                            grid_esp=esp_data.grid,iso_val=0.002)
            mesh_args = self.prep_esp(vmin, vmax, esp_mesh, active_scalar)
            self.ESP_mesh = self.plotter.add_mesh(**mesh_args)

    def draw_mo_molden(self):
        self.plotter.clear_actors()
        self.orb_mesh = []
        index = self.file_list.currentIndex()
        data_ = self.dataset_dict.get(index.data())
        # draw molecule structure
        visual_objects = draw_mol(data_.atom_points, data_.atom_types, 
                                  self.cpk_colors,self.cov_radii, self.default_radius,)
        for mesh, args in visual_objects:
            self.plotter.add_mesh(mesh, smooth_shading=True, **args)
        # plot mo
        tab = self.mo_tab.currentIndex()
        index = self.mo_views[tab].currentIndex()
        if index.isValid():
            orbital_index = index.row()
        else:  # nothing selected
            is_unrestricted = isinstance(data_.mo_occ,(list, tuple))
            if is_unrestricted:  # UKS/UHF
                current_occ = data_.mo_occ[tab]
                orbital_index = max([i for i, occ in enumerate(current_occ) if occ > 0.5], default=0)
            else: # closed shell
                orbital_index = int(sum(data_.mo_occ)/2)-1 #select HOMO
            new_model_index = self.mo_views[tab].model().index(orbital_index, 0)
            self.mo_views[tab].setCurrentIndex(new_model_index)
        raw_text = self.input_opacity.text()
        if raw_text: 
                try:
                    opac = float(raw_text) / 100
                except ValueError:
                    opac = 0.4
                    self.input_opacity.setText("40") 
        mesh_args={
                "opacity":opac, 
                "pbr":True,            # activate PBR 
                #"metallic":0.5,        # Metallic
                "roughness":0.3,       # Gloss-factor
                "smooth_shading":True
            }
        visual_objects_raw, self.grid = draw_orb_molden(data_, orbital_index=orbital_index, 
                 spin_idx=tab, iso_level=self.iso_value, nx=self.nx, ny=self.ny, nz=self.nz, padding=self.padding)  

        if hasattr(visual_objects_raw, "n_blocks"):
        # It is a MultiBlock -> convert to a list of meshes.
            visual_objects = [visual_objects_raw[i] for i in range(visual_objects_raw.n_blocks)]
        else:
        # It is already a list or another iterable
            visual_objects = list(visual_objects_raw)

        for i, item in enumerate(visual_objects):
            # If draw_orb_molden returns a tuple (mesh, args):
            if isinstance(item, tuple):
                mesh, args = item
            else:
                # If it is the mesh itself:
                mesh = item
                args = {}
            # first mesh is positive orbital lobe
            current_color = self.color_pos if i == 0 else self.color_neg
            clean_args = args.copy() if args else {}
            clean_args.pop('color', None)
            actor = self.plotter.add_mesh(mesh, 
                                          color=current_color, 
                                          **mesh_args, **clean_args)
            actor._is_orbital = True
            actor._orbital_index = i 
            self.orb_mesh.append(mesh)
            self.current_mode = "orbital"
        self.plotter.render()

    def draw_dens_molden(self):
        self.plotter.clear_actors()
        self.orb_mesh = []
        raw_text = self.input_opacity.text() # opacity
        if raw_text: 
            try:
                opac = float(raw_text) / 100
            except ValueError:
                opac = 0.5
                self.input_opacity.setText("50")
        index = self.file_list.currentIndex()
        data_ = self.dataset_dict.get(index.data())
        # draw molecule structure
        visual_objects = draw_mol(data_.atom_points, data_.atom_types,
                                self.cpk_colors, self.cov_radii, self.default_radius)
        for mesh, args in visual_objects:
            self.plotter.add_mesh(mesh, smooth_shading=True, **args)
        # plot dens
        mesh_args={
            "opacity":opac, 
            "pbr":True,            # PBR aktivieren
            #"metallic":0.5,        # Metall-Effekt
            "roughness":0.3,       # Glanz-Faktor
            "smooth_shading":True
            }
        visual_objects_raw, self.grid = draw_dens(data_, iso_val=self.iso_value_m, 
                        nx=self.nx, ny=self.ny, nz=self.nz, padding=self.padding)
        if hasattr(visual_objects_raw, "n_blocks"):
        # Es ist ein MultiBlock -> in Liste von Meshes umwandeln
            visual_objects = [visual_objects_raw[i] for i in range(visual_objects_raw.n_blocks)]
        else:
        # Es ist bereits eine Liste oder ein anderes iterierbares Objekt
            visual_objects = list(visual_objects_raw)

        for i, item in enumerate(visual_objects):
            # Falls draw_orb_molden Tupel (mesh, args) zurückgibt:
            if isinstance(item, tuple):
                mesh, args = item
            else:
                # Falls es nur das Mesh direkt ist:
                mesh = item
                args = {}
            # first mesh is positive orbital lobe
            current_color = self.color_pos if i == 0 else self.color_neg
            clean_args = args.copy() if args else {}
            clean_args.pop('color', None)
            actor = self.plotter.add_mesh(mesh, 
                                          color=current_color, 
                                          **mesh_args, **clean_args)
            actor._is_orbital = True
            actor._orbital_index = i 
            self.orb_mesh.append(mesh)
            self.current_mode = "orbital"
        self.plotter.render()

    def draw_esp_molden(self):
        self.plotter.clear_actors()
        self.orb_mesh = []
        index = self.file_list.currentIndex()
        data_ = self.dataset_dict.get(index.data())
        # draw molecule structure
        visual_objects = draw_mol(data_.atom_points, data_.atom_types, 
                            self.cpk_colors,self.cov_radii, self.default_radius)
        for mesh, args in visual_objects:
            self.plotter.add_mesh(mesh, smooth_shading=True, **args)
        
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setFormat(f"calc ESP %p%")
        # 
        mol, dm, surf,_ = prep_esp_molden(data_, iso_val=self.iso_value_m, 
                    nx=self.nx, ny=self.ny, nz=self.nz, padding=self.padding)
    
        self.start_time = time.time() 
        self.progressBar.setRange(0,0)

        self.esp_thread = ESPWorkerThread(dm, mol, surf)
        self.esp_thread.finished.connect(self.on_esp_finished)
        self.esp_thread.start(QThread.HighestPriority)
        self.current_mode = "esp"

    def on_esp_finished(self, result_data):
        """Diese Funktion wird aufgerufen, sobald die Berechnung fertig ist."""
        total_esp, surf = result_data
         
        # Attach result to mesh
        surf.point_data["ESP"] = total_esp
        v_max = np.max(np.abs(total_esp))
        
        # Add Mesh to Plotter
        mesh_args = self.prep_esp(-v_max, v_max, surf, "ESP")
        self.ESP_mesh = self.plotter.add_mesh(**mesh_args)

        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(100)
        self.progressBar.setFormat(f"finished after {time.time() - self.start_time:.2f}s")
        
    def abort_esp(self):
        if hasattr(self, 'esp_thread') and self.esp_thread.isRunning():
            # 1. Set flag (to ignore the result signal).
            self.esp_thread.abort()
            
            # 2. Request the thread to stop
            self.esp_thread.requestInterruption()
            
            # 3. Wait briefly, then force termination if necessary.
            if not self.esp_thread.wait(500): # 500ms Buffer
                self.esp_thread.terminate()   # hard stop
                self.esp_thread.wait()

            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(0)
            self.progressBar.setFormat("terminated by user")  

    def draw_spin_dens(self):
        self.plotter.clear_actors()
        self.orb_mesh = []
        index = self.file_list.currentIndex()
        data_ = self.dataset_dict.get(index.data())
        # draw molecule structure
        visual_objects = draw_mol(data_.atom_points, data_.atom_types, 
                            self.cpk_colors,self.cov_radii, self.default_radius)
        for mesh, args in visual_objects:
            self.plotter.add_mesh(mesh, smooth_shading=True, **args)
        # plot 
        raw_text = self.input_opacity.text()
        if raw_text: 
                try:
                    opac = float(raw_text) / 100
                except ValueError:
                    opac = 0.4
                    self.input_opacity.setText("40") 
        mesh_args={
                "opacity":opac, 
                "pbr":True,            # PBR 
                #"metallic":0.5,        # Metallic
                "roughness":0.3,       # Gloss
                "smooth_shading":True
            }
        visual_objects_raw, self.grid = draw_spin(data_, iso_val=self.iso_value,
                            nx=self.nx, ny=self.ny, nz=self.nz, padding=self.padding)  

        if hasattr(visual_objects_raw, "n_blocks"):
        # It is a MultiBlock -> convert to a list of meshes.
            visual_objects = [visual_objects_raw[i] for i in range(visual_objects_raw.n_blocks)]
        else:
        # It is already a list or another iterable.
            visual_objects = list(visual_objects_raw)

        for i, item in enumerate(visual_objects):
            # If draw_orb_molden returns a tuple (mesh, args):
            if isinstance(item, tuple):
                mesh, args = item
            else:
                # If it is the mesh itself:
                mesh = item
                args = {}
            # first mesh is positive orbital lobe
            current_color = self.color_pos if i == 0 else self.color_neg
            clean_args = args.copy() if args else {}
            clean_args.pop('color', None)
            actor = self.plotter.add_mesh(mesh, 
                                          color=current_color, 
                                          **mesh_args, **clean_args)
            actor._is_orbital = True
            actor._orbital_index = i 
            self.orb_mesh.append(mesh)
        self.current_mode = "spin"
        self.plotter.render()

    def draw_spin_mapped(self):
        self.check_scalar_bar.Checked=False
        self.plotter.clear_actors()
        index = self.file_list.currentIndex()
        data_ = self.dataset_dict.get(index.data())
        # draw molecule structure
        visual_objects = draw_mol(data_.atom_points, data_.atom_types, 
                        self.cpk_colors,self.cov_radii, self.default_radius)
        for mesh, args in visual_objects:
            self.plotter.add_mesh(mesh, smooth_shading=True, **args)
        # plot esp surface
        surf, v_min, v_max, act_sc = draw_spin_mapped(data_, iso_val=self.iso_value_m, 
                    nx=self.nx, ny=self.ny, nz=self.nz, padding=self.padding)

        mesh_args = self.prep_esp(v_min, v_max, surf, act_sc, "SpinDens")
        self.ESP_mesh = self.plotter.add_mesh(**mesh_args)
        self.current_mode = "spin-mapped"

# ---- SAVE IMAGES ------
    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(
                    None, 
                    "Save Image", 
                    f'image', 
                    "Image (*.png)"
                    )
        print(path)
        self.plotter.screenshot(path)

# ---- EXPORT -----
    def export_povray(self):
        path, _ = QFileDialog.getSaveFileName(
                    None, 
                    "Export to Povray", 
                    f'povray.inc', 
                    "Include (*.inc)"
                    )
        object=os.path.splitext(os.path.basename(path))[0]
        selection = self.file_list.selectionModel().selectedIndexes()
        items = [index.data() for index in selection]
        if len(items) == 1:
            data_ = self.dataset_dict.get(items[0])
            match data_.type:
                case "mo_cube":
                    mesh1 = self.orb_mesh[0]
                    mesh2 = self.orb_mesh[1]
                    export_pov_header_mo(filename=path, object_name=object, 
                       trans=0.66, color_pos=self.color_pos, color_neg=self.color_neg)
                    export_pov_header_mol(filename=path)
                    export_pov_mol(data_.atom_points,data_.atom_types,self.cov_radii, self.default_radius,
                                   cpk_colors=self.cpk_colors, filename=path)
                    export_pov_mo(mesh1, mesh2,filename=path, object_name=object)
                case "dens_cube":
                    mesh2 = pv.PolyData()
                    mesh1 = self.orb_mesh[0]
                    export_pov_header_mo(filename=path, object_name=object, 
                       trans=0.66, color_pos=self.color_pos, color_neg=self.color_neg)
                    export_pov_header_mol(filename=path)
                    export_pov_mol(data_.atom_points,data_.atom_types, self.cov_radii, self.default_radius,
                                   cpk_colors=self.cpk_colors, filename=path)
                    export_pov_mo(mesh1, mesh2,filename=path, object_name=object)
                case "molden":
                    if hasattr(self, "current_mode"):
                        match self.current_mode:
                            case "esp":
                                export_pov_header_esp(filename=path, object_name=object, trans=0.66)
                                export_pov_header_mol(filename=path)
                                export_pov_colorbar(filename=path, cmap_name=self.color, 
                                    clim=[self.v_min,self.v_max], height=2.0, radius=0.08 )
                                export_pov_mol(data_.atom_points,data_.atom_types,self.cov_radii, self.default_radius, 
                                        cpk_colors=self.cpk_colors, filename=path)
                                export_pov_esp(self.ESP_mesh, filename=path, object_name=object, 
                                    cmap_name=self.color, clim=[self.v_min,self.v_max])
                            case "orbital":
                                mesh1 = self.orb_mesh[0]
                                mesh2 = self.orb_mesh[1]
                                export_pov_header_mo(filename=path, object_name=object, 
                                    trans=0.66, color_pos=self.color_pos, color_neg=self.color_neg)
                                export_pov_header_mol(filename=path)
                                export_pov_mol(data_.atom_points,data_.atom_types,self.cov_radii, self.default_radius, 
                                        cpk_colors=self.cpk_colors, filename=path)
                                export_pov_mo(mesh1, mesh2,filename=path, object_name=object)
                            case "spin":
                                mesh1 = self.orb_mesh[0]
                                mesh2 = self.orb_mesh[1]
                                export_pov_header_spin(filename=path, object_name=object, 
                                    trans=0.66, color_pos=self.color_pos, color_neg=self.color_neg)
                                export_pov_header_mol(filename=path)
                                export_pov_mol(data_.atom_points,data_.atom_types,self.cov_radii, self.default_radius, 
                                        cpk_colors=self.cpk_colors, filename=path)
                                export_pov_mo(mesh1, mesh2,filename=path, object_name=object)
                            case "spin-mapped":
                                export_pov_header_spin_mapped(filename=path, object_name=object, trans=0.66)
                                export_pov_header_mol(filename=path)
                                export_pov_colorbar(filename=path, cmap_name=self.color, 
                                    clim=[self.v_min,self.v_max], height=2.0, radius=0.08 )
                                export_pov_mol(data_.atom_points,data_.atom_types, self.cov_radii, self.default_radius,
                                        cpk_colors=self.cpk_colors, filename=path)
                                export_pov_esp(self.ESP_mesh, filename=path, object_name=object, 
                                    cmap_name=self.color, clim=[self.v_min,self.v_max])
        elif len(items) ==2:  # esp cube
            data_1=self.dataset_dict.get(items[0])
            data_2=self.dataset_dict.get(items[1])
            if {data_1.type, data_2.type} == {"dens_cube", "esp_cube"}:    
                dens_data=next(d for d in [data_1, data_2] if d.type == "dens_cube")
                export_pov_header_esp(filename=path, object_name=object, trans=0.66)
                export_pov_header_mol(filename=path)
                export_pov_colorbar(filename=path, cmap_name=self.color, 
                        clim=[self.v_min,self.v_max], height=2.0, radius=0.08 )
                export_pov_mol(dens_data.atom_points,dens_data.atom_types,self.cov_radii, self.default_radius, 
                                   cpk_colors=self.cpk_colors, filename=path)
                export_pov_esp(self.ESP_mesh, filename=path, object_name=object, 
                               cmap_name=self.color, clim=[self.v_min,self.v_max])
            else:
                pass
        else:
            pass

    def export_blender(self):
        path, _ = QFileDialog.getSaveFileName(
                    None, 
                    "Export Blender Scene", 
                    "molecule_scene", 
                    "glTF Binary (*.glb);;glTF JSON (*.gltf)"
                    )
        self.plotter.export_gltf(path)

    def export_cube(self):
        path, _ = QFileDialog.getSaveFileName(
                    None, 
                    "Export Cube", 
                    "cube", 
                    "cube (*.cube)"
                    )
        index = self.file_list.currentIndex()
        data_ = self.dataset_dict.get(index.data())

        save_cube(path, data_.mol, self.grid, nx=self.nx, ny=self.ny, nz=self.nz)
        save_xyz(path,data_.mol)

    def export_esp_cube(self):
        filename, _ = QFileDialog.getSaveFileName(
                    None, 
                    "Export Cube", 
                    "cube", 
                    "cube (*.cube)"
                    )
        if not filename: return
        index = self.file_list.currentIndex()
        data_obj = self.dataset_dict.get(index.data())

        # Set progress bar to indeterminate (marquee mode).
        self.progressBar.setRange(0, 0) 
        self.progressBar.setFormat("Exporting Cube (Parallel)...")
        
        index = self.file_list.currentIndex()
        data_obj = self.dataset_dict.get(index.data())

        self.cube_thread = CubeWorkerThread(data_obj, filename, 
                nx=self.nx, ny=self.ny, nz=self.nz, padding=self.padding)
        self.cube_thread.finished.connect(self.on_cube_success)
        self.cube_thread.error.connect(self.on_cube_error)
        self.cube_thread.start()

    def on_cube_success(self, fname):
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(100)
        self.progressBar.setFormat(f"Saved: {fname}")

    def on_cube_error(self, err_msg):
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        QtWidgets.QMessageBox.critical(self, "Export Error", err_msg)

def get_optimal_cores():
    # 1. macOS (Apple Silicon Check)
    if platform.system() == "Darwin":
        try:
            # try to find Performance cores
            output = subprocess.check_output(['sysctl', '-n', 'hw.perflevel0.physicalcpu'], 
                                           stderr=subprocess.DEVNULL) 
            return max(1, int(output.strip()))
        except Exception:
            # in case sysctl fails
            pass

    # 2. Fallback for Windows, Linux und Intel-Macs
    # physical cores minus one
    cores = psutil.cpu_count(logical=False) or os.cpu_count() or 2
    return max(1, cores - 1)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv) 
    try:
        n_threads = get_optimal_cores()
        lib.num_threads(n_threads)
        #print(f"Auto-Config: PySCF uses {n_threads} Threads.")
    except Exception as e:
        print(f"Could not set Threads automatically: {e}")

    window = MoleculeApp()
    window.show()   
    # macOS Fokus-Fix
    window.raise_()
    window.activateWindow()
    
    sys.exit(app.exec())