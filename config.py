# import bittensor as bt
import os
import re

import pandas as pd
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


# function performs a deeper search past the bitcurrent directory 
def search_directory(start_directory, target_directory):
    current_directory = start_directory
    while current_directory:
        for root, dirs, files in os.walk(current_directory):
            if target_directory in dirs:
                found_directory_path = os.path.join(root, target_directory)
                # print(f"Found: {found_directory_path}")
                return found_directory_path  # Return or do something with the found directory path

        # Move to the parent directory
        parent_directory = os.path.dirname(current_directory)
        if parent_directory == current_directory:
            # If the parent is the same as the current, it means we are at the root and should break the loop
            break
        current_directory = parent_directory

    raise FileNotFoundError(f"Directory '{target_directory}' not found in or above '{start_directory}'")


def configure_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler that logs to the file without rotation
    file_handler = logging.FileHandler(log_file)
    # You can configure a formatter if needed
    formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

# should go to utils
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