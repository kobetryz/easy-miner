from functools import partial

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QLabel, QStackedWidget, QPushButton, QGroupBox, \
    QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt


class MachineOptionPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.wandbApiKey = None
        self.mnemonicHotkey = None
        self.mnemonicColdkey = None
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

        local_inputs = [("Enter Wandb API Key:", 'wandbApiKey')]
        self.localOptions = self.createOptionWidget(
            "Options",
            self.showLocalOptions,
            [('Use my machine', self.parent.show_dashboard_page)],
            local_inputs
        )
        self.optionsStack.addWidget(self.localOptions)

        cloud_inputs = (local_inputs +
                        [("Enter Hotkey mnemonic:", 'mnemonicHotkey'), ("Enter Coldkey mnemonic:", 'mnemonicColdkey')])

        self.cloudOptions = self.createOptionWidget(
            "Options",
            self.showCloudOptions,
            [("RunPod", self.runPodAction), ("Vast.ai", self.vastAiAction)],
            cloud_inputs)
        self.optionsStack.addWidget(self.cloudOptions)

        self.layout.addWidget(self.optionsStack)

        # Connect radio buttons to change the stacked widget index
        self.localRadioButton.toggled.connect(lambda: self.optionsStack.setCurrentIndex(0))
        self.cloudRadioButton.toggled.connect(lambda: self.optionsStack.setCurrentIndex(1))
    
    def createOptionWidget(self, title, default_action=None, additional_buttons=None, input_fields=None):
        if additional_buttons is None:
            additional_buttons = []
        if input_fields is None:
            input_fields = []
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

        for input_text, value_name in input_fields:
            self.parent.addDetail(layout, QLabel(input_text), 16)
            line_edit = QLineEdit(self)
            self.parent.addDetail(layout, line_edit, 16)
            widget.setLayout(layout)
            line_edit.textChanged.connect(partial(self.updateInputAction, attribute_name=value_name))

        return widget

    def updateInputAction(self, text, attribute_name):
        setattr(self, attribute_name, text)

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
        # show input for getting the wandb api key

        self.parent.show_runpod_page()

    def vastAiAction(self):
        # Placeholder for Vast.ai action
        print("Vast.ai selected")


