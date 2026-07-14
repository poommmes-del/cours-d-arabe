# Conception — trois corrections prioritaires

## Objectif

Corriger trois défauts démontrés sans refonte ni nouvelle dépendance :

1. empêcher une réponse de transcription obsolète d'écraser la leçon active ;
2. empêcher une exécution partielle du compresseur de supprimer les autres entrées du manifeste audio ;
3. rendre le test de taille de police compatible avec une taille supérieure au minimum pédagogique.

## Contraintes

- Usage local personnel.
- Aucun changement de format pour `catalog.json`, les inventaires ou les fichiers audio.
- Aucun téléchargement, appel API ou réencodage pendant les tests.
- Données actuelles inchangées : 14 cours et 792 leçons.
- Tests ajoutés avant code de production et vus en échec pour la cause attendue.

## 1. Course de transcription

### Problème

`renderActiveLesson()` peut lancer plusieurs appels concurrents à
`loadAndRenderTranscript()`. Une réponse ancienne peut finir après la réponse
de la nouvelle leçon et remplacer son texte et ses segments.

### Solution retenue

Ajouter un compteur monotone de rendu de transcription dans l'état frontend.
Chaque appel capture sa génération. Après le `await`, succès et erreur ne
modifient le DOM que si cette génération reste la plus récente.

Cette solution est préférée à `AbortController` : changement plus petit,
compatible avec le cache actuel, et protection correcte même si une requête ne
peut plus être annulée.

### Test

Créer un test avec deux chargements contrôlés :

1. démarrer le chargement A ;
2. démarrer le chargement B ;
3. terminer B ;
4. terminer A ;
5. vérifier que texte et segments de B restent affichés.

Le test doit échouer sur code actuel avec contenu A affiché.

## 2. Manifeste audio partiel

### Problème

`main()` filtre les travaux via `--identifier` ou `--limit`, puis
`write_manifest()` ouvre `manifest.tsv` en écriture et ne conserve que les
travaux exécutés.

### Solution retenue

Séparer calcul des lignes finales et sérialisation :

- exécution complète sans filtre : remplacer manifeste par résultats complets ;
- `--identifier` sans `--limit` : remplacer toutes les lignes des identifiants ciblés, conserver les autres ;
- `--limit` : mettre à jour uniquement les clés `(identifier, name)` traitées, conserver toutes les autres ;
- manifeste absent : écrire seulement résultats disponibles ;
- sortie toujours triée par identifiant puis ordre naturel du nom.

Écriture atomique vers fichier temporaire situé dans même dossier, puis
`os.replace()`, afin de ne pas laisser manifeste tronqué.

### Tests

Utiliser `TemporaryDirectory` :

- sous-ensemble avec `--limit` conserve entrées non traitées ;
- exécution par identifiant remplace anciennes lignes du cours ciblé et conserve autres cours ;
- exécution complète supprime lignes obsolètes ;
- ordre et en-tête restent déterministes.

## 3. Contrat CSS

### Problème

Test exige exactement `23px` et `22px`, tandis que CSS courant utilise
`28px` pour lecture arabe. Exigence fonctionnelle est une taille minimale,
pas une valeur exacte.

### Solution retenue

Extraire valeur `font-size` des blocs `.markdown-body` et
`.transcript-text`, puis vérifier :

- Markdown : au moins 23 px ;
- transcription : au moins 22 px.

CSS reste à 28 px.

## Validation finale

- suite `python3 -m unittest discover -v` entièrement verte ;
- tests race et manifeste passent après avoir échoué avant correction ;
- `node --check site/assets/app.js` ;
- `python3 -m py_compile` sur outils modifiés ;
- tests Playwright existants passent avec serveur loopback ;
- reconstruction mémoire du catalogue égale fichier courant, 14 cours et 792 leçons ;
- aucun fichier audio, transcription, PDF ou catalogue réécrit.

## Hors périmètre

- refonte serveur HTTP ou support `Range` ;
- arrêt audio au retour accueil ;
- portabilité des symlinks et chemins absolus ;
- manifests de dépendances, CI, accessibilité et autres constats de review.
