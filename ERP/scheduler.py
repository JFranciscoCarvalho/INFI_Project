from client_order import ClientOrder
from clock import get_clock_today
from order import *
from transformation import Transformations

class MasterScheduler:

    def __init__(self):
        self.master_plan = []
        self.overload = 40

    # Adds the days until current day or until a n_days
    def build_master_plan_structure(self, master_plan, n_days=0):
        last_day = max(n_days, get_clock_today(), len(master_plan))
        if last_day > len(master_plan):
            for _ in range(len(master_plan), last_day):
                master_plan.append({
                    'ExpeditionOrders': [],
                    'ProductionOrders': [],
                    'SupplierNeeds': []
                })

    # Returns a shallow copy of master plan
    def get_master_plan_copy(self, master_plan):
        self.build_master_plan_structure(master_plan)
        master_plan_copy = []
        for d in range(len(master_plan)):
            master_plan_copy.append({
                'ExpeditionOrders': [p for p in master_plan[d]['ExpeditionOrders']],
                'ProductionOrders': [p for p in master_plan[d]['ProductionOrders']],
                'SupplierNeeds': []
            })
        return master_plan_copy

    def master_scheduler_system(self, client_orders: list[ClientOrder]):
        
        if len(client_orders) == 0:
            return

        client_orders = [DeliveryOrder(order.number, order.piece, order.quantity, order.delivery_day, 'Schedulling') for order in client_orders]
        
        backup = self.get_master_plan_copy(self.master_plan)

        while True:

            client_orders.sort(key=lambda x: x.planning_day)
            last_day = client_orders[-1].planning_day
            
            self.build_master_plan_structure(backup, last_day)
            self.master_plan = self.get_master_plan_copy(backup)

            # Plan expedition orders
            for order in client_orders:

                planning_day = order.planning_day
                
                for d in range(planning_day-1, len(self.master_plan)):
                    
                    daily_orders = self.master_plan[d]
                    
                    expected_number_of_pieces = sum(expedition_order.quantity for expedition_order in daily_orders['ExpeditionOrders'])
                    if expected_number_of_pieces + order.quantity <= 8:
                        daily_orders['ExpeditionOrders'].append(order)
                        break
                else:
                    self.master_plan.append({
                        'ExpeditionOrders': [order],
                        'ProductionOrders': [],
                        'SupplierNeeds': []
                    })

            pending_pieces = []
            
            # Plan transformation orders
            for d in range(len(self.master_plan)-1, get_clock_today(), -1):
                
                daily_orders = self.master_plan[d]

                # Calculate available time for this day
                available_time = 240
                for p in daily_orders['ProductionOrders']:
                    processing_time = Transformations.get_processing_time(p.initial_type, p.final_type, Transformations.get_tool(p.initial_type, p.final_type))
                    available_time -= p.quantity * (processing_time + self.overload)

                pending_pieces.sort(key=lambda x: x.planning_day, reverse=True)
                
                new_pending_pieces = []
                for p in pending_pieces:

                    processing_time = Transformations.get_processing_time(p.initial_type, p.final_type, Transformations.get_tool(p.initial_type, p.final_type))
                    total_processing_time = (processing_time + self.overload) * p.quantity

                    max_quantity = min(int(available_time / (processing_time + self.overload)), p.quantity)

                    if max_quantity == p.quantity:
                        daily_orders['ProductionOrders'].append(p)
                        available_time -= total_processing_time
                    elif max_quantity > 0:
                        daily_orders['ProductionOrders'].append(TransformationOrder(p.number, p.initial_type, p.final_type, max_quantity, d+1))
                        available_time -= (processing_time + self.overload) * max_quantity
                        new_pending_pieces.append(TransformationOrder(p.number, p.initial_type, p.final_type, p.quantity-max_quantity, d+1))
                    else:
                        new_pending_pieces.append(p)
                        continue
                        
                    # Send a transformation to the previous day with the needed material
                    match p.initial_type:
                        case 'P9':
                            new_pending_pieces.append(TransformationOrder(p.number, 'P7', 'P9', max_quantity, d))
                        case 'P8':
                            new_pending_pieces.append(TransformationOrder(p.number, 'P6', 'P8', max_quantity, d))
                        case 'P7':
                            new_pending_pieces.append(TransformationOrder(p.number, 'P4', 'P7', max_quantity, d))
                        case 'P6':
                            new_pending_pieces.append(TransformationOrder(p.number, 'P1', 'P6', max_quantity, d))
                        case 'P5':
                            new_pending_pieces.append(TransformationOrder(p.number, 'P9', 'P5', max_quantity, d))
                        case 'P4':
                            new_pending_pieces.append(TransformationOrder(p.number, 'P2', 'P4', max_quantity, d))
                        case 'P3':
                            new_pending_pieces.append(TransformationOrder(p.number, 'P2', 'P3', max_quantity, d))
                
                pending_pieces = new_pending_pieces

                # Send transformation orders for the previous day
                for order in self.master_plan[d]['ExpeditionOrders']:
                    if order.state == 'Schedulling':
                        match order.type:
                            case 'P9':
                                pending_pieces.append(TransformationOrder(order.number, 'P7', 'P9', order.quantity, d))
                            case 'P8':
                                pending_pieces.append(TransformationOrder(order.number, 'P6', 'P8', order.quantity, d))
                            case 'P7':  
                                pending_pieces.append(TransformationOrder(order.number, 'P4', 'P7', order.quantity, d))
                            case 'P6':
                                pending_pieces.append(TransformationOrder(order.number, 'P1', 'P6', order.quantity, d))
                            case 'P5':
                                pending_pieces.append(TransformationOrder(order.number, 'P9', 'P5', order.quantity, d))
                            case 'P4':
                                pending_pieces.append(TransformationOrder(order.number, 'P2', 'P4', order.quantity, d))
                            case 'P3':
                                pending_pieces.append(TransformationOrder(order.number, 'P2', 'P3', order.quantity, d))

            # If there are pending transformation orders to schedule delay an expedition order
            if len(pending_pieces) == 0:
                break
            else:

                pending_pieces.sort(key=lambda x: x.planning_day, reverse=False)
                i = False
                for d in range(len(self.master_plan)):
                    if i:
                        break
                    for expedition_order in self.master_plan[d]['ExpeditionOrders']:
                        if expedition_order.number == pending_pieces[0].number:
                            expedition_order.planning_day += 1
                            i = True
                            break

        # Plan Supplier Needs
        # Calculate the needed raw materials for each day
        for d in range(len(self.master_plan)):
            daily_orders = self.master_plan[d]
            for p in daily_orders['ProductionOrders']:
                if p.initial_type == 'P1':
                    if d == 0:
                        self.master_plan[0]['SupplierNeeds'].append(LoadingOrder(p.number, None, 'P1', p.quantity, None, d))
                    else:
                        self.master_plan[d-1]['SupplierNeeds'].append(LoadingOrder(p.number, None, 'P1', p.quantity, None, d))
                elif p.initial_type == 'P2':
                    if d == 0:
                        self.master_plan[0]['SupplierNeeds'].append(LoadingOrder(p.number, None, 'P2', p.quantity, None, d))
                    else:
                        self.master_plan[d-1]['SupplierNeeds'].append(LoadingOrder(p.number, None, 'P2', p.quantity, None, d))

        # Change state of delivery orders from schedulling to pending
        for daily_orders in self.master_plan:
            for expedition_order in daily_orders['ExpeditionOrders']:
                if expedition_order.state == 'Schedulling':
                    expedition_order.state = 'Pending'

        # Change planning days for all the orders
        for d in range(len(self.master_plan)):
            daily_orders = self.master_plan[d]
            for e in daily_orders['ExpeditionOrders']:
                e.planning_day = d+1
            for p in daily_orders['ProductionOrders']:
                p.planning_day = d+1
            for s in daily_orders['SupplierNeeds']:
                s.planning_day = d+1

        # Try to avoid delivering the orders late
        for d in range(len(self.master_plan)):
            daily_orders = self.master_plan[d]
            # Checks every expedition order
            for e in daily_orders['ExpeditionOrders']:
                # If it was delayed throughout the schedulling try to fix it
                if e.planning_day > e.delivery_day:
                    old_list = daily_orders['ExpeditionOrders']
                    # Checks for every day between the planning_day and the delivery_day
                    for day in range(e.planning_day - 1, e.delivery_day - 2, -1):
                        orders = self.master_plan[day]
                        
                        # If there are production orders in this day, it cannot be delivered earlier
                        p_order = self.check_production_orders(orders['ProductionOrders'], e.number)
                        if p_order:
                            break

                        # Try to add it
                        expected_number_of_pieces = sum(expedition_order.quantity for expedition_order in orders['ExpeditionOrders'])
                        if expected_number_of_pieces + e.quantity <= 8:
                            e.planning_day = day + 1
                            old_list.remove(e)
                            orders['ExpeditionOrders'].append(e)
                            old_list = orders['ExpeditionOrders']

    def check_production_orders(self, production_orders, number):
        for o in production_orders:
            if o.number == number:
                return True
        return False

    def get_master_plan(self):
        self.build_master_plan_structure(self.master_plan)
        return self.master_plan

    def print_master_plan(self):
        self.build_master_plan_structure(self.master_plan)

        for i, row in enumerate(self.master_plan):
            print (i+1)
            for p in row['ExpeditionOrders']:
                print(p.number, p.type, p.quantity)
            for p in row['ProductionOrders']:
                print(p.number, p.initial_type, p.final_type, p.quantity)
            for p in row['SupplierNeeds']:
                print(p.number, p.type, p.quantity)
            print()