#pragma once

#include "base.hpp"
#include "sram.hpp"
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>

namespace proj {

class Adder4 : public Device {
 public:
  Adder4() : Device() {
    out = MakeWire<uint64_t>([&](){
      return this->in->Read() + 4;
    });
  }

  void Connect(InputPtr<uint64_t> input) {
    in = input;
  }

  WirePtr<uint64_t> out;

 public:
  InputPtr<uint64_t> in;
};

class Fetcher : public Device {
 public:
  Fetcher() : Device() {
    reg_pc = MakeReg<uint64_t>(0);

    itcm_param = MakeWire<SramParam>([&](){
      return SramParam{reg_pc->Read(), {false, 0}};
    });

    adder4 = std::make_shared<Adder4>();
    adder4->Connect(reg_pc);
    itcm = std::make_shared<Sram<>>(itcm_param);

    out_pc = MakeWire<uint64_t>([&](){
      return reg_pc->Read();
    });

    out_instr = MakeWire<uint32_t>([&](){
      auto instr_addr = reg_pc->Read();
      auto itcm_dat = itcm->out_dat->Read();
      auto instr = (instr_addr & 0b100) > 0 ? itcm_dat >> 32 : itcm_dat;
      return instr & ((1ul << 32) - 1);
    });

    out_pc_plus_4 = adder4->out;

    RegisterDevice({reg_pc, adder4, itcm});
  }

  void Connect(InputPtr<bool> fu_en, InputPtr<Optional<uint64_t>> pc_val) {
    in_fu_en = fu_en;
    in_pc_val = pc_val;
  }

  void DoFunction() override {
    Device::DoFunction();
    auto new_pc = in_pc_val->Read();
    if (new_pc.is_valid) {
      reg_pc->Write(new_pc.val);
    }
  }

  void Load(std::vector<uint64_t>&& dat) {
    itcm->Load(std::move(dat));
  }
 
 public:
  WirePtr<uint32_t> out_instr;
  WirePtr<uint64_t> out_pc;
  WirePtr<uint64_t> out_pc_plus_4;
  
 public:
  InputPtr<bool> in_fu_en;
  InputPtr<Optional<uint64_t>> in_pc_val;

  std::shared_ptr<Sram<>> itcm;
  std::shared_ptr<Adder4> adder4;
  RegPtr<uint64_t> reg_pc;
  WirePtr<SramParam> itcm_param;
};

}