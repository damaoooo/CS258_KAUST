#pragma once

#include <initializer_list>
#include <memory>
#include <optional>
#include <type_traits>
#include <vector>

#include "log.hpp"

namespace proj {

class Device {
 public:
  virtual void OnRecvClock() {
    for (const auto& dev : attach_devs_) {
      dev->OnRecvClock();
    }
  }

  virtual void DoFunction() {
    for (const auto& dev : attach_devs_) {
      dev->DoFunction();
    }
  }
  
  void RegisterDevice(std::initializer_list<std::shared_ptr<Device>> devs) {
    for (const auto& dev : devs) {
      attach_devs_.push_back(dev);
    }
  }

 private:
  std::vector<std::shared_ptr<Device>> attach_devs_;
};

template <typename Type>
class Latch : public Device {
 public:
  static_assert(std::is_pod<Type>::value, "Value type of Latch must be POD.");

  void OnRecvClock() override {
    Device::OnRecvClock();
    cur_val_ = next_val_;
  }

  void DoFunction() override {
    Device::DoFunction();
  }

  void Write(const Type& val) {
    next_val_ = val;
  }

  Type Read() {
    if (!cur_val_.has_value()) {
      WARN("reading an indeterminate value.");
    }
    return cur_val_.value();
  }

 private:
  std::optional<Type> next_val_;
  std::optional<Type> cur_val_;
};

}