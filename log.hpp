#pragma once
#include <cstdint>
#include <iostream>
#include <sstream>
#include <mutex>
#include <sys/time.h>

namespace omni {

namespace Log {

enum class ParserState {
  kNormal,
  kCapture
};

inline void FormatElem(std::stringstream& ss, std::string_view fmt) {
  ss << fmt;
}

template<typename First, typename... Rest>
void FormatElem(std::stringstream& ss, std::string_view fmt, First& first, Rest&&... rest);

template<typename First, typename... Rest>
void FormatElem(std::stringstream& ss, std::string_view fmt, First&& first, Rest&&... rest);

template<typename First, typename... Rest>
void FormatElem(std::stringstream& ss, std::string_view fmt, First& first, Rest&&... rest) {
  static thread_local char cap_buf[1024];
  static thread_local char str_buf[1024];

  ParserState stat = ParserState::kNormal;
  size_t buf_idx = 0;
  for (size_t i = 0; i < fmt.size(); ++i) {
    switch (stat) {
    case ParserState::kNormal: {
      if (fmt[i] == '{') {
        stat = ParserState::kCapture;
      } else {
        ss << fmt[i];
      }
      break;
    }
    case ParserState::kCapture: {
      if (fmt[i] == '}') {
        stat = ParserState::kNormal;
        cap_buf[buf_idx++] = '\0';
        if (buf_idx == 1) {
          ss << first;
          FormatElem(ss, fmt.substr(i + 1), std::forward<Rest>(rest)...);
          return;
        } else if (cap_buf[0] == '%') {
          snprintf(str_buf, 1024, cap_buf, first);
          ss << str_buf;
          FormatElem(ss, fmt.substr(i + 1), std::forward<Rest>(rest)...);
          return;
        } else {
          ss << cap_buf;
          buf_idx = 0;
          break;
        }
      } else {
        cap_buf[buf_idx++] = fmt[i]; 
      }
    }
    }
  }
}

template<typename First, typename... Rest>
void FormatElem(std::stringstream& ss, std::string_view fmt, First&& first, Rest&&... rest) {
  FormatElem(ss, fmt, first, std::forward<Rest>(rest)...);
}

template<typename... Args>
std::string Format(std::string_view fmt, Args&&... args) {
  std::stringstream ss;
  FormatElem(ss, fmt, std::forward<Args>(args)...);
  return ss.str();
}

template<typename... Args>
void Print(std::string_view fmt, Args&&... args) {
  std::cout << Format(fmt, std::forward<Args>(args)...);
}

template<typename... Args>
void Log(std::string_view log_level, std::string_view file, std::string_view func, int line, std::string_view fmt, Args&&... args) {
  static std::mutex mutex;
  auto msg = Format(fmt, std::forward<Args>(args)...);
  
  timeval cur_time;
  gettimeofday(&cur_time, NULL);
  auto current_time = cur_time.tv_sec * 1000000ll + cur_time.tv_usec;
  static auto start_time = current_time;
  auto elapsed_time = current_time - start_time;
  auto elapsed_time_sec = elapsed_time / 1000000ll;
  auto elapsed_time_msec = elapsed_time / 1000ll % 1000ll;
  auto elapsed_time_usec = elapsed_time % 1000ll;

  std::string bg_color;
  if (log_level == "FATAL") {
    bg_color = "\033[101m";
  } else if (log_level == "WARN") {
    bg_color = "\033[105m";
  } else {
    bg_color = "\033[49m";
  }

  auto full_msg = Format("{}{%3d}.{%03d}.{%03d} - [\033[34m{}\033[39m]({}:{})(\033[33m::{}\033[39m) {}\033[49m\n",
    bg_color, elapsed_time_sec, elapsed_time_msec, elapsed_time_usec, log_level, file, line, func, msg);

  mutex.lock();
  std::cout << full_msg;
  if (log_level == "FATAL") {
    abort();
    while (1) {}
  }
  mutex.unlock();

  // if (log_level == "FATAL") {
  //   // wait for other threads
  //   sleep(3);
  //   exit(EXIT_FAILURE);
  // }
}

#define OMNI_LOG_LEVEL_TRACE 0
#define OMNI_LOG_LEVEL_DEBUG 1
#define OMNI_LOG_LEVEL_INFO 2
#define OMNI_LOG_LEVEL_WARN 3
#define OMNI_LOG_LEVEL_FATAL 4

#ifndef OMNI_LOG_LEVEL
#define OMNI_LOG_LEVEL OMNI_LOG_LEVEL_INFO
#endif

#if OMNI_LOG_LEVEL <= OMNI_LOG_LEVEL_TRACE
#define TRACE(...) omni::Log::Log("TRACE", __FILE__, __func__, __LINE__, __VA_ARGS__)
#else
#define TRACE(...) (void)0
#endif

#if OMNI_LOG_LEVEL <= OMNI_LOG_LEVEL_DEBUG
#define DEBUG(...) omni::Log::Log("DEBUG", __FILE__, __func__, __LINE__, __VA_ARGS__)
#else
#define DEBUG(...) (void)0
#endif

#if OMNI_LOG_LEVEL <= OMNI_LOG_LEVEL_INFO
#define INFO(...) omni::Log::Log("INFO", __FILE__, __func__, __LINE__, __VA_ARGS__)
#else
#define INFO(...) (void)0
#endif

#if OMNI_LOG_LEVEL <= OMNI_LOG_LEVEL_WARN
#define WARN(...) omni::Log::Log("WARN", __FILE__, __func__, __LINE__, __VA_ARGS__)
#else
#define WARN(...) (void)0
#endif

#define FATAL(...) omni::Log::Log("FATAL", __FILE__, __func__, __LINE__, __VA_ARGS__)

#define CHECK(cond, ...) if (!(cond)) { FATAL(__VA_ARGS__); }

}

} // namespace omni