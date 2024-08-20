from order import TransformationOrder, UnloadingOrder
from transformation import Transformations

class task_t:
    def __init__(self, machine = 0, tool = 0, work_time = 0, type_out = 0):
        self.machine = machine
        self.tool = tool
        self.work_time = work_time
        self.type_out = type_out

class piece_t:
    def __init__(self, id = 0, type_ = 0, tasks = [task_t(), task_t()], deliver = 0, machine_t = 0):
        self.id = id
        self.type_ = type_
        self.tasks = tasks
        self.deliver = deliver
        self.machine_t = machine_t

class piece_delivered_t:
    def __init__(self, id = 0, type_ = 0):
        self.id = id
        self.type_ = type_

def order_to_piece_t(order, machines):
    
    if isinstance(order, TransformationOrder):
        t = Transformations.get_processing_time(order.initial_type, order.final_type, order.tool_to_use)*1000
        tool = machines['M'+str(order.machine_to_use)].get_tool_index(order.tool_to_use)
        return piece_t(order.order_id, int(order.initial_type[1]), [task_t(order.machine_to_use, tool, t, int(order.final_type[1])), task_t()], 0, 0)
    elif isinstance(order, UnloadingOrder):
        return piece_t(order.order_id, int(order.type[1]), [task_t(), task_t()], int(order.dock_to_deliver), 0)