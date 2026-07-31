# Roadmap UI — PaperNest

## État

La version actuelle de PaperNest reste terminée et stable.

`PaperNestGlideRail` et l’identité visuelle PaperNest sont désormais officiellement terminés, intégrés et validés sous Windows. Le prochain chantier UI actif est `PaperNestIconPicker`.

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
- [x] Sélection, nettoyage et intégration du symbole officiel PaperNest.
- [x] Validation visuelle du branding dans la rail.
- [x] Nettoyage complet de `forms.py` et des imports obsolètes liés aux migrations terminées.
- [x] Validation visuelle, fonctionnelle et des builds Windows.
- [x] Mise à jour des roadmaps concernées.

## Chantiers terminés

### PaperNestGlideRail

- [x] Contrôle finalisé dans PaperNestExtension.
- [x] Intégration réelle dans PaperNest.
- [x] Navigation centralisée dans son module dédié.
- [x] Validation finale par l’utilisateur.

Voir `PaperNestExtension/docs/roadmaps/ROADMAP_GLIDE_RAIL.md`.

### Identité visuelle

- [x] Symbole compact sélectionné.
- [x] SVG final nettoyé.
- [x] Intégration dans `PaperNestGlideRail`.
- [x] Validation dans les états replié et déployé.
- [x] Validation finale par l’utilisateur.

Voir `ROADMAP_BRANDING.md`.

## Chantier actif

### PaperNestIconPicker

- [x] Identifier le besoin réel autour de `BaseIconField`.
- [x] Créer une roadmap dédiée dans PaperNestExtension.
- [x] Relire l’implémentation actuelle de `BaseIconField`.
- [ ] Finaliser l’API minimale du nouveau contrôle.
- [ ] Développer le contrôle autonome dans PaperNestExtension.
- [ ] Ajouter l’exemple au projet principal de l’extension.
- [ ] Valider l’exemple sous Windows.
- [ ] Intégrer le contrôle dans l’éditeur des classeurs.
- [ ] Supprimer `BaseIconField` après validation.
- [ ] Valider le build Windows de PaperNest.

Voir `PaperNestExtension/docs/roadmaps/ROADMAP_ICON_PICKER.md`.

## Principe de maintenance

PaperNest reste une application simple. Les prochains chantiers ne doivent pas devenir une refonte générale ni entraîner l’ajout de fonctions sans besoin concret. Un composant validé ne doit plus évoluer sans problème réel ou gain clairement démontré.