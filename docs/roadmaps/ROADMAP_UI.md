# Roadmap UI — PaperNest

## État

La version actuelle de PaperNest reste terminée et stable. `PaperNestGlideRail` est intégré et validé dans l’application. Le symbole PaperNest final est intégré dans la zone de marque de la rail et son rendu a été validé.

La navigation a également été recentralisée dans `src/app/navigation/navigation.py` afin de séparer clairement la définition des destinations et la construction de la rail du cycle de vie général de `MainWindow`.

## Objectif

Préserver une interface simple et stable tout en ajoutant uniquement les améliorations qui apportent une valeur visuelle ou ergonomique directe.

## Contrôles intégrés et validés

- [x] `PaperNestTextField`.
- [x] `PaperNestDropdown` et `PaperNestDropdownOption`.
- [x] `SearchDropDown` pour les filtres concernés.
- [x] `PaperNestColorPicker` via `BaseColorPicker`.
- [x] `PaperNestDatePicker` via `BaseDatePickerField`.
- [x] `PaperNestFilePicker` via `BaseFilePicker`.
- [x] `PaperNestGlideRail` pour la navigation principale.

## Migrations terminées

- [x] Migration ColorPicker et suppression de l’ancien `BaseColorField`.
- [x] Migration DatePicker et suppression de l’ancien DatePicker natif.
- [x] Migration FilePicker, suppression de `FileDropZone` et retrait de `flet-dropzone`.
- [x] Migration de la sidebar manuelle vers `PaperNestGlideRail`.
- [x] Suppression de l’ancienne navigation après validation sous Windows.
- [x] Centralisation de la navigation dans `src/app/navigation/navigation.py`.
- [x] Réduction de `MainWindow` au cycle de vie de la vue affichée.
- [x] Utilisation de `ft.Text` personnalisés pour le titre et le sous-titre de marque.
- [x] Nettoyage complet de `forms.py` et des imports obsolètes.
- [x] Validation visuelle, fonctionnelle et des builds Windows des migrations terminées.
- [x] Mise à jour des roadmaps concernées.

## Prochains chantiers encadrés

### Identité visuelle

- [x] Définir les assets nécessaires.
- [x] Créer une roadmap dédiée.
- [x] Sélectionner le symbole compact PaperNest.
- [x] Créer une version SVG finale nettoyée.
- [x] Intégrer le symbole dans `PaperNestGlideRail`.
- [x] Valider le rendu du symbole dans la rail.
- [ ] Générer les déclinaisons PNG nécessaires au build Windows.
- [ ] Intégrer et tester l’icône du build de l’application.
- [ ] Créer un logo horizontal uniquement si un besoin réel est confirmé.

Voir `ROADMAP_BRANDING.md`.

### PaperNestIconPicker

- [x] Identifier le besoin réel autour de `BaseIconField`.
- [x] Créer une roadmap dédiée dans PaperNestExtension.
- [ ] Étudier puis développer le contrôle autonome sans fonctions inutiles.
- [ ] Intégrer le contrôle uniquement après validation de l’exemple Windows.

Voir la roadmap `PaperNestExtension/docs/roadmaps/ROADMAP_ICON_PICKER.md`.

## Principe de maintenance

PaperNest reste une application simple. Les prochains chantiers ne doivent pas devenir une refonte générale ni entraîner l’ajout de fonctions sans besoin concret. Un composant validé ne doit plus évoluer sans problème réel ou gain clairement démontré.
