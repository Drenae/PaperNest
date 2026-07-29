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
- [x] Étude du champ couleur actuel dans PaperNest.
- [x] Création de `BaseColorPicker` à partir de l’API réelle de `PaperNestColorPicker`.
- [x] Intégration de `PaperNestColorPicker` dans le formulaire d’édition des classeurs.
- [x] Remplacement de l’utilisation de l’ancien `BaseColorField`.
- [x] Suppression de l’ancien code couleur devenu inutile après validation.
- [x] Validation visuelle et fonctionnelle de `PaperNestColorPicker` sous Windows.

## En cours

- [ ] Migration de `PaperNestDatePicker`.

## À faire

- [ ] Migration de `PaperNestFilePicker`.

## Après migration de tous les contrôles

- [ ] Vérifier l’ensemble de `forms.py`.
- [ ] Supprimer définitivement les wrappers devenus inutiles.
- [ ] Nettoyer globalement les imports obsolètes.
- [ ] Effectuer une validation visuelle et fonctionnelle complète sous Windows.

## Règle de migration

Chaque migration doit être réalisée à partir de l’API réelle du contrôle présent dans PaperNestExtension. Les variantes spécialisées ne doivent être utilisées que dans les contextes qui les justifient.
