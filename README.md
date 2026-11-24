# Agence des Lices – Chasle Immobilier

Nouveau site de l'Agence des Lices (Rennes), en HTML/CSS/JS statique, responsive (conçu d'abord pour le mobile).

## Pages
- `index.html` : accueil (recherche rapide, services, biens à la une, l'agence)
- `annonces.html` : annonces vente / location avec filtres
- `vendre.html` : méthode de vente + formulaire d'estimation
- `louer.html` : location & gestion locative
- `contact.html` : coordonnées, horaires, plan, formulaire
- `mentions-legales.html` : mentions légales (champs `[à compléter]`)

## Mettre à jour les annonces
Modifier `assets/js/biens.js`. Les biens actuels sont des **exemples** à remplacer.
Mettre les photos dans `assets/img/biens/` et indiquer leur chemin dans le champ `photo`.

## Formulaires
Le site est statique : les formulaires ouvrent la messagerie du visiteur avec un e-mail
pré-rempli pour contact@agencedeslices.fr. Pour un envoi direct, brancher un service
de formulaires (Formspree, Netlify Forms…) ou un script côté serveur.

## Mise en ligne
Déposer tous les fichiers sur l'hébergement (FTP) ou via GitHub Pages / Netlify.

## Outil interne : Radar DPE (`radar-dpe.html`)
Outil de prospection (non lié dans le menu, `noindex`) : carte des DPE publics de l'ADEME
avec score de priorité, suivi des contacts, tournées terrain et courriers.

- **Recherche** : par commune, code postal, rayon autour d'une adresse ou zone de la carte ;
  filtres étiquette, type, ancienneté du DPE, surface, année, énergie de chauffage.
- **Score de priorité (0–100)** : étiquette, échéance d'interdiction de louer (G 2025, F 2028, E 2034),
  fraîcheur du DPE, surface, audit énergétique obligatoire (maisons), chauffage électrique
  reclassable (coefficient 1,9 depuis 2026), adresses avec plusieurs DPE.
- **Fiche bien** : caractéristiques, alertes réglementaires, estimation indicative (valeur, décote,
  honoraires, travaux), liens Street View / DVF / cadastre / DPE officiel.
- **Suivi** : statuts (à contacter → mandat), notes, relances, favoris ; export CSV.
- **Tournée** : itinéraire optimisé depuis l'agence, ouverture dans Google Maps, feuille de route.
- **Courriers** : modèle personnalisable, impression en lot, passage automatique en « Contacté ».
- **Stats** : répartition des étiquettes, DPE par mois, rues les plus concernées, honoraires potentiels.

Les données de suivi sont enregistrées dans le navigateur (localStorage) : faire des sauvegardes
régulières depuis l'onglet Réglages. Un mode démonstration (données fictives) permet de tester sans connexion.
