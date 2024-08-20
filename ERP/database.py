import psycopg2

class DB_handler:
    
    # Connects to the database
    def connect_db(self):
        self.conn = psycopg2.connect(
            host = "db.fe.up.pt",
            port = "5432",
            dbname = "pswa0502",
            user = "pswa0502",
            password = "jKWlEeAs"
        )

    # Closes the connection with the database
    def close_db(self):
        self.conn.close()

    # Deletes a database table
    def delete_db(self, nome):
        with self.conn.cursor() as cur:
            # Check if the database exists before trying to delete it)
            try:
                    # executar uma consulta SQL para selecionar todos os registros da tabela "orders"
                cur.execute(f"SELECT * FROM {nome}")
                if cur.rowcount == 0:
                    print(f"Table {nome} has no entries")
                    return
                else:
                    # if the table has entries, delete it
                    print(f"Deleting {nome} table...")
                    cur.execute(f"DROP TABLE {nome}")
                    print(f"The {nome} table has been deleted.")

                    print(f"The {nome} database has been deleted.")
            except psycopg2.errors.UndefinedTable as e:
                print(f"Table {nome} does not exist")
            
            self.conn.commit()

    # Prints a database table
    def print_db(self, nome):
        with self.conn.cursor() as cur:
            try:
                    # executar uma consulta SQL para selecionar todos os registros da tabela "orders"
                cur.execute(f"SELECT * FROM {nome}")
                if cur.rowcount == 0:
                    print(f"Table {nome} has no entries")
                else:
                    rows = cur.fetchall()
                    print(f"Printing {nome} database...")
                    for row in rows:
                        print(row)
            except psycopg2.errors.UndefinedTable as e:
                print(f"Table {nome} does not exist")

            self.conn.commit()

    # TODO: Add create_client_orders_table
    # Creates all the needed database tables
    def setup(self):
        #self.create_client_orders_table()
        self.create_piece_table()
        self.create_warehouse_table()

    # Creates the database for the pieces
    def create_piece_table(self):
        with self.conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS infi.pieces
                                (id SERIAL PRIMARY KEY, piece_type INTEGER, arrival_day INTEGER, cost NUMERIC, production_time INTEGER)''')
            self.conn.commit()
    
    # Returns the data of a piece (arrival_day, cost, production_time)
    def get_piece_data(self, piece_id):
        with self.conn.cursor() as cur:
            select_sql = "SELECT arrival_day, cost, production_time FROM infi.pieces WHERE id = %s"
            cur.execute(select_sql, (piece_id,))
            row = cur.fetchone()
            self.conn.commit()

            arrival_day = cost = production_time = None
            if row:
                arrival_day, cost, production_time = row
            return float(arrival_day), float(cost), float(production_time)/1000

    # Creates the database for the warehouse
    def create_warehouse_table(self):
        with self.conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS infi.warehouse (piece_id INTEGER REFERENCES infi.pieces (id), entry_date timestamp without time zone)")
            self.conn.commit()
    
    # Returns the inventory in the warehouse
    def get_warehouse_piece_counts(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT piece_type, COUNT(*) FROM infi.warehouse JOIN infi.pieces ON piece_id=id GROUP BY piece_type")
            rows = cur.fetchall()
            counts = {row[0]: row[1] for row in rows}
            self.conn.commit()
            return counts
