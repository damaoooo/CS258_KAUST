import math
import random
import unittest
from Memory import Memory, MemoryPage, Size
from Page import PageTable, page_index, MultiLevelPageTable
from TLBCache import TLB
from Cache import DirectCacheBase, AssociativeCacheBase
from Utils import CacheReplaceAlgorithm, Associativity

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.memory = Memory(0)
        self.multi_page = MultiLevelPageTable(self.memory, levels=[6, 8, 6])
        self.tlb = TLB()

    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_single_allocate(self):

        self.memory.flush()
        page = self.memory.allocate_page(Size.KB * 4)
        # print(page)
        self.assertEqual(len(page), 1)
        self.assertEqual(page[0], 0)

    def test_multi_allocate(self, size=Size.MB * 100):
        self.memory.flush()
        pages = self.memory.allocate_page(size)
        # print(pages[:3])
        num_pages = math.ceil(size / (4 * Size.KB))
        self.assertEqual(len(pages), num_pages)
        self.assertEqual(pages[0], 0)
        self.assertEqual(pages[-1], (num_pages - 1) * 4 * Size.KB)

    def test_write_and_read_byte(self, size=1000 * Size.KB):
        self.memory.flush()
        pages = self.memory.allocate_page(size)

        num_pages = math.ceil(size / (4 * Size.KB))
        self.assertEqual(len(pages), num_pages)

        data_write = {}

        for page in pages:
            random_offset = random.randint(0, 255)
            random_address = page + random_offset
            random_data = random.randint(0, 255)
            self.memory.write(random_address, random_data)
            data_write[random_address] = random_data

        for address, data in data_write.items():
            self.assertEqual(self.memory.read(address), data)

    def test_continuously_read_and_write(self, size=100 * Size.KB):
        self.memory.flush()
        pages = self.memory.allocate_page(size)
        root_page = pages[0]
        random_data = random.randbytes(size)
        self.memory.write_bytes(root_page, random_data)

        read_out = self.memory.read_bytes(root_page, size)
        self.assertEqual(read_out, random_data)

        read_out2 = self.memory.read_bytes(root_page + size // 2, size // 2)
        self.assertEqual(read_out2, random_data[size // 2:])

    def test_large_read_and_write(self):
        self.test_continuously_read_and_write(1 * Size.MB)

    def test_basic_page_table(self, virtual_address: int = 0x12345678):
        # virtual_address = 0x12345678
        self.multi_page.L1PageTable.load_from_memory(self.multi_page.root_page_address, self.memory)
        l2_address = self.multi_page.query_l1(virtual_address)

        self.multi_page.L2PageTable.load_from_memory(l2_address, self.memory)
        l3_address = self.multi_page.query_l2(virtual_address)

        self.multi_page.L3PageTable.load_from_memory(l3_address, self.memory)
        physical_address = self.multi_page.query_l3(virtual_address)

        self.multi_page.L1PageTable.write_back_to_memory(self.multi_page.root_page_address, self.memory)
        self.multi_page.L2PageTable.write_back_to_memory(l2_address, self.memory)
        self.multi_page.L3PageTable.write_back_to_memory(l3_address, self.memory)
        return (physical_address << 12) + (virtual_address & 0xfff)

    def test_page_table(self):
        self.memory.flush()
        self.multi_page.initial()
        virtual_address = 0x12345678
        physical_address = self.test_basic_page_table(virtual_address)

        virtual_address2 = 0x12345678
        physical_address2 = self.test_basic_page_table(virtual_address2)
        self.assertEqual(physical_address, physical_address2)

        virtual_address3 = 0x12345679
        physical_address3 = self.test_basic_page_table(virtual_address3)
        self.assertNotEqual(physical_address, physical_address3)
        self.assertEqual(page_index(physical_address), page_index(physical_address3))

        virtual_address4 = 0x22345678
        physical_address4 = self.test_basic_page_table(virtual_address4)
        self.assertNotEqual(page_index(physical_address), page_index(physical_address4))

        virtual_address5 = 0x22345679
        physical_address5 = self.test_basic_page_table(virtual_address5)
        self.assertEqual(page_index(physical_address4), page_index(physical_address5))

    def test_tlb_single(self):
        self.tlb.update(0x12345678, 0x87654321 >> 12)

        self.assertEqual(self.tlb.query(0x12345678).frame_number, 0x87654321 >> 12)
        self.assertEqual(self.tlb.query(0x12345679).frame_number, 0x87654321 >> 12)

    def test_tlb_overflow(self):
        random_mapping = {}

        last_frame_number = 0
        last_virtual_address = 0
        for i in range(self.tlb.size):
            last_virtual_address = random.randint(0, 0xffffffff)
            last_frame_number = random.randint(0, 0xffffffff) >> 12
            random_mapping[last_virtual_address] = last_frame_number

        for virtual_address, frame_number in random_mapping.items():
            self.tlb.update(virtual_address, frame_number)

        for virtual_address, frame_number in random_mapping.items():
            self.assertEqual(self.tlb.query(virtual_address).frame_number, frame_number)

        new_mapping = {}
        for i in range(self.tlb.size-1):
            new_mapping[random.randint(0, 0xffffffff)] = random.randint(0, 0xffffffff) >> 12

        for virtual_address, frame_number in new_mapping.items():
            self.tlb.update(virtual_address, frame_number)

        for virtual_address, frame_number in new_mapping.items():
            self.assertEqual(self.tlb.query(virtual_address).frame_number, frame_number)

        self.assertEqual(self.tlb.query(last_virtual_address).frame_number, last_frame_number)


class CacheTest(unittest.TestCase):
    def setUp(self):
        self.l1_cache = DirectCacheBase(cache_size=Size.KB * 32, cache_line_size=Size.B * 64,
                                        replace_algorithm=CacheReplaceAlgorithm.FIFO)
        self.l2_cache = AssociativeCacheBase(associative=Associativity.SetAssociative, n_way=4,
                                             cache_size=Size.KB * 512, cache_line_size=Size.B * 64,
                                             replace_algorithm=CacheReplaceAlgorithm.FIFO)

    def test_direct_cache(self):
        pass


if __name__ == '__main__':
    unittest.main()
