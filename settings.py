"""Bibliotheek voor de instellingen"""
#region Imports
from common import *
#endregion

class Settings:
    """Welkom bij de instellingen"""
    def __init__(self):
        self.temperature = 19.0
        self.temperature_margin = 0.5
        self.temperature_interval_seconds = 1.0
        self.temperature_pin = 4
        self.area_1_name = "Keuken"
        self.area_1_enabled = True
        self.area_1_pin = 12
        self.area_2_name = "Woonkamer"
        self.area_2_enabled = False
        self.area_2_pin = 13
    def save(self):
        """Slaat de instellingen op in een bestand"""
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.__dict__, f, sort_keys=True, indent=4)
            with open('settings.pkl', 'wb') as f:
                pickle.dump(self.__dict__, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e: print("Fout settings.save(): {}".format(str(e)))
    def load(self):
        """Leest de instellingen uit een bestand indien mogelijk"""
        try:
            #with open('settings.pkl', 'rb') as f:
            #    self.__dict__ = pickle.load(f)
            with open('settings.json', 'r') as f:
                #self.__dict__ = json.load(f)
                new = Settings()
                new.__dict__ = json.load(f)
                self.set(new)
        except Exception as e:
            print("Fout settings.load(): {}".format(str(e)))
    def set(self, new: 'Settings'):
        """Use this to change the settings. It checks and corrects the new settings. It prepares the GPIO pins, if changed. Then it sets the current settings to the new settings and saves them."""
        # Check and correct input:
        if new.temperature_interval_seconds < 0.1: new.temperature_interval_seconds = 0.1
        if new.temperature_interval_seconds > 25.5: new.temperature_interval_seconds = 25.5 # curses.halfdelay cannot exceed 255
        new.temperature_interval_seconds = round(new.temperature_interval_seconds, 2)
        new.temperature = round(new.temperature, 2)
        if new.temperature_margin < 0: new.temperature_margin = 0
        new.temperature_margin = round(new.temperature_margin, 2)
        # Prepare GPIO pins:
        if self.area_1_pin != new.area_1_pin:
            GPIO.output(self.area_1_pin, False) # switch off old pin
            GPIO.setup(new.area_1_pin, GPIO.OUT) # setup new pin
        if self.area_2_pin != new.area_2_pin:
            GPIO.output(self.area_2_pin, False) # switch off old pin
            GPIO.setup(new.area_2_pin, GPIO.OUT) # setup new pin
        # set current settings to new:
        self.__dict__ = new.__dict__
        self.save()

# https://danielkaes.wordpress.com/2009/06/29/iterating-over-attributes-of-a-python-object/
def SettingsTerminal():
    new = Settings()
    new.__dict__ = copy.deepcopy(settings.__dict__)
    doc = getattr(new, "__doc__")
    for key, value in sorted(new.__dict__.items()):
        if isinstance(value, bool):
            waarde = input("{}: (j:ja / n:nee) [{}] ".format(key, "j" if value else "n"))
            if waarde != '':
                if waarde == "j": setattr(new, key, True)
                else: setattr(new, key, False)
        else:
            waarde = input("{}: [{}] ".format(key, str(value)))
            if waarde != '': 
                if isinstance(value, float): setattr(new, key, float(waarde))
                elif isinstance(value, int): setattr(new, key, int(waarde))
                else: value = setattr(new, key, str(waarde))
    settings.set(new)

class SettingsWindow():
    def __init__(self, topLevel = False):
        self.new = Settings()
        self.new.__dict__ = copy.deepcopy(settings.__dict__)
        self.fields = []
        if topLevel: self.root = Toplevel()
        else: self.root = Tk()
        self.root.title("Instellingen")
        image = PhotoImage(file='icon.png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, image)
        Label(self.root, text=getattr(self.new, "__doc__"), fg="red", font=("Helvetica", 16), pady=30).grid(row=0, column=1, columnspan=2, padx=(30, 10))
        Label(self.root, image=image).grid(row=0, column=3, rowspan=len(self.new.__dict__.items()) + 2)

        row = 0
        for key, value in sorted(self.new.__dict__.items()):
            row += 1
            Label(self.root, text=str(key).replace('_', ' ').capitalize()).grid(row=row, column=1, padx=15, sticky="w")
            if isinstance(value, bool):
                self.fields.append(IntVar(value=1 if value == True else 0))
                box = Checkbutton(self.root, variable=self.fields[-1])
                box.grid(row=row, column=2, sticky="w")
            else:
                if isinstance(value, str): self.fields.append(Entry(self.root))
                else: self.fields.append(Entry(self.root, width=6))
                self.fields[-1].insert(END, str(value))
                self.fields[-1].grid(row=row, column=2, sticky="w")

        buttons = Frame(self.root)
        Button(buttons, text="OK", command=self.ok).pack(side=LEFT)
        Button(buttons, text="Annuleren", command=self.cancel).pack(side=LEFT)
        buttons.grid(row=row + 1, column=1, columnspan=2, ipady=30)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(row + 1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(3, weight=4)
        self.root.mainloop()
    def cancel(self): self.root.destroy()
    def ok(self):
        for i, (key, value) in enumerate(sorted(self.new.__dict__.items())):
            waarde = self.fields[i].get()
            if isinstance(value, bool):
                if waarde == 1: setattr(self.new, key, True)
                else: setattr(self.new, key, False)
            elif isinstance(value, float): setattr(self.new, key, float(waarde))
            elif isinstance(value, int): setattr(self.new, key, int(waarde))
            else: value = setattr(self.new, key, str(waarde))
        settings.set(self.new)
        self.root.destroy()

settings = Settings()
settings.load()

shortKeys.append(ShortKey("i1", __name__, "SettingsTerminal", "instellingen wijzigen (terminal)"))
shortKeys.append(ShortKey("i2", __name__, "SettingsWindow", "instellingen wijzigen (window)"))

if __name__ == '__main__': showMenu(sys.argv[1] if len(sys.argv) > 1 else None)
