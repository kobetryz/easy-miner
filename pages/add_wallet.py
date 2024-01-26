import os
import json
import sys
import time
import bittensor as bt
from PyQt5.QtWidgets import (QPushButton, QLabel, QVBoxLayout,QWidget, QLineEdit, 
                             QMessageBox, QHBoxLayout, QFileDialog, QGroupBox, QSpacerItem, 
                             QTextEdit,QSizePolicy)
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment

class AddWalletPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)      

        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-family: Georgia;
            }
            #     QPushButton:hover {
            #         background-color: #005500;
            #     }
        """)

        # Header Group with links
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QHBoxLayout(header_group)
        
        empty_label = QLabel("", self)
        empty_label.setFont(QFont("Georgia", 18))
        header_layout.addWidget(empty_label)
        header_group.setFixedHeight(20)   
        layout.addWidget(header_group)

        # Wallet Info       
        details_box = QGroupBox()
        details_layout = QVBoxLayout(details_box)
        details_layout.setSpacing(10)
        label = QLabel("Wallet Details", self)
        label.setFont(QFont("Georgia", 26, QFont.Bold))
        details_layout.addWidget(label)

        # Wallet Name
        wallet_name_label = QLabel("Wallet Name", self)
        wallet_name_label.setFont(QFont("Georgia", 16, QFont.Bold))
        details_layout.addWidget(wallet_name_label)
        self.wallet_name_input = QLineEdit(self)
        details_layout.addWidget(self.wallet_name_input)

        # Wallet Path
        wallet_path_label = QLabel("Wallet Path", self)
        wallet_path_label.setFont(QFont("Georgia", 18))
        details_layout.addWidget(wallet_path_label)
        self.wallet_path_input = QLineEdit(self)
        self.wallet_path_input.setPlaceholderText("Select wallet path")
        # self.wallet_path_input.setText(os.getcwd())
        self.wallet_path_input.setText(os.path.join(os.path.expanduser('~'), '.bittensor/wallets'))
        details_layout.addWidget(self.wallet_path_input)
        browse_button = QPushButton("Browse", self)
        browse_button.setFont(QFont("Georgia", 16))
        browse_button.clicked.connect(self.browse_wallet_path)
        details_layout.addWidget(browse_button)
        # details_box.setFixedHeight(200) 
        
        # Password
        wallet_password_label = QLabel("Wallet Password", self)
        wallet_password_label.setFont(QFont("Georgia", 18, QFont.Bold))
        details_layout.addWidget(wallet_password_label)
        self.wallet_password_input = QLineEdit(self)
        self.wallet_password_input.setEchoMode(QLineEdit.Password)  # Hides text entry for password
        details_layout.addWidget(self.wallet_password_input)

        # Confirm password
        wallet_password_label = QLabel("Re-enter wallet password", self)
        wallet_password_label.setFont(QFont("Georgia", 12))
        details_layout.addWidget(wallet_password_label)
        self.confirmed_password = QLineEdit(self)
        self.confirmed_password.setEchoMode(QLineEdit.Password)  # Hides text entry for password  
        details_layout.addWidget(self.confirmed_password)
        
        
        self.output_area = QTextEdit(self)
        self.output_area.setWordWrapMode(QTextOption.NoWrap)
        self.output_area.setReadOnly(False)  # Make it read-only
        self.output_area.hide()  # Hide initially
        details_layout.addWidget(self.output_area)
        
        layout.addWidget(details_box)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(self.parent.show_start_page)
        h_layout.addWidget(previous_button)
        
        # Save Button
        save_button = QPushButton("Save and Mine", self)
        save_button.clicked.connect(self.save_wallet_details)
        h_layout.addWidget(save_button)

        # Add more fields as needed...
        layout.addLayout(h_layout)
        self.setLayout(layout)


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
            return     
        
        self.wallet_name = self.wallet_name_input.text()
        self.wallet_path = self.wallet_path_input.text()
        # self.wallet_password = self.wallet_password_input.text()
        self.mining_process = QProcess(self)
        self.mining_process.setProcessChannelMode(QProcess.MergedChannels)
        self.mining_process.readyReadStandardOutput.connect(self.handle_output)
        command = "python"
        args = ["create_wallet.py", f"--wallet_name={self.wallet_name}", f"--wallet_path={self.wallet_path}"]

        # Start the process
        self.mining_process.start(command, args)
        time.sleep(15)

        
        if self.wallet_name and self.wallet_path:
            self.parent.wallet_name = self.wallet_name
            self.parent.wallet_path = os.path.join(self.wallet_path, self.wallet_name) 
            print(self.parent.wallet_path, '1')
            # new additions based on miner behaviour 
            file_path = f'{self.parent.wallet_path}/hotkeys/default'
            ok = self.edit_file_name(file_path)
            self.parent.show_dashboard_page()
        
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
    
    def handle_output(self):
        self.parent.output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
        self.output_area.append(self.parent.output.replace('|',' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').strip())   
        if self.parent.output.strip().endswith(":") or "password" in self.parent.output:
            print('prompted!!')
            self.process.write(self.wallet_password_input.text().encode())

