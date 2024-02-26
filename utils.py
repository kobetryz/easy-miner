import json
import logging
import os
import re
from datetime import datetime

import pandas as pd
from hivemind import DHT
from dotenv import load_dotenv
import requests


def get_secret_coldkey(wallet_path: str):
    try:
        with open(wallet_path + "/coldkey") as f:
            return json.loads(f.read()).get("secretPhrase")
    except FileNotFoundError:
        return None


def get_secret_hotkey(wallet_path: str):
    hotkey_path = wallet_path + "/hotkeys"
    try:
        files = os.listdir(hotkey_path)
        if files:
            first_file = files[0]
            with open(os.path.join(hotkey_path, first_file)) as f:
                return json.loads(f.read()).get("secretPhrase")
    except (FileNotFoundError, json.JSONDecodeError, IndexError) as e:
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


def get_initial_num_pers():
    open_port = 8000
    dht = DHT(host_maddrs=[f"/ip4/0.0.0.0/tcp/{open_port}"], start=True)
    return str(dht.get_visible_maddrs()[0])


def get_tao_price():
    # Connect to taostats
    url = "https://taostats.io/data.json"
    response = requests.get(url)
    taostats = json.loads(response.content)
    return float(taostats[0]['price'])


def get_runpod_api_key():
    load_dotenv()  # Load environment variables from .env file
    return os.getenv("RUNPOD_API_KEY")


def save_runpod_api_key(api_key):
    with open(".env", "a") as env_file:
        env_file.write(f"RUNPOD_API_KEY=\"{api_key}\"\n")
