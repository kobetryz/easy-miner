import sys
import json
import requests

import bittensor as bt

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QPushButton, QGroupBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pyqtgraph as pg




class SelectDashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

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
        home_button.clicked.connect(parent.show_start_page)
        header_layout.addWidget(home_button)

        wallet_button = QPushButton("Wallet")
        wallet_button.clicked.connect(parent.show_wallet_page)
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
        summary_group = QGroupBox('Welcome Bill')
        summary_group.setFont(QFont("Georgia", 26, QFont.Bold, italic=True))
        summary_group.setAlignment(Qt.AlignLeft) 
        summary_layout = QHBoxLayout(summary_group)

        # earnings infomation
        url = "https://taostats.io/data.json"
        response = requests.get(url)
        taostats = json.loads(response.content)
        price = float(taostats[0]['price'])

        
        # wallet balance we need to figure out how to get this number
        # get uid
        # subnet = bt.metagraph(netuid = 25)
        # with open('/Users/beekin/projects/btt-plug-n-play/my_wallet/hotkeys/default', 'r') as f:
        #     my_wallet = json.load(f)
        
        # uid = subnet.hotkeys.index(my_wallet['ss58_address'])
        


        wallet_bal_tao = 0.8566
        wallet_bal_dol = round(wallet_bal_tao * price, 2)

        earnings_group = QGroupBox()
        earnings_layout = QVBoxLayout(earnings_group)
        earnings_layout.addWidget(QLabel("Wallet Balance",font=QFont('Georgia', 10)))
        earnings_layout.addWidget(QLabel(f"${wallet_bal_dol}", font= QFont('Georgia', 20, QFont.Bold)))
        earnings_layout.addWidget(QLabel(f"TAO {wallet_bal_tao}", font= QFont('Georgia', 10)))
        
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


        # CPU USAGE
        gpu_info_group = QGroupBox()
        gpu_info_layout = QVBoxLayout(gpu_info_group)
        gpu_info_layout.addWidget(QLabel("GPU Usage", font=QFont('Georgia', 10)))
        gpu_info_layout.addWidget(QLabel("54.3%", font= QFont('Georgia', 20, QFont.Bold)))
        gpu_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        
        summary_layout.addWidget(gpu_info_group)


        layout.addWidget(summary_group)






        # summary_group = QGroupBox("Summary Stats")
        # summary_group.setStyleSheet("QGroupBox { font-size: 18px; color: #ffffff; border: 2px solid #3498db; border-radius: 5px; margin-top: 10px;}")
        # summary_layout = QVBoxLayout(summary_group)
        # summary_layout.addWidget(QLabel("Total Rewards: $500", font=QFont('Georgia', 14, QFont.Bold)))
        # summary_layout.addWidget(QLabel("Average Mining Time: 2 hours/day", font=QFont('Georgia', 14, QFont.Bold)))
        # layout.addWidget(summary_group)

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
        charts_layout.addWidget(QLabel("User Activity Chart", font=QFont('Georgia', 14, QFont.Bold)))
        charts_layout.addWidget(activity_plot)
        charts_layout.addWidget(QLabel("Reward History Chart", font=QFont('Georgia', 14, QFont.Bold)))
        charts_layout.addWidget(reward_plot)
        layout.addWidget(charts_group)

        self.setLayout(layout)
    
    # def show_wallet_details(self):
    #     wallet_details_page = WalletDetailsTable(data=wallet_details)
    #     wallet_details_page.show




















# # import sys
# # from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
# # from PyQt5.QtWebEngineWidgets import QWebEngineView
# # from PyQt5.QtCore import QUrl

# # class CryptoChartApp(QMainWindow):
# #     def __init__(self):
# #         super().__init__()
# #         self.setWindowTitle("Crypto Chart App")
# #         self.setGeometry(100, 100, 800, 600)

# #         central_widget = QWidget(self)
# #         self.setCentralWidget(central_widget)

# #         layout = QVBoxLayout(central_widget)

# #         # Create a QWebEngineView widget
# #         chart_view = QWebEngineView(self)

# #         # Set the URL of the dynamic chart
# #         chart_url = "https://taostats.io"
# #         chart_view.setUrl(QUrl(chart_url))

# #         # Add the QWebEngineView widget to the layout
# #         script = """
# #         var chartSection = document.getElementById('SvgjsSvg11327');
# #         document.body.innerHTML = chartSection.outerHTML;
# #             """
# #         chart_view.page().runJavaScript(script)
# #         layout.addWidget(chart_view)

# # if __name__ == '__main__':
# #     app = QApplication(sys.argv)
# #     crypto_chart_app = CryptoChartApp()
# #     crypto_chart_app.show()
# #     sys.exit(app.exec_())








# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5.QtCore import QUrl, pyqtSlot

# # class CryptoChartApp(QMainWindow):
# #     def __init__(self):
# #         super().__init__()
# #         self.setWindowTitle("Crypto Chart App")
# #         self.setGeometry(100, 100, 800, 600)

# #         central_widget = QWidget(self)
# #         self.setCentralWidget(central_widget)

# #         layout = QVBoxLayout(central_widget)

# #         # Create a QWebEngineView widget
# #         chart_view = QWebEngineView(self)

# #         # Set the URL of the dynamic chart
# #         chart_url = "https://taostats.io"
# #         chart_view.setUrl(QUrl(chart_url))

# #         # Connect the loadFinished signal to a slot
# #         chart_view.page().loadFinished.connect(self.on_page_load_finished)

# #         # Add the QWebEngineView widget to the layout
# #         layout.addWidget(chart_view)

# #     @pyqtSlot(bool)
# #     def on_page_load_finished(self, success):
# #         if success:
# #             # Load only the specific section of the webpage using JavaScript injection
# #             script = """
# #             var chartSection = document.getElementById('metagraph_view'); // Replace 'chart-section' with the actual ID or class of the HTML element
# #             if (chartSection) {
# #                 document.body.innerHTML = chartSection.outerHTML;
# #             }
# #             """
# #             self.sender().runJavaScript(script)

# # if __name__ == '__main__':
# #     app = QApplication(sys.argv)
# #     crypto_chart_app = CryptoChartApp()
# #     crypto_chart_app.show()
# #     sys.exit(app.exec_())


# from PyQt5.QtCore import Qt, QUrl
# from PyQt5.QtGui import QFont
# from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# class WebPage(QWebEnginePage):
#     def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
#         print("Console({}): {} at {} - {}".format(level, message, lineNumber, sourceID))

# class CryptoStatsApp(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Crypto Stats App")
#         self.setGeometry(100, 100, 800, 600)

#         central_widget = QWidget(self)
#         self.setCentralWidget(central_widget)

#         layout = QVBoxLayout(central_widget)

#         # Create a QWebEngineView to display the embedded webpage
#         self.webview = QWebEngineView(self)
#         layout.addWidget(self.webview)

#         # Load the embedded webpage with specific JavaScript to extract only the chart section
#         chart_url =  "https://taostats.io/" #"https://coinmarketcap.com/currencies/bittensor/"
#         self.webview.setPage(WebPage(self.webview))
#         self.webview.page().runJavaScript('''
#             document.addEventListener("DOMContentLoaded", function() {
#                 var chartSection = document.getElementsByClassName("metagraph_view");
#                 if (chartSection) {
#                     document.body.innerHTML = chartSection.outerHTML;
#                 }
#             });
#         ''')
#         # self.webview.page().runJavaScript('''
#         #     document.addEventListener("DOMContentLoaded", function() {
#         #         console.log(document.body.innerHTML);
#         #     });
#         # ''')

#         self.webview.setUrl(QUrl(chart_url))

# if __name__ == '__main__':
#     app = QApplication([])
#     crypto_app = CryptoStatsApp()
#     crypto_app.show()
#     app.exec_()
