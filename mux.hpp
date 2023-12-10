#pragma once

#include "base.hpp"
#include "log.hpp"
#include <cstdint>
#include <vector>

namespace proj {

template <typename Type>
class Mux : public Device {
 public:
  Mux(std::vector<InputPtr<Type>>&& ports, InputPtr<uint64_t> sel) :
      Device(), in_ports(ports), in_sel(sel) {
    out = MakeWire<Type>([&](){
      CHECK(in_sel->Read() < in_ports.size(), "");
      return in_ports[in_sel->Read()]->Read();
    });
  }
 
 WirePtr<Type> out;

 public:
  const std::vector<InputPtr<Type>> in_ports;
  const InputPtr<uint64_t> in_sel;
};
}