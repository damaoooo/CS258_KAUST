#pragma once

#include "base.hpp"
#include "log.hpp"
#include "decoder.hpp"
#include "common.hpp"
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>

namespace proj {

class AluCore : public Device {
 public:
  AluCore() : Device() {
    out = MakeReg<uint64_t>(0);
    RegisterDevice({out});
  }

  void Connect(InputPtr<bool> alu_en, InputPtr<AluCtrlSig> alu_sig, InputPtr<uint64_t> p0, InputPtr<uint64_t> p1) {
    in_alu_en = alu_en;
    in_alu_sig = alu_sig;
    in_p0 = p0;
    in_p1 = p1;
  }

  void DoFunction() override {
    Device::DoFunction();

    if (!in_alu_en->Read()) {
      return;
    }

    auto p0_u64 = in_p0->Read();
    auto p1_u64 = in_p1->Read();
    auto p0_i64 = Caster<uint64_t, int64_t>::Cast(in_p0->Read());
    auto p1_i64 = Caster<uint64_t, int64_t>::Cast(in_p1->Read());
    auto p0_f64 = Caster<uint64_t, double>::Cast(in_p0->Read());
    auto p1_f64 = Caster<uint64_t, double>::Cast(in_p1->Read());

    switch (in_alu_sig->Read().alu_op) {
    case AluOp::kIntAdd: out->Write(Caster<int64_t, uint64_t>::Cast(p0_i64 + p1_i64)); break;
    case AluOp::kIntSub: out->Write(Caster<int64_t, uint64_t>::Cast(p0_i64 - p1_i64)); break;
    case AluOp::kIntMul: out->Write(Caster<int64_t, uint64_t>::Cast(p0_i64 * p1_i64)); break;
    case AluOp::kIntDiv: out->Write(Caster<int64_t, uint64_t>::Cast(p0_i64 / p1_i64)); break;

    case AluOp::kFpAdd: out->Write(Caster<double, uint64_t>::Cast(p0_f64 + p1_f64)); break;
    case AluOp::kFpSub: out->Write(Caster<double, uint64_t>::Cast(p0_f64 - p1_f64)); break;
    case AluOp::kFpMul: out->Write(Caster<double, uint64_t>::Cast(p0_f64 * p1_f64)); break;
    case AluOp::kFpDiv: out->Write(Caster<double, uint64_t>::Cast(p0_f64 / p1_f64)); break;

    case AluOp::kLogicAnd: out->Write(p0_u64 & p1_u64); break;
    case AluOp::kLogicOr:  out->Write(p0_u64 | p1_u64); break;
    case AluOp::kLogicXor: out->Write(p0_u64 ^ p1_u64); break;
    case AluOp::kLogicNot: out->Write(~p0_u64); break;

    case AluOp::kShiftL: out->Write(p0_u64 << p1_u64); break;
    case AluOp::kShiftR: out->Write(p0_u64 >> p1_u64); break;
    case AluOp::kCmpNeq: out->Write(p0_u64 != p1_u64); break;
    case AluOp::kCmpGt:  out->Write(p0_i64 > p1_i64); break;

    case AluOp::kSetHigh12: {
      auto mask = (1ull << 52) - 1;
      out->Write((p0_i64 & ~mask) +  (p1_i64 << 52));
      break;
    }

    case AluOp::kNone: out->Write(12345678);
    }
  }

 public:
  RegPtr<uint64_t> out;

 public:
  InputPtr<bool> in_alu_en;
  InputPtr<AluCtrlSig> in_alu_sig;
  InputPtr<uint64_t> in_p0;
  InputPtr<uint64_t> in_p1;
};

class Alu : public Device {
 public:
  Alu() : Device() {
    alu_core = std::make_shared<AluCore>();

    alu_p0 = MakeWire<uint64_t>([&](){
      auto sig = in_alu_sig->Read();
      return MuxFunc(sig.alu_p0);
    });

    alu_p1 = MakeWire<uint64_t>([&](){
      auto sig = in_alu_sig->Read();
      return MuxFunc(sig.alu_p1);
    });

    out_dat =  MakeWire<uint64_t>([&](){
      return alu_core->out->Read();
    });

    RegisterDevice({alu_core});
  }

  uint64_t MuxFunc(AluSrc src) {
    switch (src) {
      case AluSrc::kRegD: return in_regs->Read().rd;
      case AluSrc::kRegS: return in_regs->Read().rs;
      case AluSrc::kRegT: return in_regs->Read().rt;
      case AluSrc::kImm: return in_dec_instr->Read().imm;
      case AluSrc::kPc: return in_pc->Read();
      case AluSrc::kConst0: return (uint64_t)0;
      default: return (uint64_t)12345678;
    }
  }

  void Connect(InputPtr<bool> alu_en, InputPtr<AluCtrlSig> alu_sig, InputPtr<Regs> regs,
      InputPtr<Instr> dec_instr, InputPtr<uint64_t> pc) {
    
    in_alu_en = alu_en;
    in_alu_sig = alu_sig;
    in_regs = regs;
    in_dec_instr = dec_instr;
    in_pc = pc;

    alu_core->Connect(in_alu_en, in_alu_sig, alu_p0, alu_p1);
  }

  void DoFunction() override {
    Device::DoFunction();
  }

 public:
  WirePtr<uint64_t> out_dat;

 public:
  std::shared_ptr<AluCore> alu_core;
  
  InputPtr<bool> in_alu_en;
  InputPtr<AluCtrlSig> in_alu_sig;
  InputPtr<Regs> in_regs;
  InputPtr<Instr> in_dec_instr;
  InputPtr<uint64_t> in_pc;

  WirePtr<uint64_t> alu_p0;
  WirePtr<uint64_t> alu_p1;
};

}
