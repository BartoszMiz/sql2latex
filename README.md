# USAGE
Show help: `./sql2latex.py --help`
Generate LaTeX code from the SQL file and output it to the STDOUT:
```sh
./sql2latex.py -q list.sql -a "John Smith" -t "My List"
```

# SETUP
1. Download the Oracle instant client from: https://www.oracle.com/database/technologies/instant-client/downloads.html
1. Extract the zip file so that the instant client folder is next to the script
1. Take the Wallet_*.zip, extract it and put the extracted files into instantclient_*/network/admin
1. Open the instant_client_*/network/admin/tnsnames.ora file in a text editor, take the first value (eg. dabfh646a5dsf65_high) and paste it into the DB_DSN variable
1. Set up the DB_LIB_DIR variable according to where you extracted the instantclient. See: https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html
1. Create a virtual environment `python -m venv venv` and activate it
1. Install the dependencies `pip install -r requirements.txt`
1. Set up the DB_USER and DB_PASSWORD variables

# LICENSE
This project is licensed under the GPLv3. See LICENSE.

