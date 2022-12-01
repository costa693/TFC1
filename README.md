# ROAD AI

L'app consiste à simuler un systeme de régulation routiere intelligence grace au computer vision.

* Le systeme doit analyser un flux vidéo d'un traffic routier,
* detecter les objets
* et ensuite prendre une decision reflechie.
* L'app doit aussi afficher en temps réel le flux vidéo ainsi que les objets detectés.
* L'app doit simuler les états ROUGE JAUNE VERT en arretant/demarrant le flux vidéo (Pause, Unpause)


## Préparer le remote ssh to Github

* Ouvrir le projet avec git bash
* Démarrer l'agent ssh

```
-$ eval "$(ssh-agent -s)"
```

* Charger la clé github dans l'agent ssh

```
-$ ssh-add ~/.ssh/github
```

## Travailler avec Git

Toujours se rassurer que les modifications ne sont pas faites sur la branche principale ``main``

* Vérifier la branche sur laquelle on se trouve
  * ```
    -$ git branch
    ```
  * La branche actuelle sera précédée du signe ``*``
* Créer une nouvelle branche pour ajouter des modifications
  * ```
    -$ git checkout -b nomDeLaBranche
    ```
  * Cette commande fait deux choses : crée la nouvelle branche et switch sur celle-ci. faites ``git branch`` et vous verrez que vous etes sur la nouvelle branche
* Enregistrer les modifications effectuée sur la nouvelle branche en local

```
-$ git add *
-$ git commit -m "message, dites en quoi consiste ces modifications"
```

* Enregistrer les modifications en ligne sur gthub

```
-$ git push origin nomDeLaBranche
```

* Télécharger les modifications qui sont en ligne afin que votre projet en local soit à jour

  ```
  -$ git pull origin nomDeLaBranche
  ```
* Changer de branche

  ```
  -$ git switch nomDeLaBranch
  ```

## Lancer le projet


* Ouvrir le projet avec git bash (vscode)
* Créer un environnement virtuel python

```
python -m venv venv
```

* Activer l'environnement virtuel

  ```
  -$ source venv/bin/activate #ubuntu
  -$ . venv/Scripts/activate #windows
  ```
* Installer les dependances

  ```
  -$ python -m pip install -r requirements.txt
  ```
* Collecter les fichiers statics (y les vidéos des traffic)

```
-$ python manage.py collectstatic
```

* Lancer le projet
  ```
  -$ python manage.py runserver 8000
  ```
