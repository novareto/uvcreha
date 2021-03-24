# Development

## Anlegen eines Addons


``` bash
cookiecutter https://github.com/novareto/uvc_reha_addon.git
```


## Einbinden des Projekts

Nun müssen wir das Projekt in Buildout bekannt machen
Hierzu ergänzen wir das lokale Package in der Sektion develop


```
develop = 
   src/bg.example

[app]
...
eggs
    bg.example
```
