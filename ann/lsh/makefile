CC = g++
modules = modules/UserInputHandling.cpp modules/EuclidianHashing.cpp modules/modulo_func.cpp modules/randomness.cpp modules/CosineHashing.cpp
TARGET = lsh
CXXFLAGS = -g -O0 -Wall -Wextra

lsh:
	$(CC) $(CXXFLAGS) lsh.cpp $(modules) -o $(TARGET)

clean:
	rm -rf $(TARGET)
