import os
import sys
import traceback
from queue import Queue
from threading import Lock
from time import time

from clock import *
from database import DB_handler
from dock import Dock
from erp_communication_thread import ERPCommunication
from machine import Machine
from order import *
from plc_communication_thread import PLCCommunication
from transformation import Transformations

# Defines the cycle of the main loop
MAIN_LOOP_CYCLE = 1.0

# Gets the new orders from the ERP for today
def get_today_orders_from_erp():
    # Check if there are new orders from the ERP
    if erp_orders.empty():
        return False
    
    # Clear the pending orders
    pending_orders.clear()
    # Clear the remaining loading orders
    loading_orders.clear()
    # Clear the list of the expected orders for the next days
    next_two_days_expected_orders.clear()
    # Clear the list of today orders
    today_orders.clear()

    # Locks the queue to asure that the erp_thread finished writing
    with erp_lock:
        
        # Gets all the pending orders from the erp
        while not erp_orders.empty():
            
            order = erp_orders.get()

            # If they are for today, add to the pending orders, add to the list of the expected orders in the next 2 days instead
            if order.planning_day <= get_clock_today():
                if isinstance(order, LoadingOrder):
                    loading_orders.append(order)
                else:
                    pending_orders.append(order)
                    if isinstance(order, TransformationOrder):
                        order.tool_to_use = Transformations.get_tool(order.initial_type, order.final_type)
                today_orders.append(order)
            else:
                next_two_days_expected_orders.append(order)

        # Checks if there are already processing or finished orders and removes them from the pending orders
        for p in (processing_orders + finished_orders):
            for o in pending_orders.copy():
                if p.erp_id == o.erp_id:
                    pending_orders.remove(o)
                    break

            for o in loading_orders.copy():
                if p.erp_id == o.erp_id:
                    loading_orders.remove(o)
                    break
    
    return True

# Returns the piece with that order id in that list
def get_order(order_id, lista: list[Order]):
    for piece in lista:
        if piece.order_id == order_id:
            return piece
    return None

# Moves an order from one list to the other and returns it
def move_order(id: int, origin: list[Order], dest: list[Order]):
    piece = get_order(id, origin)
    if piece is not None:
        origin.remove(piece)
        dest.append(piece)
    return piece

# Returns the current active tools in the machines (doesn't check if they are changing)
def get_machine_tools():
    return [m.active_tool for m in machines.values()]

# Schedules the pending orders
def schedule_pending_orders():
    pending_orders.sort(key=lambda order: (not isinstance(order, UnloadingOrder), order.planning_day))

# Calculates the docks to use in each unloading order
def determine_docks():
    # Calculate the docks to use
    n_dock1 = n_dock2 = 0
    for order in pending_orders:
        if order.planning_day > get_clock_today():
            break
        if n_dock1 > 0 and n_dock2 > 0:
            break

        if isinstance(order, UnloadingOrder) and order.dock_to_deliver == 0:
            unloading_orders = []
            for o in pending_orders:
                if isinstance(o, UnloadingOrder) and order.erp_id == o.erp_id:
                    unloading_orders.append(o)
            c = len(unloading_orders)
            
            if c <= 4:
                if n_dock1 == 0:
                    n_dock1 += c
                    for o in unloading_orders:
                        o.dock_to_deliver = 1
                elif n_dock2 == 0:
                    n_dock2 += c
                    for o in unloading_orders:
                        o.dock_to_deliver = 2
            else:
                if n_dock1 == 0 and n_dock2 == 0:
                    for o in range(4):
                        unloading_orders[o].dock_to_deliver = 1
                    for o in range(4, c):
                        unloading_orders[o].dock_to_deliver = 2
                    n_dock1 += 4
                    n_dock2 += c - 4

# Determines the best set of tools for each machine
def determine_tools():
    global new_tools
    
    # Read active machine tools
    machine_tools = get_machine_tools()
    
    # Get the quanitity of each active tool
    active_tools = {1: 0, 2: 0, 3: 0, 4: 0}
    for m_t in machine_tools:
        active_tools[m_t] += 1

    # Get the tools needed
    t_needed = {}
    for order in (pending_orders + next_two_days_expected_orders):
        if isinstance(order, TransformationOrder) and order.tool_to_use != 0:
            if order.tool_to_use in t_needed:
                t_needed[order.tool_to_use] += 1
            else:
                t_needed[order.tool_to_use] = 1
    n_tools_needed = len(t_needed)

    # If lots of tool or none are needed, set it to the default tools
    if n_tools_needed in [0, 3, 4]:
        new_tools = [1, 3, 2, 4]
    elif n_tools_needed == 1:
        tool = next(iter(t_needed))
        n_needed = t_needed[tool]
        
        # Get number of the tool active
        n_tool = active_tools.get(tool)
        if n_tool is None:
            n_tool = 0
        
        # Set max available and needed tools
        for i, m_t in enumerate(machine_tools):
            if n_tool >= n_needed / 2:
                break

            if m_t == tool:
                new_tools[i] = tool
            elif tool in machines['M' + str(i+1)].available_tools:
                new_tools[i] = tool
                n_tool += 1
        
    elif n_tools_needed == 2:
        
        tool = list(t_needed.keys())
        n_needed = [t_needed[tool[i]] for i in range(len(tool))]

        # Get number of the active tools
        n_tool = [active_tools.get(t) for t in tool]
        for i in range(len(n_tool)):
            if n_tool[i] is None:
                n_tool[i] = 0

        max_index = max(range(len(n_needed)), key=lambda x: n_needed[x])
        min_index = min(range(len(n_needed)), key=lambda x: n_needed[x])
        # Add a tool for the min index
        if n_tool[min_index] == 0:
            for i, m_t in enumerate(machine_tools):
                if tool[min_index] in machines['M' + str(i+1)].available_tools:
                    new_tools[i] = tool[min_index]
                    n_tool[min_index] += 1
                    break
        # Add the others to the max index
        for i, m_t in enumerate(machine_tools):
            if n_tool[max_index] >= n_needed[max_index] / 2:
                break
            if new_tools[i] == tool[min_index]:
                continue

            if m_t == tool[max_index]:
                new_tools[i] = tool[max_index]
                n_tool[max_index] += 1
    
    print(new_tools)

# Gets the information from the plc and acts accordingly
def handle_plc_info():
    # Handle all the pending info from the plc
    while not plc_info_queue.empty():

        # Checks the information type
        info = dict(plc_info_queue.get())
        
        # A piece left the warehouse for transformation or delivery
        if info['info_type'] == 'piece_left_wh':
            id = info['id']
            piece_type = info['piece_type']
            
            order = move_order(id, pending_orders, processing_orders)
            if order is None:
                continue
            if order in ready_to_send:
                ready_to_send.remove(order)
            
            # Remove piece from wh db
            piece_id = db.remove_piece_from_warehouse(piece_type)

            # Insert the piece_id to the order
            order.piece_id = piece_id

            # TODO: Update order status in db
        
        # A piece entered the warehouse coming from a supplier
        elif info['info_type'] == 'piece_from_supplier':

            piece_type = info['type']

            # Search the order from pending loading orders
            order = None
            for o in loading_orders:
                if o.type == ('P' + str(piece_type)):
                    order = o
                    break
            if order is None:
                continue

            # Add empty piece to the pieces db
            piece_id = db.add_piece(piece_type, order.cost, get_clock_today(), 0)

            # Add piece to the wh db
            db.add_piece_to_warehouse(piece_id)

            # TODO: Update order status in db

            # Send info to the ERP
            dictionary = {
                'info_type': 'piece_from_supplier',
                'erp_order': order.erp_id
            }
            erp_info_queue.put(dictionary)

            # Move the order from pending loading orders to finished orders
            move_order(order.order_id, loading_orders, finished_orders)

        # A piece entered the warehouse coming from a transformation
        elif info['info_type'] == 'piece_entered_wh':
            
            id = info['id']
            machine_time = info['machine_t']
            piece_type = info['piece_type']

            piece = move_order(id, processing_orders, finished_orders)
            if piece is None:
                continue

            # Update piece type
            piece.type = piece.final_type

            m = 'M' + str(piece.machine_to_use)

            # Update machine statistics
            worktime = Transformations.get_processing_time(piece.initial_type, piece.final_type, piece.tool_to_use)
            machines[m].add_work_piece(piece.type, worktime)

            # Update piece type in the piece db
            db.update_piece_type(piece.piece_id, piece_type)

            # Update piece production time in the piece db
            db.update_production_time(piece.piece_id, machine_time)
            
            # Add piece to the wh db
            db.add_piece_to_warehouse(piece.piece_id)

            # Update machine statistics in db
            db.update_machine(m, piece_type, worktime)

            # TODO: Update order status in db

            # Send info to the erp
            dictionary = {
                'info_type': 'piece_entered_wh',
                'erp_order': piece.erp_id
            }
            erp_info_queue.put(dictionary)

        # A piece got delivered
        elif info['info_type'] == 'piece_delivered':

            id = info['id']
            piece_type = info['piece_type']
            dock_no = info['dock_no']

            order = move_order(id, processing_orders, finished_orders)
            if order is None:
                continue

            docks[str(dock_no)].add_work_piece(order.type)

            # Update dock statistics in db
            db.update_dock(dock_no, piece_type)

            # TODO: Update order status in db

            # Send info to the erp
            dictionary = {
                'info_type': 'piece_delivered',
                'erp_order': order.erp_id,
                'piece_id': order.piece_id
            }
            erp_info_queue.put(dictionary)

# Prints all the statistics to the terminal
def print_statistics():

    os.system('cls')
    print(f"|-----------------------| {get_clock_time()} | MES |------------------------|")
    print("|--------------------------------------------------------------------|")
    print("|----------------------| Statistics | Machines |---------------------|")
    print("|--------------------------------------------------------------------|")
    print("| -- |       Total      |         Number of Operated Pieces          |")
    print("| -- |  Operating Time  |  Total  | P3 | P4 | P5 | P6 | P7 | P8 | P9 |")
    print("|--------------------------------------------------------------------|")
    for m in machines.keys():
        print(f"| {m} | {machines[m].operating_time:9d}        |", end='')
        print(f"  {machines[m].total_operated_work_pieces:3d}    |", end='')
        for t in machines[m].operated_work_pieces[2:]:
            print(f" {t:2d} |", end='')
        print()

    print("|--------------------------------------------------------------------|")
    print("|-----------------------| Statistics | Docks |-----------------------|")
    print("|--------------------------------------------------------------------|")
    print("| -- |           Number of Unloaded Work-Pieces                 | -- |")
    print("| -- |  Total  |  P3  |  P4  |  P5  |  P6  |  P7  |  P8  |  P9  | -- |")
    print("|--------------------------------------------------------------------|")
    for d in docks.keys():
        print(f"| D{d} | {docks[d].total_unloaded_work_pieces:4d}    |", end='')
        for t in docks[d].unload_work_pieces[2:]:
            print(f"  {t:2d}  |", end='')
        print(" -- |")
    print("|--------------------------------------------------------------------|")

# Prints all the orders for the current day
def print_orders():

    print("|---------------------------| ERP Orders |---------------------------|")
    print("|--------------------------------------------------------------------|")
    
    if (len(loading_orders) > 0) or (next((o for o in finished_orders if (isinstance(o, LoadingOrder) and o in today_orders)), None) is not None):
        print("|-------------------------| Loading Orders |-------------------------|")
        print("|--------------------------------------------------------------------|")
        print("|---------| ERP ID |   Supplier   |  Type  |   Progress   |----------|")
        print("|--------------------------------------------------------------------|")
        
        l_orders = loading_orders.copy() + [p for p in finished_orders if (isinstance(p, LoadingOrder) and p in today_orders)]
        l_orders.sort(key=lambda x: x.erp_id)

        ant_order = l_orders[0]
        count_arrived = 0
        count_order = 0
        for order in l_orders:
            if order.erp_id == ant_order.erp_id:
                if order in finished_orders:
                    count_arrived += 1
                count_order += 1
            else:
                print(f"|---------| {ant_order.erp_id:4d}   |   {ant_order.supplier}  |   {order.type}   |    {count_arrived:2d}/{count_order:2d}     |----------|")
                count_order = 1
                if order in finished_orders:
                    count_arrived = 1
                else:
                    count_arrived = 0
            ant_order = order
        print(f"|---------| {ant_order.erp_id:4d}   |   {ant_order.supplier}  |   {ant_order.type}   |    {count_arrived:2d}/{count_order:2d}     |----------|")
        print("|--------------------------------------------------------------------|")

    if (next((o for o in (pending_orders+processing_orders+finished_orders) if (isinstance(o, UnloadingOrder) and o in today_orders)), None) is not None):
        print("|------------------------| Unloading Orders |------------------------|")
        print("|--------------------------------------------------------------------|")
        print("|----------| ERP ID | Order ID | Type | Dock |   Status   |----------|")
        print("|--------------------------------------------------------------------|")
        for order in pending_orders:
            if isinstance(order, UnloadingOrder):
                if order in today_orders:
                    print(f"|----------| {order.erp_id:4d}   | {order.order_id:5d}    | {order.type}   |  {order.dock_to_deliver}   |   Pending  |----------|")
        for order in processing_orders:
            if isinstance(order, UnloadingOrder):
                print(f"|----------| {order.erp_id:4d}   | {order.order_id:5d}    | {order.type}   |  {order.dock_to_deliver}   | Processing |----------|")
        for order in finished_orders:
            if isinstance(order, UnloadingOrder):
                if order in today_orders:
                    print(f"|----------| {order.erp_id:4d}   | {order.order_id:5d}    | {order.type}   |  {order.dock_to_deliver}   |  Finished  |----------|")
        print("|--------------------------------------------------------------------|")

    if (next((o for o in (pending_orders+processing_orders+finished_orders) if (isinstance(o, TransformationOrder) and o in today_orders)), None) is not None):
        print("|---------------------| Transformation Orders |----------------------|")
        print("|--------------------------------------------------------------------|")
        print("|---| ERP ID | Order ID |   Type   | Machine | Tool |   Status   |---|")
        print("|--------------------------------------------------------------------|")
        for order in pending_orders:
            if isinstance(order, TransformationOrder):
                if order.machine_to_use != 0:
                    print(f"|---| {order.erp_id:4d}   | {order.order_id:5d}    | {order.initial_type} -> {order.final_type} | {order.machine_to_use:4d}    |  {order.tool_to_use}   |   Pending  |---|")
                else:
                    print(f"|---| {order.erp_id:4d}   | {order.order_id:5d}    | {order.initial_type} -> {order.final_type} |   TBD   |  {order.tool_to_use}   |   Pending  |---|")
        for order in processing_orders:
            if isinstance(order, TransformationOrder):
                print(f"|---| {order.erp_id:4d}   | {order.order_id:5d}    | {order.initial_type} -> {order.final_type} | {order.machine_to_use:4d}    |  {order.tool_to_use}   | Processing |---|")
        for order in finished_orders:
            if isinstance(order, TransformationOrder):
                if order in today_orders:
                    print(f"|---| {order.erp_id:4d}   | {order.order_id:5d}    | {order.initial_type} -> {order.final_type} | {order.machine_to_use:4d}    |  {order.tool_to_use}   |  Finished  |---|")
        print("|--------------------------------------------------------------------|")

if (__name__ == '__main__'):

    print(f"| {get_time()} | MES | Main Thread | INFO | Starting...")
    
    # Initialize connection with database
    db = DB_handler()
    try:
        print(f"| {get_time()} | MES | Main Thread | INFO | Connecting to the database...")
        # Connects to the database
        db.connect_db()
        print(f"| {get_time()} | MES | Main Thread | INFO | Connected to the database")
        # Setup database tables
        db.setup()
    except:
        # Connection failed
        print(f"| {get_time()} | MES | Main Thread | ERROR | Couldn't connect to the database")
        print(f"| {get_time()} | MES | Main Thread | INFO | Please, check you connection and make sure you are connected to FEUPNET (VPN)")
        print(f"| {get_time()} | MES | Main Thread | INFO | Shutting down...")
        sys.exit()

    # Get dock statistics from the database
    d_stats = db.get_dock_statistics()
    # Initialize dock variables
    docks = {
        '1': Dock(1, list(d_stats[0][-9:])),
        '2': Dock(2, list(d_stats[1][-9:]))
    }

    # Get machine statistics from the database
    m_stats = db.get_machine_statistics()
    # Initialize machine variables
    machines = {
        'M1': Machine([1, 2, 3], list(m_stats[0][-9:]), int(m_stats[0][1])),
        'M2': Machine([1, 3, 4], list(m_stats[1][-9:]), int(m_stats[1][1])),
        'M3': Machine([2, 3, 4], list(m_stats[2][-9:]), int(m_stats[2][1])),
        'M4': Machine([1, 3, 4], list(m_stats[3][-9:]), int(m_stats[3][1]))
    }
    
    # TODO: Get the unfinished orders from the database
    # Incoming loading orders
    loading_orders = []
    # Pending orders to store all the orders that are yet to start
    pending_orders = []
    # TODO: Get the processing orders from the database
    # Orders in execution
    processing_orders = []
    # Completed orders
    finished_orders = []
    # Today orders (Orders that were received today from the ERP)
    today_orders = []
    # List of the expected orders for the next two days
    next_two_days_expected_orders = []

    # Pending orders to send to the PLC
    pieces_queue = Queue()
    # Locker to avoid the read of data before the full writing
    plc_lock = Lock()
    # Information queue to handle PLC information
    plc_info_queue = Queue()
    # Queue to handle plc exceptions (when data is not sent)
    plc_exception_queue = Queue()
    # Initiate thread that communicates with the PLC
    PLC_communication_thread = PLCCommunication(pieces_queue, plc_lock, machines, plc_info_queue, plc_exception_queue)
    PLC_communication_thread.start()

    # Queue that receives the orders from the ERP
    erp_orders = Queue()
    # Locker to avoid the read of the data before the full writing
    erp_lock = Lock()
    # Queue to send informations to the ERP
    erp_info_queue = Queue()
    # Initiate thread that communicates with the ERP
    ERP_communication_thread = ERPCommunication(erp_orders, erp_lock, erp_info_queue)
    ERP_communication_thread.start()
    
    # Initiate thread that updates time
    clock_thread = ClockThread()
    clock_thread.start()

    determine_tools()
    ready_to_send = []

    try:

        # Main control loop
        while True:
            
            init_cycle_time = time()
            
            # Handles the new information from the PLC
            handle_plc_info()

            # If there is any error with the PLC communication, close the program
            if not plc_exception_queue.empty():
                e = plc_exception_queue.get()
                print(e)
                print(f"| {get_time()} | MES | Main Thread | ERROR | There was an error with the OPC UA connection")
                break

            # Gets new orders from the ERP
            new_orders = get_today_orders_from_erp()

            if len(pending_orders) + len(processing_orders) + len(loading_orders) == 0:
                next_two_days_expected_orders.sort(key=lambda x: x.planning_day)
                for order in next_two_days_expected_orders:
                    if order.planning_day != current_planning_day:
                        current_planning_day = order.planning_day
                        break
                    
                    if isinstance(order, TransformationOrder):
                        today_orders.append(order)
                        pending_orders.append(order)
                        new_orders = True

            # If its a new day
            if new_orders:

                # Schedule the orders (which ones to execute first)
                schedule_pending_orders()

                # Determine the docks to use
                determine_docks()
                
                # Determine best tool set for each machine
                determine_tools()

                ready_to_send = []

            # Check if the machines are ready to send the pieces to the plc
            m_ready = [machines['M1'].ready, machines['M2'].ready, machines['M3'].ready, machines['M4'].ready]
            for order in ready_to_send:
                if isinstance(order, TransformationOrder) and order.machine_to_use != 0:
                    m_ready[order.machine_to_use - 1] = False
            changed = False
            for order in pending_orders:
                # If the order is already in the queue to send, pass to the next one
                if order in ready_to_send:
                    continue
                
                # If it's an unloading order and the dock is defined, then send it
                if isinstance(order, UnloadingOrder):
                    if order.dock_to_deliver != 0:
                        ready_to_send.append(order)
                        changed = True
                # If it's a transformation order and the machine is empty, then send it
                elif isinstance(order, TransformationOrder):
                    
                    # Decide which machine to use for each transformation order
                    if order.machine_to_use == 0:
                        tool = Transformations.get_tool(order.initial_type, order.final_type)
                        if m_ready[0] and machines['M1'].active_tool == machines['M1'].new_tool == tool:
                            order.machine_to_use = 1
                        elif m_ready[1] and machines['M2'].active_tool == machines['M2'].new_tool == tool:
                            order.machine_to_use = 2
                        elif m_ready[2] and machines['M3'].active_tool == machines['M3'].new_tool == tool:
                            order.machine_to_use = 3
                        elif m_ready[3] and machines['M4'].active_tool == machines['M4'].new_tool == tool:
                            order.machine_to_use = 4

                    # If it's available send the transformation to the machine
                    if order.machine_to_use != 0  and m_ready[order.machine_to_use - 1]:
                        if machines['M'+str(order.machine_to_use)].active_tool == order.tool_to_use:
                            ready_to_send.append(order)
                            m_ready[order.machine_to_use - 1] = False
                            changed = True

            # TODO: Insert the ready pieces to the plc
            if changed:
                with plc_lock:
                    # Remove all the pieces from the plc queue
                    while not pieces_queue.empty():
                        pieces_queue.get()
                    
                    # Send pieces first to M2 and then to M1

                    # Search for pieces to M1 and to M2
                    p_m_1 = p_m_2 = None
                    for i, p in enumerate(ready_to_send):
                        if isinstance(p, TransformationOrder):
                            if p.machine_to_use == 1:
                                p_m_1 = (i, p)
                            elif p.machine_to_use == 2:
                                p_m_2 = (i, p)

                    # Check if there are pieces to send to both M1 and M2
                    if p_m_1 is not None and p_m_2 is not None:
                        # Send first to M2
                        if p_m_1[0] < p_m_2[0]:
                            ready_to_send[p_m_1[0]], ready_to_send[p_m_2[0]] = ready_to_send[p_m_2[0]], ready_to_send[p_m_1[0]]

                    # Insert the pieces in the new schedulled way
                    for piece in ready_to_send:
                        pieces_queue.put(piece)

            # Update machine tools
            for i, m in enumerate(machines.keys()):
                for p in (processing_orders + ready_to_send):
                    if isinstance(p, TransformationOrder):
                        if p.machine_to_use == int(m[1]):
                            break
                else:
                    if machines[m].ready:
                        machines[m].new_tool = new_tools[i]

            # Shows all the statistics in the terminal
            print_statistics()

            # Show ERP orders
            print_orders()

            # Wait for the next cycle
            sleep_next_cycle(init_cycle_time, MAIN_LOOP_CYCLE)
            
    except Exception as e:
        print(traceback.format_exc())


    # Closes the connection with the database
    db.close_db()
    # Closes the thread that communicates with the PLC
    PLC_communication_thread.stop()
    # Closes the thread that communicates with the ERP
    ERP_communication_thread.stop()
    # Closes the thread that handles the clock
    clock_thread.stop()

    print(f"| {get_time()} | MES | Main Thread | INFO | Shutting down...")