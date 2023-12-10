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

  void Connect(WirePtr<uint64_t> input) {
    in = input;
  }

  WirePtr<uint64_t> out;

 public:
  WirePtr<uint64_t> in;
};

class Fetcher : public Device {
 public:
  Fetcher() : Device() {
    reg_pc = MakeReg<uint64_t>(0);
    
    fetch_addr = MakeWire<uint64_t>([&](){
      auto new_pc = in_pc_val->Read();
      return new_pc.is_valid ? new_pc.val : reg_pc->Read();
    });

    itcm_param = MakeWire<SramParam>([&](){
      return SramParam{fetch_addr->Read(), {false, 0}};
    });

    adder4 = std::make_shared<Adder4>();
    adder4->Connect(fetch_addr);
    itcm = std::make_shared<Sram<>>(itcm_param);

    out_instr_addr = MakeReg<Optional<uint64_t>>({false, 0});
    out_instr = MakeWire<uint32_t>([&](){
      auto instr_addr = out_instr_addr->Read();
      auto itcm_dat = itcm->out_dat->Read();
      auto instr = (instr_addr.val & 0b100) > 0 ? itcm_dat >> 32 : itcm_dat;
      return instr & ((1ul << 32) - 1);
    });

    RegisterDevice({reg_pc, adder4, itcm, out_instr_addr});
  }

  void Connect(InputPtr<bool> fu_en, InputPtr<Optional<uint64_t>> pc_val) {
    in_fu_en = fu_en;
    in_pc_val = pc_val;
  }

  void DoFunction() override {
    Device::DoFunction();
    if (in_fu_en->Read()) {
      reg_pc->Write(adder4->out->Read());
      WARN("Go {}, fet={}", reg_pc->next_val_, fetch_addr->Read());
      out_instr_addr->Write({true, fetch_addr->Read()});
    } else {
      // reg_pc->Write(fetch_addr->Read());
      out_instr_addr->Write({true, fetch_addr->Read()});
    }
  }

  void Load(std::vector<uint64_t>&& dat) {
    itcm->Load(std::move(dat));
  }
 
 public:
  WirePtr<uint32_t> out_instr;
  RegPtr<Optional<uint64_t>> out_instr_addr;
  
 public:
  InputPtr<bool> in_fu_en;
  InputPtr<Optional<uint64_t>> in_pc_val;

  std::shared_ptr<Sram<>> itcm;
  std::shared_ptr<Adder4> adder4;
  RegPtr<uint64_t> reg_pc;
  WirePtr<uint64_t> fetch_addr;
  WirePtr<SramParam> itcm_param;
};

}