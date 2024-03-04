import time

import requests
import websocket
from PyQt5.QtCore import pyqtSignal, QThread, QDateTime
from PyQt5.QtWidgets import QMessageBox

from runpod_api.runpod import api
from .base import DashboardPageBase


class WebSocketThread(QThread):
    data_received = pyqtSignal(str)

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
        self.parent.mine_button.setEnabled(True)

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


class RunpodDashboardPage(DashboardPageBase):
    def __init__(self, parent, pod_id=None):
        self.pod_dict = {}
        self.pod_id = pod_id
        self.server_url = None
        self.dht_announce_ip = None
        self.axon_port = None
        self.dht_port = None
        super().__init__(parent)

        # Websocket
        self.websocket_thread = WebSocketThread(self)
        self.websocket_thread.data_received.connect(self.handle_received_data)  # noqa
        self.websocket_thread.start()

    def setupUI(self):
        super().setupUI()
        self.set_pod_config()

    def handle_received_data(self, data):
        self.output_area.insertPlainText(data)

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
        print("finished setting pod config")

    def start_mining(self):
        response = requests.post(f"{self.server_url}/mine", json={
            "miner_type": "validator",
            "network": "test",
            "net_id": self.parent.net_id,
            "axon_port": self.axon_port,
            "dht_port": self.dht_port,
            "dht_announce_ip": self.dht_announce_ip,
            "wallet_data": {
                "cold_key_name": self.parent.wallet_name,
                "cold_key_mnemonic": self.parent.mnemonic_hotkey,
                "hot_key_mnemonic": self.parent.mnemonic_coldkey,
            },
            "wandb_key": self.parent.wandb_api_key,
        })
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
        return self.mining_process

    def update_timer(self):
        # This function is called every second to update the timer display
        if self.is_running():
            current_time = QDateTime.currentDateTime()
            self.elapsed_time = self.start_time.secsTo(current_time)
            hours = self.elapsed_time // 3600
            minutes = (self.elapsed_time % 3600) // 60
            seconds = self.elapsed_time % 60
            self.timer_label.setText(f"{hours}h: {minutes}m: {seconds}s")
            # print(self.timer_label.text())
