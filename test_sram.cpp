#include "base.hpp"
#include "sram.hpp"
#include <cstdint>
#include <memory>

using namespace proj;

class Testbed : public Device {
 public:
  Testbed() {
    
    RegisterDevice({param, sram});
  }

  RegPtr<SramParam> param;
  std::shared_ptr<Sram<>> sram;
};

int main() {
  auto param_val = SramParam{0, 0, false};
  auto param = MakeReg<SramParam>(param_val);
  auto sram = std::make_shared<Sram<>>(param);
  sram->Load({1, 2, 3, 4});
  System::Register({param, sram});

  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  param_val.write_dat = {true, 5};
  param->Write(param_val);
  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  param_val.write_dat = {true, 6};
  param->Write(param_val);
  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  param_val.write_dat = {false, 7};
  param->Write(param_val);
  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  param_val.write_dat = {false, 8};
  param->Write(param_val);
  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  param_val.addr = 4;
  param->Write(param_val);
  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  param_val.addr = 8;
  param->Write(param_val);
  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  param_val.addr = 16;
  param->Write(param_val);
  System::Run(1);
  INFO("out={}", sram->out_dat->Read());

  System::Run(1);
  INFO("out={}", sram->out_dat->Read());
}