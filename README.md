# SmartGadget SHT31

Python interface to Sensirion SmartGadget SHT31 based on bluepy.

This project provides an API to access the functionality of the SmartGadget via BLE.

What's working so far:
  - connecting/disconnecting
  - reading data
    - device name
    - battery status
    - temperature
    - humidity
    - oldest & newest data timestamp
    - logging interval
    - logged data (humidity and temperature)
  - writing data
    - device name
    - synchronization timestamp
    - logger interval
- notifications
    - temperature
    - humidity

# Usage

Take a look at the main.py example file.
