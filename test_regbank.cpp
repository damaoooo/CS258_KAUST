#include "base.hpp"
#include "regbank.hpp"
#include <cstdint>
#include <memory>
#include <vector>

using namespace proj;

int main() {
  auto rid = MakeReg<Regs>({0, 0, 0});
  auto wr_dat = MakeReg<Optional<uint64_t>>({false, 0});

  auto regs = std::make_shared<RegBank>();
  regs->Connect(rid, wr_dat);
  System::Register({rid, wr_dat, regs});

  auto rdat = regs->out_reg_dat->Read(); INFO("rd={}, rs={}, rt={}", rdat.rd, rdat.rs, rdat.rt);

  System::Run(1);
  rdat = regs->out_reg_dat->Read(); INFO("rd={}, rs={}, rt={}", rdat.rd, rdat.rs, rdat.rt);

  rid->Write({1, 1, 2}); wr_dat->Write({true, 5});
  System::Run(1);
  rdat = regs->out_reg_dat->Read(); INFO("rd={}, rs={}, rt={}", rdat.rd, rdat.rs, rdat.rt);

  rid->Write({2, 1, 2}); wr_dat->Write({true, 6});
  System::Run(1);
  rdat = regs->out_reg_dat->Read(); INFO("rd={}, rs={}, rt={}", rdat.rd, rdat.rs, rdat.rt);

  rid->Write({1, 1, 2}); wr_dat->Write({false, 7});
  System::Run(1);
  rdat = regs->out_reg_dat->Read(); INFO("rd={}, rs={}, rt={}", rdat.rd, rdat.rs, rdat.rt);

  rid->Write({2, 1, 2}); wr_dat->Write({false, 8});
  System::Run(1);
  rdat = regs->out_reg_dat->Read(); INFO("rd={}, rs={}, rt={}", rdat.rd, rdat.rs, rdat.rt);
}