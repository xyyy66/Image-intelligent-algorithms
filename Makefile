CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic
SRC = src/main.cpp src/img.cpp src/rop.cpp src/metrics.cpp
BIN = build/rop_demo

all: $(BIN)

$(BIN): $(SRC)
	@mkdir -p build
	$(CXX) $(CXXFLAGS) $(SRC) -o $(BIN)

clean:
	rm -rf build

.PHONY: all clean
