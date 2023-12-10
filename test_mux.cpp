#include "base.hpp"
#include "mux.hpp"
#include <cstdint>
#include <memory>
#include <vector>

using namespace proj;

int main() {
  auto in1 = MakeWire<int64_t>([&](){
    return 1;
  });
  auto in2 = MakeWire<int64_t>([&](){
    return 2;
  });
  auto sel = MakeReg<uint64_t>(0);
  auto mux = std::make_shared<Mux<int64_t>>(std::vector<InputPtr<int64_t>>{in1, in2}, sel);
  System::Register({sel, mux});

  INFO("out={}", mux->out->Read());
  System::Run(1);

  INFO("out={}", mux->out->Read());
  System::Run(1);

  INFO("out={}", mux->out->Read());
  sel->Write(1);
  System::Run(1);

  INFO("out={}", mux->out->Read());
  System::Run(1);

  INFO("out={}", mux->out->Read());
}