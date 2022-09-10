import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
import webbrowser

import main
import sqlite3
import time
from Ui_MainWindow import Ui_MainWindow
import openpyxl

connection = sqlite3.connect('DrinksRecord.db')
cursor = connection.cursor()

global DrinkName
global ABYV
global currentBAC

wb = openpyxl.load_workbook(filename='Data.xlsx')
sheet = wb['Sheet2']


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

        self.ui.PublicT.clicked.connect(self.pubtran)
        self.ui.Rideshare.clicked.connect(self.rideshare)

    def pubtran(self):
        webbrowser.open('https://translink.com.au/')

    def rideshare(self):
        webbrowser.open('https://www.uber.com/au/en/ride/')


    def show(self):
        self.main_win.show()
        self.updateslider()

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
        self.updateslider()

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


    def updateslider(self):
        BAC = self.calcBAC()
        BAC = round(BAC, 3)
        self.ui.BACNumber.display(str(BAC))

        self.ui.Description.setStyleSheet("font-weight: bold")

        if BAC >= 0.05:
            self.ui.Description.setText('Our estimates show that you have past the legal limit for driving, please consider utilising the alternatives listed below')
            self.ui.Description.setStyleSheet("color: red")
            self.ui.PublicT.setStyleSheet("background-color: red")
            self.ui.Rideshare.setStyleSheet("background-color: red")
            self.ui.Warning.setStyleSheet("color: red")
        elif BAC < 0.002:
            self.ui.Description.setText('You\'re blood alcohol levels are estimated to be negligible, enjoy your night and remember to drink safe')
            self.ui.Description.setStyleSheet("color: black")
            self.ui.PublicT.setStyleSheet("")
            self.ui.Rideshare.setStyleSheet("")
            self.ui.Warning.setStyleSheet("color: black")

        else:
            self.ui.Description.setText('You are estimated to be within the legal limit for driving, however, please continue to exercise your own judgment to protect the saftey of yourself, and those around you!')
            self.ui.Description.setStyleSheet("color: gold; font-weight: bold; background-color: black;")
            self.ui.PublicT.setStyleSheet("background-color: gold")
            self.ui.Rideshare.setStyleSheet("background-color: gold")
            self.ui.Warning.setStyleSheet("color: gold; font-weight: bold; background-color: black;")

        BAC = round(BAC * 1000)
        self.ui.Dial.setValue(BAC)


    def calcBAC(self):

        cursor.execute("""
        SELECT * FROM User
        """)

        connection.commit()

        results = cursor.fetchall()

        weight = results[0][1]
        gender = results[0][2]

        global currentBAC

        weight = weight * 1000

        if gender == 'Male':
            r = 0.68
        elif gender == 'Female':
            r = 0.55
        else:
            r = 0.615

        cursor.execute(
            """
            SELECT * FROM DrinksHistory
            """
        )
        drinks = (cursor.fetchall())
        currentBAC = 0


        drinkcounter = 1
        for i in range(len(drinks)):
            if drinkcounter == len(drinks):
                alchohol = drinks[i][3]
                timeOfDrink = drinks[i][2]
                now = int(time.time())
                timediff = now - timeOfDrink
                timediff = timediff/3600
                newBAC = (alchohol/ (weight * r)) * 100
                currentBAC = (currentBAC + newBAC) - (timediff * 0.015)
                if currentBAC < 0:
                    currentBAC = 0
                else:
                    pass
            else:
                alchohol = drinks[i][3]
                timeOfDrink = drinks[i][2]
                timeOfNextDrink= drinks[int(i+1)][2]
                timediff = timeOfNextDrink - timeOfDrink
                timediff = timediff / 3600
                newBAC = (alchohol / (weight * r)) * 100
                currentBAC = (currentBAC + newBAC) - (timediff * 0.015)
                if currentBAC < 0:
                    currentBAC = 0
                else:
                    pass

            drinkcounter = drinkcounter + 1
        return currentBAC





    def ConfigPage(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.ConfigPage)

    def SetConfig(self):
        gender = self.ui.comboBox.currentText()
        weight = self.ui.spinBox_2.value()

        cursor.execute(
            """
            UPDATE User
            SET weight = (:weight), gender = (:gender)
            """,
            {'weight' : weight,
             'gender' : gender}
        )

        connection.commit()

        self.returnhome()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())