# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pyClefpKdoUc.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QStackedWidget,
    QVBoxLayout, QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1355, 775)
        MainWindow.setStyleSheet(u"background-color: #F8FAFC;\n"
"\n"
"border: none;\n"
"\n"
"")
        MainWindow.setAnimated(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.Sidebar = QWidget(self.widget)
        self.Sidebar.setObjectName(u"Sidebar")
        self.Sidebar.setMinimumSize(QSize(400, 0))
        self.Sidebar.setMaximumSize(QSize(400, 16777215))
        self.Sidebar.setStyleSheet(u"background-color: #0F172A;\n"
"\n"
"")
        self.gridLayout_5 = QGridLayout(self.Sidebar)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticaloptions = QWidget(self.Sidebar)
        self.verticaloptions.setObjectName(u"verticaloptions")
        self.verticaloptions.setStyleSheet(u"QPushButton {\n"
"    background: transparent;\n"
"    border: none;\n"
"    padding: 12px 20px;\n"
"    text-align: left;\n"
"    font-size: 15px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255,255,255,0.08);\n"
"}\n"
"\n"
"QPushButton[active=\"true\"] {\n"
"    background-color: rgba(255,255,255,0.15);\n"
"    border-left: 4px solid #00C2C7;\n"
"}")
        self.verticalLayout = QVBoxLayout(self.verticaloptions)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.menuButton = QPushButton(self.verticaloptions)
        self.menuButton.setObjectName(u"menuButton")
        font = QFont()
        self.menuButton.setFont(font)
        self.menuButton.setStyleSheet(u"color: white;\n"
"\n"
"\n"
"   ")

        self.verticalLayout.addWidget(self.menuButton, 0, Qt.AlignmentFlag.AlignTop)

        self.homeButton = QPushButton(self.verticaloptions)
        self.homeButton.setObjectName(u"homeButton")
        self.homeButton.setFont(font)
        self.homeButton.setStyleSheet(u"color: white;")

        self.verticalLayout.addWidget(self.homeButton)

        self.aboutButton = QPushButton(self.verticaloptions)
        self.aboutButton.setObjectName(u"aboutButton")
        self.aboutButton.setFont(font)
        self.aboutButton.setStyleSheet(u"color: white;")

        self.verticalLayout.addWidget(self.aboutButton)

        self.sheetsButton = QPushButton(self.verticaloptions)
        self.sheetsButton.setObjectName(u"sheetsButton")
        self.sheetsButton.setStyleSheet(u"color: white;")

        self.verticalLayout.addWidget(self.sheetsButton)


        self.gridLayout_5.addWidget(self.verticaloptions, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop)


        self.gridLayout.addWidget(self.Sidebar, 0, 0, 2, 1)

        self.stackedWidget = QStackedWidget(self.widget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"background-color: #F8FAFC;")
        self.Home = QWidget()
        self.Home.setObjectName(u"Home")
        self.gridLayout_4 = QGridLayout(self.Home)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.Logo = QWidget(self.Home)
        self.Logo.setObjectName(u"Logo")
        self.gridLayout_3 = QGridLayout(self.Logo)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label = QLabel(self.Logo)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(500, 500))
        self.label.setPixmap(QPixmap(u":/newPrefix/homeLogo.png"))
        self.label.setScaledContents(True)

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)


        self.gridLayout_4.addWidget(self.Logo, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.Home)
        self.about = QWidget()
        self.about.setObjectName(u"about")
        self.about.setMinimumSize(QSize(913, 0))
        self.gridLayout_7 = QGridLayout(self.about)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.picture = QWidget(self.about)
        self.picture.setObjectName(u"picture")
        self.gridLayout_8 = QGridLayout(self.picture)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.label_2 = QLabel(self.picture)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(180, 150))
        self.label_2.setPixmap(QPixmap(u":/newPrefix/vinicius.png"))
        self.label_2.setScaledContents(True)

        self.gridLayout_8.addWidget(self.label_2, 0, 0, 1, 1)

        self.website = QLabel(self.picture)
        self.website.setObjectName(u"website")
        self.website.setMaximumSize(QSize(180, 180))
        self.website.setPixmap(QPixmap(u":/newPrefix/site.png"))
        self.website.setScaledContents(True)

        self.gridLayout_8.addWidget(self.website, 0, 1, 1, 1)


        self.gridLayout_7.addWidget(self.picture, 2, 0, 1, 1)

        self.aboutText = QWidget(self.about)
        self.aboutText.setObjectName(u"aboutText")
        self.gridLayout_6 = QGridLayout(self.aboutText)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.text = QLabel(self.aboutText)
        self.text.setObjectName(u"text")
        self.text.setMaximumSize(QSize(700, 16777215))
        self.text.setFont(font)
        self.text.setStyleSheet(u"font-size: 25px;\n"
"    color: black;\n"
"    line-height: 22px;")
        self.text.setTextFormat(Qt.TextFormat.RichText)
        self.text.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.text.setWordWrap(True)

        self.gridLayout_6.addWidget(self.text, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.aboutText, 1, 0, 1, 1)

        self.logoAbout = QWidget(self.about)
        self.logoAbout.setObjectName(u"logoAbout")
        self.logoAbout.setMinimumSize(QSize(0, 320))
        self.logoAbout.setMaximumSize(QSize(16777215, 320))
        self.gridLayout_9 = QGridLayout(self.logoAbout)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.label_3 = QLabel(self.logoAbout)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(300, 300))
        self.label_3.setPixmap(QPixmap(u":/newPrefix/logo.png"))
        self.label_3.setScaledContents(True)

        self.gridLayout_9.addWidget(self.label_3, 0, 0, 1, 1)


        self.gridLayout_7.addWidget(self.logoAbout, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.about)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout_10 = QGridLayout(self.page)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.widget_2 = QWidget(self.page)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout = QHBoxLayout(self.widget_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.selectsheetButton = QPushButton(self.widget_2)
        self.selectsheetButton.setObjectName(u"selectsheetButton")
        self.selectsheetButton.setMinimumSize(QSize(200, 200))
        self.selectsheetButton.setMaximumSize(QSize(200, 200))
        icon = QIcon()
        icon.addFile(u":/newPrefix/partiture.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.selectsheetButton.setIcon(icon)
        self.selectsheetButton.setIconSize(QSize(200, 200))

        self.horizontalLayout.addWidget(self.selectsheetButton)


        self.gridLayout_10.addWidget(self.widget_2, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page)

        self.gridLayout.addWidget(self.stackedWidget, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.menuButton.setText(QCoreApplication.translate("MainWindow", u"Menu", None))
        self.homeButton.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.aboutButton.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.sheetsButton.setText(QCoreApplication.translate("MainWindow", u"Sheets", None))
        self.label.setText("")
        self.label_2.setText("")
        self.website.setText("")
        self.text.setText(QCoreApplication.translate("MainWindow", u"PyClef was born from a passion for both music and technology.\n"
"It was created with the goal of simplifying the reading and analysis of musical scores by combining computational intelligence with music theory in a modern, accessible, and efficient tool.\n"
"\n"
"The idea emerged from the need to transform how musicians and students interact with digital sheet musi, making the process more intuitive, faster, and increasingly automated.\n"
"\n"
"Developed by Vin\u00edcius Fernandes, PyClef represents the convergence of artistic creativity and technological innovation.", None))
        self.label_3.setText("")
        self.selectsheetButton.setText("")
    # retranslateUi

