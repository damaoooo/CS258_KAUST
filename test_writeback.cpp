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
  INFO("pc={}, instr={}, fu_en={}, alu_en={}, lsu_en={}, wb_en={}, wb_src={}, wb_dst={}, alu_out={}, lsu_out={}",
    fetcher->out_pc->Read(),
    decoder->out_fu_en->Read(),
    decoder->out_alu_en->Read(),
    decoder->out_lsu_en->Read(),
    decoder->out_wb_en->Read(),

    AsInt(decoder->out_wb_sig->Read().src),
    AsInt(decoder->out_wb_sig->Read().dst),

    alu->out_dat->Read(),
    lsu->out_dat->Read()
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
    {AsInt(InstrType::kAddi), 2, 1, 0, 8},
    {AsInt(InstrType::kAddi), 1, 2, 1, 5},
    {AsInt(InstrType::kAddi), 2, 1, 0, 8},
    {AsInt(InstrType::kAddi), 1, 2, 1, 5},
    {AsInt(InstrType::kAddi), 2, 1, 0, 8},
    {AsInt(InstrType::kAddi), 1, 2, 1, 5}
  }));

  lsu->Load({1, 2, 3, 4});

  System::Register({fetcher, decoder, regbank, alu, lsu, writeback});

  for (auto i = 0; i < 40; i++) {
    Show();
    System::Run(1);
  }

  return 0; 
}