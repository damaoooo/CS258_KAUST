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
        pass

    def do_function(self):
        self.result = self.in_ports[0].connection.value + self.in_ports[1].connection.value
        self.out.value = self.result

    def connect(self, port_id, latch):
        self.in_ports[port_id].connection = latch

class Shifter(Device):
    def __init__(self):
        self.in_ports = [None, None]  # Two 64-bit input ports
        self.out = None  # One 64-bit output latch
        self.control_signal = 0x00  # Default control signal (right shift)

    def receive_clock(self):
        pass

    def do_function(self):
        value_to_shift = self.in_ports[0].connection.value
        shift_amount = self.in_ports[1].connection.value & 0x3F  # Limiting to 64 bits

        if self.control_signal == 0x00:
            self.out.value = value_to_shift >> shift_amount
        elif self.control_signal == 0x01:
            self.out.value = value_to_shift << shift_amount

    def connect(self, port_id, latch):
        self.in_ports[port_id].connection = latch

    def set_control_signal(self, signal):
        self.control_signal = signal
class Logic(Device):
    def __init__(self):
        self.in_ports = [None, None]  # Two 64-bit input ports
        self.out = None  # One 64-bit output latch
        self.control_signal = 0x00  # Default control signal (NOT operation)

    def receive_clock(self):
        pass

    def do_function(self):
        # Extracting the values from the input ports
        input_value1 = self.in_ports[0].connection.value
        input_value2 = self.in_ports[1].connection.value

        # Performing the logical operation based on the control signal
        if self.control_signal == 0x00:
            # NOT operation (only the first input is considered)
            self.out.value = ~input_value1
        elif self.control_signal == 0x01:
            # AND operation
            self.out.value = input_value1 & input_value2
        elif self.control_signal == 0x10:
            # OR operation
            self.out.value = input_value1 | input_value2
        elif self.control_signal == 0x11:
            # XOR operation
            self.out.value = input_value1 ^ input_value2

    def connect(self, port_id, latch):
        self.in_ports[port_id].connection = latch

    def set_control_signal(self, signal):
        self.control_signal = signal



class Port:
    def __init__(self):
        self.connection = None

class Latch:
    def __init__(self):
        self.value = 0





