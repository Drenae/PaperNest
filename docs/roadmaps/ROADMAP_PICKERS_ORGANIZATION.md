# Roadmap — Organisation des Pickers PaperNest

## État

Implémentation terminée et validée sous Windows.

Les wrappers thématiques des pickers sont regroupés dans `src/app/theme/pickers`. Tous les imports applicatifs identifiés ont été migrés, les anciens fichiers ont été supprimés et `BaseIconField` a été retiré de `forms.py`.

## Objectif

Centraliser les wrappers applicatifs liés aux contrôles `PaperNest*Picker` sans modifier leur API ni leur comportement validé.

## Structure cible

- [x] Créer `src/app/theme/pickers/__init__.py`.
- [x] Créer `src/app/theme/pickers/color_picker.py`.
- [x] Créer `src/app/theme/pickers/date_picker.py`.
- [x] Créer `src/app/theme/pickers/file_picker.py`.
- [x] Créer `src/app/theme/pickers/icon_picker.py`.
- [x] Mettre à jour tous les imports applicatifs identifiés.
- [x] Supprimer les anciens fichiers à la racine de `src/app/theme`.
- [x] Vérifier qu’aucun import historique ne subsiste.
- [x] Valider le lancement et le build Windows.

## Nettoyage associé

- [x] Supprimer définitivement `BaseIconField` de `forms.py`.
- [x] Supprimer ses imports devenus inutiles.
- [x] Vérifier que `forms.py` ne contient plus de picker historique.
- [x] Mettre à jour le changelog après validation.

## Critère de finalisation

Le chantier sera terminé après validation du lancement et du build Windows de PaperNest.
