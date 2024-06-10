from functools import partial

from PyQt5.QtWidgets import (QPushButton, QLabel, QVBoxLayout, QWidget,
                             QMessageBox, QHBoxLayout, QGroupBox)

from PyQt5.QtGui import QFont,QDesktopServices
from PyQt5.QtCore import QUrl

import requests
from bs4 import BeautifulSoup

from config import VERSION_URL, VERSION, OS_CORE


class StartPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout()

        self.setStyleSheet("""
             QPushButton {
                font-family: 'Georgia'; 
                font-weight: bold;
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 10px;      
                min-height: 30px;
                font-size: 16px;
        }
            QPushButton:hover {
              background-color: #333";
            }
        """)

        # Header block
        header_group = QGroupBox("EasyMiner", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold, italic = True))
        
        header_group.setStyleSheet("font-family: 'Georgia'; \
                                   font-weight: bold;\
                                   color: black; \
                                   padding: 10px;  \
                                   border: None; \
                                   # 1px solid #3498db; \
                                   margin-top: 22px; margin-bottom: 20px;")
       
        header_layout = QHBoxLayout(header_group)
        welcome_message = QLabel("Join the revolution: Mine the Easy Way")
        welcome_message.setFont(QFont("Georgia", 34, QFont.Bold))
        header_layout.addWidget(welcome_message)

        layout.addWidget(header_group)

        # Mining options
        options_group = QGroupBox(self)
        options_group.setFont(QFont("Georgia", 24, QFont.Bold))
        options_layout = QVBoxLayout(options_group)
        
        # Use new wallet
        new_wallet_button = QPushButton("Create New Wallet and Mine", self) 
        new_wallet_button.clicked.connect(self.parent.show_create_wallet_page)
        options_layout.addWidget(new_wallet_button)

        miner_option_button = QPushButton("Mine to Existing Wallet", self)
        miner_option_button.clicked.connect(self.parent.show_miner_options_page)
        options_layout.addWidget(miner_option_button)

        layout.addWidget(options_group)
        
        # footer group
        footer_group = QGroupBox()
        footer_layout = QHBoxLayout(footer_group)
        
        # add about page
        about_button = QPushButton("About")
        about_button.setFont(QFont("Georgia", 12))
        about_button.clicked.connect(self.open_about_url)
        footer_layout.addWidget(about_button)

        # legal
        legal_button = QPushButton("Legal")
        legal_button.setFont(QFont("Georgia", 12))
        legal_button.clicked.connect(self.open_legal_url)
        footer_layout.addWidget(legal_button)

        # Support
        support_button = QPushButton("Support")
        support_button.setFont(QFont("Georgia", 12))
        support_button.clicked.connect(self.open_support_url)
        footer_layout.addWidget(support_button)

        # Terms
        terms_button = QPushButton("Terms of Use")
        terms_button.setFont(QFont("Georgia", 12))
        terms_button.clicked.connect(self.open_terms_url)
        footer_layout.addWidget(terms_button)

        # Check updates
        updates_button = QPushButton("Check updates")
        updates_button.setFont(QFont("Georgia", 12))
        updates_button.clicked.connect(partial(self.check_updates, success_msg=True, error_msg=True))
        footer_layout.addWidget(updates_button)

        footer_group.resize(800,10)
        layout.addWidget(footer_group)

        #  Bottom footnote
        warning_label = QLabel("Please ensure to keep the miner program running at all times.", self)
        warning_label.setFont(QFont("Georgia", 14))
        warning_label.setStyleSheet("QLabel { color : black;padding: 5px; }")   
        warning_label.setFixedSize(800, 50)     
        layout.addWidget(warning_label)
        self.setLayout(layout)
        self.check_updates(success_msg=False, error_msg=False)

    def create_new_wallet(self):
        QMessageBox.information(self, "New Wallet", "The new wallet creation functionality is not implemented yet.")

    def open_about_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))
    
    def open_legal_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))

    def open_support_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))

    def open_terms_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))

    def check_updates(self, success_msg=True, error_msg=True):
        try:
            response = requests.get(VERSION_URL)
        except Exception as e:
            if error_msg:
                QMessageBox.warning(self, "Error", f"Unable to get version, try again\n{str(e)}")
            return
        if not response.status_code == 200:
            if error_msg:
                QMessageBox.warning(self, "Error", "Unable to get version, try again")
            return
        soup = BeautifulSoup(response.text, "html.parser")

        files = soup.find_all("div", {"class": "KL4NAf"})

        remote_version = None
        for file in files:
            split_filename = file.text.split("_")
            if split_filename[0] == OS_CORE:
                remote_version = split_filename[1]

        if not remote_version:
            if error_msg:
                QMessageBox.warning(self, "Error", "Target file on remote server not found, you may try again later")
            return

        if remote_version > VERSION:
            answer = QMessageBox.question(
                self, "Update found", "Update available, do you want to go to Google Drive to download an updated app?"
            )
            if answer == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl(VERSION_URL))
        elif success_msg:
            QMessageBox.information(self, "Info", "Updates not found, your app are up to date")
