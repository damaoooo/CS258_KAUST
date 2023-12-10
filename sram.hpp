#pragma once

#include "base.hpp"
#include "log.hpp"
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace proj {

struct SramParam {
  uint64_t addr;
  Optional<uint64_t> write_dat;
};

template <size_t size = 1024>
class Sram : public Device {
 public:

  Sram(InputPtr<SramParam> SramParam) :          
      in_param(SramParam) {
    static_assert(size % sizeof(uint64_t) == 0);
    mem.resize(size / sizeof(uint64_t), 0);
    out_dat = MakeReg<uint64_t>(0);
    RegisterDevice({out_dat});
  }

  void DoFunction() override {
    auto in = in_param->Read();
    auto idx = in.addr / sizeof(uint64_t);
    out_dat->Write(mem[idx]);
    if (in.write_dat.is_valid) {
      mem[idx] = in.write_dat.val;
    }
  }

  void Load(std::vector<uint64_t>&& dat) {
    std::copy(dat.begin(), dat.end(), mem.begin());
  }

 public:
  RegPtr<uint64_t> out_dat;

 public:
  std::vector<uint64_t> mem;
  const InputPtr<SramParam> in_param;
};

}