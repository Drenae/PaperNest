# Roadmap UI — PaperNest

## Objectif

Stabiliser l’interface de PaperNest et migrer progressivement les champs vers PaperNestExtension sans dégrader les comportements déjà validés.

## Fait

- [x] Intégration de `PaperNestTextField`.
- [x] Intégration de `PaperNestDropdown`.
- [x] Création de `SearchDropDown` pour les filtres de recherche.
- [x] Bouton d’effacement réservé aux filtres concernés.
- [x] Correction de l’affichage des libellés des options de dropdown.
- [x] Résolution des problèmes causés par d’anciens dossiers de build.

## En cours

- [ ] Préparation de l’intégration de `PaperNestColorPicker`.

## À faire

- [ ] Étudier le champ couleur actuel dans PaperNest.
- [ ] Intégrer `PaperNestColorPicker` après finalisation dans PaperNestExtension.
- [ ] Supprimer l’ancien code couleur devenu inutile après validation.
- [ ] Vérifier l’ensemble de `forms.py` après la migration.
- [ ] Nettoyer les imports et wrappers obsolètes.
- [ ] Effectuer une validation visuelle et fonctionnelle complète sous Windows.

## Règle de migration

Chaque migration doit être réalisée à partir de l’API réelle du contrôle présent dans PaperNestExtension. Les variantes spécialisées ne doivent être utilisées que dans les contextes qui les justifient.
