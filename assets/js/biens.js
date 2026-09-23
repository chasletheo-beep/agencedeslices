/* ==========================================================================
   Liste des biens affichés sur le site.
   ⚠️ Les biens ci-dessous sont des EXEMPLES de mise en page :
   remplacez-les par les annonces réelles de l'agence.

   Champs :
   - transaction : "vente" ou "location"
   - type        : "Appartement", "Maison", "Studio", "Local", "Parking"...
   - titre, ville, quartier
   - surface (m²), pieces, chambres
   - prix (€ ; pour une location : loyer mensuel charges comprises)
   - meuble      : true / false (location)
   - photo       : chemin de l'image (ex. "assets/img/biens/rue-saint-michel.jpg")
   - aLaUne      : true pour l'afficher sur la page d'accueil
   ========================================================================== */

window.BIENS = [
  {
    transaction: "vente", type: "Appartement", titre: "Appartement de caractère",
    ville: "Rennes", quartier: "Centre historique",
    surface: 78, pieces: 3, chambres: 2, prix: 339000, photo: "", aLaUne: true
  },
  {
    transaction: "vente", type: "Appartement", titre: "Duplex sous les toits",
    ville: "Rennes", quartier: "Place des Lices",
    surface: 64, pieces: 3, chambres: 2, prix: 289000, photo: "", aLaUne: true
  },
  {
    transaction: "vente", type: "Maison", titre: "Maison de ville avec jardin",
    ville: "Rennes", quartier: "Thabor – Saint-Hélier",
    surface: 132, pieces: 6, chambres: 4, prix: 695000, photo: "", aLaUne: false
  },
  {
    transaction: "vente", type: "Studio", titre: "Studio idéal investisseur",
    ville: "Rennes", quartier: "Hoche",
    surface: 21, pieces: 1, chambres: 0, prix: 119000, photo: "", aLaUne: false
  },
  {
    transaction: "location", type: "Appartement", titre: "T2 meublé lumineux",
    ville: "Rennes", quartier: "Rue de Saint-Malo",
    surface: 42, pieces: 2, chambres: 1, prix: 780, meuble: true, photo: "", aLaUne: true
  },
  {
    transaction: "location", type: "Studio", titre: "Studio étudiant meublé",
    ville: "Rennes", quartier: "Centre-ville",
    surface: 19, pieces: 1, chambres: 0, prix: 520, meuble: true, photo: "", aLaUne: false
  },
  {
    transaction: "location", type: "Appartement", titre: "T3 dans immeuble ancien",
    ville: "Rennes", quartier: "Sainte-Anne",
    surface: 68, pieces: 3, chambres: 2, prix: 1050, meuble: false, photo: "", aLaUne: false
  }
];
