# Explorateur DPE (outil interne)

Une page qui interroge en direct l'open data DPE de l'ADEME (logements existants et tertiaire), avec carte,
liste triable, tableau de bord, recherches clients mises en correspondance, et exports CSV/PDF.

## Lancer l'outil (une seule commande)

```
python3 outils/dpe/serveur_dpe.py
```

Cette commande ouvre http://localhost:8765. Le petit serveur (Python 3, aucune installation) sert la page et relaie les
appels vers l'API ADEME si le navigateur les refuse (CORS). La page essaie d'abord l'appel direct, puis bascule
automatiquement sur le serveur. Si l'API autorise le CORS, on peut aussi ouvrir directement `outils/dpe/index.html`.

## Essayer sans connexion (mode démo)

Ouvrez http://localhost:8765/#demo, ou cliquez « Essayer avec des données d'exemple » quand l'API ne répond pas.
La page génère alors des DPE **fictifs** et des clients d'exemple, et simule l'API (pagination, filtres, limite).

## Vérifier l'API

```
python3 outils/dpe/serveur_dpe.py --test
```

Ce test vérifie le CORS et la présence de tous les champs dans le schéma ADEME. Il lance la recherche « Rennes, maisons,
octobre 2026 » et compare le total annoncé par l'API au nombre de DPE reçus après pagination. Il ouvre aussi un lien
« Rapport ADEME ».

## Bon à savoir
- Au démarrage, la page lit le schéma de chaque jeu ADEME et n'utilise que des champs qui y figurent. La liste
  apparaît en bas de page, sous « Champs ADEME utilisés ».
- Une recherche est limitée à 10 000 DPE. Au-delà, la page propose de réduire la période ou la zone.
- Icônes : Nouveau = DPE de moins de 15 jours (mise en vente ou location probable) ; Passoire = F/G ; ⧉ = doublon
  (même adresse et mêmes valeurs) ; ⚠ = coût supérieur à 50 000 €/an pour moins de 200 m² ; 👤 = clients
  correspondants.
- Les fiches « Recherches clients » sont gardées dans le navigateur. Le bouton « Sauvegarder » produit un fichier
  JSON, que « Importer » recharge sur un autre poste.
