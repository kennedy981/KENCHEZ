from PyQt5.QtWidgets import * 
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from subprocess import *
import sqlite3

class Ui_Dialog(object):
    def loadData(self):
        try:
            connection=sqlite3.connect('farmers_record.db')
            query="SELECT Roll,Litres,date_delivered,Amount_payable from payment"
            result=connection.execute(query)
            self.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.tableWidget.setItem(row_number,column_number,QtWidgets.QTableWidgetItem(str(data)))
            connection.close()
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','No Data In The Database')

    def update(self):
        try:
            con=sqlite3.connect('farmers_record.db')
            with con:
                cur=con.cursor()
                cur.execute('UPDATE payment set Amount_payable=price*litres')
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','Unable To Update The Database')


    def delete_pay(self):
        try:
            cur=sqlite3.connect('farmers_record.db')
            content='SELECT * FROM payment'
            res=cur.execute(content)
            for row in enumerate(res):
                if row[0] == self.tableWidget.currentRow():
                    data = row[1]
                    Roll=data[0]
                    Price=data[1]
                    Litres=data[2]
                    date_delivered=data[3]
                    Amount_payable=data[4]
                
                    cur.execute("DELETE FROM payment WHERE Roll=? AND Price=? AND Litres=? AND date_delivered=? AND Amount_payable=? ",(Roll,Price,Litres,date_delivered,Amount_payable))
                    cur.commit()
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','Could Not Delete Row')

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(564, 464)
        Dialog.setMinimumSize(QtCore.QSize(564, 464))
        Dialog.setMaximumSize(QtCore.QSize(564, 464))
        Dialog.setToolTipDuration(5)
        Dialog.setAutoFillBackground(True)
        Dialog.setModal(False)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setMinimumSize(QtCore.QSize(546, 410))
        self.tableWidget.setMaximumSize(QtCore.QSize(546, 415))
        self.tableWidget.setFrameShape(QtWidgets.QFrame.Panel)
        self.tableWidget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.tableWidget.setLineWidth(12)
        self.tableWidget.setGridStyle(QtCore.Qt.DashLine)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(113)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 3)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 2, 1, 1)

        self.pushButton.clicked.connect(self.loadData)
        self.pushButton_2.clicked.connect(self.delete_pay)
        self.pushButton_4.clicked.connect(self.update)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Farmer Daily Milk Delivery Table"))
        Dialog.setWhatsThis(_translate("Dialog", "showfarmer daily payment"))
        Dialog.setWindowIcon(QtGui.QIcon('daily.png'))
        self.tableWidget.setSortingEnabled(True)
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Roll"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Litres"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "date_delivered"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Amount_payable"))
        self.pushButton.setText(_translate("Dialog", "load_table"))
        self.pushButton_4.setText(_translate("Dialog", "update_Amount"))
        self.pushButton_2.setText(_translate("Dialog", "delete_row"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
