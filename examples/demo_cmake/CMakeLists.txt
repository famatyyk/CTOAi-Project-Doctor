cmake_minimum_required(VERSION 3.10)
project(MyApp)

set(CMAKE_CXX_STANDARD 17)
include_directories(include)

add_executable(app main.cpp utils.cpp)
add_compile_options(-O3)

# brak target_link_libraries, brak find_package, brak CMAKE_BUILD_TYPE
