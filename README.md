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
- control notifications
    - temperature
    - humidity

# Usage

Take a look at the main.py example file. For scanning of BLE devices take a look [here](https://ianharvey.github.io/bluepy-doc/scanner.html#sample-code "Documentation of bluepy scanner class").



# Additional information

[Sensirion Homepage - SHT31 Smart Gadget Development Kit](https://www.sensirion.com/de/umweltsensoren/feuchtesensoren/development-kit/)

[Github of Sensirion](https://github.com/Sensirion "Github of Sensirion")

