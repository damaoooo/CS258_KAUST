import math
import random
import unittest
from Memory import Memory, MemoryPage, Size


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.memory = Memory(0)

    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_single_allocate(self):

        self.memory.flush()
        page = self.memory.allocate_page(Size.KB * 4)
        self.assertEqual(len(page), 1)
        self.assertEqual(page[0], 0)

    def test_multi_allocate(self, size=Size.MB * 100):
        self.memory.flush()
        pages = self.memory.allocate_page(size)
        num_pages = math.ceil(size / (4 * Size.KB))
        self.assertEqual(len(pages), num_pages)
        self.assertEqual(pages[0], 0)
        self.assertEqual(pages[-1], (num_pages - 1) * 4 * Size.KB)

    def test_write_and_read_byte(self, size=1000*Size.KB):
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


if __name__ == '__main__':
    unittest.main()
