

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QPushButton, QGroupBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class SelectDashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # self.setWindowTitle("Mining Dashboard")

        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-family: Georgia;
            }
        """)

        layout = QVBoxLayout()

        # Header Group with links
        header_group = QGroupBox("BitCurrent")
        header_group.setFont(QFont("Orbitron", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QHBoxLayout(header_group)


        # header_layout.addWidget(QLabel("BITCURRENT"))
        home_button = QPushButton("Home")
        home_button.clicked.connect(parent.show_start_page)
        header_layout.addWidget(home_button)

        wallet_button = QPushButton("Wallet Settings")
        header_layout.addWidget(wallet_button)


        profile_button = QPushButton("Profile")
        header_layout.addWidget(profile_button)

        log_button = QPushButton("Log Out")
        header_layout.addWidget(log_button)


        test_group = QGroupBox()
        test_layout = QVBoxLayout(test_group)
        test_layout.addWidget(QPushButton("Withdraw Earnings"))
        test_layout.addWidget(QPushButton("Stop Mining"))
        header_layout.addWidget(test_group)

        # test_group.setFont(QFont("Orbitron", 18, QFont.Bold))


        layout.addWidget(header_group)

        # Summary Stats
        summary_group = QGroupBox("Summary Stats")
        summary_group.setStyleSheet("QGroupBox { font-size: 18px; color: #ffffff; border: 2px solid #3498db; border-radius: 5px; margin-top: 10px;}")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(QLabel("Total Rewards: $500", font=QFont('Arial', 14, QFont.Bold)))
        summary_layout.addWidget(QLabel("Average Mining Time: 2 hours/day", font=QFont('Arial', 14, QFont.Bold)))
        layout.addWidget(summary_group)

        # User Activity Chart
        activity_plot = pg.PlotWidget()
        activity_plot.setBackground((50, 50, 50))
        activity_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        activity_plot.showGrid(x=True, y=True, alpha=0.5)
        activity_plot.plot([0, 1, 2, 3, 4], [0, 5, 3, 8, 2], pen='g', symbol='o', symbolPen='g', symbolBrush=(50, 205, 50), symbolSize=10)

        # Reward History Chart
        reward_plot = pg.PlotWidget()
        reward_plot.setBackground((50, 50, 50))
        reward_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        reward_plot.showGrid(x=True, y=True, alpha=0.5)
        reward_plot.plot([0, 1, 2, 3, 4], [0, 10, 5, 15, 8], pen='r', symbol='o', symbolPen='r', symbolBrush=(255, 0, 0), symbolSize=10)

        # Charts Section
        charts_group = QGroupBox("Charts")
        charts_group.setStyleSheet("QGroupBox { font-size: 18px; color: #ffffff; border: 2px solid #3498db; border-radius: 5px; margin-top: 10px;}")
        charts_layout = QVBoxLayout(charts_group)
        charts_layout.addWidget(QLabel("User Activity Chart", font=QFont('Arial', 14, QFont.Bold)))
        charts_layout.addWidget(activity_plot)
        charts_layout.addWidget(QLabel("Reward History Chart", font=QFont('Arial', 14, QFont.Bold)))
        charts_layout.addWidget(reward_plot)
        layout.addWidget(charts_group)

        self.setLayout(layout)