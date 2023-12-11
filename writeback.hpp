#pragma once

#include "base.hpp"
#include "log.hpp"
#include "decoder.hpp"
#include "regbank.hpp"
#include "sram.hpp"
#include "common.hpp"
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>

namespace proj {

class Writeback : public Device {
 public:
  Writeback() : Device() {
    wb_src = MakeWire<uint64_t>([&](){
      auto alu = in_alu_out->Read();
      auto lsu = in_lsu_out->Read();

      switch (in_wb_sig->Read().src) {
      case WbSrc::kAlu: return alu;
      case WbSrc::kLsu: return lsu;
      case WbSrc::kAluCond: {
        return alu != 0 ? in_regs->Read().rd : in_pc_plus_4->Read();
      }
      default: return (uint64_t)12345678;
      }
    });

    out_reg_wb = MakeWire<Optional<uint64_t>>([&](){
      auto wb_en = in_wb_en->Read();
      auto wb_dst = in_wb_sig->Read().dst;
      return Optional<uint64_t>{
        wb_en && wb_dst == WbDst::kRegD,
        wb_src->Read()
      };
    });

    out_pc_wb = MakeWire<Optional<uint64_t>>([&](){
      auto wb_en = in_wb_en->Read();
      auto wb_dst = in_wb_sig->Read().dst;
      return Optional<uint64_t>{
        wb_en,
        wb_dst == WbDst::kRegPC ? wb_src->Read() : in_pc_plus_4->Read()
      };
    });

    RegisterDevice({});
  }

  void Connect(InputPtr<bool> wb_en, InputPtr<WbCtrlSig> wb_sig, InputPtr<Regs> regs,
      InputPtr<uint64_t> alu_out, InputPtr<uint64_t> lsu_out, InputPtr<uint64_t> pc_plus_4) {
    
    in_wb_en = wb_en;
    in_wb_sig = wb_sig;
    in_regs = regs;
    in_alu_out = alu_out;
    in_lsu_out = lsu_out;
    in_pc_plus_4 = pc_plus_4;
  }

 public:
  WirePtr<Optional<uint64_t>> out_reg_wb;
  WirePtr<Optional<uint64_t>> out_pc_wb;

 public:
  InputPtr<bool> in_wb_en;
  InputPtr<WbCtrlSig> in_wb_sig;
  InputPtr<Regs> in_regs;
  InputPtr<uint64_t> in_alu_out;
  InputPtr<uint64_t> in_lsu_out;
  InputPtr<uint64_t> in_pc_plus_4;

  WirePtr<uint64_t> wb_src;
};

}
