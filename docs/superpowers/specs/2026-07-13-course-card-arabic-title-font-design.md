# Police arabe des titres principaux

Date : 2026-07-13

## But

Rendre les titres arabes des cartes, du cours ouvert et du module actif plus lisibles pour un débutant. Le rendu actuel hérite de `Inter, system-ui, sans-serif` avec un poids `700`; Inter ne fournissant pas les glyphes arabes, le navigateur emploie un fallback système dont le gras paraît incliné et compact.

## Périmètre

- Modifier `.course-tile h3`, `#courseTitle`, `#moduleTitle` et les titres des cartes modules `.lesson-main strong`.
- Utiliser `Noto Naskh Arabic`, déjà chargée par la page, au poids `400`.
- Porter l'interligne à `1.55` pour dégager lettres et voyelles.
- Pour `.lesson-main strong`, utiliser `26px` et un interligne `1.5` au lieu de `15px Inter` poids `600`.
- Porter les titres des cartes cours `.course-tile h3` de `20px` à `26px`.
- Ne modifier ni contenu, ni taille, ni couleur, ni autres titres.
- Versionner l'URL de `app.css` afin que les navigateurs ne conservent pas l'ancien poids `700` en cache.

## Hors périmètre

La même cascade de famille et de poids existe aussi sur `.eyebrow` à une taille différente. Cet élément reste inchangé.

## Vérification

- Contrôle CSS ciblé des sélecteurs `.course-tile h3`, `#courseTitle` et `#moduleTitle`.
- Test syntaxique et suite UI existante.
- Vérification navigateur des cartes en thème clair et sombre, sans erreur console.
- Vérification que feuille chargée porte bien query string de version.
