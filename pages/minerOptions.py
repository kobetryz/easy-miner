from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QRadioButton, QVBoxLayout, \
    QLabel, QGroupBox, QMessageBox, QGridLayout

from config import SubnetType, MinerType, SUBNET_MAPPER, NetworkType
from functools import partial


class MinerOptionsPage(QWidget):
    def __init__(self, parent, *args, **kwargs):
        QWidget.__init__(self, parent)
        self.parent = parent

        self.network = NetworkType.FINNEY.value
        self.miner_type = MinerType.MINER.value
        self.subnet = SubnetType.DISTRIBUTED_TRAINING.value

        self.show_next_page = kwargs.get("instead_machine_options", self.parent.show_machine_options_page)

        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.createHeader()
        self.createNetOptions()
        self.createMinerOptions()
        self.createNetworkOptions()
        self.createFooter()

        self.setLayout(self.layout)

    def createHeader(self):
        header_group = QGroupBox("EasyMiner", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold, italic=True))
        header_layout = QHBoxLayout()
        header_group.setLayout(header_layout)
        header_group.setFixedHeight(30)
        self.layout.addWidget(header_group)

    def createMinerOptions(self):
        self.miner_option_group = QGroupBox("Run as")
        options_layout = QHBoxLayout(self.miner_option_group)
        options_layout.setSpacing(15)

        for miner_type in MinerType:
            radioButton = QRadioButton(miner_type.value.capitalize())
            radioButton.clicked.connect(self.onMinerRadioButtonClicked)
            if miner_type == MinerType.MINER:
                radioButton.click()
            self.parent.addDetail(options_layout, radioButton, 16)

        self.parent.addDetail(self.layout, self.miner_option_group, 20, bold=True)

    def onMinerRadioButtonClicked(self):
        sender = self.sender()
        self.miner_type = sender.text().lower()
        self.changeRequirements(self.subnet, self.miner_type)

    def createNetOptions(self):
        self.net_option_group = QGroupBox("Select subnet")
        self.net_option_layout = QHBoxLayout(self.net_option_group)

        self.createNetRadiobuttons()
        self.createRequirements()

        self.parent.addDetail(self.layout, self.net_option_group, 20, bold=True)

    def createNetRadiobuttons(self):
        subnets_layout = QVBoxLayout()
        subnets_layout.setSpacing(15)

        for net in SubnetType:
            radioButton = QRadioButton(net.value.upper())
            if net == SubnetType.DISTRIBUTED_TRAINING:
                radioButton.setChecked(True)
            radioButton.toggled.connect(self.onNetRadioClicked)  # noqa
            self.parent.addDetail(subnets_layout, radioButton, 16)
        self.net_option_layout.addLayout(subnets_layout)

    def onNetRadioClicked(self):
        sender = self.sender()
        if sender.isChecked():
            self.subnet = sender.text().lower()
            self.changeRequirements(self.subnet, self.miner_type)
            self.next_button.setEnabled(True)

    def createRequirements(self):
        requirements_group = QGroupBox("Minimum requirements")
        requirements = QGridLayout(requirements_group)
        requirements.addWidget(QLabel("GPU"), 0, 0)
        requirements.addWidget(QLabel("CPU"), 1, 0)
        requirements.addWidget(QLabel("RAM"), 2, 0)
        requirements.addWidget(QLabel("Storage"), 3, 0)
        requirements.addWidget(QLabel("Other"), 4, 0)


        self.cpu_required = QLabel("-")
        self.gpu_required = QLabel("-")
        self.ram_required = QLabel("-")
        self.storage_required = QLabel("-")
        self.other_required = QLabel("-")

        requirements.addWidget(self.gpu_required, 0, 1)
        requirements.addWidget(self.cpu_required, 1, 1)
        requirements.addWidget(self.ram_required, 2, 1)
        requirements.addWidget(self.storage_required, 3, 1)
        requirements.addWidget(self.other_required, 4, 1)

        self.parent.addDetail(self.net_option_layout, requirements_group, 14)

    def changeRequirements(self, subnet: str, miner_type: str):
        requirements = {
            SubnetType.DISTRIBUTED_TRAINING.value: {
                "miner": {"GPU": "16GB VRAM e.g. RTX A4000"},
                "validator": {"GPU": "16GB VRAM e.g. RTX A4000"}
            },
            SubnetType.PROMPTING.value: {
                "miner": {"GPU": "18GB of VRAM"},
                "validator": {"GPU": "24GB of VRAM"}
            },
            SubnetType.DATA_UNIVERSE.value: {
                "miner": {"GPU": "Not require a GPU", "CPU": "4+ cores",'OTHER':'NO TESTNET FOR THIS SUBNET'},
                "validator": {"GPU": "Not require a GPU", "RAM": "32 GB",'OTHER':'NO TESTNET FOR THIS SUBNET'}
            },
            SubnetType.BIT_AGENT.value: {
                "miner": {"GPU": "15GB of VRAM"},
                "validator": {"GPU": "15GB of VRAM"}
            },
            SubnetType.COMPUTE.value: {
                "miner": {"GPU": "40 GB", "CPU": "4+ cores", "STORAGE": "100 GB"},
                "validator": {"GPU": "40 GB", "CPU": "4+ cores", "STORAGE": "100 GB"},
            }
        }
        selected_requirements = requirements.get(subnet.lower(), {}).get(miner_type, {})

        self.cpu_required.setText(selected_requirements.get("CPU", "-"))
        self.gpu_required.setText(selected_requirements.get("GPU", "-"))
        self.ram_required.setText(selected_requirements.get("RAM", "-"))
        self.storage_required.setText(selected_requirements.get("STORAGE", "-"))
        self.other_required.setText(selected_requirements.get("OTHER", "-"))

    def createNetworkOptions(self):
        self.network_group = QGroupBox("Select network")
        network_layout = QHBoxLayout(self.network_group)
        network_layout.setSpacing(15)

        for network in NetworkType:
            radioButton = QRadioButton(network.value.capitalize())
            radioButton.clicked.connect(self.onNetworkRadiobuttonClicked)
            if network == NetworkType.FINNEY:
                radioButton.click()
            self.parent.addDetail(network_layout, radioButton, 16)

        self.parent.addDetail(self.layout, self.network_group, 20, bold=True)

    def onNetworkRadiobuttonClicked(self):
        sender = self.sender()
        self.network = sender.text().lower()

    def createFooter(self): 
        h_layout = QHBoxLayout(self)
        h_layout.setAlignment(Qt.AlignBottom)
        previous_button = QPushButton("Back to Main Menu")
        previous_button.clicked.connect(partial(self.parent.show_start_page, page_to_delete=self))  # noqa
        self.parent.addDetail(h_layout, previous_button, 12)

        self.next_button = QPushButton('Next')
        self.parent.addDetail(h_layout, self.next_button, 12)
        self.next_button.clicked.connect(self.nextClicked)  # noqa

        self.layout.addLayout(h_layout)

    def nextClicked(self):
        self.parent.miner_type = MinerType(self.miner_type)
        self.parent.net = SubnetType(self.subnet)
        self.parent.network = NetworkType(self.network)
        net_uid_index = 0 if self.parent.network == NetworkType.FINNEY else 1
        print(net_uid_index, self.parent.network)
        self.parent.net_id = SUBNET_MAPPER[self.parent.net.value][net_uid_index]
        print(self.parent.net_id)
        self.show_next_page(page_to_delete=self, instead_machine_options=self.show_next_page)

    def showSubnetNotImplemented(self):
        QMessageBox.warning(self, "Warning", "Current subnet is not implemented")

    @staticmethod
    def find_checked_radiobutton(radiobuttons):
        """find the checked radiobutton"""
        for items in radiobuttons:
            if items.isChecked():
                checked_radiobutton = items.text()
                return checked_radiobutton
