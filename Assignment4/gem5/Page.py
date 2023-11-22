from Utils import *

from typing import List, Dict, Optional

class PageTableEntry:
    def __init__(self, key: int, value: int, valid: bool = True) -> None:
        self.key = key
        self.value = value
        self.valid = valid

class PageTable:
    def __init__(self) -> None:
        self.entries: Dict[int, PageTableEntry] = {}
        
        