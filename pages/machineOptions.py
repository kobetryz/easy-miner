import os
import subprocess
from functools import partial

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QLabel, QStackedWidget, QPushButton, QGroupBox, \
    QHBoxLayout, QLineEdit, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt


class MachineOptionPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setupUI()

    def setupUI(self):
        self.parent.wandb_api_key = None
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

        local_inputs = []
        self.localOptions = self.createOptionWidget(
            "Options",
            self.showLocalOptions,
            [('Use my machine', self.localAction)],
            local_inputs
        )
        self.optionsStack.addWidget(self.localOptions)

        cloud_inputs = [("Enter Wandb API Key:", 'wandb_api_key', self.parent.wandb_api_key),
                        ("Enter Hotkey mnemonic:", 'mnemonic_hotkey', self.parent.mnemonic_hotkey),
                        ("Enter Coldkey mnemonic:", 'mnemonic_coldkey', self.parent.mnemonic_coldkey)]

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
        self.parent.addDetail(layout, QLabel(title), 20, bold=True)

        # itertate through options to create button and actions
        for btn_text, btn_action in additional_buttons:
            button = QPushButton(btn_text)
            self.parent.addDetail(layout, button, 16)
            button.clicked.connect(btn_action)
            widget.setLayout(layout)

        for input_text, value_name, value in input_fields:
            self.parent.addDetail(layout, QLabel(input_text), 16)
            line_edit = QLineEdit(self)
            line_edit.setText(value)
            self.parent.addDetail(layout, line_edit, 16)
            widget.setLayout(layout)
            line_edit.textChanged.connect(partial(self.updateInputAction, attribute_name=value_name))

        return widget

    def updateInputAction(self, text, attribute_name):
        setattr(self.parent, attribute_name, text)

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
        # Placeholder for RunPod actionc
        # show input for getting the wandb api key
        if self.isAllFieldsFilled():
            self.parent.show_runpod_page()

    def vastAiAction(self):
        # Placeholder for Vast.ai action
        print("Vast.ai selected")

    def localAction(self):
        self.parent.wandb_api_key = self.getLocalWandbApiKey()
        if not self.parent.wandb_api_key:
            self.parent.wandb_api_key, ok = QInputDialog.getText(self, "wandb API key", "Please confirm wandb API key:")
        if not self.parent.wandb_api_key or not self.wandbLogin():
            return
        self.parent.show_local_dashboard_page()

    def isAllFieldsFilled(self):
        if field := self.findUnfilledField():
            widgets = field.parent().children()
            QMessageBox.warning(self, "Warning", f"Field '{widgets[widgets.index(field) - 1].text()}' unfilled")
            return False
        return True

    def findUnfilledField(self):
        options = [self.localOptions, self.cloudOptions]
        for option in options:
            for child in option.children():
                if isinstance(child, QLineEdit) and child.isVisible() and not child.text():
                    return child

    def getLocalWandbApiKey(self):
        path = os.path.join(os.path.expanduser('~'), ".netrc")
        if not os.path.exists(path):
            return
        with open(path) as f:
            for line in f.readlines():
                split_line = line.split()
                if "password" in split_line:
                    return split_line[1]

    def wandbLogin(self):
        try:
            subprocess.check_output(["wandb", "login", self.parent.wandb_api_key], stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            self.parent.wandb_api_key, ok = QInputDialog.getText(self, "Wandb login", "Error login to Wandb, try again")
            if not ok:
                return False
            return self.wandbLogin()
