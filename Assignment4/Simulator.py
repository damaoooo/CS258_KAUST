from Page import MultiLevelPageTable
from TLBCache import TLB
from enum import Enum
import matplotlib.pyplot as plt
import pickle
from collections import Counter
from dataclasses import dataclass
from typing import List
from Utils import *
from Memory import Memory
from Cache import Level2Cache, SplitCache
import multiprocessing


class Instruction:
    def __init__(self, op: OP, address: int, value: int):
        self.op: OP = op
        self.address: int = address
        self.value: int = value


@dataclass
class SimulatorConfigure:
    file_path: str = "./Spec_Benchmark/013.spice2g6.din"

    separate_instruction_data: bool = True

    L1_cacheline_size: int = 32 * Size.B
    L1_cache_size: int = 32 * Size.KB

    L1_cache_access: int = 1

    L2_cacheline_size: int = L1_cacheline_size
    L2_cache_size: int = 512 * Size.KB

    L2_cache_access: int = 8

    L2_associativity: int = Associativity.SetAssociative
    L2_n_way: int = 4

    L1_replace_algorithm: int = CacheReplaceAlgorithm.LRU
    L2_replace_algorithm: int = CacheReplaceAlgorithm.FIFO

    TLB_size: int = 16
    TLB_access: int = 1

    Memory_access: int = 100


def parse_instructions(instruction: str):
    op, address, value = instruction.split(' ')
    return Instruction(op=OP(int(op)), address=int(address, 16), value=int(value, 16))


def address_align(address: int, cache_size: int):
    # Ensure the address is the multiple of cache_size
    return address // cache_size * cache_size


def address_needed(address: int, size: int, unit: int):
    # Ensure the address is the multiple of cache_size
    result = []
    i = 0
    while unit * i < size:
        result.append(address + unit * i)
        i += 1
    return result


class Simulator:
    def __init__(self, config: SimulatorConfigure):

        self.config = config
        self.file_path = config.file_path
        self.memory = Memory(start_address=0)
        self.multi_page = MultiLevelPageTable(self.memory, levels=[6, 8, 6])
        self.tlb = TLB(config.TLB_size)

        if self.config.separate_instruction_data:
            self.cache = SplitCache(
                l1_cache_size=config.L1_cache_size,
                l1_cache_line_size=config.L1_cacheline_size,
                l1_cache_policy=config.L1_replace_algorithm,
                l2_cache_size=config.L2_cache_size,
                l2_cache_line_size=config.L2_cacheline_size,
                l2_cache_policy=config.L2_replace_algorithm,
                l2_cache_associativity=config.L2_associativity,
                l2_n_way=config.L2_n_way
            )
        else:
            self.cache = Level2Cache(
                l1_cache_size=config.L1_cache_size,
                l1_cache_line_size=config.L1_cacheline_size,
                l1_cache_policy=config.L1_replace_algorithm,
                l2_cache_size=config.L2_cache_size,
                l2_cache_line_size=config.L2_cacheline_size,
                l2_cache_policy=config.L2_replace_algorithm,
                l2_cache_associativity=config.L2_associativity,
                l2_n_way=config.L2_n_way
            )

        self.instructions = self.parse_file()

        self.cycle = 0

        self.tlb_hit = 0
        self.tlb_access = 0

        self.l1_hit = 0
        self.l1_access = 0

        self.l2_hit = 0
        self.l2_access = 0

    def parse_file(self):
        instruction_list: List[Instruction] = []

        with open(self.file_path, 'r') as file:
            for line in file.readlines():
                instruction_list.append(parse_instructions(line))

        return instruction_list

    def page_walk(self, address: int):
        page_base_address = self.multi_page.root_page_address

        # L1 page table
        page_content = self.simu_read_data(page_base_address, self.multi_page.L1PageTable.page_size)
        self.multi_page.L1PageTable.deserialize(page_content)

        # L2 page table
        l2_base_address = self.multi_page.query_l1(address)
        l2_page_content = self.simu_read_data(l2_base_address, self.multi_page.L2PageTable.page_size)
        self.multi_page.L2PageTable.deserialize(l2_page_content)

        # L3 page table
        l3_base_address = self.multi_page.query_l2(address)
        l3_page_content = self.simu_read_data(l3_base_address, self.multi_page.L3PageTable.page_size)
        self.multi_page.L3PageTable.deserialize(l3_page_content)

        # Physical address
        physical_address = self.multi_page.query_l3(address)

        # Update write back
        self.simu_write_data(page_base_address, self.multi_page.L1PageTable.serialize())
        self.simu_write_data(l2_base_address, self.multi_page.L2PageTable.serialize())
        self.simu_write_data(l3_base_address, self.multi_page.L3PageTable.serialize())

        return physical_address

    def address_translate(self, v_address: int):
        self.cycle += 1
        self.tlb_access += 1

        if v_address in self.tlb:
            self.tlb_hit += 1
            p_address = self.tlb.query(v_address).frame_number
        else:
            p_address = self.page_walk(v_address)
            while p_address == 0:
                print("Oops Zero p_address!")
                p_address = self.page_walk(v_address)
            self.tlb.update(v_address, p_address)
        # print(hex(v_address), "->", hex(p_address))

        return p_address

    def simu_read_instruction(self, address: int):
        if address in self.cache:
            cache_level, result = self.cache.read_cache(address)
            if cache_level == CacheLevel.L1:
                self.cycle += self.config.L1_cache_access
                self.l1_hit += 1
                self.l1_access += 1
            elif cache_level == CacheLevel.L2:
                self.l1_access += 1
                self.l2_access += 1
                self.l2_hit += 1
                self.cycle += self.config.L2_cache_access + self.config.L1_cache_access
            else:
                self.l1_access += 1
                self.l2_access += 1
        else:
            if address not in self.memory:
                self.memory.allocate_page_at_address(address)
            result = self.memory.read_bytes(address, self.config.L1_cacheline_size)
            self.l1_access += 1
            self.l2_access += 1
            self.cache.write_cache(address, result)
            self.cycle += self.config.Memory_access + self.config.L2_cache_access + self.config.L1_cache_access

    def simu_read_data(self, address: int, size: int = 4):
        need_size = size
        # p_address = self.address_translate(address)
        aligned_address = address_align(address, self.config.L1_cacheline_size)
        aligned_size = address - aligned_address
        # padding
        padding_size = 0
        while aligned_size % self.config.L1_cacheline_size:
            aligned_size += 1
            padding_size += 1

        needed_addresses = address_needed(aligned_address, aligned_size + need_size + padding_size,
                                          self.config.L1_cacheline_size)

        result = b''

        for idx, address in enumerate(needed_addresses):
            if address in self.cache:
                cache_level, r_result = self.cache.read_cache(address)
                result += r_result
                if cache_level == CacheLevel.L1:
                    self.cycle += self.config.L1_cache_access
                    self.l1_hit += 1
                    self.l1_access += 1
                elif cache_level == CacheLevel.L2:
                    self.l1_access += 1
                    self.l2_access += 1
                    self.l2_hit += 1
                    self.cycle += self.config.L2_cache_access + self.config.L1_cache_access
                else:
                    self.l1_access += 1
                    self.l2_access += 1
            else:
                if address not in self.memory:
                    self.memory.allocate_page_at_address(address)
                result += self.memory.read_bytes(address, self.config.L1_cacheline_size)
                self.l1_access += 1
                self.l2_access += 1
                self.cache.write_cache(address, result[-self.config.L1_cacheline_size:])
                self.cycle += self.config.Memory_access + self.config.L2_cache_access + self.config.L1_cache_access

        result = result[aligned_size:aligned_size + size]
        return result

    def simu_write_data(self, address: int, data: bytes):
        # p_address = self.address_translate(address)
        aligned_address = address_align(address, self.config.L1_cacheline_size)
        aligned_size = address - aligned_address
        data = b'\x00' * aligned_size + data
        need_size = len(data)
        while need_size % self.config.L1_cacheline_size:
            data += b'\x00'
            need_size = len(data)
        assert need_size % self.config.L1_cacheline_size == 0

        needed_address = address_needed(aligned_address, need_size, self.config.L1_cacheline_size)
        sliced_data = [data[i:i + self.config.L1_cacheline_size] for i in
                       range(0, len(data), self.config.L1_cacheline_size)]

        for idx, address in enumerate(needed_address):
            if len(sliced_data[idx]) != self.config.L1_cacheline_size:
                print("Oops, not aligned!", len(sliced_data[idx]), self.cache.L1Cache.cache_line_size)
            if address in self.cache:
                cache_level = self.cache.write_cache(address, sliced_data[idx])
                if cache_level == CacheLevel.L1:
                    self.l1_access += 1
                    self.l1_hit += 1
                    self.cycle += self.config.L1_cache_access
                elif cache_level == CacheLevel.L2:
                    self.l1_access += 1
                    self.l2_access += 1
                    self.l2_hit += 1
                    self.cycle += self.config.L2_cache_access + self.config.L1_cache_access
            else:
                self.memory.write_bytes(address, sliced_data[idx])
                # Not Count, run simultaneously
                self.cache.write_cache(address, sliced_data[idx])
                self.l1_access += 1
                self.l2_access += 1
                self.cycle += self.config.Memory_access + self.config.L2_cache_access + self.config.L1_cache_access

    def start_simulation(self):
        for instruction in self.instructions:
            if instruction.op == OP.MemoryRead:
                self.simu_read_data(self.address_translate(instruction.address), 4)
                # self.memory.read_bytes(self.address_translate(instruction.address), 4)
            elif instruction.op == OP.MemoryWrite:
                self.simu_write_data(self.address_translate(instruction.address),
                                     instruction.value.to_bytes(4, 'big'))
            elif instruction.op == OP.Flush:
                self.cache.flush()
                self.tlb.flush()
            elif instruction.op == OP.InstructionFetch:
                self.simu_read_data(self.address_translate(instruction.address), 4)
            else:
                pass

    def result(self):
        print(f"TLB Hit Rate: {self.tlb_hit / self.tlb_access, self.tlb_hit, self.tlb_access}")
        print(f"L1 Hit Rate: {self.l1_hit / self.l1_access, self.l1_hit, self.l1_access}")
        print(f"L2 Hit Rate: {self.l2_hit / self.l2_access, self.l2_hit, self.l2_access}")
        print(f"Total Cycles: {self.cycle}")
        print(f"Average Cycles: {self.cycle / len(self.instructions)}")
        return {"TLB_hit": self.tlb_hit, "TLB_access": self.tlb_access,
                "L1_hit": self.l1_hit, "L1_access": self.l1_access,
                "L2_hit": self.l2_hit, "L2_access": self.l2_access,
                "Total_Cycles": self.cycle, "Average_Cycles": self.cycle / len(self.instructions)}

    def plot_instruction_address_range(self):
        instruction_address = []
        for instruction in self.instructions:
            instruction_address.append(instruction.address >> 12)
        print(Counter(instruction_address))


def test_case_1():
    config = SimulatorConfigure()
    config.file_path = "./spec_benchmark/008.espresso.din"
    total_result = {"Split": {}, "Unified": {}}
    for split, name in [(True, "Split"), (False, "Unified")]:
        for cache_line_size in [32 * Size.B, 64 * Size.B, 128 * Size.B]:
            for l1_size, l1_latency in [(32 * Size.KB, 1), (64 * Size.KB, 2)]:
                for l2_size, l2_latency in [(512 * Size.KB, 8), (1024 * Size.KB, 12), (2 * 1024 * Size.KB, 16)]:
                    for tlb_size in [8, 16]:
                        config.separate_instruction_data = split
                        config.L2_replace_algorithm = CacheReplaceAlgorithm.FIFO
                        config.L2_n_way = 4
                        config.TLB_size = tlb_size
                        config.L1_cacheline_size = cache_line_size
                        config.L1_cache_size = l1_size
                        config.L1_cache_access = l1_latency
                        config.L2_cacheline_size = cache_line_size
                        config.L2_cache_size = l2_size
                        config.L2_cache_access = l2_latency
                        simulator = Simulator(config)
                        simulator.parse_file()
                        simulator.start_simulation()
                        res = simulator.result()
                        total_result[name][(cache_line_size, l1_size, l2_size, tlb_size)] = res

    print(total_result)
    with open("case1.pickle", 'wb') as file:
        pickle.dump(total_result, file)
        file.close()


def test_case_2():
    config = SimulatorConfigure()
    config.file_path = "./spec_benchmark/008.espresso.din"
    total_result = {"FIFO": {}, "LRU": {}, "Random": {}}
    for replace_algorithm, name in [(CacheReplaceAlgorithm.FIFO, "FIFO"), (CacheReplaceAlgorithm.LRU, "LRU"),
                                    (CacheReplaceAlgorithm.Random, "Random")]:
        for cache_line_size in [32 * Size.B, 64 * Size.B, 128 * Size.B]:
            for l1_size, l1_latency in [(32 * Size.KB, 1), (64 * Size.KB, 2)]:
                for l2_size, l2_latency in [(512 * Size.KB, 8), (1024 * Size.KB, 12), (2 * 1024 * Size.KB, 16)]:
                    for tlb_size in [8, 16]:
                        config.separate_instruction_data = True
                        config.L2_replace_algorithm = replace_algorithm
                        config.L2_n_way = 4
                        config.TLB_size = tlb_size
                        config.L1_cacheline_size = cache_line_size
                        config.L1_cache_size = l1_size
                        config.L1_cache_access = l1_latency
                        config.L2_cacheline_size = cache_line_size
                        config.L2_cache_size = l2_size
                        config.L2_cache_access = l2_latency
                        simulator = Simulator(config)
                        simulator.parse_file()
                        simulator.start_simulation()
                        res = simulator.result()
                        total_result[name][(cache_line_size, l1_size, l2_size, tlb_size)] = res

    print(total_result)
    with open("case2.pickle", 'wb') as file:
        pickle.dump(total_result, file)
        file.close()


def test_case_3():
    config = SimulatorConfigure()
    config.file_path = "./spec_benchmark/008.espresso.din"
    total_result = {"Direct": {}, "2-way": {}, "4-way": {}}
    for n_way, name in [(4, "4-way"), (2, "2-way"), (1, "Direct")]:
        for cache_line_size in [32 * Size.B, 64 * Size.B, 128 * Size.B]:
            for l1_size, l1_latency in [(32 * Size.KB, 1), (64 * Size.KB, 2)]:
                for l2_size, l2_latency in [(512 * Size.KB, 8), (1024 * Size.KB, 12), (2 * 1024 * Size.KB, 16)]:
                    for tlb_size in [8, 16]:
                        config.separate_instruction_data = True
                        config.L2_replace_algorithm = CacheReplaceAlgorithm.Random
                        config.L2_n_way = n_way
                        config.TLB_size = tlb_size
                        config.L1_cacheline_size = cache_line_size
                        config.L1_cache_size = l1_size
                        config.L1_cache_access = l1_latency
                        config.L2_cacheline_size = cache_line_size
                        config.L2_cache_size = l2_size
                        config.L2_cache_access = l2_latency
                        simulator = Simulator(config)
                        instructions = simulator.parse_file()
                        simulator.start_simulation()
                        res = simulator.result()
                        total_result[name][(cache_line_size, l1_size, l2_size, tlb_size)] = res

    print(total_result)
    with open("case3.pickle", 'wb') as file:
        pickle.dump(total_result, file)
        file.close()


if __name__ == '__main__':
    t1 = multiprocessing.Process(target=test_case_1)
    t2 = multiprocessing.Process(target=test_case_2)
    t3 = multiprocessing.Process(target=test_case_3)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()

