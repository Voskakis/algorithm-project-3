cmake_minimum_required(VERSION 3.16)
project(lsh)

set(CMAKE_CXX_STANDARD 14)

include_directories(modules)

add_executable(lsh
    modules/CosineHashing.cpp
    modules/CosineHashing.h
    modules/EuclidianHashing.cpp
    modules/EuclidianHashing.h
    modules/globals.cpp
    modules/lsh_interface.cpp
    modules/lsh_interface.h
    modules/modulo_func.cpp
    modules/modulo_func.h
    modules/randomness.cpp
    modules/randomness.h
    modules/UserInputHandling.cpp
    modules/UserInputHandling.h
    lsh.cpp)
