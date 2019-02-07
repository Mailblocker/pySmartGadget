from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct
import time

class SHT31Delegate(DefaultDelegate):
    def __init__(self, parent):
        DefaultDelegate.__init__(self)
        self.parent = parent
        self.sustainedNotifications = { 'Temp' : 0, 'Humi' : 0 }
        self.enabledNotifications = { 'Temp' : False, 'Humi' : False }
        self.offset = 0

    def prepareLoggerReadout(self, loggerInterval, newestTimeStampMs):
        self.__loggerInterval = loggerInterval
        self.__newestTimeStampMs = newestTimeStampMs
        self.loggingReadout = True

    def handleNotification(self, cHandle, data):
        dataTypes = {55: 'Temp', 50: 'Humi'}
        typeData = dataTypes[cHandle]
        
        if 4 < len(data):
            # data format for on device logged data: runnumber (4 bytes (unsigned int)) + N * value (N * 4 bytes (float32); while: 1 <= N <=4 )
            unpackedData = list(struct.unpack('I'+str(int((len(data)-4)/4))+'f', data))
            runnumber = unpackedData.pop(0)
            self.sustainedNotifications[typeData] = 0
            for x in unpackedData:
                self.parent.loggedDataReadout[typeData][self.__newestTimeStampMs-(runnumber-self.offset)*self.__loggerInterval] = x
                runnumber = runnumber+1
        else:
            # data format for non device logged data: value (4 bytes (float32)) 
            self.sustainedNotifications[typeData] = self.sustainedNotifications[typeData] + 1
            if 1 < self.sustainedNotifications[typeData]:
                # logging data transmission done for this datatype
                self.sustainedNotifications[typeData] = 2
                if sum(self.sustainedNotifications.values())/len(self.sustainedNotifications) >= 2:
                    # logging data transmission done for all datatypes
                    self.loggingReadout = False
                    for dataType, enabled in self.enabledNotifications.items():
                        if dataType is 'Temp' and not enabled:
                            self.parent.setTemperatureNotification(False)
                        elif dataType is 'Humi' and not enabled:
                            self.parent.setHumidityNotification(False)
            
            if self.enabledNotifications[typeData]:
                self.parent.loggedData[typeData][int(round(time.time() * 1000))] = struct.unpack('f', data)[0]

class SHT31():
    def __init__(self, addr = None, iface = None):
        self.loggedDataReadout = {'Temp' : {}, 'Humi': {}}
        self.loggedData = {'Temp' : {}, 'Humi': {}}
        self.__loggerInterval = 0
        self.__loggingReadout = False
     
        self.__peripheral = Peripheral(addr, 'random', iface)
        if addr is not None:
            self.__peripheral.setDelegate(SHT31Delegate(self))
            self.__prepareGadget()
    
    def __prepareGadget(self):
        self.__characteristics = {}

        # READ
        self.__characteristics['SystemId'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A23))[0]
        # READ
        self.__characteristics['ManufacturerNameString'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A29))[0]
        # READ
        self.__characteristics['ModelNumberString'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A24))[0]
        # READ
        self.__characteristics['SerialNumberString'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A25))[0]
        # READ
        self.__characteristics['HardwareRevisionString'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A27))[0]
        # READ
        self.__characteristics['FirmwareRevisionString'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A26))[0]
        # READ
        self.__characteristics['SoftwareRevisionString'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A28))[0]
        # READ WRITE
        self.__characteristics['DeviceName'] = self.__peripheral.getCharacteristics(uuid=UUID("00002a00-0000-1000-8000-00805f9b34fb"))[0]
        # READ NOTIFY 
        self.__characteristics['Battery'] = self.__peripheral.getCharacteristics(uuid=UUID(0x2A19))[0]
        # WRITE
        self.__characteristics['SyncTimeMs'] = self.__peripheral.getCharacteristics(uuid=UUID("0000f235-b38d-4985-720e-0f993a68ee41"))[0]
        # READ WRITE
        self.__characteristics['OldestTimeStampMs'] = self.__peripheral.getCharacteristics(uuid=UUID("0000f236-b38d-4985-720e-0f993a68ee41"))[0]
        # READ WRITE 
        self.__characteristics['NewestTimeStampMs'] = self.__peripheral.getCharacteristics(uuid=UUID("0000f237-b38d-4985-720e-0f993a68ee41"))[0]
        # WRITE NOTIFY 
        self.__characteristics['StartLoggerDownload'] = self.__peripheral.getCharacteristics(uuid=UUID("0000f238-b38d-4985-720e-0f993a68ee41"))[0]
        # READ WRITE
        self.__characteristics['LoggerIntervalMs'] = self.__peripheral.getCharacteristics(uuid=UUID("0000f239-b38d-4985-720e-0f993a68ee41"))[0]
        # READ NOTIFY 
        self.__characteristics['Humidity'] = self.__peripheral.getCharacteristics(uuid=UUID("00001235-b38d-4985-720e-0f993a68ee41"))[0]
        # READ NOTIFY
        self.__characteristics['Temperature'] = self.__peripheral.getCharacteristics(uuid=UUID("00002235-b38d-4985-720e-0f993a68ee41"))[0]
        
        if self.readFirmwareRevisionString() == '1.3':
            # Error in the documentation/firmware of 1.3 runnumber does not start with 0 it starts with 1, therefore insert an offset here
            self.__peripheral.delegate.offset = 1
    
    def connect(self, addr, iface=None):
        self.__peripheral.setDelegate(SHT31Delegate(self))
        self.__peripheral.connect(addr, 'random', iface)
        self.__prepareGadget()                 
    
    def disconnect(self):
        self.__peripheral.disconnect()
        
    def __readCharacteristcAscii(self, name):
        return self.__characteristics[name].read().decode('ascii')
        
    def readDeviceName(self):
        return self.__readCharacteristcAscii('DeviceName')

    def setDeviceName(self, name):
        return self.__characteristics['DeviceName'].write(name.encode('ascii'))
    
    def readTemperature(self):
        return struct.unpack('f', self.__characteristics['Temperature'].read())[0]

    def setTemperatureNotification(self, enabled):
        tmp = 1 if enabled else 0
        self.__peripheral.delegate.enabledNotifications['Temp'] = enabled
        self.__setTemperatureNotification(tmp)
        
    def __setTemperatureNotification(self, byte):
        self.__peripheral.writeCharacteristic(self.__characteristics['Temperature'].valHandle+2, int(byte).to_bytes(1, byteorder = 'little'))
        
    def readHumidity(self):
        return struct.unpack('f', self.__characteristics['Humidity'].read())[0]

    def setHumidityNotification(self, enabled):
        tmp = 1 if enabled else 0
        self.__peripheral.delegate.enabledNotifications['Humi'] = enabled
        self.__setHumidityNotification(tmp)

    def __setHumidityNotification(self, byte):
        self.__peripheral.writeCharacteristic(self.__characteristics['Humidity'].valHandle+2, int(byte).to_bytes(1, byteorder = 'little'))
    
    def readBattery(self):
        return int.from_bytes(self.__characteristics['Battery'].read(), byteorder='little')
    
    def setSyncTimeMs(self, timestamp = None):
        timestampMs = timestamp if timestamp else int(round(time.time() * 1000))
        self.__characteristics['SyncTimeMs'].write(timestampMs.to_bytes(8, byteorder='little'))

    def readOldestTimestampMs(self):
        return int.from_bytes(self.__characteristics['OldestTimeStampMs'].read(), byteorder='little')

    def setOldestTimestampMs(self, value):
        self.__characteristics['OldestTimeStampMs'].write(value.to_bytes(8, byteorder='little'))

    def readNewestTimestampMs(self):
        return int.from_bytes(self.__characteristics['NewestTimeStampMs'].read(), byteorder='little')

    def setNewestTimestampMs(self, value):
        self.__characteristics['NewestTimeStampMs'].write(value.to_bytes(8, byteorder='little'))
    
    def readLoggerIntervalMs(self):
        return int.from_bytes(self.__characteristics['LoggerIntervalMs'].read(), byteorder='little')
    
    def setLoggerIntervalMs(self, interval):
        oneMonthInMs = (30 * 24 * 60 * 60 * 1000)
        interval = 1000 if interval < 1000 else oneMonthInMs if interval > oneMonthInMs else interval
        self.__characteristics['LoggerIntervalMs'].write((int(interval)).to_bytes(4, byteorder='little'))
    
    def readLoggedDataInterval(self, startMs = None, stopMs = None):
        self.setSyncTimeMs()
        time.sleep(0.1) # Sleep a bit to enable the gadget to set the SyncTime; otherwise 0 is read when readNewestTimestampMs is used
        self.__setTemperatureNotification(1)
        self.__setHumidityNotification(1)
        
        if startMs is not None:
            self.setOldestTimestampMs(startMs)
        else:
            self.setOldestTimestampMs(0)
        
        if stopMs is not None:
            self.setNewestTimestampMs(stopMs)
#         else:
#             self.setNewestTimestampMs(0)

        tmpNewestTimestamp = self.readNewestTimestampMs()
        #print(tmpNewestTimestamp)
        self.__peripheral.delegate.prepareLoggerReadout(self.readLoggerIntervalMs(), tmpNewestTimestamp)
        self.__characteristics['StartLoggerDownload'].write((1).to_bytes(1, byteorder='little'))

    def waitForNotifications(self, timeout):
        return self.__peripheral.waitForNotifications(timeout)
        
    def isLogReadoutInProgress(self):
        return self.__peripheral.delegate.loggingReadout
       
    def readSystemId(self):
        return self.__characteristics['SystemId'].read()
       
    def readManufacturerNameString(self):
        return self.__readCharacteristcAscii('ManufacturerNameString')
        
    def readModelNumberString(self):
        return self.__readCharacteristcAscii('ModelNumberString')

    def readSerialNumberString(self):
        return self.__readCharacteristcAscii('SerialNumberString')

    def readHardwareRevisionString(self):
        return self.__readCharacteristcAscii('HardwareRevisionString')

    def readFirmwareRevisionString(self):
        return self.__readCharacteristcAscii('FirmwareRevisionString')

    def readSoftwareRevisionString(self):
        return self.__readCharacteristcAscii('SoftwareRevisionString')
    