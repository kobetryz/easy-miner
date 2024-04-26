import os
import json
import sys
import time
import bittensor as bt

from datetime import datetime
from PyQt5.QtWidgets import (QPushButton, QLabel, QVBoxLayout,QWidget, QLineEdit, 
                             QMessageBox, QHBoxLayout, QFileDialog, QGroupBox, QSpacerItem, 
                             QTextEdit,QSizePolicy)
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment,QTimer, QDateTime

class AddWalletPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setupUI()

        self.mining_process = None
        self.timer = QTimer(self) # Create timer

    
    
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

        # Path
        wallet_path_label = QLabel("Wallet Path", self)
        self.addDetail(details_layout, wallet_path_label, 20, bold = True) 
        
        self.wallet_path_input = QLineEdit(self)
        self.wallet_path_input.setPlaceholderText("Select wallet path")
        # self.wallet_path_input.setText(os.path.join(os.path.expanduser('~'), '.bittensor/wallets'))
        self.wallet_path_input.setText(os.getcwd())

        self.addDetail(details_layout, self.wallet_path_input, 14)
        
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_wallet_path)
        self.addDetail(details_layout, self.browse_button , 14)

        wallet_password_label = QLabel("Wallet Password", self)
        self.addDetail(details_layout, wallet_password_label, 20, bold = True) 

        self.wallet_password_input = QLineEdit(self)
        self.wallet_password_input.setEchoMode(QLineEdit.Password)  # Hides text entry for password
        self.addDetail(details_layout, self.wallet_password_input, 14)

        wallet_password_con_label = QLabel("Re-enter wallet password", self)
        self.addDetail(details_layout, wallet_password_con_label, 14, bold = True) 
      
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
        previous_button.clicked.connect(self.parent.show_start_page)
        self.addDetail(h_layout, previous_button, 12)
        
        # Save Button
        self.save_button = QPushButton("Save", self)
        self.addDetail(h_layout, self.save_button, 12)
        self.save_button.clicked.connect(self.save_wallet_details)
    
        # Add more fields as needed...
        self.finish_button = QPushButton('Finish', self)
        self.addDetail(h_layout, self.finish_button, 12)
        self.finish_button.clicked.connect(self.parent.show_dashboard_page)
        self.finish_button.setEnabled(False) 
        
        self.layout.addLayout(h_layout)
        self.setLayout(self.layout)

    def addDetail(self, temp_layout, widget, fontsize, bold = False):
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
        self.wallet_path = self.wallet_path_input.text()
        
        # self.wallet_password = self.wallet_password_input.text()
        # if self.output_area.isVisible():
        self.create_wallet()    

    def create_wallet(self):
        self.mining_process = QProcess(self)
        self.mining_process.setProcessChannelMode(QProcess.MergedChannels)
        self.mining_process.readyReadStandardOutput.connect(self.handle_output)
        self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Creating Your wallet') 

        # Set environment variables if needed
        env = QProcessEnvironment.systemEnvironment()
        self.mining_process.setProcessEnvironment(env)

        self.start_time = QDateTime.currentDateTime()
        self.timer.start(1000)  # Update timer every second
        self.timer.timeout.connect(self.update_timer)
        
        command = "python"
        args = ["-u", "create_wallet.py", f"--wallet_name={self.wallet_name}", f"--wallet_path={self.wallet_path}"]

        # Start the process
        self.mining_process.start(command, args)
        self.mining_process.finished.connect(self.on_process_finished)
        
    def on_process_finished(self):
        if self.wallet_name and self.wallet_path:
            self.parent.wallet_name = self.wallet_name
            self.parent.wallet_path = os.path.join(self.wallet_path, self.wallet_name) 
            print(self.parent.wallet_path, '1')
            # new additions based on miner behaviour 
            file_path = f'{self.parent.wallet_path}/hotkeys/default'
            ok = self.edit_file_name(file_path)


    # def process_finished(self):
    #     if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
    #         self.mining_process.terminate()
    #         self.mining_process.waitForFinished()
    #         self.mining_process = None

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
            ok = QMessageBox.information(self, "Copy Nnenomic", "Please copy nnemonic in the terminal to a safe place! \n This is higher priority.")

        if ok:
            self.save_button.setEnabled(False)
            self.finish_button.setEnabled(True)

    def update_timer(self):
        # This function is called every second to update the timer display
        if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
            current_time = QDateTime.currentDateTime()
            self.elapsed_time = self.start_time.secsTo(current_time)
            # hours = self.elapsed_time // 3600
            # minutes = (self.elapsed_time % 3600) // 60
            # seconds = self.elapsed_time % 60
            # self.timer_label.setText(f"{hours}h: {minutes}m: {seconds}s") 


    def handle_output(self):
        self.parent.output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
        self.output_area.append(self.parent.output)  
        
         # Check for common prompt indicators
        if self.parent.output.lower().strip().endswith(":") or "password" in self.parent.output.lower():
            input_text =   self.confirmed_password.text + '\n'
            self.process.write(input_text.text().encode())
         
    
    # def handle_output(self):
    #     self.parent.output1 = self.mining_process.readAllStandardOutput().data().decode("utf-8")
    #     self.output_area.append(self.parent.output1.replace('|',' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').strip())
    #     # QApplication.processEvents()    
    #     if self.parent.output1.strip().endswith(":") or "password" in self.parent.output1:
    #         print('prompted!!')
    #         self.process.write(self.wallet_password_input.text().encode()+ b'\n')

    # def handle_output(self):
    #     self.parent.output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
    #     self.output_area.append(self.parent.output.replace('|',' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').strip())   
    #      # Check for common prompt indicators
    #     if 'password' in self.parent.output:
    #         input_text = self.confirmed_password.text() + '\n'
    #         self.mining_process.write(self.input.text().encode())
        # elif self.parent.output1.strip().endswith(":") or "password" in self.parent.output1:
        #     self.input_line.hide()
        #     self.input_button.hide()
        #     self.output_area.setReadOnly(True)