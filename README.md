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

## MES IDÉES

L'app doit simuler les états ROUGE JAUNE VERT en arretant/demarrant le flux vidéo (Pause, Unpause)

1. Simuler les les états ROUGE JAUNE VERT
   Simplement avoir un objet ``FeuDeSignalisation`` pour chaque route, car dans la réalité, il y a toujours un feu pour une route précise.

   Pour permettre un controle adequat du flux vidéo, un objet ``FeuDeSignalisation`` aura un attribut de type ``VideoCameraStreamDetection`` qui fera office de relation avec la classe de controle du flux vidéo.

   Et aussi des methodes ``allumer_rouge(), allumer_jaune(), allumer_vert()`` pour allumer ou eteindre.

   Allumer feu implique Eteindre les 2 autres.

   La fonction ``allumer_rouge()`` doit faire une pause du flux vidéo en appellant ``VideoCameraStreamDetection.pause_stream`` (Cfr point 2)

   La fonction ``allumer_jaune()`` ne change aucun état.

   La fonction ``allumer_vert()`` doit faire un play (unpause) du flux vidéo en appellant ``VideoCameraStreamDetection.unpause_stream`` (Cfr point 2)
2. en arretant/demarrant le flux vidéo (Pause, Unpause)

   Ajouter une fonction ``pause_stream, resume_stream`` à la classe ``VideoCameraStreamDetection`` ce qui permettra d'arreter / demarrer le stream.

   Ces fonctions doivent mettre en attente le ``thread : self.next_trame_thread`` dans l'objectif de mettre en pause le flux vidéo sur la vue, et aussi mettre en attente le ``tread : trame_inference_thread`` dans l'objectif de mettre en pause les inférences afin d'éviter que l'ia puisse analyser plusieurs fois la meme trame.

   [Un exemple pause/unpause Thread](https://topic.alibabacloud.com/a/python-thread-pause-resume-exit-detail-and-example-_python_1_29_20095165.html)
