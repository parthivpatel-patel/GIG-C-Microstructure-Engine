add_executable(gig_validator_benchmark validator_benchmark.cpp validator_batch.cpp)
target_link_libraries(gig_validator_benchmark PRIVATE gig::microstructure)
# A separately compiled batch prevents interprocedural folding of repeated work.
set_target_properties(gig_validator_benchmark PROPERTIES INTERPROCEDURAL_OPTIMIZATION FALSE)
gig_project_target(gig_validator_benchmark)
if(BUILD_TESTING)
  add_test(NAME benchmark.correctness COMMAND gig_validator_benchmark 1024 2 1 2 42)
  set_tests_properties(benchmark.correctness PROPERTIES PASS_REGULAR_EXPRESSION "validated_scaffold_only")
  foreach(bad_input 0 bad)
    add_test(NAME benchmark.reject_${bad_input} COMMAND ${CMAKE_COMMAND}
      -DPROGRAM=$<TARGET_FILE:gig_validator_benchmark>
      "-DARGUMENTS=${bad_input};2;1;2;42" "-DEXPECTED=argument out of range"
      -P ${PROJECT_SOURCE_DIR}/cmake/ExpectFailure.cmake)
  endforeach()
endif()
