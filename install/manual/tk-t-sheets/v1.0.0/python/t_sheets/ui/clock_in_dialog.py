# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Adam\OneDrive\Documents\Scripts\Python\Shotgun\tk-t-sheets\tk-t-sheets\install\manual\tk-t-sheets\v0.1.0\resources\clock_in_dialog.ui'
#
# Created: Sun Nov 12 19:01:54 2017
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(593, 300)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.employee_name_2 = QtGui.QLabel(Dialog)
        self.employee_name_2.setStyleSheet("font: 75 14pt \"Arial\";")
        self.employee_name_2.setObjectName("employee_name_2")
        self.verticalLayout_3.addWidget(self.employee_name_2)
        self.statement = QtGui.QLabel(Dialog)
        self.statement.setStyleSheet("font: 75 14pt \"Arial\";color: rgb(255, 0, 0);")
        self.statement.setObjectName("statement")
        self.verticalLayout_3.addWidget(self.statement)
        self.question = QtGui.QLabel(Dialog)
        self.question.setStyleSheet("font: 75 12pt \"Arial\";")
        self.question.setObjectName("question")
        self.verticalLayout_3.addWidget(self.question)
        self.current_project = QtGui.QLabel(Dialog)
        self.current_project.setStyleSheet("font: 8pt \"Arial\";")
        self.current_project.setObjectName("current_project")
        self.verticalLayout_3.addWidget(self.current_project)
        self.current_entity_label = QtGui.QLabel(Dialog)
        self.current_entity_label.setStyleSheet("font: 8pt \"Arial\";")
        self.current_entity_label.setObjectName("current_entity_label")
        self.verticalLayout_3.addWidget(self.current_entity_label)
        self.current_task_label = QtGui.QLabel(Dialog)
        self.current_task_label.setStyleSheet("font: 8pt \"Arial\";")
        self.current_task_label.setObjectName("current_task_label")
        self.verticalLayout_3.addWidget(self.current_task_label)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.yes_btn_2 = QtGui.QPushButton(Dialog)
        self.yes_btn_2.setStyleSheet("background-color: rgb(0, 255, 0);font: 75 10pt \"Arial\";color: rgb(0, 0, 0);")
        self.yes_btn_2.setObjectName("yes_btn_2")
        self.horizontalLayout_3.addWidget(self.yes_btn_2)
        self.no_btn_2 = QtGui.QPushButton(Dialog)
        self.no_btn_2.setStyleSheet("background-color: rgb(255, 0, 0);color: rgb(0, 0, 0);font: 75 10pt \"Arial\";")
        self.no_btn_2.setObjectName("no_btn_2")
        self.horizontalLayout_3.addWidget(self.no_btn_2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.employee_name_2.setText(QtGui.QApplication.translate("Dialog", "Employee Name", None, QtGui.QApplication.UnicodeUTF8))
        self.statement.setText(QtGui.QApplication.translate("Dialog", "You are not Clocked In!", None, QtGui.QApplication.UnicodeUTF8))
        self.question.setText(QtGui.QApplication.translate("Dialog", "Would you Like to Clock In to the Following?", None, QtGui.QApplication.UnicodeUTF8))
        self.current_project.setText(QtGui.QApplication.translate("Dialog", "Project Name", None, QtGui.QApplication.UnicodeUTF8))
        self.current_entity_label.setText(QtGui.QApplication.translate("Dialog", "Asset / Shot", None, QtGui.QApplication.UnicodeUTF8))
        self.current_task_label.setText(QtGui.QApplication.translate("Dialog", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.yes_btn_2.setText(QtGui.QApplication.translate("Dialog", "Yes", None, QtGui.QApplication.UnicodeUTF8))
        self.no_btn_2.setText(QtGui.QApplication.translate("Dialog", "No", None, QtGui.QApplication.UnicodeUTF8))

