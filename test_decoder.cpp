#include "base.hpp"
#include "decoder.hpp"
#include <cstdint>
#include <memory>

using namespace proj;

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
  TestBitfield();
  return 0;
}