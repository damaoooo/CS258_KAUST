#include <cstdint>
#include <memory>
#include <vector>

#include "base.hpp"
#include "log.hpp"

using namespace proj;

class TestInnerDevice : public Device {
 public:
  TestInnerDevice(int64_t val) {
    out = MakeReg<int64_t>(val);
    RegisterDevice({out});
  }

  RegPtr<int64_t> out;
};

class TestDevice : public Device {
 public:
  TestDevice() {
    dev_a = std::make_shared<TestInnerDevice>(3);
    dev_b = std::make_shared<TestInnerDevice>(5);
    RegisterDevice({dev_a, dev_b});
  }

  std::shared_ptr<TestInnerDevice> dev_a, dev_b;
};

void TestNestedDevice() {
  auto dev = std::make_shared<TestDevice>();
  System::Register({dev});

  INFO("a={}, b={}", dev->dev_a->out->Read(), dev->dev_b->out->Read());

  System::Run(1);
  INFO("a={}, b={}", dev->dev_a->out->Read(), dev->dev_b->out->Read());
  
  dev->dev_a->out->Write(7);
  INFO("a={}, b={}", dev->dev_a->out->Read(), dev->dev_b->out->Read());

  System::Run(1);
  INFO("a={}, b={}", dev->dev_a->out->Read(), dev->dev_b->out->Read());

  System::Run(1);
  INFO("a={}, b={}", dev->dev_a->out->Read(), dev->dev_b->out->Read());
}

void TestInput() {
  auto reg = MakeReg<uint32_t>(0);
  auto wire = MakeWire<uint32_t>([&](){ return reg->Read(); });
  std::vector<InputPtr<uint32_t>> io = {reg, wire};
  System::Register({reg, wire});

  INFO("reg={}, wire={}", io[0]->Read(), io[1]->Read());
  reg->Write(1);
  INFO("reg={}, wire={}", io[0]->Read(), io[1]->Read());
  System::Run(1);
  INFO("reg={}, wire={}", io[0]->Read(), io[1]->Read());
  System::Run(1);
  INFO("reg={}, wire={}", io[0]->Read(), io[1]->Read());
  reg->Write(5);
  INFO("reg={}, wire={}", io[0]->Read(), io[1]->Read());
  System::Run(1);
  INFO("reg={}, wire={}", io[0]->Read(), io[1]->Read());
}

int main() {
  TestInput();
  return 0;
}