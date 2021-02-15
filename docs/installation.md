# Voraussetzung

Folgende Voraussetzung müssen auf Betriebssystemseite gegeben sein um UVC-Reha erfolgreich zu Installieren:

 - Python > 3.6 (pip & setuptools)
 - ArangoDB bzw. Relationales DB-System
 - GIT
 - build-essential
 - libxml2-dev
 - libxslt1-dev
 - cookiecutter
 - libev-dev


Das Nutzen einen virtuellen Python Umgebung ist empfohlen aber kein muss. 


# Aufsetzen eines Projekt's mit cookiecutter


Wir nuten das OSS-Tool Cookiecutter um ein Basis Projekt für UVC-Reha anzulegen.
Cookiecutter can mit dem Python Tool pip installiert werden.

``` bash 
    pip install cookiecutter
```



# Installation Projekt

Das eigentlich Projekt können wir dann wiefolgt installieren.


``` bash 
cookiecutter https://github.com/novareto/uvc_reha_project 
```


Dieses Projekt ist die Grundlage für den Buildout unserer
neuen Umgebung. Alle Bestandteile des Umgebung können
in der Datei *buildout.cfg* angepasst werden. 

Einstellungen die die Applikation betreffen können in der 
config.ini vorgenommen werden.

*TODO:* Wir müssen noch festlegen ob wir in der config.ini dokumentieren
oder ob wir es hier machen.


