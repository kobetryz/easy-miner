import os
import json

from datetime import datetime
from functools import partial

from PyQt5.QtWidgets import (QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit,
                             QMessageBox, QHBoxLayout, QFileDialog, QGroupBox, QSpacerItem,
                             QTextEdit, QSizePolicy)
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import QProcess, QProcessEnvironment


class AddWalletPage(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.setupUI()

        self.wallet_process = None

    def setupUI(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.createHeader()
        self.createWalletDetails()
        self.createFooter()

    def createHeader(self):
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold))
        header_layout = QHBoxLayout()
        header_group.setLayout(header_layout)
        header_group.setFixedHeight(30)
        self.layout.addWidget(header_group)

    def createWalletDetails(self):
        details_box = QGroupBox()
        details_layout = QVBoxLayout(details_box)
        details_layout.setSpacing(15)
        # Add wallet name label
        self.wallet_name_label = QLabel("Wallet Name", self)
        self.addDetail(details_layout, self.wallet_name_label, 20, bold=True)
        # add space for wallet name
        self.wallet_name_input = QLineEdit(self)
        self.addDetail(details_layout, self.wallet_name_input, 14)
        # Password
        wallet_password_label = QLabel("Wallet Password", self)
        self.addDetail(details_layout, wallet_password_label, 20, bold=True)

        self.wallet_password_input = QLineEdit(self)
        self.wallet_password_input.setEchoMode(QLineEdit.Password)  # Hides text entry for password
        self.addDetail(details_layout, self.wallet_password_input, 14)

        wallet_password_con_label = QLabel("Re-enter wallet password", self)
        self.addDetail(details_layout, wallet_password_con_label, 14, bold=True)

        self.confirmed_password = QLineEdit(self)
        self.confirmed_password.setEchoMode(QLineEdit.Password)  # Hides text entry for password
        self.addDetail(details_layout, self.confirmed_password, 14)

        self.layout.addWidget(details_box)

        self.output_area = QTextEdit(self)
        self.output_area.setWordWrapMode(QTextOption.NoWrap)
        self.output_area.setReadOnly(False)  # Make it read-only
        self.output_area.append(f'New Terminal!!')
        # self.output_area.hide()  # Hide initially
        self.layout.addWidget(self.output_area)

    def createFooter(self):
        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(partial(self.parent.show_start_page, page_to_delete=self))
        self.addDetail(h_layout, previous_button, 12)

        self.save_button = QPushButton("Save", self)
        self.addDetail(h_layout, self.save_button, 12)
        self.save_button.clicked.connect(self.save_wallet_details)

        self.finish_button = QPushButton('Finish', self)
        self.addDetail(h_layout, self.finish_button, 12)
        self.finish_button.clicked.connect(self.parent.show_miner_options_page)
        self.finish_button.setEnabled(False)

        self.layout.addLayout(h_layout)
        self.setLayout(self.layout)

    def addDetail(self, temp_layout, widget, fontsize, bold=False):
        fontWeight = QFont.Bold if bold else QFont.Normal
        widget.setFont(QFont("Georgia", fontsize, fontWeight))
        temp_layout.addWidget(widget)

    def browse_wallet_path(self):
        # Open a QFileDialog to select the path
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.wallet_path = QFileDialog.getExistingDirectory(self, "Select Wallet Path", options=options)
        if self.wallet_path:
            self.wallet_path_input.setText(self.wallet_path)

    def save_wallet_details(self):
        if self.wallet_password_input.text() != self.confirmed_password.text():
            QMessageBox.warning(self, "Warning", "Passwords do not match! Please re-enter your password.")
            self.wallet_password_input.clear()  # Clear the password fields
            self.confirmed_password.clear()
            self.wallet_password_input.setFocus()
            # return
        # self.output_area.show()
        self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Checking your password')
        self.wallet_name = self.wallet_name_input.text()
        self.wallet_path = os.path.join(os.path.expanduser('~'), '.bittensor/wallets')
        self.wallet_password = self.wallet_password_input.text()
        # if self.output_area.isVisible():
        self.create_wallet()

    def create_wallet(self):
        self.wallet_process = QProcess(self)
        self.wallet_process.setProcessChannelMode(QProcess.MergedChannels)
        self.wallet_process.readyReadStandardOutput.connect(self.handle_output)
        self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Creating Your wallet')

        # Set environment variables if needed
        env = QProcessEnvironment.systemEnvironment()
        self.wallet_process.setProcessEnvironment(env)

        command = "python"
        args = [
            "-u", "create_wallet.py",
            f"--wallet_name={self.wallet_name}",
            f"--wallet_path={self.wallet_path}",
            f"--password={self.wallet_password}",
        ]

        # Start the process
        self.wallet_process.start(command, args)
        self.wallet_process.finished.connect(self.on_process_finished)

    def on_process_finished(self):
        if self.wallet_name and self.wallet_path:
            self.parent.wallet_name = self.wallet_name
            self.parent.wallet_path = os.path.join(self.wallet_path, self.wallet_name)
            # new additions based on miner behaviour
            file_path = f'{self.parent.wallet_path}/hotkeys/default'
            self.edit_file_name(file_path)

    def edit_file_name(self, file_path):
        try:
            with open(file_path, 'r') as f:
                address_json = json.load(f)
        except UnicodeDecodeError:
            pass
        self.parent.hotkey = address_json['ss58Address']
        old_path = f'{os.path.join(self.parent.wallet_path)}/hotkeys/default'
        new_path = f'{os.path.join(self.parent.wallet_path)}/hotkeys/{self.parent.hotkey}'
        os.rename(old_path, new_path)
        ok = QMessageBox.information(self, "Save Wallet Details", "Wallet details saved successfully.")
        if ok:
            ok = QMessageBox.information(
                self,
                "Copy Nnenomic",
                "Please copy nnemonic in the terminal to a safe place! \n This is higher priority."
            )

        if ok:
            self.save_button.setEnabled(False)
            self.finish_button.setEnabled(True)

    def handle_output(self):
        self.parent.output = self.wallet_process.readAllStandardOutput().data().decode("utf-8")
        self.output_area.append(self.parent.output)
        if "overwrite? (y/n)" in self.parent.output.lower():
            answer = QMessageBox.question(self, "Wallet", "Wallet already exist, overwrite?")
            if answer == QMessageBox.Yes:
                self.wallet_process.write(b"y\n")
            else:
                self.wallet_process.write(b"n\n")
            return
