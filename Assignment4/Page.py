from Utils import *
from Memory import *
from typing import List, Dict, Optional, Union


class PageTableEntry:
    def __init__(self, value: int, valid: bool = True) -> None:
        self.value = value
        self.valid = valid


class PageTable:
    def __init__(self, page_bits: int, address: Union[None, int] = None, is_last: bool = False) -> None:
        """
        One bit for valid bit
        Unit is bytes
        | name | flag | value |
        | byte |  1   |  4   |
        For Last one
        | name | flag | value |
        | byte |  1   |  3  |
        """

        if is_last:
            self.page_size = 2 ** page_bits * 4
        else:
            self.page_size = 2 ** page_bits * 5

        self.is_last = is_last
        self.page_bit = page_bits

        self.entries: Dict[int, PageTableEntry] = {}
        self.address = address

    @staticmethod
    def get_page_size(page_bits, is_last):
        if is_last:
            return 2 ** page_bits * 4
        else:
            return 2 ** page_bits * 5

    def add_entry(self, key: int, value: int) -> None:
        self.entries[key] = PageTableEntry(value, True)

    def deserialize(self, data: bytes):
        assert len(data) == self.page_size
        if self.is_last:
            for i in range(0, 2 ** self.page_bit):
                flag_byte = data[i * 4]
                valid = bool(flag_byte & 0b1)
                address = int.from_bytes(data[i * 4 + 1:i * 4 + 4], byteorder='big') & ((2 << 20) - 1)
                self.entries[i] = PageTableEntry(address, valid)
        else:
            for i in range(0, 2 ** self.page_bit):
                flag_byte = data[i * 5]
                valid = bool(flag_byte & 0b1)
                address = int.from_bytes(data[i * 5 + 1:i * 5 + 5], byteorder='big')
                self.entries[i] = PageTableEntry(address, valid)

    def serialize(self):
        buffer = b""
        for i in range(2 ** self.page_bit):
            if i in self.entries:
                flag_byte = 0b00000000
                if self.entries[i].valid:
                    flag_byte |= 0b1
                buffer += flag_byte.to_bytes(1, byteorder='big')
                if self.is_last:
                    buffer += self.entries[i].value.to_bytes(3, byteorder='big')
                else:
                    buffer += self.entries[i].value.to_bytes(4, byteorder='big')
            else:
                 buffer += b'\x00' * (4 if self.is_last else 5)
        assert len(buffer) == self.page_size
        return buffer

    def write_back_to_memory(self, memory_address: int, mmu: Memory):
        mmu.write_bytes(memory_address, self.serialize())

    def load_from_memory(self, memory_address: int, mmu: Memory):
        self.deserialize(mmu.read_bytes(memory_address, self.page_size))

    def __contains__(self, item):
        return item in self.entries and self.entries[item].valid


class MultiLevelPageTable:
    def __init__(self, mmu: Memory, levels: Union[None, List[int]] = None) -> None:
        if levels is None:
            levels = [6, 8, 6]
        self.page_levels = levels
        assert len(levels) == 3
        assert sum(levels) == 20

        self.L1PageTable = PageTable(page_bits=self.page_levels[0])
        self.L2PageTable = PageTable(page_bits=self.page_levels[1])
        self.L3PageTable = PageTable(page_bits=self.page_levels[2], is_last=True)
        self.mmu = mmu

        self.root_page_address = mmu.allocate_page(self.L1PageTable.page_size)[0]
        self.last_empty_address = self.root_page_address + self.L1PageTable.page_size

        self.L1PageTable = PageTable(page_bits=self.page_levels[0], address=self.root_page_address)

    def initial(self):
        self.L1PageTable = PageTable(page_bits=self.page_levels[0])
        self.L2PageTable = PageTable(page_bits=self.page_levels[1])
        self.L3PageTable = PageTable(page_bits=self.page_levels[2], is_last=True)
        self.root_page_address = self.mmu.allocate_page(self.L1PageTable.page_size)[0]

        self.L1PageTable = PageTable(address=self.root_page_address, page_bits=self.page_levels[0])
        self.last_empty_address = self.root_page_address + self.L1PageTable.page_size

    def allocate_page(self, page_level: int):
        assert page_level in [1, 2, 3]
        if page_level == 1:
            page_size = self.L1PageTable.page_size
        elif page_level == 2:
            page_size = self.L2PageTable.page_size
        else:
            page_size = self.L3PageTable.page_size

        if page_index(self.last_empty_address + page_size) == page_index(self.last_empty_address):
            new_page_address = self.last_empty_address
            self.last_empty_address += page_size
        else:
            new_page_address = self.mmu.allocate_page(page_size)[0]
            self.last_empty_address = new_page_address + page_size
        return new_page_address

    def query_l1(self, address: int) -> int:
        l1_index = address >> (32 - self.page_levels[0])
        if l1_index in self.L1PageTable:
            return self.L1PageTable.entries[l1_index].value
        else:
            # Allocate a new L2 page table
            # If it can be allocated in the same page
            new_l2_physical_address = self.allocate_page(page_level=2)

            # Update L1 page table
            self.L1PageTable.add_entry(l1_index, new_l2_physical_address)
            return self.L1PageTable.entries[l1_index].value

    def query_l2(self, address: int) -> int:
        l2_index = page_index(address) & (2 ** self.page_levels[1] - 1)
        if l2_index in self.L2PageTable:
            return self.L2PageTable.entries[l2_index].value

        else:
            # Allocate a new L3 page table
            new_l3_physical_address = self.allocate_page(page_level=3)
            self.L2PageTable.add_entry(l2_index, new_l3_physical_address)

        return self.L2PageTable.entries[l2_index].value

    def query_l3(self, address: int) -> int:
        l3_index = page_index(address) & (2 ** self.page_levels[2] - 1)
        if l3_index in self.L3PageTable:
            return self.L3PageTable.entries[l3_index].value
        else:
            new_page_address = self.mmu.allocate_page(1)[0]
            self.L3PageTable.add_entry(l3_index, new_page_address)
        return self.L3PageTable.entries[l3_index].value
