from Utils import *
import math
from collections import deque
from typing import List, Tuple
import random


class DirectCacheBase:
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

        self.helper_queue = deque()

    def get_evict_index(self) -> int:
        if self.replace_algorithm == CacheReplaceAlgorithm.Random:
            return random.randint(0, self.cache_line_num - 1)

        if self.replace_algorithm in [CacheReplaceAlgorithm.LRU, CacheReplaceAlgorithm.FIFO]:
            replace_index: int = self.helper_queue.pop()
            self.helper_queue.appendleft(replace_index)
            return replace_index

        raise ValueError(f"Unknown cache policy: {self.replace_algorithm}")

    def access_cache(self, address: int, value: bytes):

        index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)

        if self.cache[index] and self.cache[index][0] == tag:
            self.hits += 1
            if self.replace_algorithm in [CacheReplaceAlgorithm.LRU, CacheReplaceAlgorithm.FIFO]:
                self.helper_queue.remove(index)
                self.helper_queue.appendleft(index)
        else:
            self.misses += 1
            self.replace_cache_line(tag, value)

    def replace_cache_line(self, tag: int, value: bytes):
        replace_index: int = self.get_evict_index()
        self.cache[replace_index] = (tag, value)

    def flush(self):
        self.cache = [() for _ in range(self.cache_line_num)]
        self.helper_queue = deque()


class AssociativeCacheBase(DirectCacheBase):
    def __init__(self, associative: Associativity, n_way: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.associative = associative
        self.n_way = n_way

        self.num_sets = self.cache_line_num // self.n_way
        self.cache = [[() for _ in range(self.n_way)] for _ in range(self.num_sets)]
        self.policy_data = [[0 for _ in range(self.n_way)] for _ in range(self.num_sets)]

    def replace_set_cache_line(self, set_index: int, tag: int, value: bytes):
        set_cache: List[Tuple] = self.cache[set_index]
        policy_data: List[int] = self.policy_data[set_index]

        if self.replace_algorithm == CacheReplaceAlgorithm.Random:
            replace_index: int = random.randint(0, self.n_way - 1)

        elif self.replace_algorithm == CacheReplaceAlgorithm.LRU:
            replace_index: int = policy_data.index(min(policy_data))

        elif self.replace_algorithm == CacheReplaceAlgorithm.FIFO:
            replace_index: int = policy_data.index(max(policy_data))

        else:
            replace_index: int = set_cache.index(()) if () in set_cache else 0

        set_cache[replace_index] = (tag, value)

        if self.replace_algorithm in [CacheReplaceAlgorithm.LRU, CacheReplaceAlgorithm.FIFO]:
            policy_data[replace_index] = self.hits
        else:
            policy_data[replace_index] = 0

    def access_cache(self, address: int, value: bytes):
        set_index: int = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag: int = address >> (self.offset_bits + self.index_bits)

        set_cache: List[Tuple] = self.cache[set_index]
        tags_in_set: List[int] = [line[0] for line in set_cache if line]

        if tag in tags_in_set:
            way: int = tags_in_set.index(tag)
            self.hits += 1
            if self.replace_algorithm in [CacheReplaceAlgorithm.LRU, CacheReplaceAlgorithm.FIFO]:
                self.policy_data[set_index][way] = self.hits
        else:
            self.misses += 1
            self.replace_set_cache_line(set_index, tag, value)


class Level2Cache:
    def __init__(self):
        self.L1Cache = DirectCacheBase(cache_size=32 * Size.KB, cache_line_size=32 * Size.B,
                                       replace_algorithm=CacheReplaceAlgorithm.LRU)
        self.L2Cache = AssociativeCacheBase(associative=Associativity.SetAssociative, n_way=4,
                                            cache_size=512 * Size.KB, cache_line_size=64 * Size.B,
                                            replace_algorithm=CacheReplaceAlgorithm.LRU)

    def read_cache(self):
        raise NotImplementedError

    def write_cache(self):
        raise NotImplementedError
