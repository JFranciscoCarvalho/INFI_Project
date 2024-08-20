class Dock:
    def __init__(self, dock_no, unloaded_work_pieces = [0]*9):
        self.no = dock_no
        self.total_unloaded_work_pieces = sum(unloaded_work_pieces)
        self.unload_work_pieces = unloaded_work_pieces.copy()

    def add_work_piece(self, type):
        if not isinstance(type, int):
            type = int(type[1])
        self.unload_work_pieces[type-1] += 1
        self.total_unloaded_work_pieces += 1