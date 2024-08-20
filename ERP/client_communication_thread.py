import socket
from queue import Queue
from threading import Thread, Lock

from clock import get_time
from xml_parser import XMLPARSER

class ClientCommunication():

    def __init__(self, client_orders: Queue, client_lock: Lock, host="0.0.0.0", port=54321):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.is_alive = False

        self.client_lock = client_lock
        self.client_orders = client_orders

    def start(self):
        self.is_alive = True
        self.thread = Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.is_alive = False
        self.thread.join()

    def _run(self):

        print(f"| {get_time()} | MES | Client Thread | INFO | Starting...")

        # Create a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

            # Open the server host
            sock.bind((self.host, self.port))
            print(f"| {get_time()} | ERP | Client Thread | INFO | Client connection ready")

            while self.is_alive:
                
                # Receive the xml data
                data = b''
                while True:
                    packet = sock.recv(1024)
                    if not packet:
                        break
                    data += packet
                    if len(packet) < 1024:
                        break

                data = data.decode()

                print(f"| {get_time()} | ERP | Client Thread | INFO | New orders received")

                # Decode the xml file
                orders = XMLPARSER.parse(data)

                with self.client_lock:
                    for order in orders:

                        print(f"| {get_time()} | ERP | Client Thread | INFO | New Order: ", end='')
                        print(f"{order.name} | n. {order.number} | {order.quantity} {order.piece} | Duedate = {order.due_date} | LP = {order.late_penalty} | EP = {order.early_penalty}")

                        self.client_orders.put(order)