import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from random import choice as rc
from random import randint

POPULATE_MIN=500
POPULATE_MAX=1000

class SqliteDatabase:
    def __init__(self, logger, dbname: str):
        self.dbname = dbname
        self.logger = logger
    def create_db_file(self):
        print(f"Attempting creation of {self.dbname}.db")
        try:
            temp_dir = Path(tempfile.gettempdir())
            temp_file = Path(temp_dir,f"{self.dbname}.db")
            self.logger.info(f"{self.dbname}.db created")
            self.db_file= temp_file
        except Exception as e:
            self.logger.error(f"Could not create {self.dbname}.db: {e}")

    def connect_db(self):
        # Connect to the DB - through the file we created
        self.logger.debug(f"Connection attempt to {self.dbname}.db")
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()
            self.logger.debug(f"Successful conenction to {self.dbname}.db")
        except Exception:
            self.logger.error(f"Could not connect to {self.dbname}.db")

    def initialize_db(self):
        self.connect_db()
        self.logger.info(f"Attempting to populate {self.dbname} with data")
        with open("./tests/create.sql") as f:
            sql=f.read()
        try:
            self.cursor.executescript(sql)
            self.connection.commit()
            self.connection.close()
        except Exception as e:
            self.logger.error(f"Unable to run create.sql against db: {e}")
        # with open("./tests/update.sql", "r")as f:
        #     sql=f.read()
        # try:
        #     self.cursor.executescript(sql)
        #     self.connection()
        #     self.connection.close()
        # except Exception as e:
        #     self.logger.error(f"Unable to run update.sql against db: {e}")
    def report_db(self):
        self.connect_db()
        with open("./tests/report.sql") as f:
            sql=f.read()
        sql=sql.split("\n")
        results = []
        for line in sql:
            self.cursor.execute(line)
            # self.logger.info(self.cursor.fetchall())
            results.append(self.cursor.fetchall())
        self.connection.commit()
        self.connection.close()
        return results
    # This function will return a random datetime between two datetime objects.
    @staticmethod
    def random_date(start, end):
        return start + timedelta(seconds=randint(0, int((end - start).total_seconds())))

    def populate_db(self):
        self.connect_db()
        # ShipName, ShipAddress, ShipCity, ShipRegion, ShipPostalCode
        self.cursor.execute(
              "select distinct ShipName, ShipAddress, ShipCity, ShipRegion, ShipPostalCode, " \
              "ShipCountry from [Orders]"
        )
        locations = [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in self.cursor.fetchall()]

        # Customer.Id
        self.cursor.execute("select distinct EmployeeId from [Employees]")
        employees = [row[0] for row in self.cursor.fetchall()]

        # Shipper.Id
        self.cursor.execute("select distinct ShipperId from [Shippers]")
        shippers = [row[0] for row in self.cursor.fetchall()]

        # Customer.Id
        self.cursor.execute("select distinct CustomerId from [Customers]")
        customers = [row[0] for row in self.cursor.fetchall()]

        # Create a bunch of new orders
        for _i in range(randint(POPULATE_MIN, POPULATE_MAX)):
            sql = "INSERT INTO [Orders] (CustomerId, EmployeeId, OrderDate, RequiredDate, ShippedDate,\
                   ShipVia, Freight, ShipName, ShipAddress, ShipCity,\
                   ShipRegion, ShipPostalCode, ShipCountry) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            location = rc(locations)
            order_date = self.random_date(
                datetime.strptime("2012-07-10", "%Y-%m-%d"), datetime.today()
            )
            required_date = self.random_date(
                order_date, order_date + timedelta(days=randint(14, 60))
            )
            shipped_date = self.random_date(order_date, order_date + timedelta(days=randint(1, 30)))
            params = (
                rc(customers),  # CustomerId
                rc(employees),  # EmployeeId
                order_date,  # OrderDate
                required_date,  # RequiredDate
                shipped_date,  # ShippedDate
                rc(shippers),  # ShipVia
                0.00,  # Freight
                location[0],  # ShipName
                location[1],  # ShipAddress
                location[2],  # ShipCity
                location[3],  # ShipRegion
                location[4],  # ShipPostalCode
                location[5],  # ShipCountry
            )
            self.cursor.execute(sql, params)
        # Product.Id
        self.cursor.execute("select distinct ProductId, UnitPrice from [Products]")
        products = [(row[0], row[1]) for row in self.cursor.fetchall()]

        # Order.Id
        self.cursor.execute("select distinct OrderId from [Orders] where Freight = 0.00")
        orders = [row[0] for row in self.cursor.fetchall()]

        # Fill the order with items
        for order in orders:
            used = []
            for _x in range(randint(1, len(products))):
                sql = "INSERT INTO [Order Details] (OrderId, ProductId, UnitPrice, Quantity, Discount)\
                       VALUES (?, ?, ?, ?, ?)"
                control = 1
                while control:
                    product = rc(products)
                    if product not in used:
                        used.append(product)
                        control = 0
                params = (
                    # "%s/%s" % (order, product[0]),
                    order,  # OrderId
                    product[0],  # ProductId
                    product[1],  # UnitPrice
                    randint(1, 50),  # Quantity
                    0,  # Discount
                )
                self.cursor.execute(sql, params)
        # Cleanup
        self.cursor.execute("select sum(Quantity)*0.25+10, OrderId from [Order Details] group by OrderId")
        orders = [(row[0], row[1]) for row in self.cursor.fetchall()]
        for order in orders:
            self.cursor.execute("update [Orders] set Freight=? where OrderId=?", (order[0], order[1]))
        self.connection.commit()
        self.connection.close()
