from pySmartGadget import SHT31

def main():
    gadget =  SHT31("DC:82:71:D2:60:AF")
    print('connected')

    print('name: ', gadget.readDeviceName())
    print('Battery: ', gadget.readBattery())
    print('temperature:', gadget.readTemperature())
    print('Humidity: ', gadget.readHumidity())
#     gadget.setLoggerIntervalMs(1000)
    print('LoggerInterval: ', gadget.readLoggerIntervalMs())
    print('OldestTimestampMs: ', gadget.readOldestTimestampMs())
    print('NewestTimeStampMs: ', gadget.readNewestTimestampMs())
    
    gadget.readLoggedDataInterval()
#     gadget.setTemperatureNotification(True)
#     gadget.setHumidityNotification(True)
           
    try:
        while 1:
            gadget.waitForNotifications(3)
            print('readingData')
            if False is gadget.isLogReadoutInProgress():
                print('Done')
                break
        
    finally:
        gadget.disconnect()
        print('disconnected')
 

if __name__ == "__main__":
    main()
