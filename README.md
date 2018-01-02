Tips: 
-----
- Visual Studio Code gebruiken om dit te bewerken: https://code.visualstudio.com/
- Vanuit terminal bewerken: nano main.py (opslaan CTRL+X, Y, enter)
- Uitvoeren: python3 main.py

Bibliotheken:
-------------
- Sommige zijn alleen voor Raspberry Pi en niet beschikbaar voor Windows, Linux of Android
- Android: https://stackoverflow.com/questions/38598880/how-do-i-install-modules-on-qpython3-android-port-of-python

Normaal gesproken installeer je een bibliotheek zo:
`sudo python3 -m pip install bibliotheeknaam`
Gebruik `python` (versie 3) of `python3`, maar dit moet hetzelfde zijn als waarmee je `main.py` start.

Compile:
--------
https://wiki.python.org/moin/Asking%20for%20Help/How%20do%20you%20protect%20Python%20source%20code%3F
https://stackoverflow.com/questions/261638/how-do-i-protect-python-code
http://effbot.org/pyfaq/how-do-i-create-a-pyc-file.htm
python3 -m compileall .


Web:
----
- Start serving a folder: python3 -m http.server 8080
- Hight performance server: Japronto
    - https://github.com/squeaky-pl/japronto
    - https://medium.freecodecamp.org/million-requests-per-second-with-python-95c137af319

Python:
-------
- Data Structures: https://docs.python.org/3/tutorial/datastructures.html
- Properties: https://www.python-course.eu/python3_properties.php