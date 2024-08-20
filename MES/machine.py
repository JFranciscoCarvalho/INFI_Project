from time import time

class Machine:

    def __init__(self, available_tools:list[int], operated_work_pieces=[0]*9, operating_time = 0, active_tool=None):
        
        # Tools variables
        self.available_tools = available_tools
        if active_tool is None:
            self.active_tool = available_tools[0]
        else:
            # If retrieved from the db/plc
            self.active_tool = active_tool
        self.new_tool = self.active_tool
        
        # State variables
        self.ready = True
        self.is_busy = False
        self.is_changing_tool = False
        self.end_production_time = 0
        self.end_changing_time = 0
        
        # Statistics variables
        self.operating_time = operating_time
        self.total_operated_work_pieces = sum(operated_work_pieces)
        self.operated_work_pieces = operated_work_pieces.copy()

    def get_tool_index(self, tool):
        return self.available_tools.index(tool) + 1

    # Returns the index of the active tool (1..3)
    def get_active_tool_index(self):
        return self.get_tool_index(self.active_tool)
    
    # Returns the index of the new tool (1..3)
    def get_new_tool_index(self):
        return self.get_tool_index(self.new_tool)
    
    # Add worked_piece
    def add_work_piece(self, type, worktime):
        if not isinstance(type, int):
            type = int(type[1])
        self.operating_time += worktime
        self.operated_work_pieces[type-1] += 1
        self.total_operated_work_pieces += 1

    # Starts a production and idles the machine for the defined duration
    def start_production(self, duration):
        self.end_production_time = max(time() + duration + 2, self.end_production_time)
        self.is_busy = True
        self.ready = False

    # Starts changing the tool and idles the machine for the defined duration
    def start_changing_tool(self, duration = 25 - 10):
        self.end_changing_time = max(time() + duration, self.end_changing_time)
        self.is_changing_tool = True
        self.ready = False

    # Updates the state of the machine status
    def update_state(self):
        self.is_busy = (time() < self.end_production_time)
        self.is_changing_tool = (time() < self.end_changing_time)
        self.ready = not (self.is_busy or self.is_changing_tool)

    def update_tool(self, tool):
        self.active_tool = self.available_tools[tool - 1]