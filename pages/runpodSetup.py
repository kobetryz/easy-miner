import json
import time
from functools import partial

from config import COUNTRY_CODE, PERSISTENT_DISK_SIZE_GB, OS_DISK_SIZE_GB, MAX_INSTANCE_FOR_SUBNET
from runpod_api.runpod import GPU_DICT, GPU_LIST_TO_USE, api
from PyQt5.QtWidgets import QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel, \
    QRadioButton, QSpinBox, QTextEdit, QSizePolicy, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from utils import get_secret_hotkey, get_secret_coldkey, getLocalWandbApiKey, logger_wrapper


class PodCreatorThread(QThread):
    pod_created = pyqtSignal(str)
    creating_logs = pyqtSignal(str)

    def __init__(self, template_id, persistent_disk_size_gb, os_disk_size_gb, country_code, parent):
        super().__init__()
        self.parent = parent
        self.template_id = template_id
        self.persistent_disk_size_gb = persistent_disk_size_gb
        self.os_disk_size_gb = os_disk_size_gb
        self.country_code = country_code

    def create_pod(self, template_id, persistent_disk_size_gb, os_disk_size_gb, country_code, attempts=0):
        if attempts >= 3 or not template_id:
            self.creating_logs.emit("You may change params and try again")
            self.parent.deploy.setEnabled(True)
            return
        self.creating_logs.emit(f"Started creating pod, attempt №{attempts + 1}")
        pod_config = f"""
               gpuCount: 1,
               volumeInGb: {persistent_disk_size_gb},
               containerDiskInGb: {os_disk_size_gb},
               gpuTypeId: "{GPU_DICT[self.parent.selected_gpu]["id"]}",
               cloudType: {self.parent.cloud_option.upper()},
               supportPublicIp: true,
               name: "subnet-{self.parent.parent.net_id}"
               templateId: "{template_id}",
               dockerArgs: "",
               volumeMountPath: "/workspace",
           """
        if country_code != "Any":
            pod_config += f"""countryCode: "{country_code}",\n"""

        response = api.create_on_demand_pod(pod_config)
        resp_json = response.json()
        if response.status_code == 200:
            if 'errors' in resp_json:
                for error in resp_json['errors']:
                    if error['message'] == ('There are no longer any instances available with the requested '
                                            'specifications. Please refresh and try again.'):
                        error_message = 'No resources currently available.'
                        self.creating_logs.emit(error_message)
                        time.sleep(5)
                        return self.create_pod(
                            template_id=template_id,
                            attempts=attempts + 1,
                            persistent_disk_size_gb=persistent_disk_size_gb,
                            os_disk_size_gb=os_disk_size_gb,
                            country_code=country_code
                        )
                    elif error['message'] == 'There are no longer any instances available with enough disk space.':
                        error_message = 'No instances with enough disk space available.'
                        self.creating_logs.emit(error_message)
                        time.sleep(5)
                        return self.create_pod(
                            template_id=template_id,
                            attempts=attempts + 1,
                            persistent_disk_size_gb=persistent_disk_size_gb,
                            os_disk_size_gb=os_disk_size_gb,
                            country_code=country_code
                        )
                    else:
                        self.creating_logs.emit('Error from runpod: ' + error['message'])
                        self.pod_not_created.emit()
            self.creating_logs.emit("Pod created!")
            self.pod_created.emit(resp_json["data"]["podFindAndDeployOnDemand"]["id"])

    def run(self):
        self.create_pod(self.template_id, self.persistent_disk_size_gb, self.os_disk_size_gb, self.country_code)


class PodCheckerThread(QThread):
    pod_available = pyqtSignal()

    def __init__(self, parent, pod_id):
        super().__init__()
        self.parent = parent
        self.pod_id = pod_id

    def check_availability(self):
        response = api.get_pod(self.pod_id)
        if response.json()["data"]["pod"]["runtime"]:
            self.pod_available.emit()

    def run(self):
        while not self.isInterruptionRequested():
            self.check_availability()
            time.sleep(1)


class RunpodSetupPage(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.setLayout(self.layout)
        self.instead_machine_options = kwargs.get("instead_machine_options", self.parent.show_machine_options_page)

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.create_header()

        self.options_widget = QWidget()
        self.main_hori_layout = QHBoxLayout(self.options_widget)

        option_group = self.create_gpu_options()
        parameters_group = self.createInputs()

        self.parent.addDetail(self.main_hori_layout, option_group, 20, bold=True)
        self.parent.addDetail(self.main_hori_layout, parameters_group, 14, alignment=Qt.AlignBottom)

        self.create_wallet_options()

        self.deploy = QPushButton('Deploy')
        self.deploy.clicked.connect(self.on_deploy_clicked)
        self.parent.addDetail(self.layout, self.deploy, 16, bold=True)

        self.output_area = QTextEdit(self)
        self.output_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log = logger_wrapper(self.output_area.insertPlainText)
        self.layout.addWidget(self.output_area)

        self.createFooter()

        self.set_local_params()

    def createFooter(self):
        f_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(partial(self.parent.show_start_page, page_to_delete=self))
        self.continue_button = QPushButton("Continue", self)
        self.continue_button.setEnabled(False)
        self.parent.addDetail(f_layout, previous_button, 12)
        self.parent.addDetail(f_layout, self.continue_button, 12)
        self.layout.addLayout(f_layout)

    def createInputs(self):
        input_group = QGroupBox("Parameters", self)
        input_group.setFixedHeight(260)
        inputs_layout = QVBoxLayout(input_group)

        os_disk_layout = QHBoxLayout()
        self.os_disk_field = QSpinBox(self)
        self.os_disk_field.setValue(OS_DISK_SIZE_GB)
        os_disk_layout.addWidget(QLabel("OS DISK SIZE (GB):", self))
        os_disk_layout.addWidget(self.os_disk_field)

        persistent_disk_layout = QHBoxLayout()
        self.persistent_disk_field = QSpinBox(self)
        self.persistent_disk_field.setValue(PERSISTENT_DISK_SIZE_GB)
        persistent_disk_layout.addWidget(QLabel("PERSISTENT DISK SIZE(GB):", self))
        persistent_disk_layout.addWidget(self.persistent_disk_field)

        country_code_layout = QHBoxLayout()
        self.country_code_dropdown = QComboBox(self)
        self.country_code_dropdown.addItem("Any")
        self.country_code_dropdown.addItems(COUNTRY_CODE.split(","))
        country_code_layout.addWidget(QLabel("COUNTRY CODE:", self))
        country_code_layout.addWidget(self.country_code_dropdown)

        wandb_api_key_layout = QHBoxLayout()
        self.wandb_api_key_field = QLineEdit(self)

        wandb_api_key_layout.addWidget(QLabel("WANDB API KEY:", self))
        wandb_api_key_layout.addWidget(self.wandb_api_key_field)

        inputs_layout.addLayout(os_disk_layout)
        inputs_layout.addLayout(persistent_disk_layout)
        inputs_layout.addLayout(country_code_layout)
        inputs_layout.addLayout(wandb_api_key_layout)

        return input_group

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

        self.layout.addWidget(self.options_widget)
        self.update_gpu_specs()  # Display the initial GPU specs
        self.create_cloud_option(parent=options_layout)

        return option_group

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

    def create_cloud_option(self, parent):
        cloud_layout = QHBoxLayout()
        cloud_layout.setAlignment(Qt.AlignLeft)
        self.community_cloud_radio = QRadioButton("Community Cloud", self)
        self.secure_cloud_radio = QRadioButton("Secure Cloud", self)

        self.parent.addDetail(cloud_layout, self.community_cloud_radio, 16)
        self.parent.addDetail(cloud_layout, self.secure_cloud_radio, 16)

        parent.addLayout(cloud_layout)  # Add this layout to the main layout
        # Set Community Cloud as the default selected option
        self.community_cloud_radio.setChecked(True)

    def create_wallet_options(self):
        wallet_group = QGroupBox("Parameters", self)
        wallet_layout = QVBoxLayout(wallet_group)

        mnemonic_hotkey_layout = QHBoxLayout()
        self.mnemonic_hotkey_field = QLineEdit()

        mnemonic_hotkey_layout.addWidget(QLabel("MNEMONIC HOTKEY:", self))
        mnemonic_hotkey_layout.addWidget(self.mnemonic_hotkey_field)

        mnemonic_coldkey_layout = QHBoxLayout()
        self.mnemonic_coldkey_field = QLineEdit()

        mnemonic_coldkey_layout.addWidget(QLabel("MNEMONIC COLDKEY:", self))
        mnemonic_coldkey_layout.addWidget(self.mnemonic_coldkey_field)

        wallet_layout.addLayout(mnemonic_hotkey_layout)
        wallet_layout.addLayout(mnemonic_coldkey_layout)

        self.layout.addWidget(wallet_group)

    def set_local_params(self):
        if local_hotkey := get_secret_hotkey(self.parent.wallet_path):
            self.mnemonic_hotkey_field.setText(local_hotkey)
        if local_coldkey := get_secret_coldkey(self.parent.wallet_path):
            self.mnemonic_coldkey_field.setText(local_coldkey)
        if local_wandb_api_key := getLocalWandbApiKey():
            self.wandb_api_key_field.setText(local_wandb_api_key)

    @staticmethod
    def get_template_id():
        myself = json.loads(api.get_myself().text)
        print(myself)
        for pod in myself["data"]["myself"]["podTemplates"]:
            if pod["name"] == "Easy miner subnet 25":
                return pod["id"]

    def create_template(self):
        self.cloud_option = "Community" if self.community_cloud_radio.isChecked() else "Secure"
        template_id = self.get_template_id()
        if template_id:
            self.log("Template already exist, skipping...")
            return template_id
        self.log("Template already not exist, creating...")
        template_query = f"""
                    containerDiskInGb: {OS_DISK_SIZE_GB},
                    dockerArgs: "",
                    env: [],
                    imageName: "squirre11/miner-server:latest",
                    name: "Easy miner subnet 25",
                    ports: "21077/tcp,21078/tcp,8000/http",
                    readme: "## Its easy miner template, nothing special!",
                    volumeInGb: {PERSISTENT_DISK_SIZE_GB},
                    volumeMountPath: "/workspace"
                """
        resp = api.create_template(template_query).json()
        self.log("Template created!")
        return resp.get('data', {}).get('saveTemplate', {}).get('id', '')

    def on_deploy_clicked(self):
        if self.is_limit_per_subnet_achived():
            result = QMessageBox.question(self, "Warning", "Limit for max instances per subnet have achieved\n"
                                                           "Do you want to return to miner options to change subnet?")
            if result == QMessageBox.Yes:
                self.parent.show_miner_options_page(instead_machine_options=self.instead_machine_options)
            return
        self.parent.wandb_api_key = self.wandb_api_key_field.text()
        self.parent.mnemonic_hotkey = self.mnemonic_hotkey_field.text()
        self.parent.mnemonic_coldkey = self.mnemonic_coldkey_field.text()

        if not self.parent.mnemonic_hotkey or not self.parent.mnemonic_coldkey:
            self.log("Hotkey or coldkey are not filled, try again")
            return
        if (length := len(self.parent.wandb_api_key)) != 40:
            self.log(f"WandDb API key must have 40 chars, yours have {length}, try again")
            return
        self.deploy.setEnabled(False)
        os_disk_size_gb = self.os_disk_field.value()
        persistent_disk_size_gb = self.persistent_disk_field.value()
        country_code = self.country_code_dropdown.currentText()
        self.log("Started deploying the miner")
        template_id = self.create_template()

        self.pod_creator_thread = PodCreatorThread(
            template_id, os_disk_size_gb, persistent_disk_size_gb, country_code, self
        )
        self.pod_creator_thread.pod_created.connect(self.on_pod_created)
        self.pod_creator_thread.creating_logs.connect(self.log)
        self.pod_creator_thread.start()

    def on_pod_created(self, pod_id):
        self.pod_id = pod_id
        if not self.pod_id:
            return
        self.continue_button.clicked.connect(self.on_continue_clicked)

        self.pod_checker_thread = PodCheckerThread(self, pod_id=self.pod_id)
        self.pod_checker_thread.start()
        self.log("Waiting while pod will be available")
        self.pod_checker_thread.pod_available.connect(self.on_pod_available)

    def on_pod_available(self):
        self.pod_checker_thread.requestInterruption()
        self.continue_button.setEnabled(True)
        self.log("Pod available, you can go to dashboard!")

    def on_continue_clicked(self):
        self.parent.show_runpod_dashboard_page(self.pod_id, page_to_delete=self)

    def is_limit_per_subnet_achived(self):
        pod_name = f"subnet-{self.parent.net_id}"

        pods = api.get_pods().json().get("data", {}).get("myself", {}).get("pods", [])
        count = 0
        for pod in pods:
            if pod["name"] == pod_name:
                count += 1
        return count >= MAX_INSTANCE_FOR_SUBNET
