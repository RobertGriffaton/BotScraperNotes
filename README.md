Bot Discord - Surveillance automatique des notes (etudnotes)

📌 Présentation du projet

Ce projet est un bot Discord écrit en Python qui automatise le scraping des notes à partir de la plateforme universitaire etudnotes. Le bot surveille régulièrement l'apparition de nouvelles notes et avertit automatiquement les utilisateurs sur un serveur Discord spécifique dès leur publication.

🔍 Fonctionnalités principales

Scraping automatique :

Récupère périodiquement les nouvelles notes publiées sur le site etudnotes.

Utilise Selenium pour gérer le scraping dynamique nécessitant l'exécution JavaScript.

Notifications Discord :

Envoie automatiquement un message Discord à chaque nouvelle note détectée.

Fournit une commande Discord personnalisée !notes pour afficher toutes les notes actuelles.

Persistance des données :

Conserve les notes connues dans un fichier JSON (notes_connues.json) pour éviter les notifications répétées.

🛠️ Technologies utilisées

Python

Discord.py (bibliothèque officielle Discord en Python)

Selenium WebDriver (scraping web avec gestion JavaScript)
