# time_handler.py

from datetime import datetime


class TimeHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TimeHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, format="%Y-%m-%d %H:%M:%S"):
        if self._initialized:
            return
        self.format = format
        self.start_time = None  # Store the start time
        self.time_memory = {}  # Dictionary to store times by ID
        self._initialized = True

    def get_current_time(self):
        current_time = datetime.now()
        return current_time.strftime(self.format)

    def set_start_time(self):
        self.start_time = self.get_current_time()

    def convert_to_datetime(self, time_string):
        return datetime.strptime(time_string, self.format)

    def calculate_time_difference(self, start_time, end_time):
        start_datetime = self.convert_to_datetime(start_time)
        end_datetime = self.convert_to_datetime(end_time)
        time_difference = end_datetime - start_datetime
        return time_difference

    def keep_time_by_id(self, unique_id):
        """
        Record the current time for a given ID.
        """
        current_time = self.get_current_time()
        self.time_memory[unique_id] = current_time

    def save_time_response(self, unique_id):
        """
        Calculate the time difference and store it in the dictionary.
        """
        if unique_id in self.time_memory:
            start_time = self.time_memory[unique_id]
            current_time = self.get_current_time()
            time_difference = self.calculate_time_difference(start_time, current_time)
            self.time_memory[unique_id] = time_difference
        else:
            print(f"Error: ID '{unique_id}' not found in time_memory.")

    def build_memory_dict(self):
        """
        Build a dictionary containing IDs and their respective time differences.
        """
        return self.time_memory

    def get_start_time(self):
        """
        Get the start time of the TimeHandler instance.
        """
        return self.start_time