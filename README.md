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
