from clock import get_clock_today

class ClientOrder:

    def __init__(self, client_name, number, piece, quantity, due_date, late_penalty, early_penalty):
        
        #define client order variables
        self.name = client_name
        self.number = number
        self.piece = piece
        self.quantity = quantity
        self.due_date = due_date
        self.late_penalty = late_penalty
        self.early_penalty = early_penalty
        
        self.n_delivered = 0
        self.delivery_day = get_clock_today() + due_date
        self.planning_day = get_clock_today() + due_date

        #set innitial condictions to 0
        self.cost = 0.0
        self.raw_cost = 0.0
        self.production_cost = 0.0
        self.depreciation_cost = 0.0
        self.production_time = 0.0
        self.arrival_date = 0.0
        self.dispatch_date = 0.0

    # Adds a piece to the n_delivered and updates costs
    def add_delivered_piece(self, raw_cost, arrival_date, dispatch_date, production_time):

        # Update production time
        self.production_time = (self.production_time * self.n_delivered + production_time) / (self.n_delivered + 1)
        # Update arrival date
        self.arrival_date = (self.arrival_date * self.n_delivered + arrival_date) / (self.n_delivered + 1)
        # Update dispatch date
        self.dispatch_date = (self.dispatch_date * self.n_delivered + dispatch_date) / (self.n_delivered + 1)
        
        # Update raw cost
        self.raw_cost = (self.raw_cost * self.n_delivered + raw_cost) / (self.n_delivered + 1)
        # Update depreciation cost
        self.depreciation_cost = self.raw_cost * (self.dispatch_date - self.arrival_date) * 0.01
        # Update production cost
        self.production_cost = self.production_time * 1.0
        # Update total cost
        self.cost = self.raw_cost + self.depreciation_cost + self.production_cost

        # Update number of delivered pieces
        self.n_delivered += 1