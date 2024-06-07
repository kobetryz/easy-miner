import base64
import json
import logging
import os
import re
from datetime import datetime
from netrc import netrc

import pandas as pd
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QLineEdit
from dotenv import load_dotenv, set_key, get_key
import requests
from ansible.parsing.vault import AnsibleVaultError
from ansible_vault import Vault
from bittensor import keyfile_data_is_encrypted_nacl, keyfile_data_is_encrypted_ansible, \
    keyfile_data_is_encrypted_legacy
from bittensor.keyfile import NACL_SALT
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from nacl import pwhash, secret

import config


load_dotenv()


def get_secret_coldkey(wallet_path: str):
    try:
        with open(wallet_path + "/coldkey") as f:
            return json.loads(f.read()).get("secretPhrase")
    except (FileNotFoundError, json.JSONDecodeError, IndexError, UnicodeDecodeError) as e:
        return None


def get_secret_hotkey(wallet_path: str):
    hotkey_path = wallet_path + "/hotkeys"
    try:
        files = os.listdir(hotkey_path)
        if files:
            first_file = files[0]
            with open(os.path.join(hotkey_path, first_file)) as f:
                return json.loads(f.read()).get("secretPhrase")
    except (FileNotFoundError, json.JSONDecodeError, IndexError, UnicodeDecodeError) as e:
        print("No hotkey found: ", e)
        return None


def get_earnings_by_date_range(log_file):
    earnings_data = []
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - INFO -  Balance - Start: (\d+)')

    with open(log_file, 'r') as f:
        log_entries = f.readlines()

    for entry in log_entries:
        match = date_pattern.search(entry)
        if match:
            entry_date = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
            earnings = int(match.group(2))

            # Append the date and earnings to the list
            earnings_data.append((entry_date, earnings))
    earnings_data = pd.DataFrame(earnings_data)
    earnings_data.columns = ['date', 'balance']
    earnings_data = earnings_data.groupby(earnings_data['date'].dt.date).balance.max().reset_index()

    return earnings_data


def get_total_mining(log_file):
    mining_time = []
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - INFO -  Activity: Mining Time - (\d+)')
    with open(log_file, 'r') as f:
        log_entries = f.readlines()
    for entry in log_entries:
        match = date_pattern.search(entry)
        if match:
            entry_date = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
            m_time = int(match.group(2))
            mining_time.append((entry_date, m_time))
    mining_time_data = pd.DataFrame(mining_time)
    mining_time_data.columns = ['date', 'time(s)']
    mining_time_data = mining_time_data.groupby(mining_time_data['date'].dt.date)['time(s)'].sum().reset_index()

    return mining_time_data


def get_public_ip():
    # Use a service that returns your public IP address in plain text
    response = requests.get('https://httpbin.org/ip')
    public_ip = response.json()['origin']
    return public_ip


def configure_logger_data(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler that logs to the file without rotation
    file_handler = logging.FileHandler(log_file)
    # You can configure a formatter if needed
    formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


def get_tao_price():
    # Connect to taostats
    url = "https://taostats.io/data.json"
    response = requests.get(url)
    taostats = json.loads(response.content)
    return float(taostats[0]['price'])


def get_value_from_env(key):
    return get_key(".env", key)


def save_value_to_env(key, value):
    set_key('.env', key, value)


def getLocalWandbApiKey():
    path = os.path.join(os.path.expanduser('~'), ".netrc")
    if not os.path.exists(path):
        return
    config = netrc(path)
    wandb_config = config.hosts.get("api.wandb.ai")
    if wandb_config:
        return wandb_config[2]


def get_minner_version(subnet_id):
    if subnet_id == 25:
        dest_path = "DistributedTraining/template/__init__.py"
    elif subnet_id == 1:
        dest_path = "prompting/prompting/__init__.py"
    elif subnet_id == 13:
        dest_path = "data-universe/neurons/__init__.py"
    elif subnet_id == 20:
        dest_path = "bitagent_subnet/bitagent/validator/__init__.py"
    elif subnet_id == 27:
        dest_path = "compute-subnet/compute/__init__.py"
    elif subnet_id == 4:
        dest_path = "targon/targon/__init__.py"
    elif subnet_id == 5:
        dest_path = "openkaito/openkaito/__init__.py"
    elif subnet_id == 16:
        dest_path = "BitAds.ai/template/__init__.py"
    elif subnet_id == 120:
        dest_path = "BitAds.ai/template/__init__.py"
    else:
        return None

    with open(dest_path, 'r') as file:
        for line in file:
            if line.startswith("__version__"):
                # Extract the version string
                return line.split('=')[-1].replace('"', '').strip()
    return "Version not found."


def logger_wrapper(target, end="\n", limits=['[0m ', '| ']):
    """
    Wraps a logging function to add timestamp and custom formatting.

    Parameters:
    - target: A function that takes a single string argument. This function will be called with the formatted log message.
    - end: A string that will be appended to the end of each log message. Defaults to a newline character.
    - limits: A list of strings that act as delimiters for filtering out parts of the log message. Everything before the last occurrence of each delimiter in a line will be removed.

    Returns:
    A function that takes a single string argument (the log message), formats it, and passes it to the target function.
     """
    def log(text):
        for line in text.split("\n"):
            line = line + end
            for limit in limits:
                index = line.rfind(limit)
                if index != -1:
                    line = line[index + len(limit):]
            if line:
                target(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {line}')
    return log


def get_running_args(sub_id, network, miner_type, wallet_name, hotkey, ip):
    base_args = ["-u", f"{miner_type.value}.py", "--wallet.name", f"{wallet_name}", "--wallet.hotkey", f"{hotkey}"]
    paths = {
        25: "neurons",
        1: ("neurons/miners/huggingface" if miner_type == config.MinerType.MINER else "neurons"),
        13: "neurons",
        20: "neurons",
        27: "neurons",
        15: "neurons",
        76: "neurons",
        4: "neurons",
        5: "neurons",
        16: "neurons",
        120: "neurons",
        61: ("neurons/miners/huggingface" if miner_type == config.MinerType.MINER else "neurons"),
        100: "neurons",
    }
    extras = {
        25: ["--netuid", f"{sub_id}", "--subtensor.network", f"{network}", "--logging.debug",
             "--axon.external_ip", f"{ip}", "--axon.port", "8090", "--axon.ip", f"{ip}", "--axon.external_port", "8090",
             "--flask.host_port", "8800", "--flask.host_address", f"0.0.0.0"],
        1: ["--netuid", f"{sub_id}", "--subtensor.network", f"{network}", "--logging.debug"] + (["--neuron.device", "cuda"] if miner_type != config.MinerType.MINER else []),
        20: ["--netuid", f"{sub_id}", "--subtensor.network", f"{network}", "--axon.port", "8090"],
        76: ["--netuid", f"{sub_id}", "--subtensor.network", f"{network}", "--axon.port", "8090"],
        27: ["--netuid", f"{sub_id}", "--subtensor.network", f"{network}", "--logging.debug"],
        61: ["--neuron.model_id casperhansen/llama-3-70b-instruct-awq", "--neuron.load_in_4bit", "True", "--axon.port", "21988"]

    }

    if sub_id in paths:
        base_args[1] = f"{paths[sub_id]}/{base_args[1]}"
        if sub_id in extras:
            return base_args + extras[sub_id]
        return base_args
    return None


def decript_keyfile(self, keyfile_data):
    while True:
        password, ok = QInputDialog.getText(
            self, 'Hotkey Password', 'Please enter your password to decrypt your hotkey', QLineEdit.Password
        )
        if not ok:
            break
        # NaCl SecretBox decrypt.
        if keyfile_data_is_encrypted_nacl(keyfile_data):
            password = bytes(password, "utf-8")
            kdf = pwhash.argon2i.kdf
            key = kdf(
                secret.SecretBox.KEY_SIZE,
                password,
                NACL_SALT,
                opslimit=pwhash.argon2i.OPSLIMIT_SENSITIVE,
                memlimit=pwhash.argon2i.MEMLIMIT_SENSITIVE,
            )
            box = secret.SecretBox(key)
            try:
                return box.decrypt(keyfile_data[len("$NACL"):])
            except Exception:
                QMessageBox.warning(self, "Error", "Invalid password", QMessageBox.Ok)
                continue

        # Ansible decrypt.
        elif keyfile_data_is_encrypted_ansible(keyfile_data):
            vault = Vault(password)
            try:
                return vault.load(keyfile_data)
            except AnsibleVaultError:
                QMessageBox.warning(self, "Error", "Invalid password", QMessageBox.Ok)
                continue
        # Legacy decrypt.
        elif keyfile_data_is_encrypted_legacy(keyfile_data):
            __SALT = (
                b"Iguesscyborgslikemyselfhaveatendencytobeparanoidaboutourorigins"
            )
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                salt=__SALT,
                length=32,
                iterations=10000000,
                backend=default_backend(),
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            cipher_suite = Fernet(key)
            try:
                return cipher_suite.decrypt(keyfile_data)
            except Exception:
                QMessageBox.warning(self, "Error", "Invalid password", QMessageBox.Ok)
                continue
        # Unknown.
        else:
            QMessageBox.warning(self, "Error", "Unknown keyfile encryption type", QMessageBox.Ok)
            return
