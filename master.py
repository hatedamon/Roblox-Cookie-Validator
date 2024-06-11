import os
import sqlite3
import asyncio
import requests

from aiohttp import ClientSession
from colorama import Fore, Style, init
from pathlib import Path

inputdir = "input"
outputdir = "output"
datab = "./data/cookies.db"

init(autoreset=True)

async def main():
    print(Fore.WHITE + 'developed by @HATEDAMON')

    save_to_db = prompt_for_db_usage()
    setup_directories()

    if save_to_db:
        setup_database()

    files = list(Path(inputdir).glob("*.txt"))
    tf = len(files)

    async with ClientSession() as session:
        tasks = [process(session, file, save_to_db) for file in files]
        await asyncio.gather(*tasks)

    print(f"{Fore.GREEN}all files processed{Style.RESET_ALL}")

def prompt_for_db_usage():
    while True:
        user_input = input("would you like to save info into a database? (yes/no): ").strip().lower()
        if user_input in ['yes', 'no']:
            return user_input == 'yes'
        else:
            print("retard...")

def setup_directories():
    os.makedirs(outputdir, exist_ok=True)
    print(f"{Fore.CYAN}input dir: {inputdir}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}output dir: {outputdir}{Style.RESET_ALL}")

def setup_database():
    os.makedirs(os.path.dirname(datab), exist_ok=True)
    with sqlite3.connect(datab) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cookies (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT,
                            username TEXT,
                            robux_balance TEXT,
                            is_premium TEXT,
                            location TEXT,
                            cookie TEXT UNIQUE,
                            status TEXT)''')
        conn.commit()
    print(f"{Fore.MAGENTA}db setup completed: {datab}{Style.RESET_ALL}")

async def process(session, file_path, save_to_db):
    with file_path.open('r') as file:
        tasks = [validate(session, line.strip(), save_to_db, idx) for idx, line in enumerate(file, start=1) if line.strip()]
        await asyncio.gather(*tasks)

async def validate(session, cookie, save_to_db, linenumber):
    try:
        async with session.get("https://www.roblox.com/mobileapi/userinfo", cookies={".ROBLOSECURITY": cookie}) as response:
            if response.status == 200:
                user_data = await response.json()
                user_data['IsPremium'] = bool(user_data.get('IsPremium', 0))

                if save_to_db:
                    await save_to_db_func(cookie, user_data)
                else:
                    await save_to_txt(cookie, "valid")

            elif response.status == 429:
                print(f"{Fore.YELLOW}rate limit exceeded, retrying in 5s...{Style.RESET_ALL}")
                await asyncio.sleep(5)
                await validate(session, cookie, save_to_db, linenumber)

            else:
                print(f"{Fore.RED}cookie {linenumber} is invalid, next{Style.RESET_ALL}")
                await save_to_txt(cookie, "expired")

    except Exception:
        print(f"{Fore.RED}cookie {linenumber} is invalid, next{Style.RESET_ALL}")
        await save_to_txt(cookie, "expired")

async def save_to_db_func(cookie, user_data):
    location_response = requests.get("https://auth.roblox.com/v1/auth/metadata", cookies={".ROBLOSECURITY": cookie})
    location = location_response.headers.get("x-roblox-edge", "unknown") if location_response.status_code == 200 else "unknown"

    with sqlite3.connect(datab) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO cookies (user_id, username, robux_balance, is_premium, location, cookie, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_data["UserID"], user_data["UserName"], user_data["RobuxBalance"], user_data["IsPremium"], location, cookie, "valid"))
        conn.commit()
    print(f"{Fore.MAGENTA}data saved to db for cookie: {user_data['UserName']}{Style.RESET_ALL}")

async def save_to_txt(cookie, status):
    output_file = Path(outputdir) / f"{status}.txt"
    with output_file.open('a') as file:
        file.write(cookie + "\n")

if __name__ == "__main__":
    asyncio.run(main())