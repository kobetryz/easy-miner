# Easy miner app
# Kofi Osei - Bonsu 
# 30/12/2023
import json
import os
import sys
from multiprocessing import freeze_support
import hashlib
import uuid
from datetime import datetime, timedelta
import psycopg2

from PyQt5 import sip
from PyQt5.QtCore import QProcess
from bittensor import subtensor, wallet


from pages.dashboards import LocalDashboardPage, RunpodDashboardPage
from pages.runpod.runpodManager import RunpodManagerPage
from runpod_api.runpod import api
from utils import get_value_from_env, save_value_to_env, decript_keyfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget, QInputDialog, QLineEdit
from PyQt5.QtGui import QFont, QCloseEvent

from pages.minerOptions import MinerOptionsPage
from pages.startpage import StartPage
from pages.add_wallet import AddWalletPage
from pages.wallet import WalletDetailsTable
from pages.machineOptions import MachineOptionPage
from pages.runpod.runpodSetup import RunpodSetupPage
from database.connection import connect_to_database


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

    def show_runpod_setup_page(self, *args, **kwargs):
        self.show_page(RunpodSetupPage, *args, **kwargs)
    
    def show_local_dashboard_page(self, *args, **kwargs):
        self.show_page(LocalDashboardPage, *args, **kwargs)

    def show_runpod_dashboard_page(self, pod_id=None, *args, **kwargs):
        self.show_page(RunpodDashboardPage, pod_id=pod_id, *args, **kwargs)
       
    def show_wallet_page(self, *args, **kwargs):
        if self.wallet_name:
            self.show_page(WalletDetailsTable, *args, **kwargs)

    def check_runpod_api_key(self, check_env=True):
        api_key = None
        if check_env:
            api_key = get_value_from_env("RUNPOD_API_KEY")
        if not api_key:
            api_key, ok = QInputDialog.getText(self, "RunPod API Key", "Enter your RunPod API Key:")
            if not ok or not api_key:
                QMessageBox.warning(self, "API Key Required", "RunPod API Key is required to proceed.")

        api.API_KEY = api_key

        response = api.get_myself()
        if response.ok:
            save_value_to_env("RUNPOD_API_KEY", api_key)
            return
        elif response.status_code == 401:
            QMessageBox.warning(
                self, "API key auth failed", "Check if you entered the key correctly and try again."
            )
        else:
            QMessageBox.warning(
                self,
                "API key auth failed",
                f"An error occurred during the authorization process: "
                f"{response.status_code} {response.reason} {response.text} "
                f"\nPlease contact support"
            )
        self.check_runpod_api_key(check_env=False)

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
            self.wallet_path = None
            return  # User cancelled the dialog
        path_wallets = os.path.join(os.path.expanduser('~'), '.bittensor/wallets')
        self.wallet_path = os.path.join(path_wallets, self.wallet_name)
        if not os.path.exists(self.wallet_path):
            QMessageBox.information(self, "Wallet not found", "Wallet not found. Please enter a valid wallet name.")
            self.wallet_path = None
            self.prompt_for_wallet_name()  # Prompt again
        hotkey_files = [f for f in os.listdir(os.path.join(self.wallet_path, 'hotkeys'))]
        self.hotkey_file = hotkey_files[-1]
        try:
            with open(f'{self.wallet_path}/hotkeys/{self.hotkey_file}', 'r') as f:
                my_wallet = json.load(f)
        except UnicodeDecodeError:
            with open(f'{self.wallet_path}/hotkeys/{self.hotkey_file}', 'rb') as f:
                key_data = decript_keyfile(self, f.read())
                if not key_data:
                    return self.prompt_for_wallet_name()
                json_str = key_data.decode('utf-8')
                my_wallet = json.loads(json_str)

        self.hotkey = my_wallet['ss58Address']

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
            print(process)
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
    
    def get_device_fingerprint(self):
        # Get MAC address
       mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)])

       device_fingerprint = hashlib.md5(mac.encode()).hexdigest()
       return device_fingerprint


    def lock_user(self):
        QMessageBox.warning(self, "Access Denied", "Your access to the app has been denied because you have exceeded the usage limit.")
        self.terminate_processes()
        QApplication.quit()
        sys.exit(0)

    def check_user_lock(self):
        conn = connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()

                # Check if user exists
                cursor.execute("SELECT * FROM users WHERE device_id = %s", (self.get_device_fingerprint(),))
                user_exists = cursor.fetchone()

                if not user_exists:
                    # Register new user
                    cursor.execute("INSERT INTO users (device_id, first_usage) VALUES (%s, %s)", (self.get_device_fingerprint(), datetime.now()))
                    conn.commit()

                else:
                    # Check usage duration
                    cursor.execute("SELECT first_usage FROM users WHERE device_id = %s", (self.get_device_fingerprint(),))
                    first_usage = cursor.fetchone()[0]
                   
                    if datetime.now() - datetime.fromisoformat(first_usage.isoformat()) >= timedelta(days=30):
                        # Lock user
                        self.lock_user()
                    else :
                        print("User not locked")
                cursor.close()

            except (Exception, psycopg2.Error) as error:
                print("Error:", error)



if __name__ == "__main__":
    freeze_support()
    app = QApplication(sys.argv)
    window = MiningWizard()
    window.show()
    os._exit(app.exec_())
