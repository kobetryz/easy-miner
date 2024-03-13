import os
import re
from functools import partial
from pathlib import Path

import psutil
from PyQt5.QtCore import QProcess, QProcessEnvironment, QDateTime, QUrl, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox
import GPUtil

import config
from config import IP_ADDRESS
from utils import get_minner_version
from .base import DashboardPageBase
import bittensor as bt


class CpuUsageThread(QThread):
    cpu_usage_signal = pyqtSignal(str)

    def __init__(self, process_id):
        super().__init__()
        self.process_id = process_id

    def run(self):
        proc = psutil.Process(self.process_id)
        try:
            cpu_usage = f"{proc.cpu_percent(interval=1):.1f}%"
        except psutil.NoSuchProcess:
            print("Process not found")
            cpu_usage = "0.0%"
        self.cpu_usage_signal.emit(cpu_usage)


class LocalDashboardPage(DashboardPageBase):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.cpu_usage_thread = None
        self.timer_check_update = QTimer(self)
        self.timer_check_update.setInterval(config.CHECK_UPDATES_TIME)  # 12 hours
        self.timer_check_update.timeout.connect(self.handle_repo_is_up_to_date)

    def handle_registration(self):
        self.log('You are not registered')
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
        self.log('Checking for registration')
        while not self.registered:
            response = self.handle_registration()
            if response == None:
                break
        if self.registered:
            self.log('You are registered and ready to mine')
            self.update_miner()

    def stop_mining(self):
        self.timer_check_update.stop()
        if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
            self.timer.stop()
            self.mining_process.terminate()
            self.data_logger.info(f' Activity: Mining Time - {self.elapsed_time}')
            self.mining_process.waitForFinished()
            self.mining_process = None

    def on_mining_finished(self):
        self.timer.stop()
        self.timer_check_update.stop()
        self.log('Stop Mining')
        self.mine_button.setText("Start Mining")
        self.mining_process = None

    def is_running(self):
        return self.mining_process is not None and self.mining_process.state() == QProcess.Running

    def update_miner(self):
        if self.charts_group.isVisible():
            self.toggle_view()

        self.update_script_process = QProcess(self)
        self.update_script_process.setProcessChannelMode(QProcess.MergedChannels)
        self.update_script_process.readyReadStandardOutput.connect(self.handle_update_script_output)
        path_to_scripts = Path(__file__).resolve().parent.parent.parent / "local_scripts"
        self.update_script_process.start(
            'bash', [os.path.abspath(os.path.join(path_to_scripts, f'update_miner-{self.parent.net_id}.sh'))]
        )
        self.update_script_process.finished.connect(self.run_mining_script)

    def handle_update_script_output(self):
        output = self.update_script_process.readAllStandardOutput().data().decode('utf-8')
        self.log(output)

    def run_mining_script(self):
        self.mining_process = QProcess(self)
        self.mining_process.setProcessChannelMode(QProcess.MergedChannels)
        self.mining_process.readyReadStandardOutput.connect(self.handle_output)
        self.data_logger.info('Activity: Start Mining')

        # Set environment variables if needed
        env = QProcessEnvironment.systemEnvironment()
        self.mining_process.setProcessEnvironment(env)

        self.start_time = QDateTime.currentDateTime()
        self.timer.start(1000)  # Update timer every second
        self.timer_check_update.start()
        self.timer.timeout.connect(self.update_timer)

        # Log balance and start of mining
        self.data_logger.info(f' Balance - Start: {self.wallet_bal_tao}')
        miner_directory = config.DIRECTORY_MAPPER.get(self.parent.net_id)
        command = f"{miner_directory}/venv/bin/python"
        args = [
            "-u",
            f"{miner_directory}/neurons/{self.parent.miner_type.value}.py",
            "--netuid", f"{self.parent.net_id}",
            "--subtensor.network", "test",
            "--wallet.name", f"{self.parent.wallet_name}",
            "--wallet.hotkey", f"{self.parent.hotkey}",
            "--logging.debug",
            "--axon.port", "8000",
            "--dht.port", "8001",
            "--dht.announce_ip", f"{IP_ADDRESS}"
        ]

        self.mining_process.start(command, args)
        if self.charts_group.isVisible():
            self.toggle_view()
        self.mining_process.finished.connect(self.on_mining_finished)
        self.mine_button.setText("Stop Mining")

    def register_on_subnet(self):
        self.wallet = bt.wallet(name=self.parent.wallet_name, path=os.path.dirname(self.parent.wallet_path))
        wallet_bal = self.parent.subtensor.get_balance(address=self.parent.hotkey)
        # check wallet balance
        if wallet_bal < self.registration_cost:
            self.log('You don\'t have sufficient funds')
            warning_msg = f"You don't have sufficient funds in your account\nWould you like to add funds to you account?"
            reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl("https://bittensor.com/wallet"))
                return None
            else:
                return None
        else:
            self.log('Registration in Progress!!')
            success = self.parent.subtensor.burned_register(wallet=self.wallet, netuid=self.parent.net_id)
            if success:
                self.log('Registration complete')
                info_msg = f"Congratulations!\nRegistration Successful!!\nYou are ready to mine"
                final_reply = QMessageBox.information(self, "Information", info_msg, QMessageBox.Ok)
                return final_reply

    def handle_output(self):
        self.parent.output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
        self.log(
            self.parent.output
            .replace('|', ' ')
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .strip()
        )
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

    def check_repo_is_up_to_date(self, prev_version):
        if get_minner_version(self.parent.net_id) != prev_version:
            self.stop_mining()
            self.run_mining_script()
        self.timer_check_update.start()

    def handle_repo_is_up_to_date(self):
        self.timer_check_update.stop()
        prev_version = get_minner_version(self.parent.net_id)

        self.update_script_process = QProcess(self)
        self.update_script_process.setProcessChannelMode(QProcess.MergedChannels)
        self.update_script_process.readyReadStandardOutput.connect(self.handle_update_script_output)

        path_to_scripts = Path(__file__).resolve().parent.parent.parent / "local_scripts"
        self.update_script_process.start(
            'bash', [os.path.abspath(os.path.join(path_to_scripts, f'update_miner-{self.parent.net_id}.sh'))]
        )
        self.update_script_process.finished.connect(partial(self.check_repo_is_up_to_date, prev_version))


    def update_timer(self):
        # This function is called every second to update the timer display, CPU usage and GPU usage
        if self.is_running():
            current_time = QDateTime.currentDateTime()
            self.elapsed_time = self.start_time.secsTo(current_time)
            hours = self.elapsed_time // 3600
            minutes = (self.elapsed_time % 3600) // 60
            seconds = self.elapsed_time % 60
            self.timer_label.setText(f"{hours}h: {minutes}m: {seconds}s")
            self.update_cpu_usage()
            self.gpu_usage_label.setText(self.get_gpu_usage())

    def update_cpu_usage(self):
        if self.cpu_usage_thread is None or not self.cpu_usage_thread.isRunning():
            self.cpu_usage_thread = CpuUsageThread(self.mining_process.pid())
            self.cpu_usage_thread.cpu_usage_signal.connect(self.update_cpu_usage_label)
            self.cpu_usage_thread.start()

    def update_cpu_usage_label(self, cpu_usage):
        # Update the CPU usage label with the value received from the thread
        self.cpu_usage_label.setText(cpu_usage)

    @staticmethod
    def get_gpu_usage():
        """
        Fetches the current GPU usage percentage for the first GPU found.

        Returns:
            str: GPU usage percentage as a string with one decimal place, or 'N/A' if no GPU is found.
        """
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return f"{gpu.load * 100:.1f}%"  # Convert load (0 to 1) to percentage
        else:
            return "0.0%"
