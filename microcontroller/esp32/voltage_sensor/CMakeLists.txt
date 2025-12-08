# The minimum cmake version (usually 3.5 or 3.16)
cmake_minimum_required(VERSION 3.16)

# Include the standard ESP-IDF build rules
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Name your project (Changes the output file name, e.g., voltage_sensor.bin)
project(voltage_sensor)
