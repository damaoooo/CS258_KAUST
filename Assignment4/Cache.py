from Utils import *
import math
from collections import deque
from typing import List, Tuple, Union
import random


class DirectCacheBase:
    # If it is direct matched, there will be no replace algorithm
    def __init__(self, cache_size: int, cache_line_size: int, replace_algorithm: CacheReplaceAlgorithm):
        self.cache_size = cache_size
        self.cache_line_size = cache_line_size
        self.replace_algorithm = replace_algorithm

        self.cache_line_num = self.cache_size // self.cache_line_size

        self.offset_bits = int(math.log2(self.cache_line_size))
        self.index_bits = int(math.log2(self.cache_line_num))

        self.hits = 0
        self.misses = 0
        self.cache: List[Tuple] = [() for _ in range(self.cache_line_num)]

    def __contains__(self, item):
        return self.access_cache_free(item)

    def get_evict_index(self, address: int) -> int:
        # there is no evict algorithm in L1 Direct map cache
        index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)

        return index

    def access_cache(self, address: int, value: bytes = None) -> bool:

        index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)

        if self.cache[index] and self.cache[index][0] == tag:
            self.hits += 1
            return True
        else:
            self.misses += 1
            return False

    def access_cache_free(self, address):
        result = self.access_cache(address)
        if result:
            self.hits -= 1
        else:
            self.misses -= 1
        return result

    def replace_cache_line(self, address: int, value: bytes):
        tag: int = address >> (self.offset_bits + self.index_bits)
        replace_index: int = self.get_evict_index(address)
        self.cache[replace_index] = (tag, value)

    def flush(self):
        self.cache = [() for _ in range(self.cache_line_num)]
        self.helper_queue = deque()

    def read_cache(self, address: int):
        assert self.access_cache(address)
        index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        return self.cache[index][1]

    def write_cache(self, address: int, value: bytes):
        assert self.access_cache(address)
        index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        self.cache[index] = (self.cache[index][0], value)


class AssociativeCacheBase(DirectCacheBase):
    def __init__(self, associative: Associativity, n_way: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.associative = associative
        self.n_way = n_way

        self.num_sets = self.cache_line_num // self.n_way
        self.index_bits = int(math.log2(self.num_sets))

        self.cache: List[List[tuple]] = [[() for _ in range(self.n_way)] for _ in range(self.num_sets)]
        self.policy_data = [[0 for _ in range(self.n_way)] for _ in range(self.num_sets)]

    def replace_set_cache_line(self, set_index: int, tag: int, value: bytes):
        set_cache: List[Tuple] = self.cache[set_index]
        policy_data: List[int] = self.policy_data[set_index]

        is_full = True
        empty_n_way = 0
        for n_way in range(len(set_cache)):
            if not set_cache[n_way]:
                is_full = False
                empty_n_way = n_way
                break

        if is_full:
            if self.replace_algorithm == CacheReplaceAlgorithm.Random:
                replace_index: int = random.randint(0, self.n_way - 1)
            elif self.replace_algorithm in [CacheReplaceAlgorithm.LRU, CacheReplaceAlgorithm.FIFO]:
                replace_index: int = policy_data.index(min(policy_data))
            else:
                replace_index: int = set_cache.index(()) if () in set_cache else 0
        else:
            replace_index: int = empty_n_way

        set_cache[replace_index] = (tag, value)

        if self.replace_algorithm == CacheReplaceAlgorithm.LRU:
            policy_data[replace_index] = self.hits
        elif self.replace_algorithm == CacheReplaceAlgorithm.FIFO:
            policy_data[replace_index] = self.hits + self.misses
        else:
            policy_data[replace_index] = 0

        self.policy_data[set_index] = policy_data
        self.cache[set_index] = set_cache

    def access_cache(self, address: int, value: bytes = None) -> bool:
        set_index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)

        set_cache: List[Tuple] = self.cache[set_index]
        tags_in_set: List[int] = [line[0] for line in set_cache if line]

        if tag in tags_in_set:
            way: int = tags_in_set.index(tag)
            self.hits += 1
            if self.replace_algorithm == CacheReplaceAlgorithm.LRU:
                self.policy_data[set_index][way] = self.hits
            return True
        else:
            self.misses += 1
            return False
            # self.replace_set_cache_line(set_index, tag, value)

    def read_cache(self, address: int):
        assert self.access_cache_free(address)
        set_index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)
        set_cache: List[Tuple] = self.cache[set_index]
        tags_in_set: List[int] = [line[0] for line in set_cache if line]
        way = tags_in_set.index(tag)
        return set_cache[way][1]

    def write_cache(self, address: int, value: bytes):
        assert self.access_cache_free(address)
        set_index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)
        set_cache: List[tuple] = self.cache[set_index]
        tags_in_set: List[int] = [line[0] for line in set_cache if line]
        way: int = tags_in_set.index(tag)
        set_cache[way] = (tag, value)
        self.cache[set_index] = set_cache

    def replace_cache_line(self, address: int, value: bytes):
        set_index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)

        self.replace_set_cache_line(set_index, tag, value)

    def flush(self):
        self.cache: List[List[tuple]] = [[() for _ in range(self.n_way)] for _ in range(self.num_sets)]
        self.policy_data = [[0 for _ in range(self.n_way)] for _ in range(self.num_sets)]

    def access_cache_free(self, address):
        set_index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)
        set_cache: List[Tuple] = self.cache[set_index]
        tags_in_set: List[int] = [line[0] for line in set_cache if line]

        if tag not in tags_in_set:
            return False

        way = tags_in_set.index(tag)
        before_hit = self.policy_data[set_index][way]
        result = self.access_cache(address)
        if result:
            self.hits -= 1
            if self.replace_algorithm == CacheReplaceAlgorithm.LRU:

                self.policy_data[set_index][way] = before_hit
        else:
            self.misses -= 1
        return result


class Level2Cache:
    def __init__(self):
        self.L1Cache = DirectCacheBase(cache_size=32 * Size.KB, cache_line_size=32 * Size.B,
                                       replace_algorithm=CacheReplaceAlgorithm.LRU)
        self.L2Cache = AssociativeCacheBase(associative=Associativity.SetAssociative, n_way=4,
                                            cache_size=512 * Size.KB, cache_line_size=32 * Size.B,
                                            replace_algorithm=CacheReplaceAlgorithm.LRU)

    def read_cache(self, address: int) -> (int, bytes):
        if self.L1Cache.access_cache(address):
            return CacheLevel.L1, self.L1Cache.read_cache(address)
        elif self.L2Cache.access_cache(address):
            value = self.L2Cache.read_cache(address)
            self.L1Cache.replace_cache_line(address, value)
            return CacheLevel.L2, value
        else:
            return CacheLevel.NoCache, None

    def write_cache(self, address: int, value: bytes):
        if self.L1Cache.access_cache(address):
            self.L1Cache.write_cache(address, value)
            return CacheLevel.L1
        elif self.L2Cache.access_cache(address):
            self.L2Cache.write_cache(address, value)
            self.L1Cache.replace_cache_line(address, value)
            return CacheLevel.L2
        else:
            self.L2Cache.replace_cache_line(address, value)
            self.L1Cache.replace_cache_line(address, value)
            return CacheLevel.NoCache

    def flush(self):
        self.L1Cache.flush()
        self.L2Cache.flush()

    def __contains__(self, item):
        return item in self.L1Cache or item in self.L2Cache
