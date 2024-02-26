import json
import os
import time

from config import COUNTRY_CODE, PERSISTENT_DISK_SIZE_GB, OS_DISK_SIZE_GB
from runpod_api.runpod import GPU_DICT, GPU_LIST_TO_USE, api
from PyQt5.QtWidgets import QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel, QRadioButton, \
    QMessageBox
from PyQt5.QtCore import Qt

from utils import get_secret_hotkey


class RunpodSetupPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.setLayout(self.layout)

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        # self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.create_header()
        self.create_gpu_options()
        self.layout.addStretch()  # Add a stretchable space that expands to fill any remaining space at the end of the layout

    def create_header(self):
        header = QLabel("BitCurrent", self)
        header.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.parent.addDetail(self.layout, header, 20, bold=True)

    def create_gpu_options(self):
        option_group = QGroupBox("Select GPU", self)
        options_layout = QVBoxLayout(option_group)
        options_layout.setAlignment(Qt.AlignTop)
        options_layout.setSpacing(10)

        self.gpu_drop_down = QComboBox()
        self.gpu_drop_down.setMaximumWidth(300)
        self.parent.addDetail(options_layout, self.gpu_drop_down, 18)
        self.gpu_drop_down.addItems(GPU_LIST_TO_USE)

        # Set "RTX A4000" as the default GPU if it exists in the GPU_LIST_TO_USE
        index = self.gpu_drop_down.findText("RTX A4000")
        if index >= 0:
            self.gpu_drop_down.setCurrentIndex(index)

        # Create a new layout to hold the GPU specs labels
        self.specs_layout = QVBoxLayout()
        options_layout.addLayout(self.specs_layout)  # Add the specs layout to the options layout

        # Connect the signal to update the GPU specs when a different GPU is selected
        self.gpu_drop_down.currentIndexChanged.connect(self.update_gpu_specs)

        self.parent.addDetail(self.layout, option_group, 20, bold=True)
        self.update_gpu_specs()  # Display the initial GPU specs
        self.create_cloud_option()

        self.deploy = QPushButton('Deploy')
        self.deploy.clicked.connect(self.on_deploy_clicked)
        self.deploy.setMaximumWidth(350)
        self.parent.addDetail(self.layout, self.deploy, 16, bold=True)

    def update_gpu_specs(self):
        # Clear the previous specs
        while self.specs_layout.count():
            child = self.specs_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get the current GPU and its specs
        self.selected_gpu = self.gpu_drop_down.currentText()
        temp_dict = GPU_DICT.get(self.selected_gpu, {})  # Use an empty dict as a default to prevent KeyError

        # Define labels and values to use
        labels_values_to_use = {
            'Memory VRAM': 'memoryInGb',
            'Max Count': 'maxGpuCount',
            'Secure Cloud Price ($)': 'securePrice',
            'Community Cloud Price ($)': 'communityPrice'
        }
        # Add the specs to the specs_layout
        for label, value in labels_values_to_use.items():
            self.parent.addDetail(self.specs_layout, QLabel(f"{label}: {temp_dict.get(value, 'N/A')}"), 14)

    def create_cloud_option(self):
        cloud_layout = QHBoxLayout()
        self.community_cloud_radio = QRadioButton("Community Cloud")
        self.secure_cloud_radio = QRadioButton("Secure Cloud")
        self.parent.addDetail(cloud_layout, self.community_cloud_radio, 16)
        self.parent.addDetail(cloud_layout, self.secure_cloud_radio, 16)
        cloud_layout.addWidget(self.secure_cloud_radio)
        self.layout.addLayout(cloud_layout)  # Add this layout to the main layout
        # Set Community Cloud as the default selected option
        self.community_cloud_radio.setChecked(True)

    @staticmethod
    def get_template_id():
        myself = json.loads(api.get_myself().text)
        for pod in myself["data"]["myself"]["podTemplates"]:
            if pod["name"] == "Easy miner subnet 25":
                return pod["id"]

    def create_pod(self, template_id, attempts=0, error_message=None):
        if attempts > 3 or not template_id:
            QMessageBox.warning(self, "Warning", error_message)
            self.deploy.setEnabled(True)
            return
        pod_config = f"""
               countryCode: "{COUNTRY_CODE}",
               gpuCount: 1,
               volumeInGb: {PERSISTENT_DISK_SIZE_GB},
               containerDiskInGb: {OS_DISK_SIZE_GB},
               gpuTypeId: "{self.selected_gpu}",
               cloudType: {self.cloud_option.upper()},
               supportPublicIp: true,
               name: "subnet-{self.parent.net_id}"
               templateId: "{template_id}",
               dockerArgs: "",
               volumeMountPath: "/workspace",
           """

        response = api.create_on_demand_pod(pod_config)
        resp_json = response.json()
        if response.status_code == 200:
            if 'errors' in resp_json:
                for error in resp_json['errors']:
                    if error['message'] == 'There are no longer any instances available with the requested specifications. Please refresh and try again.':
                        error_message = 'No resources currently available.'
                        print(error_message)
                        time.sleep(5)
                        return self.create_pod(template_id, attempts + 1, error_message)
                    elif error['message'] == 'There are no longer any instances available with enough disk space.':
                        error_message = 'No instances with enough disk space available.'
                        print(error_message)
                        time.sleep(5)
                        return self.create_pod(template_id, attempts + 1, error_message)
                    else:
                        QMessageBox.warning(self, "Warning", error['message'])
                        print('ERROR: ' + error['message'])
                        return None
            else:
                print(json.dumps(resp_json, indent=4, default=str))

    def create_template(self):
        self.cloud_option = "Community" if self.community_cloud_radio.isChecked() else "Secure"
        template_id = self.get_template_id()
        if template_id:
            return template_id
        mnemonic = get_secret_hotkey(self.parent.wallet_path)
        template_query = f"""
                    containerDiskInGb: {OS_DISK_SIZE_GB},
                    dockerArgs: "",
                    env: [
                      {{
                        key: "WAND_API_KEY",
                        value: "8ca0b4aabb043cc14ebd4aaed118bc5ce0277811"
                      }},
                      {{ key: "NET_UID", value: "25" }},
                      {{ key: "NETWORK", value: "test" }},
                      {{ key: "WALLET", value: "{self.parent.wallet_name}" }},
                      {{ key: "HOTKEY", value: "hotkey" }},
                      {{ key: "AXON_PORT", value: "21077" }},
                      {{ key: "DHT_PORT", value: "21078" }},
                      {{
                        key: "MNEMONIC"
                        value: "{mnemonic}"
                      }},
                      {{ key: "MINER_TYPE", value: "{self.parent.miner_type.value}" }}
                    ],
                    imageName: "squirre11/subnet-25:latest",
                    name: "Easy miner subnet 25",
                    ports: "21077/tcp, 21078/tcp",
                    readme: "## Its easy miner template, nothing special!",
                    volumeInGb: {PERSISTENT_DISK_SIZE_GB},
                    volumeMountPath: "/workspace"
                """
        resp = api.create_template(template_query).json()
        return resp.get('data', {}).get('saveTemplate', {}).get('id', '')

    def on_deploy_clicked(self):
        self.deploy.setEnabled(False)
        QMessageBox.information(self, "Deploying", "Deploying the miner, press OK to continue")
        template_id = self.create_template()
        pod_id = self.create_pod(template_id)
        if not pod_id:
            return
        # self.parent.show_miner_options_page()
