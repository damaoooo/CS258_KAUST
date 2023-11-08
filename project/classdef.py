class Device:
    def receive_clock(self):
        # Placeholder for the base class method, to be overridden by subclasses
        pass

    def do_function(self):
        # Placeholder for the base class method, to be overridden by subclasses
        pass


class Adder(Device):
    def __init__(self):
        self.in_ports = [None, None]  # Placeholder for Port objects
        self.out = None  # Placeholder for a Latch object
        self.result = 0  # Initialize the result

    def receive_clock(self):
        # Implementation of the receive_clock method
        pass

    def do_function(self):
        # Implementation of the do_function method
        self.result = self.in_ports[0].connection.value + self.in_ports[1].connection.value
        self.out.value = self.result

    def connect(self, port_id, latch):
        self.in_ports[port_id].connection = latch

# Assuming Port and Latch are defined elsewhere
class Port:
    def __init__(self):
        self.connection = None

class Latch:
    def __init__(self):
        self.value = 0





