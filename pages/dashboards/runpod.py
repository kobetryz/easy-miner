import time
from functools import partial

import requests
import websocket
from PyQt5.QtCore import pyqtSignal, QThread, QDateTime, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QGroupBox, QHBoxLayout, QPushButton

from runpod_api.runpod import api
from .base import DashboardPageBase


class WebSocketThread(QThread):
    data_received = pyqtSignal(str)
    connection_open = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def get_websocket_address(self):
        return f"wss://{self.parent.pod_id}-8000.proxy.runpod.net/ws"

    def connect_to_websocket(self):
        self.ws = websocket.WebSocketApp(
            self.get_websocket_address(),
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()

    def on_open(self, ws):
        self.connection_open.emit()  # noqa

    def on_message(self, ws, messages):
        self.data_received.emit(messages)  # noqa

    def on_error(self, ws, error):
        self.parent.mine_button.setEnabled(False)
        print(f"Error in websocket with {error=}. Reconnecting...")
        time.sleep(5)
        self.connect_to_websocket()

    def on_close(self, ws, close_status_code, close_msg):
        self.parent.mine_button.setEnabled(False)
        print(f"Websocket clossed with {close_status_code=} {close_msg=}. Reconnecting...")
        time.sleep(5)
        self.connect_to_websocket()

    def run(self):
        self.connect_to_websocket()


class MetricsThread(QThread):
    cpu_util = pyqtSignal(float)
    gpu_util = pyqtSignal(float)

    update_signal = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.update_signal.connect(self.update_metrics)

    def update_metrics(self):
        response = api.get_pod(self.parent.pod_id)
        resp_json = response.json()
        runtime_dict = resp_json["data"]["pod"]["runtime"]
        self.gpu_util.emit(runtime_dict["gpus"][0]["gpuUtilPercent"])
        self.cpu_util.emit(runtime_dict["container"]["cpuPercent"])

    def run(self):
        self.update_metrics()


class RunpodDashboardPage(DashboardPageBase):
    def __init__(self, parent, pod_id=None, *args, **kwargs):
        self.pod_dict = {}
        self.pod_id = pod_id
        self.server_url = None
        self.dht_announce_ip = None
        self.axon_port = None
        self.dht_port = None
        self.miner_options = {}
        super().__init__(parent)

        # Websocket
        self.websocket_thread = WebSocketThread(self)
        self.websocket_thread.data_received.connect(self.output_area.insertPlainText)  # noqa
        self.websocket_thread.connection_open.connect(self.handle_websocket_open)  # noqa
        self.websocket_thread.start()

        self.metrics_thread = None

    def setupUI(self):
        super().setupUI()
        self.set_pod_config()

    def createHeader(self):
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold))
        header_layout = QHBoxLayout(header_group)

        home_button = QPushButton("Home")
        self.parent.addDetail(header_layout, home_button, 14)
        home_button.clicked.connect(self.redirect_to_home)

        self.wallet_button = QPushButton("Wallet")
        self.parent.addDetail(header_layout, self.wallet_button, 14)
        self.wallet_button.clicked.connect(
            partial(self.parent.show_wallet_page, show_dashboard=self.parent.show_runpod_dashboard_page)
        )

        self.mine_button = QPushButton("Start Mining")
        self.parent.addDetail(header_layout, self.mine_button, 14)
        self.mine_button.clicked.connect(self.toggle_mining)

        stop_pod_button = QPushButton("Terminate Pod")
        self.parent.addDetail(header_layout, stop_pod_button, 14)
        stop_pod_button.clicked.connect(self.terminate_pod)

        log_button = QPushButton("Log Out")
        self.parent.addDetail(header_layout, log_button, 14)
        log_button.clicked.connect(self.logout)

        self.layout.addWidget(header_group)

    def terminate_pod(self):
        self.mine_button.setEnabled(False)
        self.mining_process = False
        if self.charts_group.isVisible():
            self.toggle_view()
        self.log("Terminating pod...")
        response = api.terminate_pod(self.pod_id)
        if response.status_code != 200:
            QMessageBox.warning(self, "Error", f"{response.text}\nTry again", QMessageBox.Ok)
            return
        self.pod_id = None
        self.cleanup_threads()
        self.log("Pod successfully terminated!")
        self.log("You will be redirected to the home page in 10 seconds")

        QTimer.singleShot(10000, self.redirect_to_home)

    def cleanup_threads(self):
        if self.websocket_thread:
            self.websocket_thread.terminate()
            self.websocket_thread.wait()
            self.websocket_thread = None
        if self.metrics_thread:
            self.metrics_thread.terminate()
            self.metrics_thread.wait()
            self.metrics_thread = None

    def redirect_to_home(self):
        self.parent.show_start_page(page_to_delete=self)

    def handle_received_data(self, data):
        self.log(data)

    def set_pod_config(self):
        while not self.pod_dict.get("runtime"):
            time.sleep(5)
            response = api.get_pod(self.pod_id)
            self.pod_dict = response.json()["data"]["pod"]
        for port in self.pod_dict["runtime"]["ports"]:
            if port["type"] == "tcp":
                if not self.dht_announce_ip:
                    self.dht_announce_ip = port["ip"]
                if not self.dht_port:
                    self.dht_port = port["publicPort"]
                elif not self.axon_port:
                    self.axon_port = port["publicPort"]
                else:
                    break
        self.server_url = f"https://{self.pod_id}-8000.proxy.runpod.net"
        self.miner_options = {
            "miner_type": self.parent.miner_type.value,
            "network": self.parent.network.value,
            "net_id": self.parent.net_id,
            "axon_port": self.axon_port,
            "dht_port": self.dht_port,
            "dht_announce_ip": self.dht_announce_ip,
            "wallet_data": {
                "cold_key_name": self.parent.wallet_name,
                "cold_key_mnemonic": self.parent.mnemonic_coldkey,
                "hot_key_mnemonic": self.parent.mnemonic_hotkey,
            },
            "wandb_key": self.parent.wandb_api_key,
        }

    def start_mining(self):
        self.log('Checking for registration')
        while not self.registered:
            response = self.handle_registration()
            if response == None:
                break
        if not self.registered:
            return
        self.log('You are registered and ready to mine')
        response = requests.post(f"{self.server_url}/mine", json=self.miner_options)
        if response.status_code != 200:
            QMessageBox.warning(self, "Error", f"{response.text}\nTry again", QMessageBox.Ok)
            return

        self.start_time = QDateTime.currentDateTime()
        self.timer.start(1000)  # Update timer every second
        self.timer.timeout.connect(self.update_timer)

        if self.charts_group.isVisible():
            self.toggle_view()
        self.mine_button.setText("Stop Mining")
        self.mining_process = True

    def stop_mining(self):
        response = requests.post(f"{self.server_url}/stop-mine")
        if response.status_code != 200:
            QMessageBox.warning(self, "Error", f"{response.text}\nTry again", QMessageBox.Ok)
            return
        self.mine_button.setText("Start Mining")
        self.mining_process = False

    def is_running(self):
        try:
            return requests.get(f"{self.server_url}/miner-is-running").json()
        except:
            pass

    def update_timer(self):
        # This function is called every second to update the timer display
        if self.is_running():
            current_time = QDateTime.currentDateTime()
            self.elapsed_time = self.start_time.secsTo(current_time)
            hours = self.elapsed_time // 3600
            minutes = (self.elapsed_time % 3600) // 60
            seconds = self.elapsed_time % 60
            self.timer_label.setText(f"{hours}h: {minutes}m: {seconds}s")
            self.update_metrics()
            self.mine_button.setText("Stop Mining")
        else:
            self.mine_button.setText("Start Mining")

    def update_metrics(self):
        if self.metrics_thread is None or not self.metrics_thread.isRunning():
            self.metrics_thread = MetricsThread(self)
            self.metrics_thread.cpu_util.connect(self.update_cpu_usage)
            self.metrics_thread.gpu_util.connect(self.update_gpu_usage)
            self.metrics_thread.start()

    def update_cpu_usage(self, cpu_util):
        self.cpu_usage_label.setText(f"{cpu_util}%")

    def update_gpu_usage(self, gpu_util):
        self.gpu_usage_label.setText(f"{gpu_util}%")

    def handle_websocket_open(self):
        self.toggle_view()
        requests.post(f"{self.server_url}/miner-options", json=self.miner_options)
        if self.is_running():
            self.mine_button.setText("Stop Mining")
        self.mine_button.setEnabled(True)
