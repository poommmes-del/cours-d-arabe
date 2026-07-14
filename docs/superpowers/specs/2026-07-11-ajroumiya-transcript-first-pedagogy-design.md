# Conception — Ajroumiya fondée sur la transcription

Date : 2026-07-11  
Statut : conception validée en conversation, soumise à revue écrite finale  
Projet : usage local personnel, sans dépôt Git

## Objectif

Réécrire entièrement le cours et les questionnaires de `ajroumiya` pour en faire un parcours extrêmement pédagogique, fidèle en premier lieu aux 30 cours audio et à leurs transcriptions. Le matn sert à fixer les formulations canoniques; les charh servent seulement à corriger ou éclaircir. Après livraison, l’utilisateur vérifie Ajroumiya avant toute généralisation aux treize autres cours.

## Constat actuel

- Le corpus Ajroumiya contient 30 audios, environ 102 000 mots transcrits et une progression réelle du professeur.
- Le cours actuel est le meilleur parcours du projet, mais il reste organisé comme une synthèse générale et ne conserve pas précisément la progression, les explications et les exemples de chaque passage audio.
- Les transcriptions Deepgram contiennent des erreurs malgré une confiance moyenne élevée. Elles mêlent enseignement, répétitions, questions d’élèves et informations administratives.
- Le site sait déjà afficher des modules Markdown et leurs questionnaires. Aucun changement d’interface n’est requis.

## Périmètre

### Inclus

- `ajroumiya` uniquement;
- analyse des 30 transcriptions et, si nécessaire, écoute ciblée des passages ambigus;
- segmentation sémantique en environ 25 à 35 modules;
- rédaction complète en arabe;
- 8 à 10 questions progressives par module;
- provenance interne horodatée et invisible dans le site;
- validation par le matn et les charh locaux;
- assemblage du cours, régénération du catalogue et vérification navigateur.

### Exclu

- modification des treize autres cours;
- modification des audios, transcriptions, PDF, fichiers Shamela ou manifeste audio;
- changement d’interface ou nouveau système de notation;
- affichage des minutages ou références dans le cours public;
- ajout de contenu grammatical qui n’est pas réellement couvert par les audios Ajroumiya;
- appel réseau, téléchargement ou nouvelle transcription.

## Décisions validées

- Langue : arabe uniquement.
- Organisation : modules thématiques, pas un module par fichier audio et pas un découpage uniforme.
- Granularité : apprentissage de 15 à 25 minutes par module, cible de 25 à 35 modules.
- Sources : minutages et références conservés dans des métadonnées internes, invisibles à l’apprenant.
- Questionnaires : 8 à 10 questions progressives par module.
- Livraison : Ajroumiya complet, puis validation humaine avant travail sur les autres cours.
- Progression locale : les nouveaux identifiants de modules réinitialisent la progression Ajroumiya. Les autres cours restent inchangés.

## Hiérarchie des sources

### 1. Audio et transcription — source principale

Ils déterminent :

- l’ordre réellement enseigné;
- la portée du cours;
- les explications et analogies du professeur;
- les exemples réellement commentés;
- les erreurs fréquentes signalées;
- les questions et difficultés apparues pendant le cours.

La transcription n’est pas considérée comme texte canonique. Une confiance Deepgram élevée ne prouve pas l’exactitude grammaticale.

### 2. Matn — source canonique

Le matn sert à :

- rétablir la formulation exacte des définitions et règles;
- corriger les mots techniques mal reconnus;
- vocaliser les citations et exemples;
- vérifier qu’une synthèse n’altère pas le sens.

Le matn ne doit pas élargir le périmètre au-delà de ce que les audios enseignent.

### 3. Charh — complément

Les charh locaux servent à :

- lever une ambiguïté;
- confirmer une analyse grammaticale;
- préciser une condition ou exception effectivement évoquée dans l’audio;
- corriger une transcription incertaine.

Ils ne doivent pas introduire un chapitre absent de l’enseignement audio. Toute correction importante reste documentée dans les métadonnées internes.

## Architecture des fichiers

### Sauvegarde

Le cours actuel est conservé une seule fois sous :

`cours-pedagogiques/ajroumiya/cours.before-transcript-first.md`

Ce fichier n’est pas lu par le catalogue et ne doit jamais être écrasé par une exécution ultérieure.

### Cartographie interne

`cours-pedagogiques/ajroumiya/source-map.json`

Structure conceptuelle :

```json
{
  "schema_version": 1,
  "course_id": "ajroumiya",
  "modules": [
    {
      "id": "ajroumiya-module-01-منزلة-الآجرومية-وطريقة-دراستها",
      "title": "منزلة الآجرومية وطريقة دراستها",
      "estimated_study_minutes": 20,
      "audio_spans": [
        {
          "lesson_id": "001-شرح المقدمة الآجرومية للأستاذ محمود الشافعي (1)",
          "start_seconds": 65,
          "end_seconds": 695,
          "evidence": "الآجرومية متن صغير الحجم عظيم النفع يجمع الأصول النحوية للمبتدئ"
        }
      ],
      "matn_refs": ["livres/shamela/ajroumiya/matn/11371/book.md"],
      "charh_refs": ["livres/shamela/ajroumiya/sharh/21509/book.md"],
      "verification": {
        "transcript": "verified",
        "grammar": "verified",
        "arabic": "verified",
        "pedagogy": "verified"
      }
    }
  ],
  "excluded_spans": [
    {
      "lesson_id": "001-شرح المقدمة الآجرومية للأستاذ محمود الشافعي (1)",
      "start_seconds": 945,
      "end_seconds": 1405,
      "reason": "informations administratives sans contenu grammatical"
    }
  ]
}
```

Contraintes :

- chaque plage temporelle appartient à un audio existant;
- chaque module déclare `estimated_study_minutes` entre 15 et 25;
- `0 <= start_seconds < end_seconds <= durée audio`;
- un module peut référencer plusieurs plages et une plage peut contribuer à plusieurs activités lorsque cela est justifié;
- `evidence` reste court et sert à retrouver le passage, pas à dupliquer toute la transcription;
- chacune des 30 leçons possède au moins une plage rattachée à un module ou une exclusion motivée; aucune leçon ne disparaît silencieusement;
- un module non entièrement vérifié ne peut pas entrer dans `cours.md`.

### Modules sources

Les fragments vivent dans `cours-pedagogiques/ajroumiya/modules/`. Leur nom utilise l’index à deux chiffres puis le slug arabe du titre, par exemple `01-منزلة-الآجرومية.md`.

Chaque fichier contient exactement un module et ses questions. Les fichiers séparés permettent rédaction parallèle sans collision.

Contrat Markdown :

- première ligne : `## عنوان الوحدة`;
- sections pédagogiques : titres `###` dans l’ordre du gabarit;
- questionnaire : titre exact `### أسئلة التحقق`;
- chaque question : `1. نص السؤال`;
- réponse immédiatement dessous : `- الجواب: نص الجواب`;
- aucune matière avant le premier titre `##`, afin d’éviter la création automatique d’un module `Accueil` et de questions fallback.

### Assemblage public

`cours-pedagogiques/ajroumiya/cours.md`

Il est assemblé de façon déterministe selon le préfixe numérique des modules. Il reste compatible avec `load_pedagogical_modules()` et le rendu actuel du site.

L’outil prévu est `outils/build_pedagogical_course.py --identifier ajroumiya`. Il valide `source-map.json`, les fragments Markdown et les questionnaires avant d’écrire `cours.md`. Le fichier final commence directement par le premier titre `##`; les 25 à 35 modules correspondent donc exactement aux 25 à 35 titres `##`.

## Segmentation pédagogique

Le découpage suit les changements réels de `باب`, `مسألة`, définition, condition, exemple ou application. Il ne suit ni le nombre de fichiers ni un quota uniforme.

Règles :

- une introduction administrative n’est pas un module;
- une répétition est fusionnée avec l’explication la plus claire;
- deux audios peuvent alimenter un seul module;
- un audio peut fournir plusieurs modules;
- un sujet long est découpé selon les compétences à maîtriser;
- la progression respecte prérequis et ordre du professeur;
- chaque module vise une compétence observable, pas un simple titre de chapitre.

## Gabarit obligatoire d’un module

Chaque module utilise ces sections arabes, adaptées au sujet :

1. `الهدف` — compétence observable;
2. `قبل أن تبدأ` — prérequis et récupération active;
3. `شرح المسألة` — explication arabe simple fidèle au professeur;
4. `القاعدة` — formulation précise validée par le matn;
5. `لماذا؟` — logique grammaticale derrière la règle;
6. `أمثلة متدرجة` — exemple simple, intermédiaire et cas piégeux;
7. `تحليل خطوة خطوة` — raisonnement grammatical ou iʿrāb complet;
8. `خطأ شائع` — erreur probable, cause et correction;
9. `تدريب موجه` — application avec indices;
10. `تدريب مستقل` — application sans indices;
11. `خلاصة للحفظ` — synthèse courte;
12. `مراجعة تراكمية` — lien actif avec modules antérieurs;
13. `أسئلة التحقق` — questionnaire explicite.

Les exemples, citations et phrases analysées sont vocalisés. La prose explicative reste en arabe clair sans vocalisation intégrale artificielle.

Dans le premier module seulement, `تشخيص قبلي` remplace `مراجعة تراكمية`. Le validateur accepte cette unique alternative.

## Contrat des questionnaires

Chaque module contient 8 à 10 questions et réponses explicites. Aucun fallback générique ne doit être nécessaire.

Répartition attendue :

- 1 à 2 questions de rappel;
- 1 question de compréhension ou reformulation;
- 1 question de classement;
- 1 à 2 applications;
- 1 iʿrāb ou analyse progressive;
- 1 correction d’erreur;
- 1 exemple nouveau ou transfert;
- 1 révision cumulative à partir du deuxième module.

Le premier module peut remplacer la révision cumulative par une question diagnostique.

Chaque réponse :

- donne la solution;
- explique le raisonnement;
- mentionne fonction, حكم, علامة et سبب quand le sujet l’exige;
- distingue réponse fausse plausible et réponse correcte;
- évite toute consigne vide telle que «انظر إلى المثال ثم طبّق القاعدة».

## Orchestration des subagents

Le travail utilise des vagues de trois agents maximum.

### Vague 1 — dossiers sources

- Agent A : audios 1 à 10;
- Agent B : audios 11 à 20;
- Agent C : audios 21 à 30.

Chaque agent retourne thèmes, bornes temporelles, définitions, exemples, erreurs fréquentes, répétitions et incertitudes. Aucun agent ne rédige encore le cours final.

### Vague 2 — architecture

Un agent architecte fusionne les dossiers, élimine doublons, ordonne prérequis et propose les 25 à 35 modules. Une revue indépendante vérifie la couverture complète et l’absence de découpage arbitraire.

### Vague 3 — rédaction

Les modules sont distribués par fichiers disjoints. Chaque rédacteur utilise uniquement les preuves affectées et respecte le gabarit.

### Vague 4 — revues spécialisées

- fidélité audio et provenance;
- correction grammaticale contre matn/charh;
- pédagogie et qualité des questionnaires;
- arabe, terminologie et vocalisation.

Les constats Critical ou Important sont corrigés puis revus. Aucun agent ne modifie simultanément le même fichier.

## Politique des erreurs et ambiguïtés

- ASR ambigu : écouter le passage ciblé, puis consulter matn et charh.
- Terme grammatical incertain : ne jamais deviner.
- Désaccord non résolu : statut `needs_review`; module exclu de l’assemblage.
- Digression administrative : exclue.
- Question d’élève utile : intégrée comme erreur fréquente ou activité si elle sert directement la compétence.
- Répétition : conserver meilleure explication et enregistrer autres plages seulement dans la cartographie.
- Correction canonique : publier la règle correcte; conserver justification et source dans `source-map.json`.

## Assemblage et intégration

L’assemblage :

1. trie les modules par préfixe numérique;
2. vérifie présence de toutes les sections obligatoires;
3. vérifie 8 à 10 questions parsables;
4. refuse tout module dont la provenance n’est pas entièrement vérifiée;
5. génère `cours.md` sans afficher métadonnées internes;
6. reconstruit `site/data/catalog.json` avec outils existants.

Aucune modification d’interface. Le catalogue conserve 14 cours et 792 leçons; seuls contenu, modules et questions Ajroumiya changent.

## Validation automatisée

### Structure et provenance

- nombre de modules entre 25 et 35;
- identifiants et titres uniques;
- toutes sections obligatoires présentes;
- chaque module possède au moins une plage audio valide;
- les 30 leçons sont couvertes ou disposent d’exclusions motivées;
- toutes vérifications de provenance au statut `verified`;
- aucune référence vers fichier absent;
- aucun `request_id`, métadonnée Deepgram ou information administrative dans le cours public.

Ces contrôles sont ajoutés dans `tests/test_ajroumiya_pedagogy.py`.

### Pédagogie et questionnaires

- 8 à 10 questions parsées par module;
- absence des réponses génériques anciennes;
- présence d’application, correction d’erreur et transfert;
- révision cumulative à partir du deuxième module;
- exemples arabes et réponses non vides;
- aucune duplication importante entre questionnaires;
- difficulté croissante contrôlée sur début, milieu et fin du cours.

### Intégration

- suite Python complète;
- compilation Python et vérification JavaScript;
- catalogue reconstruit en mémoire puis comparé au fichier généré;
- 14 cours et 792 leçons conservés;
- test navigateur sur module initial, médian et final;
- ouverture/fermeture des réponses du quiz;
- progression locale fonctionnelle avec nouveaux identifiants;
- serveur loopback arrêté après vérification.

Le parcours navigateur dédié est ajouté dans `tests/ui_ajroumiya_course.spec.js`.

### Intégrité des données

Les hashes ou empreintes des éléments suivants sont capturés avant et après :

- `audios-opus/manifest.tsv`;
- audios `.opus`;
- transcriptions;
- PDF et exports Shamela.

Ils doivent rester identiques. `site/data/catalog.json` change uniquement pour refléter les nouveaux modules et questions Ajroumiya, sans changer nombres de cours ou leçons.

## Critères d’acceptation

La livraison Ajroumiya est acceptable lorsque :

- 25 à 35 modules arabes complets couvrent l’enseignement réel des 30 audios;
- chaque module est traçable en interne vers audio/transcription et validé par sources complémentaires lorsque nécessaire;
- le cours suit le gabarit pédagogique validé;
- chaque module contient 8 à 10 questions variées avec réponses raisonnées;
- aucun sujet non enseigné n’est inventé;
- aucune erreur ASR connue n’est propagée;
- les revues fidélité, grammaire, pédagogie et langue n’ont aucun constat Critical ou Important ouvert;
- tous tests passent;
- données métier restent intactes;
- l’utilisateur peut examiner Ajroumiya complet avant toute généralisation.

## Gate après livraison

Aucun autre cours n’est réécrit automatiquement. L’utilisateur vérifie Ajroumiya, demande les corrections éventuelles, puis valide ou refuse la généralisation du procédé.
