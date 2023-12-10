#pragma once

#include "base.hpp"
#include "log.hpp"
#include "common.hpp"
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace proj {

struct Regs {
  uint64_t rd;
  uint64_t rs;
  uint64_t rt;
};

class RegBank : public Device {
 public:
  RegBank() : Device() {
    
    for (auto i = 0ll; i < 33; i++) {
      // magic guard number
      regs.push_back(MakeReg<uint64_t>(i != 32 ? 0 : 12345678));
      RegisterDevice({regs.back()});
    }

    out_reg_dat = MakeWire<Regs>([&](){
      auto rid = in_reg_id->Read();
      return Regs{
        regs[rid.rd]->Read(),
        regs[rid.rs]->Read(),
        regs[rid.rt]->Read(),
      };
    });

  }

  void Connect(InputPtr<Regs> reg_id, InputPtr<Optional<uint64_t>> wr_dat) {
    in_reg_id = reg_id;
    in_wr_dat = wr_dat;
  }

  void DoFunction() override {
    Device::DoFunction();
    auto rid = in_reg_id->Read();
    auto wr_dat = in_wr_dat->Read();
    if (wr_dat.is_valid) {
      regs[rid.rd]->Write(wr_dat.val);
    }
  }

 public:
  WirePtr<Regs> out_reg_dat;

 public:
  InputPtr<Regs> in_reg_id;
  InputPtr<Optional<uint64_t>> in_wr_dat;
  std::vector<RegPtr<uint64_t>> regs;
};

}