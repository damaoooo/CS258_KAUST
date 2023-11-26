import math
import random
import unittest
from Simulator import SimulatorConfigure, Simulator
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
        for i in range(self.tlb.size - 1):
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

    def test_direct_cache_l1(self, address: int = 0x12345678, value: bytes = b'\x12\x34\x56\x78'):
        self.l1_cache.flush()

        if self.l1_cache.access_cache_free(address):
            print(self.l1_cache.read_cache(address))
        else:
            self.l1_cache.replace_cache_line(address, value)

        self.assertTrue(self.l1_cache.access_cache_free(address))
        self.assertFalse(self.l1_cache.access_cache_free(address + (1 << 8)))
        get_bytes = self.l1_cache.read_cache(address)
        self.assertEqual(get_bytes, value)

    def test_many_write_l1(self):
        self.l1_cache.flush()
        base_address = 0x12345678

        wrote_value = {}

        cache_line_offset = 1 << self.l1_cache.offset_bits

        for i in range(self.l1_cache.cache_line_num):
            varied_address = base_address + cache_line_offset * i
            value = random.randbytes(8)
            wrote_value[varied_address] = value
            self.assertFalse(self.l1_cache.access_cache(varied_address))
            self.l1_cache.replace_cache_line(varied_address, value)

        for address in wrote_value:
            self.assertEqual(self.l1_cache.read_cache(address), wrote_value[address])

        for i in range(self.l1_cache.cache_line_num):
            varied_address = base_address + cache_line_offset * (i + self.l1_cache.cache_line_num)
            value = random.randbytes(8)
            wrote_value[varied_address] = value
            self.l1_cache.replace_cache_line(varied_address, value)
            self.assertFalse(self.l1_cache.access_cache(base_address + cache_line_offset * i))

        for address in wrote_value:
            if address < base_address + cache_line_offset * self.l1_cache.cache_line_num:
                self.assertFalse(self.l1_cache.access_cache(address))
            else:
                self.assertEqual(self.l1_cache.read_cache(address), wrote_value[address])

    def test_direct_cache_l2(self, address: int = 0x12345678, value: bytes = b'\x12\x34\x56\x78'):
        self.l2_cache.flush()

        if self.l2_cache.access_cache(address):
            print(self.l2_cache.read_cache(address))
        else:
            self.l2_cache.replace_cache_line(address, value)

        self.assertTrue(self.l2_cache.access_cache(address))
        get_bytes = self.l2_cache.read_cache(address)
        self.assertEqual(get_bytes, value)

    def test_single_write_l2_fifo(self):
        self.l2_cache.replace_algorithm = CacheReplaceAlgorithm.FIFO
        self.l2_cache.flush()
        num_set = 1
        tag = 0

        wrote_value = {}

        for i in range(self.l2_cache.n_way):
            address = (num_set << self.l2_cache.offset_bits) + (tag << (self.l2_cache.index_bits + self.l2_cache.offset_bits))
            self.assertFalse(self.l2_cache.access_cache(address))
            value = random.randbytes(8)
            self.l2_cache.replace_cache_line(address, value)
            wrote_value[address] = value
            tag += 1

        for address in wrote_value:
            self.assertEqual(self.l2_cache.read_cache(address), wrote_value[address])

        new_wrote = {}
        for i in range(self.l2_cache.n_way):
            address = (num_set << self.l2_cache.offset_bits) + (tag << (self.l2_cache.index_bits + self.l2_cache.offset_bits))
            old_address = (num_set << self.l2_cache.offset_bits) + (tag % self.l2_cache.n_way << (self.l2_cache.index_bits + self.l2_cache.offset_bits))
            self.assertFalse(self.l2_cache.access_cache(address))
            value = random.randbytes(8)
            self.assertEqual(self.l2_cache.read_cache(old_address), wrote_value[old_address])
            self.l2_cache.replace_cache_line(address, value)
            self.assertFalse(self.l2_cache.access_cache(old_address))
            self.assertTrue(self.l2_cache.access_cache(address))
            new_wrote[address] = value

            self.assertEqual(self.l2_cache.read_cache(address), value)
            tag += 1

    def test_single_write_lru(self):
        self.l2_cache.replace_algorithm = CacheReplaceAlgorithm.LRU
        self.l2_cache.flush()
        num_set = 1
        tag = 0

        wrote_value = {}

        for i in range(self.l2_cache.n_way):
            address = (num_set << self.l2_cache.offset_bits) + (tag << (self.l2_cache.index_bits + self.l2_cache.offset_bits))
            self.assertFalse(self.l2_cache.access_cache(address))
            value = random.randbytes(8)
            self.l2_cache.replace_cache_line(address, value)
            wrote_value[address] = value
            tag += 1

        for address in wrote_value:
            self.assertTrue(self.l2_cache.access_cache(address))
            self.assertEqual(self.l2_cache.read_cache(address), wrote_value[address])

        new_wrote = {}
        for i in range(self.l2_cache.n_way):
            address = (num_set << self.l2_cache.offset_bits) + (tag << (self.l2_cache.index_bits + self.l2_cache.offset_bits))
            old_address = (num_set << self.l2_cache.offset_bits) + (tag % self.l2_cache.n_way << (self.l2_cache.index_bits + self.l2_cache.offset_bits))
            self.assertFalse(self.l2_cache.access_cache(address))
            value = random.randbytes(8)
            self.assertEqual(self.l2_cache.read_cache(old_address), wrote_value[old_address])
            self.l2_cache.replace_cache_line(address, value)
            self.assertFalse(self.l2_cache.access_cache(old_address))
            self.assertTrue(self.l2_cache.access_cache(address))
            new_wrote[address] = value

            self.assertEqual(self.l2_cache.read_cache(address), value)
            tag += 1

    def test_many_write_l2_fifo(self):
        self.l2_cache.replace_algorithm = CacheReplaceAlgorithm.FIFO
        self.l2_cache.flush()
        set_index = 0
        tag = 0
        wrote_value = {}
        for i in range(self.l2_cache.n_way):
            # print(tag)
            for j in range(self.l2_cache.num_sets):
                address = (set_index << self.l2_cache.offset_bits) + (tag << (self.l2_cache.index_bits + self.l2_cache.offset_bits))
                value = random.randbytes(8)
                self.assertFalse(self.l2_cache.access_cache(address))
                self.l2_cache.replace_cache_line(address, value)

                wrote_value[address] = value
                set_index += 1
            tag += 1

        for address in wrote_value:
            self.assertEqual(self.l2_cache.read_cache(address), wrote_value[address])


class SimulatorTest(unittest.TestCase):
    def setUp(self):
        self.simulator = Simulator(SimulatorConfigure(file_path='dummy.txt'))
        self.simulator.cache.flush()

    def test_page_walk(self):
        phy = self.simulator.page_walk(0x12345678)
        print(phy)
        phy2 = self.simulator.page_walk(0x12345678)
        self.assertEqual(phy, phy2)
        phy3 = self.simulator.page_walk(0x12345679)
        self.assertEqual(phy3, phy2)
        phy4 = self.simulator.page_walk(0x22345678)
        self.assertNotEqual(phy4, phy3)
        phy5 = self.simulator.page_walk(0x22345689)
        self.assertEqual(phy5, phy4)
        phy6 = self.simulator.page_walk(0x32345679)
        self.assertNotEqual(phy6, phy5)

    def test_dry_run(self):
        self.simulator.start_simulation()


if __name__ == '__main__':
    unittest.main()
