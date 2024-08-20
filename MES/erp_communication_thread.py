import json
import socket
from queue import Queue
from threading import Lock, Thread

from clock import *
from json_parser import JsonParser

class ERPCommunication():

    def __init__(self, erp_orders: Queue, queue_lock: Lock, info_queue: Queue, host="localhost", port=60459):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.keep_alive_timeout = 5.0
        self.is_alive = False

        self.erp_orders = erp_orders
        self.queue_lock = queue_lock
        self.info_queue = info_queue

    def start(self):
        self.is_alive = True
        self.thread = Thread(target=self._run, name="MES_ERP_Thread")
        self.thread.start()

    def stop(self):
        self.is_alive = False
        self.thread.join()

    def recv(self, client: socket.socket):
        data = b''
        while True:
            packet = client.recv(1024)
            if not packet:
                break
            data += packet
            if len(packet) < 1024:
                break
        return data.decode()

    def _run(self):

        print(f"| {get_time()} | MES | ERP Thread | INFO | Starting...")

        while self.is_alive:

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

                sock.bind((self.host, self.port))
                print(f"| {get_time()} | MES | ERP Thread | INFO | MES server ready")

                sock.listen(1)
                sock.settimeout(self.keep_alive_timeout)
                print(f"| {get_time()} | MES | ERP Thread | INFO | Listening for incoming communications...")

                while self.is_alive:
                    try:
                        #print(f"| {get_time()} | MES | ERP Thread | INFO | Waiting for incoming clients...")
                        client, addr = sock.accept()
                        #print(f"| {get_time()} | MES | ERP Thread | INFO | Client accepted: {addr}")

                        with client:

                            data = self.recv(client)

                            #print(f"| {get_time()} | MES | ERP Thread | INFO | Data received")

                            # Handle the data (if it's a request send the response or add the orders to the queue)
                            
                            # ERP asked for new information, if available
                            if (data.startswith("get")):
                                
                                _, day, seconds = data.split()
                                day = int(day)
                                seconds = int(seconds)
                                set_time(day, seconds, time()-seconds)

                                # Verifies if there is any new info to send
                                if not self.info_queue.empty():

                                    # Gets the next info to send
                                    info = self.info_queue.get()

                                    # Encodes the dictionary into a json file
                                    json_info = json.dumps(info)

                                    # Send the response
                                    client.sendall(json_info.encode())

                                    try:
                                        # Wait for the ACK response
                                        response = self.recv(client)
                                        
                                        # Check response
                                        if (response != 'ACK'):
                                            self.info_queue.put(info)

                                    except socket.timeout:
                                        # Insert the info to the queue to resend it later
                                        self.info_queue.put(info)
                                        
                                else:
                                    # Send the ACK response
                                    client.sendall("ACK".encode())

                            # ERP asked for MES current time
                            elif (data == 'time'):
                                # Send current time
                                print(f"| {get_time()} | MES | ERP Thread | Negociating time with ERP")
                                client.sendall(get_time_to_erp().encode())

                            # ERP sent a new json file with orders
                            else:
                                
                                print(f"| {get_time()} | MES | ERP Thread | INFO | New orders received")

                                # Lock the access to the queue while adding new orders
                                with self.queue_lock:
                                    
                                    # Clear the orders from the queue
                                    while not self.erp_orders.empty():
                                        self.erp_orders.get()

                                    # Decode the json file
                                    orders = JsonParser.parse(data)

                                    # Add the new orders to the queue
                                    for order in orders:
                                        self.erp_orders.put(order)
                                    
                                # Send the ACK response
                                client.sendall("ACK".encode())

                    except socket.timeout:
                        print(f"| {get_time()} | MES | ERP Thread | ERROR | The connection with the ERP reached a timeout")
                        print(f"| {get_time()} | MES | ERP Thread | INFO | Retrying connection...")
                else:
                    print(f"| {get_time()} | MES | ERP Thread | INFO | Shutting down...")