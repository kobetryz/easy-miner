import time

import requests
import websocket
from PyQt5.QtCore import pyqtSignal, QThread, QDateTime
from PyQt5.QtWidgets import QMessageBox

from config import IP_ADDRESS
from .base import DashboardPageBase


class WebSocketThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def get_websocket_address(self):
        # TODO: Get websocket address from server
        return "ws://127.0.0.1:8001/ws"

    def connect_to_websocket(self):
        self.ws = websocket.WebSocketApp(
            self.get_websocket_address(),
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()

    def on_message(self, ws, messages):
        self.data_received.emit(messages)  # noqa

    def on_error(self, ws, error):
        print(f"Error in websocket with {error=}. Reconnecting...")
        time.sleep(5)
        self.connect_to_websocket()

    def on_close(self, ws, close_status_code, close_msg):
        print(f"Websocket clossed with {close_status_code=} {close_msg=}")

    def run(self):
        self.connect_to_websocket()


class RunpodDashboardPage(DashboardPageBase):
    def __init__(self, parent):
        super().__init__(parent)

        # Websocket
        self.websocket_thread = WebSocketThread(self)
        self.websocket_thread.data_received.connect(self.handle_received_data)  # noqa
        self.websocket_thread.start()

        # Server
        self.server_url = "http://127.0.0.1:8001"

    def handle_received_data(self, data):
        self.output_area.insertPlainText(data)

    def get_axon_port(self):
        # TODO: Get axon port from server
        return 8001

    def get_dht_port(self):
        # TODO: Get dht port from server
        return 8002

    def get_dht_announce_ip(self):
        # TODO: Get dht announce ip from server
        return IP_ADDRESS

    def start_mining(self):
        self.wandb_login()
        response = requests.post(f"{self.server_url}/mine", json={
            "miner_type": "validator",
            "network": "test",
            "net_id": self.parent.net_id,
            "axon_port": self.get_axon_port(),
            "dht_port": self.get_dht_port(),
            "dht_announce_ip": self.get_dht_announce_ip(),
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
