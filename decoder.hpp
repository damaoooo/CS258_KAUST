#pragma once

#include "base.hpp"
#include "log.hpp"
#include "regbank.hpp"
#include "common.hpp"
#include <cstdint>
#include <cstdlib>
#include <cstring>

namespace proj {

enum class ProcState {
  kFetch = 0,
  kDecode = 1,
  kExecute = 2,
  kMemory = 3,
  kWriteback = 4
};

class Decoder : public Device {
 public:
  Decoder() : Device() { 
    state = MakeReg<ProcState>(ProcState::kFetch);

    out_dec_instr = MakeWire<Instr>([&](){
      return Instr::FromUInt32(in_instr->Read());
    });

    out_fu_en = MakeWire<bool>([&](){
      return state->Read() == ProcState::kFetch;
    });

    out_alu_en = MakeWire<bool>([&](){
      return state->Read() == ProcState::kExecute;
    });

    out_lsu_en = MakeWire<bool>([&](){
      return state->Read() == ProcState::kMemory;
    });

    out_wb_en = MakeWire<bool>([&](){
      return state->Read() == ProcState::kWriteback;
    });

    out_reg_map = MakeWire<RegMapEntry>([&](){
      return reg_map_tab[out_dec_instr->Read().op];
    });

    out_alu_sig = MakeWire<AluCtrlSig>([&](){
      return alu_sig_tab[out_dec_instr->Read().op];
    });

    out_lsu_sig = MakeWire<LsuCtrlSig>([&](){
      return lsu_sig_tab[out_dec_instr->Read().op];
    });

    out_wb_sig = MakeWire<WbCtrlSig>([&](){
      return wb_sig_tab[out_dec_instr->Read().op];
    });

    out_reg_id = MakeWire<Regs>([&](){
      auto dec = out_dec_instr->Read();
      auto map = out_reg_map->Read();
      return Regs{
        MapReg(map.rd, dec.rd),
        MapReg(map.rs, dec.rs),
        MapReg(map.rt, dec.rt)
      };
    });

    RegisterDevice({state});
  }

  static uint64_t MapReg(RegMapOpt op, uint64_t reg_id) {
    switch (op) {
    case RegMapOpt::kDirect: return reg_id;
    case RegMapOpt::kDisabled: return 32;
    case RegMapOpt::kMapToR31: return 31;
    }
    return 0;
  }

  void Connect(InputPtr<uint32_t> instr) {
    in_instr = instr;
  }

  void DoFunction() override {
    Device::DoFunction();
    switch (state->Read()) {
    case ProcState::kFetch: {
      state->Write(ProcState::kDecode);
      break;
    }
    case ProcState::kDecode:
      state->Write(ProcState::kExecute);
      break;
    case ProcState::kExecute:
      state->Write(ProcState::kMemory);
      break;
    case ProcState::kMemory:
      state->Write(ProcState::kWriteback);
      break;
    case ProcState::kWriteback:
      state->Write(ProcState::kFetch);
      break;
    }
  }
 
 public:
  WirePtr<bool> out_fu_en, out_alu_en, out_lsu_en, out_wb_en;
  WirePtr<RegMapEntry> out_reg_map;
  WirePtr<Regs> out_reg_id;
  WirePtr<AluCtrlSig> out_alu_sig;
  WirePtr<LsuCtrlSig> out_lsu_sig;
  WirePtr<WbCtrlSig> out_wb_sig;
  WirePtr<Instr> out_dec_instr;

 public:
  InputPtr<uint32_t> in_instr;
  RegPtr<ProcState> state;
  
};

}