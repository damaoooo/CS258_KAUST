from Page import MultiLevelPageTable
from TLBCache import TLB
from enum import Enum
from dataclasses import dataclass
from typing import List
from Utils import *
from Memory import Memory


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

    L2_cacheline_size: int = 64 * Size.B
    L2_cache_size: int = 512 * Size.KB

    L2_associativity: int = Associativity.SetAssociative
    L2_n_way: int = 4

    L1_replace_algorithm: int = CacheReplaceAlgorithm.LRU
    L2_replace_algorithm: int = CacheReplaceAlgorithm.LRU

    TLB_size: int = 16


def parse_instructions(instruction: str):
    op, address, value = instruction.split(' ')
    return Instruction(op=OP(int(op)), address=int(address, 16), value=int(value, 16))


class Simulator:
    def __init__(self, config: SimulatorConfigure):

        self.config = config
        self.file_path = config.file_path
        self.memory = Memory(start_address=0)
        self.multi_page = MultiLevelPageTable(self.memory, levels=[6, 8, 6])
        self.tlb = TLB(config.TLB_size)

        self.cache = Cache(config.L1_cacheline_size, config.L1_cache_size, config.L1_replace_algorithm)

        self.instructions = self.parse_file()

    def parse_file(self):
        instruction_list: List[Instruction] = []

        with open(self.file_path, 'r') as file:
            for line in file.readlines():
                instruction_list.append(parse_instructions(line))

        return instruction_list

    def page_walk(self, address: int):
        page_base_address = self.multi_page.root_page_address

        # L1 page table
        if page_base_address in self.cache:
            page_content = self.cache.read(page_base_address, self.multi_page.L1PageTable.page_size)
            self.multi_page.L1PageTable.deserialize(page_content)
        else:
            self.multi_page.L1PageTable.load_from_memory(page_base_address, self.memory)
            self.cache.write(page_base_address, self.multi_page.L1PageTable.serialize())

        # L2 page table
        l2_base_address = self.multi_page.query_l1(address)
        if l2_base_address in self.cache:
            page_content = self.cache.read(l2_base_address, self.multi_page.L2PageTable.page_size)
            self.multi_page.L2PageTable.deserialize(page_content)
        else:
            self.multi_page.L2PageTable.load_from_memory(l2_base_address, self.memory)
            self.cache.write(l2_base_address, self.multi_page.L2PageTable.serialize())

        # L3 page table
        l3_base_address = self.multi_page.query_l2(address)
        if l3_base_address in self.cache:
            page_content = self.cache.read(l3_base_address, self.multi_page.L3PageTable.page_size)
            self.multi_page.L3PageTable.deserialize(page_content)
        else:
            self.multi_page.L3PageTable.load_from_memory(l3_base_address, self.memory)
            self.cache.write(l3_base_address, self.multi_page.L3PageTable.serialize())

        # Physical address
        physical_address = self.multi_page.query_l3(address)
        return physical_address

    def address_translate(self, v_address: int):
        if v_address in self.tlb:
            p_address = self.tlb.query(v_address).frame_number
        else:
            p_address = self.page_walk(v_address)
            self.tlb.update(v_address, p_address)
        return p_address

    def read_bytes(self, address: int, size: int = 4):
        p_address = self.address_translate(address)
        if p_address in self.cache:
            return self.cache.read(p_address, size)

        return self.memory.read_bytes(p_address, size)

    def write_bytes(self, address: int, value: bytes):
        p_address = self.address_translate(address)
        if p_address in self.cache:
            self.cache.write(p_address, value)
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
