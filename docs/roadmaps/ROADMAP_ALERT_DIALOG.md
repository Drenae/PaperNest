# Roadmap — Migration vers PaperNestAlertDialog

## État

Migration implémentée dans PaperNest, en attente de validation applicative et du build Windows.

`PaperNestAlertDialog` et `PaperNestDialogSurface` sont validés dans PaperNestExtension. Les dialogues internes compatibles des ColorPicker et IconPicker utilisent la surface partagée. Le DatePicker conserve son dialogue Material natif avec un thème PaperNest. Le FilePicker ne possède aucun dialogue Flutter interne à migrer : ses fenêtres sont fournies par le système via `file_picker`.

## Objectif

Faire évoluer `AppDialog` pour qu’il hérite de `PaperNestAlertDialog` fourni par PaperNestExtension, tout en conservant les variantes et les comportements validés dans PaperNest.

## Architecture

- [x] Étudier l’API Python et le code Flutter d’`AlertDialog`.
- [x] Définir l’API de `PaperNestAlertDialog` avec PaperNestExtension.
- [x] Créer un composant Flutter interne partagé par les pickers.
- [x] Faire hériter `AppDialog` de `PaperNestAlertDialog`.
- [x] Conserver l’API publique `DialogVariant` par alias vers `PaperNestDialogVariant`.
- [x] Conserver `ConfirmDialog`, `DangerDialog` et `FormDialog`.
- [x] Préserver l’en-tête sombre, les espacements, les actions et la barrière.
- [x] Conserver la personnalisation des actions avec les boutons PaperNest.
- [x] Supprimer la construction Python manuelle de l’en-tête et des palettes.

## Pickers

- [x] Utiliser `PaperNestDialogSurface` dans ColorPicker.
- [x] Utiliser `PaperNestDialogSurface` dans IconPicker.
- [x] Conserver le DatePicker Material natif et lui appliquer un thème PaperNest via son `builder`.
- [x] Vérifier FilePicker : aucun `AlertDialog` Flutter interne à migrer.
- [x] Conserver les fenêtres natives de sélection, sauvegarde et dossier du système.

## Dialogues PaperNest à vérifier

- [ ] Ouvrir et fermer un `AppDialog` standard.
- [ ] Tester `ConfirmDialog` et ses deux actions.
- [ ] Tester `DangerDialog`, ses détails et son action irréversible.
- [ ] Tester `FormDialog` avec formulaire.
- [ ] Tester l’état de chargement du bouton de soumission.
- [ ] Tester les variantes standard, primary, success, warning et danger.
- [ ] Tester `title_action`.
- [ ] Tester les contenus courts et scrollables.
- [ ] Tester les états modal et dismissible.
- [ ] Vérifier plusieurs dialogues successifs ou superposés.

## Validation

- [ ] Lancer PaperNest avec `flet run --recursive`.
- [ ] Vérifier les dialogues des catégories, recherches, déplacements, renommages, sauvegardes et corbeille.
- [ ] Vérifier qu’aucun import historique ou héritage direct de `ft.AlertDialog` ne subsiste dans `AppDialog`.
- [ ] Valider PaperNest sous Windows.
- [ ] Valider le build Windows.
- [ ] Faire valider visuellement et fonctionnellement la migration par l’utilisateur.

## Critère de finalisation

Le chantier sera terminé lorsque tous les dialogues applicatifs auront été testés, que `AppDialog` utilisera le contrôle de PaperNestExtension sans régression et que le build Windows aura été validé.
