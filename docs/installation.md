# Voraussetzung

Folgende Voraussetzung müssen auf Betriebssystemseite gegeben sein um UVC-Reha erfolgreich zu Installieren:

 - Python > 3.8 (pip & setuptools)
 - ArangoDB bzw. Relationales DB-System
 - GIT
 - build-essential
 - libxml2-dev
 - libxslt1-dev
 - cookiecutter
 - libev-dev
 - python-virtualenv


```bash
   apt-get install build-essential libxml2-dev libxslt1-dev libev-dev libev-dev python3-virtualenv git 
```


Das Nutzen einen virtuellen Python Umgebung ist empfohlen aber kein muss. 


# Installation Virtualenv

``` bash
virtualenv --python=/usr/bin/python3.8 portal
```


# Aufsetzen eines Projekt's mit cookiecutter


Wir nuten das OSS-Tool Cookiecutter um ein Basis Projekt für UVC-Reha anzulegen.
Cookiecutter can mit dem Python Tool pip installiert werden. Bitte achtet darauf
nun mit der richtigen Python Umgebung zu arbeiten. 
Ich gehe hierzu in meine virtuelle Umgebung bzw. aktiviere die Virtualenv.
Bevor wir das cookiecutter Projekt installieren führe ich zunächst einen upgrade auf pip und setuptools aus.


``` bash 
bin/pip install --upgrade pip==21.0
bin/pip install --upgrade setuptools==51.1.0
bin/pip install wheel
bin/pip install cookiecutter
```



# Installation Projekt

Das eigentlich Projekt können wir dann wiefolgt installieren.


``` bash 
bin/cookiecutter https://github.com/novareto/uvc_reha_project 
```

Anschließend können wir in das Verzeichnis wechseln, und dann können wir 
zc.buildout erstellen Hierzu verwenden wir das mitgelieferte default script


``` 
bin/python bootstrap-buildout.py --allow-site-packages
bin/buildout
```



Dieses Projekt ist die Grundlage für den Buildout unserer
neuen Umgebung. Alle Bestandteile des Umgebung können
in der Datei *buildout.cfg* angepasst werden. 

Einstellungen die die Applikation betreffen können in der 
config.ini vorgenommen werden.

*TODO:* Wir müssen noch festlegen ob wir in der config.ini dokumentieren
oder ob wir es hier machen.

# ArangoDB

Informationen für die ArangoDB kann über folgende Seite aufgerufen werden:

[Installation ArangoDB](https://www.arangodb.com/download-major/ubuntu/)



# Schlüssel für Push Notifications

``` bash
mkdir identities
cd identities
../bin/py ../parts/omelette/py_vapid/main.py
../bin/py ../parts/omelette/py_vapid/main.py --sign claim.json
```



