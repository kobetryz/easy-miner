import os
from functools import partial

from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QPushButton, \
    QMessageBox, QAbstractItemView

from config import MinerType, NetworkType
from runpod_api.runpod import api


class PodsTable(QTableWidget):
    def __init__(self):
        self.header_labels = ["pod name", "pod id", "pod status", "memory", "volume", "wallet name", "miner type"]
        data = self.get_data()
        super().__init__(len(data["pod id"]), len(self.header_labels))
        self.setHorizontalHeaderLabels(self.header_labels)
        self.set_data(data)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def get_data(self):
        self.data = {key: [] for key in self.header_labels}
        pods = api.get_pods().json().get("data", {}).get("myself", {}).get("pods", [])
        for pod in pods:
            self.data["pod name"].append(pod["name"])
            self.data["pod id"].append(pod["id"])
            self.data["pod status"].append(pod["desiredStatus"])
            self.data["memory"].append(pod["memoryInGb"])
            self.data["volume"].append(pod["volumeInGb"])
            if pod["desiredStatus"] == "RUNNING" and (miner_options := api.get_miner_options(pod["id"])):
                self.data["wallet name"].append(miner_options["wallet_data"]["cold_key_name"])
                self.data["miner type"].append(miner_options["miner_type"])

        return self.data

    def set_data(self, data):
        for n, key in enumerate(data.keys()):
            for m, item in enumerate(data[key]):
                newitem = QTableWidgetItem(str(item))
                self.setItem(m, n, newitem)

    def get_checked(self, key):
        return self.data[key][current_row] if (current_row := self.currentRow()) != -1 else None

    def get_checked_pod_id(self):
        return self.get_checked("pod id")

    def get_checked_status(self):
        return self.get_checked("pod status")


class RunpodManagerPage(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()

        self.createHeader()

        self.table = PodsTable()
        self.layout.addWidget(self.table)

        self.createFooter()

        self.setLayout(self.layout)

    def createHeader(self):
        self.header_layout = QHBoxLayout()

        add_button = QPushButton("Add new pod")
        remove_button = QPushButton("Remove pod")
        dashboard_button = QPushButton("Go to dashboard")
        refresh_button = QPushButton("Refresh table")

        add_button.clicked.connect(
            partial(
                self.parent.show_miner_options_page,  # noqa
                instead_machine_options=self.parent.show_runpod_page,  # noqa
                page_to_delete=self  # noqa
            )
        )
        remove_button.clicked.connect(self.on_remove_button_clicked)  # noqa
        dashboard_button.clicked.connect(self.on_dashboard_button_clicked)  # noqa
        refresh_button.clicked.connect(self.refresh_table)  # noqa

        self.header_layout.addWidget(add_button)
        self.header_layout.addWidget(remove_button)
        self.header_layout.addWidget(dashboard_button)
        self.header_layout.addWidget(refresh_button)

        self.layout.addLayout(self.header_layout)

    def createFooter(self):
        f_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(partial(self.parent.show_start_page, page_to_delete=self))  # noqa
        self.parent.addDetail(f_layout, previous_button, 12)  # noqa
        f_layout.addStretch()
        self.layout.addLayout(f_layout)

    def refresh_table(self):
        self.parent.show_runpod_manager_page(page_to_delete=self)

    def on_dashboard_button_clicked(self):
        pod_id = self.table.get_checked_pod_id()
        pod_status = self.table.get_checked_status()
        if not pod_id:
            QMessageBox.warning(self, "Error", "Error: No cells are selected")
            return
        if pod_status != "RUNNING":
            QMessageBox.warning(self, "Error", "Error: Pod is not running")
            return
        miner_options = api.get_miner_options(pod_id)
        if not miner_options:
            QMessageBox.warning(self, "Error", "Miner options not available, you may try to recreate pod")
            return

        self.set_miner_options(miner_options)

        self.parent.show_runpod_dashboard_page(pod_id=pod_id, page_to_delete=self)  # noqa

    def on_remove_button_clicked(self):
        pod_id = self.table.get_checked_pod_id()
        if not pod_id:
            QMessageBox.warning(self, "Error", "Error: No cells are selected")
        response = api.terminate_pod(pod_id)
        errors = response.json().get("errors")
        if not errors:
            QMessageBox.information(self, "Success", "Pod terminated successfully")
        else:
            msg = "Error occurred while removing, maybe pod not exist:\n"
            msg += "\n".join([error["message"] for error in errors])
            QMessageBox.warning(self, "Error", msg)

    def set_miner_options(self, miner_options: dict):
        self.parent.miner_type = MinerType(miner_options["miner_type"])
        self.parent.network = NetworkType(miner_options["network"])
        self.parent.net_id = miner_options["net_id"]
        self.parent.wallet_name = miner_options["wallet_data"]["cold_key_name"]
        self.parent.mnemonic_coldkey = miner_options["wallet_data"]["cold_key_mnemonic"]
        self.parent.mnemonic_hotkey = miner_options["wallet_data"]["hot_key_mnemonic"]
        self.parent.wandb_api_key = miner_options["wandb_key"]

        path_wallets = os.path.join(os.path.expanduser('~'), '.bittensor/wallets')
        self.parent.wallet_path = os.path.join(path_wallets, self.parent.wallet_name)
        if not os.path.exists(self.parent.wallet_path):
            QMessageBox.information(self, "Wallet not found", "Wallet from runpod not found on your computer")
            self.parent.wallet_path = None
