# README

## Présentation

Le présent dossier contient l'ensemble des livrables attendus pour le projet 6 du parcours DA Python d'Openclassrooms, à savoir :

- le dossier de conception technique
- le diagramme de classes
- le diagramme ER
- le diagramme de composants
- le diagramme de déploiement
- le script SQL permettant de créer la base de données (PostgreSQL)
- le script `pop_db.py` qui permet de peupler la base avec des valeurs aléatoires (si applicable)
- un dump de la base utilisée en exemple pour la présentation

## Déploiement de la base

La solution la plus simple pour déployer la base est de charger entièrement le fichier `OCP6.dump` dans PostgreSQL. Je vous fournis néanmoins les scripts ayant permis la création de cette base.

Pour créer "manuellement" une base de données, il vous faudra :
1. Exécuter `OCP6.sql` dans la base de données souhaitée (PostgreSQL).

2. Placer les fichiers `Pipfile`, `Pipfile.lock` et `pop_db.py` dans un même dossier

3. Définir les variables d'environnement requises, à savoir
    ```bash
    host="Nom de la machine hôte de PostgreSQL"
    user="Nom de l'utilisateur de la base"
    password="Mot de passe associé"
    dbname="Nom de la base à employer"
    ```
Elles peuvent naturellement être déclarées dans un fichier `.env` dans le dossier du script.

4. Lancer le script `pop_db.py` qui permet l'alimentation de la base. Pour ce faire,, créer un environnement virtuel, définir les variables d'environnement utiles au déploiement et lancer le script
    ```bash
    pipenv install
    pipenv run python pop_db.py
    ```
Le script `pop_db.py` prend en argument l'option `--size` (ou `-s`) permettant de définir le nombre d'enregistrements aléatoires souhaités. La valeur par défaut est 10 et la valeur utilisée pour générer la base de tests est 250.
