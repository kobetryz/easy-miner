import os
import json

from functools import partial

import bittensor as bt
from PyQt5.QtWidgets import (QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit,
                             QMessageBox, QHBoxLayout, QGroupBox, QSpacerItem,
                             QTextEdit, QSizePolicy, QApplication)
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import pyqtSignal, QThread
from substrateinterface import Keypair

from utils import logger_wrapper


class WalletCreationThread(QThread):
    # Define a signal to emit logs
    log_signal = pyqtSignal(str)

    def __init__(self, wallet_name, wallet_path, wallet_password):
        super().__init__()
        self.wallet_name = wallet_name
        self.wallet_path = wallet_path
        self.wallet_password = wallet_password

    def show_mnemonic(self, keypair, key_type):
        self.log_signal.emit(
                "\nIMPORTANT: Store this mnemonic in a secure (preferable offline place), if someone has your mnemonic, "
                "they have your tao!!. \n"
        )
        self.log_signal.emit("The mnemonic to the new {} is:\n\n{}\n".format(key_type, keypair.mnemonic))
        self.log_signal.emit(
            "You can use the mnemonic to recreate the key in case it gets lost. The command to use to regenerate the key using this mnemonic is:"
        )
        self.log_signal.emit("btcli w regen_{} --mnemonic {}".format(key_type, keypair.mnemonic))
        self.log_signal.emit("")

    def run(self):
        wallet = bt.wallet(name=self.wallet_name, path=self.wallet_path)
        wallet.create_new_hotkey(use_password=False, overwrite=True)
        self.show_mnemonic(wallet.hotkey, "hotkey")
        self.log_signal.emit('Generating coldkey!')
        ck_mnemonic = Keypair.generate_mnemonic()
        ck_keypair = Keypair.create_from_mnemonic(ck_mnemonic)
        wallet._coldkey = ck_keypair
        wallet.coldkey_file.set_keypair(ck_keypair, encrypt=True, password=self.wallet_password, overwrite=True)
        wallet.set_coldkeypub(ck_keypair, overwrite=True)
        self.mnemonic = ck_mnemonic
        self.show_mnemonic(ck_keypair, "coldkey")


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

        # top_spacer = QSpacerItem(1,1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.layout.addItem(top_spacer)
        
        self.createHeader()
        self.createWalletDetails()
        self.createFooter()
        
        # bottom_spacer = QSpacerItem(10, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.layout.addItem(bottom_spacer)

    def createHeader(self):
        header_group = QGroupBox("EasyMiner", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold, italic=True))
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
        self.output_area.setReadOnly(True)  # Make it read-only
        self.log = logger_wrapper(self.output_area.insertPlainText)
        # self.output_area.hide()  # Hide initially
        self.layout.addWidget(self.output_area)

    def createFooter(self):
        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(partial(self.parent.show_start_page, page_to_delete=self))
        self.addDetail(h_layout, previous_button, 12)

        self.save_button = QPushButton("Create", self)
        self.addDetail(h_layout, self.save_button, 12)
        self.save_button.clicked.connect(self.save_wallet_details)

        self.finish_button = QPushButton('Finish', self)
        self.addDetail(h_layout, self.finish_button, 12)
        self.finish_button.clicked.connect(partial(self.parent.show_miner_options_page, page_to_delete=self))
        self.finish_button.setEnabled(False)

        self.layout.addLayout(h_layout)
        self.setLayout(self.layout)

    def addDetail(self, temp_layout, widget, fontsize, bold=False):
        fontWeight = QFont.Bold if bold else QFont.Normal
        widget.setFont(QFont("Georgia", fontsize, fontWeight))
        temp_layout.addWidget(widget)

    def clear_password_fields(self):
        self.wallet_password_input.clear()  # Clear the password fields
        self.confirmed_password.clear()
        self.wallet_password_input.setFocus()

    def save_wallet_details(self):
        if self.wallet_password_input.text() != self.confirmed_password.text():
            QMessageBox.warning(self, "Warning", "Passwords do not match! Please re-enter your password.")
            self.clear_password_fields()
            return
        # self.output_area.show()
        self.log('Checking your password')
        self.wallet_name = self.wallet_name_input.text()
        self.wallet_path = os.path.join(os.path.expanduser('~'), '.bittensor/wallets')


        self.wallet_password = self.wallet_password_input.text()
        # if self.output_area.isVisible():
        self.create_wallet()

    def check_wallet_exists(self):
        if os.path.exists(f'{self.wallet_path}/{self.wallet_name}'):
            return True
        return False

    def create_wallet(self):
        if self.check_wallet_exists():
            answer = QMessageBox.question(self, "Wallet", "Wallet already exists, Do you want to overwrite?")
            if answer == QMessageBox.No:
                self.clear_password_fields()
                return
        self.walletThread = WalletCreationThread(self.wallet_name, self.wallet_path, self.wallet_password)
        self.walletThread.log_signal.connect(self.handle_output)
        self.walletThread.finished.connect(self.on_process_finished)
        self.walletThread.start()
        self.clear_password_fields()

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
                "Please copy nnemonic in the terminal to a safe place! \n This is more important than your password."
            )

        if ok:
            self.save_button.setEnabled(False)
            self.finish_button.setEnabled(True)
        self.copy_mnemonic()

        

    def handle_output(self, text):
        self.log(text)

    def copy_mnemonic(self):
        mnemonic = f"{self.walletThread.mnemonic}"
        print(mnemonic)
        if mnemonic:
            clipboard = QApplication.clipboard()
            clipboard.setText(mnemonic)
            QMessageBox.information(self, "Mnemonic Copied", "Mnemonic copied to clipboard.")
