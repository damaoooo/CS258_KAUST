import math
import random


memory_access_time = 100  # Time to access memory

class D1CacheSimulator:
    def __init__(self, cache_size, line_size, d2cache):
        self.cache_size = cache_size
        self.line_size = line_size
        self.num_lines = self.cache_size // self.line_size
        self.cache = [None] * self.num_lines  # Initialize cache with None
        self.l2_cache = d2cache

        # Calculate bit sizes
        self.offset_bits = int(math.log2(self.line_size))
        self.index_bits = int(math.log2(self.num_lines))
        self.tag_bits = 32 - self.offset_bits - self.index_bits

        # Statistics
        self.hits = 0
        self.misses = 0

    def access_cache(self, address: int):
        offset = address & ((1 << self.offset_bits) - 1) # directely map to the cache, don't need offset
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)

        if self.cache[index] == tag:
            self.hits += 1
        else:
            # On L1 miss, access L2 cache
            self.misses += 1
            self.l2_cache.access_cache(address)
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

class D2CacheSimulator:
    def __init__(self, cache_size, line_size):
        self.cache_size = cache_size
        self.line_size = line_size
        self.num_lines = self.cache_size // self.line_size
        self.cache = [None] * self.num_lines  # Initialize cache with None

        self.offset_bits = int(math.log2(self.line_size))
        self.index_bits = int(math.log2(self.num_lines))
        self.tag_bits = 32 - self.offset_bits - self.index_bits

        self.hits = 0
        self.misses = 0

    def access_cache(self, address):
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)

        if self.cache[index] == tag:
            self.hits += 1
        else:
            self.misses += 1
            # For simplicity, always replace the cache line on a miss
            self.cache[index] = tag

    def flush_cache(self):
        self.cache = [None] * self.num_lines

    def process_trace(self, trace_line):
        parts = trace_line.split()
        op = int(parts[0])  # Operation code is in decimal
        address = int(parts[1], 16)  # Address is in hexadecimal

        if op == 0 or op == 1:  # Memory read or write
            self.access_cache(address)
        elif op == 4:  # Flush the cache
            self.flush_cache()
        # OP=2 (Instruction fetch) and OP=3 (Ignore) are not processed

    def report_stats(self):
        return self.hits, self.misses
    

def run_simulator(d1_cache_size, d1_access_time, d2_cache_size, d2_access_time, line_size, trace_file):
    d2_simulator = D2CacheSimulator(d2_cache_size, line_size)
    d1_simulator = D1CacheSimulator(d1_cache_size, line_size, d2_simulator)

    with open(trace_file, 'r') as file:
        for line in file:
            d1_simulator.process_trace(line)

    l1_hits, l1_misses = d1_simulator.report_stats()
    l2_hits, l2_misses = d2_simulator.report_stats()
    print(f"L1 Cache Size: {d1_cache_size// 1024} KB, L2 Cache Size: {d2_cache_size // 1024} KB, Line Size: {line_size} Bytes")
    print(f"L1 Hits: {l1_hits}, L1 Misses: {l1_misses}, L2 Hits: {l2_hits}, L2 Misses: {l2_misses}")
    total_time = (l1_hits +l1_misses) * d1_access_time + (l1_misses) * d2_access_time + l2_misses * memory_access_time
    l1_hit_rate = l1_hits / (l1_hits + l1_misses) if (l1_hits + l1_misses) > 0 else 0
    l2_hit_rate = l2_hits / (l2_hits + l2_misses) if (l2_hits + l2_misses) > 0 else 0
    print(f"L1 Hit Rate: {l1_hit_rate}, L2 Hit Rate: {l2_hit_rate}")
    print(f"total_time: {total_time} cycles")


if __name__ == '__main__':
    trace_file = './spec_benchmark/008.espresso.din'  # Assuming this file is already decompressed
    d1_cache_sizes = [(32 * 1024, 1), (64 * 1024, 2)]  # (Size, Access Time)
    d2_cache_sizes = [(512 * 1024, 8), (1024 * 1024, 12), (2 * 1024 * 1024, 16)]  # (Size, Access Time)
    line_sizes = [32, 64, 128]

    for d1_cache_size, d1_access_time in d1_cache_sizes:
        for d2_cache_size, d2_access_time in d2_cache_sizes:
            for line_size in line_sizes:
                run_simulator(d1_cache_size, d1_access_time, d2_cache_size, d2_access_time, line_size, trace_file)
                print("-------------------------------------")