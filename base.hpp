#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <type_traits>
#include <vector>

namespace proj {

class Device {
 public:
  Device() : clock(0) {}
  
  Device(const Device&) = delete;
  Device(Device&&) = delete;
  Device& operator=(const Device&) = delete;
  Device& operator=(Device&&) = delete;

  virtual void DoFunction() {
    for (const auto& dev : attach_devs_) {
      dev->DoFunction();
    }
  }

  virtual void OnRecvClock() {
    for (const auto& dev : attach_devs_) {
      dev->OnRecvClock();
    }
    clock += 1;
  }
  
  void RegisterDevice(std::vector<std::shared_ptr<Device>>&& devs) {
    for (auto& e : devs) {
      attach_devs_.push_back(e);
    }
  }

 public:
  std::vector<std::shared_ptr<Device>> attach_devs_;
  int64_t clock;
};

class System : public Device {
 public:

  System() : Device(), stop(false) {}

  static void Register(std::vector<std::shared_ptr<Device>>&& devs) {
    Get_().RegisterDevice(std::move(devs));
  } 

  static void Run(int64_t n_clocks) {
    for (auto i = 0ll; i < n_clocks; i++) {
      Get_().DoFunction();
      Get_().OnRecvClock();
    }
  }

  static void Reset() {
    auto& sys = Get_();
    sys.attach_devs_.clear();
    sys.clock = 0;
    sys.stop = false;
  }

  static int64_t GetClock() {
    return Get_().clock;
  }

  static void Stop() {
    Get_().stop = true;
  }
  
  static bool IsStopped() {
    return Get_().stop;
  }
  

 private:
  static System& Get_() {
    static System sys{};
    return sys;
  }

  bool stop;
};

template <typename Type>
struct Optional {
  bool is_valid = false;
  Type val = {};
};

template <typename Type>
class Input : public Device {
 public:

  virtual Type Read() = 0;
};

template <typename Type>
class Reg : public Input<Type> {
 public:

  Reg(Type init_val) :
      Input<Type>(), next_val_(init_val), cur_val_(init_val) {}
  
  void OnRecvClock() override {
    Device::OnRecvClock();
    cur_val_ = next_val_;
  }

  void Write(Type val) {
    next_val_ = val;
  }

  Type Read() override {
    return cur_val_;
  }

 public:
  Type next_val_;
  Type cur_val_;
};

template <typename Type>
class Wire : public Input<Type> {
 public:

  Wire(std::function<Type()> do_func) :
      Input<Type>(), do_function_(do_func) {}

  Type Read() override {
    return do_function_();
  }

 private:
  const std::function<Type()> do_function_;
};

template <typename Type>
using InputPtr = std::shared_ptr<Input<Type>>;

template <typename Type>
using RegPtr = std::shared_ptr<Reg<Type>>;

template <typename Type>
using WirePtr = std::shared_ptr<Wire<Type>>;

template <typename Type>
static RegPtr<Type> MakeReg(Type init_val) {
  return std::make_shared<Reg<Type>>(init_val);
}

template <typename Type>
static WirePtr<Type> MakeWire(std::function<Type()> do_func) {
  return std::make_shared<Wire<Type>>(do_func);
}

template <typename Enum>
auto AsInt(const Enum value) {
  return static_cast<typename std::underlying_type<Enum>::type>(value);
}

}