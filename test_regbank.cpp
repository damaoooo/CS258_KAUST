#include "base.hpp"
#include "regbank.hpp"
#include <cstdint>
#include <memory>
#include <vector>

using namespace proj;

int main() {
  auto rd0 = MakeReg<uint64_t>(0);
  auto rd1 = MakeReg<uint64_t>(0);
  auto wr = MakeReg<uint64_t>(0);
  auto wr_dat = MakeReg<Optional<uint64_t>>({false, 0});

  auto regs = std::make_shared<RegBank>(rd0, rd1, wr, wr_dat);
  System::Register({rd0, rd1, wr, wr_dat, regs});

  INFO("rd0={}, rd1={}", regs->out_rd0->Read(), regs->out_rd1->Read());

  System::Run(1);
  INFO("rd0={}, rd1={}", regs->out_rd0->Read(), regs->out_rd1->Read());

  rd0->Write(1); rd1->Write(2); wr->Write(1); wr_dat->Write({true, 5});
  System::Run(1);
  INFO("rd0={}, rd1={}", regs->out_rd0->Read(), regs->out_rd1->Read());

  rd0->Write(1); rd1->Write(2); wr->Write(2); wr_dat->Write({true, 6});
  System::Run(1);
  INFO("rd0={}, rd1={}", regs->out_rd0->Read(), regs->out_rd1->Read());

  rd0->Write(2); rd1->Write(1); wr->Write(2); wr_dat->Write({false, 7});
  System::Run(1);
  INFO("rd0={}, rd1={}", regs->out_rd0->Read(), regs->out_rd1->Read());

  rd0->Write(2); rd1->Write(1); wr->Write(2); wr_dat->Write({false, 8});
  System::Run(1);
  INFO("rd0={}, rd1={}", regs->out_rd0->Read(), regs->out_rd1->Read());
}