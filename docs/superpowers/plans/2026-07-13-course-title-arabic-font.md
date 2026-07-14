# Beginner-Friendly Arabic Course Titles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Afficher les trois titres arabes ciblés avec une Naskh régulière, aérée et lisible pour débutants.

**Architecture:** Ajouter une règle typographique strictement limitée à `.course-tile h3`, `#courseTitle` et `#moduleTitle`. Conserver taille, couleur, contenu et tous autres composants.

**Tech Stack:** CSS, Python `unittest`, Playwright Chromium local.

## Global Constraints

- Utiliser `Noto Naskh Arabic`, déjà chargée par `site/index.html`, au poids `400`.
- Utiliser `line-height: 1.55`.
- Ne modifier aucun autre sélecteur, contenu ou fichier de données.
- Préfixer toute commande shell avec `rtk`.
- Projet sans dépôt Git : aucun commit possible.

---

### Task 1: Typographie ciblée des titres arabes

**Files:**
- Create: `tests/test_site_typography.py`
- Modify: `site/assets/app.css:471-475`
- Test: `tests/test_site_typography.py`

**Interfaces:**
- Consumes: variable CSS `--font-ar` définie dans `site/assets/app.css` et police chargée dans `site/index.html`.
- Produces: règle CSS commune aux sélecteurs `.course-tile h3`, `#courseTitle`, `#moduleTitle`.

- [x] **Step 1: Écrire test de régression en échec**

```python
import re
import unittest
from pathlib import Path


CSS = (Path(__file__).resolve().parents[1] / "site/assets/app.css").read_text(encoding="utf-8")


class SiteTypographyTest(unittest.TestCase):
    def test_beginner_arabic_title_typography_is_scoped(self) -> None:
        match = re.search(
            r"\.course-tile h3,\s*#courseTitle,\s*#moduleTitle\s*\{(?P<body>[^}]*)\}",
            CSS,
        )
        self.assertIsNotNone(match)
        body = match.group("body")
        self.assertIn("font-family: var(--font-ar);", body)
        self.assertIn("font-weight: 400;", body)
        self.assertIn("line-height: 1.55;", body)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Vérifier échec initial**

Run: `rtk proxy python3 -m unittest tests.test_site_typography -v`

Expected: `FAIL`, car règle commune absente.

- [x] **Step 3: Ajouter implémentation CSS minimale**

Après règle existante `.course-tile h3`, ajouter :

```css
.course-tile h3,
#courseTitle,
#moduleTitle {
  font-family: var(--font-ar);
  font-weight: 400;
  line-height: 1.55;
}
```

- [x] **Step 4: Vérifier test ciblé et suite Python**

Run: `rtk proxy python3 -m unittest tests.test_site_typography -v`

Expected: `OK`, 1 test vert.

Run: `rtk proxy python3 -m unittest discover`

Expected: `OK`, 64 tests verts.

- [x] **Step 5: Vérifier navigateur**

Run serveur dans une session dédiée :

```bash
rtk proxy python3 -m http.server 8766
```

Run suite UI dans une seconde session :

```bash
rtk proxy npx --yes -p @playwright/test@latest bash -lc 'BIN_DIR=$(dirname "$(which playwright)"); export NODE_PATH=$(dirname "$BIN_DIR"); playwright test tests/ui_quiz.spec.js tests/ui_resources.spec.js tests/ui_transcript_race.spec.js tests/ui_ajroumiya_course.spec.js tests/ui_course_quality.spec.js --browser=chromium --reporter=line'
```

Inspecter `http://127.0.0.1:8766/site/` en clair puis sombre. Sur première carte, puis après ouverture du cours et du premier module, vérifier styles calculés de `.course-tile h3`, `#courseTitle`, `#moduleTitle` : famille contenant `Noto Naskh Arabic`, poids `400`, ratio interligne/taille proche de `1.55`.

Expected: suite UI verte; titres lisibles en clair/sombre; aucune erreur console. Arrêter serveur et confirmer que `rtk proxy curl --max-time 2 http://127.0.0.1:8766/site/` échoue avec code `7`.

## Résultat d'exécution

- TDD : test ciblé observé rouge, puis vert.
- Python : 66/66 verts après ajout des tests de cache et de titre module.
- Playwright Chromium : 18/18 verts.
- Styles calculés : famille `Noto Naskh Arabic`, poids `400`, ratio interligne/taille `1.55` sur les trois sélecteurs.
- Rendu clair/sombre contrôlé; zéro erreur console, zéro overlay.
- Serveur arrêté; connexion `8766` refusée avec code `7`.

### Correctif après retour visuel

La capture utilisateur montrait encore ancien poids `700`, tandis que reproduction locale étroite calculait déjà `400`. Cause : URL CSS inchangée, donc ancien asset conservable en cache. `site/index.html` référence maintenant `assets/app.css?v=20260713-title-font`; test d'intégrité des assets ignore correctement query string via `urlsplit`. Contrôle post-correctif : Playwright Ajroumiya 1/1 vert, nouvelle URL chargée, poids calculé `400`, zéro erreur console.

### Extension validée : titres des cartes modules

L'inspecteur utilisateur a confirmé `.lesson-main strong` comme cible : `15px Inter`, poids `600`. Style attendu : `Noto Naskh Arabic`, `18px`, poids `400`, interligne `1.5`. Nouvelle version d'asset requise pour éviter ancien CSS en cache.

Contrôle final : style calculé `18px`, poids `400`, interligne `27px`, nouvelle URL CSS chargée, zéro erreur console; Playwright Ajroumiya 1/1 vert; serveur arrêté.

### Extension validée : titres plus grands

Augmenter cartes cours de `20px` à `22px` et cartes modules de `18px` à `20px`, sans modifier les en-têtes ouverts `#courseTitle` et `#moduleTitle`. Renouveler version CSS.

Contrôle final : Python 67/67; styles calculés cours `22px/400/34.1px`, modules `20px/400/30px`; captures contrôlées; zéro erreur console; serveur arrêté.

### Ajustement validé : 26px

Porter cartes cours et cartes modules à `26px`, poids `400`; renouveler version CSS.

Contrôle final : Python 67/67; tailles calculées `26px`, poids `400`; aucune coupure horizontale; captures contrôlées; zéro erreur console; serveur arrêté.
