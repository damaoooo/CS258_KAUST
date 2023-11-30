#include <cstdint>
#include <memory>

#include "base.hpp"

using namespace proj;

class TestInnerDevice : public Device {
 public:
  TestInnerDevice(int64_t val) {
    out = std::make_shared<Latch<int64_t>>();
    RegisterDevice({out});
    out->Write(val);
  }

  std::shared_ptr<Latch<int64_t>> out;
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

int main() {
  auto dev = std::make_shared<TestDevice>();
  // INFO("out={}", dev->dev_a->out->Read());
  dev->OnRecvClock();
  INFO("out={}", dev->dev_a->out->Read());
  INFO("out={}", dev->dev_b->out->Read());
  dev->OnRecvClock();
  INFO("out={}", dev->dev_a->out->Read());
  INFO("out={}", dev->dev_b->out->Read());
  dev->dev_a->out->Write(7);
  INFO("out={}", dev->dev_a->out->Read());
  dev->OnRecvClock();
  INFO("out={}", dev->dev_a->out->Read());
  return 0;
}