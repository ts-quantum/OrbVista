# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QHBoxLayout, QLabel, QLineEdit, QListView,
    QMainWindow, QMenu, QMenuBar, QProgressBar,
    QPushButton, QSizePolicy, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(885, 600)
        self.actioncube_file = QAction(MainWindow)
        self.actioncube_file.setObjectName(u"actioncube_file")
        self.actionESP_Dense_cube = QAction(MainWindow)
        self.actionESP_Dense_cube.setObjectName(u"actionESP_Dense_cube")
        self.actionmolden_file = QAction(MainWindow)
        self.actionmolden_file.setObjectName(u"actionmolden_file")
        self.action_export_povray = QAction(MainWindow)
        self.action_export_povray.setObjectName(u"action_export_povray")
        self.actionimage = QAction(MainWindow)
        self.actionimage.setObjectName(u"actionimage")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionExit_2 = QAction(MainWindow)
        self.actionExit_2.setObjectName(u"actionExit_2")
        self.actionApp = QAction(MainWindow)
        self.actionApp.setObjectName(u"actionApp")
        self.actionExit_3 = QAction(MainWindow)
        self.actionExit_3.setObjectName(u"actionExit_3")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionLoad_MO_cube = QAction(MainWindow)
        self.actionLoad_MO_cube.setObjectName(u"actionLoad_MO_cube")
        self.actionSave_Image = QAction(MainWindow)
        self.actionSave_Image.setObjectName(u"actionSave_Image")
        self.actionLoad_Dens_cube = QAction(MainWindow)
        self.actionLoad_Dens_cube.setObjectName(u"actionLoad_Dens_cube")
        self.actionLoad_ESP_cube = QAction(MainWindow)
        self.actionLoad_ESP_cube.setObjectName(u"actionLoad_ESP_cube")
        self.actionLoad_molden_file = QAction(MainWindow)
        self.actionLoad_molden_file.setObjectName(u"actionLoad_molden_file")
        self.action_draw_mo_cube = QAction(MainWindow)
        self.action_draw_mo_cube.setObjectName(u"action_draw_mo_cube")
        self.action_draw_esp_cube = QAction(MainWindow)
        self.action_draw_esp_cube.setObjectName(u"action_draw_esp_cube")
        self.action_draw_mo_molden = QAction(MainWindow)
        self.action_draw_mo_molden.setObjectName(u"action_draw_mo_molden")
        self.action_draw_mo_molden.setEnabled(True)
        self.action_draw_esp_molden = QAction(MainWindow)
        self.action_draw_esp_molden.setObjectName(u"action_draw_esp_molden")
        self.action_draw_esp_molden.setEnabled(True)
        self.action_export_cube = QAction(MainWindow)
        self.action_export_cube.setObjectName(u"action_export_cube")
        self.action_export_cube.setEnabled(True)
        self.action_export_blender = QAction(MainWindow)
        self.action_export_blender.setObjectName(u"action_export_blender")
        self.action_export_blender.setEnabled(True)
        self.action_draw_dens_molden = QAction(MainWindow)
        self.action_draw_dens_molden.setObjectName(u"action_draw_dens_molden")
        self.action_draw_dens_molden.setEnabled(True)
        self.action_draw_spin_dens = QAction(MainWindow)
        self.action_draw_spin_dens.setObjectName(u"action_draw_spin_dens")
        self.action_draw_spin_mapped = QAction(MainWindow)
        self.action_draw_spin_mapped.setObjectName(u"action_draw_spin_mapped")
        self.action_export_ESP_cube = QAction(MainWindow)
        self.action_export_ESP_cube.setObjectName(u"action_export_ESP_cube")
        self.actionLoad_fchk_file = QAction(MainWindow)
        self.actionLoad_fchk_file.setObjectName(u"actionLoad_fchk_file")
        self.action_export_Cube = QAction(MainWindow)
        self.action_export_Cube.setObjectName(u"action_export_Cube")
        self.action_export_esp_cube = QAction(MainWindow)
        self.action_export_esp_cube.setObjectName(u"action_export_esp_cube")
        self.actionLoad_wfn_file = QAction(MainWindow)
        self.actionLoad_wfn_file.setObjectName(u"actionLoad_wfn_file")
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.plot_widget = QWidget(self.centralwidget)
        self.plot_widget.setObjectName(u"plot_widget")
        self.plot_widget.setGeometry(QRect(230, 10, 641, 481))
        self.colorbox = QComboBox(self.centralwidget)
        self.colorbox.setObjectName(u"colorbox")
        self.colorbox.setGeometry(QRect(130, 20, 91, 26))
        self.file_list = QListView(self.centralwidget)
        self.file_list.setObjectName(u"file_list")
        self.file_list.setGeometry(QRect(10, 40, 111, 201))
        self.file_list.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 20, 111, 16))
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(130, 60, 91, 183))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.input_opacity = QLineEdit(self.layoutWidget)
        self.input_opacity.setObjectName(u"input_opacity")

        self.verticalLayout.addWidget(self.input_opacity)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.input_v_max = QLineEdit(self.layoutWidget)
        self.input_v_max.setObjectName(u"input_v_max")

        self.verticalLayout.addWidget(self.input_v_max)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.input_v_min = QLineEdit(self.layoutWidget)
        self.input_v_min.setObjectName(u"input_v_min")

        self.verticalLayout.addWidget(self.input_v_min)

        self.check_scalar_bar = QCheckBox(self.layoutWidget)
        self.check_scalar_bar.setObjectName(u"check_scalar_bar")
        self.check_scalar_bar.setChecked(True)

        self.verticalLayout.addWidget(self.check_scalar_bar)

        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 260, 101, 16))
        self.mo_tab = QTabWidget(self.centralwidget)
        self.mo_tab.setObjectName(u"mo_tab")
        self.mo_tab.setGeometry(QRect(10, 280, 211, 261))
        self.tab_alpha = QWidget()
        self.tab_alpha.setObjectName(u"tab_alpha")
        self.mo_list = QListView(self.tab_alpha)
        self.mo_list.setObjectName(u"mo_list")
        self.mo_list.setGeometry(QRect(0, 0, 201, 231))
        self.mo_tab.addTab(self.tab_alpha, "")
        self.tab_beta = QWidget()
        self.tab_beta.setObjectName(u"tab_beta")
        self.mo_list_beta = QListView(self.tab_beta)
        self.mo_list_beta.setObjectName(u"mo_list_beta")
        self.mo_list_beta.setGeometry(QRect(0, 0, 201, 231))
        self.mo_tab.addTab(self.tab_beta, "")
        self.layoutWidget1 = QWidget(self.centralwidget)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(240, 510, 331, 36))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.progressBar = QProgressBar(self.layoutWidget1)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"\n"
"            QProgressBar {\n"
"                border: 2px solid grey;\n"
"                border-radius: 5px;\n"
"                text-align: center;\n"
"            }\n"
"            QProgressBar::chunk {\n"
"                background-color: #05B8CC; /* Ein kr\u00e4ftiges Blau/T\u00fcrkis */\n"
"                width: 20px;\n"
"            }\n"
"")
        self.progressBar.setValue(0)

        self.horizontalLayout.addWidget(self.progressBar)

        self.abort = QPushButton(self.layoutWidget1)
        self.abort.setObjectName(u"abort")

        self.horizontalLayout.addWidget(self.abort)

        self.grid_settings = QPushButton(self.centralwidget)
        self.grid_settings.setObjectName(u"grid_settings")
        self.grid_settings.setGeometry(QRect(750, 510, 113, 32))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 885, 33))
        self.menuExport = QMenu(self.menubar)
        self.menuExport.setObjectName(u"menuExport")
        self.menuApp = QMenu(self.menubar)
        self.menuApp.setObjectName(u"menuApp")
        self.menuDraw = QMenu(self.menubar)
        self.menuDraw.setObjectName(u"menuDraw")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuApp.menuAction())
        self.menubar.addAction(self.menuDraw.menuAction())
        self.menubar.addAction(self.menuExport.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuExport.addAction(self.actionSave_Image)
        self.menuExport.addSeparator()
        self.menuExport.addAction(self.action_export_povray)
        self.menuExport.addAction(self.action_export_blender)
        self.menuExport.addSeparator()
        self.menuExport.addAction(self.action_export_Cube)
        self.menuExport.addAction(self.action_export_esp_cube)
        self.menuApp.addAction(self.actionLoad_MO_cube)
        self.menuApp.addAction(self.actionLoad_Dens_cube)
        self.menuApp.addAction(self.actionLoad_ESP_cube)
        self.menuApp.addAction(self.actionLoad_molden_file)
        self.menuApp.addAction(self.actionLoad_fchk_file)
        self.menuApp.addSeparator()
        self.menuApp.addAction(self.actionQuit)
        self.menuDraw.addAction(self.action_draw_mo_cube)
        self.menuDraw.addAction(self.action_draw_esp_cube)
        self.menuDraw.addSeparator()
        self.menuDraw.addAction(self.action_draw_mo_molden)
        self.menuDraw.addAction(self.action_draw_esp_molden)
        self.menuDraw.addAction(self.action_draw_dens_molden)
        self.menuDraw.addAction(self.action_draw_spin_dens)
        self.menuDraw.addAction(self.action_draw_spin_mapped)
        self.menuHelp.addAction(self.actionHelp)

        self.retranslateUi(MainWindow)

        self.mo_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"OrbVista", None))
        self.actioncube_file.setText(QCoreApplication.translate("MainWindow", u"cube file", None))
        self.actionESP_Dense_cube.setText(QCoreApplication.translate("MainWindow", u"ESP/Dense cube", None))
        self.actionmolden_file.setText(QCoreApplication.translate("MainWindow", u"molden file", None))
        self.action_export_povray.setText(QCoreApplication.translate("MainWindow", u" povray inc", None))
        self.actionimage.setText(QCoreApplication.translate("MainWindow", u"image", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionExit_2.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionApp.setText(QCoreApplication.translate("MainWindow", u"App", None))
        self.actionExit_3.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.actionLoad_MO_cube.setText(QCoreApplication.translate("MainWindow", u"Load MO cube", None))
        self.actionSave_Image.setText(QCoreApplication.translate("MainWindow", u"Save Image", None))
        self.actionLoad_Dens_cube.setText(QCoreApplication.translate("MainWindow", u"Load Dens cube", None))
        self.actionLoad_ESP_cube.setText(QCoreApplication.translate("MainWindow", u"Load ESP cube", None))
        self.actionLoad_molden_file.setText(QCoreApplication.translate("MainWindow", u"Load molden file", None))
        self.action_draw_mo_cube.setText(QCoreApplication.translate("MainWindow", u"MO/Dens cube", None))
        self.action_draw_esp_cube.setText(QCoreApplication.translate("MainWindow", u"ESP cube", None))
        self.action_draw_mo_molden.setText(QCoreApplication.translate("MainWindow", u"MO molden", None))
        self.action_draw_esp_molden.setText(QCoreApplication.translate("MainWindow", u"ESP molden", None))
        self.action_export_cube.setText(QCoreApplication.translate("MainWindow", u"MO/Dens cube", None))
        self.action_export_blender.setText(QCoreApplication.translate("MainWindow", u"blender glb", None))
        self.action_draw_dens_molden.setText(QCoreApplication.translate("MainWindow", u"dens molden", None))
        self.action_draw_spin_dens.setText(QCoreApplication.translate("MainWindow", u"Spin dens molden", None))
        self.action_draw_spin_mapped.setText(QCoreApplication.translate("MainWindow", u"Spin dens mappend", None))
        self.action_export_ESP_cube.setText(QCoreApplication.translate("MainWindow", u"ESP cube", None))
        self.actionLoad_fchk_file.setText(QCoreApplication.translate("MainWindow", u"Load fchk file", None))
        self.action_export_Cube.setText(QCoreApplication.translate("MainWindow", u"MO/Dens Cube", None))
        self.action_export_esp_cube.setText(QCoreApplication.translate("MainWindow", u"ESP Cube", None))
        self.actionLoad_wfn_file.setText(QCoreApplication.translate("MainWindow", u"Load wfn file", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"available files", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Opacity %", None))
        self.input_opacity.setText(QCoreApplication.translate("MainWindow", u"50", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"v_max", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"v_min", None))
        self.check_scalar_bar.setText(QCoreApplication.translate("MainWindow", u"scale bar", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"available MOs", None))
        self.mo_tab.setTabText(self.mo_tab.indexOf(self.tab_alpha), QCoreApplication.translate("MainWindow", u"alpha", None))
        self.mo_tab.setTabText(self.mo_tab.indexOf(self.tab_beta), QCoreApplication.translate("MainWindow", u"beta", None))
        self.abort.setText(QCoreApplication.translate("MainWindow", u"abbort", None))
        self.grid_settings.setText(QCoreApplication.translate("MainWindow", u"Grid Settings", None))
        self.menuExport.setTitle(QCoreApplication.translate("MainWindow", u"Export", None))
        self.menuApp.setTitle(QCoreApplication.translate("MainWindow", u"App", None))
        self.menuDraw.setTitle(QCoreApplication.translate("MainWindow", u"Draw", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

