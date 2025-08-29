import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from random import choice as rc
from random import randint

# Create/Overwrite the db file
# if file exists, get rid of it, else create mew file


def create_db_file(dbname):
    # temp_dir = Path(tempfile.gettempdir(), self.extension_name, self.monitoring_config_id)
    print(f"Attempting creation of {dbname}.db")
    try:
        temp_dir = Path(tempfile.gettempdir())
        temp_file = Path(temp_dir,f"{dbname}.db")
        print(f"{dbname}.db created")
    except Exception as e:
        print(f"Could not create {dbname}.db")
    return temp_file

def connect_db(temp_file,dbname):
    # Connect to the DB - through the tempfile
    print(f"Connection attempt to {dbname}.db")
    try:
        conn = sqlite3.connect(temp_file)
        c = conn.cursor()
        print(f"Successful conenction to {dbname}.db")
    except Exception as e:
        print(f"Could not connect to {dbname.db}")
        #self.logger.info(f"Reading Cache File from : {temp_file}")
    return c,conn


def init_db(temp_file,dbname,cursor,conn):
    print(f"Attempting to initially populate {dbname} with data")
    with open("../tests/create.sql", "r") as f:
        sql=f.read()
    try:
        cursor.executescript(sql)
    except Exception as e:
        print("Unable to write to db")

        
    with open("../tests/update.sql", "r")as f:
        sql=f.read()
    try:
        cursor.executescript(sql)
        conn.commit()
        conn.close()
    except Exception as e:
        print("Unable to write to db")
        
def report_db(temp_file,dbname):
    cursor,conn=connect_db(temp_file, dbname)
    with open("../tests/report.sql", "r") as f:
        sql=f.read()

    sql=sql.split("\n")
    for line in sql:
        cursor.execute(line)
        print(cursor.fetchall())

    
dbname="northwind"
temp_file=create_db_file(dbname)
cursor,conn=connect_db(temp_file,dbname)
init_db(temp_file, dbname, cursor,conn)
report_db(temp_file, dbname)
