class Order:

    def __init__(self, erp_id, order_id, type, planning_day):
        self.erp_id = erp_id
        self.order_id = order_id
        self.type = type

        self.planning_day = planning_day

class TransformationOrder(Order):
    
    def __init__(self, erp_id, order_id, initial_type, final_type, planning_day):
        super().__init__(erp_id, order_id, initial_type, planning_day)

        self.initial_type = initial_type
        self.final_type = final_type

        self.piece_id = 0
        self.machine_to_use = 0
        self.tool_to_use = 0

class UnloadingOrder(Order):

    def __init__(self, erp_id, order_id, type, planning_day):
        super().__init__(erp_id, order_id, type, planning_day)

        self.piece_id = 0
        self.dock_to_deliver = 0

class LoadingOrder(Order):
    
    def __init__(self, erp_id, order_id, supplier, type, cost, planning_day):
        super().__init__(erp_id, order_id, type, planning_day)

        self.supplier = supplier
        self.cost = cost