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
