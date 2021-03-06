cmake_minimum_required(VERSION 3.8)

project(cci)

set(LIBRARY_VERSION_MAJOR 1 CACHE STRING "major version" FORCE)
set(LIBRARY_VERSION_MINOR 0 CACHE STRING "minor version" FORCE)
set(LIBRARY_VERSION_PATCH 0 CACHE STRING "minor version" FORCE)
set(LIBRARY_VERSION ${LIBRARY_VERSION_MAJOR}.${LIBRARY_VERSION_MINOR}.${LIBRARY_VERSION_PATCH} CACHE STRING "version" FORCE)

set(LIBRARY_NAME cciapi)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

if(DEFINED ENV{SYSTEMC_HOME})
    set(SYSTEMC_ROOT $ENV{SYSTEMC_HOME})
else()
    message(ERROR "SYSTEMC_HOME environment variable not defined")
endif()

if(DEFINED ENV{RAPIDJSON_HOME})
    set(RAPIDJSON $ENV{RAPIDJSON_HOME})
else()
	set(RAPIDJSON ${CMAKE_CURRENT_SOURCE_DIR}/packages/rapidjson)
endif()

if(EXISTS "${SYSTEMC_ROOT}/lib/")
	set(SYSTEMC_LIBDIR ${SYSTEMC_ROOT}/lib)
elseif(EXISTS "${SYSTEMC_ROOT}/lib-linux/")
	set(SYSTEMC_LIBDIR ${SYSTEMC_ROOT}/lib-linux)
elseif(EXISTS "${SYSTEMC_ROOT}/lib-linux64/")
	set(SYSTEMC_LIBDIR ${SYSTEMC_ROOT}/lib-linux64)
endif()

FILE(GLOB CFG_HEADER_FILES src/cci_cfg/*.h )
FILE(GLOB CORE_HEADER_FILES src/cci_core/*.h )
FILE(GLOB UTILS_HEADER_FILES src/cci_utils/*.h )
set(SOURCES
	src/cci_cfg/cci_broker_handle.cpp
	src/cci_cfg/cci_broker_manager.cpp
	src/cci_cfg/cci_originator.cpp
	src/cci_cfg/cci_param_if.cpp
	src/cci_cfg/cci_param_untyped.cpp
	src/cci_cfg/cci_param_untyped_handle.cpp
	src/cci_cfg/cci_report_handler.cpp
	src/cci_core/cci_name_gen.cpp
	src/cci_core/cci_value_converter.cpp
	src/cci_core/cci_value.cpp
	src/cci_utils/broker.cpp
	src/cci_utils/consuming_broker.cpp
)

link_directories(${SYSTEMC_LIBDIR})
add_library(${LIBRARY_NAME} ${SOURCES})	

target_include_directories(${LIBRARY_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_include_directories(${LIBRARY_NAME} PRIVATE ${SYSTEMC_ROOT}/include)
target_include_directories(${LIBRARY_NAME} PUBLIC ${RAPIDJSON}/include)

target_link_libraries(${LIBRARY_NAME} systemc)

install(TARGETS ${LIBRARY_NAME}
  EXPORT ${PROJECT_NAME}Targets            # for downstream dependencies
  ARCHIVE DESTINATION lib COMPONENT libs   # static lib
  LIBRARY DESTINATION lib COMPONENT libs   # shared lib
  FRAMEWORK DESTINATION bin COMPONENT libs # for mac
  PUBLIC_HEADER DESTINATION include COMPONENT devel   # headers for mac (note the different component -> different package)
  INCLUDES DESTINATION include             # headers
  PUBLIC_HEADER DESTINATION include
)

install(FILES src/cci_configuration DESTINATION include)
install(FILES ${CFG_HEADER_FILES} DESTINATION include/cci_cfg)
install(FILES ${CORE_HEADER_FILES} DESTINATION include/cci_core)
install(FILES ${UTILS_HEADER_FILES} DESTINATION include/cci_utils)


