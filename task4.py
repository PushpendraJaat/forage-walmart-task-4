import csv
import sqlite3

class DatabaseConnector:
    """
    Manages a connection to a SQLite database.
    """
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def populate(self, spreadsheet_folder):
        """
        Populate the database with data imported from each spreadsheet.
        """
        # Open the spreadsheets
        with open(f"{spreadsheet_folder}/shipping_data_0.csv", "r") as spreadsheet_file_0:
            with open(f"{spreadsheet_folder}/shipping_data_1.csv", "r") as spreadsheet_file_1:
                with open(f"{spreadsheet_folder}/shipping_data_2.csv", "r") as spreadsheet_file_2:
                    # Prepare the CSV readers
                    csv_reader_0 = csv.reader(spreadsheet_file_0)
                    csv_reader_1 = csv.reader(spreadsheet_file_1)
                    csv_reader_2 = csv.reader(spreadsheet_file_2)
                    
                    # Skip headers
                    next(csv_reader_0)
                    next(csv_reader_1)
                    next(csv_reader_2)

                    # Populate the data
                    self.populate_first_shipping_data(csv_reader_0)
                    self.populate_second_shipping_data(csv_reader_1, csv_reader_2)

    def populate_first_shipping_data(self, csv_reader_0):
        """
        Populate the database with data imported from the first spreadsheet.
        """
        for row_index, row in enumerate(csv_reader_0):
            # Extract each required field
            product_name = row[2]
            product_quantity = row[4]
            origin = row[0]
            destination = row[1]

            # Insert the data into the database
            self.insert_product_if_it_does_not_already_exist(product_name)
            self.insert_shipment(product_name, product_quantity, origin, destination)

            # Give an indication of progress
            print(f"Inserted product {row_index + 1} from shipping_data_0")

    def populate_second_shipping_data(self, csv_reader_1, csv_reader_2):
        """
        Populate the database with data imported from the second and third spreadsheets.
        """
        # Collect shipment info
        shipment_info = {}
        for row_index, row in enumerate(csv_reader_2):
            # Extract each required field from shipping_data_2
            shipment_identifier = row[0]
            origin = row[1]
            destination = row[2]

            # Store shipment info
            shipment_info[shipment_identifier] = {
                "origin": origin,
                "destination": destination,
                "products": {}
            }

        # Read in product information from shipping_data_1
        for row_index, row in enumerate(csv_reader_1):
            # Extract shipment and product info from shipping_data_1
            shipment_identifier = row[0]
            product_name = row[1]

            # Populate intermediary data structure
            products = shipment_info[shipment_identifier]["products"]
            if product_name not in products:
                products[product_name] = 1
            else:
                products[product_name] += 1

        # Insert the data into the database
        count = 0
        for shipment_identifier, shipment in shipment_info.items():
            # Collect origin and destination
            origin = shipment["origin"]
            destination = shipment["destination"]

            for product_name, product_quantity in shipment["products"].items():
                # Insert product and shipment data
                self.insert_product_if_it_does_not_already_exist(product_name)
                self.insert_shipment(product_name, product_quantity, origin, destination)

                # Progress indication
                count += 1
                print(f"Inserted product {count} from shipping_data_1")

    def insert_product_if_it_does_not_already_exist(self, product_name):
        """
        Insert a new product into the database.
        If a product already exists in the database with the given name,
        ignore it.
        """
        query = """
        INSERT OR IGNORE INTO product (name)
        VALUES (?);
        """
        self.cursor.execute(query, (product_name,))
        self.connection.commit()

    def insert_shipment(self, product_name, product_quantity, origin, destination):
        """
        Insert a new shipment into the database.
        """
        # Collect the product id
        query = """
        SELECT id
        FROM product
        WHERE name = ?;
        """
        self.cursor.execute(query, (product_name,))
        product_id = self.cursor.fetchone()[0]

        # Insert the shipment
        query = """
        INSERT OR IGNORE INTO shipment (product_id, quantity, origin, destination)
        VALUES (?, ?, ?, ?);
        """
        self.cursor.execute(query, (product_id, product_quantity, origin, destination))
        self.connection.commit()

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()


if __name__ == '__main__':
    # Initialize the database connector and populate the database
    database_connector = DatabaseConnector("shipment_database.db")
    database_connector.populate("./data")
    database_connector.close()