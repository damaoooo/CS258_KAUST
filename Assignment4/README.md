


 
Please refer to drawcase08.ipynb and drawcase015.ipynb for the report. We found that ./spec_benchmark/008.espresso.din only accesses three addresses. Most of it is accommodated in the L1 cache, so it is unrelated to cache size.


Arguments

1. Cache line size :  32-byte, 64-byte and 128-byte.
2. cache size of 32KB and 64KB for the L1, (1 cycle and 2 cycle access time, respectively)
3. L2 (512K, 1MB and 2MB, with 8, 12 and 16 cycles respectively). Memory is at 100 cycles away.
4. L1 is split in half between instructions and data.
5. Cache replacement algorithm: random, versus LRU. versus FIFO. Use a split L1 cache. Make the L2 4-way set associative.
6. L2 is direct mapped, versus 2-way and 4-way set associative. Use the random replacement policy and a split L1 cache.

Reference

1. https://github.com/bhavin392/Two-Level-Cache-Simulator-with-Translation-Lookaside-Buffer-TLB-/tree/master


