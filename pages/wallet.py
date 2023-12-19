import json
import sys
import bittensor as bt
from PyQt5.QtWidgets import (QInputDialog, QPushButton, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout,QHBoxLayout, QWidget, QGroupBox, QLabel)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


with open('../my_wallet/hotkeys/default', 'r') as f:
    my_wallet = json.load(f)


# wallet_name, ok = QInputDialog.getText(None, "Wallet Name", "Enter your wallet name:")
# if not ok:
#     sys.exit()  

# print(my_wallet['ss58Address'])
# subnet = bt.metagraph(netuid = 25)

# ###  check if wallet is registered on subnet
# if my_wallet['ss58Address'] in subnet.hotkeys:
#     uid = subnet.hotkeys.index(my_wallet['ss58Address'])
# else: uid = 1    

# wallet_details = {
#     'coldkey' : subnet.coldkeys[uid],
#     'hotkey' : subnet.hotkeys[uid],
#     'uid' : uid,
#     'active' : subnet.active.tolist()[uid],
#     'stake' : subnet.stake.tolist()[uid],
#     'rank' : subnet.ranks.tolist()[uid],
#     'trust' : subnet.trust.tolist()[uid],
#     'consensus' : subnet.consensus.tolist()[uid],
#     'incentive' : subnet.incentive.tolist()[uid],
#     'dividends' : subnet.dividends.tolist()[uid],
#     'vtrust' : subnet.validator_trust.tolist()[uid]
# }
    
wallet_details = {"Name": "John", "Age": 30, "Location": "City"}


class WalletDetailsTable(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # self.wallet_name, ok = QInputDialog.getText(None, "Wallet Name", "Enter your wallet name:")
        # if not ok:
        #     sys.exit()  

        # print(parent.get_wallet_path)

        # self.setWindowTitle("Wallet Details")

        # central_widget = QWidget(self)
        # self.setCentralWidget(central_widget)

        # layout = QVBoxLayout(central_widget)

        layout = QVBoxLayout()


        # bit_label
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QVBoxLayout(header_group)

        page_label = QLabel("Wallet Overview", self)
        page_label.setFont(QFont("Georgia", 24, QFont.Bold))

        header_layout.addWidget(page_label)

        # Add table
        table_widget = QTableWidget(self)
        self.populate_table(table_widget, wallet_details)

        table_widget.setFixedSize(500, 400)
        header_layout.addWidget(table_widget)   
        layout.addWidget(header_group)

        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back", self)
        previous_button.setFont(QFont("Georgia", 14))
        previous_button.clicked.connect(parent.show_dashboard_page)
        h_layout.addWidget(previous_button)
        
        # Spacer to push the Previous button to the left
        h_layout.addStretch()
        layout.addLayout(h_layout)
        self.setLayout(layout)
    
    def populate_table(self, table_widget, wallet_details):
        table_widget.setRowCount(len(wallet_details))
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(["Parameter", "Value"])

        header = table_widget.horizontalHeader()
        font1 = QFont("Georgia", 18, QFont.Bold)  
        header.setFont(font1)

        
        font2 = QFont("Georgia", 14)
        for row, (key, value) in enumerate(wallet_details.items()):
            key_item = QTableWidgetItem(str(key))
            key_item.setFont(font2)
            value_item = QTableWidgetItem(str(value))
            value_item.setFont(font2)

            table_widget.setItem(row, 0, key_item)
            table_widget.setItem(row, 1, value_item)
        table_widget.setColumnWidth(0, 150)  # Set the width of the first column to 150 pixels
        table_widget.setColumnWidth(1, 350) 

