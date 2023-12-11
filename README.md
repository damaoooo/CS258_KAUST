# CS258 Course Project

## Quick Start

```bash
make -j
./test_sys_mem.out
```

Note: Compiler should support C++17 at minimal.

## Directory Structure

- Fetcher: Fetch Unit
    - Contains 1KB Instruction Tightly-Coupled Memory (ITCM)
- Decoder: Decode Unit
    - Contains a Register Bank with 3 Read and 1 Write Ports
- ALU: Arithmetic Logic Unit
- LSU: Load Store Unit
    - Contains 1KB Data Tightly-Coupled Memory (DTCM)
- WB: Write Back Datapath

Supporting files:

- Base.hpp: Provide the support for our programming model
- Common.hpp: Definition of Instructions and Control Signals
- Log.hpp: A C++20 Style Log Libray adopted from OmNICreduce Project

## Design

- Five-stage
    - Fetch
    - Decode
    - Execute
    - Load/Store
    - Writeback
- Single-issue
- In-order

Note: due to the time constrain, we adopted the simplifed design:

- ALU
    - Use "magic C++ code" to perform complex INT/FP operations
    - All ALU operations can be done in 1 cycle
- Decoder
    - Non-pipelined design
- Load Store Unit
    - ITCM and DTCM do not share the same memory space
    - Drop the support for I/O instrutions