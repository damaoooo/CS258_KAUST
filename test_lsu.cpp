#include "base.hpp"
#include "common.hpp"
#include "fetcher.hpp"
#include "decoder.hpp"
#include "alu.hpp"
#include "lsu.hpp"
#include "mux.hpp"
#include "regbank.hpp"
#include <cstdint>
#include <memory>
#include <vector>

using namespace proj;

auto fetcher = std::make_shared<Fetcher>();
auto decoder = std::make_shared<Decoder>();
auto regbank = std::make_shared<RegBank>();
auto alu = std::make_shared<Alu>();
auto lsu = std::make_shared<Lsu>();

void Show() {
  INFO("pc={}, fu_en={}, alu_en={}, lsu_en={}, wb_en={}, lsu_op={}, lsu_addr={}, lsu_dat={}, alu_out={}, lsu_out={}",
    fetcher->out_pc->Read(),
    decoder->out_fu_en->Read(),
    decoder->out_alu_en->Read(),
    decoder->out_lsu_en->Read(),
    decoder->out_wb_en->Read(),

    AsInt(decoder->out_lsu_sig->Read().lsu_op),
    AsInt(decoder->out_lsu_sig->Read().lsu_addr_src),
    AsInt(decoder->out_lsu_sig->Read().lsu_dat_src),

    alu->out_dat->Read(),
    lsu->out_dat->Read()
  );
}

int main() {
  auto pc_val = MakeReg<Optional<uint64_t>>({false, 0});
  auto wr_dat = MakeReg<Optional<uint64_t>>({false, 0});
  fetcher->Connect(decoder->out_fu_en, pc_val);
  decoder->Connect(fetcher->out_instr);
  regbank->Connect(decoder->out_reg_id, wr_dat);
  alu->Connect(decoder->out_alu_en, decoder->out_alu_sig, regbank->out_reg_dat,
    decoder->out_dec_instr, fetcher->out_pc);
  lsu->Connect(decoder->out_lsu_en, decoder->out_lsu_sig, regbank->out_reg_dat,
    alu->out_dat, fetcher->out_pc_plus_4);
  
  fetcher->Load(BuildItcm({
    {AsInt(InstrType::kLd), 2, 1, 0, 8},
    {AsInt(InstrType::kAddi), 1, 0, 0, 5}
  }));

  lsu->Load({1, 2, 3, 4});

  System::Register({pc_val, wr_dat, fetcher, decoder, regbank, alu, lsu});

  for (auto i = 0; i < 10; i++) {
    Show();
    System::Run(1);
  }

  return 0; 
}