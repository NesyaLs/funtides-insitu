# Check for conflicting options
if(USE_KOKKOS AND USE_VECTOR)
    message(FATAL_ERROR "Both Vector and Kokkos array implementations selected. Please only select one.")
endif()

# Set default if neither is selected
if(NOT USE_KOKKOS AND NOT USE_VECTOR)
    message(WARNING "No array implementation selected. Kokkos implementation chosen as default.")
    set(USE_KOKKOS TRUE CACHE BOOL "Use KOKKOS to parallelise loops" FORCE)
endif()
