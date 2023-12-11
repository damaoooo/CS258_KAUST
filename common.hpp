#pragma once

#include "base.hpp"
#include "log.hpp"
#include <cstdint>
#include <vector>

namespace proj {

template <typename FromType, typename ToType>
struct Caster {
  union {
    FromType from;
    ToType to;
  } data;
  static ToType Cast(FromType from) {
    static_assert(sizeof(FromType) == sizeof(ToType));
    Caster<FromType, ToType> converter;
    converter.data.from = from;
    return converter.data.to;
  }
};

struct Instr {
  uint64_t op : 5;
  uint64_t rd : 5;
  uint64_t rs : 5;
  uint64_t rt : 5;
  uint64_t imm : 12;

  uint32_t AsUInt32() {
    return Caster<Instr, uint32_t>::Cast(*this);
  }

  static Instr FromUInt32(uint32_t raw_data) {
    return Caster<uint32_t, Instr>::Cast(raw_data);
  }

} __attribute__((packed));

static_assert(sizeof(Instr) == sizeof(uint32_t));

enum class InstrType : uint64_t {
  kAdd = 0,
  kAddi = 1,
  kSub = 2,
  kSubi = 3,
  kMul = 4,
  kDiv = 5,
  kAnd = 6,
  kOr = 7,
  kXor = 8,
  kNot = 9,
  kShftr = 10,
  kShftri = 11,
  kShftl = 12,
  kShftli = 13,
  kBr = 14,
  kBrr = 15,
  kBri = 16,
  kBrnz = 17,
  kCall = 18,
  kReturn = 19,
  kBrgt = 20,
  kLd = 21,
  kMov = 22,
  kMovi = 23,
  kSt = 24,
  kAddf = 25,
  kSubf = 26,
  kMulf = 27,
  kDivf = 28,
  kIn = 29,
  kOut = 30,
  kHalt = 31
};

enum class RegMapOpt : uint64_t {
  kDirect = 0,
  kMapToR31 = 1,
  kDisabled = 2
};

enum class AluSrc : uint64_t {
  kNone = 0,
  kRegD = 1,
  kRegS = 2,
  kRegT = 3,
  kImm = 4,
  kPc = 5,
  kConst0 = 6
};

enum class AluOp : uint64_t {
  kNone = 0,
  kIntAdd = 1,
  kIntSub = 2,
  kIntMul = 3,
  kIntDiv = 4,
  kFpAdd = 5,
  kFpSub = 6,
  kFpMul = 7,
  kFpDiv = 8,
  kLogicAnd = 9,
  kLogicOr = 10,
  kLogicXor = 11,
  kLogicNot = 12,
  kShiftR = 13,
  kShiftL = 14,
  kCmpNeq = 15,
  kCmpGt = 16,
  kSetHigh12 = 17,
};

enum class LsuOp : uint64_t {
  kNop = 0,
  kLoad = 1,
  kStore = 2
};

enum class LsuSrc : uint64_t {
  kNone = 0,
  kReg31 = 1,
  kRegS = 3,
  kAlu = 5,
  kPcPlus4 = 6
};

enum class WbDst : uint64_t {
  kNone = 0,
  kRegD = 1,
  kRegPC = 2
};

enum class WbSrc : uint64_t {
  kNone = 0,
  kAlu = 1,
  kLsu = 2,
  kAluCond = 3,
};

struct RegMapEntry {
  RegMapOpt rd;
  RegMapOpt rs;
  RegMapOpt rt;
};

struct AluCtrlSig {
  AluOp alu_op;
  AluSrc alu_p0;
  AluSrc alu_p1;
};

struct LsuCtrlSig {
  LsuOp lsu_op;
  LsuSrc lsu_addr_src;
  LsuSrc lsu_dat_src;
};

struct WbCtrlSig {
  WbSrc src;
  WbDst dst;
};

inline RegMapEntry reg_map_tab[] = {
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},

  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDisabled},

  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDisabled, RegMapOpt::kDisabled},

  {RegMapOpt::kDirect, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
  {RegMapOpt::kDisabled, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDisabled},

  {RegMapOpt::kDirect, RegMapOpt::kMapToR31, RegMapOpt::kDisabled},
  {RegMapOpt::kDisabled, RegMapOpt::kMapToR31, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},

  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDisabled},

  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  {RegMapOpt::kDirect, RegMapOpt::kDirect, RegMapOpt::kDirect},
  
  {RegMapOpt::kDisabled, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
  {RegMapOpt::kDisabled, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
  {RegMapOpt::kDisabled, RegMapOpt::kDisabled, RegMapOpt::kDisabled},
};

inline AluCtrlSig alu_sig_tab[] = {
  {AluOp::kIntAdd, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kIntAdd, AluSrc::kRegS, AluSrc::kImm},
  {AluOp::kIntSub, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kIntSub, AluSrc::kRegS, AluSrc::kImm},
  {AluOp::kIntMul, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kIntDiv, AluSrc::kRegS, AluSrc::kRegT},

  {AluOp::kLogicAnd, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kLogicOr, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kLogicXor, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kLogicNot, AluSrc::kRegS, AluSrc::kConst0},

  {AluOp::kShiftR, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kShiftR, AluSrc::kRegS, AluSrc::kImm},
  {AluOp::kShiftL, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kShiftL, AluSrc::kRegS, AluSrc::kImm},

  {AluOp::kIntAdd, AluSrc::kRegD, AluSrc::kConst0},
  {AluOp::kIntAdd, AluSrc::kRegD, AluSrc::kPc},
  {AluOp::kIntAdd, AluSrc::kRegD, AluSrc::kImm},
  {AluOp::kCmpNeq, AluSrc::kRegS, AluSrc::kConst0},
  {AluOp::kIntAdd, AluSrc::kRegD, AluSrc::kConst0},
  {AluOp::kIntAdd, AluSrc::kConst0, AluSrc::kConst0},
  {AluOp::kCmpGt, AluSrc::kRegS, AluSrc::kRegT},

  {AluOp::kIntAdd, AluSrc::kRegS, AluSrc::kImm},
  {AluOp::kIntAdd, AluSrc::kRegS, AluSrc::kConst0},
  {AluOp::kSetHigh12, AluSrc::kRegD, AluSrc::kImm},
  {AluOp::kIntAdd, AluSrc::kRegS, AluSrc::kImm},

  {AluOp::kFpAdd, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kFpSub, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kFpMul, AluSrc::kRegS, AluSrc::kRegT},
  {AluOp::kFpDiv, AluSrc::kRegS, AluSrc::kRegT},
  
  {AluOp::kIntAdd, AluSrc::kConst0, AluSrc::kConst0},
  {AluOp::kIntAdd, AluSrc::kConst0, AluSrc::kConst0},
  {AluOp::kIntAdd, AluSrc::kConst0, AluSrc::kConst0}
};

inline LsuCtrlSig lsu_sig_tab[] = {
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},

  {LsuOp::kStore, LsuSrc::kReg31, LsuSrc::kPcPlus4},
  {LsuOp::kLoad, LsuSrc::kReg31, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kLoad, LsuSrc::kAlu, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kStore, LsuSrc::kAlu, LsuSrc::kRegS},

  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
  {LsuOp::kNop, LsuSrc::kNone, LsuSrc::kNone},
};

inline WbCtrlSig wb_sig_tab[] = {
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},

  {WbSrc::kAlu, WbDst::kRegPC},
  {WbSrc::kAlu, WbDst::kRegPC},
  {WbSrc::kAlu, WbDst::kRegPC},
  {WbSrc::kAluCond, WbDst::kRegPC},
  {WbSrc::kAlu, WbDst::kRegPC},
  {WbSrc::kLsu, WbDst::kRegPC},
  {WbSrc::kAluCond, WbDst::kRegPC},

  {WbSrc::kLsu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kNone, WbDst::kNone},

  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},
  {WbSrc::kAlu, WbDst::kRegD},

  {WbSrc::kNone, WbDst::kNone},
  {WbSrc::kNone, WbDst::kNone},
  {WbSrc::kNone, WbDst::kNone},
};

inline std::vector<uint64_t> BuildItcm(std::vector<Instr>&& instrs) {
  std::vector<uint64_t> itcm;
  CHECK(instrs.size() % 2 == 0, "");
  for (auto i = 0ul; i < instrs.size(); i += 2) {
    auto& i0 = instrs[i];
    auto& i1 = instrs[i + 1];
    itcm.push_back(((uint64_t)i1.AsUInt32() << 32) + i0.AsUInt32());
  }
  return itcm;
}

}