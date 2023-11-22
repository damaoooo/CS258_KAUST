from Utils import *

from typing import List, Dict, Optional


class PageTableEntry:
    def __init__(self, key: int, value: int, valid: bool = True) -> None:
        self.key = key
        self.value = value
        self.valid = valid


class PageTable:
    def __init__(self, page_bit: int) -> None:
        self.page_bit = page_bit
        self.entries: Dict[int, PageTableEntry] = {}

    def add_query(self, key: int, value: int) -> None:
        self.entries[key] = PageTableEntry(key, value)

    def __contains__(self, item):
        return item in self.entries
        

class MultiLevelPageTable:
    def __init__(self):
        self.L1PageTable = PageTable(6)
        self.L2PageTable = PageTable(8)
        self.L3PageTable = PageTable(6)

    def page_walk(self, virtual_address: int):
        l1_index = virtual_address >> 26
        l2_index = (virtual_address >> 18) & 0xFF
        l3_index = (virtual_address >> 12) & 0x3F

        if l1_index not in self.L1PageTable:
            # Allocate a new Memory Page
            # Update L1/L2/L3 Page Table