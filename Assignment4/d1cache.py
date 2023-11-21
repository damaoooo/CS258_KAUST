import math
import random

class D1CacheSimulator:
    def __init__(self,line_size):
        self.cache_size = 16 * 1024  # 16 KB for data
        self.line_size = line_size  # 32 bytes
        self.num_lines = self.cache_size // self.line_size
        self.cache = [None] * self.num_lines  # Initialize cache with None

        # Calculate bit sizes
        self.offset_bits = int(math.log2(self.line_size))
        self.index_bits = int(math.log2(self.num_lines))
        self.tag_bits = 32 - self.offset_bits - self.index_bits

        # Statistics
        self.hits = 0
        self.misses = 0

    def access_cache(self, address):
        offset = address & ((1 << self.offset_bits) - 1) # directely map to the cache, don't need offset
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)

        if self.cache[index] == tag:
            self.hits += 1
        else:
            self.misses += 1
            if random.choice([True, False]):
                self.cache[index] = tag

    def flush_cache(self):
        self.cache = [None] * self.num_lines

    def process_trace(self, trace_line):
        parts = trace_line.split()
        op = int(parts[0])  # Operation code is in decimal
        address = int(parts[1], 16)  # Address is in hexadecimal
        address &= (1 << 32) - 1  # Ensure 32-bit address

        if op == 0 or op == 1:  # Memory read or write
            self.access_cache(address)
        elif op == 4:  # Flush the cache
            self.flush_cache()
        # OP=2 (Instruction fetch) and OP=3 (Ignore) are not processed

    def report_stats(self):
        return self.hits, self.misses

def run_simulator(line_size, trace_file):
    simulator = D1CacheSimulator(line_size)
    with open(trace_file, 'r') as file:
        for line in file:
            simulator.process_trace(line)
    hits, misses = simulator.report_stats()
    print(f"Line Size: {line_size} - Cache Hits: {hits}, Cache Misses: {misses}")

trace_file = './Spec_Benchmark/008.espresso.din'  # Assuming this file is already decompressed
# Output the results
for line_size in [32, 64, 128]:
    run_simulator(line_size, trace_file)
