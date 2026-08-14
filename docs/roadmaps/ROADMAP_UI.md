# Roadmap UI — PaperNest

## État

La version actuelle de PaperNest reste terminée et stable.

`PaperNestGlideRail`, l’identité visuelle, les wrappers Python des pickers et `AppDialog` sont terminés, intégrés et validés sous Windows. Les anciens contrôles Flutter de dialogue, couleur, date et icône ont été retirés de PaperNestExtension.

## Objectif

Préserver une interface simple et stable tout en ajoutant uniquement les améliorations qui apportent une valeur visuelle ou ergonomique directe.

## Contrôles intégrés et validés

- [x] `PaperNestTextField`.
- [x] `PaperNestDropdown` et `PaperNestDropdownOption`.
- [x] `SearchDropDown` pour les filtres concernés.
- [x] `BaseColorPicker` Python avec `MaterialPicker`.
- [x] `BaseDatePickerField` Python avec `ft.DatePicker`.
- [x] `PaperNestFilePicker` via `BaseFilePicker`.
- [x] `BaseIconPicker` Python avec recherche dans `ft.Icons`.
- [x] `PaperNestGlideRail` pour la navigation principale.

## Migrations terminées

- [x] Migration ColorPicker.
- [x] Migration DatePicker.
- [x] Migration FilePicker et retrait de `flet-dropzone`.
- [x] Migration IconPicker et validation du build Windows.
- [x] Migration de la sidebar manuelle vers `PaperNestGlideRail`.
- [x] Centralisation de la navigation dans `src/app/navigation/navigation.py`.
- [x] Sélection, nettoyage et intégration du symbole officiel PaperNest.

## Chantier terminé — Organisation des Pickers

- [x] Créer le package `src/app/theme/pickers`.
- [x] Y créer les quatre wrappers thématiques.
- [x] Mettre à jour tous les imports applicatifs.
- [x] Supprimer les anciens fichiers à la racine de `src/app/theme`.
- [x] Supprimer définitivement `BaseIconField` de `forms.py`.
- [x] Nettoyer les imports devenus inutiles.
- [x] Valider le lancement et le build Windows.

Voir `ROADMAP_PICKERS_ORGANIZATION.md`.

## Chantier terminé — AppDialog Python

- [x] Créer une roadmap PaperNest dédiée.
- [x] Créer une roadmap PaperNestExtension dédiée.
- [x] Étudier les sources Python et Flutter d’`AlertDialog`.
- [x] Abandonner le fork `PaperNestAlertDialog` au profit de `ft.AlertDialog`.
- [x] Faire hériter `AppDialog` de `ft.AlertDialog`.
- [x] Construire le rendu PaperNest entièrement en Python.
- [x] Conserver et valider le DatePicker natif.

Voir `ROADMAP_ALERT_DIALOG.md`.

## Principe de maintenance

PaperNest reste une application simple. Les prochains chantiers ne doivent pas devenir une refonte générale ni entraîner l’ajout de fonctions sans besoin concret. Un composant validé ne doit plus évoluer sans problème réel ou gain clairement démontré.
