import pySmartGadget

def main():
    bleAddress = 'C3:77:1E:95:8E:E3'
    print('connecting to:', bleAddress)
    gadget = pySmartGadget.SHT31(bleAddress)
    print('connected')

    print('name: ', gadget.readDeviceName())
    print('Battery: ', gadget.readBattery())
    print('temperature:', gadget.readTemperature())
    print('Humidity: ', gadget.readHumidity())
#     gadget.setLoggerIntervalMs(1000)
    print('LoggerInterval: ', gadget.readLoggerIntervalMs())
    gadget.setSyncTimeMs()
    print('OldestTimestampMs: ', gadget.readOldestTimestampMs())
    print('NewestTimeStampMs: ', gadget.readNewestTimestampMs())
    
    gadget.readLoggedDataInterval()
#     gadget.setTemperatureNotification(True)
#     gadget.setHumidityNotification(True)
           
    try:
        while 1:
            if False is gadget.waitForNotifications(5) or False is gadget.isLogReadoutInProgress():
                print('Done')
                break
            print('readingData')
    finally:
        gadget.disconnect()
        print('disconnected')
 

if __name__ == "__main__":
    main()
