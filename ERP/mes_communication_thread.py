import json
import socket
from queue import Queue
from threading import Lock, Thread
from time import time

from clock import *
from json_generator import JsonGenerator
from order import *

MES_COMMUNICATION_CYCLE = 1.0

class MESCommunication():

    def __init__(self, erp_orders: Queue, mes_lock: Lock, info_queue: Queue, host="localhost", port=60459):
        self.host = host
        self.port = port
        self.keep_alive_timeout = 10
        self.is_alive = False

        self.erp_orders = erp_orders
        self.mes_lock = mes_lock
        self.info_queue = info_queue

    def start(self):
        self.is_alive = True
        self.thread = Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.is_alive = False
        self.thread.join()

    def recv(self, sock: socket.socket):
        response = b''
        while True:
            packet = sock.recv(1024)
            if not packet:
                break
            response += packet
            if len(packet) < 1024:
                break
        return response.decode()

    def negociate_time(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                sock.sendall('time'.encode())
                response = self.recv(sock)
                if response:
                    day, seconds = response.split()
                    return int(day), int(seconds)
                else:
                    return None, None
        except:
            return None, None
            
    def _run(self):

        print(f"| {get_time()} | ERP | MES Thread | INFO | Starting...")

        while self.is_alive:

            init_cycle = time()

            # Create a new tcp/ip socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                
                try:
                    # Connect to the Mes server
                    sock.connect((self.host, self.port))
                    sock.settimeout(self.keep_alive_timeout)

                    # Send erp orders to the MES
                    if (not self.erp_orders.empty()):
                        
                        transformation_orders = []
                        delivery_orders = []
                        loading_orders = []

                        # Asure that the main thread wrote all the data
                        with self.mes_lock:
                            while not self.erp_orders.empty():
                                order = self.erp_orders.get()
                                
                                if isinstance(order, TransformationOrder):
                                    transformation_orders.append(order)
                                elif isinstance(order, DeliveryOrder):
                                    delivery_orders.append(order)
                                elif isinstance(order, LoadingOrder):
                                    loading_orders.append(order)

                        # Generates the json file
                        message = JsonGenerator.generate(transformation_orders, delivery_orders, loading_orders)
                        
                        # Sends the orders to the MES
                        sock.sendall(message.encode())

                        # Waits for an ACK response
                        try:
                            response = self.recv(sock)
                            
                            # If there is any error resend the orders
                            if (response != 'ACK'):
                                # This should never happen
                                
                                for order in transformation_orders:
                                    self.erp_orders.put(order)
                                for order in delivery_orders:
                                    self.erp_orders.put(order)
                                for order in loading_orders:
                                    self.erp_orders.put(order)

                        except socket.timeout:
                        
                            print(f"| {get_time()} | ERP | MES Thread | ERROR | The connection with the ERP reached a timeout")

                            for order in transformation_orders:
                                self.erp_orders.put(order)
                            for order in delivery_orders:
                                self.erp_orders.put(order)
                            for order in loading_orders:
                                self.erp_orders.put(order)

                            print(f"| {get_time()} | ERP | MES Thread | INFO | Trying to send again...")

                    # Ask for new data from the MES
                    else:
                        #print(f"| {get_time()} | ERP | MES Thread | INFO | Asking MES for new data...")
                        message = f'get {get_time_to_mes()}'
                        sock.sendall(message.encode())

                        response = self.recv(sock)

                        # If there is no data, the MES sends an ACK packet
                        if response != 'ACK':
                            
                            # Decode the data
                            response = dict(json.loads(response))

                            # Send the information to the main thread
                            self.info_queue.put(response)

                            # Send the response
                            sock.sendall(b'ACK')

                        sleep_next_cycle(init_cycle, MES_COMMUNICATION_CYCLE)

                except socket.timeout:
                    print(f"| {get_time()} | ERP | MES Thread | ERROR | The connection with the ERP reached a timeout")
                    sleep_next_cycle(init_cycle, MES_COMMUNICATION_CYCLE)
                    print(f"| {get_time()} | ERP | MES Thread | INFO | Trying to reconnect")
                
                except ConnectionRefusedError:
                    print(f"| {get_time()} | ERP | MES Thread | ERROR | MES server is down")
                    sleep_next_cycle(init_cycle, MES_COMMUNICATION_CYCLE)
                    print(f"| {get_time()} | ERP | MES Thread | INFO | Retrying connection with MES server")