cmake_minimum_required(VERSION 3.16)
project(lsh)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")

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

set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "lsh.exe")