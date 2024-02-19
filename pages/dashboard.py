import os
import re
import json
import pandas as pd
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
import bittensor as bt
import matplotlib.dates as mdates
from datetime import datetime


from PyQt5.QtWidgets import QPushButton, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QPushButton, QGroupBox,QMessageBox, QTextEdit, QLineEdit
from PyQt5.QtGui import QFont,QDesktopServices, QTextOption, QTextCursor
from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment, QTimer, QDateTime, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
# import pyqtgraph as pg

from config import configure_logger_data, get_earnings_by_date_range, get_total_mining, INITIAL_PEERS, IP_ADDRESS, tao_price

class DashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # self.addDetail = self.parent.addDetail
        self.data_logger = configure_logger_data(f"{self.parent.wallet_path}/full_user_data.log")
        
        self.get_user_hotkey_and_set_reg()
        self.setupUI()
        
        self.data_logger.info(f' Balance - Start: {self.wallet_bal_tao}')
        self.data_logger.info('Activity: Log in')
        self.data_logger.info(f' Activity: Mining Time - 0') 
        reward_data = get_earnings_by_date_range(f"{self.parent.wallet_path}/full_user_data.log")
        activity_data = get_total_mining(f"{self.parent.wallet_path}/full_user_data.log")
        
        # self.setStyleSheet("""
        #     QPushButton {
        #         font-size: 14px;
        #         font-family: Georgia;
        #     }
        # """)
    
        # layout = QVBoxLayout()
        # # Header Group with links
        # header_group = QGroupBox("BitCurrent")
        # header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        # header_group.setAlignment(Qt.AlignLeft) 
        # header_layout = QHBoxLayout(header_group)

        # home_button = QPushButton("Home")
        # home_button.clicked.connect(self.parent.show_start_page)
        # header_layout.addWidget(home_button)

        # wallet_button = QPushButton("Wallet")
        # wallet_button.clicked.connect(self.parent.show_wallet_page)
        # header_layout.addWidget(wallet_button)

        # self.mine_button = QPushButton("Start Mining")
        # self.mine_button.clicked.connect(self.toggle_mining)
        # header_layout.addWidget(self.mine_button)

        # log_button = QPushButton("Log Out")
        # log_button.clicked.connect(self.logout)
        # header_layout.addWidget(log_button)
        # layout.addWidget(header_group)
            
        # SUMMARY STATS
        summary_group = QGroupBox(f'Welcome {self.parent.wallet_name}!!')
        summary_group.setFont(QFont("Georgia", 26, QFont.Bold, italic=True))
        summary_group.setAlignment(Qt.AlignLeft) 
        summary_layout = QHBoxLayout(summary_group)

        wallet_bal_dol = round(self.wallet_bal_tao * tao_price, 2)
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
        mining_info_layout.addWidget(QLabel("0.0HRS", font= QFont('Georgia', 20, QFont.Bold)))
        mining_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        summary_layout.addWidget(mining_info_group)
        # layout.addWidget(summary_group)

        # CPU USAGE
        cpu_info_group = QGroupBox()
        cpu_info_layout = QVBoxLayout(cpu_info_group)
        cpu_info_layout.addWidget(QLabel("CPU Usage", font=QFont('Georgia', 10)))
        cpu_info_layout.addWidget(QLabel("0.0%", font= QFont('Georgia', 20, QFont.Bold)))
        cpu_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))        
        summary_layout.addWidget(cpu_info_group)

        # GPU USAGE
        gpu_info_group = QGroupBox()
        gpu_info_layout = QVBoxLayout(gpu_info_group)
        gpu_info_layout.addWidget(QLabel("GPU Usage", font=QFont('Georgia', 10)))
        gpu_info_layout.addWidget(QLabel("0.0%", font= QFont('Georgia', 20, QFont.Bold)))
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
        self.layout.addWidget(summary_group)

        # # User Activity Chart
        # activity_plot = pg.PlotWidget()
        # activity_plot.setBackground((50, 50, 50))
        # activity_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        # activity_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        # activity_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        # activity_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        # activity_plot.showGrid(x=True, y=True, alpha=0.5)
        # # activity_plot.plot([0, 1, 2, 3,5], [0, 5, 3, 8, 2], pen='r', symbol='o', symbolPen='r', symbolBrush=(255, 0, 0), symbolSize=10)
        # num_dates = mdates.date2num(activity_data['date'].tolist()).tolist()
        # activity_plot.plot(num_dates, activity_data['time(s)'].tolist(), pen='g', symbol='o', symbolPen='r', symbolBrush=(50, 205, 50), symbolSize=10)
        # activity_plot.getAxis('bottom').setTicks([[(num_dates[i], activity_data['date'].tolist()[i].strftime('%Y-%m-%d')) for i in range(len(activity_data['date'].tolist()))]])

        # # Reward History Chart
        # reward_plot = pg.PlotWidget()
        # reward_plot.setBackground((50, 50, 50))
        # reward_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        # reward_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        # reward_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        # reward_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        # reward_plot.showGrid(x=True, y=True, alpha=0.5)
        # num_dates = mdates.date2num(reward_data['date'].tolist()).tolist()
        # reward_plot.plot(num_dates, reward_data['balance'].tolist(), pen='g', symbol='o', symbolPen='g', symbolBrush=(50, 205, 50), symbolSize=10)
        # reward_plot.getAxis('bottom').setTicks([[(num_dates[i], reward_data['date'].tolist()[i].strftime('%Y-%m-%d')) for i in range(len(reward_data['date'].tolist()))]])

        # *****************************
        # button to show charts or logs
        # *****************************
        self.toggle_button = QPushButton("Show Logs")
        self.toggle_button.clicked.connect(self.toggle_view)
        self.layout.addWidget(self.toggle_button)
        
        self.output_area = QTextEdit(self)
        self.output_area.setWordWrapMode(QTextOption.NoWrap)
        self.output_area.setReadOnly(False)  # Make it read-only
        self.output_area.hide()  # Hide initially
        self.layout.addWidget(self.output_area)  # Add it to the main layout

        self.input_line = QLineEdit(self)
        self.input_line.hide()  # Initially hide the input line
        self.layout.addWidget(self.input_line)  # Add it to your layout

        self.input_button = QPushButton("Enter")
        self.input_button.clicked.connect(self.send_input)
        self.input_button.hide()
        self.layout.addWidget(self.input_button)  # Place the button below the QTextEdit

        # Charts Section
        self.charts_group = QGroupBox()
        # self.charts_group.setStyleSheet("QGroupBox { font-size: 18px; color: #ffffff; border: 2px solid #3498db; border-radius: 5px; margin-top: 10px;}")
        charts_layout = QVBoxLayout(self.charts_group)
        # charts_layout.addWidget(QLabel("Cumulative Earnings", font=QFont('Georgia', 12, QFont.Bold)))
        # charts_layout.addWidget(reward_plot)
        # charts_layout.addWidget(QLabel("Daily Mining Time", font=QFont('Georgia', 12, QFont.Bold)))
        # charts_layout.addWidget(activity_plot)
        self.plot_graph(reward_data['date'], reward_data['balance'])
        charts_layout.addWidget(self.webEngineView)
        self.layout.addWidget(self.charts_group)
        self.setLayout(self.layout)
     
    # ********
    # Methods
    # ********
        
    def setupUI(self):
        self.layout = QVBoxLayout()
        self.createHeader()

    def createHeader(self):
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold))
        header_layout = QHBoxLayout(header_group)
        # header_group.setLayout(header_layout)
        # header_group.setFixedHeight(30) 

        home_button = QPushButton("Home")
        self.parent.addDetail(header_layout, home_button, 14)
        home_button.clicked.connect(self.parent.show_start_page)

        wallet_button = QPushButton("Wallet")
        self.parent.addDetail(header_layout, wallet_button, 14)
        wallet_button.clicked.connect(self.parent.show_wallet_page)

        self.mine_button = QPushButton("Start Mining")
        self.parent.addDetail(header_layout,  self.mine_button, 14)
        self.mine_button.clicked.connect(self.toggle_mining)

        log_button = QPushButton("Log Out")
        self.parent.addDetail(header_layout, log_button, 14)
        log_button.clicked.connect(self.logout)
        
        self.layout.addWidget(header_group)


    def get_user_hotkey_and_set_reg(self):
        """
        get users hotkey and checks if registered on subnet
        """
        if not hasattr(self.parent, 'hotkey'):
            hotkey_files = [f for f in os.listdir(os.path.join(self.parent.wallet_path,'hotkeys'))]
            hotkey_file = hotkey_files[-1]
            with open(f'{self.parent.wallet_path}/hotkeys/{hotkey_file}', 'r') as f:
                my_wallet = json.load(f)
            self.parent.hotkey= my_wallet['ss58Address']

        if self.parent.hotkey in self.parent.subnet.hotkeys:
            uid = self.parent.subnet.hotkeys.index(self.parent.hotkey)
            self.wallet_bal_tao = self.parent.subnet.stake.tolist()[uid]
            self.registered = True
        else:
            wallet_bal_tao = str(self.parent.subtensor.get_balance(address = self.parent.hotkey))[1:]
            self.wallet_bal_tao = float(wallet_bal_tao)
            self.registered = False


    def toggle_mining(self):
        """changes start mining button to stop mining"""
        if self.mining_process is None or self.mining_process.state() == QProcess.NotRunning:
            self.start_mining()
        else:
            self.stop_mining()
    
    # changes chat to logs
    def toggle_view(self):
        if self.charts_group.isVisible():
            self.charts_group.hide()
            self.output_area.show()
            self.toggle_button.setText("Show Charts")
        else:
            self.output_area.hide()
            self.charts_group.show()
            self.toggle_button.setText("Show Logs")

    def start_mining(self):
        self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Checking for registration')
        while not self.registered:
            response = self.handle_registration()
            if response == None:
                break
        if self.registered:
            self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - You are registered and ready to mine')
            self.run_mining_script()

    def handle_registration(self):
        self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - You are not registered')
        self.registration_cost = self.parent.subtensor.recycle(netuid=25)
        warning_msg = f"You are not registered to mine on Bitcurrent!\nRegistration cost is {self.registration_cost} TAO\n Do you want to register?\nNote this amount will be deducted from your wallet."
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
        wallet_bal = self.parent.subtensor.get_balance(address=self.parent.hotkey)
        # check wallet balance
        if wallet_bal < self.registration_cost:
            self.output_area.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - You don\'t have sufficient funds')
            warning_msg = f"[red]Insufficient balance {wallet_bal} to register neuron.t\nWould you like to add funds to you account?"
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
        self.timer.timeout.connect(self.update_timer)

        # Log balance and start of mining
        self.data_logger.info(f' Balance - Start: {self.wallet_bal_tao}')
        command = "python"
        args = ["-u",
            "DistributedTraining/neurons/miner.py",
            "--netuid", "34",
            "--subtensor.network", "test",
            "--wallet.name", f"{self.parent.wallet_name}",
            "--wallet.hotkey", f"{self.parent.hotkey}",
            "--logging.debug",
            "--axon.port", "8000",
            "--dht.port", "8001",
            "--dht.announce_ip", f"{IP_ADDRESS}",
            "--neuron.initial_peers", f"{INITIAL_PEERS}",
            # "--neuron.wandb_project", "subnet25_test"
        ]
        
        self.mining_process.start(command, args)
        # self.mining_process.start("python", [script_path])
        if self.charts_group.isVisible():
            self.toggle_view()
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
        self.parent.output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
        self.output_area.append(self.parent.output.replace('|',' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').strip())   
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
        self.timer.stop()
        self.data_logger.info(f' Balance - Stop: {self.wallet_bal_tao}') 
        self.data_logger.info(f' Activity: Stop Mining')
        self.data_logger.info(f' Activity: Mining Time - {self.elapsed_time}') 
        self.mine_button.setText("Start Mining")

        cpu_usage_match = re.search(r'CPU Usage: ([\d.]+)%', self.parent.output)
        # time_taken_cpu_match = re.search(r'Time taken on CPU: ([\d.]+) seconds', output)
        if cpu_usage_match: # and time_taken_cpu_match:
            cpu_usage = float(cpu_usage_match.group(1))
            self.data_logger.info(f' Activity - CPU Usage%: {cpu_usage}')
            # time_taken_cpu = float(time_taken_cpu_match.group(1))     
        # print(self.parent.output)

    # def display_errors(self, error_message):
    #     error_traceback = traceback.format_exc()
    #     current_font = self.output_area.font()
    #     current_wrap_mode = self.output_area.wordWrapMode()
    #     # Set monospace font and turn off word wrap for better error display
    #     self.output_area.setFont(QFont("Courier New"))
    #     self.output_area.setWordWrapMode(QTextOption.NoWrap)
    #     # Append the error traceback as plain text
    #     self.output_area.append(error_traceback) 
    #     # Restore the original font and word wrap mode
    #     self.output_area.setFont(current_font)
    #     self.output_area.setWordWrapMode(current_wrap_mode)
    #     # Ensure the latest output/error is visible in the QTextEdit
    #     self.output_area.moveCursor(QTextCursor.End)

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

    def send_input(self):
        input_text = self.input_line.text() + '\n'
        self.mining_process.write(input_text.encode())
        self.input_line.clear()
        self.input_line.hide()  # Hide the input line after sending input
        self.input_button.hide()
         
      
    def logout(self):
        warning_msg = f"Are you sure you want to log out?"
        reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.parent.dashboardpage
            if hasattr(self.parent, 'walletdetailstable'):
                del self.parent.walletdetailstable
            self.parent.wallet_name = None
            self.parent.wallet_path = None
            self.parent.show_start_page()


    def plot_graph(self, x, y):
        # Create a QWebEngineView to display the Plotly chart
        self.webEngineView = QWebEngineView()
        # Sample data generation for demonstration
        dates = x #pd.date_range(start="2023-01-01", periods=100, freq='D')
        earnings = y  # Cumulative earnings

        fig = go.Figure(data=[go.Scatter(x=dates, y=earnings, mode='lines+markers', name='Cumulative Earnings',line=dict(color='Green', width=2),marker=dict(color='green', size=3))])
        # fig.update_layout(title='Cumulative Earnings Over Time', xaxis_title='Time', yaxis_title='Cumulative Earnings')

        fig.update_layout(
            title_text='Cumulative Earnings Over Time',
            xaxis_title='Time',
            yaxis_title='Cumulative Earnings',
            template="plotly_dark"  # Use Plotly's dark theme
        )
        # # Create a Plotly figure
        # fig = go.Figure(data=[go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13])])
        # fig.update_layout(title='Plotly Chart in PyQt')

        # Convert the figure to HTML and load it into the QWebEngineView
        raw_html = '<html><head><meta charset="utf-8" /></head><body>'
        raw_html += pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
        raw_html += '</body></html>'
        self.webEngineView.setHtml(raw_html)
        # self.layout.addWidget(self.webEngineView)