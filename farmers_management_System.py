from PyQt5.QtWidgets import * 
from PyQt5 import QtSql, QtPrintSupport
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from subprocess import *
import sqlite3
import sys
import os
import csv
from payment_table import Ui_Dialog
from farmers_table import Ui_Dialog1


class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("DatabaseViewer")
        self.settings = QSettings(self.objectName())
        self.viewer = QTableView()

#        self.viewer.rowMoved.connect(self.is)

        self.viewer.verticalHeader().setSectionsMovable(True)
        self.viewer.verticalHeader().setDragEnabled(True)
        self.viewer.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)

        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.model = QtSql.QSqlTableModel()
        self.dbfile = ""
        self.tablename = ""
        self.headers = []
        self.results = ""
        self.mycolumn = 0
        self.viewer.verticalHeader().setVisible(True)
        self.setStyleSheet(stylesheet(self))        
        self.viewer.setModel(self.model)
        
        self.dlg = QDialog()
        self.layout = QGridLayout()
        self.layout.addWidget(self.viewer,0, 0, 1, 3)


        self.myWidget = QWidget()
        self.myWidget.setLayout(self.layout)

        self.createToolbar()
        self.statusBar().showMessage("Ready")
        self.setCentralWidget(self.myWidget)
        self.setWindowIcon(QIcon.fromTheme("office-database"))
        self.setGeometry(20,20,600,450)
        self.setWindowTitle("SqliteViewer")
        self.setWindowIcon(QtGui.QIcon('daily.png'))
        self.readSettings()
        self.msg("Ready")
        self.viewer.setFocus()

    def createToolbar(self):
        self.actionOpen = QPushButton("Open DB")
        self.actionOpen.clicked.connect(self.fileOpen)
        icon = QIcon.fromTheme("document-open")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.setShortcutEnabled(True)
        self.actionOpen.setIcon(icon)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setStatusTip("Open Database")
        self.actionOpen.setToolTip("Open Database")

        self.actionSave_comma = QPushButton("Export CSV")
        self.actionSave_comma.clicked.connect(self.fileSaveComma)
        icon = QIcon.fromTheme("document-save-as")
        self.actionSave_comma.setShortcut("Shift+Ctrl+S")
        self.actionSave_comma.setShortcutEnabled(True)
        self.actionSave_comma.setIcon(icon)
        self.actionSave_comma.setObjectName("actionSave_comma")
        self.actionSave_comma.setStatusTip("save comma delimited Text")
        self.actionSave_comma.setToolTip("save comma delimited Text")

        ### first row as headers
        self.actionHeaders = QPushButton()
        icon = QIcon.fromTheme("ok")
        self.actionHeaders.setIcon(icon)
        self.actionHeaders.setToolTip("selected row to headers")
        self.actionHeaders.setShortcut("F5")
        self.actionHeaders.setShortcutEnabled(True)
        self.actionHeaders.setStatusTip("selected row to headers")

        self.actionPreview = QPushButton('Preview')
        self.actionPreview.clicked.connect(self.handlePreview)
        icon = QIcon.fromTheme("document-print-preview")
        self.actionPreview.setShortcut("Shift+Ctrl+P")
        self.actionPreview.setShortcutEnabled(True)
        self.actionPreview.setIcon(icon)
        self.actionPreview.setObjectName("actionPreview")
        self.actionPreview.setStatusTip("Print Preview")
        self.actionPreview.setToolTip("Print Preview")

        self.actionPrint = QPushButton('Print')
        self.actionPrint.clicked.connect(self.handlePrint)
        icon = QIcon.fromTheme("document-print")
        self.actionPrint.setShortcut("Shift+Ctrl+f")
        self.actionPrint.setShortcutEnabled(True)
        self.actionPrint.setIcon(icon)
        self.actionPrint.setObjectName("actionPrint")
        self.actionPrint.setStatusTip("Print")
        self.actionPrint.setToolTip("Print")

        ###############################
        self.tb = self.addToolBar("ToolBar")
        self.tb.setIconSize(QSize(16, 16))
        self.tb.setMovable(False)
        self.tb.addWidget(self.actionOpen)
        self.tb.addWidget(self.actionSave_comma)
        self.tb.addSeparator()
        self.tb.addWidget(self.actionPreview)
        self.tb.addWidget(self.actionPrint)
        ### sep
        self.tb.addSeparator()
        self.tb.addSeparator()
        ### popupMenu
        self.pop = QComboBox()
        self.pop.setFixedWidth(200)
        self.pop.currentIndexChanged.connect(self.setTableName)
        self.tb.addWidget(self.pop)
        self.tb.addSeparator()
        self.addToolBar(self.tb)

    def fileOpen(self):
        tablelist = []
        fileName, _ = QFileDialog.getOpenFileName(None, "Open Database File", "/home/DB", "DB (*.sqlite *.db *.sql3);; All Files (*.*)")
        if fileName:
            self.db.close()
            self.dbfile = fileName
            conn = sqlite3.connect(self.dbfile)
            cur = conn.cursor()
            res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            for name in res:
                print (name[0])
                tablelist.append(name[0])
        self.db.setDatabaseName(self.dbfile)
        self.db.open()
        self.fillComboBox(tablelist)
        self.msg("please choose Table from the ComboBox")

    def fileOpenStartup(self, fileName):
        tablelist = []
        if fileName:
            self.db.close()
            self.dbfile = fileName
            conn = sqlite3.connect(self.dbfile)
            cur = conn.cursor()
            res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            for name in res:
                print (name[0])
                tablelist.append(name[0])
        self.db.setDatabaseName(self.dbfile)
        self.db.open()
        self.fillComboBox(tablelist)
        self.msg("please choose Table from the ComboBox")

    def setAutoWidth(self):
        self.viewer.resizeColumnsToContents()

    def fillComboBox(self, tablelist):
        self.pop.clear()
        self.pop.insertItem(0, "choose Table ...")
        self.pop.setCurrentIndex(0)
        for row in tablelist:
            self.pop.insertItem(self.pop.count(), row)
        if self.pop.count() > 1:
            self.pop.setCurrentIndex(1)
            self.setTableName()

    def fileSaveComma(self):
        if not self.model.rowCount() == 0:
            self.msg("exporting Table")
            conn=sqlite3.connect(self.dbfile)
            c=conn.cursor()
            data = c.execute("SELECT * FROM " + self.tablename)
            headers = [description[0] for description in c.description]
            fileName, _ = QFileDialog.getSaveFileName(None, "Export Table to CSV", self.tablename + ".csv", "CSV Files (*.csv)")
            if fileName:
                with open(fileName, 'w') as f:
                    writer = csv.writer(f, delimiter = ',')
                    writer.writerow(headers)
                    writer.writerows(data)
        else:
            self.msg("nothing to export")



    def setTableName(self):
        if not self.pop.currentText() == "choose Table ...":
            self.tablename = self.pop.currentText()
            print("DB is:", self.dbfile)
            self.msg("initialize")
            self.initializeModel()

    def initializeModel(self):
        print("Table selected:", self.tablename)
        self.model.setTable(self.tablename)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.select()
        self.setAutoWidth()
        self.msg(self.tablename + " loaded *** " + str(self.model.rowCount()) + " records")


    def closeEvent(self, e):
        self.writeSettings()
        e.accept()

    def readSettings(self):
        print("reading settings")
        if self.settings.contains('geometry'):
            self.setGeometry(self.settings.value('geometry'))

    def writeSettings(self):
        print("writing settings")
        self.settings.setValue('geometry', self.geometry())

    def msg(self, message):
        self.statusBar().showMessage(message)

    def handlePrint(self):
        if self.model.rowCount() == 0:
            self.msg("no rows")
        else:
            dialog = QtPrintSupport.QPrintDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.handlePaintRequest(dialog.printer())
                self.msg("Document printed")

    def handlePreview(self):
        if self.model.rowCount() == 0:
            self.msg("no rows")
        else:
            dialog = QtPrintSupport.QPrintPreviewDialog()
            dialog.setFixedSize(1000,700)
            dialog.paintRequested.connect(self.handlePaintRequest)
            dialog.exec_()
            self.msg("Print Preview closed")

    def handlePaintRequest(self, printer):
        printer.setDocName(self.tablename)
        document = QTextDocument()
        cursor = QTextCursor(document)
        model = self.viewer.model()
        tableFormat = QTextTableFormat()
        tableFormat.setBorder(0.2)
        tableFormat.setBorderStyle(3)
        tableFormat.setCellSpacing(0);
        tableFormat.setTopMargin(0);
        tableFormat.setCellPadding(4)
        table = cursor.insertTable(model.rowCount() + 1, model.columnCount(), tableFormat)
        model = self.viewer.model()
        ### get headers
        myheaders = []
        for i in range(0, model.columnCount()):
            myheader = model.headerData(i, Qt.Horizontal)
            cursor.insertText(myheader)
            cursor.movePosition(QTextCursor.NextCell)
        ### get cells
        for row in range(0, model.rowCount()):
           for col in range(0, model.columnCount()):
               index = model.index( row, col )
               cursor.insertText(str(index.data()))
               cursor.movePosition(QTextCursor.NextCell)
        document.print_(printer)
#colors----#20C5C6  #C839C5  #0A2FC4
def stylesheet(self):
        return """
        QTableView
        {
            border: 1px solid grey;
            border-radius: 9px;
            font-size: 10pt;
            background-color:#e8eaf3;
            selection-color: #ffffff;
        }
        QMainWindow{
            border: 2px solid grey;
            border-radius: 78px;
            font-size: 10pt;
            background-color:#FFFFFF;
            selection-color: #ffffff;"""
###################################     


#        -------------------------------------------------------------------------------------------------------------------
'''
     ->DBHelper class holding all important functions for the application
     ->addfarmer() add a farmer given roll,First_name,Last_name,Phone_number,State
     ->searchfarmer() searches for a farmer associating to the given roll number
     ->addPayment() adds the payment to the database
     ->DB has only two tables which has rows and columns in it currently. as the  application expand and
      make it more complex other tables can be created as the need arises
     ->the most important table which is used here is farmers_info and payment
     ->farmers_info holds the records of the farmers and payment hold the records of the payments
'''
#        -----------------------------------------------------------------------------------------------------------------       
class DBHelper():

    #------------------creating tables-------------------------------------
    def __init__(self):
        self.conn=sqlite3.connect('farmers_record.db')
        self.c=self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS farmers_info(Roll integer PRIMARY KEY,ID integer not null,First_name TEXT not null,Last_name TEXT not null,Phone_number TEXT not null,State TEXT not null,join_date datetime)")
        self.c.execute("CREATE TABLE IF NOT EXISTS payment(Roll integer references farmers_info(Roll) on delete cascade,price integer,litres integer,date_delivered timestamp,Amount_payable int)")
        


    #----------------inserting data into the tables-------------------------

    def addPayment(self,Roll,price,litres,date_delivered):
        try:
            self.c.execute("INSERT INTO payment(Roll,price,litres,date_delivered) VALUES(?,?,?,?)",(Roll,price,litres,date_delivered))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(),'successful','farmer added successfully to the database.')
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','could not add farmer to the database')


    #------------searching if farmer in the database--------------------------------------------------

    def addfarmer(self,Roll,ID,First_name,Last_name,Phone_number,State,join_date):
        try:
            self.c.execute("INSERT INTO farmers_info(Roll,ID,First_name,Last_name,Phone_number,State,join_date) VALUES(?,?,?,?,?,?,?)",(Roll,ID,First_name,Last_name,Phone_number,State,join_date))
            self.conn.commit()
            self.c.close()
            self.conn.close()
            QMessageBox.information(QMessageBox(),'successful','farmer added successfully to the database.')
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','could not add farmer to the database')


    #------------searching if farmer in the database--------------------------------------------------

    def searchfarmer(self,Roll):
        try:
            '''
            ->we make a DB query to search for a farmer holding the roll number. if we find any then,we pass the result returned
            from the DB to our custom function showfarmer() which then analyze the list.

            '''
            self.c.execute("SELECT * FROM farmers_info WHERE Roll ="+str(Roll))
            self.data = self.c.fetchone()
            '''
            ->if there is no data returned by above cursor function fetchone() then it means there is no record
            holding the roll number. so we show a warning box saying the same and return from the function.

            '''

            if not self.data:
                QMessageBox.warning(QMessageBox(),'Error','could not find any farmer with Roll no'+str(Roll))
                return None
            self.list=[]
            for i in range(0,6):
                self.list.append(self.data[i])
            self.c.close()
            self.conn.close()
            ##it's out custom function which analyzes the list and show the output in tabular form to the application user.
            showfarmer(self.list)
        except Exception:
            QMessageBox.warning(QMessageBox(),'Error','could not add farmer to the database')

#------------------------------------login class-----------------------------------------------------------------------------------
class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.userNameLabel=QLabel("Username")
        self.userPassLabel=QLabel("Password")
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QGridLayout(self)
        layout.addWidget(self.userNameLabel, 1, 1)
        layout.addWidget(self.userPassLabel, 2, 1)
        layout.addWidget(self.textName,1,2)
        layout.addWidget(self.textPass,2,2)
        layout.addWidget(self.buttonLogin,3,1,1,2)

        self.setWindowTitle("Login")
        self.setWindowIcon(QtGui.QIcon('daily.png'))


    def handleLogin(self):
        if (self.textName.text() == 'admin' and
            self.textPass.text() == 'admin'):
            self.accept()
        else:
            QMessageBox.warning(
                self, 'Error', 'Bad user or password try again')  
    
'''----------------------------------show farmer function----------------------------------------------------------------------------------
function to show the dialog with records of the student returned for the DB holding the roll number.
'''
def showfarmer(list):
    Roll=0
    ID=-1
    First_name=-1
    Last_name=""
    Phone_number=""
    State=""

    Roll=list[0]
    ID=list[1]
    First_name=list[2]
    Last_name=list[3]
    Phone_number=list[4]
    State=list[5]

    #----------designing the table to display the information of the farmer
    '''->we make the table here. Table has six rows and 2 columns.
       ->in PyQt,tables are like grids. you have to place each QTableWidgetItem seprately corresponding to the grid system with x and y
       both starting at 0 index. Then we populate the table with values from the passed list as we got all of them above.
    '''
    table=QTableWidget()
    tableItem=QTableWidgetItem()
    table.setWindowTitle('Farmer Details')
    table.setRowCount(6)
    table.setColumnCount(2)

    table.setItem(0,0,QTableWidgetItem("Roll"))
    table.setItem(0,1,QTableWidgetItem(str(Roll)))
    table.setItem(1,0,QTableWidgetItem("ID"))
    table.setItem(1,1,QTableWidgetItem(str(ID)))
    table.setItem(2,0,QTableWidgetItem("First_name"))
    table.setItem(2,1,QTableWidgetItem(str(First_name)))
    table.setItem(3,0,QTableWidgetItem("Last_name"))
    table.setItem(3,1,QTableWidgetItem(str(Last_name)))
    table.setItem(4,0,QTableWidgetItem("Phone_number"))
    table.setItem(4,1,QTableWidgetItem(str(Phone_number)))
    table.setItem(5,0,QTableWidgetItem("State"))
    table.setItem(5,1,QTableWidgetItem(str(State)))
    table.horizontalHeader().setStretchLastSection(True)
    table.show()

    #------------->creating the QDialog for the table
    dialog=QDialog()
    dialog.setWindowTitle('Farmers Detail')
    dialog.setWindowIcon(QtGui.QIcon('daily.png'))
    dialog.resize(520,380)
    dialog.setLayout(QVBoxLayout())
    dialog.layout().addWidget(table)
    dialog.exec()


'''-------------------------------------------class AddFarmer---------------------------------------------------------------------------------------
->this is class which inherits QDialog to create the entry form of adding farmer functionality.
->it has three buttons. Reset,Add,Cancel.
->Reset clear the text fields, Add calls the function AddFarmer() which in turn calls addfarmer() of DBHelper class.
'''

class AddFamer(QDialog):
    def __init__(self):
        super().__init__()
        self.Roll=-1
        self.ID=-1
        self.First_name=''
        self.Last_name=''
        self.Phone_number=''
        self.State=''
        self.join_date=""

        #--------->creating the default buttons
        self.btnReset=QPushButton('Reset',self)
        self.btnAdd=QPushButton('Add',self)

        #--------->defining the size of the buttons
        self.btnReset.setFixedHeight(30)
        self.btnAdd.setFixedHeight(30)

        #--------->creating Labels
        self.RollLabel=QLabel('Roll')
        self.IDLabel = QLabel('ID')
        self.First_nameLabel = QLabel('First_name')
        self.Last_nameLabel = QLabel('Last_name')
        self.Phone_numberLabel = QLabel('Phone_number')
        self.StateLabel = QLabel('State')
        self.join_dateLabel = QLabel('join_date')

        #----------->creating LineEdit...QRegExpValidotor is used to control the user inputs to ensure correct data type are inserted into the database
        self.RollText=QLineEdit(self)
        self.RollText.setTextMargins(20,0,6,1)
        self.RollText.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,10}$')))
        self.IDText=QLineEdit(self)
        self.IDText.setTextMargins(20,0,6,1)
        self.IDText.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,10}$')))
        self.First_nameText=QLineEdit(self)
        self.First_nameText.setTextMargins(20,0,6,1)
        self.First_nameText.setValidator(QRegExpValidator(QRegExp('^[ A-Za-z]{1,16}$')))
        self.Last_nameText=QLineEdit(self)
        self.Last_nameText.setTextMargins(20,0,6,1)
        self.Last_nameText.setValidator(QRegExpValidator(QRegExp('^[ A-Za-z]{1,16}$')))
        self.Phone_NumberText=QLineEdit(self)
        self.Phone_NumberText.setTextMargins(20,0,6,1)
        self.Phone_NumberText.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,10}$')))
        self.StateText=QLineEdit(self)
        self.StateText.setTextMargins(20,0,6,1)
        self.StateText.setValidator(QRegExpValidator(QRegExp('^[ A-Za-z0-9]{1,16}$')))

        self.join_dateText = QDateTimeEdit(self)
        self.join_dateText.setDateTime(QDateTime.currentDateTime())
        self.join_dateText.setDateTimeRange(QDateTime(1900, 1, 1, 00, 00, 00), QDateTime(2100, 1, 1, 00, 00, 00))
        self.join_dateText.setDisplayFormat('yyyy-MM-dd hh:mm:ss')


        #---------->grid for labels
        self.grid=QGridLayout(self)
        self.grid.addWidget(self.RollLabel,1,1)
        self.grid.addWidget(self.IDLabel,2,1)
        self.grid.addWidget(self.First_nameLabel, 3, 1)
        self.grid.addWidget(self.Last_nameLabel, 4, 1)
        self.grid.addWidget(self.Phone_numberLabel, 5, 1)
        self.grid.addWidget(self.StateLabel, 6, 1)
        self.grid.addWidget(self.join_dateLabel, 7, 1)

        #---------->grid for LineEdit
        self.grid.addWidget(self.RollText,1,2)
        self.grid.addWidget(self.IDText,2,2)
        self.grid.addWidget(self.First_nameText, 3, 2)
        self.grid.addWidget(self.Last_nameText, 4, 2)
        self.grid.addWidget(self.Phone_NumberText, 5, 2)
        self.grid.addWidget(self.StateText, 6, 2)
        self.grid.addWidget(self.join_dateText, 7, 2)

        #----------->grid for default buttons
        self.grid.addWidget(self.btnReset,9,1)
        self.grid.addWidget(self.btnAdd,9,2)

        #----------->connecting to functions
        self.btnAdd.clicked.connect(self.addfarmer)
        self.btnReset.clicked.connect(self.reset)

        #----------->creating QDialog layout and iniating the it
        self.setLayout(self.grid)
        self.setWindowTitle("Add Farmer Details")
        self.setWindowIcon(QtGui.QIcon('daily.png'))
        self.resize(520,380)
        self.show()
        self.exec()

     #-------------->creating the functions to perform tasks   
    def exitWindow(self):
        self.close()

    def reset(self):
        self.RollText.setText("")
        self.IDText.setText("")
        self.First_nameText.setText("")
        self.Last_nameText.setText("")
        self.Phone_NumberText.setText("")
        self.StateText.setText("")

    def addfarmer(self):
        self.Roll=int(self.RollText.text())
        self.onlyInt = QIntValidator()
        self.RollText.setValidator(self.onlyInt)
        self.ID=int(self.IDText.text())
        self.First_name=self.First_nameText.text()
        self.Last_name=self.Last_nameText.text()
        self.Phone_Number=self.Phone_NumberText.text()
        self.State=self.StateText.text()
        self.join_date=self.join_dateText.text()

        self.dbhelper=DBHelper()
        self.dbhelper.addfarmer(self.Roll,self.ID,self.First_name,self.Last_name,self.Phone_Number,self.State,self.join_date)


'''--------------------------------------------------class payment -----------------------------------------------------------------------
it is the dialog for adding payment functionality
'''

class AddPayment(QDialog):
    def __init__(self):
        super().__init__()
        #general variables
        self.Roll=-1
        self.price=-1
        self.litres=-1
        self.date_delivered=''


        self.btnReset=QPushButton('Reset',self)
        self.btnAdd=QPushButton('Add',self)

        self.btnReset.setFixedHeight(30)
        self.btnAdd.setFixedHeight(30)

        self.RollLabel=QLabel('Roll')
        self.priceLabel= QLabel('price')
        self.litresLabel = QLabel('litres')
        self.date_deliveredLabel = QLabel('date_delivered')

        self.RollText=QLineEdit(self)
        self.RollText.setTextMargins(20,0,6,1)
        self.RollText.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,10}$')))
        self.priceText=QLineEdit(self)
        self.priceText.setTextMargins(20,0,6,1)
        self.priceText.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,3}$')))
        self.litresText=QLineEdit(self)
        self.litresText.setTextMargins(20,0,6,1)
        self.litresText.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,5}$')))

        self.date_deliveredText = QDateEdit(self)
        self.date_deliveredText.setDate(QDate.currentDate())
        self.date_deliveredText.setMinimumDate(QDate(1900, 1, 1))
        self.date_deliveredText.setMaximumDate(QDate(2100, 12, 31))
       
        #---------->grid for labels
        self.grid=QGridLayout(self)
        self.grid.addWidget(self.RollLabel,1,1)
        self.grid.addWidget(self.priceLabel,2,1)
        self.grid.addWidget(self.litresLabel, 3, 1)
        self.grid.addWidget(self.date_deliveredLabel, 4, 1)
    
        self.grid.addWidget(self.RollText,1,2)
        self.grid.addWidget(self.priceText,2,2)
        self.grid.addWidget(self.litresText, 3, 2)
        self.grid.addWidget(self.date_deliveredText, 4, 2)

        self.grid.addWidget(self.btnReset,9,1)
        self.grid.addWidget(self.btnAdd,9,2)

        self.btnAdd.clicked.connect(self.addPayment)
        self.btnReset.clicked.connect(self.reset)

        self.setLayout(self.grid)
        self.setWindowTitle("Add Farmer payment Details")
        self.setWindowIcon(QtGui.QIcon('daily.png'))
        self.resize(520,380)
        self.exec()

    def reset(self):
        self.RollText.setText("")
        self.litresText.setText("")

    def addPayment(self):
        self.Roll=int(self.RollText.text())
        self.price=int(self.priceText.text())
        self.litres=self.litresText.text()
        self.date_delivered=self.date_deliveredText.text()
    

        self.dbhelper=DBHelper()
        self.dbhelper.addPayment(self.Roll,self.price,self.litres,self.date_delivered)

'''
->this is the main window which holds everything. It holds for buttons.
->Enter farmer Details
->Enter Payment Details
->Show farmer Details
->Show Payment Details
->it has two functions named enterfarmer() and enterPayment() which show the dialogs created above respectively
->another two functions showfarmer() and showfarmerPaymentDialog() shows dialog for the user to enter the roll number
 he or she wants to search records for.
->showfarmer() which is the actual function which call the corresponding searching function
 DBHelper class.
'''
class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        self.setFixedWidth(500)
        self.setFixedHeight(250)

        QBtn = QDialogButtonBox.Ok  
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        
        self.setWindowTitle("About")
        title = QLabel("Farmers Record Maintainer In PyQt5")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        labelpic = QLabel()
        pixmap = QPixmap('icon/dexter.jpg')
        pixmap = pixmap.scaledToWidth(275)
        labelpic.setPixmap(pixmap)
        labelpic.setFixedHeight(150)

        layout.addWidget(title)

        layout.addWidget(QLabel("v2.0"))
        layout.addWidget(QLabel("Copyright 2020"))
        layout.addWidget(labelpic)


        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w=MyWindow()
        self.CreateMenu()
        self.setWindowIcon(QtGui.QIcon('daily.png'))

        #--------->searching the farmer
        self.RollToBeSearched=0
        self.vbox = QVBoxLayout()
        self.text = QLabel("Enter the roll no of the farmer")
        self.editField = QLineEdit(self)
        self.editField.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,10}$')))
        self.btnSearch = QPushButton("Search", self)
        self.btnSearch.clicked.connect(self.showfarmer)

        self.vbox.addWidget(self.text)
        self.vbox.addWidget(self.editField)
        self.vbox.addWidget(self.btnSearch)

        self.dialog = QDialog()
        self.dialog.setWindowTitle("Enter Roll No")
        self.dialog.setWindowIcon(QtGui.QIcon('daily.png'))
        self.dialog.setLayout(self.vbox)

        self.btnenterPayment=QPushButton("Enter payment Details",self)
        self.btnenterPayment.setStyleSheet('border: 1px solid grey;border-radius: 16px;font-size: 10pt;background-color: #e9eff3;selection-color: #ffffff;')
        self.btnPaywindow=QPushButton("Show Payment",self)
        self.btnPaywindow.setStyleSheet('border: 1px solid grey;border-radius: 16px;font-size: 10pt;background-color: #e9eff3;selection-color: #ffffff;')
        self.btnenterfarmer=QPushButton("Enter farmer Details",self)
        self.btnenterfarmer.setStyleSheet('border: 1px solid grey;border-radius: 16px;font-size: 10pt;background-color: #e9eff3;selection-color: #ffffff;')
        self.btnshowfarmerDetails=QPushButton("Show farmer Details",self)
        self.btnshowfarmerDetails.setStyleSheet('border: 1px solid grey;border-radius: 16px;font-size: 10pt;background-color: #e9eff3;selection-color: #ffffff;')
        self.btndatabaseviewer=QPushButton("SqliteViewer",self)
        self.btndatabaseviewer.setStyleSheet('border: 1px solid grey;border-radius: 16px;font-size: 10pt;background-color: #e9eff3;selection-color: #ffffff;')
        self.btnfarmertable=QPushButton('Farmers_Table',self)
        self.btnfarmertable.setStyleSheet('border: 1px solid grey;border-radius: 16px;font-size: 10pt;background-color: #e9eff3;selection-color: #ffffff;')
       
        self.btnenterPayment.move(270,170)
        self.btnenterPayment.resize(240,40)
        self.btnenterPaymentFont=self.btnenterPayment.font()
        self.btnenterPaymentFont.setPointSize(14)
        self.btnenterPayment.setFont(self.btnenterPaymentFont)
        self.btnenterPayment.clicked.connect(self.enterPayment)

        self.btnPaywindow.move(270, 220)
        self.btnPaywindow.resize(240, 40)
        self.btnPaywindowFont = self.btnenterPayment.font()
        self.btnPaywindowFont.setPointSize(14)
        self.btnPaywindow.setFont(self.btnPaywindowFont)
        self.btnPaywindow.clicked.connect(self.Paywindow)

        self.btnenterfarmer.move(15,170)
        self.btnenterfarmer.resize(240,40)
        self.btnenterfarmerFont=self.btnenterPayment.font()
        self.btnenterfarmerFont.setPointSize(14)
        self.btnenterfarmer.setFont(self.btnenterfarmerFont)
        self.btnenterfarmer.clicked.connect(self.enterfarmer)

        self.btnshowfarmerDetails.move(15, 220)
        self.btnshowfarmerDetails.resize(240, 40)
        self.btnshowfarmerDetailsFont = self.btnenterPayment.font()
        self.btnshowfarmerDetailsFont.setPointSize(14)
        self.btnshowfarmerDetails.setFont(self.btnshowfarmerDetailsFont)
        self.btnshowfarmerDetails.clicked.connect(self.showfarmerDialog)

        self.btndatabaseviewer.move(15,270)
        self.btndatabaseviewer.resize(240,40)
        self.btndatabaseviewerFont=self.btnenterPayment.font()
        self.btndatabaseviewerFont.setPointSize(14)
        self.btndatabaseviewer.setFont(self.btndatabaseviewerFont)
        self.btndatabaseviewer.clicked.connect(self.Sqliteviewer)

        self.btnfarmertable.move(270,270)
        self.btnfarmertable.resize(240,40)
        self.btnfarmertableFont=self.btnenterPayment.font()
        self.btnfarmertableFont.setPointSize(14)
        self.btnfarmertable.setFont(self.btnfarmertableFont)
        self.btnfarmertable.clicked.connect(self.farmers_table)
        self.resize(520,380)
        self.setWindowTitle("Olkalou Daily Farmers")

    def CreateMenu(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        aboutMenu = mainMenu.addMenu('about')

        dropAction = QAction('drop payment', self)
        dropAction.setShortcut("Ctrl+S")
        dropAction.triggered.connect(self.droptable)
        fileMenu.addAction(dropAction)

        dropAction = QAction('drop farmers_info', self)
        dropAction.setShortcut("Ctrl+D")
        dropAction.triggered.connect(self.Droptable)
        fileMenu.addAction(dropAction)

        viewAction = QAction('farmer_table', self)
        viewAction.setShortcut("Ctrl+T")
        viewAction.triggered.connect(self.farmers_table)
        fileMenu.addAction(viewAction)

        viewAction = QAction('payment_table', self)
        viewAction.setShortcut("Ctrl+Y")
        viewAction.triggered.connect(self.Paywindow)
        fileMenu.addAction(viewAction)

        viewAction = QAction('search_farmer', self)
        viewAction.setShortcut("Ctrl+O")
        viewAction.triggered.connect(self.showfarmerDialog)
        fileMenu.addAction(viewAction)


        printAction = QAction('DatabaseViewer', self)
        printAction.setShortcut("Ctrl+P")
        printAction.triggered.connect(self.Sqliteviewer)
        fileMenu.addAction(printAction)

        exiteAction = QAction('Exit', self)
        exiteAction.setShortcut("Ctrl+E")
        exiteAction.triggered.connect(self.exitWindow)
        fileMenu.addAction(exiteAction)

        about_action = QAction("Developer", self)  #info icon
        about_action.triggered.connect(self.about)
        aboutMenu.addAction(about_action)

    def droptable(self):
        con=sqlite3.connect('farmers_record.db')
        with con:
            cur=con.cursor()
            cur.execute('DELETE FROM payment')
            cur.close()

    def Droptable(self):
        con=sqlite3.connect('farmers_record.db')
        with con:
            cur=con.cursor()
            cur.execute('DELETE FROM farmers_info')
            cur.close()

    def exitWindow(self):
        self.close()

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()
    
    def enterPayment(self):
        enterPayment=AddPayment()
    def enterfarmer(self):
        enterfarmer=AddFamer()
    def showfarmerDialog(self):
        self.dialog.exec()
    def showfarmer(self):
        if self.editField.text() is "":
            QMessageBox.warning(QMessageBox(), 'Error','You must give the roll number to show the results for.')
            return None
        showfarmer = DBHelper()
        showfarmer.searchfarmer(int(self.editField.text()))

    def Paywindow(self):
        self.window=QtWidgets.QDialog()
        self.ui=Ui_Dialog()
        self.ui.setupUi(self.window)
        self.window.show()

    def farmers_table(self):
        self.window=QtWidgets.QDialog()
        self.ui=Ui_Dialog1()
        self.ui.setupUi(self.window)
        self.window.show()

    def Sqliteviewer(self, checked):
        if self.w.isVisible():
            self.w.hide()
        else:
            self.w.show()

style="""
QMainWindow{
            font-size: 10pt;
            background-color:#FFFFFF;
            selection-color: #ffffff;
    
}
QPushButton{
            border: 1px solid grey;
            border-radius: 4px;
            font-size: 10pt;
            background-color:#FFFFFF;
            selection-color: #ffffff;
    
}
QLineEdit{
            border:1px solid grey;
            border-radius: 4px;
            font-size: 10pt;
            background-color:#FFFFFF;
            selection-color: #ffffff;
}
QLabel{
            border: 1px solid grey;
            border-radius: 4px;
            font-size: 10pt;
            background-color:#FFFFFF;
            selection-color: #ffffff;
}
QComboBox{
            border: 2px solid grey;
            border-radius: 4px;
            font-size: 10pt;
            background-color:#FFFFFF;
            selection-color: #ffffff;
}
QTableView
        {
            border: 1px solid grey;
            border-radius: 120px;
            font-size: 10pt;
            background-color:#FFFFFF;
            selection-color: #ffffff;
        }
"""


#main function which shows the login dialog first. if user puts the correct username and password it then goes to the main window
#where there are four buttons as mentioned above.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()

    if login.exec_() == QDialog.Accepted:
        window = Window()
        window.show()
    app.setStyleSheet(style)
    if len(sys.argv) > 1:
        print(sys.argv[1])
        main.fileOpenStartup(sys.argv[1])
    sys.exit(app.exec_())


##000000  #C51E14   #1DC121  #C7C329  #0A2FC4  #C839C5  #20C5C6  #C7C7C7  #686868  #FD6F6B  #67F86F  #FFFA72  #6A76FB  #FD7CFC  #68FDFE  #FFFFFF 