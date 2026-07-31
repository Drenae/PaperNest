# Roadmap UI — PaperNest

## État

La version actuelle de PaperNest reste terminée et stable.

`PaperNestGlideRail` et l’identité visuelle PaperNest sont officiellement terminés. `PaperNestIconPicker` est désormais intégré dans l’éditeur des classeurs et attend sa validation finale dans PaperNest avant suppression de l’ancien `BaseIconField`.

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

- [x] Finaliser et valider le contrôle dans PaperNestExtension.
- [x] Créer `src/app/theme/icon_picker.py`.
- [x] Créer `BaseIconPicker` héritant directement de `PaperNestIconPicker`.
- [x] Convertir `AVAILABLE_ICONS` vers `PaperNestIconPickerOption`.
- [x] Remplacer l’usage de `BaseIconField` dans l’éditeur des classeurs.
- [x] Préserver les noms Material enregistrés et le fallback `FOLDER_ROUNDED`.
- [x] Préserver la prévisualisation de l’icône sélectionnée.
- [ ] Tester la création d’un classeur.
- [ ] Tester la modification d’un classeur existant.
- [ ] Tester une ancienne valeur d’icône inconnue et le fallback.
- [ ] Tester le build Windows de PaperNest.
- [ ] Supprimer définitivement `BaseIconField` de `forms.py` après validation.
- [ ] Nettoyer les imports devenus inutiles.
- [ ] Clôturer les roadmaps et changelogs des deux dépôts.

Voir `PaperNestExtension/docs/roadmaps/ROADMAP_ICON_PICKER.md`.

## Principe de maintenance

PaperNest reste une application simple. Les prochains chantiers ne doivent pas devenir une refonte générale ni entraîner l’ajout de fonctions sans besoin concret. Un composant validé ne doit plus évoluer sans problème réel ou gain clairement démontré.
