#include "base.hpp"
#include "common.hpp"
#include "fetcher.hpp"
#include "decoder.hpp"
#include "mux.hpp"
#include <cstdint>
#include <memory>
#include <vector>

using namespace proj;

void Show(int lineno, std::shared_ptr<Fetcher> fetcher, std::shared_ptr<Decoder> decoder) {
  INFO("{}, addr={}, instr={}, stat={}, fu_en={}, alu_en={}, lsu_en={}, alu_op={}, alu_p0={}, alu_p1={}, rs={}, rd={}, rt={}",
    lineno,
    fetcher->out_pc->Read(),
    fetcher->out_instr->Read(),
    AsInt(decoder->state->Read()),
    decoder->out_fu_en->Read(),
    decoder->out_alu_en->Read(),
    decoder->out_lsu_en->Read(),
    AsInt(decoder->out_alu_sig->Read().alu_op),
    AsInt(decoder->out_alu_sig->Read().alu_p0),
    AsInt(decoder->out_alu_sig->Read().alu_p1),
    decoder->out_reg_id->Read().rd,
    decoder->out_reg_id->Read().rs,
    decoder->out_reg_id->Read().rt
  );
}

void TestBitfield() {
  auto ins = Instr{1, 0, 0, 0, 0};
  CHECK(((ins.AsUInt32() >> 0) & 1) == 1, "");

  ins = Instr{0, 1, 0, 0, 0};
  CHECK(((ins.AsUInt32() >> 5) & 1) == 1, "");

  ins = Instr{0, 0, 1, 0, 0};
  CHECK(((ins.AsUInt32() >> 10) & 1) == 1, "");

  ins = Instr{0, 0, 0, 1, 0};
  CHECK(((ins.AsUInt32() >> 15) & 1) == 1, "");

  ins = Instr{0, 0, 0, 0, 1};
  CHECK(((ins.AsUInt32() >> 20) & 1) == 1, "");
}

int main() {
  auto pc_val = MakeReg<Optional<uint64_t>>({false, 0});
  auto fetcher = std::make_shared<Fetcher>();
  auto decoder = std::make_shared<Decoder>();
  fetcher->Connect(decoder->out_fu_en, pc_val);
  decoder->Connect(fetcher->out_instr);
  // auto decoder = std::make_shared<Fetcher>();
  fetcher->Load(BuildItcm({
    {AsInt(InstrType::kAddi), 0, 0, 0, 5},
    {AsInt(InstrType::kAddi), 1, 0, 0, 5}
  }));
  
  System::Register({pc_val, fetcher, decoder});

  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
  Show(__LINE__, fetcher, decoder);

  System::Run(1);
 

  return 0; 
}