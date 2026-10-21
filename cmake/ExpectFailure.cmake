# Negative tests must fail for the intended reason, not a sanitizer/runtime crash.
execute_process(COMMAND "${PROGRAM}" ${ARGUMENTS}
  RESULT_VARIABLE result OUTPUT_VARIABLE output ERROR_VARIABLE error)
if(NOT "${result}" STREQUAL "1")
  message(FATAL_ERROR "Expected exit 1; got ${result}: ${output}${error}")
endif()
string(FIND "${error}" "${EXPECTED}" found)
if(found EQUAL -1 OR error MATCHES "Sanitizer|runtime error:")
  message(FATAL_ERROR "Unexpected failure diagnostic: ${error}")
endif()
message(STATUS "Verified expected exit 1: ${EXPECTED}")
