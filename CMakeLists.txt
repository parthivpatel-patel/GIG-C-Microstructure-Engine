cmake_minimum_required(VERSION 3.20)
project(gig_microstructure VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(gig_microstructure INTERFACE)
target_include_directories(gig_microstructure INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
if(MSVC)
  target_compile_options(gig_microstructure INTERFACE /W4 /permissive-)
else()
  target_compile_options(gig_microstructure INTERFACE -Wall -Wextra -Wpedantic)
endif()

add_executable(gig_engine_demo src/main.cpp)
target_link_libraries(gig_engine_demo PRIVATE gig_microstructure)

enable_testing()
add_executable(gig_engine_tests tests/test_types.cpp)
target_link_libraries(gig_engine_tests PRIVATE gig_microstructure)
add_test(NAME gig_engine_tests COMMAND gig_engine_tests)
