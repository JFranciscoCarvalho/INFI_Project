class Transformation:
    
    def __init__(self, initial_type, final_type, tool, processing_time):
        self.initial_type = initial_type
        self.final_type = final_type
        self.tool = tool
        self.processing_time = processing_time

class Transformations:

    transformations = [
        Transformation('P1', 'P6', 1, 20),
        Transformation('P2', 'P3', 2, 10),
        Transformation('P2', 'P4', 3, 10),
        Transformation('P9', 'P5', 4, 15),
        Transformation('P3', 'P6', 1, 20),
        Transformation('P4', 'P7', 4, 10),
        Transformation('P6', 'P8', 3, 30),
        Transformation('P7', 'P9', 3, 10)
    ]
    
    @staticmethod
    def get_tool(initial_type, final_type):

        for t in Transformations.transformations:
            if (t.initial_type == initial_type and t.final_type == final_type):
                return t.tool
        return None
    
    @staticmethod
    def get_processing_time(initial_type, final_type, tool):

        for t in Transformations.transformations:
            if (t.initial_type == initial_type and t.final_type == final_type and t.tool == tool):
                return t.processing_time
        return None