# Roadmap — Organisation des Pickers PaperNest

## État

Chantier en cours.

Les wrappers thématiques des pickers sont maintenant regroupés dans `src/app/theme/pickers`. Tous les imports applicatifs identifiés ont été migrés et les anciens fichiers ont été supprimés. Le nettoyage de `BaseIconField` dans `forms.py` reste à terminer avant validation Windows.

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
- [ ] Valider le lancement et le build Windows.

## Nettoyage associé

- [ ] Supprimer définitivement `BaseIconField` de `forms.py`.
- [ ] Supprimer ses imports devenus inutiles.
- [ ] Vérifier que `forms.py` ne contient plus de picker historique.
- [ ] Mettre à jour le changelog.

## Critère de finalisation

Le chantier sera terminé lorsque `BaseIconField` aura été supprimé, que `forms.py` aura été nettoyé et que PaperNest aura été validé sous Windows.
