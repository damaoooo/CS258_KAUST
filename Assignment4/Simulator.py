from Page import MultiLevelPageTable
from TLBCache import TLB
from enum import Enum
from dataclasses import dataclass
from typing import List
from Utils import *
from Memory import Memory
from Cache import Level2Cache


class Instruction:
    def __init__(self, op: OP, address: int, value: int):
        self.op: OP = op
        self.address: int = address
        self.value: int = value


@dataclass
class SimulatorConfigure:
    file_path: str = "./Spec_Benchmark/013.spice2g6.din"

    L1_cacheline_size: int = 32 * Size.B
    L1_cache_size: int = 32 * Size.KB

    L1_cache_access: int = 1

    L2_cacheline_size: int = 32 * Size.B
    L2_cache_size: int = 512 * Size.KB

    L2_cache_access: int = 8

    L2_associativity: int = Associativity.SetAssociative
    L2_n_way: int = 4

    L1_replace_algorithm: int = CacheReplaceAlgorithm.LRU
    L2_replace_algorithm: int = CacheReplaceAlgorithm.LRU

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

        self.cache = Level2Cache()

        self.instructions = self.parse_file()

        assert self.cache.L1Cache.cache_line_size == self.cache.L2Cache.cache_line_size

        self.cycle = 0

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

        if v_address in self.tlb:
            p_address = self.tlb.query(v_address).frame_number
        else:
            p_address = self.page_walk(v_address)
            while p_address == 0:
                print("Oops Zero p_address!")
                p_address = self.page_walk(v_address)
            self.tlb.update(v_address, p_address)
        print(hex(v_address), "->", hex(p_address))

        return p_address

    def simu_read_data(self, address: int, size: int = 4):
        need_size = size
        # p_address = self.address_translate(address)
        aligned_address = address_align(address, self.config.L1_cacheline_size)
        aligned_size = address - aligned_address
        # padding
        padding_size = 0
        if aligned_size % self.config.L1_cacheline_size:
            aligned_size += aligned_address % self.config.L1_cacheline_size
            padding_size = aligned_address % self.config.L1_cacheline_size

        needed_addresses = address_needed(aligned_address, aligned_size + need_size + padding_size, self.config.L1_cacheline_size)

        result = b''

        for idx, address in enumerate(needed_addresses):
            if address in self.cache:
                cache_level, r_result = self.cache.read_cache(address)
                result += r_result
                if cache_level == CacheLevel.L1:
                    self.cycle += self.config.L1_cache_access
                elif cache_level == CacheLevel.L2:
                    self.cycle += self.config.L2_cache_access + self.config.L1_cache_access
            else:
                if address not in self.memory:
                    self.memory.allocate_page_at_address(address)
                result += self.memory.read_bytes(address, self.config.L1_cacheline_size)
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
        if self.config.L1_cacheline_size - need_size % self.config.L1_cacheline_size:
            data += b'\x00' * (self.config.L1_cacheline_size - need_size % self.config.L1_cacheline_size)
        need_size = len(data)
        assert need_size % self.config.L1_cacheline_size == 0

        needed_address = address_needed(aligned_address, need_size, self.config.L1_cacheline_size)
        sliced_data = [data[i:i + self.config.L1_cacheline_size] for i in
                       range(0, len(data), self.config.L1_cacheline_size)]

        for idx, address in enumerate(needed_address):
            if len(sliced_data[idx]) != 32:
                print("Oops")
            if address in self.cache:
                cache_level = self.cache.write_cache(address, sliced_data[idx])
                if cache_level == CacheLevel.L1:
                    self.cycle += self.config.L1_cache_access
                elif cache_level == CacheLevel.L2:
                    self.cycle += self.config.L2_cache_access + self.config.L1_cache_access
            else:
                self.memory.write_bytes(address, sliced_data[idx])
                # Not Count, run simultaneously
                self.cache.write_cache(address, sliced_data[idx])
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
                if instruction.address == 4224480:
                    print("That address")
                self.simu_read_data(self.address_translate(instruction.address), 4)
            else:
                pass


if __name__ == '__main__':
    config = SimulatorConfigure()
    config.file_path = "./spec_benchmark/008.espresso.din"
    simulator = Simulator(config)
    instructions = simulator.parse_file()
    simulator.start_simulation()
    print(len(instructions))
