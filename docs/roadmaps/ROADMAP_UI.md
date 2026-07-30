# Roadmap UI — PaperNest

## État

La version actuelle de PaperNest reste terminée et stable. Trois améliorations limitées sont désormais à l’étude sans remettre en cause ce périmètre : `PaperNestIconPicker`, une navigation native avec effet drawer et les assets visuels PaperNest.

## Objectif

Préserver une interface simple et stable tout en étudiant uniquement les améliorations qui apportent une valeur visuelle ou ergonomique directe.

## Contrôles intégrés et validés

- [x] `PaperNestTextField`.
- [x] `PaperNestDropdown` et `PaperNestDropdownOption`.
- [x] `SearchDropDown` pour les filtres concernés.
- [x] `PaperNestColorPicker` via `BaseColorPicker`.
- [x] `PaperNestDatePicker` via `BaseDatePickerField`.
- [x] `PaperNestFilePicker` via `BaseFilePicker`.

## Migrations terminées

- [x] Migration ColorPicker et suppression de l’ancien `BaseColorField`.
- [x] Migration DatePicker et suppression de l’ancien DatePicker natif.
- [x] Migration FilePicker, suppression de `FileDropZone` et retrait de `flet-dropzone`.
- [x] Nettoyage complet de `forms.py` et des imports obsolètes.
- [x] Validation visuelle, fonctionnelle et des builds Windows.
- [x] Mise à jour des roadmaps et changelogs des deux projets.

## Nouvelles pistes encadrées

### PaperNestIconPicker

- [x] Identifier le besoin réel autour de `BaseIconField`.
- [x] Créer une roadmap dédiée dans PaperNestExtension.
- [ ] Étudier puis développer le contrôle autonome sans fonctions inutiles.
- [ ] Intégrer le contrôle uniquement après validation de l’exemple Windows.

Voir la roadmap `PaperNestExtension/docs/roadmaps/ROADMAP_ICON_PICKER.md`.

### NavigationDrawer

- [x] Étudier la sidebar actuelle.
- [x] Étudier les sources Python et Dart du `NavigationDrawer` natif Flet.
- [x] Créer une roadmap dédiée.
- [ ] Réaliser un prototype natif séparé sans supprimer la sidebar actuelle.
- [ ] Comparer le rendu sous Windows.
- [ ] Décider d’un éventuel fork uniquement si une limite réelle est démontrée.

Voir `ROADMAP_NAVIGATION_DRAWER.md`.

### Identité visuelle

- [x] Définir les assets nécessaires.
- [x] Créer une roadmap dédiée.
- [ ] Créer et valider l’icône PaperNest.
- [ ] Créer et valider le logo destiné au drawer.
- [ ] Intégrer les assets uniquement après validation graphique.

Voir `ROADMAP_BRANDING.md`.

## Principe de maintenance

PaperNest reste une application simple. Ces pistes ne doivent pas devenir une refonte générale ni entraîner l’ajout de fonctions sans besoin concret. La version actuelle doit rester fonctionnelle pendant toute la durée des prototypes, et aucun ancien composant ne doit être supprimé avant validation de son remplacement.