from enum import Enum

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QRadioButton, QVBoxLayout, QLabel, QGroupBox


class MinerType(Enum):
    MINER = 'miner'
    VALIDATOR = 'validator'


class MinerOptionsPage(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent

        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.createHeader()
        self.createMinerOptions()
        self.createNetOptions()
        self.createFooter()

        self.setLayout(self.layout)

    def createHeader(self):
        header = QLabel("BitCurrent", self)
        header.setAlignment(Qt.AlignTop)
        self.parent.addDetail(self.layout, header, 20, bold=True)

    def createMinerOptions(self):
        self.miner_option_group = QGroupBox("Select mode")
        options_layout = QVBoxLayout(self.miner_option_group)
        options_layout.setSpacing(15)

        self.minerRadioButton = QRadioButton("Miner")
        self.minerRadioButton.setChecked(True)
        self.parent.addDetail(options_layout, self.minerRadioButton, 16)

        self.validatorRadioButton = QRadioButton("Validator")
        self.parent.addDetail(options_layout, self.validatorRadioButton, 16)

        self.parent.addDetail(self.layout, self.miner_option_group, 20, bold=True)

    def createNetOptions(self):
        self.net_option_group = QGroupBox("Select net")
        self.net_option_group.setAlignment(Qt.AlignTop)
        options_layout = QVBoxLayout(self.net_option_group)
        options_layout.setSpacing(15)
        #  TODO: change the nets to the actual nets
        nets = [
            25,
        ]
        for net in nets:
            radioButton = QRadioButton(str(net))
            radioButton.setChecked(net == nets[0])
            self.parent.addDetail(options_layout, radioButton, 16)

        self.parent.addDetail(self.layout, self.net_option_group, 20, bold=True)

    def createFooter(self):
        h_layout = QHBoxLayout(self)
        h_layout.setAlignment(Qt.AlignBottom)
        previous_button = QPushButton("Back to Main Menu")
        previous_button.clicked.connect(self.parent.show_start_page)  # noqa
        self.addDetail(h_layout, previous_button, 12)

        self.next_button = QPushButton('Next')
        self.addDetail(h_layout, self.next_button, 12)
        self.next_button.clicked.connect(self.nextClicked)  # noqa

        self.layout.addLayout(h_layout)

    def nextClicked(self):
        checked_miner = self.find_checked_radiobutton(self.miner_option_group.findChildren(QtWidgets.QRadioButton))
        checked_net = self.find_checked_radiobutton(self.net_option_group.findChildren(QtWidgets.QRadioButton))
        self.parent.miner_type = MinerType(checked_miner.lower())
        self.parent.net = checked_net
        self.parent.show_dashboard_page()  # noqa

    @staticmethod
    def find_checked_radiobutton(radiobuttons):
        ''' find the checked radiobutton '''
        for items in radiobuttons:
            if items.isChecked():
                checked_radiobutton = items.text()
                return checked_radiobutton

    @staticmethod
    def addDetail(temp_layout, widget, fontsize, bold=False):
        fontWeight = QFont.Bold if bold else QFont.Normal
        widget.setFont(QFont("Georgia", fontsize, fontWeight))
        temp_layout.addWidget(widget)
