# SmartGadget SHT31

Python interface to Sensirion SmartGadget SHT31 based on bluepy.

This project provides an API to access the functionality of the SmartGadget via BLE.
What's working so far:
  - Connecting
  - Disconnecting
  - Reading
    - Device data: Device name, System ID, Model number, Serial number, Firmware revision, Hardware revision, Software revision, Manufacturer name
    - Battery status
    - Temperature & Humidity (actual values and logged data on device)
    - Oldest & newest timestamp
    - Logging interval
  - Writing
    - Device name
    - Synchronization timestamp
    - Logger interval
- Control notifications
    - Temperature & Humidity

# Usage

Take a look at the main.py example file. For scanning of BLE devices take a look [here](https://ianharvey.github.io/bluepy-doc/scanner.html#sample-code "Documentation of bluepy scanner class").



# Additional information

[Sensirion Homepage - SHT31 Smart Gadget Development Kit](https://www.sensirion.com/de/umweltsensoren/feuchtesensoren/development-kit/)

[Github of Sensirion](https://github.com/Sensirion "Github of Sensirion")

