from utils import generate_random_data, generate_sorted_random_data


class DataManager:
    def __init__(self, size: int):
        self.original_data = generate_random_data(size)
        self.current_data = self.original_data[:]

    def regenerate(self, size: int, sorted_mode: bool = False):
        if sorted_mode:
            self.original_data = generate_sorted_random_data(size)
        else:
            self.original_data = generate_random_data(size)
        self.current_data = self.original_data[:]

    def reset(self):
        self.current_data = self.original_data[:]

    def get_data(self):
        return self.current_data[:]

    def set_data(self, new_data):
        self.current_data = new_data[:]