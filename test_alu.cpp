#include "base.hpp"
#include "common.hpp"
#include "fetcher.hpp"
#include "decoder.hpp"
#include "alu.hpp"
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

void Show(int lineno) {
  INFO("{}, pc={}, fu_en={}, alu_en={}, lsu_en={}, alu_op={}, alu_p0={}, alu_p1={}, rs={}, rd={}, rt={}, alu_out={}",
    lineno,
    fetcher->out_pc->Read(),
    decoder->out_fu_en->Read(),
    decoder->out_alu_en->Read(),
    decoder->out_lsu_en->Read(),
    AsInt(decoder->out_alu_sig->Read().alu_op),
    // AsInt(decoder->out_alu_sig->Read().alu_p0),
    // AsInt(decoder->out_alu_sig->Read().alu_p1),
    alu->alu_p0->Read(),
    alu->alu_p1->Read(),

    // decoder->out_reg_id->Read().rd,
    // decoder->out_reg_id->Read().rs,
    // decoder->out_reg_id->Read().rt,

    regbank->out_reg_dat->Read().rd,
    regbank->out_reg_dat->Read().rs,
    regbank->out_reg_dat->Read().rt,

    alu->out_dat->Read()
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
  
  fetcher->Load(BuildItcm({
    {AsInt(InstrType::kAddi), 0, 0, 0, 5},
    {AsInt(InstrType::kAddi), 1, 0, 0, 5}
  }));
  
  System::Register({pc_val, wr_dat, fetcher, decoder, regbank, alu});

  for (auto i = 0; i < 10; i++) {
    Show(__LINE__);
    System::Run(1);
  }

  return 0; 
}