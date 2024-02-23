from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QRadioButton, QVBoxLayout, \
    QLabel, QGroupBox, QMessageBox

from config import SubnetType, MinerType


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
        self.createNetOptions()
        self.createMinerOptions()
        self.createFooter()

        self.setLayout(self.layout)

    def createHeader(self):
        header = QLabel("BitCurrent", self)
        header.setAlignment(Qt.AlignTop)
        self.parent.addDetail(self.layout, header, 20, bold=True)

    def createMinerOptions(self):
        self.miner_option_group = QGroupBox("Run as")
        options_layout = QHBoxLayout(self.miner_option_group)
        options_layout.setSpacing(15)

        for miner_type in MinerType:
            radioButton = QRadioButton(miner_type.value.capitalize())
            radioButton.setChecked(miner_type == MinerType.MINER)
            self.parent.addDetail(options_layout, radioButton, 16)

        self.parent.addDetail(self.layout, self.miner_option_group, 20, bold=True)

    def createNetOptions(self):
        self.net_option_group = QGroupBox("Select subnet")
        options_layout = QVBoxLayout(self.net_option_group)
        options_layout.setSpacing(15)

        for net in SubnetType:
            radioButton = QRadioButton(net.value.upper())

            if net == SubnetType.COMPUTE:
                radioButton.setChecked(True)
                radioButton.toggled.connect(self.onNetRadioClicked)  # noqa
            else:
                radioButton.clicked.connect(self.showSubnetNotImplemented)  # noqa
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
        if checked_net.lower() != SubnetType.COMPUTE.value:
            self.showSubnetNotImplemented()
            return
        self.parent.miner_type = MinerType(checked_miner.lower())
        self.parent.net = SubnetType(checked_net.lower())
        self.parent.show_machine_options_page()  # noqa

    def showSubnetNotImplemented(self):
        QMessageBox.warning(self, "Warning", "Current subnet is not implemented")

    def onNetRadioClicked(self):
        sender = self.sender()
        self.next_button.setEnabled(sender.isChecked())

    @staticmethod
    def find_checked_radiobutton(radiobuttons):
        """find the checked radiobutton"""
        for items in radiobuttons:
            if items.isChecked():
                checked_radiobutton = items.text()
                return checked_radiobutton

    @staticmethod
    def addDetail(temp_layout, widget, fontsize, bold=False):
        fontWeight = QFont.Bold if bold else QFont.Normal
        widget.setFont(QFont("Georgia", fontsize, fontWeight))
        temp_layout.addWidget(widget)
