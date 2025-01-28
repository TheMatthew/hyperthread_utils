# Compiler and flags
CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -pedantic

# Target executable
TARGET := cross_core_test

# Source file
SRC := cross_core_test.cpp

# Default target
all: $(TARGET)

# Build target
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

# Clean target
clean:
	rm -f $(TARGET)

# Phony targets
.PHONY: all clean

