Finanzplaner (Eduard Petri [710642] & Florian Haus [710651] )

Moin. Da wir bei Moodle nicht mehr als 20 Anhänge auf einmal hochladen können, haben wir uns entschieden ein öffentliches GitHub Repository zu erstellen. 
Hier erstmal der Link: https://github.com/D0X5/C-Budget-Tracker_Source-Code


Voraussetzungen:

Python3.x oder höher
Pytest-			--> pip install pytest-cov
PySide6 		--> pip install pyside6
matplotlib		--> pip install matplotlib	



Ausführungshinweise:
Um das Programm zu starten, muss der folgender Ordner in der Testumgebung geöffnet werden: C-Budget-Tracker_Source-Code_Florian-Haus-710651_Eduard-Petri-710642
Hier muss die Datei _Main.py ausgeführt werden.
Um einzelne Unit-Tests durchzuführen kann man jede ..._unit_test.py ausführen.
Mit dem Befehl pytest --cov im Terminal kann man alle Tests überprüfen & deren Coverage.
