import sys
from queue import Queue
from threading import Lock, Thread
from time import time
import traceback

from clock import *
from machine import Machine
from node_ids import NodeId
from opcua_communication import OPCUAClient
from plc_variable_types import order_to_piece_t

PLC_CONNECTION_CYCLE_TIME = 0.1

class PLCCommunication():

    def __init__(self, pending_orders: Queue, plc_lock: Lock, machines: dict[str, Machine], info_queue: Queue, exception_queue: Queue):
        Thread.__init__(self)
        self.is_alive = False
        
        self.pending_orders = pending_orders
        self.plc_lock = plc_lock
        self.machines = machines
        self.info_queue = info_queue
        self.exception_queue = exception_queue

        self.piece_waiting = None
        self.old_piece_waiting = None

        self.tools_output = [1,1,1,1]

    def start(self):
        self.is_alive = True
        self.thread = Thread(target=self._run, name="MES_PLC_Thread")
        self.thread.start()
    
    def stop(self):
        self.is_alive = False
        self.thread.join()

    def get_new_machine_tools(self):
        return [m.get_new_tool_index() for m in self.machines.values()]

    def _run(self):

        print(f"| {get_time()} | MES | PLC Thread | INFO | Starting...")

        try:
            
            # Connection to the opc-ua server
            print(f"| {get_time()} | MES | PLC Thread | INFO | Connecting to the opc-ua server...")
            client = OPCUAClient()
            client.connect()
            print(f"| {get_time()} | MES | PLC Thread | INFO | Connected to opc-ua server")

        except:
            # Couldn't connect to the opc ua server, so exit the program
            print(f"| {get_time()} | MES | PLC Thread | ERROR | Couldn't connect to the opc ua server")
            print(f"| {get_time()} | MES | PLC Thread | INFO | Shutting down...")
            self.exception_queue.put(sys.exc_info())
            sys.exit()

        try:
            # PLC loop
            while self.is_alive:
                
                init_cycle_time = time()

                # Read inputs
                piece_whout_sync = client.read(NodeId.piece_WHOut_Sync.value)
                piece_whout      = client.read_piece_t(NodeId.piece_WHOut.value)
                piece_whin_sync  = client.read(NodeId.piece_WHIn_Sync.value)
                piece_whin       = client.read_piece_t(NodeId.piece_WHIn.value)
                pusher1_out_sync = client.read(NodeId.pusher1_Out_Sync.value)
                pusher1_out      = client.read_piece_delivered_t(NodeId.pusher1_Out.value)
                pusher2_out_sync = client.read(NodeId.pusher2_Out_Sync.value)
                pusher2_out      = client.read_piece_delivered_t(NodeId.pusher2_Out.value)
                loading_out_sync = client.read(NodeId.loading_Out_Sync.value)
                m_active_tool    = client.read(NodeId.m_active_tool.value)
                
                # Update machine active status (free and active tools)
                for i, m in enumerate(self.machines.values()):
                    m.update_state()
                    m.update_tool(m_active_tool[i])
                
                # Piece left the warehouse
                if (piece_whout_sync):
                    print(f"| {get_time()} | MES | PLC Thread | INFO | Piece {piece_whout.id} (P{piece_whout.type_}) left the warehouse")

                    # Move the piece from waiting to processing
                    self.old_piece_waiting, self.piece_waiting = self.piece_waiting, None
                    
                    # Send this information to the main thread
                    information = {
                        'info_type': 'piece_left_wh',
                        'id': piece_whout.id,
                        'piece_type': piece_whout.type_
                    }

                    self.info_queue.put(information)

                # A piece entered the warehouse
                if piece_whin_sync:
                    
                    if piece_whin.id != 0:

                        print(f"| {get_time()} | MES | PLC Thread | INFO | Piece {piece_whin.id} (P{piece_whin.type_}) entered the warehouse")

                        # It's a piece coming from a transformation
                        information = {
                            'info_type': 'piece_entered_wh',
                            'id': piece_whin.id,
                            'machine_t': piece_whin.machine_t,
                            'piece_type': piece_whin.type_
                        }
                        
                        self.info_queue.put(information)

                # Piece delivered in dock1
                if (pusher1_out_sync):
                    print(f"| {get_time()} | MES | PLC Thread | INFO | Piece {pusher1_out.id} (P{pusher1_out.type_}) delivered in dock1")

                    # Send this information to the main thread
                    information = {
                        'info_type' : 'piece_delivered',
                        'id'        : pusher1_out.id,
                        'dock_no'   : 1,
                        'piece_type': pusher1_out.type_
                    }

                    self.info_queue.put(information)

                # Piece delivered in dock2
                if (pusher2_out_sync):
                    print(f"| {get_time()} | MES | PLC Thread | INFO | Piece {pusher2_out.id} (P{pusher2_out.type_}) delivered in dock2")

                    # Send this information to the main thread
                    information = {
                        'info_type' : 'piece_delivered',
                        'id'        : pusher2_out.id,
                        'dock_no'   : 2,
                        'piece_type': pusher2_out.type_
                    }

                    self.info_queue.put(information)
                
                # Raw material P1 arrived at the production line from a supplier
                if (loading_out_sync[0]):
                    print(f"| {get_time()} | MES | PLC Thread | INFO | Piece P1 arrived from supplier")

                    # Send this information to the main thread
                    information = {
                        'info_type': 'piece_from_supplier',
                        'type': 1
                    }

                    self.info_queue.put(information)

                # Raw material P2 arrived at the production line from a supplier
                if loading_out_sync[1]:
                    print(f"| {get_time} | MES | PLC Thread | INFO | Piece P2 arrived from supplier")
                    
                    # Send this information to the main thread
                    information = {
                        'info_type': 'piece_from_supplier',
                        'type': 2
                    }

                    self.info_queue.put(information)

                # Ready to send new piece
                if ((self.piece_waiting is None) and (not piece_whout_sync) and (not self.pending_orders.empty())):
                    with self.plc_lock:
                        new_piece = self.pending_orders.get()
                        self.piece_waiting = order_to_piece_t(new_piece, self.machines)

                        if self.old_piece_waiting is None or self.piece_waiting.id != self.old_piece_waiting.id:
                            # Update machine status if it's a transformation order
                            machine = self.piece_waiting.tasks[0].machine
                            if machine != 0:
                                work_time = self.piece_waiting.tasks[0].work_time / 1000
                                self.machines['M'+str(machine)].start_production(work_time)
                                if machine == 1:
                                    self.machines['M2'].start_production(work_time)
                        else:
                            self.piece_waiting = None
                    
                # Calculate machine tools
                machine_tools = self.tools_output
                for i, m in enumerate(self.machines.values()):
                    # If the tool is not changing then it's free to change
                    if not m.is_changing_tool and (self.tools_output[i] != m.get_new_tool_index()):
                        machine_tools[i] = m.get_new_tool_index()
                        m.start_changing_tool()

                # Update outputs
                # Update sync signals
                if piece_whout_sync:
                    client.write_bool(NodeId.piece_WHOut_Sync.value, False)
                if piece_whin_sync:
                    client.write_bool(NodeId.piece_WHIn_Sync.value, False)
                if pusher1_out_sync:
                    client.write_bool(NodeId.pusher1_Out_Sync.value, False)
                if pusher2_out_sync:
                    client.write_bool(NodeId.pusher2_Out_Sync.value, False)
                if loading_out_sync[0]:
                    client.write_bool(NodeId.loading_out_sync1.value, False)
                if loading_out_sync[1]:
                    client.write_bool(NodeId.loading_out_sync2.value, False)
                # Update machine tools
                client.write_uint(NodeId.m_tool.value, machine_tools)
                self.tools_output = machine_tools
                # Update piece to leave wh
                if self.piece_waiting is not None:
                    client.write_piece_t(NodeId.piece_WHOut.value, self.piece_waiting)

                # Wait for the next cycle
                sleep_next_cycle(init_cycle_time, PLC_CONNECTION_CYCLE_TIME)

        except:
            # Send exception error to the main thread
            print(f"| {get_time()} | MES | PLC Thread | ERROR | Couldn't write/read variables into the opc ua server")
            print(f"| {get_time()} | MES | PLC Thread | INFO | Shutting down...")
            self.exception_queue.put(sys.exc_info())
            print(traceback.format_exc())
        finally:
            # Disconnect the opc-ua server
            print(f"| {get_time()} | MES | PLC Thread | INFO | Disconnecting from the opc-ua server...")
            try:
                client.disconnect()
            except:
                pass
            print(f"| {get_time()} | MES | PLC Thread | INFO | Disconnected from the opc-ua server")
            print(f"| {get_time()} | MES | PLC Thread | INFO | Shutting down...")