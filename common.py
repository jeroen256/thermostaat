"""Module met code welke overal beschikbaar moet zijn"""
#region Imports
import os
import sys
import time
import datetime
# Importeer colorama (kleuren in print functie): # https://pypi.python.org/pypi/colorama
try: from colorama import init, Fore, Back, Style
except ImportError as e:
    print("colorama - ImportError, probeer: sudo python3 -m pip install colorama")
    sys.exit()
init()  # voor kleuren onder Windows

# Importeer tkinter (windows en formulieren): http://effbot.org/tkinterbook/tkinter-index.htm#class-reference
try: 
    from tkinter import *
    from tkinter import messagebox
    import tkinter as tk
except ImportError as e: print(Fore.RED + "tkinter - ImportError, probeer: sudo apt install python3-tk")

# PyMongo is a Python distribution containing tools for working with MongoDB
# bson is a PyMongo package for json serializing complex types such as datetime
# https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
# http://api.mongodb.com/python/current/api/bson/json_util.html
try: from bson import json_util
except ImportError as ex: print(Fore.RED+"bson - ImportError, probeer: sudo python3 -m pip install pymongo")
import json
import pickle
import copy

# Imporeer GPIO (General Purpose Input/Output): https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/
try: import RPi.GPIO as GPIO 
except RuntimeError: print(Fore.RED+"GPIO - RuntimeError, probeer met meer rechten: sudo python3 jeroen.py")
except ImportError as e: print(Fore.RED + "GPIO - ImportError, probeer: sudo python3 -m pip install RPi.GPIO")
if not 'GPIO' in dir():
    print(Fore.RED + "GPIO - Neppe bibliotheek in gebruik"+Style.RESET_ALL)
    class GPIO:
        BOARD = 1
        BCM = 2
        IN = 'input'
        OUT = 'output'
        LOW = 0
        HIGH = 1
        lastPrint = {}
        def setmode(mode): pass
        def cleanup(): pass
        def setup(channel, mode): print("Neppe kanaal {} nu gereed voor {}.".format(channel,mode))
        def output(channel, state): 
            newPrint = "Neppe kanaal {} nu zogenaamd {}.".format(channel,state)
            if channel in GPIO.lastPrint and GPIO.lastPrint[channel] != newPrint: print(newPrint)
            GPIO.lastPrint[channel] = newPrint
#endregion

def clearScreen(): os.system('cls' if os.name == 'nt' else 'clear')

class ShortKey():
    def __init__(self, key, module_name, command, description):
        self.key = key
        self.module_name = module_name
        self.command = command
        self.description = description

shortKeys = []
"""Voeg hier ShortKeys aan toe om automatisch te tonen in het menu"""

def showMenu(y):
    shortKeys.sort(key=lambda x: x.key)
    try:
        print(Style.RESET_ALL+"Tip: typ h om help te tonen.")
        stop = 0
        while stop == 0:
            if y == None: y = input(Fore.YELLOW + Back.BLACK + "Wat wilt u doen? " + Style.RESET_ALL)
            selectedShortKey = next((x for x in shortKeys if x.key == y), None)
            if selectedShortKey != None:
                attribute = getattr(sys.modules[selectedShortKey.module_name], selectedShortKey.command)
                attribute()
            elif y == 'c':  clearScreen()
            elif y == 'h':
                for item in shortKeys: print("{:<2} - {}".format(item.key, item.description))
                print("c  - scherm leegmaken")
                print("q  - afsluiten (of CTRL + C, of x)")
            elif y == 'q' or y == 'x': stop = 1
            else: print(Fore.RED + "Onbekende keuze." + Style.RESET_ALL + " Typ h om help te tonen.")
            y = None
    except KeyboardInterrupt: print("")
    print("Tot ziens")
