CXX = g++
CXXFLAGS = -std=c++17 -g -O0 -DOMNI_LOG_LEVEL=OMNI_LOG_LEVEL_DEBUG -Wall -Wextra -pedantic -march=native -mtune=native
SRCS = $(wildcard *.cpp)
HEADERS = $(wildcard *.hpp)
TARGETS = $(SRCS:.cpp=.out)

all: $(TARGETS)

%.out: %.cpp $(HEADERS)
	${CXX} ${CXXFLAGS} -o $@ $<

clean:
	rm -f *.out
