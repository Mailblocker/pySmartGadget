import pySmartGadget
from datetime import datetime
import time

def main():
    bleAddress = 'C3:77:1E:95:8E:E3'
    print('Connecting to:', bleAddress)
    gadget = pySmartGadget.SHT31(bleAddress)
    print('Connected')

    print('Device name:', gadget.readDeviceName())

    print('System ID: ', gadget.readSystemId())
    print('Model number string:', gadget.readModelNumberString())
    print('Serial number string:', gadget.readSerialNumberString())
    print('Firmware revision string:', gadget.readFirmwareRevisionString())
    print('Hardware revision string:', gadget.readHardwareRevisionString())
    print('Software revision string:', gadget.readSoftwareRevisionString())
    print('Manufacturer name string:', gadget.readManufacturerNameString())
    
    print('Battery level [%]:', gadget.readBattery())
    print('Temperature [°C]:', '{:.2f}'.format(gadget.readTemperature()))
    print('Humidity [%]:', '{:.2f}'.format(gadget.readHumidity()))
    gadget.setLoggerIntervalMs(1000 * 60) # setting a new logger interval will clear all the logged data on the device
    print('LoggerInterval [ms]: ', gadget.readLoggerIntervalMs())
    gadget.setSyncTimeMs()
    time.sleep(0.1) # Sleep a bit to enable the gadget to set the SyncTime; otherwise 0 is read when readNewestTimestampMs is used
    print('OldestTimestampMs [µs]:', gadget.readOldestTimestampMs(), datetime.utcfromtimestamp(gadget.readOldestTimestampMs()/1000).strftime('%Y-%m-%d %H:%M:%S'))
    print('NewestTimeStampMs [µs]:', gadget.readNewestTimestampMs(), datetime.utcfromtimestamp(gadget.readNewestTimestampMs()/1000).strftime('%Y-%m-%d %H:%M:%S'))
    
    gadget.readLoggedDataInterval()
#     gadget.setTemperatureNotification(True) # enable notifications for humidity values; the object will log incoming data into the loggedData variable
    gadget.setHumidityNotification(True) # enable notifications for humidity values; the object will log incoming data into the loggedData variable 
           
    try:
        while True:
            if False is gadget.waitForNotifications(5) or False is gadget.isLogReadoutInProgress():
                print('Done reading data')
                break
            print('Read dataset')
    finally:
        print(gadget.loggedDataReadout) # contains the data logged by the smartgadget
        print(gadget.loggedData) # contains the data sent via notifications
        gadget.disconnect()
        print('Disconnected')

if __name__ == "__main__":
    main()
