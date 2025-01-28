# Compiler and flags
CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -pedantic

# Targets
TARGETS := cross_core_test cross_core_bench

# Source files
SRCS := cross_core_test.cpp cross_core_bench.cpp

# Default target
all: $(TARGETS)

# Build each target from its corresponding source file
cross_core_test: cross_core_test.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

cross_core_bench: cross_core_bench.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

# Clean target
clean:
	rm -f $(TARGETS)

# Phony targets
.PHONY: all clean

