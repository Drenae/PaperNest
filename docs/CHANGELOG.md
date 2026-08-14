# Changelog — PaperNest

Les évolutions importantes de PaperNest sont consignées dans ce fichier.

## Version finalisée

PaperNest est considéré comme terminé dans son périmètre actuel. L’application doit désormais rester simple, stable et centrée sur ses usages réels.

### Interface et contrôles

- Intégration de `PaperNestTextField`.
- Intégration de `PaperNestDropdown` et de `PaperNestDropdownOption`.
- Ajout de `SearchDropDown` pour les filtres disposant d’un effacement dédié.
- Remplacement de `PaperNestColorPicker` par `BaseColorPicker`, composé en Python autour de `MaterialPicker`.
- Remplacement de `PaperNestDatePicker` par `BaseDatePickerField`, composé en Python autour de `ft.DatePicker`.
- Intégration de `PaperNestFilePicker` via `BaseFilePicker`.
- Remplacement de `PaperNestIconPicker` par `BaseIconPicker`, composé entièrement en Python avec recherche dans `ft.Icons`.
- Retour définitif à `AppDialog(ft.AlertDialog)` pour tous les dialogues applicatifs.
- Harmonisation des wrappers thématiques avec des valeurs par défaut surchargeables.

### DatePicker

- Utilisation directe de `ft.DatePicker` depuis le wrapper Python.
- Conservation d’une valeur publique `datetime` représentant une date civile.
- Ajout de `iso_value` pour les services utilisant le format ISO.
- Migration du dialogue des métadonnées.
- Localisation française et thème PaperNest validés.
- Correction du décalage d’un jour par l’utilisation de dates civiles.

### FilePicker

- Migration de la sélection multiple et du glisser-déposer du tableau de bord.
- Conservation du bouton « Ajouter des fichiers » ouvrant l’explorateur.
- Utilisation de la sélection interne du contrôle comme source de vérité.
- Migration de la restauration des sauvegardes ZIP dans l’administration.
- Suppression du FilePicker partagé historique de `MainWindow`.
- Suppression de `FileDropZone` et de la dépendance `flet-dropzone`.

### Nettoyage et validation

- Nettoyage de `forms.py` et des imports obsolètes.
- Suppression des anciens wrappers devenus inutiles.
- Suppression de `PaperNestAlertDialog`, `PaperNestColorPicker`, `PaperNestDatePicker`, `PaperNestIconPicker` et `PaperNestDialogSurface` dans PaperNestExtension.
- Validation visuelle et fonctionnelle complète sous Windows.
- Validation des parcours d’import, de restauration, de couleur et de date.
- Validation du build Windows.
- Mise à jour et clôture de toutes les roadmaps.

## Maintenance

Les futures modifications doivent se limiter aux corrections nécessaires ou à de petites améliorations directement utiles, sans complexifier l’application.
