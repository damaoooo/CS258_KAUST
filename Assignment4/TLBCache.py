from Utils import *
from typing import Dict, Optional, Union


class TLBEntry:
    def __init__(self, page_number: int, frame_number: int, valid: bool = True) -> None:
        self.page_number = page_number
        self.frame_number = frame_number
        self.valid = valid


class TLB:
    def __init__(self, tlb_size: int = 16) -> None:
        self.entries: Dict[int, TLBEntry] = {}

        self.fifo_list = []
        self.size = tlb_size

    def __contains__(self, item):
        return page_index(item) in self.entries

    def __getitem__(self, item):
        return self.entries[page_index(item)]

    def query(self, virtual_address: int) -> TLBEntry:
        page_number = page_index(virtual_address)
        assert page_number in self.entries
        return self.entries[page_number]

    def update(self, virtual_address: int, frame_number: int) -> None:
        page_number = page_index(virtual_address)
        assert page_number not in self.entries
        if len(self.entries) >= self.size:
            pop_item = self.fifo_list.pop(0)
            self.entries.pop(pop_item)

        self.entries[page_number] = TLBEntry(page_number, frame_number)
        self.fifo_list.append(page_number)

        assert len(self.entries) <= self.size
        assert len(self.fifo_list) <= self.size

    def flush(self):
        self.entries.clear()
        self.fifo_list.clear()

