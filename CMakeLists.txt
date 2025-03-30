cmake_minimum_required(VERSION 3.10)
project(subscription CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define output directory for plugins and executable
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/plugins)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/src/include
    /opt/homebrew/Cellar/nlohmann-json/3.11.3/include
    /opt/homebrew/Cellar/cpr/1.11.2/include
    /opt/homebrew/Cellar/opencv/4.11.0_1/include/opencv4
)

# Find required packages
find_package(nlohmann_json 3.11.3 REQUIRED)
find_package(cpr REQUIRED)
find_package(OpenCV 4.11.0 REQUIRED) # Add OpenCV package

# Source files for main executable
file(GLOB MAIN_SOURCES
    "${CMAKE_SOURCE_DIR}/src/*.cpp"
)

add_executable(${PROJECT_NAME} ${MAIN_SOURCES})

# Link libraries to main executable
target_link_libraries(${PROJECT_NAME} PRIVATE
    nlohmann_json::nlohmann_json
    cpr::cpr
    ${OpenCV_LIBS} # Link OpenCV libraries 
    "-ldl" # Link dynamic loading library for dlopen/dlsym on Unix
)

# Compile plugins
file(GLOB PLUGIN_SOURCES "${CMAKE_SOURCE_DIR}/plugins_src/*.cpp")
set(PLUGIN_TARGETS "") # Create empty list for plugin target names

foreach(PLUGIN_SOURCE ${PLUGIN_SOURCES})
    get_filename_component(PLUGIN_NAME ${PLUGIN_SOURCE} NAME_WE)

    add_library(${PLUGIN_NAME} SHARED ${PLUGIN_SOURCE})

    set_target_properties(${PLUGIN_NAME} PROPERTIES
        PREFIX "lib" # Adds "lib" prefix on Unix-like systems
        SUFFIX ".dylib" # Forces .dylib extension on macOS
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/plugins # Ensure output is in project/plugins
    )

    # Link libraries to plugins
    target_link_libraries(${PLUGIN_NAME} PRIVATE
        nlohmann_json::nlohmann_json
        ${OpenCV_LIBS} # Link OpenCV libraries to plugins
        "-lc++" # Link libc++ (macOS C++ standard library)
    )

    # Add plugin name to the list of targets
    list(APPEND PLUGIN_TARGETS ${PLUGIN_NAME})
endforeach()

# Use plugin target names as dependencies
add_dependencies(${PROJECT_NAME} ${PLUGIN_TARGETS})

set_target_properties(${PROJECT_NAME} PROPERTIES
    INSTALL_RPATH "${CMAKE_SOURCE_DIR}/plugins"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/plugins"
)

# Apple-specific settings
if(APPLE)
    # Ensure -stdlib=libc++ is passed to both compiler and linker
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -stdlib=libc++")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -stdlib=libc++")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -stdlib=libc++")
endif()

# Optional: Print OpenCV configuration for debugging
message(STATUS "OpenCV library status:")
message(STATUS "    version: ${OpenCV_VERSION}")
message(STATUS "    libraries: ${OpenCV_LIBS}")
message(STATUS "    include path: ${OpenCV_INCLUDE_DIRS}")
