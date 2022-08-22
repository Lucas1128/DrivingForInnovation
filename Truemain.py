import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow

import main
import sqlite3
import time
from Ui_MainWindow import Ui_MainWindow

connection = sqlite3.connect('DrinksRecord.db')
cursor = connection.cursor()

global DrinkName
global ABYV
global weight
global gender

class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        self.ui.LogButton.clicked.connect(self.Scan)

        self.ui.Continue.clicked.connect(self.Volume)
        self.ui.Cancel.clicked.connect(self.returnhome)

        self.ui.pushButton.clicked.connect(self.one)
        self.ui.pushButton_2.clicked.connect(self.two)
        self.ui.pushButton_3.clicked.connect(self.three)
        self.ui.pushButton_4.clicked.connect(self.four)
        self.ui.pushButton_5.clicked.connect(self.five)
        self.ui.pushButton_6.clicked.connect(self.six)

        self.ui.Cancel_2.clicked.connect(self.returnhome)
        self.ui.Continue_2.clicked.connect(self.Insert)

        self.ui.ConfigButton.clicked.connect(self.ConfigPage)

        self.ui.pushButton_7.clicked.connect(self.SetConfig)

    def show(self):
        self.main_win.show()

    def Scan(self):
        result = main.run()
        print(result)

        global ABYV
        ABYV = int(result[0])
        EName = result[1]
        FName = result[2]
        BName = result[3]

        if EName == 'None': #If the drink does not have a valid English name, use the French Name Instead
            EName = FName

        global DrinkName
        DrinkName = EName

        EName = 'Drink Name: ' + EName
        BName = 'Brand Name: ' + BName



        self.ui.stackedWidget.setCurrentWidget(self.ui.ConfirmPage)

        self.ui.DrinkName.setText(EName)
        self.ui.DrinkBrand.setText(BName)

    def returnhome(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Homepage)

    def Volume(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.WeightPage)

    def one(self):
        self.ui.spinBox.setValue(150)

    def two(self):
        self.ui.spinBox.setValue(285)

    def three(self):
        self.ui.spinBox.setValue(375)

    def four(self):
        self.ui.spinBox.setValue(100)

    def five(self):
        self.ui.spinBox.setValue(30)

    def six(self):
        self.ui.spinBox.setValue(250)

    def Insert(self):
        volume = self.ui.spinBox.value()
        mass = volume * (ABYV / 100) * 0.8

        now = int(time.time())

        cursor.execute(
            """
            INSERT INTO DrinksHistory(DrinkName, UnixTime, Grams)
            VALUES ((:Name), (:Time), (:Grams))
            """,
            {'Name': DrinkName,
             'Time': str(now),
             'Grams': int(round(mass))
             }

        )

        connection.commit()

        self.returnhome()

        global gender
        global weight

        #FILENAME.MATTYBFUNCTION(gender, weight)

    def ConfigPage(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.ConfigPage)

    def SetConfig(self):
        global gender
        gender = self.ui.comboBox.currentText()

        global weight
        weight = self.ui.spinBox_2.value()

        self.returnhome()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())