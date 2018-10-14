from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct
import time

class MyDelegate(DefaultDelegate):
    parent = None
    sustainedNotifications = {}
    
    def __init__(self, parent):
        DefaultDelegate.__init__(self)
        self.parent = parent
        self.sustainedNotifications['Temp'] = 0
        self.sustainedNotifications['Humi'] = 0

    def handleNotification(self, cHandle, data):
        # data format for logging data: runnumber (4 bytes (unsigned int)) + N * value (N * 4 bytes (float32); while: 1 <= N <=4 )
        # data format for non-logging data: value (4 bytes (float32)) 
        unpackedData = list(struct.unpack('I'+str(int((len(data)-4)/4))+'f', data))
        runnumber = unpackedData.pop(0)
        
        typeData = ''
        if 55 is cHandle:
            typeData = 'Temp'
        elif 50 is cHandle:
            typeData = 'Humi'
        
        if 0 < len(unpackedData):
            # logging data
            self.sustainedNotifications[typeData] = 0
            for x in unpackedData:
                self.parent.loggedData[typeData][self.parent.newestTimeStampMs-runnumber*self.parent.loggerInterval] = x
                runnumber = runnumber+1
        else:
            # non logging data
            self.sustainedNotifications[typeData] = self.sustainedNotifications[typeData] + 1
            if 1 < self.sustainedNotifications[typeData]:
                # logging data transmission done
                self.sustainedNotifications[typeData] = 2
                if 1 < self.sustainedNotifications['Temp'] and 1 < self.sustainedNotifications['Humi']:
                    self.parent.loggingReadout = False
             
class SHT31:
    characteristics = {}
    newestTimeStampMs = 0
    loggerInterval = 0
    delegate = None
    loggedData = {}
    loggingReadout = False

    def __init__(self, address = '', interface = None):
        self.peripheral = Peripheral(address, addrType="random", iface=interface)

        self.loggedData['Temp'] = {}
        self.loggedData['Humi'] = {}

        # READ WRITE
        self.characteristics['DeviceName'] = self.peripheral.getCharacteristics(uuid=UUID("00002a00-0000-1000-8000-00805f9b34fb"))[0]
  
        # READ NOTIFY 
        self.characteristics['Battery'] = self.peripheral.getCharacteristics(uuid=UUID(0x2A19))[0]
        
        # WRITE
        self.characteristics['SyncTimeMs'] = self.peripheral.getCharacteristics(uuid=UUID("0000f235-b38d-4985-720e-0f993a68ee41"))[0]
        
        # READ WRITE
        self.characteristics['OldestTimeStampMs'] = self.peripheral.getCharacteristics(uuid=UUID("0000f236-b38d-4985-720e-0f993a68ee41"))[0]
        
        # READ WRITE 
        self.characteristics['NewestTimeStampMs'] = self.peripheral.getCharacteristics(uuid=UUID("0000f237-b38d-4985-720e-0f993a68ee41"))[0]
        
        # WRITE NOTIFY 
        self.characteristics['StartLoggerDownload'] = self.peripheral.getCharacteristics(uuid=UUID("0000f238-b38d-4985-720e-0f993a68ee41"))[0]
        
        # READ WRITE
        self.characteristics['LoggerIntervalMs'] = self.peripheral.getCharacteristics(uuid=UUID("0000f239-b38d-4985-720e-0f993a68ee41"))[0]
        
        # READ NOTIFY 
        self.characteristics['Humidity'] = self.peripheral.getCharacteristics(uuid=UUID("00001235-b38d-4985-720e-0f993a68ee41"))[0]
        
        # READ NOTIFY
        self.characteristics['Temperature'] = self.peripheral.getCharacteristics(uuid=UUID("00002235-b38d-4985-720e-0f993a68ee41"))[0]
                 
        self.delegate = MyDelegate(self)      
        self.peripheral.setDelegate(self.delegate)
        
    def disconnect(self):
        self.peripheral.disconnect()
        
    def readDeviceName(self):
        return self.characteristics['DeviceName'].read()
    
    def readTemperature(self):
        return struct.unpack('f', self.characteristics['Temperature'].read())[0]

    def setTemperatureNotification(self, enabled):
        if enabled:
            self.peripheral.writeCharacteristic(self.characteristics['Temperature'].valHandle+2, int(1).to_bytes(1, byteorder = 'little'))
        else:
            self.peripheral.writeCharacteristic(self.characteristics['Temperature'].valHandle+2, int(0).to_bytes(1, byteorder = 'little'))
    
    def readHumidity(self):
        return struct.unpack('f', self.characteristics['Humidity'].read())[0]

    def setHumidityNotification(self, enabled):
        if enabled:
            self.peripheral.writeCharacteristic(self.characteristics['Humidity'].valHandle+2, int(1).to_bytes(1, byteorder = 'little'))
        else:
            self.peripheral.writeCharacteristic(self.characteristics['Humidity'].valHandle+2, int(0).to_bytes(1, byteorder = 'little'))
    
    def readBattery(self):
        return int.from_bytes(self.characteristics['Battery'].read(), byteorder='little')
    
    def setSyncTimeMs(self, timestamp = time.time()):
        self.characteristics['SyncTimeMs'].write(int(round(timestamp * 1000)).to_bytes(8, byteorder='little'))

    def readOldestTimestampMs(self):
        return int.from_bytes(self.characteristics['OldestTimeStampMs'].read(), byteorder='little')

    def readNewestTimestampMs(self):
        return int.from_bytes(self.characteristics['NewestTimeStampMs'].read(), byteorder='little')
    
    def readLoggerIntervalMs(self):
        return int.from_bytes(self.characteristics['LoggerIntervalMs'].read(), byteorder='little')
    
    def setLoggerIntervalMs(self, milliseconds):
        monthMs = (30 * 24 * 60 * 60 * 1000)
        
        if milliseconds < 1000:
            milliseconds = 1000
        elif milliseconds > monthMs:
            milliseconds = monthMs
        self.characteristics['LoggerIntervalMs'].write((int(milliseconds)).to_bytes(4, byteorder='little'))
    
    def readLoggedDataInterval(self, startMs = 0, stopMs = int(round(time.time() * 1000))):
        self.setTemperatureNotification(True)
        self.setHumidityNotification(True)
        
        self.setSyncTimeMs()
        self.newestTimeStampMs = self.readNewestTimestampMs()
        self.loggerInterval = self.readLoggerIntervalMs()
        self.characteristics['OldestTimeStampMs'].write(startMs.to_bytes(8, byteorder='little'))
        self.characteristics['NewestTimeStampMs'].write(stopMs.to_bytes(8, byteorder='little'))
        self.loggingReadout = True
        self.characteristics['StartLoggerDownload'].write((1).to_bytes(1, byteorder='little'))

    def waitForNotifications(self, timeoutS):
        self.peripheral.waitForNotifications(timeoutS)
        
    def isLogReadoutInProgress(self):
        return self.loggingReadout
    