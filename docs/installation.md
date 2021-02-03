* Installation


* Voraussetzung

Folgende Voraussetzung müssen auf Betriebssystemseite gegeben sein um UVC-Reha erfolgreich zu Installieren:

 - Python > 3.6 (pip & setuptools)
 - ArangoDB bzw. Relationales DB-System
 - GIT
 - build-essential
 - libxml2-dev
 - libxslt1-dev

Das Nutzen einen virtuellen Python Umgebung ist empfohlen aber kein muss. 

* Cookiecutter

Wir nuten das OSS-Tool Cookiecutter um ein Basis Projekt für UVC-Reha anzulegen.
Cookiecutter can mit dem Python Tool pip installiert werden.

``` bash 
   pip install cookiecutter
'''



* Installation Projekt

Das eigentlich Projekt können wir dann wiefolgt Installieren.


``` bash 
cookiecutter https://github.com/novareto/uvc_reha_project 
```



``` python linenums="1"
def bubble_sort(items):
    for i in range(len(items)):
        for j in range(len(items) - 1 - i):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
```


