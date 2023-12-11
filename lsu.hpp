#pragma once

#include "base.hpp"
#include "log.hpp"
#include "decoder.hpp"
#include "sram.hpp"
#include "common.hpp"
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>

namespace proj {

class Lsu : public Device {
 public:
  Lsu() : Device() {
    lsu_addr = MakeWire<uint64_t>([&](){
      auto sig = in_lsu_sig->Read();
      return MuxFunc(sig.lsu_addr_src);
    });

    lsu_dat = MakeWire<uint64_t>([&](){
      auto sig = in_lsu_sig->Read();
      return MuxFunc(sig.lsu_dat_src);
    });

    dtcm_param = MakeWire<SramParam>([&](){
      auto op = in_lsu_sig->Read().lsu_op;
      return SramParam{
        op == LsuOp::kLoad && in_lsu_en->Read() ? lsu_addr->Read() : 0,
        {
          op == LsuOp::kStore && in_lsu_en->Read(),
          op == LsuOp::kStore && in_lsu_en->Read() ? lsu_dat->Read() : 0
        }
      };
    });

    dtcm = std::make_shared<Sram<>>();

    out_dat = MakeWire<uint64_t>([&](){
      return dtcm->out_dat->Read();
    });

    RegisterDevice({dtcm});
  }

  uint64_t MuxFunc(LsuSrc src) {
    switch (src) {
      case LsuSrc::kReg31: return in_regs->Read().rs - 8;
      case LsuSrc::kRegS: return in_regs->Read().rs;
      case LsuSrc::kAlu: return in_alu_out->Read();
      case LsuSrc::kPcPlus4: return in_pc_plus_4->Read();
      default: return (uint64_t)12345678;
    }
  }

  void Connect(InputPtr<bool> lsu_en, InputPtr<LsuCtrlSig> lsu_sig, InputPtr<Regs> regs,
      InputPtr<uint64_t> alu_out, InputPtr<uint64_t> pc_plus_4) {
    
    in_lsu_en = lsu_en;
    in_lsu_sig = lsu_sig;
    in_regs = regs;
    in_alu_out = alu_out;
    in_pc_plus_4 = pc_plus_4;

    dtcm->Connect(dtcm_param);
  }

  void Load(std::vector<uint64_t>&& dat) {
    dtcm->Load(std::move(dat));
  }

 public:
  WirePtr<uint64_t> out_dat;

 public:
  InputPtr<bool> in_lsu_en;
  InputPtr<LsuCtrlSig> in_lsu_sig;
  InputPtr<Regs> in_regs;
  InputPtr<uint64_t> in_alu_out;
  InputPtr<uint64_t> in_pc_plus_4;

  std::shared_ptr<Sram<>> dtcm;
  WirePtr<uint64_t> lsu_addr;
  WirePtr<uint64_t> lsu_dat;
  WirePtr<SramParam> dtcm_param;
};

}
