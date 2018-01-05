#!/usr/bin/python3.6
"""Startpunt voor de applicatie"""
#region Imports
from common import *
# Importeer pygame (geluid): https://www.pygame.org/wiki/GettingStarted
try: import pygame
except ImportError as e:
    print(Fore.RED + "pygame - Neppe bibliotheek in gebruik" + Style.RESET_ALL)
    class pygame:
        class mixer:
            def init(): return True
            class music:
                def load(file): return True
                def play(): print("Zogenaamd wordt nu een geluid afgespeeld..")
                def get_busy(): return False
#from settings import *
from thermostaat import *
#endregion

def vraagGetal():
    x = int(input("Typ een getal: "))
    if x > 5: print("groter dan 5")
    elif x == 5: print("precies 5")
    else: print("kleiner dan 5")
def klokTonen(): print('Tijd: {}'.format(time.strftime('%H:%M:%S')))
def geluidAfspelen():
    file = "alert2.wav"
    print("Geluid afspelen: " + file)
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True: continue
class Voorbeeld1():
    def __init__(self):
        print("Voorbeeld van: https://stackoverflow.com/questions/36506152/tkinter-grid-or-pack-inside-a-grid")
        self.root = tk.Tk()
        self.root.title("some application")
        # menu left
        self.menu_left = tk.Frame(self.root, width=150, bg="#ababab")
        self.menu_left_upper = tk.Frame(self.menu_left, width=150, height=150, bg="red")
        self.menu_left_lower = tk.Frame(self.menu_left, width=150, bg="blue")
        self.test = tk.Label(self.menu_left_upper, text="test")
        self.test.pack()
        self.menu_left_upper.pack(side="top", fill="both", expand=True)
        self.menu_left_lower.pack(side="top", fill="both", expand=True)
        # right area
        self.some_title_frame = tk.Frame(self.root, bg="#dfdfdf")
        self.some_title = tk.Label(self.some_title_frame, text="some title", bg="#dfdfdf")
        self.some_title.pack()
        self.canvas_area = tk.Canvas(self.root, width=500, height=400, background="#ffffff")
        self.canvas_area.grid(row=1, column=1)
        # status bar
        self.status_frame = tk.Frame(self.root)
        self.status = tk.Label(self.status_frame, text="this is the status bar")
        self.status.pack(fill="both", expand=True)
        self.menu_left.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.some_title_frame.grid(row=0, column=1, sticky="ew")
        self.canvas_area.grid(row=1, column=1, sticky="nsew")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.mainloop()

shortKeys.append(ShortKey("k", __name__, "klokTonen", "klok tonen"))
shortKeys.append(ShortKey("v", __name__, "vraagGetal", "vraag getal"))
shortKeys.append(ShortKey("g", __name__, "geluidAfspelen", "geluid afspelen"))
shortKeys.append(ShortKey("v1", __name__, "Voorbeeld1", "voorbeeld window (tkinter)"))

# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
if __name__ == '__main__': showMenu(sys.argv[1] if len(sys.argv) > 1 else None)
