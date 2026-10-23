add_executable(gig_validator_benchmark validator_benchmark.cpp validator_batch.cpp)
target_link_libraries(gig_validator_benchmark PRIVATE gig::microstructure)
target_include_directories(gig_validator_benchmark PRIVATE ${PROJECT_SOURCE_DIR})
# A separately compiled batch prevents interprocedural folding of repeated work.
set_target_properties(gig_validator_benchmark PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
gig_project_target(gig_validator_benchmark)
if(BUILD_TESTING)
  add_test(NAME benchmark.correctness COMMAND gig_validator_benchmark 1024 2 1 2 42)
  set_tests_properties(benchmark.correctness PROPERTIES PASS_REGULAR_EXPRESSION "validated_add_order_payload_only")
  foreach(bad_input 0 bad)
    add_test(NAME benchmark.reject_${bad_input} COMMAND ${CMAKE_COMMAND}
      -DPROGRAM=$<TARGET_FILE:gig_validator_benchmark>
      "-DARGUMENTS=${bad_input};2;1;2;42" "-DEXPECTED=argument out of range"
      -P ${PROJECT_SOURCE_DIR}/cmake/ExpectFailure.cmake)
  endforeach()
endif()

add_executable(gig_book_benchmark book_benchmark.cpp copy_probe.cpp)
target_link_libraries(gig_book_benchmark PRIVATE gig::microstructure)
target_include_directories(gig_book_benchmark PRIVATE ${PROJECT_SOURCE_DIR})
set_target_properties(gig_book_benchmark PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
gig_project_target(gig_book_benchmark)
if(BUILD_TESTING)
  add_test(NAME benchmark.book_smoke COMMAND ${Python3_EXECUTABLE}
    ${PROJECT_SOURCE_DIR}/scripts/check_book_benchmark.py $<TARGET_FILE:gig_book_benchmark>)
endif()

add_executable(gig_research_benchmark research_benchmark.cpp)
target_link_libraries(gig_research_benchmark PRIVATE gig::microstructure)
target_include_directories(gig_research_benchmark PRIVATE ${PROJECT_SOURCE_DIR})
gig_project_target(gig_research_benchmark)

add_executable(gig_flow_benchmark flow_benchmark.cpp)
target_link_libraries(gig_flow_benchmark PRIVATE gig::microstructure)
target_include_directories(gig_flow_benchmark PRIVATE ${PROJECT_SOURCE_DIR})
gig_project_target(gig_flow_benchmark)

add_executable(gig_simulation_benchmark simulation_benchmark.cpp)
target_link_libraries(gig_simulation_benchmark PRIVATE gig::microstructure)
target_include_directories(gig_simulation_benchmark PRIVATE ${PROJECT_SOURCE_DIR})
gig_project_target(gig_simulation_benchmark)

add_executable(gig_execution_benchmark execution_benchmark.cpp)
target_link_libraries(gig_execution_benchmark PRIVATE gig::microstructure)
target_include_directories(gig_execution_benchmark PRIVATE ${PROJECT_SOURCE_DIR})
gig_project_target(gig_execution_benchmark)

add_executable(gig_itch_benchmark itch_benchmark.cpp)
target_link_libraries(gig_itch_benchmark PRIVATE gig::itch)
set_target_properties(gig_itch_benchmark PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
gig_project_target(gig_itch_benchmark)
if(BUILD_TESTING)
  add_test(NAME itch.benchmark_correctness COMMAND ${Python3_EXECUTABLE}
    ${PROJECT_SOURCE_DIR}/scripts/check_itch_benchmark.py $<TARGET_FILE:gig_itch_benchmark>)
endif()

add_executable(gig_itch_context_benchmark itch_context_benchmark.cpp)
target_link_libraries(gig_itch_context_benchmark PRIVATE gig::itch_context)
set_target_properties(gig_itch_context_benchmark PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
gig_project_target(gig_itch_context_benchmark)
if(BUILD_TESTING)
  add_test(NAME itch.context_benchmark_correctness COMMAND ${Python3_EXECUTABLE}
    ${PROJECT_SOURCE_DIR}/scripts/check_itch_context_benchmark.py $<TARGET_FILE:gig_itch_context_benchmark>)
endif()

add_executable(gig_itch_reconstruction_benchmark itch_reconstruction_benchmark.cpp)
target_link_libraries(gig_itch_reconstruction_benchmark PRIVATE gig::itch_reconstruction)
set_target_properties(gig_itch_reconstruction_benchmark PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
gig_project_target(gig_itch_reconstruction_benchmark)
if(BUILD_TESTING)
  add_test(NAME itch.reconstruction_benchmark_correctness COMMAND ${Python3_EXECUTABLE}
    ${PROJECT_SOURCE_DIR}/scripts/check_itch_reconstruction_benchmark.py $<TARGET_FILE:gig_itch_reconstruction_benchmark>)
endif()

if(GIG_BUILD_ITCH_STREAMING)
  add_executable(gig_itch_streaming_benchmark itch_streaming_benchmark.cpp)
  target_link_libraries(gig_itch_streaming_benchmark PRIVATE gig::itch_streaming)
  set_target_properties(gig_itch_streaming_benchmark PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
  gig_project_target(gig_itch_streaming_benchmark)
  if(BUILD_TESTING)
    add_test(NAME itch.streaming_benchmark_correctness COMMAND ${Python3_EXECUTABLE}
      ${PROJECT_SOURCE_DIR}/scripts/check_itch_streaming_benchmark.py $<TARGET_FILE:gig_itch_streaming_benchmark>)
  endif()
endif()
