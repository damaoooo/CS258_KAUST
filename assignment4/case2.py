import math
import random
from collections import deque

# change l2 directcache.py to l2 4 way set associative cache
memory_access_time = 100  # Time to access memory


class CacheSimulatorBase:
    def __init__(self, cache_size, line_size, cache_policy):
        self.cache_size = cache_size
        self.line_size = line_size
        self.num_lines = self.cache_size // self.line_size
        self.cache_policy = cache_policy

        self.offset_bits = int(math.log2(self.line_size))
        self.index_bits = int(math.log2(self.num_lines))

        # Statistics
        self.hits = 0
        self.misses = 0

        if cache_policy == "LRU":
            self.usage_order = deque()  # Track usage for LRU
        elif cache_policy == "FIFO":
            self.insertion_order = deque()  # Track insertion for FIFO
        elif cache_policy == "Random":
            pass
        else:
            raise ValueError(f"Unknown cache policy: {cache_policy}")

    def replace_cache_line(self, tag, value):
        if self.cache_policy == "Random":
            replace_index = random.randint(0, self.num_lines - 1)
        elif self.cache_policy == "LRU":
            replace_index = self.usage_order.pop()  # Remove the least recently used
            self.usage_order.appendleft(replace_index)  # Add the new one as the most recent
        elif self.cache_policy == "FIFO":
            replace_index = self.insertion_order.pop()  # Remove the oldest
            self.insertion_order.appendleft(replace_index)  # Add the new one as the most recent
        else:  # Default behavior for unknown policy
            raise ValueError(f"Unknown cache policy: {self.cache_policy}")

        self.cache[replace_index] = (tag, value)

    def access_cache(self, address):
        # Similar to your existing access_cache implementation
        # Call self.replace_cache_line(index, tag) on a miss
        raise NotImplementedError


class D1CacheSimulator(CacheSimulatorBase):
    def __init__(self, cache_size, line_size, d2cache, cache_policy):
        super().__init__(cache_size, line_size, cache_policy)
        self.l2_cache = d2cache
        self.cache = [None] * self.num_lines

    def access_cache(self, address: int, value):
        offset = address & ((1 << self.offset_bits) - 1)  # directely map to the cache, don't need offset
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)

        if self.cache[index] and self.cache[index][0] == tag: 
            self.hits += 1
            if self.cache_policy == "LRU":
                self.usage_order.remove(index)  # Remove from current position
                self.usage_order.appendleft(index)  # Add to front as most recently used
        else:
            # On L1 miss, access L2 cache
            self.misses += 1
            self.l2_cache.access_cache(address,value)
            if self.cache_policy == "LRU" and index not in self.usage_order:
                self.usage_order.appendleft(index)  # Add new index for LRU tracking
            if self.cache_policy == "FIFO" and index not in self.insertion_order:
                self.insertion_order.appendleft(index)
            self.replace_cache_line(tag, value) 

    def flush_cache(self):
        self.cache = [None] * self.num_lines

    def process_trace(self, trace_line):
        parts = trace_line.split()
        op = int(parts[0])  # Operation code is in decimal
        address = int(parts[1], 16)  # Address is in hexadecimal
        address &= (1 << 32) - 1  # Ensure 32-bit address
        value = int(parts[2], 16)

        if op == 0 or op == 1:  # Memory read or write
            self.access_cache(address, value)
        elif op == 4:  # Flush the cache
            self.flush_cache()
        # OP=2 (Instruction fetch) and OP=3 (Ignore) are not processed

    def report_stats(self):
        return self.hits, self.misses


class D2CacheSimulator(CacheSimulatorBase):
    def __init__(self, cache_size, line_size, cache_policy):
        super().__init__(cache_size, line_size, cache_policy)
        self.associativity = 4  # 4-way set associative
        self.num_sets = self.cache_size // (self.line_size * self.associativity)
        self.cache = [[None] * self.associativity for _ in range(self.num_sets)]
        self.set_index_bits = int(math.log2(self.num_sets))

        self.policy_data = [[0] * self.associativity for _ in range(self.num_sets)]

    def replace_line_in_set(self, set_index, tag,value):
        set = self.cache[set_index]
        policy_data = self.policy_data[set_index]

        if self.cache_policy == "Random":
            replace_index = random.randint(0, self.associativity - 1)
        elif self.cache_policy == "LRU":
            replace_index = policy_data.index(min(policy_data))
        elif self.cache_policy == "FIFO":
            replace_index = policy_data.index(max(policy_data))
        else:  # Default behavior, replace first None or the first line
            replace_index = set.index(None) if None in set else 0

        set[replace_index] = (tag,value)
        policy_data[replace_index] = self.hits if self.cache_policy in ["LRU", "FIFO"] else 0

    def access_cache(self, address,value):
        offset = address & ((1 << self.offset_bits) - 1)
        set_index = (address >> self.offset_bits) & ((1 << self.set_index_bits) - 1)
        tag = address >> (self.offset_bits + self.set_index_bits)

        set = self.cache[set_index]  # one set has 4 lines
        tags_in_set = [line[0] for line in set if line] 
        try:
            way = tags_in_set.index(tag)
            self.hits += 1
            if self.cache_policy == "LRU":
                self.policy_data[set_index][way] = self.hits  # Update LRU timestamp
        except ValueError:
            self.misses += 1
            self.replace_line_in_set(set_index, tag,value)

    def flush_cache(self):
        self.cache = [None] * self.num_lines

    def process_trace(self, trace_line):
        parts = trace_line.split()
        op = int(parts[0])  # Operation code is in decimal
        address = int(parts[1], 16)  # Address is in hexadecimal
        value = int(parts[2], 16)

        if op == 0 or op == 1:  # Memory read or write
            self.access_cache(address, value)
        elif op == 4:  # Flush the cache
            self.flush_cache()
        # OP=2 (Instruction fetch) and OP=3 (Ignore) are not processed

    def report_stats(self):
        return self.hits, self.misses


def run_simulator(d1_cache_size, d1_access_time, d2_cache_size, d2_access_time, line_size, trace_file, cache_policy):
    d2_simulator = D2CacheSimulator(d2_cache_size, line_size, cache_policy)
    d1_simulator = D1CacheSimulator(d1_cache_size // 2, line_size, d2_simulator,
                                    cache_policy)  # L1 is split in half between instructions and data.

    with open(trace_file, 'r') as file:
        for line in file:
            d1_simulator.process_trace(line)

    l1_hits, l1_misses = d1_simulator.report_stats()
    l2_hits, l2_misses = d2_simulator.report_stats()
    print(
        f"L1 Cache Size: {d1_cache_size // 1024} KB, L2 Cache Size: {d2_cache_size // 1024} KB, Line Size: {line_size} Bytes")
    print(f"L1 Hits: {l1_hits}, L1 Misses: {l1_misses}, L2 Hits: {l2_hits}, L2 Misses: {l2_misses}")
    total_time = (l1_hits + l1_misses) * d1_access_time + (l1_misses) * d2_access_time + l2_misses * memory_access_time
    l1_hit_rate = l1_hits / (l1_hits + l1_misses) if (l1_hits + l1_misses) > 0 else 0
    l2_hit_rate = l2_hits / (l2_hits + l2_misses) if (l2_hits + l2_misses) > 0 else 0
    print(f"L1 Hit Rate: {l1_hit_rate}, L2 Hit Rate: {l2_hit_rate}")
    print(f"total_time: {total_time} cycles")


if __name__ == '__main__':
    trace_file = './spec_benchmark/008.espresso.din'  # Assuming this file is already decompressed
    d1_cache_sizes = [(32 * 1024, 1), (64 * 1024, 2)]  # (Size, Access Time)
    d2_cache_sizes = [(512 * 1024, 8), (1024 * 1024, 12), (2 * 1024 * 1024, 16)]  # (Size, Access Time)
    line_sizes = [32, 64, 128]

    # cache_policies = ["Random", "LRU", "FIFO"]
    cache_policy = "FIFO"

    for d1_cache_size, d1_access_time in d1_cache_sizes:
        for d2_cache_size, d2_access_time in d2_cache_sizes:
            for line_size in line_sizes:
                # for cache_policy in cache_policies:
                run_simulator(d1_cache_size, d1_access_time, d2_cache_size, d2_access_time, line_size, trace_file, cache_policy)
                print("-------------------------------------")
