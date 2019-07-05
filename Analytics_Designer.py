
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import QCoreApplication

class Ui_MainWindow(QWidget):

    def __init__(self):

        QWidget.__init__(self)

    def setupUi(self):

        QWidget.setObjectName("MainWindow")
        QWidget.resize(1124, 738)

        self.centralwidget = QtWidgets.QWidget(QWidget)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)

        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)

        self.button = QPushButton(self.centralwidget)
        self.button.setAutoFillBackground(False)
        self.button.setObjectName("pushButton")
        self.button.setText('Start')
        self.verticalLayout.addWidget(self.pushButton)
        QWidget.setCentralWidget(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(QWidget)
        self.statusbar.setObjectName("statusbar")
        QWidget.setStatusBar(self.statusbar)

        self.retranslateUi(QWidget)
        QtCore.QMetaObject.connectSlotsByName(QWidget)

        #self.show()

    def retranslateUi(self, QWidget):

        _translate = QtCore.QCoreApplication.translate
        QWidget.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button.setText(_translate("MainWindow", "Start"))

def main():

    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = Ui_MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    sys.exit(app.exec_()) # и запускаем приложение

if __name__ == '__main__':
    main()



"""

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(QCoreApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Quit button')
        self.show()

if __name__ == '__main__':
        app = QApplication(sys.argv)
        ex = Example()
        sys.exit(app.exec_())
"""
