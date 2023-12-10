#pragma once

#include "base.hpp"
#include "log.hpp"
#include <cstdint>
#include <vector>

namespace proj {

template <typename Type>
class Mux : public Device {
 public:
  Mux() : Device() {
    out = MakeWire<Type>([&](){
      CHECK(in_sel->Read() < in_ports.size(), "");
      return in_ports[in_sel->Read()]->Read();
    });
  }

  void Connect(std::vector<InputPtr<Type>>&& ports, InputPtr<uint64_t> sel) {
    in_ports = ports;
    in_sel = sel;
  }
 
  WirePtr<Type> out;

 public:
  std::vector<InputPtr<Type>> in_ports;
  InputPtr<uint64_t> in_sel;
};
}