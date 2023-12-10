#include "base.hpp"
#include "fetcher.hpp"
#include "mux.hpp"
#include <cstdint>
#include <memory>
#include <vector>

using namespace proj;

#define Show(fetcher) \
  INFO("valid={}, addr={}, instr={}, itcm_in_addr={}, itcm_out={}", \
    fetcher->out_instr_addr->Read().is_valid, \
    fetcher->out_instr_addr->Read().val, \
    fetcher->out_instr->Read(), \
    fetcher->itcm->in_param->Read().addr, \
    fetcher->itcm->out_dat->Read() \
  );

int main() {
  auto fu_en = MakeReg<bool>(false);
  auto pc_val = MakeReg<Optional<uint64_t>>({false, 0});
  auto fetcher = std::make_shared<Fetcher>(fu_en, pc_val);
  fetcher->Load({
    (2ull << 32) + 1ull,
    (4ull << 32) + 3ull,
    (6ull << 32) + 5ull});
  
  System::Register({fu_en, pc_val, fetcher});

  Show(fetcher);

  System::Run(1);
  Show(fetcher);

  fu_en->Write(true);
  System::Run(1);
  Show(fetcher);

  System::Run(1);
  Show(fetcher);

  System::Run(1);
  Show(fetcher);

  System::Run(1);
  Show(fetcher);

  System::Run(1);
  Show(fetcher);

  pc_val->Write({true, 0});
  System::Run(1);
  Show(fetcher);

  pc_val->Write({false, 0});
  System::Run(1);
  Show(fetcher);

  pc_val->Write({false, 0});
  System::Run(1);
  Show(fetcher);

  pc_val->Write({true, 0});
  System::Run(1);
  Show(fetcher);

  pc_val->Write({false, 0});
  System::Run(1);
  Show(fetcher);

  pc_val->Write({false, 0});
  System::Run(1);
  Show(fetcher);

  return 0; 
}