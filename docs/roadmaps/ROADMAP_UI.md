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
  - [x] Création de l’adaptateur thématique conservant la valeur ISO historique.
  - [x] Remplacement des usages de `BaseDatePickerField` dans le dialogue des métadonnées.
  - [x] Validation visuelle et fonctionnelle sous Windows.
  - [x] Validation du build Windows.

## En cours

- [ ] Migration de `PaperNestFilePicker`.
  - [x] Lecture de la roadmap dédiée de l’extension.
  - [x] Lecture de l’API Python réelle.
  - [x] Identification du wrapper historique `BaseFilePicker`.
  - [x] Identification du sélecteur partagé créé dans `MainWindow`.
  - [x] Identification de la sélection multiple et du glisser-déposer dans `UploadPanel`.
  - [x] Identification de la sélection simple de sauvegarde dans `AdminController`.
  - [x] Comparaison détaillée des événements et de la source de vérité.
  - [x] Décision de ne pas créer d’adaptateur thématique pour le parcours d’import.
  - [x] Migration de la sélection multiple de `UploadPanel`.
  - [x] Migration du glisser-déposer de `UploadPanel`.
  - [x] Suppression de la dépendance de `DashboardView` au `BaseFilePicker` partagé.
  - [x] Utilisation des identifiants du contrôle comme lien avec les métadonnées de classement.
  - [ ] Validation visuelle et fonctionnelle de l’import sous Windows.
  - [ ] Migration de la sélection simple de sauvegarde dans l’administration.
  - [ ] Validation visuelle et fonctionnelle du parcours de restauration sous Windows.

## Après migration de tous les contrôles

- [ ] Vérifier l’ensemble de `forms.py`.
- [ ] Supprimer définitivement les wrappers devenus inutiles, dont l’ancien `BaseDatePickerField` et `BaseFilePicker`.
- [ ] Nettoyer globalement les imports obsolètes.
- [ ] Effectuer une validation visuelle et fonctionnelle complète sous Windows.

## Règle de migration

Chaque migration doit être réalisée à partir de l’API réelle du contrôle présent dans PaperNestExtension. Les variantes spécialisées ne doivent être utilisées que dans les contextes qui les justifient.
