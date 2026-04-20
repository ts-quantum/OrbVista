# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'grid.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Grid_settings(object):
    def setupUi(self, Grid_settings):
        if not Grid_settings.objectName():
            Grid_settings.setObjectName(u"Grid_settings")
        Grid_settings.resize(391, 211)
        self.layoutWidget = QWidget(Grid_settings)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 11, 248, 178))
        self.formLayout = QFormLayout(self.layoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.edit_padding = QLineEdit(self.layoutWidget)
        self.edit_padding.setObjectName(u"edit_padding")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.edit_padding)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.edit_nx = QLineEdit(self.layoutWidget)
        self.edit_nx.setObjectName(u"edit_nx")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.edit_nx)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.edit_ny = QLineEdit(self.layoutWidget)
        self.edit_ny.setObjectName(u"edit_ny")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.edit_ny)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.edit_nz = QLineEdit(self.layoutWidget)
        self.edit_nz.setObjectName(u"edit_nz")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.edit_nz)

        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.edit_iso = QLineEdit(self.layoutWidget)
        self.edit_iso.setObjectName(u"edit_iso")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.edit_iso)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_6)

        self.edit_iso_m = QLineEdit(self.layoutWidget)
        self.edit_iso_m.setObjectName(u"edit_iso_m")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.edit_iso_m)

        self.layoutWidget1 = QWidget(Grid_settings)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(270, 120, 81, 66))
        self.verticalLayout = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.apply = QPushButton(self.layoutWidget1)
        self.apply.setObjectName(u"apply")

        self.verticalLayout.addWidget(self.apply)

        self.cancel = QPushButton(self.layoutWidget1)
        self.cancel.setObjectName(u"cancel")

        self.verticalLayout.addWidget(self.cancel)

        self.label_7 = QLabel(Grid_settings)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(270, 10, 101, 71))
        self.label_7.setWordWrap(True)

        self.retranslateUi(Grid_settings)

        QMetaObject.connectSlotsByName(Grid_settings)
    # setupUi

    def retranslateUi(self, Grid_settings):
        Grid_settings.setWindowTitle(QCoreApplication.translate("Grid_settings", u"Grid Settings", None))
        self.label.setText(QCoreApplication.translate("Grid_settings", u"padding", None))
        self.label_2.setText(QCoreApplication.translate("Grid_settings", u"nx", None))
        self.label_3.setText(QCoreApplication.translate("Grid_settings", u"ny", None))
        self.label_4.setText(QCoreApplication.translate("Grid_settings", u"nz", None))
        self.label_5.setText(QCoreApplication.translate("Grid_settings", u"iso value Orb", None))
        self.label_6.setText(QCoreApplication.translate("Grid_settings", u"iso value Dens ", None))
        self.apply.setText(QCoreApplication.translate("Grid_settings", u"Apply", None))
        self.cancel.setText(QCoreApplication.translate("Grid_settings", u"Cancel", None))
        self.label_7.setText(QCoreApplication.translate("Grid_settings", u"Re-Plot required to see changes ", None))
    # retranslateUi

