#pragma once

#include "base.hpp"
#include "log.hpp"
#include "common.hpp"
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace proj {

class RegBank : public Device {
 public:
  RegBank(InputPtr<uint64_t> in_rd0, InputPtr<uint64_t> in_rd1,
      InputPtr<uint64_t> in_wr, InputPtr<Optional<uint64_t>> in_wr_dat) :
      Device(), in_rd0_(in_rd0), in_rd1_(in_rd1), in_wr_(in_wr), in_wr_dat_(in_wr_dat) {
    
    for (auto i = 0ll; i < 32; i++) {
      regs_.push_back(MakeReg<uint64_t>(0));
      RegisterDevice({regs_.back()});
    }

    out_rd0 = MakeWire<uint64_t>([&](){
      return regs_[in_rd0_->Read()]->Read();
    });

    out_rd1 = MakeWire<uint64_t>([&](){
      return regs_[in_rd1_->Read()]->Read();
    });

  }

  void DoFunction() override {
    auto wr_dat = in_wr_dat_->Read();
    if (wr_dat.is_valid) {
      regs_[in_wr_->Read()]->Write(wr_dat.val);
    }
  }

 public:
  WirePtr<uint64_t> out_rd0, out_rd1;

 public:
  const InputPtr<uint64_t> in_rd0_, in_rd1_, in_wr_;
  const InputPtr<Optional<uint64_t>> in_wr_dat_;
  std::vector<RegPtr<uint64_t>> regs_;
};

}