#!/usr/bin/python3.6
"""Bibliotheek voor de verschillende thermostaten"""
#region Imports
from common import *

# Importeer curses (terminal print verversen zonder flikkeren): https://docs.python.org/3/howto/curses.html
# Windows? download: https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
# Windows? run: pyhton -m pip install curses-2.2-cp36-cp36m-win_amd64.whl
try: import curses
except ImportError as ex: 
    if os.name == 'nt': print(Fore.RED+"curses - ImportError, probeer: 1) download: https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses 2) run: pyhton -m pip install curses-2.2-cp36-cp36m-win_amd64.whl")
    else: print(Fore.RED+"curses - ImportError, ({}), probeer: sudo python3 -m pip install curses".format(str(ex)))

from http.server import *
import socket
import threading

from settings import *
from hardware import *
#endregion

class Thermostaat:
    """Bevat papa's thermostaat logica."""
    def __init__(self, auto_update=False):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(settings.area_1_pin, GPIO.OUT)
        self.heating = False
        self.dht22 = Dht22()
        self.slimmeMeter = SlimmeMeter()
        #print("Thermostaat.__init__()")
        if auto_update: self.update(True)
    def change_settings(self, new_settings: Settings):
        settings.set(new_settings)
        self.update(False, False)
    def update(self, repeat=False, read_sensors=True):
        if read_sensors: self.dht22.read()
        if read_sensors: self.slimmeMeter.read()
        if self.dht22.temperature < settings.temperature - settings.temperature_margin: self.heating = True
        if self.dht22.temperature >= settings.temperature + settings.temperature_margin: self.heating = False
        if settings.area_1_enabled: GPIO.output(settings.area_1_pin, self.heating)
        else:
            try: GPIO.output(settings.area_1_pin, False)
            except: pass
        if settings.area_2_enabled: GPIO.output(settings.area_2_pin, self.heating)
        else:
            try: GPIO.output(settings.area_2_pin, False)
            except: pass
        #print("Thermostaat.update()")
        if repeat:
            self.timer = threading.Timer(settings.temperature_interval_seconds, self.update, args={True})
            self.timer.start()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
    def cleanup(self):
        print("Thermostaat.cleanup()")
        try: self.timer
        except: print("no timer to cancel")
        else: self.timer.cancel()
        settings.save()
        GPIO.cleanup()

def thermostaatTerminal():
    with Thermostaat() as thermostaat:
        stop = 0
        while stop == 0:
            try:
                clearScreen()
                thermostaat.update()
                print('Temperatuur: {0:0.1f}'.format(thermostaat.dht22.temperature))
                print('Vochtigheid: {0:0.1f}'.format(thermostaat.dht22.humidity))
                print('Watt: {}'.format(thermostaat.slimmeMeter.watt))
                print('Tijd: {}'.format(time.strftime('%H:%M:%S')))
                status = Back.BLUE + "Uitgeschakeld" + Style.RESET_ALL
                if thermostaat.heating == True:
                    status = Back.RED + "Ingeschakeld" + Style.RESET_ALL
                print("Thermostaat " + str(settings.temperature) + "*C +/- " + str(settings.temperature_margin) + "*C: " + status)
                print("Temperatuur wordt elke {} seconden uitgelezen.".format(settings.temperature_interval_seconds))
                print("Druk op CTRL + C om te stoppen.")
                time.sleep(settings.temperature_interval_seconds)
            except KeyboardInterrupt: stop = 1

def thermostaatCurses():
    curses.wrapper(thermostaatCursesWrapper)

def thermostaatCursesWrapper(stdscr):
    with Thermostaat() as thermostaat:
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        stop, key = 0, -1
        while stop == 0:
            try:
                curses.halfdelay(int(settings.temperature_interval_seconds * 10))
                stdscr.clear()
                if key == -1: thermostaat.update()
                stdscr.addstr(0, 0, 'Temperatuur: ')
                stdscr.addstr(1, 0, 'Luchtvochtigheid: ')
                stdscr.addstr(2, 0, 'Watt / Tijd: ')
                zin = 'Thermostaat {}*C +/- {}*C: '.format(settings.temperature, settings.temperature_margin)
                stdscr.addstr(0, len(zin), '{}*C'.format(thermostaat.dht22.temperature))
                stdscr.addstr(1, len(zin), '{}%'.format(thermostaat.dht22.humidity))
                stdscr.addstr(2, len(zin), '{} / {}'.format(thermostaat.slimmeMeter.watt, time.strftime('%H:%M:%S')))
                stdscr.addstr(3, 0, zin)
                if thermostaat.heating: stdscr.addstr(3, len(zin), 'Ingeschakeld', curses.color_pair(1))
                else: stdscr.addstr(3, len(zin), 'Uitgeschakeld', curses.color_pair(2))
                stdscr.addstr(4, 0, "Temperatuur uitlezen: ")
                stdscr.addstr(4, len(zin), "elke {} seconde(n)".format(settings.temperature_interval_seconds))
                if curses.LINES > 6: stdscr.addstr(6, 0, "- +: Thermostaat temperatuur instellen")
                if curses.LINES > 7: stdscr.addstr(7, 0, "[ ]: Thermostaat temperatuur instellen (achter de komma)")
                if curses.LINES > 8: stdscr.addstr(8, 0, "< >: Thermostaat marge instellen (achter de komma)")
                if curses.LINES > 9: stdscr.addstr(9, 0, "( ): Temperatuur uitleestijd instellen")
                if curses.LINES > 10: stdscr.addstr(10, 0, "x of CTRL + C: terug naar hoofdmenu")
                if curses.LINES > 12: stdscr.addstr(12, 0, 'Laatst ontvangen toetscode: {}'.format(key))
                if curses.LINES > 6: stdscr.refresh()
                key = stdscr.getch() # waits up to <settings.temperature_interval_seconds> seconds, continues immediately after keypress
                new = Settings()
                new.__dict__ = copy.deepcopy(settings.__dict__)
                if key == ord('x'): stop=1
                elif key == ord('-') or key == 464: new.temperature -= 1
                elif key == ord('+') or key == 465: new.temperature += 1
                elif key == ord('['): new.temperature -= 0.1
                elif key == ord(']'): new.temperature += 0.1
                elif key == ord('<'): new.temperature_margin -= 0.1
                elif key == ord('>'): new.temperature_margin += 0.1
                elif key == ord('('): new.temperature_interval_seconds -= 0.1
                elif key == ord(')'): new.temperature_interval_seconds += 0.1
                thermostaat.change_settings(new)
            except KeyboardInterrupt: stop = 1

class ThermostaatWindow():
    def __init__(self):
        self.root = Tk()
        self.root.title("Thermostaat")
        #self.root.wm_attributes('-transparentcolor','red')
        image = PhotoImage(file='icon.png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, image)
        image = PhotoImage(file='thermostaat.png')
        frame = Frame(self.root)
        Label(frame, image=image).pack()
        vlamImage = PhotoImage(file='thermostaat-vlam.png')
        self.vlamLabel = Label(frame, image=vlamImage, bg="#dadada")
        self.v0 = StringVar()
        Label(frame, textvariable=self.v0, font=("Helvetica", 50), fg="#515151", bg="#dadada").place(x=310, y=210, anchor=NE)
        self.v1 = StringVar()
        Label(frame, textvariable=self.v1, font=("Helvetica", 16), fg="#515151", bg="#dadada").place(x=130, y=173)
        self.v2 = StringVar()
        Label(frame, textvariable=self.v2, font=("Helvetica", 16), fg="#515151", bg="#dadada").place(x=370, y=173, anchor=NE)
        self.v3 = StringVar()
        Label(frame, textvariable=self.v3, font=("Helvetica", 16), fg="#515151", bg="#dadada").place(x=130, y=285)
        self.v4 = StringVar()
        Label(frame, textvariable=self.v4, font=("Helvetica", 16), fg="#515151", bg="#dadada").place(x=370, y=285, anchor=NE)
        buttons = Frame(frame, bg="#7e7e7e")
        Button(buttons, text="⇧", font=("Helvetica", 18), bg="#7e7e7e", fg="white", highlightbackground="#7e7e7e", command=self.omhoog).pack(side=LEFT, padx=2)
        Button(buttons, text="⚙", font=("Helvetica", 18), bg="#7e7e7e", fg="white", highlightbackground="#7e7e7e", command=self.instellingen).pack(side=LEFT, padx=2)
        Button(buttons, text="⇩", font=("Helvetica", 18), bg="#7e7e7e", fg="white", highlightbackground="#7e7e7e", command=self.omlaag).pack(side=LEFT, padx=2)
        buttons.place(x=250, y=333, anchor=N)
        
        frame.grid(row=1, column=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        self.thermostaat = Thermostaat()
        self.update()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    def update(self, repeat=True):
        if repeat: self.thermostaat.update()
        if self.thermostaat.heating: self.vlamLabel.place(x=120, y=225)
        else: self.vlamLabel.place_forget()
        self.v0.set('{0:0.1f}'.format(self.thermostaat.dht22.temperature))
        self.v1.set('{}'.format(time.strftime('%H:%M')))
        self.v2.set('{} Watt'.format(self.thermostaat.slimmeMeter.watt))
        self.v3.set('{0:0.1f} °C'.format(settings.temperature))
        self.v4.set('{0:0.1f} %'.format(self.thermostaat.dht22.humidity))
        if repeat: self.timer = self.root.after(int(settings.temperature_interval_seconds * 1000), self.update)
    def omhoog(self):
        new = copy.deepcopy(settings)
        new.temperature += .5
        self.thermostaat.change_settings(new)
        self.update(False)
    def omlaag(self):
        new = copy.deepcopy(settings)
        new.temperature -= .5
        self.thermostaat.change_settings(new)
        self.update(False)
    def on_closing(self):
        self.messageWindow()
        #if messagebox.askokcancel("Afsluiten", "Wilt u dit venster sluiten?"):
        #    GPIO.cleanup()
        #    self.root.destroy()
    def messageWindow(self):
        win = Toplevel()
        win.title('Sluiten')
        Label(win, text="Wat wilt u doen?").pack(fill=X, padx=16, pady=16)
        Button(win, text='Instellingen', command=self.instellingen).pack(fill=X, padx=16, pady=4)
        Button(win, text='Terminal (menu)', command=self.close).pack(fill=X, padx=16, pady=4)
        Button(win, text='Afsluiten', command=self.quit).pack(fill=X, padx=16, pady=4)
        Button(win, text='Niets', command=win.destroy).pack(fill=X, padx=16, pady=(4, 16))
    def instellingen(self):
        SettingsWindow(True)
    def close(self):
        self.thermostaat.cleanup()
        self.root.after_cancel(self.timer)
        self.root.destroy()
    def quit(self):
        self.close()
        sys.exit()

class RoundTripEncoder(json.JSONEncoder): # https://gist.github.com/simonw/7000493
    def default(self, obj):
        # if isinstance(obj, datetime.datetime): return { "_type": "datetime", "value": obj.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT)) }
        if isinstance(obj, datetime.datetime): return obj.isoformat()
        #if isinstance(obj, threading.Timer): return "threading.Timer"
        if hasattr(obj, '__dict__'): return obj.__dict__
        if not isinstance(obj, (dict, list, str, int, float, bool)): return "not supported"
        return super(RoundTripEncoder, self).default(obj)

def del_private(d): #https://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization
    """ Delete keys that start with ``__`` in a dictionary, recursively.
    This alters the input so you may wish to ``copy`` the dict first. """
    for key, value in list(d.items()):
        if str(key).startswith("__"): del d[key]
        elif isinstance(value, dict): del_ndel_privateone(value)
    return d  # For convenience

# https://stackoverflow.com/questions/18444395/basehttprequesthandler-with-custom-instance
class ThermostaatWeb_RequestHandler(BaseHTTPRequestHandler):
    """https://code-maven.com/static-server-in-python"""
    def __init__(self, thermostaat, *args):
        self.thermostaat = thermostaat
        self.headers_already_sent = False
        BaseHTTPRequestHandler.__init__(self, *args)
    def do_OPTIONS(self):
        #self.headers1(content_type=None)
        self.send_response(200, "ok")
        #self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:4200')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    def do_GET(self):
        try:
            #root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'html')
            root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wwwroot')
            print(self.path)
            if self.path == '/': filename = root + '/index.html'
            else: filename = root + self.path
            # Make dynamic response?
            if self.path == "/api/settings": return self.json(settings)
            if self.path == "/api/status": return self.json(self.thermostaat)
            if self.path == "/api/test": 
                birthDate = datetime.datetime(1980, 10, 28)
                return self.json({ 'name': "Jeroen", 'age': 37, 'birthDate': birthDate, 'birthDate2': birthDate.isoformat(), "birthDate3": birthDate.strftime("%d-%m-%Y %H:%M:%S"), 'now': datetime.datetime.now(), 'now2': datetime.datetime.now().isoformat() })
            # Serve the static file
            content_type = 'text/html'
            if filename[-4:] == '.css': content_type = 'text/css'
            elif filename[-5:] == '.json': content_type = 'application/json'
            elif filename[-7:] == '.js.map': content_type = 'application/json'
            elif filename[-3:] == '.js': content_type = 'application/javascript'
            elif filename[-4:] == '.ico': content_type = 'image/x-icon'
            elif filename[-4:] == '.png': content_type = 'image/png'
            elif filename[-4:] == '.gif': content_type = 'image/gif'
            elif filename[-4:] == '.jpg': content_type = 'image/jpeg'
            elif filename[-4:] == '.svg': content_type = 'image/svg+xml'
            try:
                self.headers1(content_type = content_type)
                with open(filename, 'rb') as fh:
                    html = fh.read()
                    self.wfile.write(html)
            except: return self.json({'Exception': 'Not Found (404)' }, 404)
        except Exception as ex:
            self.json({'Exception': str(ex) }, 500)
            raise
    def do_POST(self): # https://stackoverflow.com/questions/31371166/reading-json-from-simplehttpserver-post-data
        try:
            if self.path == "/api/settings":
                body = self.rfile.read(int(self.headers['Content-Length']))
                body1 = body.decode('utf-8') #https://stackoverflow.com/questions/31019854/python-3-3-typeerror-cant-use-a-string-pattern-on-a-bytes-like-object-in-re-fi
                new = Settings()
                new.__dict__ = json.loads(body1)
                self.thermostaat.change_settings(new)
                return self.json(settings)
        except Exception as ex:
            self.json({'Exception': str(ex) }, 500)
            raise
    def json(self, my_object, status_code=200):
        """Converts the object to json and sends it to the client"""
        self.headers1(status_code = status_code)
        body = json.dumps(my_object, cls=RoundTripEncoder, sort_keys=True, indent=4)
        self.wfile.write(bytes(body ,'utf8'))
    def html(self, body, code=200):
        """Sends html to the client"""
        self.headers1(content_type = 'text/html')
        self.wfile.write(bytes(body ,'utf8'))
    def headers1(self, status_code = 200, content_type = 'application/json'):
        """Sends statuscode (https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) and content-type header to the client. Can only be done once. Returns True if succesful or False if they already have been sent."""
        if self.headers_already_sent: return False
        self.send_response(status_code)
        if content_type != None: self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:4200')
        self.end_headers()
        self.headers_already_sent = True
        return True

def thermostaatWeb(server_class=HTTPServer, port=8080):
    """Choose port 8080, for port 80, which is normally used for a http server, you need root access"""
    server_address = ('', port)
    # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]

    thermostaat = Thermostaat(True)
    def handler(*args): ThermostaatWeb_RequestHandler(thermostaat, *args)
    httpd = server_class(server_address, handler)
    print('Webserver running, press CTRL + C to stop. Goto: \nhttp://raspberrypi:8080\nhttp://localhost:{0}\nhttp://{1}:{0}\n(CTRL + click to open)'.format(port, ip))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        thermostaat.cleanup()

shortKeys.append(ShortKey("t1", __name__, "thermostaatTerminal", "thermostaat tonen (terminal)"))
shortKeys.append(ShortKey("t2", __name__, "thermostaatCurses", "thermostaat tonen (curses)"))
shortKeys.append(ShortKey("t3", __name__, "ThermostaatWindow", "thermostaat tonen (window)"))
shortKeys.append(ShortKey("t4", __name__, "thermostaatWeb", "thermostaat tonen (website)"))

if __name__ == '__main__': showMenu(sys.argv[1] if len(sys.argv) > 1 else None)
