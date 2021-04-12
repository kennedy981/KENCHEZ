from PyQt5.QtWidgets import * 
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from subprocess import *

import sqlite3
class Ui_Dialog1(object):

    def loadData(self):
        try:
            connection=sqlite3.connect('farmers_record.db')
            query="SELECT * from farmers_info"
            result=connection.execute(query)
            self.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.tableWidget.insertRow(row_number)
                for column_number,data in enumerate(row_data):
                    self.tableWidget.setItem(row_number,column_number,QtWidgets.QTableWidgetItem(str(data)))
            connection.close()
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','Database Is Empty')

    def delete_data(self):
        try:
            cur=sqlite3.connect('farmers_record.db')
            content='SELECT * FROM farmers_info'
            res=cur.execute(content)
            for row in enumerate(res):
                if row[0] == self.tableWidget.currentRow():
                    data = row[1]
                    Roll=data[0]
                    ID=data[1]
                    First_name=data[2]
                    Last_name=data[3]
                    Phone_number=data[4]
                    State=data[5]
                    cur.execute("DELETE FROM farmers_info WHERE Roll=? AND First_name=? AND Last_name=? AND Phone_number=? AND State=? ",(Roll,First_name,Last_name,Phone_number,State))
                    cur.commit()
                    self.loadData
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','Unable To Delete')



    def entire_database(self):
        try:
            con=sqlite3.connect('farmers_record.db')
            with con:
                cur=con.cursor()
                cur.execute('DELETE FROM farmers_info')
                cur.close()
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','Unable To Drop The Table')

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(741, 487)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(111)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 3)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 1, 2, 1, 1)

        self.pushButton.clicked.connect(self.loadData)
        self.pushButton_2.clicked.connect(self.delete_data)
        self.pushButton_3.clicked.connect(self.entire_database)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        Dialog.setWindowIcon(QtGui.QIcon('daily.png'))
        self.tableWidget.setSortingEnabled(True)
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Roll"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "ID"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "First_name"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Last_name"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "Phone_number"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("Dialog", "State"))
        self.pushButton.setText(_translate("Dialog", "loadall"))
        self.pushButton_2.setText(_translate("Dialog", "delete"))
        self.pushButton_3.setText(_translate("Dialog", "drop_table"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog1()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
