#include "base.hpp"
#include "common.hpp"
#include "fetcher.hpp"
#include "decoder.hpp"
#include "alu.hpp"
#include "lsu.hpp"
#include "mux.hpp"
#include "regbank.hpp"
#include "writeback.hpp"
#include <cstdint>
#include <memory>
#include <vector>

using namespace proj;

auto fetcher = std::make_shared<Fetcher>();
auto decoder = std::make_shared<Decoder>();
auto regbank = std::make_shared<RegBank>();
auto alu = std::make_shared<Alu>();
auto lsu = std::make_shared<Lsu>();
auto writeback = std::make_shared<Writeback>();

void Show() {
  if (decoder->state->Read() != proj::ProcState::kFetch) {
    return;
  }
  auto& r = regbank->regs;
  INFO("pc={} ({}), r0={}, r1={}, r2={}, r3={}, r4={}, r5={}, r6={}, r7={}, r31={}",
    fetcher->out_pc->Read(), fetcher->out_pc->Read() / 4,
    r[0]->Read(), r[1]->Read(), r[2]->Read(), r[3]->Read(),
    r[4]->Read(), r[5]->Read(), r[6]->Read(), r[7]->Read(),
    r[31]->Read()
    
  );
}

int main() {
  
  fetcher->Connect(decoder->out_fu_en, writeback->out_pc_wb);
  decoder->Connect(fetcher->out_instr);
  regbank->Connect(decoder->out_reg_id, writeback->out_reg_wb);
  alu->Connect(decoder->out_alu_en, decoder->out_alu_sig, regbank->out_reg_dat,
    decoder->out_dec_instr, fetcher->out_pc);
  lsu->Connect(decoder->out_lsu_en, decoder->out_lsu_sig, regbank->out_reg_dat,
    alu->out_dat, fetcher->out_pc_plus_4);
  writeback->Connect(decoder->out_wb_en, decoder->out_wb_sig, regbank->out_reg_dat,
    alu->out_dat, lsu->out_dat, fetcher->out_pc_plus_4);
  
  fetcher->Load(BuildItcm({
    {AsInt(InstrType::kAddi), 0, 0, 0, 8},
    {AsInt(InstrType::kBrr), 0, 0, 0, 0},
    {AsInt(InstrType::kSubi), 0, 0, 0, 4},
    {AsInt(InstrType::kBri), 0, 0, 0, 8},
    {AsInt(InstrType::kSubi), 0, 0, 0, 4},
    {AsInt(InstrType::kBrnz), 0, 0, 0, 0},
    {AsInt(InstrType::kBrnz), 0, 0, 0, 0},
    {AsInt(InstrType::kHalt), 0, 0, 0, 0},
  }));

  lsu->Load({1, 2, 3, 4});

  System::Register({fetcher, decoder, regbank, alu, lsu, writeback});

  while (!System::IsStopped() && System::GetClock() < 100) {
    Show();
    System::Run(1);
  }

  return 0; 
}