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
  INFO("{}, addr={}, instr={}, fu_en={}, stat={}",
    lineno,
    fetcher->out_pc->Read(),
    fetcher->out_instr->Read(),
    decoder->out_fu_en->Read(),
    AsInt(decoder->state->Read())
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
  decoder->Connect(fetcher->out_instr, fetcher->out_pc);
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