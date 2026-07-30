# Roadmap UI — PaperNest

## Objectif

Stabiliser l’interface de PaperNest et migrer progressivement les champs vers PaperNestExtension sans dégrader les comportements déjà validés.

## Fait

- [x] Intégration de `PaperNestTextField`.
- [x] Intégration de `PaperNestDropdown`.
- [x] Création de `SearchDropDown` pour les filtres de recherche.
- [x] Bouton d’effacement réservé aux filtres concernés.
- [x] Correction de l’affichage des libellés des options de dropdown.
- [x] Résolution des problèmes causés par d’anciens dossiers de build.
- [x] Étude du champ couleur actuel dans PaperNest.
- [x] Création de `BaseColorPicker` à partir de l’API réelle de `PaperNestColorPicker`.
- [x] Intégration de `PaperNestColorPicker` dans le formulaire d’édition des classeurs.
- [x] Remplacement de l’utilisation de l’ancien `BaseColorField`.
- [x] Suppression de l’ancien code couleur devenu inutile après validation.
- [x] Validation visuelle et fonctionnelle de `PaperNestColorPicker` sous Windows.
- [x] Migration de `PaperNestDatePicker`.
  - [x] Lecture de l’API Python réelle.
  - [x] Lecture de l’implémentation Flutter réelle.
  - [x] Création du fichier thématique dédié `date_picker.py`.
  - [x] Héritage direct de `PaperNestDatePicker`, sans conteneur `ft.Row`.
  - [x] Harmonisation du wrapper avec `BaseColorPicker` et `BaseFilePicker` via des `kwargs.setdefault(...)` surchargeables.
  - [x] Conservation de `value` au type natif `datetime`.
  - [x] Exposition explicite de `iso_value` pour les services PaperNest.
  - [x] Remplacement des usages dans le dialogue des métadonnées.
  - [x] Suppression de l’ancien DatePicker natif de `forms.py`.
  - [x] Validation visuelle et fonctionnelle sous Windows.
  - [x] Validation du build Windows.
- [x] Migration de `PaperNestFilePicker`.
  - [x] Lecture de la roadmap dédiée de l’extension.
  - [x] Lecture de l’API Python réelle.
  - [x] Lecture de l’exemple fonctionnel de l’extension.
  - [x] Création du wrapper thématique dédié `file_picker.py` héritant de `PaperNestFilePicker`.
  - [x] Migration de la sélection multiple et du glisser-déposer de `UploadPanel`.
  - [x] Conservation du bouton « Ajouter des fichiers » utilisant `pick_files()`.
  - [x] Utilisation de la sélection interne du contrôle comme source de vérité.
  - [x] Utilisation des identifiants du contrôle comme lien avec les métadonnées de classement.
  - [x] Migration du bouton `restore_button` de l’administration.
  - [x] Migration de la sélection simple des sauvegardes ZIP.
  - [x] Suppression du FilePicker historique partagé de `MainWindow`.
  - [x] Suppression de l’ancien wrapper `ft.FilePicker` de `forms.py`.
  - [x] Suppression de `FileDropZone`.
  - [x] Suppression de la dépendance `flet-dropzone`.
  - [x] Validation visuelle et fonctionnelle de l’import sous Windows.
  - [x] Validation visuelle et fonctionnelle du parcours de restauration sous Windows.
  - [x] Validation du build Windows après migration.

## Nettoyage final

- [x] Vérifier l’ensemble de `forms.py` pour les anciens DatePicker et FilePicker.
- [x] Supprimer les anciens wrappers DatePicker et FilePicker devenus inutiles.
- [x] Supprimer l’ancien `FileDropZone` devenu inutile.
- [x] Nettoyer les imports liés à ces anciens wrappers.
- [x] Retirer la dépendance `flet-dropzone` devenue inutile.
- [x] Effectuer une validation visuelle et fonctionnelle complète sous Windows.

## Règle de migration

Chaque migration doit être réalisée à partir de l’API réelle du contrôle présent dans PaperNestExtension. Les variantes spécialisées ne doivent être utilisées que dans les contextes qui les justifient.
