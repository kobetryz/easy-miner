import os
import re
import json
import requests
import pandas as pd


import bittensor as bt
import matplotlib.dates as mdates
from datetime import datetime,time
import datetime as dt

from PyQt5.QtWidgets import QPushButton, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QPushButton, QGroupBox,QMessageBox
from PyQt5.QtGui import QFont,QDesktopServices
from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment, QTimer, QDateTime, QUrl
import pyqtgraph as pg



from config import configure_logger, get_earnings_by_date_range, get_total_mining
# from utils import MiningManager


class SelectDashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.data_logger = configure_logger(f"./{self.parent.wallet_name}/full_user_data.log")
       
       # Connect to taostats
        url = "https://taostats.io/data.json"
        response = requests.get(url)
        taostats = json.loads(response.content)
        price = float(taostats[0]['price'])  
    

        with open(f'{os.path.join(self.parent.wallet_path)}/coldkey', 'r') as f:
            address_json = json.load(f)
        self.coldkey = address_json['ss58Address']

        if self.coldkey in self.parent.subnet.coldkeys:
            uid = self.parent.subnet.coldkeys.index(self.coldkey)
            self.wallet_bal_tao = self.parent.subnet.stake.tolist()[uid]
            self.registered = True
        else:
            wallet_bal_tao = str(self.parent.subtensor.get_balance(address = self.coldkey))[1:]
            self.wallet_bal_tao = float(wallet_bal_tao)
            self.registered = False
        self.data_logger.info(f' Balance - Start: {self.wallet_bal_tao}')
        self.data_logger.info('Activity: Log in')
        self.data_logger.info(f' Activity: Mining Time - 0') 
        reward_data = get_earnings_by_date_range(f"./{self.parent.wallet_name}/full_user_data.log")
        activity_data = get_total_mining(f"./{self.parent.wallet_name}/full_user_data.log")
        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-family: Georgia;
            }
        """)
    
        layout = QVBoxLayout()
        # Header Group with links
        header_group = QGroupBox("BitCurrent")
        header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QHBoxLayout(header_group)


        # header_layout.addWidget(QLabel("BITCURRENT"))
        home_button = QPushButton("Home")
        home_button.clicked.connect(self.parent.show_start_page)
        header_layout.addWidget(home_button)

        wallet_button = QPushButton("Wallet")
        wallet_button.clicked.connect(self.parent.show_wallet_page)
        header_layout.addWidget(wallet_button)


        self.mine_button = QPushButton("Start Mining")
        self.mine_button.clicked.connect(self.toggle_mining)
        header_layout.addWidget(self.mine_button)

        log_button = QPushButton("Log Out")
        log_button.clicked.connect(self.logout)
        header_layout.addWidget(log_button)

        layout.addWidget(header_group)
            
        # Summary Stats
        summary_group = QGroupBox(f'Welcome {self.parent.wallet_name}!!')
        summary_group.setFont(QFont("Georgia", 26, QFont.Bold, italic=True))
        summary_group.setAlignment(Qt.AlignLeft) 
        summary_layout = QHBoxLayout(summary_group)

  
        wallet_bal_dol = round(self.wallet_bal_tao * price, 2)
        earnings_group = QGroupBox()
        earnings_layout = QVBoxLayout(earnings_group)
        earnings_layout.addWidget(QLabel("Wallet Balance",font=QFont('Georgia', 10)))
        earnings_layout.addWidget(QLabel(f"${wallet_bal_dol}", font= QFont('Georgia', 20, QFont.Bold)))
        earnings_layout.addWidget(QLabel(f"TAO {self.wallet_bal_tao}", font= QFont('Georgia', 10)))
        
        summary_layout.addWidget(earnings_group)
       

        # Mining infomation
        mining_info_group = QGroupBox()
        mining_info_layout = QVBoxLayout(mining_info_group)
        mining_info_layout.addWidget(QLabel("Average Mining Time", font=QFont('Georgia', 10)))
        mining_info_layout.addWidget(QLabel("23.5HRS", font= QFont('Georgia', 20, QFont.Bold)))
        mining_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        
        summary_layout.addWidget(mining_info_group)
        # layout.addWidget(summary_group)

        # CPU USAGE
        cpu_info_group = QGroupBox()
        cpu_info_layout = QVBoxLayout(cpu_info_group)
        cpu_info_layout.addWidget(QLabel("CPU Usage", font=QFont('Georgia', 10)))
        cpu_info_layout.addWidget(QLabel("12.3%", font= QFont('Georgia', 20, QFont.Bold)))
        cpu_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        
        summary_layout.addWidget(cpu_info_group)


        # GPU USAGE
        gpu_info_group = QGroupBox()
        gpu_info_layout = QVBoxLayout(gpu_info_group)
        gpu_info_layout.addWidget(QLabel("GPU Usage", font=QFont('Georgia', 10)))
        gpu_info_layout.addWidget(QLabel("54.3%", font= QFont('Georgia', 20, QFont.Bold)))
        gpu_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        summary_layout.addWidget(gpu_info_group)
        

        # Timer
        self.timer = QTimer(self) # Create timer 
        timer_group = QGroupBox()
        timer_info_layout = QVBoxLayout(timer_group)
        timer_info_layout.addWidget(QLabel("Live Mining Time", font=QFont('Georgia', 10)))
        self.timer_label = QLabel("0h: 0m: 0s", self)
        self.timer_label.setFont(QFont("Georgia", 20, QFont.Bold)) 
        timer_info_layout.addWidget(self.timer_label)
        timer_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        
        # # Define Mining/Live time
        self.mining_process = None #just removed
        self.start_time = QDateTime.currentDateTime()
        self.timer.timeout.connect(self.update_timer)
        summary_layout.addWidget(timer_group)
        layout.addWidget(summary_group)

        # User Activity Chart
        activity_plot = pg.PlotWidget()
        activity_plot.setBackground((50, 50, 50))
        activity_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        activity_plot.showGrid(x=True, y=True, alpha=0.5)
        activity_plot.plot([0, 1, 2, 3,5], [0, 5, 3, 8, 2], pen='r', symbol='o', symbolPen='r', symbolBrush=(255, 0, 0), symbolSize=10)
        num_dates = mdates.date2num(activity_data['date'].tolist()).tolist()
        activity_plot.plot(num_dates, activity_data['time(s)'].tolist(), pen='g', symbol='o', symbolPen='g', symbolBrush=(50, 205, 50), symbolSize=10)
        activity_plot.getAxis('bottom').setTicks([[(num_dates[i], activity_data['date'].tolist()[i].strftime('%Y-%m-%d')) for i in range(len(activity_data['date'].tolist()))]])


        # Reward History Chart
        reward_plot = pg.PlotWidget()
        reward_plot.setBackground((50, 50, 50))
        reward_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        reward_plot.showGrid(x=True, y=True, alpha=0.5)
        num_dates = mdates.date2num(reward_data['date'].tolist()).tolist()
        reward_plot.plot(num_dates, reward_data['balance'].tolist(), pen='g', symbol='o', symbolPen='g', symbolBrush=(50, 205, 50), symbolSize=10)
        reward_plot.getAxis('bottom').setTicks([[(num_dates[i], reward_data['date'].tolist()[i].strftime('%Y-%m-%d')) for i in range(len(reward_data['date'].tolist()))]])


        # Charts Section
        charts_group = QGroupBox("Charts")
        charts_group.setStyleSheet("QGroupBox { font-size: 18px; color: #ffffff; border: 2px solid #3498db; border-radius: 5px; margin-top: 10px;}")
        charts_layout = QVBoxLayout(charts_group)
        charts_layout.addWidget(QLabel("Cumulative Earnings", font=QFont('Georgia', 14, QFont.Bold)))
        charts_layout.addWidget(reward_plot)
        charts_layout.addWidget(QLabel("Daily Mining Time", font=QFont('Georgia', 14, QFont.Bold)))
        charts_layout.addWidget(activity_plot)

        layout.addWidget(charts_group)

        self.setLayout(layout)
     
    # **********
    # Methods
    # ********** 
    def toggle_mining(self):
        if self.mining_process is None or self.mining_process.state() == QProcess.NotRunning:
            self.start_mining()
        else:
            self.stop_mining()

    def start_mining(self):
        while not self.registered:
            response = self.handle_registration()
            if response == None:
                break
        if self.registered:
            self.run_mining_script()

    def handle_registration(self):
        self.registration_cost = self.parent.subtensor.burn(netuid=25)
        warning_msg = f"You are not registered to mine on Bitcurrent!\nRegistration cost for Bitcurrent is {self.registration_cost}\n Do you want to register?\nNote this amount will be deducted from your wallet."
        reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            response = self.register_on_subnet()
            if response == QMessageBox.Ok:
                self.registered = True
            else:
                self.registered = False
                return None


    def register_on_subnet(self):
        self.wallet = bt.wallet(name=self.parent.wallet_name, path=os.path.dirname(self.parent.wallet_path))
        wallet_bal = self.parent.subtensor.get_balance(address=self.coldkey)
        # check wallet balance
        if wallet_bal < self.registration_cost:
            warning_msg = f"You don't have sufficient funds in your account\nWould you like to add funds to you account?"
            reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl("https://bittensor.com/wallet"))
                return None
            else:
                return None
        else:
            success = self.parent.subtensor.burned_register(wallet=self.wallet, netuid=25)
            if success:
                info_msg = f"Congratulations!\nRegistration Successful!!\nYou are ready to mine"
                final_reply = QMessageBox.information(self, "Information", info_msg, QMessageBox.Ok)
                return final_reply

    def run_mining_script(self):
        script_path = os.path.join(os.getcwd(), 'gpu_cpu.py') # Replace with the actual path
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
        self.mining_process.start("python", [script_path])
        self.mining_process.finished.connect(self.stop_mining)
        self.mine_button.setText("Stop Mining")


    def stop_mining(self):
        if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
            self.mining_process.terminate()
            self.timer.stop()
            self.data_logger.info(f' Activity: Mining Time - {self.elapsed_time}') 
            self.mining_process.waitForFinished()
            self.mining_process = None
            self.mine_button.setText("Start Mining")


    def handle_output(self):
        # Handle output from the mining script if needed
        self.timer.stop()
        output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
        self.data_logger.info(f' Balance - Stop: {self.wallet_bal_tao}') 
        self.data_logger.info(f' Activity: Stop Mining')
        self.data_logger.info(f' Activity: Mining Time - {self.elapsed_time}') 
        self.mine_button.setText("Start Mining")

        cpu_usage_match = re.search(r'CPU Usage: ([\d.]+)%', output)
        # time_taken_cpu_match = re.search(r'Time taken on CPU: ([\d.]+) seconds', output)
        if cpu_usage_match: # and time_taken_cpu_match:
            cpu_usage = float(cpu_usage_match.group(1))
            self.data_logger.info(f' Activity - CPU Usage%: {cpu_usage}')
            # time_taken_cpu = float(time_taken_cpu_match.group(1))     
        print(output)

    def update_timer(self):
        # This function is called every second to update the timer display
        if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
            current_time = QDateTime.currentDateTime()
            self.elapsed_time = self.start_time.secsTo(current_time)
            hours = self.elapsed_time // 3600
            minutes = (self.elapsed_time % 3600) // 60
            seconds = self.elapsed_time % 60
            self.timer_label.setText(f"{hours}h: {minutes}m: {seconds}s") 
            # print(self.timer_label.text())
 
    def logout(self):
        warning_msg = f"Are you sure you want to log out?"
        reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent.wallet_name = None
            self.parent.show_start_page()

 