# Plug and Play miner
# Kofi Osei - Bonsu 
# 30/12/2023 


import os
import sys

from bittensor import subtensor

from pages.dashboards import LocalDashboardPage, RunpodDashboardPage
from utils import get_runpod_api_key, save_runpod_api_key
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox, QStackedWidget, QInputDialog
from PyQt5.QtGui import QFont

from pages.minerOptions import MinerOptionsPage
from pages.startpage import StartPage
from pages.add_wallet import AddWalletPage
from pages.wallet import WalletDetailsTable
from pages.machineOptions import MachineOptionPage
from pages.runpodSetup import RunpodSetupPage


class MiningWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.initialize_pages()

        #initialise vars
        self.wallet_name = None
        self.wallet_path = None
        self.miner_type = None
        self.net = None

    # methods to open pages
    def initialize_subtensor(self):
        self.subtensor = subtensor(network='test')
        self.subnet = self.subtensor.metagraph(netuid=self.net_id)

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

    def show_miner_options_page(self):
        if not self.wallet_path:
            self.prompt_for_wallet_name()
        if self.wallet_path:
            self.show_page(MinerOptionsPage)

    def show_machine_options_page(self):
        self.show_page(MachineOptionPage)
    
    def show_local_dashboard_page(self):
        # TODO: Remove this line and uncomment the next line after testing
        self.show_page(RunpodDashboardPage)
        # self.show_page(LocalDashboardPage)

    def show_runpod_dashboard_page(self):
        self.show_page(RunpodDashboardPage)
       
    def show_wallet_page(self):
        if self.wallet_name:
            self.show_page(WalletDetailsTable)

    def show_runpod_page(self):
        api_key = get_runpod_api_key()
        if not api_key:
            api_key, ok = QInputDialog.getText(self, "RunPod API Key", "Enter your RunPod API Key:")
            if ok and api_key:
                save_runpod_api_key(api_key)
                self.show_page(RunpodSetupPage)
            else:
                QMessageBox.warning(self, "API Key Required", "RunPod API Key is required to proceed.")
        else:
            self.show_page(RunpodSetupPage)

    def addDetail(self, temp_layout, widget, fontsize, bold = False):
        fontWeight = QFont.Bold if bold else QFont.Normal 
        widget.setFont(QFont("Georgia", fontsize, fontWeight))
        temp_layout.addWidget(widget)

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
                return
            path_wallets = os.path.join(os.path.expanduser('~'), '.bittensor/wallets')
            if self.wallet_name in os.listdir(path_wallets):
                self.wallet_path = os.path.join(path_wallets, self.wallet_name)
                return
            else:
                new_wallet_name, ok = QInputDialog.getText(self, "Wallet not found", "Wallet not found\nEnter a valid wallet name:")
                if not ok:
                    # print("User canceled")
                    break  # Break out of the loop if the user cancels
                self.wallet_name = new_wallet_name  # Update the wallet name for the next iteration
                self.wallet_path = os.path.join(path_wallets, self.wallet_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiningWizard()
    window.show()
    sys.exit(app.exec_())
