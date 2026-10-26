# Radar DPE (outil interne)

Une page qui interroge en direct l'open data DPE de l'ADEME (logements existants et tertiaire). Elle est organisée en
quatre onglets :

- **Radar DPE** : filtres, tableau de bord, carte et liste synchronisées, fiche détaillée de chaque DPE (rapport ADEME,
  Google Maps, recherche d'annonces sur les portails avec statut de vérification, entreprises à l'adresse pour le
  tertiaire), exports CSV/PDF.
- **Acquéreurs** : recherches clients (type, secteur, surface, étiquettes, travaux, budget).
- **Correspondances** : DPE × acquéreurs avec un score et ses raisons, export CSV.
- **Suivi** : dossiers de prospection par étape, prochaine action, source de l'information, export CSV/JSON.

Sur téléphone, les onglets passent dans une barre en bas de l'écran et la liste s'affiche en cartes.

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

## Veille automatique

Tant que `serveur_dpe.py` tourne, il interroge l'ADEME toutes les 60 minutes (`--veille-minutes 30` pour changer,
`0` pour arrêter). Il garde dans `veille_dpe.json` les DPE de Rennes Métropole publiés ces 14 derniers jours. Le
panneau « Veille automatique » de la page liste les derniers détectés et marque ceux arrivés depuis votre dernière visite.

## Bon à savoir
- Au démarrage, la page lit le schéma de chaque jeu ADEME et n'utilise que des champs qui y figurent. La liste
  apparaît en bas de page, sous « Champs ADEME utilisés ».
- Une recherche est limitée à 10 000 DPE. Au-delà, la page propose de réduire la période ou la zone.
- Icônes : Nouveau = DPE de moins de 15 jours (mise en vente ou location probable) ; Passoire = F/G ; ⧉ = doublon
  (même adresse et mêmes valeurs) ; ⚠ = coût supérieur à 50 000 €/an pour moins de 200 m² ; 👤 = clients
  correspondants.
- Recherches acquéreurs, vérifications d'annonces et suivi sont gardés dans le navigateur. Les boutons « Sauvegarder »
  produisent un fichier JSON, que « Importer » recharge sur un autre poste.
- L'ADEME ne fournit pas l'identité des propriétaires : notez uniquement des informations obtenues légalement (RGPD).
