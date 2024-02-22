import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QRadioButton, QLabel, QStackedWidget, QPushButton, QGroupBox,
                             QHBoxLayout, QSpacerItem, QSizePolicy)
# from PyQt5.QtGui import QFont,QDesktopServices, QTextOption, QTextCursor
from PyQt5.QtCore import Qt


class MachineOptionPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.setupUI()
        
    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.createHeader()
        self.createMachineOptions()
        self.createSelectionPool()
        self.createFooter()
        self.setLayout(self.layout)

    def createHeader(self):
        header = QLabel("BitCurrent", self)
        header.setAlignment(Qt.AlignLeft)
        self.parent.addDetail(self.layout, header, 20, bold=True)
 
    def createMachineOptions(self):
        option_group = QGroupBox("Select Machine to Use", self) 
        options_layout = QVBoxLayout(option_group)
        options_layout.setSpacing(15)

        self.localRadioButton = QRadioButton("Local Computer")
        self.parent.addDetail(options_layout, self.localRadioButton, 16)
        self.localRadioButton.setChecked(True)

        self.cloudRadioButton = QRadioButton("Cloud Computer")
        self.parent.addDetail(options_layout, self.cloudRadioButton, 16)
        
        self.parent.addDetail(self.layout, option_group, 20, bold=True)

    def createSelectionPool(self):    
        # Stacked widget to hold different option sets
        self.optionsStack = QStackedWidget()  
        # local option
        self.localOptions = self.createOptionWidget("Options", self.showLocalOptions,
                                                    [('Use my machine', self.parent.show_miner_options_page)])
        self.optionsStack.addWidget(self.localOptions)
        
        self.cloudOptions = self.createOptionWidget("Options", self.showCloudOptions, [("RunPod", self.runPodAction), ("Vast.ai", self.vastAiAction)])
        self.optionsStack.addWidget(self.cloudOptions)
        
        self.layout.addWidget(self.optionsStack)

        # Connect radio buttons to change the stacked widget index
        self.localRadioButton.toggled.connect(lambda: self.optionsStack.setCurrentIndex(0))
        self.cloudRadioButton.toggled.connect(lambda: self.optionsStack.setCurrentIndex(1))
    
    def createOptionWidget(self, title, default_action=None, additional_buttons=[]):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        self.parent.addDetail(layout,QLabel(title), 20, bold = True)
        
        # itertate through options to create button and actions
        for btn_text, btn_action in additional_buttons:
            button = QPushButton(btn_text)
            self.parent.addDetail(layout, button, 16)
            button.clicked.connect(btn_action)
            widget.setLayout(layout)

        return widget

    def createFooter(self):
        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(self.parent.show_start_page)
        self.parent.addDetail(h_layout, previous_button, 12)
        self.layout.addLayout(h_layout)

    def showLocalOptions(self):
        # Placeholder for local machine options action
        print("Local machine selected")

    def showCloudOptions(self):
        # Placeholder for cloud options action
        print("Cloud options selected")

    def runPodAction(self):
        # Placeholder for RunPod action
        self.parent.show_runpod_page()

    def vastAiAction(self):
        # Placeholder for Vast.ai action
        print("Vast.ai selected")


