import os
import json
from abc import abstractmethod
from functools import partial

import plotly.io as pio
import plotly.graph_objects as go
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QGroupBox, QMessageBox, QTextEdit, \
    QLineEdit
from PyQt5.QtGui import QFont, QTextOption, QDesktopServices
from PyQt5.QtCore import Qt, QTimer, QDateTime, QProcess, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pyqtgraph as pg
import bittensor as bt

from config import tao_price
from utils import get_earnings_by_date_range, get_total_mining, configure_logger_data, logger_wrapper


class DashboardPageBase(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent
        # self.addDetail = self.parent.addDetail
        self.data_logger = configure_logger_data(f"{self.parent.wallet_path}/full_user_data.log")
        self.parent.initialize_subtensor()

        self.get_user_hotkey_and_set_reg()
        self.setupUI()

        self.data_logger.info(f' Balance - Start: {self.parent.wallet_bal_tao}')
        self.data_logger.info('Activity: Log in')
        self.data_logger.info(f' Activity: Mining Time - 0')
        reward_data = get_earnings_by_date_range(f"{self.parent.wallet_path}/full_user_data.log")
        activity_data = get_total_mining(f"{self.parent.wallet_path}/full_user_data.log")

        # SUMMARY STATS
        summary_group = QGroupBox(f'Welcome {self.parent.wallet_name}!!')
        summary_group.setFont(QFont("Georgia", 26, QFont.Bold, italic=True))
        summary_group.setAlignment(Qt.AlignLeft)
        summary_layout = QHBoxLayout(summary_group)

        wallet_bal_dol = round(self.parent.wallet_bal_tao * tao_price, 2)
        earnings_group = QGroupBox()
        earnings_layout = QVBoxLayout(earnings_group)
        earnings_layout.addWidget(QLabel("Wallet Balance", font=QFont('Georgia', 10)))
        earnings_layout.addWidget(QLabel(f"${wallet_bal_dol}", font=QFont('Georgia', 20, QFont.Bold)))
        earnings_layout.addWidget(QLabel(f"TAO {self.parent.wallet_bal_tao}", font=QFont('Georgia', 10)))
        summary_layout.addWidget(earnings_group)

        # Mining infomation
        mining_info_group = QGroupBox()
        mining_info_layout = QVBoxLayout(mining_info_group)
        mining_info_layout.addWidget(QLabel("Average Mining Time", font=QFont('Georgia', 10)))
        mining_info_layout.addWidget(QLabel("0.0HRS", font=QFont('Georgia', 20, QFont.Bold)))
        mining_info_layout.addWidget(QLabel(" ", font=QFont('Georgia', 10)))
        summary_layout.addWidget(mining_info_group)
        # layout.addWidget(summary_group)

        # CPU USAGE
        cpu_info_group = QGroupBox()
        cpu_info_layout = QVBoxLayout(cpu_info_group)
        cpu_info_layout.addWidget(QLabel("CPU Usage", font=QFont('Georgia', 10)))
        self.cpu_usage_label = QLabel("0.0%", font=QFont('Georgia', 20, QFont.Bold))
        cpu_info_layout.addWidget(self.cpu_usage_label)
        cpu_info_layout.addWidget(QLabel(" ", font=QFont('Georgia', 10)))
        summary_layout.addWidget(cpu_info_group)

        # GPU USAGE
        gpu_info_group = QGroupBox()
        gpu_info_layout = QVBoxLayout(gpu_info_group)
        gpu_info_layout.addWidget(QLabel("GPU Usage", font=QFont('Georgia', 10)))
        self.gpu_usage_label = QLabel("0.0%", font=QFont('Georgia', 20, QFont.Bold))
        gpu_info_layout.addWidget(self.gpu_usage_label)
        gpu_info_layout.addWidget(QLabel(" ", font=QFont('Georgia', 10)))
        summary_layout.addWidget(gpu_info_group)

        # Timer
        self.timer = QTimer(self)  # Create timer
        timer_group = QGroupBox()
        timer_info_layout = QVBoxLayout(timer_group)
        timer_info_layout.addWidget(QLabel("Live Mining Time", font=QFont('Georgia', 10)))
        self.timer_label = QLabel("0h: 0m: 0s", self)
        self.timer_label.setFont(QFont("Georgia", 20, QFont.Bold))
        timer_info_layout.addWidget(self.timer_label)
        timer_info_layout.addWidget(QLabel(" ", font=QFont('Georgia', 10)))

        # # Define Mining/Live time
        self.mining_process = None
        self.update_script_process = None
        self.start_time = QDateTime.currentDateTime()
        self.timer.timeout.connect(self.update_timer)
        summary_layout.addWidget(timer_group)
        self.layout.addWidget(summary_group)

        # User Activity Chart
        activity_plot = pg.PlotWidget()
        activity_plot.setBackground((50, 50, 50))
        activity_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        activity_plot.showGrid(x=True, y=True, alpha=0.5)
        # activity_plot.plot([0, 1, 2, 3,5], [0, 5, 3, 8, 2], pen='r', symbol='o', symbolPen='r', symbolBrush=(255, 0, 0), symbolSize=10)
        num_dates = mdates.date2num(activity_data['date'].tolist()).tolist()
        activity_plot.plot(num_dates, activity_data['time(s)'].tolist(), pen='g', symbol='o', symbolPen='r',
                           symbolBrush=(50, 205, 50), symbolSize=10)
        activity_plot.getAxis('bottom').setTicks([[(
            num_dates[i], activity_data['date'].tolist()[i].strftime('%Y-%m-%d'))
            for i in range(len(activity_data['date'].tolist()))]])

        # Reward History Chart
        reward_plot = pg.PlotWidget()
        reward_plot.setBackground((50, 50, 50))
        reward_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        reward_plot.showGrid(x=True, y=True, alpha=0.5)
        num_dates = mdates.date2num(reward_data['date'].tolist()).tolist()
        reward_plot.plot(num_dates, reward_data['balance'].tolist(), pen='g', symbol='o', symbolPen='g',
                         symbolBrush=(50, 205, 50), symbolSize=10)
        reward_plot.getAxis('bottom').setTicks([[(num_dates[i], reward_data['date'].tolist()[i].strftime('%Y-%m-%d'))
                                                 for i in range(len(reward_data['date'].tolist()))]])

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

        self.log = logger_wrapper(self.output_area.append, end="")

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
        header_group = QGroupBox("EasyMiner", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold))
        header_layout = QHBoxLayout(header_group)
        # header_group.setLayout(header_layout)
        # header_group.setFixedHeight(30)

        home_button = QPushButton("Home")
        self.parent.addDetail(header_layout, home_button, 14)
        home_button.clicked.connect(partial(self.parent.show_start_page, page_to_delete=self))

        self.wallet_button = QPushButton("Wallet")
        self.parent.addDetail(header_layout, self.wallet_button, 14)

        self.mine_button = QPushButton("Start Mining")
        self.parent.addDetail(header_layout, self.mine_button, 14)
        self.mine_button.clicked.connect(self.toggle_mining)

        log_button = QPushButton("Log Out")
        self.parent.addDetail(header_layout, log_button, 14)
        log_button.clicked.connect(self.logout)

        self.layout.addWidget(header_group)

    def get_user_coldkey(self):
        coldkey_pub_file = os.path.join(self.parent.wallet_path, 'coldkeypub.txt')
        with open (coldkey_pub_file,'r') as f:
            my_coldkey = json.load(f)
        return my_coldkey['ss58Address']

    
    def get_user_hotkey_and_set_reg(self):
        """
        get users hotkey and checks if registered on subnet
        """
        if not hasattr(self.parent, 'hotkey') or self.parent.hotkey is None:
            hotkey_files = [f for f in os.listdir(os.path.join(self.parent.wallet_path, 'hotkeys'))]
            hotkey_file = hotkey_files[-1]
            with open(f'{self.parent.wallet_path}/hotkeys/{hotkey_file}', 'r') as f:
                my_wallet = json.load(f)
            self.parent.hotkey = my_wallet['ss58Address']

            self.parent.coldkey = self.get_user_coldkey()
            print(self.parent.coldkey)

            wallet_bal_tao = str(self.parent.subtensor.get_balance(address=self.parent.coldkey))[1:]
            self.parent.wallet_bal_tao = float(wallet_bal_tao)
            print(self.parent.wallet_bal_tao)

        self.registered = self.parent.hotkey in self.parent.subnet.hotkeys

    def toggle_mining(self):
        """changes start mining button to stop mining"""
        if not self.is_running():
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

    def handle_registration(self):
        self.log('You are not registered')
        self.registration_cost = self.parent.subtensor.recycle(netuid=self.parent.net_id)
        warning_msg = f"You are not registered on Subnet {self.parent.net_id}! \nRegistration cost is {self.registration_cost}. \n Do you want to register?\nNote this amount will be deducted from your wallet."
        reply = QMessageBox.warning(self, "Warning", warning_msg, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            response = self.register_on_subnet()
            if response == QMessageBox.Ok:
                self.registered = True
            else:
                self.registered = False

    def register_on_subnet(self):
        self.wallet = bt.wallet(
            name=self.parent.wallet_name,
            path=os.path.dirname(self.parent.wallet_path),
            hotkey=self.parent.hotkey
        )
        wallet_bal = self.parent.subtensor.get_balance(address=self.parent.coldkey)
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

    @abstractmethod
    def stop_mining(self):
        pass

    @abstractmethod
    def start_mining(self):
        pass

    @abstractmethod
    def is_running(self):
        pass

    @abstractmethod
    def update_cpu_usage(self):
        pass

    @abstractmethod
    def update_gpu_usage(self):
        pass

    @abstractmethod
    def update_timer(self):
        pass

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
            self.parent.wallet_name = None
            self.parent.wallet_path = None
            self.parent.hotkey = None
            self.parent.show_start_page(page_to_delete=self)

    def plot_graph(self, x, y):
        # Create a QWebEngineView to display the Plotly chart
        self.webEngineView = QWebEngineView()
        # Sample data generation for demonstration
        dates = x  # pd.date_range(start="2023-01-01", periods=100, freq='D')
        earnings = y  # Cumulative earnings

        fig = go.Figure(data=[go.Scatter(x=dates, y=earnings, mode='lines+markers', name='Cumulative Earnings',
                                         line=dict(color='Green', width=2), marker=dict(color='green', size=3))])
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

    def wandb_login(self):
        self.wandb_login_process = QProcess(self)
        self.parent.process.append(self.wandb_login_process)

        self.wandb_login_process.setProcessChannelMode(QProcess.MergedChannels)
        command = "wandb"
        args = [
            "login",
            f"{self.parent.wandb_api_key}"
        ]
        self.wandb_login_process.start(command, args)
