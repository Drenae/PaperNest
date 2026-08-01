# Roadmap UI — PaperNest

## État

La version actuelle de PaperNest reste terminée et stable.

`PaperNestGlideRail`, l’identité visuelle et `PaperNestIconPicker` sont terminés, intégrés et validés sous Windows. Les chantiers actifs sont maintenant le nettoyage final des wrappers de pickers et la réorganisation de l’application d’exemple de PaperNestExtension. La migration vers `PaperNestAlertDialog` est planifiée mais n’a pas encore commencé.

## Objectif

Préserver une interface simple et stable tout en ajoutant uniquement les améliorations qui apportent une valeur visuelle ou ergonomique directe.

## Contrôles intégrés et validés

- [x] `PaperNestTextField`.
- [x] `PaperNestDropdown` et `PaperNestDropdownOption`.
- [x] `SearchDropDown` pour les filtres concernés.
- [x] `PaperNestColorPicker` via `BaseColorPicker`.
- [x] `PaperNestDatePicker` via `BaseDatePickerField`.
- [x] `PaperNestFilePicker` via `BaseFilePicker`.
- [x] `PaperNestIconPicker` via `BaseIconPicker`.
- [x] `PaperNestGlideRail` pour la navigation principale.

## Migrations terminées

- [x] Migration ColorPicker.
- [x] Migration DatePicker.
- [x] Migration FilePicker et retrait de `flet-dropzone`.
- [x] Migration IconPicker et validation du build Windows.
- [x] Migration de la sidebar manuelle vers `PaperNestGlideRail`.
- [x] Centralisation de la navigation dans `src/app/navigation/navigation.py`.
- [x] Sélection, nettoyage et intégration du symbole officiel PaperNest.

## Chantier actif — Organisation des Pickers

- [x] Créer le package `src/app/theme/pickers`.
- [x] Y créer les quatre wrappers thématiques.
- [ ] Mettre à jour tous les imports applicatifs.
- [ ] Supprimer les anciens fichiers à la racine de `src/app/theme`.
- [ ] Supprimer définitivement `BaseIconField` de `forms.py`.
- [ ] Nettoyer les imports devenus inutiles.
- [ ] Valider le lancement et le build Windows.

Voir `ROADMAP_PICKERS_ORGANIZATION.md`.

## Chantier planifié — PaperNestAlertDialog

- [x] Créer une roadmap PaperNest dédiée.
- [x] Créer une roadmap PaperNestExtension dédiée.
- [ ] Étudier les sources Python et Flutter d’`AlertDialog`.
- [ ] Développer `PaperNestAlertDialog` dans PaperNestExtension.
- [ ] Faire hériter `AppDialog` du nouveau contrôle.
- [ ] Partager le rendu Flutter avec les pickers compatibles.
- [ ] Conserver le DatePicker natif si la migration dégrade ses fonctions.

Voir `ROADMAP_ALERT_DIALOG.md`.

## Principe de maintenance

PaperNest reste une application simple. Les prochains chantiers ne doivent pas devenir une refonte générale ni entraîner l’ajout de fonctions sans besoin concret. Un composant validé ne doit plus évoluer sans problème réel ou gain clairement démontré.
