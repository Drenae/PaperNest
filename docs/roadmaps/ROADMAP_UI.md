# Roadmap UI — PaperNest

## État

La version actuelle de PaperNest reste stable. Trois améliorations limitées sont suivies : l’intégration de `PaperNestGlideRail`, la future identité visuelle et l’étude de `PaperNestIconPicker`.

## Objectif

Préserver une interface simple et stable tout en ajoutant uniquement les améliorations qui apportent une valeur visuelle ou ergonomique directe.

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

## PaperNestGlideRail

- [x] Redéfinir le besoin réel : rail compacte permanente, déploiement au survol et superposition.
- [x] Abandonner le prototype `NavigationDrawer` modal.
- [x] Développer `PaperNestGlideRail` dans PaperNestExtension.
- [x] Valider son build, son exemple et son comportement sous Windows.
- [x] Intégrer une première version dans `MainWindow`.
- [x] Conserver la logique de navigation et le cycle de vie des vues.
- [ ] Valider l’intégration dans PaperNest.
- [ ] Supprimer l’ancienne sidebar après validation.
- [ ] Valider le build Windows de PaperNest.

Voir `ROADMAP_GLIDE_RAIL.md`.

## Identité visuelle

- [x] Définir les assets nécessaires.
- [x] Créer une roadmap dédiée.
- [ ] Créer et valider le symbole compact PaperNest en SVG.
- [ ] Créer et valider le logo horizontal PaperNest en SVG.
- [ ] Produire les déclinaisons PNG et l’icône Windows nécessaires.
- [ ] Intégrer les assets dans `PaperNestGlideRail` après validation graphique.

Voir `ROADMAP_BRANDING.md`.

## PaperNestIconPicker

- [x] Identifier le besoin réel autour de `BaseIconField`.
- [x] Créer une roadmap dédiée dans PaperNestExtension.
- [ ] Étudier puis développer le contrôle autonome sans fonctions inutiles.
- [ ] Intégrer le contrôle uniquement après validation de l’exemple Windows.

Voir `PaperNestExtension/docs/roadmaps/ROADMAP_ICON_PICKER.md`.

## Principe de maintenance

PaperNest reste une application simple. Aucun nouveau comportement ne doit être ajouté sans besoin concret, et aucun ancien composant ne doit être supprimé avant validation complète de son remplacement.
