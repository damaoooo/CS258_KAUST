from Utils import *
from typing import List, Dict, Optional
import math

page_bit = 12
page_size = 2 ** page_bit

class MemoryPage:
    def __init__(self, address: int) -> None:
        self.address = address
        self.base_address = address >> page_bit
        self.data = {}
        
    def write(self, address: int, data: int) -> None:
        offset = address & (page_size - 1)
        self.data[offset] = data
        
    def read(self, address: int) -> int:
        offset = address & (page_size - 1)
        return self.data[offset]
    
    def read_page(self) -> Dict[int, int]:
        return self.data
    
    def write_page(self, data: Dict[int, int]) -> None:
        self.data = data

class Memory:
    def __init__(self, start_address: int) -> None:
        self.start_address = start_address
        self.allocated_pages: Dict[int, MemoryPage] = {}
        
    def allocate_page_at_address(self, address: int) -> None:
        page = MemoryPage(address)
        self.allocated_pages[page.base_address] = page
        
    def allocate_page(self, size: int) -> List[int]:
        """
        Allocate Memory Using First Fit Algorithm
        return a list of allocated page addresses
        """
        ret = []
        
        pages_needed = math.ceil(size / (page_size))
        allocated_pages = list(self.allocated_pages.keys())
        allocated_pages.sort()
        
        if len(allocated_pages) == 0:
            page_start = self.start_address
            for i in range(pages_needed):
                i_th_page = page_start + i * page_size
                self.allocate_page_at_address(i_th_page)
                ret.append(i_th_page)
            return ret
        elif len(allocated_pages) == 1:
            page_start = allocated_pages[0] + 1
            for i in range(pages_needed):
                i_th_page = page_start + i * page_size
                self.allocate_page_at_address(i_th_page)
                ret.append(i_th_page)
            return ret
        else:
            
            # Allocate pages in the middle
            for i in range(len(allocated_pages) - 1):
                if allocated_pages[i + 1] - allocated_pages[i] > pages_needed:
                    page_start = allocated_pages[i] + 1
                    for j in range(pages_needed):
                        j_th_page = page_start + j * page_size
                        self.allocate_page_at_address(j_th_page)
                        ret.append(j_th_page)
                    return ret
            # No space in the middle, allocate at the end
            page_start = allocated_pages[-1] + 1
            for i in range(pages_needed):
                i_th_page = page_start + i * page_size
                self.allocate_page_at_address(i_th_page)
                ret.append(i_th_page)
            return ret

    def free_page(self, address: int) -> None:
        self.allocated_pages.pop(address, None)
        
    def __contains__(self, address: int) -> bool:
        return address in self.allocated_pages
                
            