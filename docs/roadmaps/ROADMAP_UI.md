# Roadmap UI — PaperNest

## État

La roadmap UI est terminée. PaperNest est considéré comme finalisé dans son périmètre actuel.

## Objectif

Stabiliser l’interface de PaperNest et migrer les champs vers PaperNestExtension sans dégrader les comportements validés ni complexifier l’application.

## Contrôles intégrés

- [x] `PaperNestTextField`.
- [x] `PaperNestDropdown` et `PaperNestDropdownOption`.
- [x] `SearchDropDown` pour les filtres concernés.
- [x] `PaperNestColorPicker` via `BaseColorPicker`.
- [x] `PaperNestDatePicker` via `BaseDatePickerField`.
- [x] `PaperNestFilePicker` via `BaseFilePicker`.

## Migration ColorPicker

- [x] Étude de l’ancien champ couleur.
- [x] Création du wrapper thématique dédié avec des valeurs par défaut surchargeables.
- [x] Intégration dans le formulaire d’édition des classeurs.
- [x] Suppression de l’ancien `BaseColorField` et de son code devenu inutile.
- [x] Validation visuelle, fonctionnelle et du build Windows.

## Migration DatePicker

- [x] Lecture de l’API Python, de l’implémentation Flutter et de l’exemple.
- [x] Création de `date_picker.py`.
- [x] Héritage direct de `PaperNestDatePicker`, sans conteneur `ft.Row`.
- [x] Application du thème avec des `kwargs.setdefault(...)` surchargeables.
- [x] Conservation de `value` au type natif `datetime`.
- [x] Exposition de `iso_value` pour les services PaperNest.
- [x] Remplacement des usages dans le dialogue des métadonnées.
- [x] Suppression de l’ancien DatePicker natif de `forms.py`.
- [x] Validation visuelle, fonctionnelle et du build Windows.

## Migration FilePicker

- [x] Lecture de la roadmap, de l’API réelle et de l’exemple fonctionnel.
- [x] Création de `file_picker.py`.
- [x] Héritage direct de `PaperNestFilePicker`.
- [x] Application du thème avec des `kwargs.setdefault(...)` surchargeables.
- [x] Migration de la sélection multiple et du glisser-déposer de `UploadPanel`.
- [x] Conservation du bouton « Ajouter des fichiers » utilisant `pick_files()`.
- [x] Utilisation de la sélection interne comme source de vérité.
- [x] Conservation des métadonnées de classement via les identifiants des fichiers.
- [x] Migration du bouton `restore_button` et de la sélection simple ZIP.
- [x] Suppression du FilePicker historique partagé de `MainWindow`.
- [x] Suppression de l’ancien wrapper `ft.FilePicker` de `forms.py`.
- [x] Suppression de `FileDropZone` et de la dépendance `flet-dropzone`.
- [x] Validation de l’import, de la restauration et du build Windows.

## Nettoyage final

- [x] Vérification complète de `forms.py`.
- [x] Suppression des anciens wrappers DatePicker et FilePicker.
- [x] Suppression de `FileDropZone`.
- [x] Nettoyage des imports obsolètes.
- [x] Retrait de `flet-dropzone`.
- [x] Validation visuelle et fonctionnelle complète sous Windows.
- [x] Mise à jour des roadmaps et changelogs de PaperNest et PaperNestExtension.

## Principe de maintenance

PaperNest est terminé et doit rester simple. Les futures modifications doivent se limiter aux corrections nécessaires ou à de petites améliorations apportant une valeur directe, sans transformer l’application en système complexe.
