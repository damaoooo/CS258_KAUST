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

    L2_cacheline_size: int = 32 * Size.B
    L2_cache_size: int = 512 * Size.KB

    L2_associativity: int = Associativity.SetAssociative
    L2_n_way: int = 4

    L1_replace_algorithm: int = CacheReplaceAlgorithm.LRU
    L2_replace_algorithm: int = CacheReplaceAlgorithm.LRU

    TLB_size: int = 16


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
        if v_address in self.tlb:
            p_address = self.tlb.query(v_address).frame_number
        else:
            p_address = self.page_walk(v_address)
            self.tlb.update(v_address, p_address)
        return p_address

    def simu_read_data(self, address: int, size: int = 4):
        need_size = size
        # p_address = self.address_translate(address)
        aligned_address = address_align(address, self.config.L1_cacheline_size)
        aligned_size = address - aligned_address
        needed_addresses = address_needed(aligned_address, need_size + aligned_size, self.config.L1_cacheline_size)

        result = b''

        for idx, address in enumerate(needed_addresses):
            if address in self.cache:
                result += self.cache.read_cache(address)[1]
            else:
                result += self.memory.read_bytes(address, self.config.L1_cacheline_size)
                self.cache.write_cache(address, result[-self.config.L1_cacheline_size:])

        result = result[aligned_size:aligned_size + size]
        return result

    def simu_write_data(self, address: int, data: bytes):
        # p_address = self.address_translate(address)
        aligned_address = address_align(address, self.config.L1_cacheline_size)
        aligned_size = address - aligned_address
        data = b'\x00' * aligned_size + data
        need_size = len(data)

        needed_address = address_needed(aligned_address, need_size, self.config.L1_cacheline_size)
        sliced_data = [data[i:i + self.config.L1_cacheline_size] for i in
                       range(0, len(data), self.config.L1_cacheline_size)]

        for idx, address in enumerate(needed_address):
            if address in self.cache:
                self.cache.write_cache(address, sliced_data[idx])
            else:
                self.memory.write_bytes(address, sliced_data[idx])
                self.cache.write_cache(address, sliced_data[idx])

    def read_bytes(self, address: int, size: int = 4):
        p_address = self.address_translate(address)
        if p_address in self.cache:
            return self.cache.read_cache(p_address, size)

        return self.memory.read_bytes(p_address, size)

    def write_bytes(self, address: int, value: bytes):
        p_address = self.address_translate(address)
        if p_address in self.cache:
            self.cache.write_cache(p_address, value)
        else:
            self.memory.write_bytes(p_address, value)

    def start_simulation(self):
        for instruction in self.instructions:
            if instruction.op == OP.MemoryRead:
                self.memory.read_bytes(self.address_translate(instruction.address), 4)
            elif instruction.op == OP.MemoryWrite:
                self.memory.write_bytes(self.address_translate(instruction.address),
                                        instruction.value.to_bytes(4, 'big'))
            elif instruction.op == OP.Flush:
                self.cache.flush()
                self.tlb.flush()
            elif instruction.op == OP.InstructionFetch:
                self.memory.read_bytes(self.address_translate(instruction.address), 4)
            else:
                pass


if __name__ == '__main__':
    config = SimulatorConfigure()
    config.file_path = "./Spec_Benchmark/013.spice2g6.din"
    simulator = Simulator(config)
    instructions = simulator.parse_file()
    print(len(instructions))
