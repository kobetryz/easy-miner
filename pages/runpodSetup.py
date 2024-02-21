from runpod_api.runpod import GPU_DICT, GPU_LIST_TO_USE
from PyQt5.QtWidgets import QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel, QRadioButton
from PyQt5.QtCore import Qt


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
        header.setAlignment(Qt.AlignLeft| Qt.AlignTop)
        self.parent.addDetail(self.layout, header, 20, bold = True)

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

        self.parent.addDetail(self.layout, option_group, 20, bold = True)
        self.update_gpu_specs()  # Display the initial GPU specs
        self.create_cloud_option()

        self.deploy = QPushButton('Deploy')
        self.deploy.setMaximumWidth(350)
        self.parent.addDetail(self.layout, self.deploy, 16, bold = True)

    def update_gpu_specs(self):
        # Clear the previous specs
        while self.specs_layout.count():
            child = self.specs_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get the current GPU and its specs
        current_gpu = self.gpu_drop_down.currentText()
        temp_dict = GPU_DICT.get(current_gpu, {})  # Use an empty dict as a default to prevent KeyError

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

    def on_deploy_clicked(self):
        # Determine which cloud option is selected
        cloud_option = "Community" if self.community_cloud_radio.isChecked() else "Secure"
        print(f"Deploying on {cloud_option} Cloud")  # Example action, replace with your deployment logic
        # Your additional logic for deployment based on the selected cloud option

