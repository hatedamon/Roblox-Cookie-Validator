# Cookie Validator + Database for mass cookie storage

Designed to validate & process cookies, validate them and store the results in either text files or a SQL db, Can be used for large amounts of cookies, quickly.

## Features

- **Cookie Validation**: Validate cookies
- **Data Collection**: Data collection on cookies (RobuxBalance, UserID, Username, DisplayName, IsPremium?)
- **Database Integration**: Option to save valid cookie information into a SQL db

## Requirements

- Python 3.0+
- `requests` library
- `colorama` library
- `sqlite3` (built-in with Python)
- Properly formatted cookies in a text file, one per line

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/hatedamon/cookie-validator.git
    cd cookie-validator
    ```

2. Install the required Python libraries:

    ```sh
    pip install requests colorama
    ```

3. Make sure your cookies are located in the correct directory (`Data`) n are formatted correctly in `.txt` files (one cookie per line).

## Usage

1. Place your cookies in the `Data` directory.

2. Run the script:

    ```sh
    python master.py
    ```
