from supplier import Supplier

class PurchasingPlanner:

    def __init__(self, purchase_plan):
        self.plan = purchase_plan

        self.pending_P1 = 0
        self.pending_P2 = 0
    
    def update_plan( self,  current_day, master_plan, inventory):

        # Check if there are supplier needs for the next day
        count_P1 = count_P2 = 0
        for p in master_plan[min(current_day, len(master_plan)-1)]['SupplierNeeds']:
            if p.type == 'P1':
                count_P1 += p.quantity
            elif p.type == 'P2':
                count_P2 += p.quantity
        if (count_P1 - inventory[0] - self.pending_P1 > 0):
            incoming = max(count_P1 - inventory[0] - self.pending_P1, 4)
            if self.check_warehouse_capacity(inventory, incoming):
                self.plan.append([current_day, 'SupplierC', 'P1', incoming, 55])
                self.pending_P1 += incoming
        if (count_P2 - inventory[1] - self.pending_P2 > 0):
            incoming = max(count_P2 - inventory[1] - self.pending_P2, 4)
            if self.check_warehouse_capacity(inventory, incoming):
                self.plan.append([current_day, 'SupplierC', 'P2', incoming, 18])
                self.pending_P2 += incoming
        
        count_P1 = count_P2 = 0
        for test_day in range(min(current_day + 1, len(master_plan) - 1), min(current_day + 4, len(master_plan))):
            for p in master_plan[test_day]['SupplierNeeds']:
                if p.type == 'P1':
                    count_P1 += p.quantity
                elif p.type == 'P2':
                    count_P2 += p.quantity
        if (count_P1 - inventory[0] - self.pending_P1 > 4):
            incoming = max(count_P1 - inventory[0] - self.pending_P1, 8)
            if self.check_warehouse_capacity(inventory, incoming):
                self.plan.append([current_day, 'SupplierB', 'P1', incoming, 45])
                self.pending_P1 += incoming
        if (count_P2 - inventory[1] - self.pending_P2 > 4):
            incoming = max(count_P2 - inventory[1] - self.pending_P2, 8)
            if self.check_warehouse_capacity(inventory, incoming):
                self.plan.append([current_day, 'SupplierB', 'P2', incoming, 15])
                self.pending_P2 += incoming

        count_P1 = count_P2 = 0
        first_day_P1 = first_day_P2 = 0
        for test_day in range(min(current_day + 4, len(master_plan) - 1), len(master_plan)):
            for p in master_plan[test_day]['SupplierNeeds']:
                if p.type == 'P1':
                    count_P1 += p.quantity
                    if (first_day_P1 == 0) and (count_P1 - inventory[0] - self.pending_P1 > 0):
                        first_day_P1 = test_day
                elif p.type == 'P2':
                    count_P2 += p.quantity
                    if (first_day_P2 == 0) and (count_P2 - inventory[1] - self.pending_P2 > 0):
                        first_day_P2 = test_day
        if (count_P1 - inventory[0] - self.pending_P1 > 12):
            if (first_day_P1 <= current_day + 5):
                incoming = 16
                if self.check_warehouse_capacity(inventory, incoming):
                    self.plan.append([current_day, 'SupplierA', 'P1', incoming, 30])
                    self.pending_P1 += incoming
        if (count_P2 - inventory[1] - self.pending_P2 > 12):
            if (first_day_P2 <= current_day + 5):
                incoming = 16
                if self.check_warehouse_capacity(inventory, incoming):
                    self.plan.append([current_day, 'SupplierA', 'P2', incoming, 10])
                    self.pending_P2 += incoming
        
    def check_warehouse_capacity(self, inventory, quantity):
        return (sum(inventory) + self.pending_P1 + self.pending_P2 + quantity < 32)
    
    def get_plan ( self ):
        return self.plan

    def update_pending(self, piece, quantity):
        if( piece == 'P1'):
            self.pending_P1 -= quantity
        elif( piece == 'P2' ):
            self.pending_P2 -= quantity