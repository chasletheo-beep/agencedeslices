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

## Outil interne : Carnet de prospection + Agent IA (`/prospection/`)
En plus du site public ci-dessus, `prospection/index.html` est un **outil interne** (pas
un site vitrine) pour l'équipe commerciale : un carnet de prospection des entreprises
rennaises (locataires ou propriétaires de bureaux), avec pour chacune un suivi de son
« cycle de vie » dans ses locaux (installée, signal de changement, recherche de locaux,
négociation, achat, départ confirmé, locaux libérés), les échéances de bail, un score
d'opportunité, une carte, et un **Agent IA** qui fait le lien entre le terrain et les
données.

**Agent IA — comment ça marche :**
- Un commercial note (au clavier ou à la voix) ce qu'il a vu/appris sur le terrain
  (« Rendez-vous avec X, ils cherchent 300m² secteur Alma d'ici 6 mois… »).
- L'agent retrouve la fiche correspondante (entreprise ou contact) et propose une mise à
  jour (statut, cycle de vie, relance, signaux d'opportunité, résumé ajouté à l'historique).
  **Rien n'est jamais écrit sans validation humaine** — l'utilisateur relit, corrige la
  fiche associée si besoin, et valide.
- Sans configuration : extraction par mots-clés, 100 % hors-ligne et gratuite.
- Avec une clé API Claude (console.anthropic.com), saisie une seule fois dans
  « Réglages » de l'onglet Agent IA : l'extraction comprend le langage libre. La clé est
  stockée uniquement dans le navigateur de la personne qui l'a saisie (localStorage) et
  n'est envoyée qu'à `api.anthropic.com` — jamais commitée dans ce dépôt.
- Un onglet « Poser une question » permet d'interroger les données (baux proches,
  relances en retard, entreprises en mouvement, meilleurs scores), en local ou via l'IA.

**Stockage des données :** comme pour le reste de l'outil, par défaut tout reste dans le
navigateur (localStorage). Pour une synchro multi-appareils/équipe, renseigner
`SUPABASE_URL` / `SUPABASE_ANON_KEY` en haut du fichier (compte Supabase gratuit,
table `carnet_kv`).

**⚠️ Confidentialité.** Cette page contient des données commerciales sensibles
(entreprises, décideurs, échéances de bail). Elle est exclue de l'indexation
(`robots.txt`, balise `noindex`) mais reste accessible à quiconque connaît son URL sur un
hébergement statique classique. Pour une vraie protection, activer une protection par
mot de passe côté hébergeur (ex. Netlify password protection / Vercel Password
Protection), ou la déployer sur un sous-domaine non public / un accès restreint par IP.
