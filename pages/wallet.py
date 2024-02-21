import json
import os
import bittensor as bt
from PyQt5.QtWidgets import (QInputDialog, QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class WalletDetailsTable(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        if not self.parent.hotkey:
            hotkey_files = [f for f in os.listdir(os.path.join(self.parent.wallet_path, 'hotkeys'))]
            hotkey_file = hotkey_files[-1]
            with open(f'{self.parent.wallet_path}/hotkeys/{hotkey_file}', 'r') as f:
                my_wallet = json.load(f)
            self.parent.hotkey = my_wallet['ss58Address']

        if self.parent.hotkey in parent.subnet.hotkeys:
            uid = self.parent.subnet.hotkeys.index(self.parent.hotkey)
            self.parent.wallet_details = {
                'coldkey': self.parent.subnet.coldkeys[uid],
                'hotkey': self.parent.hotkey,
                'uid': uid,
                'active': self.parent.subnet.active.tolist()[uid],
                'stake': self.parent.subnet.stake.tolist()[uid],
                'rank': self.parent.subnet.ranks.tolist()[uid],
                'trust': self.parent.subnet.trust.tolist()[uid],
                'consensus': self.parent.subnet.consensus.tolist()[uid],
                'incentive': self.parent.subnet.incentive.tolist()[uid],
                'dividends': self.parent.subnet.dividends.tolist()[uid],
                'vtrust': self.parent.subnet.validator_trust.tolist()[uid]
            }
        else:
            print(f"{self.parent.hotkey} not registered")
            with open(f'{os.path.join(self.parent.wallet_path)}/coldkeypub.txt', 'r') as f:
                address_json = json.load(f)
                self.parent.coldkey = address_json['ss58Address']
            uid = 000
            self.parent.wallet_details = {
                'coldkey': self.parent.coldkey,
                'hotkey': self.parent.hotkey,
                'uid': uid,
                'active': 0,
                'stake': 0,
                'rank': 0,
                'trust': 0,
                'consensus': 0,
                'incentive': 0,
                'dividends': 0,
                'vtrust': 0
            }

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
        self.populate_table(table_widget)

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

    def populate_table(self, table_widget):
        table_widget.setRowCount(len(self.parent.wallet_details))
        table_widget.setColumnCount(2)
        table_widget.setHorizontalHeaderLabels(["Parameter", "Value"])

        header = table_widget.horizontalHeader()
        font1 = QFont("Georgia", 18, QFont.Bold)
        header.setFont(font1)

        font2 = QFont("Georgia", 14)
        for row, (key, value) in enumerate(self.parent.wallet_details.items()):
            key_item = QTableWidgetItem(str(key))
            key_item.setFont(font2)
            value_item = QTableWidgetItem(str(value))
            value_item.setFont(font2)

            table_widget.setItem(row, 0, key_item)
            table_widget.setItem(row, 1, value_item)
        table_widget.setColumnWidth(0, 150)  # Set the width of the first column to 150 pixels
        table_widget.setColumnWidth(1, 350)
