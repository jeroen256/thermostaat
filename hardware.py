"""Bibliotheek met handware"""

#region Imports
from common import *

# Importeer Adafruit_DHT (temperatuur): https://github.com/adafruit/Adafruit_Python_DHT
try: import Adafruit_DHT
except ImportError as e:
    print(Fore.RED+"Adafruit_DHT - Neppe bibliotheek in gebruik"+Style.RESET_ALL)
    class Adafruit_DHT:
        DHT22 = 'c'
        temperatuur = 20.0
        afkoelen = True
        def read_retry(a, b):
            if Adafruit_DHT.temperatuur < 13: Adafruit_DHT.afkoelen = False
            if Adafruit_DHT.temperatuur > 20: Adafruit_DHT.afkoelen = True
            if Adafruit_DHT.afkoelen: Adafruit_DHT.temperatuur -= 1
            else: Adafruit_DHT.temperatuur += 1
            return 11, Adafruit_DHT.temperatuur

try: import serial
except ImportError as e: print(Fore.RED + "serial - ImportError, probeer: sudo apt install python3-serial"+Style.RESET_ALL)

from settings import *
#endregion

class Dht22():
    """Leest de DHT22 temperatuur en vochtigheids sensor uit."""
    temperature = 0.0
    """Temperatuur in graden celcius"""
    humidity = 0.0
    """Luchtvochtigheid in procenten"""
    def read(self):
        """Leest de sensor uit"""
        self.humidity, self.temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, settings.temperature_pin)
        if self.humidity == None: self.humidity = 0
        if self.humidity > 150: self.humidity = 150
        if self.temperature == None: self.temperature = 0
        self.humidity = round(self.humidity, 2)
        self.temperature = round(self.temperature, 2)

class SlimmeMeter:
    """Leest de slimme meter uit"""
    def __init__(self):
        self.read_time = None
        """Tijdstip waarop de meter voor het laatst is uitgelezen"""
        self.start_time = None
        """Tijdstip waarop is begonnen met het uitlezen van de meter"""
        self.start_m3 = 0.0
        """Meterstand gas aan het begin"""
        self.start_kwh = 0.0
        """Meterstand electriciteit aan het begin"""
        self.m3 = 0.0
        """Meterstand gas"""
        self.kwh = 0.0
        """Meterstand electriciteit"""
        self.watt = 0
        """Hoeveelheid electriciteit wat op dit moment wordt gebruikt"""
        self.stack = []
        self.error = None
    def read(self):
        """Leest de sensor uit"""
        try:
            self.read_time = datetime.datetime.now()
            ser = serial.Serial()
            ser.baudrate = 115200
            ser.bytesize  = serial.EIGHTBITS
            ser.parity = serial.PARITY_NONE
            ser.stopbits = serial.STOPBITS_ONE
            ser.xonxoff = 0
            ser.rtscts = 0
            ser.timeout = 20
            ser.port = "/dev/ttyUSB0"
            ser.open()
            self.read_time = datetime.datetime.now()
            self.stack = []
            for i in range(26):
                self.stack.append(str(ser.readline()).strip())
            #self.hoog_tarief = int(stack[7][12:18])
            #self.laag_tarief = int(stack[6][12:18])
            self.kwh = float(self.stack[7][12:22]) + float(self.stack[6][12:22])
            self.watt = int(float(self.stack[21][13:19]) * 1000)
            self.m3 = float(self.stack[25][28:37])
            if self.start_time == None:
                self.start_time = datetime.datetime.now()
                self.start_m3 = self.m3
                self.start_kwh = self.kwh
            ser.close()
        except Exception as ex: 
            time.sleep(.5)
            new_error = str(ex)
            if self.error != new_error: print("Fout SlimmeMeter.read(): " + new_error)
            self.error = new_error

def main():
    dht22 = Dht22()
    dht22.read()
    print("Dht22:\n" + json.dumps(dht22.__dict__, default=json_util.default, indent=4))
    slimmeMeter = SlimmeMeter()
    slimmeMeter.read()
    # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
    print("SlimmeMeter:\n" + json.dumps(slimmeMeter.__dict__, default=json_util.default, indent=4))

if __name__ == '__main__': main()
