import bittensor
import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QTextEdit, QMessageBox, QStackedWidget, QHBoxLayout, QFileDialog, 
    QGroupBox, QStatusBar, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QColor, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl


from pages.subnet import SelectSubnetPage
from pages.neuron import SelectNeuronPage
from pages.dashboard import SelectDashboardPage


class MiningWizard(QMainWindow):
    def __init__(self):
        super().__init__()

        ##
        self.subnet = None
        self.neuron = None
        
        self.setWindowTitle("Plug and play miner")
        # self.setStyleSheet(f"background-image: url('cyberpunk_background.png'); background-position: center; background-repeat: no-repeat; background-attachment: fixed;")
        # self.setStyleSheet("{background: rgba(0, 0, 0, 0.3); width: 1px; }")
        self.setGeometry(100, 100, 800, 600)

        # # Set background image
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)


        # Initialize pages
        self.start_page = StartPage(self)
        self.mining_page = MiningPage(self)
        self.create_wallet_page = AddWalletPage(self)
        self.get_wallet_page = GetWalletPage(self)
        self.select_subnet_page = SelectSubnetPage(self)
        self.select_neuron_page = SelectNeuronPage(self)
        self.dashboard_page = SelectDashboardPage(self)

    

        # Adding pages to the stack
        self.central_widget.addWidget(self.start_page)
        self.central_widget.addWidget(self.mining_page)
        self.central_widget.addWidget(self.create_wallet_page)
        self.central_widget.addWidget(self.get_wallet_page)
        self.central_widget.addWidget(self.select_subnet_page)
        self.central_widget.addWidget(self.select_neuron_page)
        self.central_widget.addWidget(self.dashboard_page)

    def show_start_page(self):
        self.central_widget.setCurrentWidget(self.start_page)

    def show_mining_page(self):
        self.central_widget.setCurrentWidget(self.mining_page)

    def show_create_wallet_page(self):
        self.central_widget.setCurrentWidget(self.create_wallet_page)

    def show_get_wallet_page(self):
        self.central_widget.setCurrentWidget(self.get_wallet_page)

    def show_select_subnet_page(self):
        self.central_widget.setCurrentWidget(self.select_subnet_page)

    def show_select_neuron_page(self):
        self.central_widget.setCurrentWidget(self.select_neuron_page)

    def show_dashboard_page(self):
        self.central_widget.setCurrentWidget(self.dashboard_page)

class StartPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Add a cyberpunk style
        self.setStyleSheet("""
             QPushButton {
                font-family: 'Georgia'; 
                font-weight: bold;
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 10px;      
                min-height: 30px;
                font-size: 16px;
        }
            QPushButton:hover {
              background-color: #333";
            }
        """)
        

        # Header
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 20, QFont.Bold))
        
        header_group.setStyleSheet("font-family: 'Georgia'; \
                                   font-weight: bold;\
                                   color: black; \
                                   padding: 10px;  \
                                   border: None; \
                                   # 1px solid #3498db; \
                                   margin-top: 22px; margin-bottom: 20px;")
       
        # header_group.setAlignment(Qt.AlignCenter) 
        header_layout = QHBoxLayout(header_group)
        welcome_message = QLabel("Making Mining Accessible to All")
        welcome_message.setFont(QFont("Georgia", 42, QFont.Bold, italic=True))
        header_layout.addWidget(welcome_message)

        layout.addWidget(header_group)

        # Mining options
        options_group = QGroupBox()
        options_group.setFont(QFont("Georgia", 16, QFont.Bold))
        options_layout = QVBoxLayout(options_group)
        
        # Use new wallet
        new_wallet_button = QPushButton("Create New Wallet and Mine", self) 
        new_wallet_button.clicked.connect(parent.show_create_wallet_page)
        options_layout.addWidget(new_wallet_button)

        # Using existing Wallet
        existing_wallet_button = QPushButton("Mine to Existing Wallet", self)
        existing_wallet_button.clicked.connect(parent.show_get_wallet_page)
        options_layout.addWidget(existing_wallet_button)

        # to dashboard
        view_dashboard_button = QPushButton("View Dashboard", self)
        view_dashboard_button.clicked.connect(parent.show_dashboard_page)
        options_layout.addWidget(view_dashboard_button)


        layout.addWidget(options_group)
        options_group.setFixedSize(800,200)
        
        # footer group
        footer_group = QGroupBox()
        footer_layout = QHBoxLayout(footer_group)
        
        # add about page
        about_button = QPushButton("About")
        about_button.setFont(QFont("Georgia", 12))
        about_button.clicked.connect(self.open_about_url)
        footer_layout.addWidget(about_button)

        # legal
        legal_button = QPushButton("Legal and Compliance")
        legal_button.setFont(QFont("Georgia", 12))
        legal_button.clicked.connect(self.open_legal_url)
        footer_layout.addWidget(legal_button)

        # Support
        support_button = QPushButton("Support")
        support_button.setFont(QFont("Georgia", 12))
        support_button.clicked.connect(self.open_support_url)
        footer_layout.addWidget(support_button)

        # Terms
        terms_button = QPushButton("Terms of Use")
        terms_button.setFont(QFont("Georgia", 12))
        terms_button.clicked.connect(self.open_terms_url)
        footer_layout.addWidget(terms_button)
        footer_group.resize(800,10)
        layout.addWidget(footer_group)

        #  Bottom footnote
        warning_label = QLabel("Please ensure to keep the miner program running at all times.", self)
        warning_label.setFont(QFont("Georgia", 14))
        warning_label.setStyleSheet("QLabel { color : black;padding: 5px; }")   
        warning_label.setFixedSize(800, 50)     
        layout.addWidget(warning_label)
        self.setLayout(layout)

    def create_new_wallet(self):
        QMessageBox.information(self, "New Wallet", "The new wallet creation functionality is not implemented yet.")

    def open_about_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))
    
    def open_legal_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))

    def open_support_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))

    def open_terms_url(self):
        QDesktopServices.openUrl(QUrl("https://bitcurrent.net/"))

    # def show_dashboard(self):
    #     dashboard = MiningDashboard(self)
    #     dashboard.show()


class MiningPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()

        # self.setStyleSheet("""
        #     QPushButton {
        #         border: 2px solid #00ff00;
        #         border-radius: 15px;
        #         min-height: 30px;
        #         font-size: 16px;
        #     }
        #     QPushButton:hover {
        #         background-color: #005500;
        #     }
        #     QLineEdit {
        #         border: 1px solid #00ff00;
        #         border-radius: 10px;
        #         padding: 5px;
        #         color: #00ff00;
        #         background-color: #000;
        #         font-family: 'Orbitron', sans-serif;
        #     }
        #     QTextEdit {
        #         color: #00ff00;
        #         background-color: #000;
        #         font-family: 'Orbitron', sans-serif;
        #     }
                           

        # """)

        label = QLabel("Step 2: Start Mining", self)
        label.setFont(QFont("Orbitron", 16))
        layout.addWidget(label)

        label_entry = QLabel("Enter Your Bittensor Address", self)
        label_entry.setFont(QFont("Orbitron", 12))
        layout.addWidget(label_entry)

        self.entry = QLineEdit(self)
        layout.addWidget(self.entry)

        self.start_button = QPushButton("Start Mining", self)
        self.start_button.clicked.connect(self.start_mining)
        layout.addWidget(self.start_button)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        h_layout = QHBoxLayout()
        previous_button = QPushButton("Previous", self)
        previous_button.clicked.connect(parent.show_start_page)
        h_layout.addWidget(previous_button)
        
        # Spacer to push the Previous button to the left
        h_layout.addStretch()
        layout.addLayout(h_layout)

        self.setLayout(layout)

    def start_mining(self):
        address = self.entry.text()
        if address:
            self.output.append(f"Started mining to address: {address}\n")
        else:
            QMessageBox.warning(self, "Warning", "Please enter a Bittensor wallet address.")


class AddWalletPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-family: Georgia;
            }
            #     QPushButton:hover {
            #         background-color: #005500;
            #     }
        """)

        
# =====

        # Header Group with links
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QHBoxLayout(header_group)
        
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
        header_group.setFixedHeight(150)
        
        layout.addWidget(header_group)

# =====
       
        details_box = QGroupBox()
        details_layout = QVBoxLayout(details_box)
        
        label = QLabel("Wallet Details", self)
        label.setFont(QFont("Georgia", 26, QFont.Bold))
        details_layout.addWidget(label)


        # Wallet Name
        wallet_name_label = QLabel("Wallet Name:", self)
        wallet_name_label.setFont(QFont("Georgia", 16, QFont.Bold))
        details_layout.addWidget(wallet_name_label)
        self.wallet_name_input = QLineEdit(self)
        details_layout.addWidget(self.wallet_name_input)

        # Wallet Path
        wallet_path_label = QLabel("Wallet Path:", self)
        wallet_path_label.setFont(QFont("Georgia", 18))
        details_layout.addWidget(wallet_path_label)
        self.wallet_path_input = QLineEdit(self)
        self.wallet_path_input.setPlaceholderText("Select wallet path")
        self.wallet_path_input.setText(os.getcwd())
        details_layout.addWidget(self.wallet_path_input)
        browse_button = QPushButton("Browse", self)
        browse_button.setFont(QFont("Georgia", 16))
        browse_button.clicked.connect(self.browse_wallet_path)
        details_layout.addWidget(browse_button)

        

        # Other Fields (Add as necessary)
        # Example: Wallet Password
        wallet_password_label = QLabel("Wallet Password:", self)
        wallet_password_label.setFont(QFont("Georgia", 18, QFont.Bold))
        details_layout.addWidget(wallet_password_label)
        self.wallet_password_input = QLineEdit(self)
        self.wallet_password_input.setEchoMode(QLineEdit.Password)  # Hides text entry for password

        details_layout.addWidget(self.wallet_password_input)

        layout.addWidget(details_box)

        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(parent.show_start_page)
        h_layout.addWidget(previous_button)
        # Save Button
        save_button = QPushButton("Save Wallet & Mine", self)
        save_button.clicked.connect(self.save_wallet_details)
        save_button.clicked.connect(parent.show_select_subnet_page)#TODO move wallet details
        h_layout.addWidget(save_button)

        # Add more fields as needed...
        
        layout.addLayout(h_layout)

        self.setLayout(layout)

    def browse_wallet_path(self):
        # Open a QFileDialog to select the path
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        wallet_path = QFileDialog.getExistingDirectory(self, "Select Wallet Path", options=options)
        if wallet_path:
            self.wallet_path_input.setText(wallet_path)

    def save_wallet_details(self):
        # Logic to handle saving wallet details
        wallet_name = self.wallet_name_input.text()
        wallet_path = self.wallet_path_input.text()
        wallet_password = self.wallet_password_input.text()

        wallet = bittensor.wallet(name=wallet_name, path=wallet_path)

        wallet.create_new_coldkey(use_password=False)
        wallet.create_new_hotkey(use_password=False)
        # Implement the saving logic here, possibly including validation and actual saving to a file or database
        QMessageBox.information(self, "Save Wallet Details", "Wallet details saved successfully.")



class GetWalletPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Header Group with links
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QHBoxLayout(header_group)
        
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
        header_group.setFixedHeight(150)
        
        layout.addWidget(header_group)


        details_box = QGroupBox()
        details_layout = QVBoxLayout(details_box)
        
        label = QLabel("Wallet Details", self)
        label.setFont(QFont("Georgia", 26, QFont.Bold))
        details_layout.addWidget(label)


        # Wallet Name
        wallet_name_label = QLabel("Wallet Name:", self)
        wallet_name_label.setFont(QFont("Georgia", 16, QFont.Bold))
        details_layout.addWidget(wallet_name_label)
        self.wallet_name_input = QLineEdit(self)
        details_layout.addWidget(self.wallet_name_input)

        # Wallet Path
        wallet_path_label = QLabel("Wallet Path:", self)
        wallet_path_label.setFont(QFont("Georgia", 18))
        details_layout.addWidget(wallet_path_label)
        self.wallet_path_input = QLineEdit(self)
        self.wallet_path_input.setPlaceholderText("Select wallet path")
        self.wallet_path_input.setText(os.getcwd())
        details_layout.addWidget(self.wallet_path_input)
        browse_button = QPushButton("Browse", self)
        browse_button.setFont(QFont("Georgia", 16))
        browse_button.clicked.connect(self.browse_wallet_path)
        details_layout.addWidget(browse_button)

        

        # Other Fields (Add as necessary)
        # Example: Wallet Password
        wallet_password_label = QLabel("Wallet Password:", self)
        wallet_password_label.setFont(QFont("Georgia", 18, QFont.Bold))
        details_layout.addWidget(wallet_password_label)
        self.wallet_password_input = QLineEdit(self)
        self.wallet_password_input.setEchoMode(QLineEdit.Password)  # Hides text entry for password

        details_layout.addWidget(self.wallet_password_input)

        layout.addWidget(details_box)

        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(parent.show_start_page)
        h_layout.addWidget(previous_button)
        # Save Button
        save_button = QPushButton("Get Wallet & Mine", self)
        save_button.clicked.connect(self.get_wallet_details)
        save_button.clicked.connect(parent.show_select_subnet_page)#TODO move wallet details
        h_layout.addWidget(save_button)

        # Add more fields as needed...
        
        layout.addLayout(h_layout)

        self.setLayout(layout)

    def browse_wallet_path(self):
        # Open a QFileDialog to select the path
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        wallet_path = QFileDialog.getExistingDirectory(self, "Select Wallet Path", options=options)
        if wallet_path:
            self.wallet_path_input.setText(wallet_path)

    def get_wallet_details(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow::separator { background: rgba(0, 0, 0, 0.3); width: 1px; }")
    # QFontDatabase.addApplicationFont("./Orbitron/Orbitron-VariableFont_wght.ttf")  # Add the path to the Orbitron font file

    window = MiningWizard()
    window.show()
    sys.exit(app.exec_())
