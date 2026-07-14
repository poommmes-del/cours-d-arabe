# Conception - Generalisation transcript-first aux treize cours restants

Date : 2026-07-12  
Statut : approuve par delegation autonome de l'utilisateur  
Projet : usage local personnel, sans depot Git

## Objectif

Reecrire les treize cours restants avec le meme niveau de fidelite et de pedagogie que l'Ajroumiya terminee. Chaque parcours doit etre fonde d'abord sur ses audios et transcriptions locales, puis borne et corrige par les textes locaux disponibles. Le travail s'effectue par vagues de trois cours en parallele, sans checkpoint de validation humaine.

## Ordre obligatoire

L'ordre public reste celui du catalogue :

1. `moutammima`
2. `qatr-nada`
3. `qawaid-i3raab-sa3di`
4. `qawaid-i3raab-zawawi`
5. `mawsil-toullab`
6. `shoudhour-dhahab`
7. `alfiya-nahw`
8. `moulakhas-sarfi`
9. `nadhm-maqsoud`
10. `alfiya-sarf`
11. `laamiya-af3al`
12. `dourous-balagha`
13. `maani-we-bayan`

Les vagues sont :

- vague 1 : cours 1 a 3;
- vague 2 : cours 4 a 6;
- vague 3 : cours 7 a 9;
- vague 4 : cours 10 a 12;
- vague 5 : cours 13.

Une vague peut etre produite en parallele, mais elle n'est publiee dans le catalogue qu'apres validation complete de tous ses cours. La vague suivante ne modifie aucun cours public avant cloture de la vague courante.

## Contraintes globales

- Langue des cours et questionnaires : arabe uniquement.
- Audio et transcription fixent ordre, portee, explications, exemples et difficultes.
- Textes locaux canoniques corrigent les formulations sans elargir artificiellement le programme.
- Provenance, minutages et chemins internes restent invisibles dans le cours public.
- Chaque module conserve les treize sections pedagogiques Ajroumiya.
- Chaque questionnaire contient 8 a 10 questions explicites avec reponses raisonnees.
- Aucun reseau, telechargement, appel API, reencodage ou nouvelle transcription.
- Audios, transcriptions, PDF, Shamela et `audios-opus/manifest.tsv` restent immuables.
- Un cours deja publie et valide devient protege pendant les vagues suivantes.
- Le catalogue garde 14 cours et 792 lecons; seuls les modules et questions des cours de la vague changent.
- Projet non-Git : rapports, baselines et ledgers durables remplacent commits et branches.
- Toutes commandes shell sont prefixees par `rtk`.
- Edits manuels via `apply_patch`; assembleur et generateur peuvent ecrire leurs sorties generees.

## Granularite adaptative

La segmentation reste semantique, jamais un module par audio ni quota uniforme. La taille valide depend du nombre d'audios :

| Nombre de lecons | Modules autorises |
|---:|---:|
| 1 a 39 | 25 a 40 |
| 40 a 79 | 30 a 55 |
| 80 a 129 | 45 a 75 |
| 130 et plus | 70 a 110 |

Chaque module vise 15 a 25 minutes d'apprentissage. Une plage audio peut contribuer a plusieurs activites si la source le justifie. Chaque lecon doit posseder au moins une plage rattachee ou une exclusion motivee.

## Fondation generique

Le pipeline Ajroumiya doit devenir multi-cours avant premiere vague.

### Configuration par cours

Chaque `source-map.json` ajoute :

```json
{
  "schema_version": 2,
  "course_id": "moutammima",
  "module_count_range": [30, 55]
}
```

L'assembleur lit cette plage au lieu d'imposer 25 a 35. `course_id` est compare a `--identifier`, jamais a une constante Ajroumiya. Les batches sources suivent meme regle.

La fondation migre aussi `ajroumiya/source-map.json` vers schema 2 avec `module_count_range: [25, 35]` et les nouvelles cles de references, sans changer ses 35 modules, spans, statuts ni sortie publique. Les tests Ajroumiya restent verts apres migration. Le builder ne maintient pas deux schemas concurrents.

### References locales

Chaque module declare :

- `audio_spans` non vide;
- `canonical_refs` non vide quand une source canonique locale existe;
- `supporting_refs` facultatif pour commentaires, PDF ou autres complements locaux;
- quatre statuts `transcript`, `grammar`, `arabic`, `pedagogy`.

Le source-map porte aussi `source_inventory: {"canonical_available": true|false}`. Si ce booléen vaut `true`, chaque module exige au moins une `canonical_refs`; s'il vaut `false`, la liste peut être vide et `source-inventory.md` doit expliquer l'absence.

Si aucun texte canonique local n'existe, le dossier d'inventaire le documente explicitement et la transcription/audio reste source principale. Aucun chemin factice n'est ajoute pour satisfaire validation.

### Sauvegarde

Chaque cours conserve une fois son ancien cours dans :

`cours-pedagogiques/<identifier>/cours.before-transcript-first.md`

Une nouvelle execution ne l'ecrase jamais.

## Architecture de production par cours

Chaque cours possede :

```text
cours-pedagogiques/<id>/
  cours.before-transcript-first.md
  cours.md
  source-map.json
  modules/
    01-....md

.superpowers/sdd/all-courses/<id>/
  progress.md
  baseline.json
  source-inventory.md
  source-001-015.json
  source-016-030.json
  ...
  architecture-report.md
  writing-01-10-report.md
  ...
  final-report.md
```

Les lots sources couvrent au maximum 15 audios. Les lots de redaction couvrent au maximum 10 modules. Chaque lot termine est inscrit dans `progress.md`; une nouvelle session reprend le premier lot incomplet sans refaire le travail valide.

## Parallelisation par sous-agents

Pendant une vague, un agent durable est responsable d'un cours. Il ne modifie que son dossier de cours et son dossier SDD. Aucun agent de cours ne modifie `site/data/catalog.json`, `README.md`, les tests communs ou un autre cours.

Travail de chaque agent :

1. inventorier sources et enregistrer baselines;
2. extraire les dossiers sources par lots de 15 audios;
3. produire `source-map.json` avec toutes les lecons couvertes;
4. rediger les modules par lots de 10;
5. passer validations de fragments et source-map;
6. corriger tout echec mecanique ou grammatical detecte;
7. ecrire rapport final durable.

Le controleur racine :

1. generalise et teste le pipeline commun;
2. lance trois agents de cours en parallele;
3. surveille les ledgers sans relancer lots termines;
4. assemble les trois cours seulement apres leurs validations;
5. regenere catalogue une seule fois par vague;
6. execute suites Python, syntaxe et navigateur;
7. compare hashes des donnees protegees et objets de cours hors vague;
8. marque vague complete puis lance suivante.

## Contrat pedagogique d'un module

Chaque fragment suit exactement cet ordre :

1. `الهدف`
2. `قبل أن تبدأ`
3. `شرح المسألة`
4. `القاعدة`
5. `لماذا؟`
6. `أمثلة متدرجة`
7. `تحليل خطوة خطوة`
8. `خطأ شائع`
9. `تدريب موجه`
10. `تدريب مستقل`
11. `خلاصة للحفظ`
12. `تشخيص قبلي` pour premier module, sinon `مراجعة تراكمية`
13. `أسئلة التحقق`

Questionnaire : rappel, comprehension, classement, application, analyse, correction d'erreur, transfert et cumulatif. Reponse complete avec fonction, حكم, علامة et سبب lorsque requis.

Pour sarf, les analyses remplacent fonction/hukm par وزن, اصل, زيادة, اعلال, ابدال ou سبب morphologique selon le chapitre. Pour balagha, elles donnent type, indice textuel, effet semantique et comparaison pertinente.

## Validation sans checkpoint humain

L'utilisateur a explicitement delegue toute validation. Aucun arret n'est demande entre cours ou vagues. La qualite reste assuree par :

- validation structurelle du builder;
- couverture de chaque audio ou exclusion;
- audits de provenance publique;
- tests Python complets;
- tests Playwright des premiers, milieux et derniers modules des cours touches;
- audit croise final par sous-agent sur chaque vague;
- hashes de toutes donnees protegees;
- controle de non-drift des cours hors vague.

Tout Critical ou Important trouve par audit interne est corrige avant publication de la vague. Aucun accord utilisateur n'est requis pour ces corrections dans le perimetre approuve.

## Integration d'une vague

Ordre strict :

1. valider chaque source-map sans `pending`;
2. valider tous fragments;
3. assembler chaque cours, creant sauvegarde immuable;
4. regenerer `site/data/catalog.json` une fois;
5. verifier 14 cours et 792 lecons;
6. verifier nombres modules/questions selon configuration;
7. executer suite Python complete;
8. executer Playwright;
9. verifier empreintes protegees;
10. arreter serveur et enregistrer rapport de vague.

## Politique d'erreur et reprise

- Echec d'un lot : seul ce lot est repris.
- Agent interrompu : ledger disque fait foi.
- Conflit de fichiers : controleur stoppe agent fautif; aucun merge aveugle.
- Source locale absente : documenter inventaire, ne pas inventer reference.
- Ambiguite grammaticale : conserver formulation audio bornee ou consulter source locale; ne pas elargir.
- Echec global apres integration : identifier cours responsable, corriger fragment source, reconstruire cours et catalogue.
- Une vague n'est complete qu'avec zero Critical/Important et toutes validations vertes.

## Criteres de fin

- Treize cours reecrits dans ordre catalogue.
- Chaque cours respecte sa plage de modules adaptative.
- Chaque module possede sections requises et 8 a 10 questions.
- Chaque lecon est couverte ou exclue.
- Tous statuts sont `verified`.
- Sauvegardes initiales presentes et immuables.
- Catalogue reproductible : 14 cours, 792 lecons.
- Ajroumiya et cours hors vague ne regressent jamais.
- Donnees protegees gardent empreintes de baseline.
- Python, syntaxe et navigateur verts.
- Ledgers des cinq vagues et treize cours marques `complete`.
