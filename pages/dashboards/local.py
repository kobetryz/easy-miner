import os
import re

from PyQt5.QtCore import QProcess, QProcessEnvironment, QDateTime, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox
from black import datetime

from config import IP_ADDRESS, INITIAL_PEERS
from .base import DashboardPageBase
import bittensor as bt


class LocalDashboardPage(DashboardPageBase):
    def __init__(self, parent):
        super().__init__(parent)

    def handle_registration(self):
        self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - You are not registered')
        self.registration_cost = self.parent.subtensor.recycle(netuid=self.parent.net_id)
        warning_msg = f"You are not registered to mine on Bitcurrent!\nRegistration cost for Bitcurrent is {self.registration_cost}\n Do you want to register?\nNote this amount will be deducted from your wallet."
        reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            response = self.register_on_subnet()
            if response == QMessageBox.Ok:
                self.registered = True
            else:
                self.registered = False

    def start_mining(self):
        self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Checking for registration')
        while not self.registered:
            response = self.handle_registration()
            if response == None:
                break
        if self.registered:
            self.output_area.append(
                f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - You are registered and ready to mine')
            self.update_miner()

    def stop_mining(self):
        if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
            self.mining_process.terminate()
            self.timer.stop()
            self.data_logger.info(f' Activity: Mining Time - {self.elapsed_time}')
            self.mining_process.waitForFinished()
            self.mining_process = None
            self.mine_button.setText("Start Mining")
            self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Stop Mining')

    def is_running(self):
        return self.mining_process is not None and self.mining_process.state() == QProcess.Running

    def update_miner(self):
        if self.charts_group.isVisible():
            self.toggle_view()

        self.update_script_process = QProcess(self)
        self.update_script_process.setProcessChannelMode(QProcess.MergedChannels)
        self.update_script_process.readyReadStandardOutput.connect(self.handle_update_script_output)
        self.update_script_process.start('sh', ['update_miner-25.sh'])
        self.update_script_process.finished.connect(self.run_mining_script)

    def handle_update_script_output(self):
        output = self.update_script_process.readAllStandardOutput().data().decode('utf-8')
        self.output_area.append(output)

    def run_mining_script(self):
        self.wandb_login()
        self.mining_process = QProcess(self)
        self.mining_process.setProcessChannelMode(QProcess.MergedChannels)
        self.mining_process.readyReadStandardOutput.connect(self.handle_output)
        self.data_logger.info('Activity: Start Mining')

        # Set environment variables if needed
        env = QProcessEnvironment.systemEnvironment()
        self.mining_process.setProcessEnvironment(env)

        self.start_time = QDateTime.currentDateTime()
        self.timer.start(1000)  # Update timer every second
        self.timer.timeout.connect(self.update_timer)

        # Log balance and start of mining
        self.data_logger.info(f' Balance - Start: {self.wallet_bal_tao}')
        command = "python"
        args = [
            "-u",
            f"DistributedTraining/neurons/{self.parent.miner_type.value}.py",
            "--netuid", f"{self.parent.net_id}",
            "--subtensor.network", "test",
            "--wallet.name", f"{self.parent.wallet_name}",
            "--wallet.hotkey", f"{self.parent.hotkey}",
            "--logging.debug",
            "--axon.port", "8000",
            "--dht.port", "8001",
            "--dht.announce_ip", f"{IP_ADDRESS}",
            "--neuron.initial_peers", f"{INITIAL_PEERS}"
        ]

        self.mining_process.start(command, args)
        if self.charts_group.isVisible():
            self.toggle_view()
        self.mining_process.finished.connect(self.stop_mining)
        self.mine_button.setText("Stop Mining")

    def register_on_subnet(self):
        self.wallet = bt.wallet(name=self.parent.wallet_name, path=os.path.dirname(self.parent.wallet_path))
        wallet_bal = self.parent.subtensor.get_balance(address=self.parent.hotkey)
        # check wallet balance
        if wallet_bal < self.registration_cost:
            self.output_area.append(
                f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - You don\'t have sufficient funds')
            warning_msg = f"You don't have sufficient funds in your account\nWould you like to add funds to you account?"
            reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl("https://bittensor.com/wallet"))
                return None
            else:
                return None
        else:
            self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Registration in Progress!!')
            success = self.parent.subtensor.burned_register(wallet=self.wallet, netuid=25)
            if success:
                self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Registration complete')
                info_msg = f"Congratulations!\nRegistration Successful!!\nYou are ready to mine"
                final_reply = QMessageBox.information(self, "Information", info_msg, QMessageBox.Ok)
                return final_reply

    def handle_output(self):
        self.parent.output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
        self.output_area.append(
            self.parent.output.replace('|', ' ').replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                    '&gt;').strip())
        # Check for common prompt indicators
        if self.parent.output.strip().endswith(":") or "?" in self.parent.output:
            self.input_line.show()
            self.input_line.setFocus()
            self.input_button.show()
            self.output_area.setReadOnly(False)
        else:
            # Optionally hide the input button if no input is required
            self.input_line.hide()
            self.input_button.hide()
            self.output_area.setReadOnly(True)
        self.data_logger.info(f' Balance - Stop: {self.wallet_bal_tao}')
        self.data_logger.info(f' Activity: Stop Mining')
        self.data_logger.info(f' Activity: Mining Time - {self.elapsed_time}')

        cpu_usage_match = re.search(r'CPU Usage: ([\d.]+)%', self.parent.output)
        # time_taken_cpu_match = re.search(r'Time taken on CPU: ([\d.]+) seconds', output)
        if cpu_usage_match:  # and time_taken_cpu_match:
            cpu_usage = float(cpu_usage_match.group(1))
            self.data_logger.info(f' Activity - CPU Usage%: {cpu_usage}')
            # time_taken_cpu = float(time_taken_cpu_match.group(1))
        # print(self.parent.output)
