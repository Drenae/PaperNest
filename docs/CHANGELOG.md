# Changelog — PaperNest

Les évolutions importantes de PaperNest sont consignées dans ce fichier.

## Version finalisée

PaperNest est considéré comme terminé dans son périmètre actuel. L’application doit désormais rester simple, stable et centrée sur ses usages réels.

### Interface et contrôles

- Intégration de `PaperNestTextField`.
- Intégration de `PaperNestDropdown` et de `PaperNestDropdownOption`.
- Ajout de `SearchDropDown` pour les filtres disposant d’un effacement dédié.
- Intégration de `PaperNestColorPicker` via `BaseColorPicker`.
- Intégration de `PaperNestDatePicker` via `BaseDatePickerField`.
- Intégration de `PaperNestFilePicker` via `BaseFilePicker`.
- Harmonisation des wrappers thématiques avec des valeurs par défaut surchargeables.

### DatePicker

- Héritage direct de `PaperNestDatePicker` sans conteneur intermédiaire.
- Conservation de la valeur native `datetime`.
- Ajout de `iso_value` pour les services utilisant le format ISO.
- Migration du dialogue des métadonnées.
- Suppression de l’ancien DatePicker natif de `forms.py`.

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
- Validation visuelle et fonctionnelle complète sous Windows.
- Validation des parcours d’import, de restauration, de couleur et de date.
- Validation du build Windows.
- Mise à jour et clôture de toutes les roadmaps.

## Maintenance

Les futures modifications doivent se limiter aux corrections nécessaires ou à de petites améliorations directement utiles, sans complexifier l’application.
