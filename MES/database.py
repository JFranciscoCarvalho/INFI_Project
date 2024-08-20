import psycopg2
import time

class DB_handler:
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.conn = None

    # Connects to the database
    def connect_db(self):
        self.conn = psycopg2.connect(
            host = "db.fe.up.pt",
            port = "5432",
            dbname = "pswa0502",
            user = "pswa0502",
            password = "jKWlEeAs",
            keepalives = 1,
            keepalives_idle = 30,
            keepalives_interval = 10,
            keepalives_count = 15
        )
        self.conn.autocommit = True

    # Closes the connection with the database
    def close_db(self):
        self.conn.close()

    # Deletes a database table
    def delete_db(self, nome):
        try:
            with self.conn, self.conn.cursor() as cur:
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
                        cur.execute(f"DROP TABLE {nome} CASCADE")
                        print(f"The {nome} table has been deleted.")

                        print(f"The {nome} database has been deleted.")
                except psycopg2.errors.UndefinedTable as e:
                    print(f"Table {nome} does not exist")
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            self.delete_db(nome)

    # Prints a database table
    def print_db(self, nome):
        with self.conn, self.conn.cursor() as cur:
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

    # TODO: Add the other tables
    # Creates all the needed database tables
    def setup(self):
        self.create_machine_table()
        self.create_dock_table()
        self.create_piece_table()
        self.create_warehouse_table()

    # TODO
    def create_transformation_order_table(self):
        pass

    # TODO
    def create_unloading_order_table(self):
        pass

    # TODO
    def create_loading_order_table(self):
        pass

    def add_transformation_order(self, order_id: int, erp_id: int, initial_type: int, final_type: int):
        with self.conn, self.conn.cursor() as cur:
            insert_sql = f"INSERT INTO infi.mes_transformation_order (order_id, erp_id, status, initial_type, final_type) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(insert_sql, (order_id, erp_id, "pending", initial_type, final_type))

    def add_unloading_order(self, order_id: int, erp_id: int, type: int):
        with self.conn, self.conn.cursor() as cur:
            insert_sql = f"INSERT INTO infi.mes_unloading_order (order_id, erp_id, status, type) VALUES (%s, %s, %s, %s)"
            cur.execute(insert_sql, (order_id, erp_id, "pending", type))

    def add_loading_order(self, order_id: int, erp_id: int, type: int, cost: int, supplier: str):
        with self.conn, self.conn.cursor() as cur:
            insert_sql = f"INSERT INTO infi.mes_loading_order (order_id, erp_id, status, type, cost, supplier) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(insert_sql, (order_id, erp_id, "pending", type, cost, supplier))

    def update_transformation_order(self, order_id: int, end: bool, piece_id: int = 0, machine: int = 0):
        with self.conn, self.conn.cursor() as cur:
            if end:
                insert_sql = f"UPDATE infi.mes_transformation_order SET status='finished' WHERE order_id={order_id}"
            else:
                insert_sql = f"UPDATE infi.mes_transformation_order SET status='processing', piece_id={piece_id}, machine={machine} WHERE order_id={order_id}"
            cur.execute(insert_sql)

    def update_unloading_order(self, order_id: int, end: bool, piece_id: int = 0, dock: int = 0):
        with self.conn, self.conn.cursor() as cur:
            if end:
                insert_sql = f"UPDATE infi.mes_unloading_order SET status='finished' WHERE order_id={order_id}"
            else:
                insert_sql = f"UPDATE infi.mes_unloading_order SET status='processing', piece_id={piece_id}, dock={dock} WHERE order_id={order_id}"
            cur.execute(insert_sql)

    def update_loading_order(self, order_id: int):
        with self.conn, self.conn.cursor() as cur:
            insert_sql = f"UPDATE infi.mes_loading_order SET status='finished' WHERE order_id={order_id}"
            cur.execute(insert_sql)

    def get_transformation_orders(self):
        with self.conn, self.conn.cursor() as cur:
            select_sql = f"SELECT * FROM infi.mes_transformation_order WHERE NOT status='finished'"
            cur.execute(select_sql)
            rows = cur.fetchall()
        return rows

    def get_unloading_orders(self):
        with self.conn, self.conn.cursor() as cur:
            select_sql = f"SELECT * FROM infi.mes_unloading_order WHERE NOT status='finished'"
            cur.execute(select_sql)
            rows = cur.fetchall()
        return rows

    def get_loading_order(self):
        with self.conn, self.conn.cursor() as cur:
            select_sql = f"SELECT * FROM infi.mes_loading_order WHERE NOT status='finished'"
            cur.execute(select_sql)
            rows = cur.fetchall()
        return rows
    
    # Creates the database for the machine statistics
    def create_machine_table(self):
        try:
            with self.conn, self.conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS infi.machine (name text NOT NULL, total_operating_time integer, total_operated_pieces integer, p1 integer, p2 integer, p3 integer, p4 integer, p5 integer, p6 integer, p7 integer, p8 integer, p9 integer)")

                cur.execute("SELECT * FROM infi.machine")
                if cur.rowcount < 4:
                    for i in range(1, 5):
                        cur.execute(f"INSERT INTO infi.machine VALUES ('M{i}', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) ON CONFLICT DO NOTHING")
                                
                cur.execute("ALTER TABLE ONLY infi.machine DROP CONSTRAINT IF EXISTS machine_pkey")
                cur.execute("ALTER TABLE ONLY infi.machine ADD CONSTRAINT machine_pkey PRIMARY KEY (name)")
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.create_machine_table()

    # Returns the machine statistics stored in the database
    def get_machine_statistics(self):
        try:
            with self.conn, self.conn.cursor() as cur:
                cur.execute("SELECT * FROM infi.machine ORDER BY name")
                rows = cur.fetchall()
            return rows
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.get_machine_statistics()

    # Adds worked piece to db
    def update_machine(self, machine, type, operating_time):
        try:
            with self.conn, self.conn.cursor() as cur:
                update_sql = f"UPDATE infi.machine SET total_operating_time = total_operating_time + %s, total_operated_pieces = total_operated_pieces + 1, p%s = p%s + 1 WHERE name=%s"
                cur.execute(update_sql, (operating_time, type, type, machine))
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.update_machine(machine, type, operating_time)

    # Creates the database for the dock statistics
    def create_dock_table(self):
        try:
            with self.conn, self.conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS infi.dock (no integer NOT NULL, total_unloaded_pieces integer, p1 integer, p2 integer, p3 integer, p4 integer, p5 integer, p6 integer, p7 integer, p8 integer, p9 integer)")
                
                cur.execute("SELECT * FROM infi.dock")
                if cur.rowcount < 4:
                    for i in range(1, 3):
                        cur.execute(f"INSERT INTO infi.dock VALUES ({i}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) ON CONFLICT DO NOTHING")
                
                cur.execute("ALTER TABLE ONLY infi.dock DROP CONSTRAINT IF EXISTS dock_pkey")
                cur.execute("ALTER TABLE ONLY infi.dock ADD CONSTRAINT dock_pkey PRIMARY KEY (no)")
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.create_dock_table()

    # Returns the dock statistics stored in the database
    def get_dock_statistics(self):
        try:
            with self.conn, self.conn.cursor() as cur:
                cur.execute("SELECT * FROM infi.dock ORDER BY no")
                rows = cur.fetchall()
            return rows
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.get_dock_statistics()
            
    # Adds unloaded piece to db    
    def update_dock(self, doca, peca):
        try:
            with self.conn, self.conn.cursor() as cur:
                update_sql = f"UPDATE infi.dock SET total_unloaded_pieces = total_unloaded_pieces + 1, p{peca}=p{peca}+1 WHERE no={doca}"
                cur.execute(update_sql)
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.update_dock(doca, peca)

    # Creates the database for the pieces
    def create_piece_table(self):
        try:
            with self.conn, self.conn.cursor() as cur:
                cur.execute('''CREATE TABLE IF NOT EXISTS infi.pieces
                                    (id SERIAL PRIMARY KEY, piece_type INTEGER, arrival_day INTEGER, cost NUMERIC, production_time INTEGER)''')
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.create_piece_table()

    # Creates a new piece in the pieces database
    def add_piece(self, piece_type, cost, arrival_day, production_time):
        try:
            with self.conn, self.conn.cursor() as cur:
                insert_sql = "INSERT INTO infi.pieces (piece_type, arrival_day, cost, production_time) VALUES (%s, %s, %s, %s) RETURNING id"
                cur.execute(insert_sql, (piece_type, arrival_day, cost, production_time))
                piece_id = cur.fetchone()[0]
            return piece_id
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.add_piece(piece_type, cost, arrival_day, production_time)
    
    # Updates the type of a piece
    def update_piece_type(self, piece_id, new_type):
        try:
            with self.conn, self.conn.cursor() as cur:
                update_sql = "UPDATE infi.pieces SET piece_type = %s WHERE id = %s"
                cur.execute(update_sql, (new_type, piece_id))
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.update_piece_type(piece_id, new_type)

    # Adds the production time of a piece
    def update_production_time(self, piece_id, production_time):
        try:
            with self.conn, self.conn.cursor() as cur:
                update_sql = "UPDATE infi.pieces SET production_time = production_time + %s WHERE id = %s"
                cur.execute(update_sql,(production_time, piece_id))
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.update_production_time(piece_id, production_time)

    # Creates the database for the warehouse
    def create_warehouse_table(self):
        try:
            with self.conn, self.conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS infi.warehouse (piece_id INTEGER REFERENCES infi.pieces (id), entry_date timestamp without time zone)")
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.create_warehouse_table()

    # Adds the piece to the warehouse
    def add_piece_to_warehouse(self, piece_id):
        try:
            with self.conn, self.conn.cursor() as cur:
                insert_sql = f"INSERT INTO infi.warehouse (piece_id, entry_date) VALUES ({piece_id}, NOW())"
                cur.execute(insert_sql)
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.add_piece_to_warehouse(piece_id)
    
    # Returns the inventory in the warehouse
    def get_warehouse_piece_counts(self):
        try:
            with self.conn, self.conn.cursor() as cur:
                cur.execute("SELECT piece_type, COUNT(*) FROM infi.warehouse JOIN infi.pieces ON piece_id=id GROUP BY piece_type")
                rows = cur.fetchall()
                counts = {row[0]: row[1] for row in rows}
            return counts
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.get_warehouse_piece_counts()
    
    # Removes the piece from the warehouse in database
    def remove_piece_from_warehouse(self, piece_type):
        try:
            with self.conn, self.conn.cursor() as cur:
                select_sql = "SELECT piece_id FROM infi.warehouse JOIN infi.pieces ON piece_id=id WHERE piece_type = %s ORDER BY entry_date ASC LIMIT 1"
                cur.execute(select_sql, (piece_type,))
                row = cur.fetchone()

                piece_id = None
                if row:
                    piece_id = row[0]
                    delete_sql = "DELETE FROM infi.warehouse WHERE piece_id = %s"
                    cur.execute(delete_sql, (piece_id,))
            return int(piece_id)
        except:
            print("DB CONNECTION FAILED FOR WHATEVER REASON")
            self.close_db()
            self.connect_db()
            return self.remove_piece_from_warehouse(piece_type)


if __name__ == '__main__':
    t = time.time()
    db = DB_handler()
    db.connect_db()

    db.delete_db('infi.machine')
    db.delete_db('infi.dock')
    db.delete_db('infi.warehouse')
    db.delete_db('infi.pieces')

    db.close_db()
    print(time.time() - t)