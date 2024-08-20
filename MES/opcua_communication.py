from opcua import Client, ua

from plc_variable_types import *

class OPCUAClient:

    def __init__(self, url = "opc.tcp://localhost:4840/", timeout = 1000):
        self.client = Client(url, timeout)

    # Connects to the PLC
    def connect(self):
        self.client.connect()

    # Disconnects with the PLC
    def disconnect(self):
        self.client.disconnect()

    # Reads variable from PLC (bool/uint/array)
    def read(self, node_id):
        node = self.client.get_node(node_id)
        return node.get_value()
    
    # Reads a piece_t variable from PLC
    def read_piece_t(self, node_id):
        # get the node of the variable
        id_node = self.client.get_node(node_id + ".id")
        type_node = self.client.get_node(node_id + ".type_")
        task1_machine_node = self.client.get_node(node_id + ".tasks[1].machine")
        task1_tool_node = self.client.get_node(node_id + ".tasks[1].tool")
        task1_work_time_node = self.client.get_node(node_id + ".tasks[1].work_time")
        task1_type_out_node = self.client.get_node(node_id + ".tasks[1].type_out")
        task2_machine_node = self.client.get_node(node_id + ".tasks[2].machine")
        task2_tool_node = self.client.get_node(node_id + ".tasks[2].tool")
        task2_work_time_node = self.client.get_node(node_id + ".tasks[2].work_time")
        task2_type_out_node = self.client.get_node(node_id + ".tasks[2].type_out")
        deliver_node = self.client.get_node(node_id + ".deliver")
        machine_t_node = self.client.get_node(node_id + ".machine_t")

        # write a new value to the variable
        id = id_node.get_value()
        type_ = type_node.get_value()
        task1_machine = task1_machine_node.get_value()
        task1_tool = task1_tool_node.get_value()
        task1_work_time = task1_work_time_node.get_value()
        task1_type_out = task1_type_out_node.get_value()
        task2_machine = task2_machine_node.get_value()
        task2_tool = task2_tool_node.get_value()
        task2_work_time = task2_work_time_node.get_value()
        task2_type_out = task2_type_out_node.get_value()
        deliver = deliver_node.get_value()
        machine_t = machine_t_node.get_value()

        task1 = task_t(task1_machine, task1_tool, task1_work_time, task1_type_out)
        task2 = task_t(task2_machine, task2_tool, task2_work_time, task2_type_out)
        return piece_t(id, type_, [task1, task2], deliver, machine_t)
    
    # Reads a piece_delivered_t variable from PLC
    def read_piece_delivered_t(self, node_id):
        id_node = self.client.get_node(node_id + ".id")
        type_node = self.client.get_node(node_id + ".type_")
        
        id = id_node.get_value()
        type_ = type_node.get_value()

        return piece_delivered_t(id, type_)

    # Writes a boolean value to a PLC variable
    def write_bool(self, node_id, value):
        node = self.client.get_node(node_id)
        node.set_value(value, ua.VariantType.Boolean)
    
    # Writes a uint value/array to a PLC Variable
    def write_uint(self, node_id, value):
        node_id = self.client.get_node(node_id)
        node_id.set_value(value, ua.VariantType.UInt16)

    # Writes a piece_t variable to PLC
    def write_piece_t(self, node_id, piece: piece_t):
        # get the node of the variable
        id_node = self.client.get_node(node_id + ".id")
        type_node = self.client.get_node(node_id + ".type_")
        task1_machine_node = self.client.get_node(node_id + ".tasks[1].machine")
        task1_tool_node = self.client.get_node(node_id + ".tasks[1].tool")
        task1_work_time_node = self.client.get_node(node_id + ".tasks[1].work_time")
        task1_type_out_node = self.client.get_node(node_id + ".tasks[1].type_out")
        task2_machine_node = self.client.get_node(node_id + ".tasks[2].machine")
        task2_tool_node = self.client.get_node(node_id + ".tasks[2].tool")
        task2_work_time_node = self.client.get_node(node_id + ".tasks[2].work_time")
        task2_type_out_node = self.client.get_node(node_id + ".tasks[2].type_out")
        deliver_node = self.client.get_node(node_id + ".deliver")
        machine_t_node = self.client.get_node(node_id + ".machine_t")

        # write a new value to the variable
        id = ua.Variant(piece.id, ua.VariantType.UInt16)
        type_ = ua.Variant(piece.type_, ua.VariantType.UInt16)
        task1_machine = ua.Variant(piece.tasks[0].machine, ua.VariantType.UInt16)
        task1_tool = ua.Variant(piece.tasks[0].tool, ua.VariantType.UInt16)
        task1_work_time = ua.Variant(piece.tasks[0].work_time, ua.VariantType.Int64)
        task1_type_out = ua.Variant(piece.tasks[0].type_out, ua.VariantType.UInt16)
        task2_machine = ua.Variant(piece.tasks[1].machine, ua.VariantType.UInt16)
        task2_tool = ua.Variant(piece.tasks[1].tool, ua.VariantType.UInt16)
        task2_work_time = ua.Variant(piece.tasks[1].work_time, ua.VariantType.Int64)
        task2_type_out = ua.Variant(piece.tasks[1].type_out, ua.VariantType.UInt16)
        deliver = ua.Variant(piece.deliver, ua.VariantType.UInt16)
        machine_t = ua.Variant(piece.machine_t, ua.VariantType.Int64)

        # write the values to the nodes
        type_node.set_value(type_)
        task1_machine_node.set_value(task1_machine)
        task1_tool_node.set_value(task1_tool)
        task1_work_time_node.set_value(task1_work_time)
        task1_type_out_node.set_value(task1_type_out)
        task2_machine_node.set_value(task2_machine)
        task2_tool_node.set_value(task2_tool)
        task2_work_time_node.set_value(task2_work_time)
        task2_type_out_node.set_value(task2_type_out)
        deliver_node.set_value(deliver)
        machine_t_node.set_value(machine_t)
        id_node.set_value(id)
