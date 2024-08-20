order_counter = 1

class Order:
    def __init__(self, number, quantity, planning_day, state):
        global order_counter

        self.number = number
        self.id = order_counter
        self.quantity = quantity
        self.n_completed = 0
        self.planning_day = planning_day
        self.state = state

        order_counter += 1

class TransformationOrder(Order):
    def __init__(self, number, initial_type, final_type, quantity, planning_day = 0):
        
        super().__init__(number, quantity, planning_day, 'Pending')

        self.initial_type = initial_type
        self.final_type = final_type

class DeliveryOrder(Order):
    def __init__(self, number, type, quantity, planning_day = 0, state = 'Pending'):
        
        super().__init__(number, quantity, planning_day, state)

        self.delivery_day = planning_day
        self.type = type

class LoadingOrder(Order):
    def __init__(self, number, name, type, quantity, cost, planning_day = 0):
    
        super().__init__(number, quantity, planning_day, 'Pending')

        self.name = name
        self.type = type
        
        self.cost = cost