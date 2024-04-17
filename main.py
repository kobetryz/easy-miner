# Easy miner app
# Kofi Osei - Bonsu 
# 30/12/2023 


import os
import sys
from multiprocessing import freeze_support

from PyQt5 import sip
from PyQt5.QtCore import QProcess
from bittensor import subtensor, wallet

from pages.dashboards import LocalDashboardPage, RunpodDashboardPage
from pages.runpod.runpodManager import RunpodManagerPage
from runpod_api.runpod import api
from utils import get_value_from_env, save_value_to_env
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget, QInputDialog, QLineEdit
from PyQt5.QtGui import QFont, QCloseEvent

from pages.minerOptions import MinerOptionsPage
from pages.startpage import StartPage
from pages.add_wallet import AddWalletPage
from pages.wallet import WalletDetailsTable
from pages.machineOptions import MachineOptionPage
from pages.runpod.runpodSetup import RunpodSetupPage


class MiningWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.initialize_pages()

        # initialise vars
        self.wallet_name = None
        self.wallet_path = None
        self.miner_type = None
        self.net = None
        self.network = None
        self.mnemonic_hotkey = None
        self.mnemonic_coldkey = None
        self.processes: list[QProcess] = []

    # methods to open pages
    def initialize_subtensor(self):
        print(f"Init subtensor..., {self.network.value}, {self.net_id}")
        self.subtensor = subtensor(network=self.network.value)
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
    
    def show_page(self, page_class, *args, **kwargs):
        if previous_page := kwargs.get("page_to_delete"):
            self.central_widget.removeWidget(previous_page)
            previous_page.setParent(None)
            sip.delete(previous_page)
        page = None
        for widget in self.central_widget.children():
            if isinstance(widget, page_class):
                page = widget
        if not page:
            page = page_class(self, *args, **kwargs)
            self.central_widget.addWidget(page)

        self.central_widget.setCurrentWidget(page)

    def show_start_page(self, *args, **kwargs):
        self.show_page(StartPage, *args, **kwargs)
    
    def show_create_wallet_page(self, *args, **kwargs):
        self.show_page(AddWalletPage, *args, **kwargs)

    def show_miner_options_page(self, *args, **kwargs):
        if not self.wallet_path:
            self.prompt_for_wallet()
        if self.wallet_path:
            self.show_page(MinerOptionsPage, *args, **kwargs)

    def show_machine_options_page(self, *args, **kwargs):
        self.show_page(MachineOptionPage, *args, **kwargs)
    
    def show_local_dashboard_page(self, *args, **kwargs):
        self.show_page(LocalDashboardPage, *args, **kwargs)

    def show_runpod_dashboard_page(self, pod_id=None, *args, **kwargs):
        self.show_page(RunpodDashboardPage, pod_id=pod_id, *args, **kwargs)
       
    def show_wallet_page(self, *args, **kwargs):
        if self.wallet_name:
            self.show_page(WalletDetailsTable, *args, **kwargs)

    def check_runpod_api_key(self):
        api_key = get_value_from_env("RUNPOD_API_KEY")
        if not api_key:
            api_key, ok = QInputDialog.getText(self, "RunPod API Key", "Enter your RunPod API Key:")
            if ok and api_key:
                save_value_to_env("RUNPOD_API_KEY", api_key)
                api.API_KEY = api_key
            else:
                QMessageBox.warning(self, "API Key Required", "RunPod API Key is required to proceed.")

    def show_runpod_page(self, *args, **kwargs):
        self.check_runpod_api_key()
        self.show_page(RunpodSetupPage, *args, **kwargs)

    def show_runpod_manager_page(self, *args, **kwargs):
        self.check_runpod_api_key()
        self.show_page(RunpodManagerPage, *args, **kwargs)

    def addDetail(self, temp_layout, widget, fontsize, bold=False, **kwargs):
        fontWeight = QFont.Bold if bold else QFont.Normal
        widget.setFont(QFont("Georgia", fontsize, fontWeight))
        temp_layout.addWidget(widget, **kwargs)

    def print_attributes(self):
        for attr_name in dir(self):
            # Optionally, filter out built-in attributes and methods
            if not attr_name.startswith('__'):
                attr_value = getattr(self, attr_name)
                print(f"{attr_name}: {attr_value}")

    def prompt_for_wallet(self):
        msgBox = QMessageBox()
        msgBox.setText("Select the method of adding a wallet:")
        msgBox.addButton("By Wallet Name", QMessageBox.AcceptRole)
        msgBox.addButton("By Mnemonic", QMessageBox.RejectRole)
        ret = msgBox.exec()

        if ret == QMessageBox.AcceptRole:
            self.prompt_for_wallet_name()
        else:
            self.prompt_for_mnemonic()

    def prompt_for_wallet_name(self):
        self.wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Please confirm wallet name:")
        if not ok:
            return  # User cancelled the dialog
        path_wallets = os.path.join(os.path.expanduser('~'), '.bittensor/wallets')
        self.wallet_path = os.path.join(path_wallets, self.wallet_name)
        if not os.path.exists(self.wallet_path):
            QMessageBox.information(self, "Wallet not found", "Wallet not found. Please enter a valid wallet name.")
            self.wallet_path = None
            self.prompt_for_wallet_name()  # Prompt again

    def prompt_for_mnemonic(self):
        cold_key, ok = QInputDialog.getText(self, "Enter ColdKey Mnemonic", "Please enter your coldkey mnemonic:", QLineEdit.Normal, "")
        if not ok or not cold_key.strip():
            return  # User cancelled or entered an empty mnemonic
        # Assuming you have a method to regenerate wallet using mnemonic
        hot_key, ok = QInputDialog.getText(self, "Enter HotKey Mnemonic", "Please enter your hot key mnemonic:",
                                           QLineEdit.Normal, "")
        if not ok or not hot_key.strip():
            return  # User cancelled or entered an empty hot key mnemonic
        wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Please confirm wallet name:")
        if not ok or not wallet_name.strip():
            return
        self.regenerate_wallet_from_mnemonic(cold_key, hot_key, wallet_name)

    # Assuming you have a separate method to handle wallet regeneration from mnemonic
    def regenerate_wallet_from_mnemonic(self, cold_key, hot_key, wallet_name):
        # Your logic to regenerate the wallet from the mnemonic
        # Check if wallet name already exists
        if os.path.exists(wallet_path := os.path.join(os.path.expanduser('~'), '.bittensor/wallets', wallet_name)):
            QMessageBox.warning(self, "Wallet Exists", "Wallet with the same name already exists.")
            self.wallet_path = wallet_path
            return
        try:
            bt_wallet = wallet(name=wallet_name, path='~/.bittensor/wallets')
            bt_wallet.regen_coldkey(mnemonic=cold_key, use_password=False)
            bt_wallet.regen_hotkey(mnemonic=hot_key, use_password=False)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")
            self.wallet_path = None
            self.prompt_for_mnemonic()
        self.mnemonic_hotkey = hot_key
        self.mnemonic_coldkey = cold_key
        self.wallet_name = wallet_name
        self.wallet_path = wallet_path

    def terminate_processes(self):
        for process in self.processes:
            if process.state() != QProcess.NotRunning:
                print(f"Terminating process {process.program()}")
                process.terminate()
                if not process.waitForFinished(3000):
                    print(f"Forcing termination of {process.program()}")
                    process.kill()
                process.waitForFinished()

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.terminate_processes()
            print("Quitting...")
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    freeze_support()
    window = MiningWizard()
    window.show()
    sys.exit(app.exec_())
