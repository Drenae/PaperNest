# Roadmap — Organisation des Pickers PaperNest

## État

Chantier en cours.

Les wrappers thématiques des pickers sont regroupés dans `src/app/theme/pickers` afin de clarifier l’architecture et de faciliter leur maintenance.

## Objectif

Centraliser les wrappers applicatifs liés aux contrôles `PaperNest*Picker` sans modifier leur API ni leur comportement validé.

## Structure cible

- [x] Créer `src/app/theme/pickers/__init__.py`.
- [x] Créer `src/app/theme/pickers/color_picker.py`.
- [x] Créer `src/app/theme/pickers/date_picker.py`.
- [x] Créer `src/app/theme/pickers/file_picker.py`.
- [x] Créer `src/app/theme/pickers/icon_picker.py`.
- [ ] Mettre à jour tous les imports applicatifs.
- [ ] Supprimer les anciens fichiers à la racine de `src/app/theme`.
- [ ] Vérifier qu’aucun import historique ne subsiste.
- [ ] Valider le lancement et le build Windows.

## Nettoyage associé

- [ ] Supprimer définitivement `BaseIconField` de `forms.py`.
- [ ] Supprimer ses imports devenus inutiles.
- [ ] Vérifier que `forms.py` ne contient plus de picker historique.
- [ ] Mettre à jour le changelog.

## Critère de finalisation

Le chantier sera terminé lorsque tous les imports utiliseront `app.theme.pickers`, que les anciens fichiers et `BaseIconField` auront été supprimés et que PaperNest aura été validé sous Windows.
