# Plug and Play miner
# Kofi Osei - Bonsu 
# 30/12/2023 


import os
import sys
import json

import bittensor as bt
from config import search_directory

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QTextEdit, QMessageBox, QStackedWidget, QHBoxLayout, QFileDialog, 
    QGroupBox, QInputDialog, QSpacerItem, QSizePolicy
)

from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QColor, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl

from pages.startpage import StartPage
from pages.add_wallet import AddWalletPage
from pages.dashboard import DashboardPage
from pages.wallet import WalletDetailsTable
from pages.machineOptions import MachineOptionPage


class MiningWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.initialize_subtensor()
        self.setup_ui()
        self.initialize_pages()

        #initialise vars
        self.wallet_name = None
        self.wallet_path = None

    # methods to open pages
    def initialize_subtensor(self):
        self.subtensor = bt.subtensor(network='test')
        self.subnet = self.subtensor.metagraph(netuid=25)
    
    def setup_ui(self):
        self.setWindowTitle("Easy Miner")
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
    
    def initialize_pages(self):
        # Initialize and add Startpage to the stack
        self.start_page = StartPage(self)
        self.central_widget.addWidget(self.start_page)
    
    def loadStyleSheet(self):
        with open("style.qss", "r") as file:
            self.setStyleSheet(file.read())

  
    def show_page(self, page_class):
        if hasattr(self, page_class.__name__.lower()):
            page = getattr(self, page_class.__name__.lower())
        else:
            page = page_class(self)
            setattr(self, page_class.__name__.lower(), page)
            self.central_widget.addWidget(page)
        print(page_class.__name__)
        print(page)
        self.central_widget.setCurrentWidget(page)
    
    def show_start_page(self):
        self.show_page(StartPage)
    
    def show_create_wallet_page(self):
        self.show_page(AddWalletPage)
    
    def show_machine_options_page(self):
        self.show_page(MachineOptionPage)
    
    def show_dashboard_page(self):
        if self.wallet_name:
            self.show_page(DashboardPage)
        else:
            self.prompt_for_wallet_name()
       
    def show_wallet_page(self):
        if self.wallet_name:
            self.show_page(WalletDetailsTable)

    
    def addDetail(self, temp_layout, widget, fontsize, bold = False):
        fontWeight = QFont.Bold if bold else QFont.Normal 
        widget.setFont(QFont("Georgia", fontsize, fontWeight))
        temp_layout.addWidget(widget)

    # def prompt_for_wallet_name(self):
    #     wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Please confirm wallet name:")
    #     while True:
    #         if not ok and wallet_name:
    #             try:
    #                 self.wallet_path = search_directory(os.path.join(os.path.expanduser('~'), '.bittesor/wallets'), self.wallet_name)
    #                 self.wallet_name = wallet_name
    #                 self.show_page(DashboardPage)
    #             except FileNotFoundError as e:
    #                 QInputDialog.getText(self, "Wallet not found", str(e) + "\nEnter a valid wallet name:")
    #                 self.prompt_for_wallet_name()
    #         elif not ok:
    #             pass

    def print_attributes(self):
        for attr_name in dir(self):
            # Optionally, filter out built-in attributes and methods
            if not attr_name.startswith('__'):
                attr_value = getattr(self, attr_name)
                print(f"{attr_name}: {attr_value}")
 
       
    def prompt_for_wallet_name(self):
        self.wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Please confirm wallet name:")
        while True:
            if not ok:
                if hasattr(self, 'dashboardpage'):
                    del self.dashboardpage
                break  # Break out of the loop if the user cancels
                pass
            try:
                self.wallet_path = search_directory(os.path.join(os.path.expanduser('~'), '.bittesor/wallets'), self.wallet_name)
                if self.wallet_path:
                    self.show_page(DashboardPage)
                    break  # Break out of the loop if the directory is found
            except FileNotFoundError as e:
                new_wallet_name, ok = QInputDialog.getText(self, "Wallet not found", str(e) + "\nEnter a valid wallet name:")
                if not ok:
                    # print("User canceled")
                    break  # Break out of the loop if the user cancels
                self.wallet_name = new_wallet_name  # Update the wallet name for the next iteration   
       
       
    #     else:
    #         self.wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Please confirm wallet name:")
    #         while True:
    #             if not ok:
    #                 break  # Break out of the loop if the user cancels
    #             try:
    #                 self.wallet_path = search_directory(os.path.join(os.path.expanduser('~'), '.bittesor/wallets'), self.wallet_name)
    #                 print(self.wallet_path)
    #                 if self.wallet_path:
    #                     self.dashboard_page = DashboardPage(self)
    #                     self.central_widget.addWidget(self.dashboard_page)
    #                     self.central_widget.setCurrentWidget(self.dashboard_page)
    #                     break  # Break out of the loop if the directory is found
    #             except FileNotFoundError as e:
    #                 new_directory, ok = QInputDialog.getText(self, "Wallet not found", str(e) + "\nEnter a valid wallet name:")
    #                 if not ok:
    #                     # print("User canceled")
    #                     break  # Break out of the loop if the user cancels
    #                 self.wallet_name = new_directory  # Update the wallet name for the next iteration
    


    # def show_wallet_page(self):
    #     if self.wallet_name != None:
    #         self.wallet_page = WalletDetailsTable(self)
    #         self.central_widget.addWidget(self.wallet_page)
    #         self.central_widget.setCurrentWidget(self.wallet_page)
    #     else:
    #         self.wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Plese confirm wallet name:")
    #         if ok and self.wallet_name:
    #             self.wallet_page = WalletDetailsTable(self)
    #             self.central_widget.addWidget(self.wallet_page)
    #             self.central_widget.setCurrentWidget(self.wallet_page)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyleSheet("QMainWindow::separator { background: rgba(0, 0, 0, 0.3); width: 1px; }")
    window = MiningWizard()
    window.show()
    sys.exit(app.exec_())


