import sys
import os 
from queue import Queue
from threading import Lock
from time import time

from client_communication_thread import ClientCommunication
from clock import *
from database import DB_handler
from mes_communication_thread import MESCommunication
from order import *
from purchasing_planner import PurchasingPlanner
from scheduler import MasterScheduler
from supplier import Supplier


# Inserts all the pending orders from client to the client_orders list
def get_orders_from_client():
    if client_orders_queue.empty():
        return None

    new_orders = []
    with client_lock:
        # Get all the orders from the client queue
        while not client_orders_queue.empty():
            order = client_orders_queue.get()
            client_orders.append(order)
            new_orders.append(order)
    return new_orders

# Sends the orders to the MES
def send_orders_to_mes():
    # Locks the queue and send every order for the next 3 days
    with mes_lock:
        for order in daily_orders:
            erp_orders.put(order)

# Checks the current day with the MES
def negociate_time_with_mes():
    d, s = mes_communication_thread.negociate_time()
    if d is not None:
        set_time(d, s, time() - s)

# Gets the information from the MES and acts accordingly
def handle_mes_info():
    # Handle all the pending info from the MES
    while not mes_info_queue.empty():

        # Checks the information type
        info = dict(mes_info_queue.get())
        
        info_type = info['info_type']
        erp_order_id = info['erp_order']

        order = next((o for o in daily_orders if o.id == erp_order_id), None)
        if order is None:
            continue

        order.n_completed += 1

        # A piece entered the wh coming from a supplier
        if info_type == 'piece_from_supplier':
            if order.n_completed == order.quantity:
                order.state = 'Completed'
                sourcing_orders.remove(order)
        # A piece entered the wh after finishing a transformation
        elif info_type == 'piece_entered_wh':
            if order.n_completed == order.quantity:
                order.state = 'Completed'
                production_orders.remove(order)
        elif info_type == 'piece_delivered':

            # Get piece id
            piece_id = info['piece_id']

            if order.n_completed == order.quantity:
                order.state = 'Completed'
                expedition_orders.remove(order)

            # Search for the respective client order
            client_order = next((o for o in client_orders if o.number == order.number), None)
            if client_order is None:
                continue
            
            # Get the data from the database
            arrival_day, cost, production_time = db.get_piece_data(piece_id)
            # Update cost of the order
            client_order.add_delivered_piece(cost, arrival_day, current_day, production_time)

# Returns the current stored inventory in the database
def update_inventory():
    db_inventory = db.get_warehouse_piece_counts()

    inventory = [0]*9
    for (piece_type, piece_count) in db_inventory.items():
        inventory[piece_type-1] = piece_count

    return inventory

# Determines the expedition orders for the current day
def plan_expedition():
    n_count = 0
    for i in range(0, current_day):
        if n_count >= 8:
                break
        for p in master_plan[i]['ExpeditionOrders']:
            if p.state != 'Pending':
                continue
            index = int(p.type[1]) - 1
            if inventory[index] >= p.quantity and n_count + p.quantity <= 8:
                expedition_orders.append(p)
                inventory[index] -= p.quantity
                p.state = 'Processing'
                n_count += p.quantity

# Determines the production orders for the current day
def plan_prodution():
    needed_pieces = [0]*9
    for i in range(len(needed_pieces)):
        needed_pieces[i] -= inventory[i]

    for i in range(0, current_day):
        for p in master_plan[i]['ProductionOrders']:
            if p.state != 'Pending':
                continue
            index = int(p.initial_type[1])-1
            needed_pieces[index] += p.quantity
            if needed_pieces[index] <= 0:
                p.state = 'Processing'
                production_orders.append(p)

# Determines the supplier orders for the current day
def plan_sourcing():    
    purchase_plan = buy_plan.get_plan()

    for plan in purchase_plan:
        for supplier in suppliers:
            if (plan[1] == supplier.name and current_day == plan[0] + supplier.delivery):
                sourcing_orders.append(LoadingOrder(0, plan[1], plan[2], plan[3], plan[4], current_day))
                buy_plan.update_pending(plan[2], plan[3])

# Prints all the client orders and its status
def print_client_orders():

    os.system('cls')
    
    print(f"|--------------------------------------| {get_clock_time()} | ERP |-----------------------------------|")
    print("|------------------------------------- Current Inventory --------------------------------------|")
    print("|-------------------| Total | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 |---------------------|")
    print(f"|-------------------| {sum(inventory):3d}   | {inventory[0]:2d} | {inventory[1]:2d} | {inventory[2]:2d} | {inventory[3]:2d} | {inventory[4]:2d} | {inventory[5]:2d} | {inventory[6]:2d} | {inventory[7]:2d} | {inventory[8]:2d} |---------------------|")
    print("|----------------------------------------------------------------------------------------------|")
    print("|-------------------------------------- Client Orders  ----------------------------------------|")
    print("|----------------------------------------------------------------------------------------------|")
    print("|       Client       |   Number  |  Type | Quantity | DueDate | LP | EP | DeliveryDay |  Cost  |")
    for order in client_orders:
        if order.cost > 0:
            print(f"|{order.name:^20s}|   {order.number:^4s}    |  {order.piece}   | {order.quantity:4d}     | {order.due_date:4d}    | {order.late_penalty:2d} | {order.early_penalty:2d} |    {int(order.dispatch_date):3d}      | {order.cost:.2f}  |")
        else:
            print(f"|{order.name:^20s}|   {order.number:^4s}    |  {order.piece}   | {order.quantity:4d}     | {order.due_date:4d}    | {order.late_penalty:2d} | {order.early_penalty:2d} |      -      | ------ |")
    print("|----------------------------------------------------------------------------------------------|")
    print("")

# Prints all the supplier orders
def print_supplier_orders(): 

    print("|-------------------------Supplier Orders -------------------------|")
    print("|------------------------------------------------------------------|")
    print("| Order Date |   Supplier  | Quantity to order | Piece Type | Cost |")
    for row in buy_plan.plan:
        print(f"|     {row[0]:2d}     | {row[1]}   |        {row[3]:2d}         |     {row[2]}     |  {row[4]}  |")
    print("|------------------------------------------------------------------|")
    print("")

# Print all the transformation orders for the next 10 days
def print_planning(): 
    i=0
    print("|--------------------------| Production Plan |-------------------------|")
    print("|----------------------------------------------------------------------|")
    print("|   Number   | Transformation | Quantity | Expected Date of Production |")
    for i in range(current_day-1, min(current_day+10, len(master_plan))):
        for orders in master_plan[i]['ProductionOrders']:
            print(f"|    {orders.number:^4s}    |   {orders.initial_type} --> {orders.final_type}    |     {orders.quantity}    |              {orders.planning_day:3d}            |")
    print("|----------------------------------------------------------------------|")

if (__name__ == '__main__'):

    try:
        
        print(f"| {get_time()} | ERP | Main Thread | INFO | Starting...")

        # Initialize connection with database
        db = DB_handler()
        try:
            print(f"| {get_time()} | ERP | Main Thread | INFO | Connecting to the database...")
            # Connect to the database
            db.connect_db()
            print(f"| {get_time()} | ERP | Main Thread | INFO | Connected to the database")
            # Setup database tables
            db.setup()
        except:
            # Connection failed
            print(f"| {get_time()} | ERP | Main Thread | ERROR | Couldn't connect to the database")
            print(f"| {get_time()} | ERP | Main Thread | INFO | Please, check you connection and make sure you are connected to FEUPNET (VPN)")
            print(f"| {get_time()} | ERP | Main Thread | INFO | Shutting down...")
            sys.exit()

        # Initialize suppliers variables
        suppliers = [
            Supplier('SupplierA', 16, 4, 30, 10),
            Supplier('SupplierB',  8, 2, 45, 15),
            Supplier('SupplierC',  4, 1, 55, 18)
        ]
        
        # TODO: Get unfinished client orders from the database
        client_orders = []

        # 
        daily_orders = []
        expedition_orders = []
        production_orders = []
        sourcing_orders = []

        # Queue for sending ERP orders to the MES
        erp_orders = Queue()
        # Locker to prevent the MES thread from sending data before finishing the writing
        mes_lock = Lock()
        # Queue to receive information from the MES
        mes_info_queue = Queue()
        # Initiate thread that communicates with the MES
        mes_communication_thread = MESCommunication(erp_orders, mes_lock, mes_info_queue)
        # Register the current day
        negociate_time_with_mes()
        # Start the thread that communicates with the MES
        mes_communication_thread.start()

        # Queue for receiving client orders
        client_orders_queue = Queue()
        # Locker to prevent the Plannig before all the orders arrive
        client_lock = Lock()
        # Initiate thread that communicates with the client
        client_communication_thread = ClientCommunication(client_orders_queue, client_lock)
        client_communication_thread.start()

        # Initiate thread that updates time
        clock_thread = ClockThread()
        clock_thread.start()

        # Creates the schedulling for the orders
        scheduler = MasterScheduler()
        # Creates the schedulling for the raw material shoppings
        purchase_plan = []
        buy_plan = PurchasingPlanner(purchase_plan)

        # Get current inventory
        inventory = update_inventory()

        current_day = -1
        # Main control loop
        while True:

            # Handles the new information from the MES
            handle_mes_info()

            # Check if there are new orders from the client
            new_orders = get_orders_from_client()

            # If there are new orders, remake the schedule
            if new_orders is not None:
                # Update master scheduler
                scheduler.master_scheduler_system(new_orders)

            # Plans the buying of raw material
            if get_clock_seconds() >= 58:
                buy_plan.update_plan(current_day, scheduler.get_master_plan(), inventory)

            # Update Inventory
            # TODO: The inventory doesn't consider the pieces that are currently in the production line
            inventory = update_inventory()

            # Gets the current master planning
            master_plan = scheduler.get_master_plan()

            # New day
            if get_clock_today() != current_day:
                current_day = get_clock_today()

                # Plan Expedition Orders for the current day
                plan_expedition()
                
                # Plan Production Orders for the current day
                plan_prodution()

                # Plan sourcing for the current day
                plan_sourcing()

                # Create the list with all the orders for the current day to send to the MES
                daily_orders = expedition_orders + production_orders + sourcing_orders

                # Send orders to the MES
                send_orders_to_mes()


            print_client_orders()

            print_supplier_orders()

            print_planning()

            sleep(1.0)

    finally:
        
        # Closes the database connection
        db.close_db()
        # Close thread that communicates with the MES
        mes_communication_thread.stop()
        # Close thread that communicates with the client
        client_communication_thread.stop()
        # Close thread that updates clock
        clock_thread.stop()

        print(f"| {get_time()} | MES | Main Thread | INFO | Shutting down...")